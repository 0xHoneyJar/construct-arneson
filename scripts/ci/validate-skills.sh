#!/usr/bin/env bash
# Validate skill files exist for implemented skills.
# Sprint 2 implements /braunstein only; other skills are declared but not yet implemented.
# This script checks IMPLEMENTED skills have both SKILL.md and index.yaml.

set -euo pipefail

FAIL=0

# Skills implemented so far (updated each sprint)
IMPLEMENTED_SKILLS=(
  braunstein    # Sprint 2
)

# Skills declared in construct.yaml but not yet implemented (no failure — just note)
DECLARED_NOT_IMPLEMENTED=(
  voice         # Sprint 4
  scene         # Sprint 4
  narrate       # Sprint 4
  improvise     # Sprint 5
  arneson       # Sprint 6
  fragment      # Sprint 6
  distill       # Sprint 3
)

for skill in "${IMPLEMENTED_SKILLS[@]}"; do
  skill_dir="skills/$skill"
  if [ ! -f "$skill_dir/SKILL.md" ]; then
    echo "FAIL: $skill_dir/SKILL.md missing (skill is marked as implemented)"
    FAIL=1
  fi
  if [ ! -f "$skill_dir/index.yaml" ]; then
    echo "FAIL: $skill_dir/index.yaml missing (skill is marked as implemented)"
    FAIL=1
  fi

  if [ -f "$skill_dir/index.yaml" ]; then
    # Validate index.yaml parses
    if ! yq eval '.' "$skill_dir/index.yaml" > /dev/null 2>&1; then
      echo "FAIL: $skill_dir/index.yaml does not parse as YAML"
      FAIL=1
    fi

    # Verify name field matches directory
    name=$(yq eval '.name' "$skill_dir/index.yaml")
    if [ "$name" != "$skill" ]; then
      echo "FAIL: $skill_dir/index.yaml name mismatch (expected $skill, got $name)"
      FAIL=1
    fi
  fi
done

NOT_IMPL_COUNT=${#DECLARED_NOT_IMPLEMENTED[@]}
echo "INFO: $NOT_IMPL_COUNT skills declared but not yet implemented (expected — they land in future sprints)"

if [ $FAIL -eq 1 ]; then
  exit 1
fi

echo "OK: all implemented skills have SKILL.md + index.yaml, parse correctly."
