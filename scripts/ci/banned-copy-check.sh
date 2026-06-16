#!/usr/bin/env bash
# Banned-copy check (FR-3/G5/NFR-7). The honesty boundary, mechanized.
# Scans agent-systems prose docs + the sweep report wording for overclaiming
# phrases (sandbox-limits §A/B). The ONE legitimate home for these phrases is the
# ban-list table in domain.conventions.md — quoted table rows (lines starting with
# `| "`) are excluded; a violation anywhere else fails the build.
set -euo pipefail

DOCS="domains/agent-systems/docs"
CONV="domains/agent-systems/domain.conventions.md"
REPORT="domains/agent-systems/scripts/sweep_report.py"
GAP_REPORT="domains/agent-systems/scripts/gap_report.py"

# Single ban-list source of truth (shared with test-gap-report.sh).
# shellcheck source=scripts/ci/banned-phrases.sh
source "$(dirname "${BASH_SOURCE[0]}")/banned-phrases.sh"

fail=0
scan() {  # file
  local f="$1"
  [ -f "$f" ] || return 0
  # drop ban-list table rows (a quoted phrase in a markdown table cell: line starts with | ")
  local hits
  hits=$(grep -niE "$BANNED" "$f" 2>/dev/null | grep -vE '^[0-9]+:[[:space:]]*\|[[:space:]]*"' || true)
  if [ -n "$hits" ]; then
    echo "BANNED-COPY in $f:"
    echo "$hits" | sed 's/^/    /'
    fail=1
  fi
}

for f in "$DOCS"/*.md; do scan "$f"; done
scan "$CONV"
scan "$REPORT"
scan "$GAP_REPORT"

if [ "$fail" -ne 0 ]; then
  echo "FAIL: banned-copy violations found (sandbox-limits §A/B). Reframe; the ban list + 'say instead' guidance is in domain.conventions.md."
  exit 1
fi
echo "OK: banned-copy clean across agent-systems docs + report wording."
