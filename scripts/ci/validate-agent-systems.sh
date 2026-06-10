#!/usr/bin/env bash
# Hermetic agent-systems vertical check (arneson-alone CI leg; FR-14).
# Runs the three validator test suites and validates the committed fixture batch.
# No network, no Gygax, no LLM — the deterministic toolchain under test.

set -euo pipefail

DOMAIN="domains/agent-systems"

if [ ! -d "$DOMAIN" ]; then
  echo "FAIL: $DOMAIN missing"
  exit 1
fi

echo "== agent-systems: validator test suites =="
"$DOMAIN/scripts/test-validate-scenario.sh"
"$DOMAIN/scripts/test-validate-sidecar.sh"
"$DOMAIN/scripts/test-validate-batch.sh"
"$DOMAIN/scripts/test-discover-engine.sh"
"$DOMAIN/scripts/test-ollama-agent.sh"

echo "== agent-systems: projection round-trip + hermetic playout (simulated lane) =="
"$DOMAIN/scripts/test-sim-pipeline.sh"

echo "== agent-systems: dungeon fixture — referee determinism + party wrapper (v4.1) =="
"$DOMAIN/scripts/test-dungeon-referee.sh"
"$DOMAIN/scripts/test-party-wrapper.sh"

echo "== agent-systems: rigor — cross-config sweep report + payoff-dominance (v4.1) =="
"$DOMAIN/scripts/test-sweep-report.sh"
"$DOMAIN/scripts/test-check-payoff-dominance.sh"

echo "== agent-systems: versatility — scaffolder + banned-copy honesty gate (v4.1) =="
"$DOMAIN/scripts/test-scaffold-playtest.sh"
scripts/ci/banned-copy-check.sh

echo "== agent-systems: committed fixture batch conformance =="
python3 "$DOMAIN/scripts/validate_batch.py" "$DOMAIN/resources/fixtures/batches/valid-batch"
python3 "$DOMAIN/scripts/validate_batch.py" "$DOMAIN/resources/fixtures/batches/dungeon-sample"

echo "OK: agent-systems vertical hermetic checks green."
