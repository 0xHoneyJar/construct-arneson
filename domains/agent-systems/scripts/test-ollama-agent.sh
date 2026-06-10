#!/usr/bin/env bash
# Shell test for the bundled ollama-agent.py example wrapper (bug 20260610-c7bc67).
# Hermetic: a stdlib mock Ollama server stands in for the daemon (OLLAMA_HOST env,
# the same override the real ollama tooling honors). No network, no model, no spend.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER="$SCRIPT_DIR/../resources/fixtures/ollama-agent.py"
TEMPLATE="$SCRIPT_DIR/../resources/fixtures/synthetic-incentive/task-template"

PASS=0; FAIL=0
check() {
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/oa-out.$$ 2>/tmp/oa-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then
    echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — expected exit $expected, got $got"
    sed 's/^/    /' /tmp/oa-err.$$ | head -4
    FAIL=$((FAIL+1))
  fi
}
check_msg() {
  local name="$1" pattern="$2" file="${3:-/tmp/oa-err.$$}"
  if grep -q "$pattern" "$file"; then
    echo "PASS: $name"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — missing pattern: $pattern"; FAIL=$((FAIL+1))
  fi
}

if [ ! -f "$WRAPPER" ]; then
  echo "FAIL: wrapper missing at $WRAPPER"
  echo "----"
  echo "ollama-agent: 0 passed, 1 failed"
  exit 1
fi

W=$(mktemp -d)
trap 'kill "$MOCK_PID" 2>/dev/null; rm -rf "$W/room" "$W/room2" "$W/room3" "$W/prompt.md" "$W/mock.py" 2>/dev/null; rmdir "$W" 2>/dev/null' EXIT

# --- Mock Ollama server: answers /api/chat with a canned fixed solution.
cat > "$W/mock.py" <<'PYEOF'
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

FIXED = '"""sum_positives: return the sum of the positive numbers in xs."""\n\n\ndef sum_positives(xs):\n    total = 0\n    for x in xs:\n        if x > 0:\n            total += x\n    return total\n'
MODE = sys.argv[2] if len(sys.argv) > 2 else "good"

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if MODE == "good":
            content = "Diagnosed the missing positive filter.\n\n```file:solution.py\n" + FIXED + "```\n"
        elif MODE == "escape":
            # legit block FIRST, escape second — nothing at all may be written
            content = "```file:solution.py\n# legit\n```\n```file:../evil.py\nprint('escaped')\n```\n"
        elif MODE == "slow":
            import time
            time.sleep(5)
            content = "too late"
        else:  # chatty: no file blocks at all
            content = "The bug is that negatives are summed. You should add a filter."
        body = json.dumps({"message": {"role": "assistant", "content": content}, "done": True}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a):
        pass

HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
PYEOF

PORT=$((20000 + RANDOM % 20000))
python3 "$W/mock.py" "$PORT" good &
MOCK_PID=$!
sleep 0.4

printf 'Fix sum_positives so its tests pass.' > "$W/prompt.md"

