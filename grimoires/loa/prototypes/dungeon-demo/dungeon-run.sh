#!/usr/bin/env bash
# The Bone Tyrant run — party of three local models through the dungeon fixture,
# rungs 0 (blind) and 2 (adversarial), via the real engine. Zero API spend.
set -uo pipefail

FIXTURE=/tmp/dungeon-fixture
WRAPPER=/tmp/party-wrapper.py
VALIDATE=/Users/mandy/construct-arneson/domains/agent-systems/scripts/validate_batch.py
LIVE=/tmp/dungeon-live.log
PARTY="Brakka=qwen3-coder:30b,Miriel=gemma:latest,Pip=gemma3:1b"

echo "⚔️  DUNGEON RUN — party: $PARTY" >> "$LIVE"

for M in "qwen3-coder:30b" "gemma:latest" "gemma3:1b"; do
  echo "▶ warming $M" >> "$LIVE"
  curl -s --max-time 900 http://127.0.0.1:11434/api/generate \
    -d "{\"model\":\"$M\",\"prompt\":\"ready\",\"stream\":false,\"keep_alive\":\"45m\"}" >/dev/null \
    || { echo "✗ WARMUP FAILED: $M" >> "$LIVE"; exit 1; }
done
echo "▶ all three models warm — engine takes over" >> "$LIVE"

cd /Users/mandy/construct-gygax
npx tsx scripts/lib/ladder/index.ts run \
  --fixture "$FIXTURE" --rungs 0,2 --trials 1 \
  --agent-cmd "python3 $WRAPPER --party $PARTY {promptfile}" \
  --timeout 1800 --json > /tmp/dungeon-result.json 2>> "$LIVE"
ENGINE_EXIT=$?
echo "▶ engine exit: $ENGINE_EXIT" >> "$LIVE"
[ $ENGINE_EXIT -ne 0 ] && { echo "✗ ENGINE FAILURE" >> "$LIVE"; exit 1; }

BATCH=$(python3 -c "import json;print(json.load(open('/tmp/dungeon-result.json'))['batch_dir'])")
echo "▶ validating batch (byte-untouched): $BATCH" >> "$LIVE"
python3 "$VALIDATE" "$BATCH" >> "$LIVE" 2>&1
echo "▶ grading (regrade ingest)" >> "$LIVE"
npx tsx scripts/lib/trace/index.ts "$BATCH" --regrade > /tmp/dungeon-report.txt 2>&1
grep -E "^\| [02] " /tmp/dungeon-report.txt | sed 's/^/🏆 VERDICT /' >> "$LIVE"
echo "■ DUNGEON RUN COMPLETE — report at /tmp/dungeon-report.txt, batch $BATCH" >> "$LIVE"
