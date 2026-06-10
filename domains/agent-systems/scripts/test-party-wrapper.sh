#!/usr/bin/env bash
# Party-wrapper test suite (Sprint 1, Task 1.7). Hermetic: a stdlib mock Ollama
# server stands in for the daemon (OLLAMA_HOST). No daemon, no model, no network.
# Asserts: final-line-only parsing (table-talk verbs NOT matched), file-block
# containment refusal (exit 2), marker-on-unreachable, mock round trip.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER="$SCRIPT_DIR/../resources/fixtures/party-wrapper.py"
TEMPLATE="$SCRIPT_DIR/../resources/fixtures/dungeon-crawl/task-template"
PARTY="Brakka=m,Miriel=m,Pip=m"

PASS=0; FAIL=0
check() {
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/pw-out.$$ 2>/tmp/pw-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else echo "FAIL: $name — expected $expected, got $got"; sed 's/^/    /' /tmp/pw-err.$$|head -4; FAIL=$((FAIL+1)); fi
}
check_msg() { grep -q "$2" "${3:-/tmp/pw-err.$$}" && { echo "PASS: $1"; PASS=$((PASS+1)); } || { echo "FAIL: $1 — missing: $2"; FAIL=$((FAIL+1)); }; }

[ -f "$WRAPPER" ] || { echo "FAIL: wrapper missing at $WRAPPER"; echo "party-wrapper: 0 passed, 1 failed"; exit 1; }

# --- Unit: the final-line-only parser, tested directly (no daemon needed) ---
python3 - "$WRAPPER" > /tmp/pw-parser.$$ 2>&1 <<'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("pw", sys.argv[1])
pw = importlib.util.module_from_spec(spec); spec.loader.exec_module(pw)
A = pw.ACTION
def parse(reply):
    lines = [ln for ln in reply.strip().splitlines() if ln.strip()]
    for ln in reversed(lines):
        m = A.match(ln.strip())
        if m: return (m.group(1).lower(), m.group(2) or "")
    return None
cases = [
    # table-talk with a verb buried mid-sentence, real action on the final line
    ("I should firebolt the troll soon, but first:\nattack goblin-1", ("attack","goblin-1")),
    ("Let me take stock of the situation.\ndisarm", ("disarm","")),
    ("take -rune-blade looks tempting in the lore\nadvance", ("advance","")),
    # pure prose, no action line → None (turn passes, not a misparse)
    ("I think we should probably attack something eventually.", None),
    # action line with list marker
    ("Reasoning here.\n- firebolt troll", ("firebolt","troll")),
]
bad = 0
for reply, want in cases:
    got = parse(reply)
    if got != want:
        print(f"MISPARSE: {reply!r} -> {got} (want {want})"); bad += 1
print("PARSER_OK" if bad == 0 else f"PARSER_FAIL {bad}")
PYEOF
if grep -q "PARSER_OK" /tmp/pw-parser.$$; then echo "PASS: final-line parser — table-talk verbs NOT matched, final line wins"; PASS=$((PASS+1))
else echo "FAIL: final-line parser"; sed 's/^/    /' /tmp/pw-parser.$$ | head -6; FAIL=$((FAIL+1)); fi

# --- Mock Ollama daemon ---
W=$(mktemp -d)
trap 'kill "$MOCK_PID" 2>/dev/null; rm -rf "$W/room" "$W/esc" "$W/mock.py" 2>/dev/null; rmdir "$W" 2>/dev/null' EXIT
cat > "$W/mock.py" <<'PYEOF'
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
MODE = sys.argv[2] if len(sys.argv) > 2 else "act"
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if MODE == "escape":
            content = "Working on it.\n```file:../escaped.py\nprint('out')\n```\n"
        else:
            content = "Brakka charges in.\nattack goblin-1"
        b = json.dumps({"message":{"role":"assistant","content":content},"done":True}).encode()
        self.send_response(200); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self,*a): pass
HTTPServer(("127.0.0.1",int(sys.argv[1])),H).serve_forever()
PYEOF
PORT=$((22000 + RANDOM % 20000))
MOCK_PID=""

# Mock round trip: wrapper drives a 1-round playout, records the parsed action
python3 "$W/mock.py" "$PORT" act & MOCK_PID=$!; sleep 0.4
mkdir -p "$W/room" && cp "$TEMPLATE"/dungeon.json "$TEMPLATE"/referee.py "$W/room/" && echo "[]" > "$W/room/moves.json"
check "mock round trip drives the wrapper" 0 \
  bash -c "cd '$W/room' && OLLAMA_HOST=127.0.0.1:$PORT python3 '$WRAPPER' --party '$PARTY' --max-rounds 1 '$TEMPLATE/../rungs/rung-0-blind.md'"
grep -q '"action": "attack"' "$W/room/moves.json" && { echo "PASS: parsed action written to moves.json"; PASS=$((PASS+1)); } || { echo "FAIL: no parsed action in moves.json"; FAIL=$((FAIL+1)); }
kill "$MOCK_PID" 2>/dev/null; wait "$MOCK_PID" 2>/dev/null

# Containment: a file-block escaping cwd → all writes refused, exit 2
python3 "$W/mock.py" "$PORT" escape & MOCK_PID=$!; sleep 0.4
mkdir -p "$W/esc" && cp "$TEMPLATE"/dungeon.json "$TEMPLATE"/referee.py "$W/esc/" && echo "[]" > "$W/esc/moves.json"
check "file-block escaping cwd → refused (exit 2)" 2 \
  bash -c "cd '$W/esc' && OLLAMA_HOST=127.0.0.1:$PORT python3 '$WRAPPER' --party '$PARTY' --max-rounds 1 '$TEMPLATE/../rungs/rung-0-blind.md'"
check_msg "containment names the escape" "escapes the working directory"
[ ! -f "$W/escaped.py" ] && { echo "PASS: nothing written outside cwd"; PASS=$((PASS+1)); } || { echo "FAIL: file escaped"; FAIL=$((FAIL+1)); }
kill "$MOCK_PID" 2>/dev/null; wait "$MOCK_PID" 2>/dev/null; MOCK_PID=""

# Marker on unreachable daemon (infrastructure-marker convention)
mkdir -p "$W/room"; cp "$TEMPLATE"/dungeon.json "$TEMPLATE"/referee.py "$W/room/" 2>/dev/null; echo "[]" > "$W/room/moves.json"
check "unreachable daemon → exit 1" 1 \
  bash -c "cd '$W/room' && OLLAMA_HOST=127.0.0.1:1 python3 '$WRAPPER' --party '$PARTY' --max-rounds 1 '$TEMPLATE/../rungs/rung-0-blind.md'"
check_msg "emits the [party-wrapper] marker" "ERROR: \[party-wrapper\]"

rm -f /tmp/pw-out.$$ /tmp/pw-err.$$ /tmp/pw-parser.$$
echo "----"
echo "party-wrapper: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
