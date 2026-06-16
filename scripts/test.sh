#!/usr/bin/env bash
# Unified test runner (FR-10, cycle-004). The single local + CI front door for the
# repo's tests. Discovers every domains/*/scripts/test-*.sh by glob (so new tests —
# like test-gap-report.sh — are picked up with zero wiring) and runs each. Exits
# nonzero if any test script fails. stdlib bash tools only — NOT pytest/npm.
#
# Relationship to scripts/ci/ (OQ-4: complement, not supersede): this runner covers
# the domain test-*.sh suite. The specialized ci/ probes (e.g. banned-copy-check.sh,
# validate-construct.sh) remain their own CI steps; CI may also call this runner as
# one step. It does not duplicate those legs.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail=0
ran=0

for t in "$REPO_ROOT"/domains/*/scripts/test-*.sh; do
  [ -f "$t" ] || continue
  ran=$((ran + 1))
  echo "== ${t#$REPO_ROOT/}"
  if ! bash "$t"; then
    echo "!! FAILED: ${t#$REPO_ROOT/}"
    fail=1
  fi
done

echo "============================================================"
if [ "$ran" -eq 0 ]; then
  echo "WARNING: no domains/*/scripts/test-*.sh discovered"
  exit 1
fi
if [ "$fail" -eq 0 ]; then
  echo "OK: all $ran test script(s) passed"
else
  echo "FAIL: one or more of $ran test script(s) failed"
fi
exit "$fail"
