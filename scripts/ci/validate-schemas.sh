#!/usr/bin/env bash
# Validate each schema file parses as YAML and has required top-level 'schema' block.
# Does NOT enforce schema-of-schemas — these are declarative schemas in YAML, not JSON Schema.

set -euo pipefail

CORE_SCHEMAS_DIR="schemas/core"
TTRPG_SCHEMAS_DIR="domains/ttrpg/schemas"

if [ ! -d "$CORE_SCHEMAS_DIR" ]; then
  echo "FAIL: $CORE_SCHEMAS_DIR directory missing"
  exit 1
fi

if [ ! -d "$TTRPG_SCHEMAS_DIR" ]; then
  echo "FAIL: $TTRPG_SCHEMAS_DIR directory missing"
  exit 1
fi

# Core schemas (domain-agnostic) + TTRPG schemas (reference vertical)
# Format: "dir:filename"
EXPECTED_SCHEMAS=(
  "$CORE_SCHEMAS_DIR:experiential_intent.schema.yaml"
  "$CORE_SCHEMAS_DIR:voice-base.schema.yaml"
  "$CORE_SCHEMAS_DIR:session-events-base.schema.yaml"
  "$CORE_SCHEMAS_DIR:digest-base.schema.yaml"
  "$CORE_SCHEMAS_DIR:safety.schema.yaml"
  "$TTRPG_SCHEMAS_DIR:voice-archetype.schema.yaml"
  "$TTRPG_SCHEMAS_DIR:voice-npc.schema.yaml"
  "$TTRPG_SCHEMAS_DIR:voice-pc.schema.yaml"
  "$TTRPG_SCHEMAS_DIR:session-events-ttrpg.schema.yaml"
  "$TTRPG_SCHEMAS_DIR:digest-ttrpg.schema.yaml"
)

FAIL=0

for entry in "${EXPECTED_SCHEMAS[@]}"; do
  dir="${entry%%:*}"
  schema_file="${entry#*:}"
  path="$dir/$schema_file"
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

echo "OK: all 10 schemas parse and have required schema.name + schema.version (core: $CORE_SCHEMAS_DIR, ttrpg: $TTRPG_SCHEMAS_DIR)."
