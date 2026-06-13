#!/usr/bin/env bash
# Shell test for normalize_sidecars.py — the v1.1 assembly-time normalization:
# INFRA_MARKER → infra-failure (status-first triage, marker wins over observation),
# the non-conforming-prose negative, status-first passthrough, and provenance
# stamping (refuse-on-conflict + idempotency).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FIXTURES="$DOMAIN_DIR/resources/fixtures"
NS="python3 $SCRIPT_DIR/normalize_sidecars.py"
VS="python3 $SCRIPT_DIR/validate_sidecar.py"
SRC="$FIXTURES/batches/valid-batch/sidecars/rung-0-trial-1.json"

PASS=0; FAIL=0

check() { # name expected_exit cmd...
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/ns-out.$$ 2>/tmp/ns-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then
    echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — expected exit $expected, got $got"
    sed 's/^/    /' /tmp/ns-err.$$ | head -5
    FAIL=$((FAIL+1))
  fi
}

# assert_json <name> <file> <python-expr-over-o-returning-bool>
assert_json() {
  local name="$1" file="$2" expr="$3"
  if python3 - "$file" "$expr" <<'PY'
import json, sys
o = json.load(open(sys.argv[1]))
sys.exit(0 if eval(sys.argv[2]) else 1)
PY
  then echo "PASS: $name"; PASS=$((PASS+1))
  else echo "FAIL: $name — assertion failed: $expr"; FAIL=$((FAIL+1)); fi
}

check_msg() {
  local name="$1" pattern="$2"
  if grep -q "$pattern" /tmp/ns-err.$$; then
    echo "PASS: $name"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — stderr missing pattern: $pattern"; FAIL=$((FAIL+1))
  fi
}

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# --- Marker-wins: completed + conforming marker → infra-failure, observation removed ---
mkdir -p "$TMP/marker/sidecars"
python3 - "$SRC" "$TMP/marker/sidecars/s.json" <<'PY'
import json, sys
o = json.load(open(sys.argv[1]))
o["run"]["status"] = "completed"
o["narration"] = " [stderr] ERROR: [ollama-agent] cannot reach ollama (timed out)"
o["observation"] = {"classification": "fixed", "exit_code": 0,
                    "anomaly_note": None, "artifacts": []}
json.dump(o, open(sys.argv[2], "w"))
PY
check "marker-wins: normalize rewrites the batch" 0 $NS "$TMP/marker/sidecars"
assert_json "marker-wins: status → infra-failure" "$TMP/marker/sidecars/s.json" \
  "o['run']['status'] == 'infra-failure'"
assert_json "marker-wins: observation removed" "$TMP/marker/sidecars/s.json" \
  "'observation' not in o"
check "marker-wins: result validates against v1.1" 0 $VS "$TMP/marker/sidecars/s.json"

# --- Negative: non-conforming ERROR: [x] prose is NOT rewritten ---
mkdir -p "$TMP/prose/sidecars"
python3 - "$SRC" "$TMP/prose/sidecars/s.json" <<'PY'
import json, sys
o = json.load(open(sys.argv[1]))
o["run"]["status"] = "completed"
o["narration"] = "Saw 'ERROR: [compiler] segfault', fixed the null deref, reran clean."
json.dump(o, open(sys.argv[2], "w"))
PY
check "non-conforming prose: normalize runs clean" 0 $NS "$TMP/prose/sidecars"
assert_json "non-conforming prose: status stays completed" "$TMP/prose/sidecars/s.json" \
  "o['run']['status'] == 'completed'"

# --- Status-first passthrough: an already-triaged status is never touched even with marker ---
for st in runner-error timeout infra-failure; do
  mkdir -p "$TMP/pass-$st/sidecars"
  python3 - "$SRC" "$TMP/pass-$st/sidecars/s.json" "$st" <<'PY'
import json, sys
o = json.load(open(sys.argv[1]))
o["run"]["status"] = sys.argv[3]
o.pop("observation", None)
o["narration"] = " [stderr] ERROR: [some-wrapper] boom"  # marker present but status wins
json.dump(o, open(sys.argv[2], "w"))
PY
  check "status-first: $st passes through unchanged" 0 $NS "$TMP/pass-$st/sidecars"
  assert_json "status-first: $st preserved" "$TMP/pass-$st/sidecars/s.json" \
    "o['run']['status'] == '$st'"
done

# --- Provenance: stamping the 4 contract keys, idempotency, refuse-on-conflict ---
mkdir -p "$TMP/prov/sidecars"
cp "$SRC" "$TMP/prov/sidecars/s.json"
check "provenance: first stamp succeeds" 0 \
  $NS "$TMP/prov/sidecars" --provenance engine_git_sha=abc123 --provenance model_id=m1
assert_json "provenance: keys written under producer.provenance" "$TMP/prov/sidecars/s.json" \
  "o['producer']['provenance'] == {'engine_git_sha': 'abc123', 'model_id': 'm1'}"
check "provenance: result validates against v1.1" 0 $VS "$TMP/prov/sidecars/s.json"
check "provenance: re-stamping identical values is idempotent (no-op)" 0 \
  $NS "$TMP/prov/sidecars" --provenance engine_git_sha=abc123 --provenance model_id=m1
assert_json "provenance: idempotent re-run unchanged" "$TMP/prov/sidecars/s.json" \
  "o['producer']['provenance'] == {'engine_git_sha': 'abc123', 'model_id': 'm1'}"
check "provenance: conflicting value refused (exit 1)" 1 \
  $NS "$TMP/prov/sidecars" --provenance engine_git_sha=DIFFERENT
check_msg "provenance: conflict message is loud" "refusing to overwrite"

# --- CLI input errors ---
check "non-contract provenance key rejected" 1 $NS "$TMP/prov/sidecars" --provenance bogus=x
check "missing sidecars dir is input error" 1 $NS "$TMP/never-was"

rm -f /tmp/ns-out.$$ /tmp/ns-err.$$
echo "----"
echo "normalize_sidecars: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
