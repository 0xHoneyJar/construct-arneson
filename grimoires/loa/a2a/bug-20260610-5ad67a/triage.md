# Bug Triage: Infrastructure triage in validate_batch.py is wrapper-specific — misses second wrapper's marker

## Metadata
- **schema_version**: 1
- **bug_id**: 20260610-5ad67a
- **classification**: logic_bug
- **severity**: medium
- **eligibility_score**: 3
- **eligibility_reasoning**: Reproducible steps with observed probe output (+2: confirmed live during triage — party-wrapper marker passes with exit 0 and no warning); regression against the stated purpose of a shipped fix, bug 20260610-594345 / PR #16 (+1). No disqualifiers: this generalizes an existing defect-guard whose stated invariant ("infrastructure non-runs must never masquerade as graded verdicts") demonstrably fails for the second wrapper. Prior review flagged this exact gap (a2a/bug-20260610-594345/engineer-feedback.md concern 1: "a shared 'infrastructure marker' convention would generalize this").
- **test_type**: unit
- **risk_level**: low
- **created**: 2026-06-10T00:00:00Z

## Reproduction
### Steps
1. Copy the committed fixture batch: `cp -R domains/agent-systems/resources/fixtures/batches/valid-batch /tmp/party-casualty`
2. Set the sidecar narration to a second wrapper's infrastructure error: `" [stderr] ERROR: [party-wrapper] cannot reach ollama at 127.0.0.1:11434 (timed out)"` in `sidecars/rung-0-trial-1.json`
3. Run `python3 domains/agent-systems/scripts/validate_batch.py /tmp/party-casualty`

### Expected Behavior
The validator warns "non-run, not a verdict" (warn-not-reject, exit 0) — the same triage it gives the bundled `ollama-agent.py` marker — because the narration carries a wrapper's own infrastructure error and no agent ever acted.

### Actual Behavior
Output `OK /tmp/party-casualty (1 sidecar(s))`, exit 0, NO infrastructure warning. The non-run masquerades as a graded verdict and silently poisons any comparison drawn from the batch.

Confirmed during triage (2026-06-10): the literal-string match at `validate_batch.py:127` (`"ERROR: [ollama-agent]" in obj["narration"]`) only fires for the bundled wrapper.

### Environment
local — stdlib-only Python validator, exercised via the domain shell test harness (`domains/agent-systems/scripts/test-validate-batch.sh`)

## Analysis
### Suspected Files
| File | Line(s) | Confidence | Reason |
|------|---------|------------|--------|
| domains/agent-systems/scripts/validate_batch.py | 120-132 | high | The infrastructure-triage block; line 127 matches the literal `"ERROR: [ollama-agent]"` only. Verified by direct read + live repro. |
| domains/agent-systems/scripts/test-validate-batch.sh | 92-116 | high | Co-tests for the triage feature; needs party-wrapper warn case, ollama regression case, and a non-conforming false-positive guard. |
| domains/agent-systems/resources/fixtures/ollama-agent.py | 53-57 | high | `err()` carries the LOAD-BEARING marker comment ("change it there + in the tests together") — must be updated to reference the convention, marker string itself unchanged. |
| domains/agent-systems/domain.conventions.md | ~60-68 ("Local-model agents" section) | medium | Documentation target for the new wrapper-marker convention (wrapper authors section). |

### Related Tests
| Test File | Coverage |
|-----------|----------|
| domains/agent-systems/scripts/test-validate-batch.sh | Existing: infra-casualty warn case (ollama-agent marker, lines ~92-109), clean-batch no-false-triage guard (lines ~111-116). Missing: any second-wrapper marker, any non-conforming-marker false-positive case. |

### Test Target
Extend `test-validate-batch.sh` with three cases (shell harness pattern already established at lines 92-116):
1. **party-wrapper marker warns**: sidecar narration carrying `"ERROR: [party-wrapper] ..."` → exit 0 AND stderr contains "non-run, not a verdict". This test FAILS on current code (proves the bug).
2. **ollama-agent marker still warns** (regression): existing case stays green.
3. **Non-conforming marker does NOT warn** (false-positive guard): narration containing `"ERROR: [compiler] segfault"` (agent's own stdout) → exit 0 AND stderr does NOT contain "non-run".

Note: `party-wrapper.py` is referenced in grimoires docs (context/dungeon-demo-direction.md, discovery/dungeon-party-findings.md) but is NOT committed in this repo — tests must synthesize the marker string in a fixture narration (same pattern the existing infra-casualty test uses), not invoke the prototype.

### Constraints
- Warn-not-reject unchanged: triage stays a WARNING; exit code stays 0 for a layout-valid batch.
- Stdlib only (`re` is stdlib — acceptable; module already imports json/sys/pathlib).
- Stamping-not-judging posture (G-4): match a declared marker convention, never interpret narration content.
- Regex must stay anchored/bounded — `r"ERROR: \[[A-Za-z0-9_-]*(?:agent|wrapper)\]"` — so arbitrary agent stdout containing `ERROR: [x]` does not false-positive. Verified during triage: 5/5 cases behave as intended (ollama-agent ✓, party-wrapper ✓, bare `[wrapper]` ✓, `[compiler]` rejected ✓, `[x]` rejected ✓).
- Co-tested with both marker emitters per the load-bearing comment contract; the ollama-agent.py marker string itself must NOT change.

## Fix Strategy
Replace the wrapper-specific literal substring match with a documented CONVENTION:

1. **Convention (the actual fix)**: bundled/operator wrappers emit stderr infrastructure errors prefixed `ERROR: [<tool-name>]` where `<tool-name>` ends in `-agent` or `-wrapper` (bare `agent`/`wrapper` also conforms). `validate_batch.py`'s infrastructure-triage block matches the convention via the anchored regex `r"ERROR: \[[A-Za-z0-9_-]*(?:agent|wrapper)\]"` (compiled once at module level), replacing the `"ERROR: [ollama-agent]" in obj["narration"]` literal at line 127. Update the block's comment to define the convention as the contract.
2. **Documentation**: add the convention to `domain.conventions.md` "Local-model agents" section (wrapper-author guidance: emit the conforming prefix so the validator can triage your non-runs). Update the load-bearing comment in `ollama-agent.py` `err()` to reference the convention instead of pointing solely at the literal match site.
3. **Tests**: the three cases in Test Target above, in `test-validate-batch.sh`.

Root cause, not symptom: adding `"ERROR: [party-wrapper]"` as a second literal would recreate the same bug for wrapper #3; the convention + bounded regex closes the class.

### Fix Hints
Structured hints for multi-model handoff (each hint targets one file change):

| File | Action | Target | Constraint |
|------|--------|--------|------------|
| domains/agent-systems/scripts/validate_batch.py | fix | replace literal `"ERROR: [ollama-agent]"` substring check (line 127) with anchored regex `r"ERROR: \[[A-Za-z0-9_-]*(?:agent|wrapper)\]"` | infrastructure-triage block only; warn-not-reject and message text unchanged |
| domains/agent-systems/scripts/test-validate-batch.sh | add | party-wrapper warn case + ollama-agent regression case + `ERROR: [compiler]` false-positive guard | follow existing check/check_msg harness pattern; synthesize markers in fixture narration |
| domains/agent-systems/domain.conventions.md | add | wrapper infrastructure-marker convention in "Local-model agents" section | document the convention for wrapper authors; no behavior |
| domains/agent-systems/resources/fixtures/ollama-agent.py | fix | load-bearing comment at `err()` (lines 53-57) to reference the convention | comment only; marker string `ERROR: [ollama-agent]` unchanged |
