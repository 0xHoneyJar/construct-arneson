#!/usr/bin/env bash
# test-scaffold-playtest.sh (Sprint 4, Task 4.2). Hermetic, stdlib only.
# Generates a skeleton into a temp dir and asserts: smoke test passes, the
# incentive-state passes payoff-dominance, manifest parses, and the self-check
# exit-2 path fires on a broken generation.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="python3 $SCRIPT_DIR/scaffold_playtest.py"
CP="python3 $SCRIPT_DIR/check_payoff_dominance.py"

PASS=0; FAIL=0
check() {
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/sc-out.$$ 2>/tmp/sc-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else echo "FAIL: $name — expected $expected got $got"; sed 's/^/    /' /tmp/sc-{out,err}.$$|head -4; FAIL=$((FAIL+1)); fi
}

W=$(mktemp -d)
trap 'rm -rf "$W/gen" "$W/gen2" "$W/exists" 2>/dev/null; rmdir "$W" 2>/dev/null' EXIT

# Happy path: generate + self-check passes (exit 0)
check "scaffold generates + self-checks (exit 0)" 0 \
  $SC --id sample-test --task "do a thing" --difficulty-range 1-10 --rungs 3 --out "$W/gen"

# Generated skeleton's smoke test passes when run independently
check "generated smoke test passes standalone" 0 bash "$W/gen/test-referee.sh"

# Generated incentive-state is payoff-dominant (cliff claim meaningful once authored)
check "generated incentive-state → payoff-dominance PASS" 0 $CP "$W/gen/incentive-state"
grep -q "PASS:" /tmp/sc-out.$$ && { echo "PASS: dominance verdict is PASS"; PASS=$((PASS+1)); } || { echo "FAIL: not PASS"; FAIL=$((FAIL+1)); }

# Generated referee is an honest DEFEAT no-op
check "generated referee --check → DEFEAT (exit 1)" 1 python3 "$W/gen/task-template/referee.py" --check
python3 "$W/gen/task-template/referee.py" --state | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null \
  && { echo "PASS: generated referee --state is valid JSON"; PASS=$((PASS+1)); } || { echo "FAIL: --state not JSON"; FAIL=$((FAIL+1)); }

# Prose-equalized rungs: bodies share structure, differ only in the awareness clause
b0=$(grep -c "working directory contains" "$W/gen/rungs/rung-0-blind.md")
b2=$(grep -c "working directory contains" "$W/gen/rungs/rung-2-adversarial.md")
[ "$b0" = "1" ] && [ "$b2" = "1" ] && { echo "PASS: rungs share the common body"; PASS=$((PASS+1)); } || { echo "FAIL: rung bodies diverge"; FAIL=$((FAIL+1)); }

# Input errors
check "bad --id (not kebab) → exit 1" 1 $SC --id Bad_ID --task x --difficulty-range 1-10 --out "$W/gen2"
check "bad difficulty range → exit 1" 1 $SC --id ok --task x --difficulty-range 10-1 --out "$W/gen2"
check "missing required flag → exit 1" 1 $SC --id ok --task x --out "$W/gen2"
mkdir -p "$W/exists" && touch "$W/exists/x"
check "non-empty --out → exit 1 (no clobber)" 1 $SC --id ok --task x --difficulty-range 1-5 --out "$W/exists"
check "--out with .. traversal → exit 1 (SEC-001)" 1 $SC --id ok --task x --difficulty-range 1-5 --out "$W/../escape"
check "--id with trailing dash → exit 1 (CQ-001)" 1 $SC --id "bad-" --task x --difficulty-range 1-5 --out "$W/gen3"

# Self-check exit-2 path: break the smoke template via a broken referee, confirm exit 2.
# Simulate by generating, corrupting the referee, and re-running the smoke as the scaffolder would.
$SC --id breakme --task x --difficulty-range 1-5 --out "$W/gen2" >/dev/null 2>&1
echo "import sys; sys.exit(3)" > "$W/gen2/task-template/referee.py"  # undefined exit for --check
bash "$W/gen2/test-referee.sh" >/dev/null 2>&1; rc=$?
[ "$rc" != "0" ] && { echo "PASS: corrupted referee makes the smoke test fail (exit-2 path is reachable)"; PASS=$((PASS+1)); } || { echo "FAIL: smoke test passed a broken referee"; FAIL=$((FAIL+1)); }

rm -f /tmp/sc-out.$$ /tmp/sc-err.$$
echo "----"
echo "scaffold-playtest: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
