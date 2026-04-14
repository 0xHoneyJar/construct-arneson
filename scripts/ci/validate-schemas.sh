#!/usr/bin/env bash
# Validate each schema file parses as YAML and has required top-level 'schema' block.
# Does NOT enforce schema-of-schemas — these are declarative schemas in YAML, not JSON Schema.

set -euo pipefail

SCHEMAS_DIR="schemas"

if [ ! -d "$SCHEMAS_DIR" ]; then
  echo "FAIL: $SCHEMAS_DIR directory missing"
  exit 1
fi

EXPECTED_SCHEMAS=(
  "experiential_intent.schema.yaml"
  "voice-base.schema.yaml"
  "voice-archetype.schema.yaml"
  "voice-npc.schema.yaml"
  "voice-pc.schema.yaml"
  "session-events.schema.yaml"
  "digest.schema.yaml"
)

FAIL=0

for schema_file in "${EXPECTED_SCHEMAS[@]}"; do
  path="$SCHEMAS_DIR/$schema_file"
  if [ ! -f "$path" ]; then
    echo "FAIL: expected schema $path missing"
    FAIL=1
    continue
  fi

  # Parse as YAML
  if ! yq eval '.' "$path" > /dev/null 2>&1; then
    echo "FAIL: $path does not parse as YAML"
    FAIL=1
    continue
  fi

  # Require top-level 'schema' key with name and version
  name=$(yq eval '.schema.name' "$path" 2>/dev/null)
  version=$(yq eval '.schema.version' "$path" 2>/dev/null)
  if [ -z "$name" ] || [ "$name" = "null" ]; then
    echo "FAIL: $path missing schema.name"
    FAIL=1
  fi
  if [ -z "$version" ] || [ "$version" = "null" ]; then
    echo "FAIL: $path missing schema.version"
    FAIL=1
  fi
done

if [ $FAIL -eq 1 ]; then
  exit 1
fi

echo "OK: all 7 schemas parse and have required schema.name + schema.version."
