# Sprint Plan: Bug Fix — Infrastructure triage in validate_batch.py is wrapper-specific — misses second wrapper's marker

**Type**: bugfix
**Bug ID**: 20260610-5ad67a
**Source**: /bug (triage)
**Sprint**: sprint-bug-3

---

## sprint-bug-3: Infrastructure triage in validate_batch.py is wrapper-specific — misses second wrapper's marker

### Sprint Goal
Fix the reported bug with a failing test proving the fix.

### Deliverables
- [ ] Failing test that reproduces the bug
- [ ] Source code fix
- [ ] All existing tests pass (no regressions)
- [ ] Triage analysis document

### Technical Tasks

#### Task 1: Write Failing Test [G-5]
- Create unit test reproducing the bug
- Verify test fails with current code
- Test file: domains/agent-systems/scripts/test-validate-batch.sh

Three cases (existing check/check_msg harness pattern):
1. Sidecar narration carrying `"ERROR: [party-wrapper] ..."` → exit 0 AND stderr warns "non-run, not a verdict" (FAILS on current code — proves the bug)
2. `"ERROR: [ollama-agent] ..."` marker still warns (regression guard)
3. Narration containing `"ERROR: [compiler] segfault"` does NOT warn (false-positive guard)

**Acceptance Criteria**:
- Test fails with current code, proving the bug exists
- Test name clearly describes the bug scenario
- Test is isolated (no side effects on other tests)

#### Task 2: Implement Fix [G-1, G-2]
- Fix root cause in domains/agent-systems/scripts/validate_batch.py (infrastructure-triage block, lines 120-132): replace the literal `"ERROR: [ollama-agent]"` match with the documented convention — anchored regex `r"ERROR: \[[A-Za-z0-9_-]*(?:agent|wrapper)\]"`
- Document the wrapper-marker convention in domains/agent-systems/domain.conventions.md ("Local-model agents" section, wrapper-author guidance)
- Update the load-bearing marker comment in domains/agent-systems/resources/fixtures/ollama-agent.py `err()` to reference the convention (comment only; marker string unchanged)
- Verify failing test now passes
- Run full test suite

**Acceptance Criteria**:
- Failing test now passes
- No regressions in existing tests
- Fix addresses root cause (not just symptoms): convention + bounded regex closes the class — wrapper #3 with a conforming marker is triaged without further code change
- Warn-not-reject posture unchanged (exit 0 for layout-valid batches); stdlib only; stamping-not-judging

### Acceptance Criteria
- [ ] Bug is no longer reproducible
- [ ] Failing test proves the fix
- [ ] No regressions in existing tests
- [ ] Fix addresses root cause (not just symptoms)

### Triage Reference
See: grimoires/loa/a2a/bug-20260610-5ad67a/triage.md
