#!/usr/bin/env bash
# Zero-edit ingestion probe (arneson-with-gygax CI leg; milestone b, FR-14).
#
# Drives the REAL pipeline end-to-end with a deterministic no-spend agent:
#   engine run → Arneson conformance gate (byte-untouched) → trace --regrade → diff
#
# Acceptance is the contract's own: "a batch produced entirely outside Gygax …
# is graded and diffed with zero manual edits" (observed-trace-batch.v1.md:107-109).
# Probe fixture: Arneson's bundled synthetic-incentive fixture — ours, format-true,
# decoupled from upstream fixture churn.
#
# Requires: node + npx in PATH, a real Gygax checkout (ARNESON_GYGAX_ROOT or sibling).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AGENT="$REPO_ROOT/domains/agent-systems/resources/fixtures/deterministic-agent.py"

ENGINE_ROOT=$(python3 "$REPO_ROOT/domains/agent-systems/scripts/discover_engine.py")
echo "== engine: $ENGINE_ROOT"

FIXTURE="$REPO_ROOT/domains/agent-systems/resources/fixtures/synthetic-incentive"

echo "== engine run (deterministic agent, rungs 0,2 × 1 trial — no API spend) =="
RESULT=$(cd "$ENGINE_ROOT" && npx tsx scripts/lib/ladder/index.ts run \
  --fixture "$FIXTURE" \
  --rungs 0,2 --trials 1 \
  --agent-cmd "python3 $AGENT {promptfile}" \
  --timeout 60 --json)
echo "$RESULT"

BATCH_DIR=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['batch_dir'])")
echo "== batch: $BATCH_DIR"

echo "== Arneson conformance gate (byte-untouched) =="
if ! python3 "$REPO_ROOT/domains/agent-systems/scripts/validate_batch.py" "$BATCH_DIR"; then
  echo "FAIL: engine-produced batch is nonconformant."
  echo "      Known upstream gap? See grimoires/loa/discovery/gygax-seam-bugs-cycle008.md"
  echo "      (Bug 2: runner omits the contract-required batch.json 'schema' field)."
  exit 1
fi

echo "== analyst regrade ingest (the grade that counts) =="
(cd "$ENGINE_ROOT" && npx tsx scripts/lib/trace/index.ts "$BATCH_DIR" --regrade) | tee /tmp/probe-report.txt

echo "== assertions =="
grep -q "Observed per rung" /tmp/probe-report.txt || { echo "FAIL: no observed-per-rung table in report"; exit 1; }
grep -qE "argmax|forecast" /tmp/probe-report.txt || { echo "FAIL: no forecast line in report"; exit 1; }

echo "OK: zero-edit ingestion probe complete — engine batch graded + diffed, no edits anywhere."
