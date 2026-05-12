#!/usr/bin/env bash
# Validate skill files exist for implemented skills.
# Sprint 2 implements /braunstein only; other skills are declared but not yet implemented.
# This script checks IMPLEMENTED skills have both SKILL.md and index.yaml.

set -euo pipefail

FAIL=0

# Core skills (domain-agnostic, in skills/)
CORE_SKILLS=(
  arneson       # status dashboard
  distill       # session compressor
  voice         # persona workshop
)

# TTRPG skills (reference vertical, in domains/ttrpg/skills/)
TTRPG_SKILLS=(
  braunstein    # live playtest
  scene         # scene generator
  narrate       # fiction-mechanics-fiction
  improvise     # inverse braunstein
  fragment      # setting material
)

DECLARED_NOT_IMPLEMENTED=()

# Validate core skills
for skill in "${CORE_SKILLS[@]}"; do
  skill_dir="skills/$skill"
  if [ ! -f "$skill_dir/SKILL.md" ]; then
    echo "FAIL: $skill_dir/SKILL.md missing (core skill)"
    FAIL=1
  fi
  if [ ! -f "$skill_dir/index.yaml" ]; then
    echo "FAIL: $skill_dir/index.yaml missing (core skill)"
    FAIL=1
  fi

  if [ -f "$skill_dir/index.yaml" ]; then
    if ! yq eval '.' "$skill_dir/index.yaml" > /dev/null 2>&1; then
      echo "FAIL: $skill_dir/index.yaml does not parse as YAML"
      FAIL=1
    fi
    name=$(yq eval '.name' "$skill_dir/index.yaml")
    if [ "$name" != "$skill" ]; then
      echo "FAIL: $skill_dir/index.yaml name mismatch (expected $skill, got $name)"
      FAIL=1
    fi
  fi
done

# Validate TTRPG domain skills
for skill in "${TTRPG_SKILLS[@]}"; do
  skill_dir="domains/ttrpg/skills/$skill"
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

echo "OK: ${#CORE_SKILLS[@]} core + ${#TTRPG_SKILLS[@]} TTRPG skills have SKILL.md + index.yaml, parse correctly."
