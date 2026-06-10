#!/usr/bin/env bash
# Shell test for the simulated-lane deterministic pipeline (FR-8, FR-14):
# projection round-trip (project → validate_sidecar vs vendored contract) and
# hermetic playout (project → materialize → assemble → validate_batch), plus
# violation paths. No network, no Gygax, no LLM.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN="$(cd "$SCRIPT_DIR/.." && pwd)"
FIX="$DOMAIN/resources/fixtures"
NATIVE="$FIX/native-sidecar.events.yaml"

PASS=0; FAIL=0
check() {
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/sim-out.$$ 2>/tmp/sim-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then
    echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — expected exit $expected, got $got"
    sed 's/^/    /' /tmp/sim-err.$$ | head -4
    FAIL=$((FAIL+1))
  fi
}
check_msg() {
  local name="$1" pattern="$2"
  if grep -q "$pattern" /tmp/sim-err.$$; then
    echo "PASS: $name"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — stderr missing: $pattern"; FAIL=$((FAIL+1))
  fi
}

W=$(mktemp -d)
trap 'rm -rf "$W/traces" "$W/work" "$W/batch" "$W/tampered" 2>/dev/null; rmdir "$W" 2>/dev/null' EXIT
mkdir -p "$W/traces"

# --- Projection round-trip (SDD §7.1 check 2)
check "project_trace on fixture sidecar" 0 \
  python3 "$SCRIPT_DIR/project_trace.py" --native "$NATIVE" --out "$W/traces"
check "projected record conforms to vendored contract" 0 \
  python3 "$SCRIPT_DIR/validate_sidecar.py" "$W/traces/rung-0-trial-1.json"

# Projected record must be simulation-labeled and ungraded
python3 - "$W/traces/rung-0-trial-1.json" > /tmp/sim-out.$$ 2>/tmp/sim-err.$$ <<'PYEOF'
import json, sys
o = json.load(open(sys.argv[1]))
assert o["producer"]["kind"] == "simulation", "producer kind"
assert o["claim_strength"] == "simulation-derived", "claim"
assert "observation" not in o, "host must not grade"
print("labels ok")
PYEOF
if [ $? -eq 0 ]; then echo "PASS: projection labels + no observation"; PASS=$((PASS+1)); else echo "FAIL: projection labels"; FAIL=$((FAIL+1)); fi

# --- Hermetic playout (SDD §7.1 check 4)
check "materialize artifacts (seed + overlay, hash-verified)" 0 \
  python3 "$SCRIPT_DIR/materialize_artifacts.py" --native "$NATIVE" --batch "$W/work" --template "$FIX/synthetic-incentive/task-template"
if [ -f "$W/work/runs/rung-0/trial-1/test_solution.py" ] && [ -f "$W/work/runs/rung-0/trial-1/solution.py" ]; then
  echo "PASS: run dir seeded (baseline) + overlaid (declared artifact)"; PASS=$((PASS+1))
else
  echo "FAIL: run dir contents missing"; FAIL=$((FAIL+1))
fi
check "assemble batch" 0 \
  python3 "$SCRIPT_DIR/assemble_batch.py" --scenario "$FIX/scenarios/valid-simulated.yaml" --traces "$W/traces" --runs "$W/work/runs" --out "$W/batch"
check "assembled batch passes layout validation (ungraded sim)" 0 \
  python3 "$SCRIPT_DIR/validate_batch.py" "$W/batch"
check_msg "honest ungraded-simulation warning present" "not Gygax-ingestible until scored"

# The materialized solution must actually pass the fixture's reward command
( cd "$W/batch/runs/rung-0/trial-1" && python3 test_solution.py >/dev/null 2>&1 )
if [ $? -eq 0 ]; then echo "PASS: materialized artifacts pass the reward command"; PASS=$((PASS+1)); else echo "FAIL: materialized artifacts do not pass reward command"; FAIL=$((FAIL+1)); fi

# --- Violations
mkdir -p "$W/tampered"
sed 's/content_sha256: 31cd519f/content_sha256: 00d519f000/' "$NATIVE" > "$W/tampered/bad-hash.events.yaml"
cp -R "$FIX/synthetic-incentive" "$W/tampered/synthetic-incentive"
check "tampered content_sha256 rejected" 2 \
  python3 "$SCRIPT_DIR/materialize_artifacts.py" --native "$W/tampered/bad-hash.events.yaml" --batch "$W/tampered/work" --template "$FIX/synthetic-incentive/task-template"
check_msg "names the inconsistency" "content_sha256 mismatch"

sed 's|    path: solution.py|    path: ../../../escape.py|' "$NATIVE" > "$W/tampered/escape.events.yaml"
check "artifact path escaping batch rejected" 2 \
  python3 "$SCRIPT_DIR/materialize_artifacts.py" --native "$W/tampered/escape.events.yaml" --batch "$W/tampered/work2" --template "$FIX/synthetic-incentive/task-template"

grep -v "trial_end" "$NATIVE" | grep -v "status: completed" | grep -v "turns_used" | grep -v "stop_reason" > "$W/tampered/no-end.events.yaml"
check "sidecar without trial_end does not project" 2 \
  python3 "$SCRIPT_DIR/project_trace.py" --native "$W/tampered/no-end.events.yaml" --out "$W/tampered/traces"

check "missing native file is input error" 1 \
  python3 "$SCRIPT_DIR/project_trace.py" --native "$W/tampered/nope.yaml" --out "$W/tampered/traces"

# Audit findings (sprint-11): hostile state_path + malformed timestamp
sed 's|  state_path: synthetic-incentive|  state_path: ../../../../etc|' "$NATIVE" > "$W/tampered/evil-state.events.yaml"
check "escaping state_path rejected (CWE-22)" 2 \
  python3 "$SCRIPT_DIR/project_trace.py" --native "$W/tampered/evil-state.events.yaml" --out "$W/tampered/traces"
check_msg "names the escape" "state_path escapes"

sed 's|  state_path: synthetic-incentive|  state_path: /etc|' "$NATIVE" > "$W/tampered/abs-state.events.yaml"
check "absolute state_path rejected" 2 \
  python3 "$SCRIPT_DIR/project_trace.py" --native "$W/tampered/abs-state.events.yaml" --out "$W/tampered/traces"

cp -R "$FIX/synthetic-incentive" "$W/tampered/synthetic-incentive" 2>/dev/null || true
sed 's|    at: "2026-06-09T21:10:01Z"|    at: "yesterday-ish"|' "$NATIVE" > "$W/tampered/bad-ts.events.yaml"
cp "$W/tampered/bad-ts.events.yaml" "$W/tampered/bad-ts2.events.yaml"
mkdir -p "$W/tampered/syn-near" && cp -R "$FIX/synthetic-incentive/." "$W/tampered/syn-near/" 2>/dev/null
sed 's|  state_path: synthetic-incentive|  state_path: syn-near|' "$W/tampered/bad-ts.events.yaml" > "$W/tampered/bad-ts-local.events.yaml"
check "malformed timestamp fails with named error (no traceback)" 2 \
  python3 "$SCRIPT_DIR/project_trace.py" --native "$W/tampered/bad-ts-local.events.yaml" --out "$W/tampered/traces"
check_msg "clean catalog-style message" "invalid timestamp"

rm -f /tmp/sim-out.$$ /tmp/sim-err.$$
echo "----"
echo "sim-pipeline: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
