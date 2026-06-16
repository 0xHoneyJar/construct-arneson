#!/usr/bin/env bash
# test-scaffold-agent-persona.sh (cycle-005, Sprint 22). Hermetic: scaffold an
# agent-persona skeleton from a voice and assert it's schema-valid, seeded (not
# auto-converted), provenance-traceable, deterministic, and refuses bad input.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SC="python3 $SCRIPT_DIR/scaffold_agent_persona.py"

PASS=0; FAIL=0
ok() { if eval "$2"; then echo "PASS: $1"; PASS=$((PASS+1)); else echo "FAIL: $1"; FAIL=$((FAIL+1)); fi; }

W=$(mktemp -d)
trap 'rm -rf "$W" 2>/dev/null' EXIT

# A self-contained voice fixture (so the test doesn't depend on a workshop artifact).
mkdir -p "$W/grimoires/arneson/voices/npcs"
cat > "$W/grimoires/arneson/voices/npcs/probe.yaml" <<'YAML'
voice_id: probe
display_name: "Probe"
speech_patterns:
  sentence_length: terse
  vocabulary_register: colloquial
emotional_register:
  baseline: sharp-engaged
YAML

# Run the scaffolder from inside the fixture root so VOICE_DIR resolves.
( cd "$W" && $SC --from-voice probe --out "$W/probe.persona.yaml" >/dev/null 2>"$W/err1" )
ok "scaffold --from-voice exits 0" "[ \$? -eq 0 ]"

# Validate the emitted skeleton with Python (parse + required-field contract).
# cwd-independent: the scripts dir is passed in as argv[1].
check_py() {  # $1 = persona file
python3 - "$SCRIPT_DIR" "$1" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
from restricted_yaml import parse
d = parse(open(sys.argv[2]).read())
req = ["persona_id", "source", "disposition", "capabilities", "knowledge", "rung_overlays"]
assert all(k in d for k in req), f"missing: {[k for k in req if k not in d]}"
s = d["source"]
# voice-sourced => character-voice (exploration-origin), never behavioral-spec.
assert s.get("ref") and s.get("sha256") and s.get("kind") == "character-voice", "bad source provenance"
assert list(d["rung_overlays"].keys()) == ["blind", "reward-aware", "adversarial"], "rung keys wrong"
assert isinstance(d["capabilities"], list) and d["capabilities"], "capabilities empty"
print("OK")
PY
}
ok "emitted skeleton is schema-valid (required fields + named rungs + provenance)" \
   "[ \"\$(check_py '$W/probe.persona.yaml')\" = OK ]"

# Seeded, NOT auto-converted: disposition is a DRAFT; task-behavior fields are TODO stubs.
ok "disposition is a seeded DRAFT (edit me)" "grep -q 'DRAFT seeded from voice' '$W/probe.persona.yaml'"
ok "disposition carries the voice signal (baseline)" "grep -q 'sharp-engaged' '$W/probe.persona.yaml'"
ok "capabilities are TODO stubs (not fabricated task behavior)" "grep -q 'TODO: what this agent would DO' '$W/probe.persona.yaml'"
ok "rung overlays are TODO stubs" "grep -q 'TODO: what the agent knows at the blind rung' '$W/probe.persona.yaml'"
ok "source pins voice provenance (sha256)" "grep -qE 'sha256: [0-9a-f]{64}' '$W/probe.persona.yaml'"
# Honest provenance: voice-sourced => character-voice (exploration), NOT behavioral-spec.
ok "voice persona is labelled kind: character-voice" "grep -q 'kind: character-voice' '$W/probe.persona.yaml'"
ok "voice persona is NOT stamped behavioral-spec" "! grep -q 'kind: behavioral-spec' '$W/probe.persona.yaml'"
ok "voice persona carries the EXPLORATION-only marker" "grep -q 'EXPLORATION persona' '$W/probe.persona.yaml'"
ok "marker disclaims fidelity / gap-report eligibility" "grep -qi 'NOT eligible for fidelity' '$W/probe.persona.yaml'"

# Determinism: byte-equal across two runs.
( cd "$W" && $SC --from-voice probe --out "$W/d1.yaml" >/dev/null 2>&1 )
( cd "$W" && $SC --from-voice probe --out "$W/d2.yaml" >/dev/null 2>&1 )
ok "deterministic (byte-equal across runs)" "diff -q '$W/d1.yaml' '$W/d2.yaml' >/dev/null"

# --blank path produces a valid skeleton too.
( cd "$W" && $SC --blank --id test-blank --out "$W/blank.yaml" >/dev/null 2>&1 )
ok "--blank exits 0" "[ \$? -eq 0 ]"
ok "--blank skeleton has required fields" "grep -q 'persona_id: test-blank' '$W/blank.yaml' && grep -q 'rung_overlays:' '$W/blank.yaml'"
# --blank is meant to be grounded in a real spec by the human => behavioral-spec, no exploration marker.
ok "--blank uses behavioral-spec (human grounds it in a real spec)" "grep -q 'kind: behavioral-spec' '$W/blank.yaml'"
ok "--blank carries no exploration marker" "! grep -q 'EXPLORATION persona' '$W/blank.yaml'"

# Negative paths.
( cd "$W" && $SC --from-voice does-not-exist --out "$W/x.yaml" >/dev/null 2>"$W/err2" )
ok "missing voice -> exit 1" "[ \$? -eq 1 ]"
ok "error names the tool" "grep -q 'ERROR: \[scaffold_agent_persona\]' '$W/err2'"
( cd "$W" && $SC --blank --id 'Bad Id!!' --out "$W/y.yaml" >/dev/null 2>"$W/err3" )
ok "bad id rejected -> exit 1" "[ \$? -eq 1 ]"
ok "--from-voice + --blank mutually exclusive" "! ( cd '$W' && $SC --from-voice probe --blank --id z >/dev/null 2>&1 )"

# Guardrail: the scaffolder is standalone — no gap_report wiring, no /voice-skill import.
ok "no gap_report / sweep_report coupling (guardrail)" "! grep -qE 'gap_report|sweep_report' '$SCRIPT_DIR/scaffold_agent_persona.py'"
ok "stdlib-only imports" "! grep -nE '^(import [a-z]|from [a-z_]+ import)' '$SCRIPT_DIR/scaffold_agent_persona.py' | grep -vE 'import (hashlib|os|re|sys)|from restricted_yaml import'"

echo "---"
echo "scaffold-agent-persona: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
