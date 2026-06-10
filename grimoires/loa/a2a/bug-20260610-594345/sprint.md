# Sprint Plan: Bug Fix — Wrapper timeout undercuts engine trial budget; infrastructure non-runs grade as verdicts

**Type**: bugfix
**Bug ID**: 20260610-594345
**Source**: /bug (triage)
**Sprint**: sprint-bug-2

---

## sprint-bug-2: Wrapper timeout undercuts engine trial budget; infrastructure non-runs grade as verdicts

### Sprint Goal
Fix the reported bug with a failing test proving the fix.

### Deliverables
- [ ] Failing test that reproduces the bug
- [ ] Source code fix
- [ ] All existing tests pass (no regressions)
- [ ] Triage analysis document

### Technical Tasks

#### Task 1: Write Failing Test [G-5]
- Create unit tests reproducing both defects
- Verify tests fail with current code
- Test files: domains/agent-systems/scripts/test-ollama-agent.sh (timeout flag/default), domains/agent-systems/scripts/test-validate-batch.sh (infrastructure-triage warning)

**Acceptance Criteria**:
- test-ollama-agent.sh: assertion that the wrapper honors `--timeout N` and that the default is the new sane local-model value — fails against current 240s default
- test-validate-batch.sh: fixture sidecar with `run.status: "completed"` and narration carrying `ERROR: [ollama-agent] ... (timed out)` — assert WARNING on stderr ("non-run, not a verdict") and exit 0; assert warning ABSENT on a clean sidecar — warning assertion fails against current validate_batch.py
- Tests are hermetic (mock Ollama server / temp-dir fixtures only; no network, no model, no spend)
- Preserved sweep evidence under `resources/fixtures/synthetic-incentive/runs/` is NOT modified — copy its shape into test fixtures

#### Task 2: Implement Fix [G-1, G-2]
- Fix root cause in domains/agent-systems/resources/fixtures/ollama-agent.py (default timeout, line 125), domains/agent-systems/scripts/validate_batch.py (triage warning beside the existing honesty warning, lines 109-118), domains/agent-systems/docs/quickstart.md (explicit `--timeout` in the bundled-wrapper agent_cmd example + sizing note vs `stopping.timeout_seconds`)
- Verify failing tests now pass
- Run full domain test suite (`scripts/test-*.sh`)

**Acceptance Criteria**:
- Failing tests now pass
- No regressions in existing tests
- Fix addresses root cause (not just symptoms)
- Constraints honored: stdlib-only (NFR-5); warn-not-reject (`validate_batch.py` exit code unchanged when the triage warning is the only finding — NFR-3/G-4 posture); docs respect the banned-copy table in domain.conventions.md

### Acceptance Criteria
- [ ] Bug is no longer reproducible
- [ ] Failing test proves the fix
- [ ] No regressions in existing tests
- [ ] Fix addresses root cause (not just symptoms)

### Triage Reference
See: grimoires/loa/a2a/bug-20260610-594345/triage.md
