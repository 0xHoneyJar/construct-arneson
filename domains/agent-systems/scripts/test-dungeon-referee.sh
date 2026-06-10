#!/usr/bin/env bash
# Deterministic referee test suite for the dungeon-crawl fixture (Sprint 1, Task 1.4).
# Four classes: winning-line → exit 0; defeat cases → exit 1; DETERMINISM (same moves
# twice → byte-identical --state, NFR-3); illegal-move semantics (no crash). Hermetic,
# stdlib only, no network.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../resources/fixtures/dungeon-crawl/task-template"

PASS=0; FAIL=0
check() {
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/ref-out.$$ 2>/tmp/ref-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else echo "FAIL: $name — expected $expected, got $got"; sed 's/^/    /' /tmp/ref-err.$$ | head -4; FAIL=$((FAIL+1)); fi
}

W=$(mktemp -d)
trap 'rm -rf "$W/win" "$W/empty" "$W/illegal" "$W/det1" "$W/det2" 2>/dev/null; rmdir "$W" 2>/dev/null' EXIT
room() { mkdir -p "$W/$1" && cp "$TEMPLATE"/dungeon.json "$TEMPLATE"/referee.py "$W/$1/"; }

# --- The hand-verified winning line (27 moves / 42 budget) ---
winning_moves() {
python3 - "$1" <<'PYEOF'
import json, sys
m = lambda a, act, t="": {"actor": a, "action": act, "target": t}
B, M, P = "Brakka", "Miriel", "Pip"
moves = [
    m(B,"attack","goblin-1"), m(M,"attack","goblin-1"), m(P,"attack","goblin-2"),
    m(B,"attack","goblin-2"), m(M,"advance"), m(P,"disarm"),
    m(B,"advance"), m(M,"take","potion"), m(P,"take","potion"),
    m(B,"take","rune-blade"), m(M,"advance"), m(P,"attack","troll"),
    m(B,"attack","troll"), m(M,"firebolt","troll"), m(P,"attack","troll"),
    m(B,"attack","troll"), m(M,"advance"), m(P,"attack","bone-tyrant"),
    m(B,"attack","bone-tyrant"), m(M,"use-potion","Miriel"), m(P,"use-potion","Miriel"),
    m(B,"attack","bone-tyrant"), m(M,"attack","bone-tyrant"), m(P,"attack","bone-tyrant"),
    m(B,"attack","bone-tyrant"), m(M,"attack","bone-tyrant"), m(P,"attack","bone-tyrant"),
]
json.dump(moves, open(sys.argv[1], "w"))
PYEOF
}

# Class 1: winning line → exit 0
room win; winning_moves "$W/win/moves.json"
check "winning line replays to VICTORY (exit 0)" 0 bash -c "cd '$W/win' && python3 referee.py --check"

# Class 2: defeat — empty moves (boss alive) → exit 1
room empty; echo "[]" > "$W/empty/moves.json"
check "empty moves → DEFEAT (exit 1)" 1 bash -c "cd '$W/empty' && python3 referee.py --check"

# Class 3: DETERMINISM — same moves twice → byte-identical --state
room det1; winning_moves "$W/det1/moves.json"
room det2; winning_moves "$W/det2/moves.json"
( cd "$W/det1" && python3 referee.py --state > "$W/state1.json" 2>/dev/null )
( cd "$W/det2" && python3 referee.py --state > "$W/state2.json" 2>/dev/null )
if cmp -s "$W/state1.json" "$W/state2.json"; then echo "PASS: determinism — identical --state across two runs (NFR-3)"; PASS=$((PASS+1))
else echo "FAIL: determinism — --state differs across runs"; FAIL=$((FAIL+1)); fi
# and the winning state actually reports victory
grep -q '"victory": true' "$W/state1.json" && { echo "PASS: winning --state reports victory:true"; PASS=$((PASS+1)); } || { echo "FAIL: winning state not victory"; FAIL=$((FAIL+1)); }

# Class 4: illegal move — unknown verb wastes a turn, never crashes
room illegal
python3 - "$W/illegal/moves.json" <<'PYEOF'
import json, sys
json.dump([{"actor":"Brakka","action":"teleport","target":"moon"},
           {"actor":"Nobody","action":"attack","target":"goblin-1"}], open(sys.argv[1],"w"))
PYEOF
check "illegal verb + unknown actor → no crash, defined exit (1)" 1 bash -c "cd '$W/illegal' && python3 referee.py --check"
if grep -q "Traceback" /tmp/ref-err.$$; then echo "FAIL: illegal move produced a traceback"; FAIL=$((FAIL+1)); else echo "PASS: illegal move produced no traceback"; PASS=$((PASS+1)); fi

rm -f /tmp/ref-out.$$ /tmp/ref-err.$$
echo "----"
echo "dungeon-referee: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
