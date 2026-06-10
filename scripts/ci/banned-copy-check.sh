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

BANNED='hard metrics|zero hallucination|high-fidelity|proves it'"'"'?s compelling|validates your incentives|effectively real|as good as observed'

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

if [ "$fail" -ne 0 ]; then
  echo "FAIL: banned-copy violations found (sandbox-limits §A/B). Reframe; the ban list + 'say instead' guidance is in domain.conventions.md."
  exit 1
fi
echo "OK: banned-copy clean across agent-systems docs + report wording."
