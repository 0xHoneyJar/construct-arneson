#!/usr/bin/env bash
# test-vendor-drift-guard.sh (sprint-2, global #17, G-5).
# Regression test for the source↔vendor signal-taxonomy convergence guard added
# to scripts/ci/vendor-drift-guard.sh. The guard exits early when the gygax
# sibling is absent, so this test SKIPs cleanly without it; CI always has the
# sibling checked out (.github/workflows/ci.yaml).
#
# Proves both directions of the AC: green on a clean tree, and a LOUD non-zero
# exit when the source signal.classification enum is reordered relative to the
# vendored taxonomy. The real source file is mutated transiently and restored
# via an EXIT trap so an interrupted run can never leave it dirty.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

GUARD=./scripts/ci/vendor-drift-guard.sh
GYGAX_ROOT="${ARNESON_GYGAX_ROOT:-../construct-gygax}"
SRC=schemas/core/session-events-base.schema.yaml

if [ ! -d "$GYGAX_ROOT/schemas" ]; then
  echo "SKIP: no gygax sibling at $GYGAX_ROOT — convergence regression test needs upstream present."
  exit 0
fi
export ARNESON_GYGAX_ROOT="$GYGAX_ROOT"

PASS=0; FAIL=0
ok() { if eval "$2"; then echo "PASS: $1"; PASS=$((PASS+1)); else echo "FAIL: $1"; FAIL=$((FAIL+1)); fi; }

# Positive: a clean tree passes (byte-diff + pin + convergence all green).
ok "guard green on clean tree" "$GUARD >/dev/null 2>&1"

# Negative: reorder the source signal enum → convergence guard must fail loudly.
BACKUP="$(mktemp)"
cp "$SRC" "$BACKUP"
trap 'cp "$BACKUP" "$SRC"; rm -f "$BACKUP"' EXIT
python3 - "$SRC" <<'PYEOF'
import sys
from pathlib import Path
p = Path(sys.argv[1])
t = p.read_text()
t = t.replace("values: [safety, insight, concern,", "values: [insight, safety, concern,", 1)
p.write_text(t)
PYEOF
ok "guard fails on reordered source enum" "! $GUARD >/dev/null 2>&1"

# Restore and confirm the tree is clean again.
cp "$BACKUP" "$SRC"; rm -f "$BACKUP"; trap - EXIT
ok "guard green after restore" "$GUARD >/dev/null 2>&1"

echo "SUMMARY: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
