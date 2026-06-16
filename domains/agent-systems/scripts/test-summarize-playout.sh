#!/usr/bin/env bash
# test-summarize-playout.sh (cycle-004, Sprint 18). Hermetic: project the committed
# native sidecar into playout-summary/v1 and assert the projection is correct,
# deterministic, and refuses unknown stop_reasons. No grade is ever computed.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SP="python3 $SCRIPT_DIR/summarize_playout.py"
FIX="$REPO_ROOT/domains/agent-systems/resources/fixtures/native-sidecar.events.yaml"
SHA="0000000000000000000000000000000000000000000000000000000000000000"

PASS=0; FAIL=0
ok() { if eval "$2"; then echo "PASS: $1"; PASS=$((PASS+1)); else echo "FAIL: $1"; FAIL=$((FAIL+1)); fi; }

W=$(mktemp -d)
trap 'rm -rf "$W" 2>/dev/null' EXIT

# 1. Projects the committed sidecar cleanly
$SP --sidecar "$FIX" --scenario-sha256 "$SHA" > "$W/out1.json" 2> "$W/err1"
ok "projection exits 0" "[ \$? -eq 0 ]"
ok "schema is playout-summary/v1" "grep -q '\"playout-summary/v1\"' '$W/out1.json'"
ok "lane is simulated" "grep -q '\"lane\": \"simulated\"' '$W/out1.json'"
ok "producer label quoted verbatim" "grep -q '\"claim_strength\": \"simulation-derived\"' '$W/out1.json'"
ok "scenario_sha256 carried through" "grep -q '$SHA' '$W/out1.json'"
ok "action_label slug projected (not prose)" "grep -q '\"add-positive-filter\"' '$W/out1.json'"
ok "outcome_signal mapped from stop_reason" "grep -q '\"outcome_signal\": \"task-declared-done\"' '$W/out1.json'"
ok "prose narrated_action is NOT in the summary" "! grep -qi 'missing positive filter' '$W/out1.json'"

# 2. Deterministic: byte-identical on a second run
$SP --sidecar "$FIX" --scenario-sha256 "$SHA" > "$W/out2.json" 2>/dev/null
ok "deterministic (byte-equal across runs)" "diff -q '$W/out1.json' '$W/out2.json' >/dev/null"

# 3. Unknown stop_reason -> exit 1 (never invents an outcome_signal)
cat > "$W/bad.yaml" <<'YAML'
preamble:
  scenario_id: bad-stop
events:
  - type: rung_start
    seq: 1
    at: "2026-01-01T00:00:00Z"
    rung: 0
    rung_name: blind
    trial: 1
  - type: trial_end
    seq: 2
    at: "2026-01-01T00:00:01Z"
    status: completed
    turns_used: 1
    stop_reason: teleported
YAML
$SP --sidecar "$W/bad.yaml" --scenario-sha256 "$SHA" > /dev/null 2> "$W/err3"
ok "unknown stop_reason exits 1" "[ \$? -eq 1 ]"
ok "error names the tool" "grep -q 'ERROR: \[summarize_playout\]' '$W/err3'"

# 4. Usage error on missing args
$SP --sidecar "$FIX" > /dev/null 2>&1
ok "missing --scenario-sha256 exits 1" "[ \$? -eq 1 ]"

echo "---"
echo "summarize_playout: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
