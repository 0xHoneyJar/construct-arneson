#!/usr/bin/env bash
# Shell test for validate_batch.py — committed batch happy path, layout violations,
# run_dir escape containment, and the ungraded-simulation honesty warning.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FIXTURES="$DOMAIN_DIR/resources/fixtures"
VB="python3 $SCRIPT_DIR/validate_batch.py"

PASS=0; FAIL=0

check() {
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/vb-out.$$ 2>/tmp/vb-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then
    echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — expected exit $expected, got $got"
    sed 's/^/    /' /tmp/vb-err.$$ | head -5
    FAIL=$((FAIL+1))
  fi
}

check_msg() {
  local name="$1" pattern="$2"
  if grep -q "$pattern" /tmp/vb-err.$$; then
    echo "PASS: $name"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — stderr missing pattern: $pattern"; FAIL=$((FAIL+1))
  fi
}

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Happy path: the committed fixture batch
check "committed fixture batch conformant" 0 $VB "$FIXTURES/batches/valid-batch"

# missing batch.json
mkdir -p "$TMP/no-manifest/sidecars"
cp "$FIXTURES/batches/valid-batch/sidecars/rung-0-trial-1.json" "$TMP/no-manifest/sidecars/"
check "missing batch.json rejected" 2 $VB "$TMP/no-manifest"
check_msg "names the grade-on-ingest requirement" "batch.json missing"

# wrong batch schema string
cp -R "$FIXTURES/batches/valid-batch" "$TMP/wrong-schema"
python3 - "$TMP/wrong-schema/batch.json" <<'PYEOF'
import json, sys
p = sys.argv[1]
m = json.load(open(p)); m["schema"] = "observed-trace-batch/v2"
json.dump(m, open(p, "w"))
PYEOF
check "wrong batch.json schema rejected" 2 $VB "$TMP/wrong-schema"

# run_dir escapes the batch dir
cp -R "$FIXTURES/batches/valid-batch" "$TMP/escape"
python3 - "$TMP/escape/sidecars/rung-0-trial-1.json" <<'PYEOF'
import json, sys
p = sys.argv[1]
o = json.load(open(p)); o["run"]["run_dir"] = "../../outside"
json.dump(o, open(p, "w"))
PYEOF
check "run_dir escaping batch dir rejected" 2 $VB "$TMP/escape"
check_msg "containment message" "escapes the batch directory"

# run_dir missing on disk
cp -R "$FIXTURES/batches/valid-batch" "$TMP/missing-rundir"
rm -rf "$TMP/missing-rundir/runs"
check "missing run_dir tree rejected" 2 $VB "$TMP/missing-rundir"

# nonconformant sidecar inside an otherwise-valid batch
cp -R "$FIXTURES/batches/valid-batch" "$TMP/bad-sidecar"
cp "$FIXTURES/violations/laundering-sim-as-real.json" "$TMP/bad-sidecar/sidecars/rung-0-trial-2.json"
mkdir -p "$TMP/bad-sidecar/runs/rung-0/trial-1"
check "batch with laundering sidecar rejected" 2 $VB "$TMP/bad-sidecar"

# no sidecars at all
mkdir -p "$TMP/empty"
cp "$FIXTURES/batches/valid-batch/batch.json" "$TMP/empty/"
check "batch with zero sidecars rejected" 2 $VB "$TMP/empty"

# honesty warning: completed simulation sidecar, ungraded → exit 0 + WARNING
cp -R "$FIXTURES/batches/valid-batch" "$TMP/sim-ungraded"
python3 - "$TMP/sim-ungraded/sidecars/rung-0-trial-1.json" <<'PYEOF'
import json, sys
p = sys.argv[1]
o = json.load(open(p))
o["producer"]["kind"] = "simulation"
o["claim_strength"] = "simulation-derived"
json.dump(o, open(p, "w"))
PYEOF
check "ungraded simulation batch passes layout" 0 $VB "$TMP/sim-ungraded"
check_msg "but warns it is not ingestible until scored" "not Gygax-ingestible until scored"

# Infrastructure triage (bug 20260610-594345): a completed sidecar whose narration
# carries the bundled wrapper's own error signature is a NON-RUN, not a verdict —
# the validator must say so (warn-not-reject; exit stays 0).
cp -R "$FIXTURES/batches/valid-batch" "$TMP/infra-casualty"
python3 - "$TMP/infra-casualty/sidecars/rung-0-trial-1.json" <<'PYEOF'
import json, sys
p = sys.argv[1]
o = json.load(open(p))
o["narration"] = " [stderr] ERROR: [ollama-agent] cannot reach ollama at 127.0.0.1:11434 (timed out). Is the daemon running?"
json.dump(o, open(p, "w"))
PYEOF
check "infrastructure-casualty batch still layout-valid (warn-not-reject)" 0 $VB "$TMP/infra-casualty"
check_msg "but warns it is a non-run, not a verdict" "non-run, not a verdict"

check "clean batch emits no infrastructure warning" 0 $VB "$FIXTURES/batches/valid-batch"
if grep -q "non-run" /tmp/vb-err.$$; then
  echo "FAIL: clean batch falsely flagged as infrastructure casualty"; FAIL=$((FAIL+1))
else
  echo "PASS: no false triage on clean narration"; PASS=$((PASS+1))
fi

# Marker CONVENTION (bug 20260610-5ad67a): triage must match any conforming wrapper
# marker (…-agent / …-wrapper), not one literal string — and must NOT flag arbitrary
# agent-printed ERROR strings that don't conform.
cp -R "$FIXTURES/batches/valid-batch" "$TMP/party-casualty"
python3 - "$TMP/party-casualty/sidecars/rung-0-trial-1.json" <<'PYEOF'
import json, sys
o = json.load(open(sys.argv[1]))
o["narration"] = " [stderr] ERROR: [party-wrapper] cannot reach ollama at 127.0.0.1:11434 for gemma:latest (timed out)"
json.dump(o, open(sys.argv[1], "w"))
PYEOF
check "second wrapper's marker triages (convention, not literal)" 0 $VB "$TMP/party-casualty"
check_msg "party-wrapper casualty flagged as non-run" "non-run, not a verdict"

cp -R "$FIXTURES/batches/valid-batch" "$TMP/agent-stdout-error"
python3 - "$TMP/agent-stdout-error/sidecars/rung-0-trial-1.json" <<'PYEOF'
import json, sys
o = json.load(open(sys.argv[1]))
o["narration"] = "Ran the tests, saw 'ERROR: [compiler] segfault in module x', fixed the null deref, reran clean."
json.dump(o, open(sys.argv[1], "w"))
PYEOF
check "non-conforming ERROR string in agent prose does NOT triage" 0 $VB "$TMP/agent-stdout-error"
if grep -q "non-run" /tmp/vb-err.$$; then
  echo "FAIL: false positive — agent-printed ERROR flagged as infrastructure"; FAIL=$((FAIL+1))
else
  echo "PASS: false-positive guard holds (ERROR: [compiler] ignored)"; PASS=$((PASS+1))
fi

# input errors
check "nonexistent batch dir" 1 $VB "$TMP/never-was"

rm -f /tmp/vb-out.$$ /tmp/vb-err.$$
echo "----"
echo "validate_batch: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