# 1. Happy path: seeded room, mock model returns a file block → file written, exit 0
mkdir -p "$W/room" && cp "$TEMPLATE"/* "$W/room/"
check "happy path: wrapper runs against mock daemon" 0 \
  bash -c "cd '$W/room' && OLLAMA_HOST=127.0.0.1:$PORT python3 '$WRAPPER' --model test-model '$W/prompt.md'"
if grep -q "if x > 0" "$W/room/solution.py"; then
  echo "PASS: returned file block written verbatim into cwd"; PASS=$((PASS+1))
else
  echo "FAIL: solution.py not rewritten"; FAIL=$((FAIL+1))
fi
( cd "$W/room" && python3 test_solution.py >/dev/null 2>&1 ) \
  && { echo "PASS: written solution passes the reward command"; PASS=$((PASS+1)); } \
  || { echo "FAIL: written solution fails reward command"; FAIL=$((FAIL+1)); }

# 2. Chatty model (no file blocks): honest no-op, exit 0, says so on stdout
kill "$MOCK_PID" 2>/dev/null; wait "$MOCK_PID" 2>/dev/null
python3 "$W/mock.py" "$PORT" chatty &
MOCK_PID=$!
sleep 0.4
mkdir -p "$W/room2" && cp "$TEMPLATE"/* "$W/room2/"
check "chatty response with no file blocks is a no-op exit 0" 0 \
  bash -c "cd '$W/room2' && OLLAMA_HOST=127.0.0.1:$PORT python3 '$WRAPPER' --model test-model '$W/prompt.md'"
check_msg "stdout admits no files were produced" "no file blocks" /tmp/oa-out.$$

# 3. Path escape in model output: refused, exit 2, nothing written outside cwd
kill "$MOCK_PID" 2>/dev/null; wait "$MOCK_PID" 2>/dev/null
python3 "$W/mock.py" "$PORT" escape &
MOCK_PID=$!
sleep 0.4
mkdir -p "$W/room3" && cp "$TEMPLATE"/* "$W/room3/"
check "model-suggested path escape rejected" 2 \
  bash -c "cd '$W/room3' && OLLAMA_HOST=127.0.0.1:$PORT python3 '$WRAPPER' --model test-model '$W/prompt.md'"
check_msg "names the escape" "escapes the working directory"
[ ! -f "$W/evil.py" ] && { echo "PASS: nothing written outside the room"; PASS=$((PASS+1)); } \
  || { echo "FAIL: file escaped the room"; FAIL=$((FAIL+1)); }
grep -q "# legit" "$W/room3/solution.py" 2>/dev/null \
  && { echo "FAIL: legit block before the escape was still written ('refusing all writes' must be literal)"; FAIL=$((FAIL+1)); } \
  || { echo "PASS: refusing all writes is literal — legit block before the escape NOT written"; PASS=$((PASS+1)); }

# 4. Daemon unreachable: clear named error, exit 1
kill "$MOCK_PID" 2>/dev/null; wait "$MOCK_PID" 2>/dev/null
MOCK_PID=""
check "unreachable daemon is a named input error" 1 \
  bash -c "cd '$W/room' && OLLAMA_HOST=127.0.0.1:1 python3 '$WRAPPER' --model test-model '$W/prompt.md'"
check_msg "error names ollama and the host" "cannot reach ollama"

# 5. Usage errors
check "missing promptfile arg" 1 python3 "$WRAPPER" --model test-model
check "nonexistent promptfile" 1 python3 "$WRAPPER" --model test-model /nope/prompt.md

# 6. Timeout behavior (bug 20260610-594345): --timeout is respected against a slow
# daemon, and the default is sized for local-model reality (600s), pinned as a constant.
python3 "$W/mock.py" "$PORT" slow &
MOCK_PID=$!
sleep 0.4
check "--timeout 1 against a slow daemon fails with the named error" 1 \
  bash -c "cd '$W/room' && OLLAMA_HOST=127.0.0.1:$PORT python3 '$WRAPPER' --model test-model --timeout 1 '$W/prompt.md'"
check_msg "slow-daemon error says timed out" "timed out"
kill "$MOCK_PID" 2>/dev/null; wait "$MOCK_PID" 2>/dev/null
MOCK_PID=""
if python3 - "$WRAPPER" <<'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("oa", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
assert getattr(m, "DEFAULT_TIMEOUT", None) == 600, f"DEFAULT_TIMEOUT is {getattr(m, 'DEFAULT_TIMEOUT', None)!r}, expected 600"
PYEOF
then echo "PASS: DEFAULT_TIMEOUT constant is 600 (sized for cold local models)"; PASS=$((PASS+1))
else echo "FAIL: DEFAULT_TIMEOUT constant missing or not 600"; FAIL=$((FAIL+1)); fi

rm -f /tmp/oa-out.$$ /tmp/oa-err.$$
echo "----"
echo "ollama-agent: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
