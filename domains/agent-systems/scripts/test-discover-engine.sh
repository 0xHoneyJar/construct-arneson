#!/usr/bin/env bash
# Shell test for discover_engine.py — all three resolution paths + absence cases.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DE="python3 $SCRIPT_DIR/discover_engine.py"

PASS=0; FAIL=0

check() { # name expected_exit cmd...
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/de-out.$$ 2>/tmp/de-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then
    echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — expected exit $expected, got $got"
    sed 's/^/    /' /tmp/de-err.$$ | head -3
    FAIL=$((FAIL+1))
  fi
}

check_out() {
  local name="$1" pattern="$2" file="$3"
  if grep -q "$pattern" "$file"; then
    echo "PASS: $name"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — missing pattern: $pattern"; FAIL=$((FAIL+1))
  fi
}

# Fake engine tree for hermetic tests (real sibling may or may not exist on CI).
FAKE=$(mktemp -d)
mkdir -p "$FAKE/engine/scripts/lib/ladder" "$FAKE/hollow"
touch "$FAKE/engine/scripts/lib/ladder/index.ts"

# 1. --engine flag (valid)
check "--engine flag resolves" 0 $DE --engine "$FAKE/engine"
check_out "flag path printed to stdout" "engine" /tmp/de-out.$$

# 2. --engine flag pointing at a hollow dir: authoritative, NO fallback
ARNESON_GYGAX_ROOT="$FAKE/engine" check "--engine hollow dir fails (no silent fallback to env)" 1 \
  env ARNESON_GYGAX_ROOT="$FAKE/engine" python3 "$SCRIPT_DIR/discover_engine.py" --engine "$FAKE/hollow"
check_out "FR-6 message names the dependency" "MISSING DEPENDENCY: construct-gygax engine not found" /tmp/de-err.$$
check_out "FR-6 message points at simulated mode" "Simulated mode works standalone" /tmp/de-err.$$

# 3. env var (valid), no flag
check "ARNESON_GYGAX_ROOT resolves" 0 env ARNESON_GYGAX_ROOT="$FAKE/engine" python3 "$SCRIPT_DIR/discover_engine.py"

# 4. env var hollow: authoritative, no sibling fallback
check "hollow env root fails (no silent fallback to sibling)" 1 \
  env ARNESON_GYGAX_ROOT="$FAKE/hollow" python3 "$SCRIPT_DIR/discover_engine.py"

# 5. sibling probe — exercised only when the real sibling checkout exists
if [ -f "$SCRIPT_DIR/../../../../construct-gygax/scripts/lib/ladder/index.ts" ]; then
  check "sibling probe resolves (real checkout present)" 0 $DE
else
  check "sibling probe absent -> FR-6 failure" 1 $DE
fi

# 6. usage errors
check "--engine without value" 1 $DE --engine
check "unexpected positional arg" 1 $DE stray

rm -rf "$FAKE/engine" "$FAKE/hollow" && rmdir "$FAKE" 2>/dev/null
rm -f /tmp/de-out.$$ /tmp/de-err.$$
echo "----"
echo "discover_engine: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
