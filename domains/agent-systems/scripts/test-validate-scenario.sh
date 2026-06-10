#!/usr/bin/env bash
# Shell test for validate_scenario.py — happy paths, each exit-1 class, each exit-2 class.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES="$SCRIPT_DIR/../resources/fixtures"
VS="python3 $SCRIPT_DIR/validate_scenario.py"

PASS=0; FAIL=0

check() { # name expected_exit cmd...
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/vscen-out.$$ 2>/tmp/vscen-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then
    echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — expected exit $expected, got $got"
    sed 's/^/    /' /tmp/vscen-err.$$ | head -5
    FAIL=$((FAIL+1))
  fi
}

check_msg() { # name pattern (stderr of last check)
  local name="$1" pattern="$2"
  if grep -q "$pattern" /tmp/vscen-err.$$; then
    echo "PASS: $name (message present)"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — stderr missing pattern: $pattern"; FAIL=$((FAIL+1))
  fi
}

# Happy paths
check "valid real-lane scenario" 0 $VS --lane real "$FIXTURES/scenarios/valid-real.yaml"
if ! grep -q '"runs_planned": 4' /tmp/vscen-out.$$; then
  echo "FAIL: stdout summary missing runs_planned=4 (rungs 2 × trials 2)"; FAIL=$((FAIL+1))
else
  echo "PASS: stdout summary carries runs_planned"; PASS=$((PASS+1))
fi
check "valid simulated-lane scenario" 0 $VS --lane simulated "$FIXTURES/scenarios/valid-simulated.yaml"
check "valid with no --lane (shared core only)" 0 $VS "$FIXTURES/scenarios/valid-real.yaml"

# Exit-1 class: input errors
check "unbounded scenario rejected" 1 $VS --lane real "$FIXTURES/scenarios/unbounded.yaml"
check_msg "unbounded message exact" "UNBOUNDED SCENARIO REJECTED: stopping.max_turns required"
check "missing file" 1 $VS --lane real "$FIXTURES/scenarios/does-not-exist.yaml"
check "real lane requires agent_cmd" 1 $VS --lane real "$FIXTURES/scenarios/valid-simulated.yaml"
check "simulated lane requires persona" 1 $VS --lane simulated "$FIXTURES/scenarios/valid-real.yaml"
check "bad --lane value" 1 $VS --lane warp "$FIXTURES/scenarios/valid-real.yaml"

# Exit-2 class: checksum contract violations
check "fixture manifest checksum mismatch" 2 $VS --lane real "$FIXTURES/scenarios/bad-checksum.yaml"
check_msg "checksum mismatch names ref + hashes" "checksum mismatch: fixture.manifest_sha256"

# Persona checksum mismatch: tampered copy in a temp dir (fixture copied alongside
# so the scenario's relative paths still resolve; persona file then modified).
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/scenarios"
cp "$FIXTURES/scenarios/valid-simulated.yaml" "$FIXTURES/scenarios/test-persona.yaml" "$TMP/scenarios/"
cp -R "$FIXTURES/synthetic-incentive" "$TMP/synthetic-incentive"
echo "# tampered" >> "$TMP/scenarios/test-persona.yaml"
check "persona checksum mismatch after tamper" 2 $VS --lane simulated "$TMP/scenarios/valid-simulated.yaml"
check_msg "persona mismatch names ref" "checksum mismatch: persona.sha256"

rm -f /tmp/vscen-out.$$ /tmp/vscen-err.$$
echo "----"
echo "validate_scenario: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
