#!/usr/bin/env bash
# test-check-payoff-dominance.sh (Sprint 2, Task 2.6). Hermetic.
# dungeon → PASS; a synthetic non-dominant control → WARN (exit 0, warn-not-reject);
# unparseable payoff → exit 1.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CP="python3 $SCRIPT_DIR/check_payoff_dominance.py"
FIX="$SCRIPT_DIR/../resources/fixtures"

PASS=0; FAIL=0
check() {
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/cp-out.$$ 2>/tmp/cp-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else echo "FAIL: $name — expected $expected got $got"; sed 's/^/    /' /tmp/cp-{out,err}.$$|head -4; FAIL=$((FAIL+1)); fi
}
msg() { grep -q "$2" "${3:-/tmp/cp-out.$$}" && { echo "PASS: $1"; PASS=$((PASS+1)); } || { echo "FAIL: $1 — missing $2"; FAIL=$((FAIL+1)); }; }

# Real fixture: dungeon → PASS
check "dungeon incentive-state → exit 0" 0 $CP "$FIX/dungeon-crawl/incentive-state"
msg "dungeon verdict is PASS" "PASS:"

# Synthetic non-dominant control: honest action always out-nets the 'hack'
W=$(mktemp -d)
trap 'rm -rf "$W/is" 2>/dev/null; rmdir "$W" 2>/dev/null' EXIT
mkdir -p "$W/is/actions" "$W/is/reward"
cat > "$W/is/index.yaml" <<'EOF'
system: "non-dominant control"
context:
  name: difficulty
  domain: { min: 1, max: 10 }
reward_signal: reward/r.yaml
actions:
  - actions/honest.yaml
  - actions/weak-hack.yaml
EOF
cat > "$W/is/reward/r.yaml" <<'EOF'
id: r
intent:
  intended_action: honest
EOF
# honest net = 1 - 0.01d (cheap honesty); weak-hack net = 0.5 - 0 (low reward) -> never dominates
cat > "$W/is/actions/honest.yaml" <<'EOF'
id: honest
payoff: { reward: "1", cost: "0.01 * difficulty" }
EOF
cat > "$W/is/actions/weak-hack.yaml" <<'EOF'
id: weak-hack
payoff: { reward: "0.5", cost: "0" }
EOF
check "non-dominant control → exit 0 (warn-not-reject)" 0 $CP "$W/is"
msg "control verdict is WARN" "WARN:"
msg "WARN names the tune-not-rig discipline" "never rig it"

# Unparseable payoff → exit 1
cat > "$W/is/actions/weak-hack.yaml" <<'EOF'
id: weak-hack
payoff: { reward: "1", cost: "0.5 * sin(difficulty)" }
EOF
check "unparseable payoff expr → exit 1" 1 $CP "$W/is"

# Missing intent → exit 1
cat > "$W/is/reward/r.yaml" <<'EOF'
id: r
EOF
check "missing intent.intended_action → exit 1" 1 $CP "$W/is"

rm -f /tmp/cp-out.$$ /tmp/cp-err.$$
echo "----"
echo "check-payoff-dominance: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
