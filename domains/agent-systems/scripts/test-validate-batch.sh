#!/usr/bin/env bash
# Shell test for validate_batch.py — committed batch happy path, layout violations,
# run_dir escape containment, and the ungraded-simulation honesty warning.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FIXTURES="$DOMAIN_DIR/resources/fixtures"
VB="python3 $SCRIPT_DIR/validate_batch.py"

PASS=0; FAIL=0

check() {
  local name="$1" expected="$2"; shift 2
  "$@" >/tmp/vb-out.$$ 2>/tmp/vb-err.$$
  local got=$?
  if [ "$got" -eq "$expected" ]; then
    echo "PASS: $name (exit $got)"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — expected exit $expected, got $got"
    sed 's/^/    /' /tmp/vb-err.$$ | head -5
    FAIL=$((FAIL+1))
  fi
}

check_msg() {
  local name="$1" pattern="$2"
  if grep -q "$pattern" /tmp/vb-err.$$; then
    echo "PASS: $name"; PASS=$((PASS+1))
  else
    echo "FAIL: $name — stderr missing pattern: $pattern"; FAIL=$((FAIL+1))
  fi
}

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Happy path: the committed fixture batch
check "committed fixture batch conformant" 0 $VB "$FIXTURES/batches/valid-batch"

# missing batch.json
mkdir -p "$TMP/no-manifest/sidecars"
cp "$FIXTURES/batches/valid-batch/sidecars/rung-0-trial-1.json" "$TMP/no-manifest/sidecars/"
check "missing batch.json rejected" 2 $VB "$TMP/no-manifest"
check_msg "names the grade-on-ingest requirement" "batch.json missing"

# wrong batch schema string
cp -R "$FIXTURES/batches/valid-batch" "$TMP/wrong-schema"
python3 - "$TMP/wrong-schema/batch.json" <<'PYEOF'
import json, sys
p = sys.argv[1]
m = json.load(open(p)); m["schema"] = "observed-trace-batch/v2"
json.dump(m, open(p, "w"))
PYEOF
check "wrong batch.json schema rejected" 2 $VB "$TMP/wrong-schema"

# run_dir escapes the batch dir
cp -R "$FIXTURES/batches/valid-batch" "$TMP/escape"
python3 - "$TMP/escape/sidecars/rung-0-trial-1.json" <<'PYEOF'
import json, sys
p = sys.argv[1]
o = json.load(open(p)); o["run"]["run_dir"] = "../../outside"
json.dump(o, open(p, "w"))
PYEOF
check "run_dir escaping batch dir rejected" 2 $VB "$TMP/escape"
check_msg "containment message" "escapes the batch directory"

# run_dir missing on disk
cp -R "$FIXTURES/batches/valid-batch" "$TMP/missing-rundir"
rm -rf "$TMP/missing-rundir/runs"
check "missing run_dir tree rejected" 2 $VB "$TMP/missing-rundir"

# nonconformant sidecar inside an otherwise-valid batch
cp -R "$FIXTURES/batches/valid-batch" "$TMP/bad-sidecar"
cp "$FIXTURES/violations/laundering-sim-as-real.json" "$TMP/bad-sidecar/sidecars/rung-0-trial-2.json"
mkdir -p "$TMP/bad-sidecar/runs/rung-0/trial-1"
check "batch with laundering sidecar rejected" 2 $VB "$TMP/bad-sidecar"

# no sidecars at all
mkdir -p "$TMP/empty"
cp "$FIXTURES/batches/valid-batch/batch.json" "$TMP/empty/"
check "batch with zero sidecars rejected" 2 $VB "$TMP/empty"

# honesty warning: completed simulation sidecar, ungraded → exit 0 + WARNING
cp -R "$FIXTURES/batches/valid-batch" "$TMP/sim-ungraded"
python3 - "$TMP/sim-ungraded/sidecars/rung-0-trial-1.json" <<'PYEOF'
import json, sys
p = sys.argv[1]
o = json.load(open(p))
o["producer"]["kind"] = "simulation"
o["claim_strength"] = "simulation-derived"
json.dump(o, open(p, "w"))
PYEOF
check "ungraded simulation batch passes layout" 0 $VB "$TMP/sim-ungraded"
check_msg "but warns it is not ingestible until scored" "not Gygax-ingestible until scored"

# input errors
check "nonexistent batch dir" 1 $VB "$TMP/never-was"

rm -f /tmp/vb-out.$$ /tmp/vb-err.$$
echo "----"
echo "validate_batch: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
