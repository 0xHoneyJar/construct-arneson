# Bug Triage: Wrapper timeout undercuts engine trial budget; infrastructure non-runs grade as verdicts

## Metadata
- **schema_version**: 1
- **bug_id**: 20260610-594345
- **classification**: logic_bug (two coupled defects: silent timeout undercut + missing infrastructure triage)
- **severity**: high
- **eligibility_score**: 4
- **eligibility_reasoning**: Reproducible observed failure (+2: live four-model sweep, caught twice during monitoring); error logs preserved on disk (+1: narrations in synthetic-incentive/runs/2026-06-10T17-01-16-683Z and 2026-06-10T17-29-55-550Z carry the wrapper's named error verbatim); evidence cites exact file:line behavior verifiable in the repo (+1: sidecar duration_ms 240674 matches the 240s default in ollama-agent.py:125). No disqualifiers: no new endpoint, UI, schema, or service — a default value fix, a validator warning on existing data, docs, and tests.
- **test_type**: unit (domain test runners: scripts/test-ollama-agent.sh, scripts/test-validate-batch.sh)
- **risk_level**: low
- **created**: 2026-06-10T17:57:16Z

## Reproduction
### Steps
1. Write a scenario with `stopping.timeout_seconds: 600` (per-trial engine budget) and `agent_cmd` using the bundled wrapper WITHOUT `--timeout` (the quickstart's own example: `python3 .../ollama-agent.py --model qwen3 {promptfile}`).
2. Run a trial against a cold Ollama model large enough that load + first token exceeds 240s (observed: qwen3-coder:30b cold-loading 19GB; again with qwen3-vl:30b under memory pressure from keep_alive stacking).
3. The wrapper's `urlopen` hits its fixed 240s default timeout, prints `ERROR: [ollama-agent] cannot reach ollama at 127.0.0.1:11434 (timed out)...` to stderr, exits 1 — well inside the engine's 600s budget.
4. The engine records `run.status: "completed"` (the agent_cmd process completed, from its viewpoint) and grades `observation.classification: "failed"`.
5. Run `validate_batch.py <batch_dir>`: it prints `OK` with no warning. The /playout report shows "failed" in the comparison table for a trial where no agent ever acted.

### Expected Behavior
- The wrapper's timeout should not silently undercut the engine's per-trial budget; the bundled example and quickstart should make sizing it explicit.
- A completed sidecar whose narration is the wrapper's own infrastructure error signature should be flagged by `validate_batch.py` as a non-run, not passed silently as a graded verdict.

### Actual Behavior
- Fixed 240s default (`ollama-agent.py:125`, `model, timeout = None, 240`) times out under cold-load; wrapper exits 1; engine grades `failed`.
- `validate_batch.py` has no infrastructure triage — the only honesty warning it knows is the ungraded-simulation case (validate_batch.py:109-118). Infrastructure non-runs poison any conclusion drawn from the comparison table.
- Observed twice in the 2026-06-10 four-model sweep. Evidence preserved:
  - `domains/agent-systems/resources/fixtures/synthetic-incentive/runs/2026-06-10T17-01-16-683Z/sidecars/rung-0-trial-1.json` — `duration_ms: 240674`, `status: "completed"`, `classification: "failed"`, narration = wrapper timeout error
  - same batch `rung-2-trial-1.json`, and both sidecars in `runs/2026-06-10T17-29-55-550Z/`

### Environment
Local. macOS, local Ollama daemon (127.0.0.1:11434), four-model sweep (qwen3-coder:30b, qwen3-vl:30b, gemma:latest, gemma3:1b) on the synthetic-incentive fixture, rungs 0+2 × 1 trial, zero spend. Full empirical context: `grimoires/loa/discovery/sweep-observability-findings.md` findings 1-4.

## Analysis
### Suspected Files
| File | Line(s) | Confidence | Reason |
|------|---------|------------|--------|
| domains/agent-systems/resources/fixtures/ollama-agent.py | 125 (`timeout = None, 240` default), 85-90 (urlopen timeout → exit 1 path), 48 (error signature `ERROR: [ollama-agent]`) | high | Defect (1): fixed 240s default silently undercuts engine budget; sidecar duration_ms 240674 matches exactly |
| domains/agent-systems/scripts/validate_batch.py | 83-118 (per-sidecar loop; honesty-warning block at 109-118 is the insertion pattern) | high | Defect (2): no infrastructure triage — completed sidecars with wrapper error narration pass silently |
| domains/agent-systems/docs/quickstart.md | 32 (agent_cmd example lacks `--timeout`), 53-61 (Step 2 field table: `stopping` row), 99 (`--timeout 300` hand-run example) | high | Doc half of fix (a): example must show `--timeout` explicitly and document sizing from `stopping.timeout_seconds` |
| domains/agent-systems/scripts/test-ollama-agent.sh | whole file (no `--timeout` coverage today) | medium | Test home for fix (c): timeout flag respected |
| domains/agent-systems/scripts/test-validate-batch.sh | whole file (existing check/check_msg harness, warning-assert pattern) | medium | Test home for fix (c): triage warning fires on signature fixture, absent on clean ones |

### Related Tests
| Test File | Coverage |
|-----------|----------|
| domains/agent-systems/scripts/test-ollama-agent.sh | Hermetic mock-Ollama harness (good/escape/chatty modes); exit codes; containment. NO timeout coverage today. |
| domains/agent-systems/scripts/test-validate-batch.sh | Happy path, layout violations, run_dir escape, ungraded-simulation warning (`check_msg` asserts stderr patterns). NO infrastructure-triage coverage today. |

### Test Target
1. `test-ollama-agent.sh`: assert `--timeout N` is parsed and honored (mock server with delayed response; small `--timeout` exits 1 with the timeout error, larger `--timeout` succeeds — or assert the parsed value reaches `call_ollama` via a deterministic path the harness can observe). Also assert the new default is in effect.
2. `test-validate-batch.sh`: fixture sidecar with `run.status: "completed"` and narration containing `ERROR: [ollama-agent] ... (timed out)` → `validate_batch.py` exits 0 (warn, not reject) AND stderr matches the new WARNING (`check_msg` on "wrapper infrastructure error" / "non-run, not a verdict"). Clean sidecar → warning absent. Real-world shape to copy: `synthetic-incentive/runs/2026-06-10T17-01-16-683Z/sidecars/rung-0-trial-1.json`.

### Constraints
- **stdlib-only** (NFR-5, stated in ollama-agent.py:19) — no new dependencies in either Python file.
- **Warn, not reject**: the batch is contract-valid. Counting our own error marker is stamping, not judging — NFR-3/G-4 posture (judgments are Gygax's; Arneson reports mechanically-detectable facts). Exit code stays 0 when the triage warning is the only finding. Mirrors the existing ungraded-simulation honesty warning (validate_batch.py:109-118).
- **Banned-copy rules in docs** (domain.conventions.md "Banned copy" table): quickstart wording must avoid the banned-phrase list; frame the warning as mechanical signature detection, not a judgment about the run.
- **Surgical**: detection regex matches the bundled wrapper's OWN signature (`ERROR: \[ollama-agent\]`) in narration — this is self-recognition of our shipped fixture's error marker, not general failure classification (that belongs to Gygax's report layer per finding 4).
- Sweep evidence sidecars under `synthetic-incentive/runs/` are preserved empirical data — do not modify them; copy their shape into hermetic test fixtures instead.

## Fix Strategy
Two coupled, independently-testable changes plus docs:

**(a) Wrapper default + doc** — `ollama-agent.py:125`: raise the default `--timeout` from 240 to a sane local-model value (600s recommended: matches the trial budget that was undercut in the field; cold-load of a 19GB model observed to exceed 240s). Update the module docstring usage line and `docs/quickstart.md`: the bundled-wrapper `agent_cmd` example (line 32) gains an explicit `--timeout`, with one sentence documenting sizing it from the scenario's `stopping.timeout_seconds` (wrapper timeout ≤ engine budget minus margin — the engine budget must be the binding one, or at minimum the operator must see the relationship). Keep the wrapper's failure mode identical (named error, exit 1).

**(b) Mechanical infrastructure-triage WARNING** — `validate_batch.py`, in the per-sidecar loop alongside the existing honesty warning (lines 109-118): when a sidecar has `run.status == "completed"` and its `narration` matches the bundled wrapper's own error signature (regex `ERROR: \[ollama-agent\]`), emit `WARNING: <name>: wrapper infrastructure error in narration — this is a non-run, not a verdict` via the existing `warn()` helper. Do NOT add to `violations`; exit code unchanged. This is signature self-recognition (we shipped the wrapper; we recognize its marker), not failure classification.

**(c) Tests** — extend both shell harnesses per Test Target above: timeout flag respected; triage warning fires on a fixture sidecar carrying the signature, absent on clean ones; exit code stays 0 with the warning.

### Fix Hints
Structured hints for multi-model handoff (each hint targets one file change):

| File | Action | Target | Constraint |
|------|--------|--------|------------|
| domains/agent-systems/resources/fixtures/ollama-agent.py | fix | default timeout value at line 125 (240 → 600) | stdlib-only; keep exit-code contract (0/1/2) and error wording |
| domains/agent-systems/docs/quickstart.md | add | explicit `--timeout` in bundled-wrapper agent_cmd example + sizing note vs `stopping.timeout_seconds` | banned-copy rules; one example, one sentence |
| domains/agent-systems/scripts/validate_batch.py | add | WARNING when completed sidecar narration matches `ERROR: \[ollama-agent\]` | warn not reject — never append to violations, exit code unchanged |
| domains/agent-systems/scripts/test-ollama-agent.sh | add | assertions: `--timeout` flag parsed and honored; new default in effect | hermetic — mock server only, no network/model |
| domains/agent-systems/scripts/test-validate-batch.sh | add | assertions: triage warning on signature fixture, absent on clean; exit 0 | copy sidecar shape from preserved sweep runs, do not touch originals |
