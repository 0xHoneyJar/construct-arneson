#!/bin/sh
# test-roundtrip.sh — Validate ingest -> emit round-trip for freeside adapter.
# Exit 0 on pass, exit 1 on fail.
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURE="$SCRIPT_DIR/../resources/fixtures/test-persona.md"
INGEST="$SCRIPT_DIR/ingest_persona.py"
EMIT="$SCRIPT_DIR/emit_persona.py"

TMPDIR="${TMPDIR:-/tmp}"
STATE="$TMPDIR/arneson-rt-state-$$.yaml"
OUTPUT="$TMPDIR/arneson-rt-output-$$.md"

cleanup() {
    rm -f "$STATE" "$OUTPUT"
}
trap cleanup EXIT

echo "=== Freeside Adapter Round-Trip Test ==="

# Step 1: Ingest
echo "  [1/4] Ingest: $FIXTURE"
if ! python3 "$INGEST" "$FIXTURE" > "$STATE" 2>&1; then
    echo "  FAIL: ingest_persona.py exited non-zero"
    cat "$STATE" >&2
    exit 1
fi

# Step 2: Emit
echo "  [2/4] Emit: state -> persona.md"
if ! python3 "$EMIT" --template "$FIXTURE" --state "$STATE" > "$OUTPUT" 2>&1; then
    echo "  FAIL: emit_persona.py exited non-zero"
    cat "$OUTPUT" >&2
    exit 1
fi

# Step 3: Diff
echo "  [3/4] Diff: original vs round-trip output"
if ! diff -b "$FIXTURE" "$OUTPUT" > /dev/null 2>&1; then
    echo "  FAIL: round-trip produced differences:"
    diff -b "$FIXTURE" "$OUTPUT" || true
    exit 1
fi

# Step 4: Sync contract validation
echo "  [4/4] Sync contract: checking dual-target fields"
PASS=0
TOTAL=0

check_marker() {
    marker="$1"
    label="$2"
    TOTAL=$((TOTAL + 1))
    if grep -q "$marker" "$OUTPUT" 2>/dev/null; then
        PASS=$((PASS + 1))
    else
        echo "  FAIL: sync contract marker missing: $label ($marker)"
    fi
}

# Body targets
check_marker "## battle whispers" "voice_anchors body"
check_marker "### decline patterns" "decline_patterns body"
check_marker "## world presence" "canon_boundary body"
check_marker "## exemplars (canon-quality exchanges)" "exemplars body"

# Prompt targets (inside system prompt template)
check_marker "VOICE CANON" "voice_anchors prompt"
check_marker "DON'T" "anti_patterns prompt"
check_marker "CANON BOUNDARY" "canon_boundary prompt"
check_marker "TOOL USE" "decline_patterns prompt"
check_marker "EXEMPLARS" "exemplars prompt"

if [ "$PASS" -ne "$TOTAL" ]; then
    echo "  FAIL: sync contract $PASS/$TOTAL markers found"
    exit 1
fi

echo "  Sync contract: $PASS/$TOTAL markers present"
echo "=== PASS ==="
