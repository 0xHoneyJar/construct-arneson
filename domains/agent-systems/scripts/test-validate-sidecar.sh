#!/usr/bin/env bash
# Shell test for validate_sidecar.py — happy path, every committed violation
# fixture (incl. the allOf laundering pairs), and the vendor drift-guard refusal.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FIXTURES="$DOMAIN_DIR/resources/fixtures"
VS="python3 $SCRIPT_DIR/validate_sidecar.py"

PASS=0; FAIL=0

check() { # name expected_exit cmd...
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/vsc-out.$$ 2>/tmp/vsc-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then
    echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — expected exit $expected, got $got"
    sed 's/^/    /' /tmp/vsc-err.$$ | head -5
    FAIL=$((FAIL+1))
  fi
}

check_msg() {
  local name="$1" pattern="$2"
  if grep -q "$pattern" /tmp/vsc-err.$$; then
    echo "PASS: $name"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — stderr missing pattern: $pattern"; FAIL=$((FAIL+1))
  fi
}

# Happy path
check "valid committed sidecar" 0 $VS "$FIXTURES/batches/valid-batch/sidecars/rung-0-trial-1.json"
check "valid sidecar via stdin" 0 bash -c "cat '$FIXTURES/batches/valid-batch/sidecars/rung-0-trial-1.json' | $VS -"

# Exit-2 class: every committed violation fixture
check "allOf: simulation laundered as real-agent-observed" 2 $VS "$FIXTURES/violations/laundering-sim-as-real.json"
check_msg "laundering message names the binding" "may not launder"
check "allOf: real-agent downgraded to simulation-derived" 2 $VS "$FIXTURES/violations/laundering-real-as-sim.json"
check "allOf: runner-error must omit observation" 2 $VS "$FIXTURES/violations/runner-error-with-observation.json"
check "unknown schema version hard-rejected" 2 $VS "$FIXTURES/violations/unknown-schema.json"
check "additionalProperties rejected at top level" 2 $VS "$FIXTURES/violations/extra-top-key.json"
check "missing required key (narration)" 2 $VS "$FIXTURES/violations/missing-narration.json"

# v1.1 cases (re-vendor at gygax 64f6d75): infra-failure status + producer.provenance
V11=$(mktemp -d)
python3 - "$FIXTURES/batches/valid-batch/sidecars/rung-0-trial-1.json" "$V11" <<'PY'
import json, sys
from pathlib import Path
base = json.loads(Path(sys.argv[1]).read_text())
out = Path(sys.argv[2])

def variant(name, mutate):
    s = json.loads(json.dumps(base))
    mutate(s)
    (out / name).write_text(json.dumps(s))

def infra_ok(s):
    s["run"]["status"] = "infra-failure"
    s.pop("observation", None)
variant("infra-failure-ok.json", infra_ok)

def prov_ok(s):
    s["producer"]["provenance"] = {
        "agent_cmd_sha256": "a" * 64, "engine_git_sha": "b" * 40,
        "model_id": "test-model", "construct_sha": "c" * 40}
variant("provenance-ok.json", prov_ok)

variant("provenance-unknown-key.json",
        lambda s: s["producer"].update(provenance={"engine_git_sha": "b", "extra_key": "x"}))
variant("provenance-non-string.json",
        lambda s: s["producer"].update(provenance={"engine_git_sha": 42}))

def infra_with_obs(s):
    s["run"]["status"] = "infra-failure"
    s["observation"] = {"classification": "failed", "exit_code": 1,
                        "anomaly_note": None, "artifacts": []}
variant("infra-failure-with-observation.json", infra_with_obs)
PY
check "v1.1: infra-failure without observation accepted" 0 $VS "$V11/infra-failure-ok.json"
check "v1.1: full 4-key producer.provenance accepted" 0 $VS "$V11/provenance-ok.json"
check "v1.1: unknown provenance key rejected" 2 $VS "$V11/provenance-unknown-key.json"
check_msg "v1.1: unknown-key message names the property" "additional property 'extra_key'"
check "v1.1: non-string provenance value rejected" 2 $VS "$V11/provenance-non-string.json"
check "v1.1: infra-failure with observation rejected" 2 $VS "$V11/infra-failure-with-observation.json"
rm -rf "$V11"

# Exit-1 class: input errors
check "missing file" 1 $VS "$FIXTURES/violations/nope.json"
check "invalid JSON" 1 bash -c "echo 'not json' | $VS -"
check "no args is usage error" 1 $VS

# Drift guard: copy the domain tree, tamper the vendored schema, expect refusal.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cp -R "$DOMAIN_DIR/scripts" "$TMP/scripts"
mkdir -p "$TMP/schemas"
cp -R "$DOMAIN_DIR/schemas/vendor" "$TMP/schemas/vendor"
printf '\n' >> "$TMP/schemas/vendor/observed-trace.v1.schema.json"
check "vendor drift refusal (sha256 mismatch)" 2 \
  python3 "$TMP/scripts/validate_sidecar.py" "$FIXTURES/batches/valid-batch/sidecars/rung-0-trial-1.json"
check_msg "drift message is loud and instructive" "CONTRACT DRIFT"

rm -f /tmp/vsc-out.$$ /tmp/vsc-err.$$
echo "----"
echo "validate_sidecar: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
