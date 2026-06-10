#!/usr/bin/env bash
# Live sweep proof (arneson-with-gygax CI leg; Sprint 3, Task 3.5; FR-1/FR-8).
# Drives ≥2 configs through the REAL Gygax engine with the deterministic no-spend
# agent, then assembles the cross-config triaged table via sweep_report.py.
# Proves: per-config runs work, batches are byte-untouched, the table assembles.
# No API spend (deterministic agent), no Ollama (not a model). Needs node + sibling.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AGENT="$REPO_ROOT/domains/agent-systems/resources/fixtures/deterministic-agent.py"
FIXTURE="$REPO_ROOT/domains/agent-systems/resources/fixtures/synthetic-incentive"
SR="$REPO_ROOT/domains/agent-systems/scripts/sweep_report.py"
VB="$REPO_ROOT/domains/agent-systems/scripts/validate_batch.py"

ENGINE_ROOT=$(python3 "$REPO_ROOT/domains/agent-systems/scripts/discover_engine.py")
echo "== engine: $ENGINE_ROOT"

run_config() {  # label rungs -> echoes batch_dir
  local label="$1" rungs="$2"
  local result
  result=$(cd "$ENGINE_ROOT" && npx tsx scripts/lib/ladder/index.ts run \
    --fixture "$FIXTURE" --rungs "$rungs" --trials 1 \
    --agent-cmd "python3 $AGENT {promptfile}" --timeout 120 --json 2>/dev/null)
  python3 -c "import json,sys; print(json.load(sys.stdin)['batch_dir'])" <<<"$result"
}

echo "== sweep: 2 configs through the real engine (deterministic agent, no spend) =="
BATCH_A=$(run_config configA 0)
BATCH_B=$(run_config configB 2)
echo "  configA batch: $BATCH_A"
echo "  configB batch: $BATCH_B"

echo "== byte-untouched conformance per config =="
python3 "$VB" "$BATCH_A"
python3 "$VB" "$BATCH_B"

echo "== regrade each (Gygax fills observation) =="
( cd "$ENGINE_ROOT" && npx tsx scripts/lib/trace/index.ts "$BATCH_A" --regrade >/dev/null 2>&1 )
( cd "$ENGINE_ROOT" && npx tsx scripts/lib/trace/index.ts "$BATCH_B" --regrade >/dev/null 2>&1 )

echo "== cross-config triaged table =="
python3 "$SR" --config "configA=$BATCH_A" --config "configB=$BATCH_B" | tee /tmp/sweep-probe-table.txt

echo "== assertions =="
grep -q "configA" /tmp/sweep-probe-table.txt || { echo "FAIL: configA row missing"; exit 1; }
grep -q "configB" /tmp/sweep-probe-table.txt || { echo "FAIL: configB row missing"; exit 1; }
grep -qi "never recomputed" /tmp/sweep-probe-table.txt || { echo "FAIL: trust-boundary legend missing"; exit 1; }

echo "OK: live sweep proof — 2 configs graded + assembled into one triaged table, batches byte-untouched."
