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

echo "== agent-systems: committed fixture batch conformance =="
python3 "$DOMAIN/scripts/validate_batch.py" "$DOMAIN/resources/fixtures/batches/valid-batch"

echo "OK: agent-systems vertical hermetic checks green."
