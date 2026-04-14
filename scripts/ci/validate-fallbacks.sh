#!/usr/bin/env bash
# Validate the 9-archetype fallback bundle.
# Each YAML must parse, have required fields per voice-archetype schema, and be marked fallback_source: true.

set -euo pipefail

FALLBACK_DIR="resources/archetypes-fallback"

EXPECTED_ARCHETYPES=(
  newcomer
  optimizer
  chaos-agent
  storyteller
  rules-lawyer
  explorer
  min-maxer
  casual
  contrarian
)

FAIL=0

if [ ! -d "$FALLBACK_DIR" ]; then
  echo "FAIL: $FALLBACK_DIR directory missing"
  exit 1
fi

for archetype in "${EXPECTED_ARCHETYPES[@]}"; do
  path="$FALLBACK_DIR/$archetype.yaml"
  if [ ! -f "$path" ]; then
    echo "FAIL: fallback archetype $archetype missing ($path)"
    FAIL=1
    continue
  fi

  # Parse
  if ! yq eval '.' "$path" > /dev/null 2>&1; then
    echo "FAIL: $path does not parse as YAML"
    FAIL=1
    continue
  fi

  # Required fields per voice-archetype.schema.yaml
  voice_id=$(yq eval '.voice_id' "$path")
  archetype_ref=$(yq eval '.archetype_ref' "$path")
  fallback_source=$(yq eval '.fallback_source' "$path")

  if [ "$voice_id" != "$archetype" ]; then
    echo "FAIL: $path voice_id mismatch (expected $archetype, got $voice_id)"
    FAIL=1
  fi
  if [ "$archetype_ref" != "$archetype" ]; then
    echo "FAIL: $path archetype_ref mismatch (expected $archetype, got $archetype_ref)"
    FAIL=1
  fi
  if [ "$fallback_source" != "true" ]; then
    echo "FAIL: $path must be marked fallback_source: true (got $fallback_source)"
    FAIL=1
  fi

  # experiential_intent_weights must have at least 3 entries (per validation rule)
  weight_count=$(yq eval '.experiential_intent_weights | length' "$path")
  if [ "$weight_count" -lt 3 ]; then
    echo "FAIL: $path has fewer than 3 experiential_intent_weights entries"
    FAIL=1
  fi

  # At least one distinctive_marker
  marker_count=$(yq eval '.speech_patterns.distinctive_markers | length' "$path")
  if [ "$marker_count" -lt 1 ]; then
    echo "FAIL: $path has no distinctive_markers (voice must be distinct)"
    FAIL=1
  fi
done

# Chaos Agent MUST have chaos_axis_config populated
chaos_path="$FALLBACK_DIR/chaos-agent.yaml"
if [ -f "$chaos_path" ]; then
  chaos_config=$(yq eval '.chaos_axis_config' "$chaos_path")
  if [ "$chaos_config" = "null" ]; then
    echo "FAIL: chaos-agent.yaml missing required chaos_axis_config"
    FAIL=1
  fi
fi

if [ $FAIL -eq 1 ]; then
  exit 1
fi

echo "OK: 9 fallback archetypes validate — voice_id/archetype_ref consistent, fallback_source: true, distinctive_markers present, Chaos Agent bounded."
