#!/usr/bin/env bash
# test-emit-decision-trace.sh (cycle-007, Sprint 1, FR-1). The gate for
# emit_decision_trace.py: golden byte-match, self-validating records, determinism,
# degenerate exit 1, broken-self-output exit 2, claim honesty, stdlib-only /
# no-gygax, banned-copy clean. Hermetic; nonzero on any failure. Auto-discovered
# by scripts/test.sh. Mirrors test-gap-report.sh shape.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
EMIT="python3 $SCRIPT_DIR/emit_decision_trace.py"
FIX="$REPO_ROOT/domains/agent-systems/resources/fixtures/decision-trace"
GOLDEN="$FIX/golden"
# Single ban-list source of truth (shared with scripts/ci/banned-copy-check.sh).
# shellcheck source=../../../scripts/ci/banned-phrases.sh
source "$REPO_ROOT/scripts/ci/banned-phrases.sh"

PASS=0; FAIL=0
ok() { if eval "$2"; then echo "PASS: $1"; PASS=$((PASS+1)); else echo "FAIL: $1"; FAIL=$((FAIL+1)); fi; }

W=$(mktemp -d)
trap 'rm -rf "$W" 2>/dev/null' EXIT

# 1. Emitter exits 0 on the canonical fixture (records self-validate; SM-1a).
$EMIT --in "$FIX/sim-episode.events.yaml" --out "$W/out" >/dev/null 2>"$W/err"; rc=$?
ok "emitter exits 0 on a valid sim episode (self-validated, SM-1a)" "[ $rc -eq 0 ]"

# 2. Golden byte-match — the corpus is byte-stable against the committed golden (SM-1).
ok "golden byte-match t=0 (SM-1)" \
  "diff -q '$GOLDEN/synthetic-simulated-smoke-dt-run-1-0.json' '$W/out/synthetic-simulated-smoke-dt-run-1-0.json' >/dev/null"
ok "golden byte-match t=1 (SM-1)" \
  "diff -q '$GOLDEN/synthetic-simulated-smoke-dt-run-1-1.json' '$W/out/synthetic-simulated-smoke-dt-run-1-1.json' >/dev/null"

# 3. Determinism — a second run is byte-identical to the first (NFR-3).
$EMIT --in "$FIX/sim-episode.events.yaml" --out "$W/out2" >/dev/null 2>&1
ok "deterministic across runs (NFR-3)" "diff -rq '$W/out' '$W/out2' >/dev/null"

# 4. Degenerate input (no action_label anywhere) -> exit 1.
$EMIT --in "$FIX/degenerate.events.yaml" --out "$W/degen" >/dev/null 2>"$W/derr"; rc=$?
ok "degenerate input exits 1" "[ $rc -eq 1 ]"
ok "degenerate refusal names the emitter" "grep -q 'ERROR: \[emit_decision_trace\]' '$W/derr'"

# 5. Broken self-output (empty action_label -> empty option type) -> exit 2.
$EMIT --in "$FIX/broken-label.events.yaml" --out "$W/broken" >/dev/null 2>"$W/berr"; rc=$?
ok "broken self-output exits 2 (never ship a broken corpus)" "[ $rc -eq 2 ]"
ok "exit-2 refusal cites the vendored contract" "grep -q 'vendored contract' '$W/berr'"

# 6. Claim honesty — every record is simulation-derived / producer.kind simulation (NFR-5).
ok "both records carry simulation-derived (NFR-5)" \
  "[ \"\$(grep -RIl 'simulation-derived' '$W/out' | wc -l | tr -d ' ')\" = 2 ]"
ok "no real-agent leaks into a sim corpus (NFR-5)" \
  "! grep -RIl 'real-agent' '$W/out' >/dev/null"

# 7. stdlib-only + zero gygax coupling (NFR-1).
thirdparty=$(grep -nE '^(import|from) ' "$SCRIPT_DIR/emit_decision_trace.py" \
  | grep -vE 'import (hashlib|json|re|sys)|from pathlib import|from restricted_yaml import' || true)
ok "no third-party imports (NFR-1)" "[ -z \"\$thirdparty\" ]"
badimport=$(grep -nE '^[[:space:]]*(import|from)[[:space:]].*(subprocess|gygax)' "$SCRIPT_DIR/emit_decision_trace.py" || true)
badcall=$(grep -nE 'os\.system|os\.popen|Popen|subprocess\.' "$SCRIPT_DIR/emit_decision_trace.py" || true)
ok "no subprocess / shell-out / gygax import (NFR-1/NFR-2)" "[ -z \"\$badimport\" ] && [ -z \"\$badcall\" ]"
ok "zero construct-gygax imports/refs in the emitter (NFR-1)" \
  "! grep -nE 'construct-gygax|construct_gygax' '$SCRIPT_DIR/emit_decision_trace.py'"

# 8. Banned-copy clean over the generated corpus (NFR-7).
ok "generated corpus has no banned phrases (NFR-7)" "! grep -RniE \"\$BANNED\" '$W/out'"

echo "---"
echo "emit-decision-trace: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
