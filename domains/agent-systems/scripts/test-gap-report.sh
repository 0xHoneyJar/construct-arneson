#!/usr/bin/env bash
# test-gap-report.sh (cycle-004, Sprint 20). The gate for gap_report.py:
# golden byte-match, banned-copy clean, pairing refusal, stdlib-only, read-only.
# Hermetic; nonzero on any failure. Mirrors test-sweep-report.sh shape.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
GR="python3 $SCRIPT_DIR/gap_report.py"
FIX="$REPO_ROOT/domains/agent-systems/resources/fixtures/gap-report"
# Single ban-list source of truth (shared with scripts/ci/banned-copy-check.sh).
# shellcheck source=../../../scripts/ci/banned-phrases.sh
source "$REPO_ROOT/scripts/ci/banned-phrases.sh"

PASS=0; FAIL=0
ok() { if eval "$2"; then echo "PASS: $1"; PASS=$((PASS+1)); else echo "FAIL: $1"; FAIL=$((FAIL+1)); fi; }

W=$(mktemp -d)
trap 'rm -rf "$W" 2>/dev/null' EXIT

# 1. Golden byte-match (SM-1)
report=$($GR --sim "$FIX/sim.summary.json" --real "$FIX/real.playout.yaml" --out-dir "$W/out")
ok "gap_report exits 0 on valid pair" "[ \$? -eq 0 ]"
ok "golden byte-match (SM-1)" "diff -q '$FIX/gap-report.golden.md' '$report' >/dev/null"

# 2. Banned-copy clean over the freshly generated report (SM-3)
ok "report has no banned phrases (SM-3)" "! grep -niE \"\$BANNED\" '$report'"

# 3. Pairing refusal: scenario_sha256 mismatch -> exit 2 (SM-4)
$GR --sim "$FIX/sim.summary.json" --real "$FIX/mismatch.real.playout.yaml" --out-dir "$W/out" > /dev/null 2> "$W/err"
ok "scenario_sha256 mismatch exits 2 (SM-4)" "[ \$? -eq 2 ]"
ok "refusal names both shas" "grep -q 'scenario_sha256 mismatch: sim=.* real=' '$W/err'"

# 4. Deterministic body across two runs (NFR-6)
r2=$($GR --sim "$FIX/sim.summary.json" --real "$FIX/real.playout.yaml" --out-dir "$W/out2")
ok "deterministic body (NFR-6)" "diff -q '$report' '$r2' >/dev/null"

# 5. stdlib-only: no third-party import in gap_report.py (NFR-1)
#    Allowed imports: stdlib + local siblings restricted_yaml, triage_lib.
thirdparty=$(grep -nE '^(import|from) ' "$SCRIPT_DIR/gap_report.py" \
  | grep -vE 'import (json|os|sys|re)|from (datetime|pathlib|collections) import|from (restricted_yaml|triage_lib) import' || true)
ok "no third-party imports in gap_report.py (NFR-1)" "[ -z \"\$thirdparty\" ]"
# Target actual import/call lines, not the trust-rule docstring that NAMES these.
badimport=$(grep -nE '^[[:space:]]*(import|from)[[:space:]].*(subprocess|gygax)' "$SCRIPT_DIR/gap_report.py" || true)
badcall=$(grep -nE 'os\.system|os\.popen|Popen|subprocess\.' "$SCRIPT_DIR/gap_report.py" || true)
ok "no subprocess / shell-out / gygax import (FR-8/NFR-2)" "[ -z \"\$badimport\" ] && [ -z \"\$badcall\" ]"

# 6. Read-only: real batch bytes unchanged after a run (FR-8)
before=$(find "$FIX/real-batch" -type f -exec shasum {} \; | sort | shasum)
$GR --sim "$FIX/sim.summary.json" --real "$FIX/real.playout.yaml" --out-dir "$W/out3" > /dev/null 2>&1
after=$(find "$FIX/real-batch" -type f -exec shasum {} \; | sort | shasum)
ok "real batch is read-only (FR-8)" "[ \"\$before\" = \"\$after\" ]"

echo "---"
echo "gap-report: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
