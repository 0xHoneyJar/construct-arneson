# Sprint Plan: Bug Fix — Local-model agent path in agent-systems quickstart is unrunnable as documented

**Type**: bugfix
**Bug ID**: 20260610-c7bc67
**Source**: /bug (triage)
**Sprint**: sprint-bug-1

---

## sprint-bug-1: Local-model agent path in agent-systems quickstart is unrunnable as documented

### Sprint Goal
Fix the reported bug with a failing test proving the fix.

### Deliverables
- [ ] Failing test that reproduces the bug
- [ ] Source code fix
- [ ] All existing tests pass (no regressions)
- [ ] Triage analysis document

### Technical Tasks

#### Task 1: Write Failing Test [G-5]
- Create integration test reproducing the bug
- Verify test fails with current code
- Test file: domains/agent-systems/scripts/test-ollama-agent.sh

**Acceptance Criteria**:
- Test fails with current code, proving the bug exists (wrapper absent; quickstart Step 1 has no bundled local-model example)
- Test name clearly describes the bug scenario
- Test is isolated (no side effects on other tests): offline, stdlib-only stub server, zero network spend

#### Task 2: Implement Fix [G-1, G-2]
- Fix root cause in domains/agent-systems/resources/fixtures/ollama-agent.py (new), domains/agent-systems/docs/quickstart.md, domains/agent-systems/domain.conventions.md
- Verify failing test now passes
- Run full test suite

**Acceptance Criteria**:
- Failing test now passes
- No regressions in existing tests (all domains/agent-systems/scripts/test-*.sh green)
- Fix addresses root cause (not just symptoms): bundled stdlib-only wrapper exists and is the documented works-out-of-the-box local-model example

### Acceptance Criteria
- [ ] Bug is no longer reproducible: an operator with Ollama running can copy the quickstart Step 1 local-model example and run it with only repo contents
- [ ] Failing test proves the fix (test-ollama-agent.sh: stub-server file-writing, nonzero exit on failure, stdlib-only imports, doc reference grep)
- [ ] No regressions in existing tests
- [ ] Fix addresses root cause (not just symptoms)
- [ ] NFR-5 held: wrapper imports stdlib only
- [ ] Banned-copy grep clean on all touched docs (0 banned phrases outside quoted ban lists)
- [ ] Manual live verification recorded: engine run against the bundled synthetic-incentive fixture with ollama/gemma, zero API spend, batch_dir noted in sprint evidence

### Triage Reference
See: grimoires/loa/a2a/bug-20260610-c7bc67/triage.md
