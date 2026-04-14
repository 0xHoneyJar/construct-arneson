#!/usr/bin/env bash
# Validate synthetic fixture: game-state.yaml parses, has required structure,
# and HEKATE-free.

set -euo pipefail

FIXTURE_DIR="examples/synthetic-fixture"

if [ ! -d "$FIXTURE_DIR" ]; then
  echo "FAIL: $FIXTURE_DIR missing"
  exit 1
fi

EXPECTED_FILES=(
  "$FIXTURE_DIR/README.md"
  "$FIXTURE_DIR/game-state.yaml"
  "$FIXTURE_DIR/tradition-folk-horror-minimalist.yaml"
  "$FIXTURE_DIR/scene-seeds.md"
)

FAIL=0

for f in "${EXPECTED_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "FAIL: fixture file $f missing"
    FAIL=1
  fi
done

GS="$FIXTURE_DIR/game-state.yaml"

if [ -f "$GS" ]; then
  # Parse
  if ! yq eval '.' "$GS" > /dev/null 2>&1; then
    echo "FAIL: game-state.yaml does not parse as YAML"
    FAIL=1
  fi

  # Required top-level keys
  REQUIRED_KEYS=(.game.title .game.tradition .stats .mechanics .locations .villagers .pc_slots)
  for k in "${REQUIRED_KEYS[@]}"; do
    v=$(yq eval "$k" "$GS" 2>/dev/null)
    if [ -z "$v" ] || [ "$v" = "null" ]; then
      echo "FAIL: game-state.yaml missing $k"
      FAIL=1
    fi
  done

  # title should be 'Threshold'
  title=$(yq eval '.game.title' "$GS")
  if [ "$title" != "Threshold" ]; then
    echo "FAIL: game-state.yaml title expected 'Threshold', got '$title'"
    FAIL=1
  fi

  # Both intent axes present on at least one mechanic
  mech_intent_mech=$(yq eval '.mechanics.threshold_roll.mechanical_intent' "$GS")
  mech_intent_exp=$(yq eval '.mechanics.threshold_roll.experiential_intent' "$GS")
  if [ "$mech_intent_mech" = "null" ]; then
    echo "FAIL: threshold_roll.mechanical_intent missing"
    FAIL=1
  fi
  if [ "$mech_intent_exp" = "null" ]; then
    echo "FAIL: threshold_roll.experiential_intent missing"
    FAIL=1
  fi
fi

# HEKATE check (double-insurance — the audit script also covers this, but fixture
# is an especially sensitive area to check).
# Filter meta-references (the phrase "HEKATE-free" etc. is OK; a real game reference is not).
raw=$(grep -rinI -E 'mibera|hekate' "$FIXTURE_DIR" 2>/dev/null || true)
filtered=$(echo "$raw" | grep -viE 'hekate[- ](free|audit)' \
                        | grep -viE 'like (mibera|hekate)' \
                        | grep -viE 'without.*(mibera|hekate)' \
                        | grep -viE '(mibera|hekate)[- ]is' \
                        || true)
if [ -n "$filtered" ]; then
  echo "FAIL: fixture contains non-meta MIBERA/HEKATE references:"
  echo "$filtered"
  FAIL=1
fi

if [ $FAIL -eq 1 ]; then
  exit 1
fi

echo "OK: synthetic fixture validates — all files present, game-state schema-conformant, HEKATE-free."
