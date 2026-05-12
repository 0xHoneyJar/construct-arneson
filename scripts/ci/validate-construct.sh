#!/usr/bin/env bash
# Validate construct.yaml: required top-level fields present, structure correct.

set -euo pipefail

MANIFEST="construct.yaml"

if [ ! -f "$MANIFEST" ]; then
  echo "FAIL: construct.yaml missing"
  exit 1
fi

# Required fields (per SDD Appendix 11.A)
REQUIRED_FIELDS=(
  ".schema_version"
  ".slug"
  ".name"
  ".version"
  ".type"
  ".domain"
  ".identity.prose"
  ".identity.persona"
  ".identity.expertise"
  ".identity.refusals"
  ".skills"
  ".composition.siblings"
  ".composition.fallbacks.archetypes"
  ".schemas"
  ".output_paths.grimoire_root"
)

FAIL=0
for field in "${REQUIRED_FIELDS[@]}"; do
  value=$(yq eval "$field" "$MANIFEST" 2>/dev/null)
  if [ -z "$value" ] || [ "$value" = "null" ]; then
    echo "FAIL: $MANIFEST missing required field: $field"
    FAIL=1
  fi
done

# Verify slug is 'arneson'
slug=$(yq eval '.slug' "$MANIFEST")
if [ "$slug" != "arneson" ]; then
  echo "FAIL: expected slug 'arneson', got '$slug'"
  FAIL=1
fi

# Verify 3 core skills declared
core_skill_count=$(yq eval '.skills | length' "$MANIFEST")
if [ "$core_skill_count" != "3" ]; then
  echo "FAIL: expected 3 core skills in construct.yaml; got $core_skill_count"
  FAIL=1
fi

# Verify core skill names
EXPECTED_CORE_SKILLS=(arneson distill voice)
for skill in "${EXPECTED_CORE_SKILLS[@]}"; do
  exists=$(yq eval ".skills[] | select(. == \"$skill\")" "$MANIFEST")
  if [ -z "$exists" ]; then
    echo "FAIL: expected core skill '$skill' not in construct.yaml"
    FAIL=1
  fi
done

# Verify 5 TTRPG domain skills declared
ttrpg_skill_count=$(yq eval '.domains.ttrpg.skills | length' "$MANIFEST")
if [ "$ttrpg_skill_count" != "5" ]; then
  echo "FAIL: expected 5 TTRPG domain skills; got $ttrpg_skill_count"
  FAIL=1
fi

# Verify TTRPG skill names
EXPECTED_TTRPG_SKILLS=(braunstein scene narrate improvise fragment)
for skill in "${EXPECTED_TTRPG_SKILLS[@]}"; do
  exists=$(yq eval ".domains.ttrpg.skills[] | select(. == \"$skill\")" "$MANIFEST")
  if [ -z "$exists" ]; then
    echo "FAIL: expected TTRPG skill '$skill' not in construct.yaml"
    FAIL=1
  fi
done

# Verify each declared schema file exists (core + ttrpg)
for schema_path in $(yq eval '.schemas.core[]' "$MANIFEST") $(yq eval '.schemas.ttrpg[]' "$MANIFEST"); do
  if [ ! -f "$schema_path" ]; then
    echo "FAIL: declared schema $schema_path does not exist"
    FAIL=1
  fi
done

# Verify identity files exist
IDENTITY_FILES=(
  "identity/ARNESON.md"
  "identity/persona.yaml"
  "identity/expertise.yaml"
  "identity/refusals.yaml"
)
for f in "${IDENTITY_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "FAIL: identity file $f does not exist"
    FAIL=1
  fi
done

if [ $FAIL -eq 1 ]; then
  exit 1
fi

echo "OK: construct.yaml validates — all required fields present, 3 core + 5 TTRPG skills declared, schemas + identity files exist."
