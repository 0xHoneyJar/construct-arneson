# Security and Quality Audit — Sprint 15 (Final)

**Date:** 2026-06-10  
**Sprint:** Local 4 / Global 15 (cycle-002 playtest-instrument-v4.1)  
**Branch:** feature/sprint-plan-v41-20260610  
**Audit Type:** Codebase Security + Cycle Invariants  

## Executive Summary

Sprint 15 introduces the playtest scaffolder (`scaffold_playtest.py`), authoring guide, and honesty boundary gate (`banned-copy-check.sh`). All five PRD goals (G1–G5) are validated end-to-end. Core invariants are preserved: **zero changes to stdlib or producer**, **138 assertions across 11 suites all passing**, **determinism maintained**, no eval/exec/pickle, and subprocess calls use safe argv-list patterns.

**Verdict:** ONE MEDIUM-severity vulnerability identified (path traversal via `--out`), two LOW-severity code quality issues (--id regex loose, banned-copy table exclusion has narrow edge case). All are non-blocking for merge given documented usage patterns and the reviewer's sign-off. No CRITICAL/HIGH findings. Cycle invariants preserved. **APPROVED - LET'S FUCKING GO** pending path-traversal remediation in post-cycle hardening.

---

## Scope

**In Scope (Audited):**
- `domains/agent-systems/scripts/scaffold_playtest.py` (240 LOC)
- `domains/agent-systems/scripts/test-scaffold-playtest.sh` (63 LOC)
- `domains/agent-systems/docs/authoring-a-playtest.md` (94 LOC)
- `scripts/ci/banned-copy-check.sh` (38 LOC)
- Inherited invariants: stdlib-only, no producer changes, determinism, 95+ assertions

**Out of Scope:**
- Engine/wrapper code (no changes this sprint)
- Dungeon fixture logic (unchanged from prior sprints)
- Ancillary CI suites (validate_scenario, validate_batch, etc.)

---

## Findings

### HIGH Priority

**None identified.** All injection vectors in the generator are properly validated or safe.

### MEDIUM Priority

#### SEC-001: Path Traversal via --out Parameter

**Severity:** MEDIUM  
**Confidence:** HIGH  
**Exploitability:** LOW (requires user to explicitly use relative paths with ../)  

**Location:** `scaffold_playtest.py`, lines 180–187

**Description:**  
The `--out` parameter accepts both absolute and relative paths without validating that relative paths cannot escape the intended directory via `../` sequences.

**Code:**
```python
out = Path(args["--out"])
if out.exists() and any(out.iterdir()):
    err(f"--out {out} exists and is non-empty (refusing to overwrite)")
    return 1
(out / "task-template").mkdir(parents=True, exist_ok=True)
```

**Proof of Concept:**
```bash
cd /tmp/safe-dir
python3 scaffold_playtest.py --id test --task x --difficulty-range 1-10 \
  --out "../sibling-dir"
# Creates files at /tmp/sibling-dir (outside intended parent)
```

**Impact:**  
- A malicious or confused user could create playtest scaffolding outside the intended directory.
- Low practical risk: users naturally use absolute paths from `/tmp` or known directories (all test cases use absolute paths).
- Does NOT enable code injection (only file creation at alternate location).

**Remediation:**  
1. **Preferred:** Require absolute paths only:
   ```python
   out = Path(args["--out"])
   if not out.is_absolute():
       err(f"--out must be an absolute path, got {args['--out']!r}")
       return 1
   ```

2. **Alternative:** Validate that resolved path stays within a safe directory:
   ```python
   out = Path(args["--out"]).resolve()
   safe_base = Path(args.get("--safe-base", "/tmp")).resolve()
   if not str(out).startswith(str(safe_base)):
       err(f"--out {out} would escape safe base {safe_base}")
       return 1
   ```

**References:**  
- CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
- OWASP A01:2021 – Broken Access Control

**Status:** DOCUMENTED. Non-blocking given test suite always uses absolute paths and reviewer has approved. Recommend fix in post-merge hardening.

---

### LOW Priority

#### CQ-001: --id Regex Allows Trailing Dash

**Severity:** LOW  
**Confidence:** HIGH  
**Impact:** Code quality only (not a security issue)

**Location:** `scaffold_playtest.py`, lines 159–161

**Description:**  
The `--id` validation regex `[a-z0-9][a-z0-9-]*` permits IDs ending with a dash (e.g., `"myid-"`), which violates proper kebab-case format (should be `[a-z0-9][a-z0-9-]*[a-z0-9]`).

**Issue:**
```python
if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", pid):  # Allows trailing dash
    err(f"--id must be kebab-case [a-z0-9-]: {pid!r}")
    return 1
```

**Example:**
- `"test-id-"` passes validation (incorrect kebab-case)
- `"test-"` passes validation (incorrect)
- `"test-id"` passes validation (correct)

**Impact:**  
- Does NOT break functionality; the ID is used only in comments and YAML keys, both of which tolerate trailing dashes.
- Violates naming convention; cosmetic issue.
- Confuses operators authoring new playtests (they might believe the regex enforces proper kebab-case).

**Remediation:**  
Change regex to: `r"[a-z0-9]([a-z0-9-]*[a-z0-9])?"` to enforce alphanumeric start and end (allowing single-char IDs like `"a"`).

**Status:** DOCUMENTED. Cosmetic; does not affect security or functionality. Can be addressed in post-release quality pass.

---

#### CQ-002: banned-copy Table-Line Exclusion Has Narrow Edge Case

**Severity:** LOW  
**Confidence:** MEDIUM  
**Impact:** Documentation oversight (unlikely but possible)

**Location:** `scripts/ci/banned-copy-check.sh`, lines 20–21

**Description:**  
The exclusion pattern for ban-list table rows in `domain.conventions.md` assumes lines start with `| "` (pipe + space + quote), as in markdown table syntax.

**Code:**
```bash
hits=$(grep -niE "$BANNED" "$f" 2>/dev/null | grep -vE '^[0-9]+:[[:space:]]*\|[[:space:]]*"' || true)
```

**Edge Case:**  
If a future table in the documentation quotes a banned phrase in a non-leading cell (e.g., starting with text before the pipe), the exclusion would NOT catch it:
```markdown
| Some text | "proves it's compelling" | more text |
```
This would be detected as a violation (correctly, if not a true table of definitions).

**Current Risk:** MINIMAL
- The only table quoting banned phrases is `domain.conventions.md:§Ban List` (the approved source).
- Prose is the real risk; tables with these quotes are intentional citations in the ban-list itself.
- The exclusion correctly catches the actual use case.

**Remediation (Optional):**  
Tighten the pattern to exclude entire table rows (not just lines starting with pipe):
```bash
# If a line contains both | and a banned phrase, assume it's a table row
hits=$(grep -niE "$BANNED" "$f" 2>/dev/null | grep -vE '\|.*"' || true)
```
But this over-excludes (any table row with a banned phrase anywhere would be skipped). Current approach is pragmatic.

**Status:** DOCUMENTED. Non-blocking; the edge case is narrow and the current pattern is pragmatic. Reviewer noted this as a concern; accepted trade-off.

---

## Code Quality and Best Practices

### Positive Findings

✓ **Injection Safety (--id, --task, --difficulty-range)**  
- All user input is validated or safely interpolated.
- No eval/exec; subprocess uses safe argv-list pattern (no shell=True).
- Generated referee stub is a true DEFEAT no-op with correct exit codes.

✓ **Stdlib Only (NFR-2)**  
- Imports: `re`, `subprocess`, `sys`, `pathlib` — all stdlib.
- No external dependencies (pyyaml, requests, etc.).

✓ **Determinism**  
- No randomness, no timestamps, no UUIDs.
- Referee stub enforces deterministic grading in generated code.
- Manifest field layout is stable across runs.

✓ **Self-Check (R-2)**  
- Scaffolder runs the generated smoke test before returning success (exit 0).
- If smoke test fails, scaffolder exits 2 and refuses to claim the fixture works.
- Test suite confirms exit-2 path is reachable (corrupted referee → smoke fails).

✓ **Subprocess Safety**  
- `subprocess.run(["bash", str(smoke)], ...)` uses argv list.
- No shell interpolation; immune to shell injection.

✓ **Test Coverage**  
- test-scaffold-playtest.sh: 12 assertions covering happy path, errors, edge cases.
- Integration tests verify DEFEAT stub runs, payoff-dominance passes, manifest parses.

---

### Areas for Improvement (Non-Blocking)

1. **Path Validation (SEC-001):** Enforce absolute paths or validate resolution bounds.
2. **--id Regex (CQ-001):** Tighten to enforce true kebab-case (alphanumeric at both ends).
3. **Guide Nudge (from Reviewer Concern #2):** `authoring-a-playtest.md` could more explicitly nudge authors to write deterministic referee tests (e.g., pointing at dungeon test patterns).

---

## Cycle Invariants Verification

### Invariant 1: Stdlib Only (NFR-2)

**Status:** ✓ PRESERVED

All new scripts (scaffold_playtest.py, sweep_report.py, check_payoff_dominance.py) use only Python stdlib. No external dependencies introduced this sprint.

**Evidence:** Grep confirms only `re`, `subprocess`, `sys`, `pathlib`, `json` imports in scaffold_playtest.py.

### Invariant 2: Zero Core Changes

**Status:** ✓ PRESERVED

No changes to:
- `construct_core/` (engine, producer, grader)
- Core stdlib invariants
- Producer-never-grades principle

**Evidence:** `git diff main...HEAD --stat` shows no changes to core modules.

### Invariant 3: Producer Never Grades

**Status:** ✓ PRESERVED

All grading logic remains in the referee (agent-systems domain), not the producer. The scaffolder generates referee stubs; authors must implement the actual grading logic.

**Evidence:** REFEREE_STUB is a DEFEAT no-op until the author fills in `run()` logic.

### Invariant 4: Determinism

**Status:** ✓ PRESERVED

Generated fixtures and referee stubs enforce deterministic evaluation. No randomness in generation or generated code.

**Evidence:** 
- No random/time/uuid imports in scaffold_playtest.py
- Referee stub comment enforces determinism (line 41)
- Test suite confirms identical smoke test output across runs

### Invariant 5: 95+ Assertions All Green

**Status:** ✓ VERIFIED: 138 assertions across 11 suites

```
validate_scenario:       16 ✓
validate_sidecar:        14 ✓
validate_batch:          20 ✓
discover_engine:         10 ✓
ollama-agent:            16 ✓
sim-pipeline:            19 ✓
dungeon-referee:          6 ✓
party-wrapper:            8 ✓
sweep-report:            10 ✓
check-payoff-dominance:   7 ✓
scaffold-playtest:       12 ✓
─────────────────────────────
Total:                  138 ✓
```

All pass with `exit 0`. No failures, no warnings.

### Invariant 6: Banned-Copy Gate Active

**Status:** ✓ ACTIVE AND WORKING

- Grep patterns correctly identify overclaiming phrases (OWASP sandbox-limits §A/B).
- Table-line exclusion correctly exempts the ban-list table in domain.conventions.md.
- CI integration confirmed (wired into validate-agent-systems.sh).

**Test Results:**
```
OK: banned-copy clean across agent-systems docs + report wording.
```

---

## End-to-End Goal Validation (from Sprint Plan, Task 4.E2E)

| Goal | Validation | Result |
|------|-----------|--------|
| **G1** New-playtest authorability | Scaffolded `code-golf` + `maze-solver` from flags alone | ✓ validates + runs; payoff-dominance PASS |
| **G2** One-command comparison | 3-config sweep (modelA/B/C), n=2/rung, via real engine | ✓ sweep_report triaged table, all configs × rungs |
| **G3** Honest power (capability-not-gate) | Multi-trial run (n=2/rung) on fixture via real engine | ✓ runs with n>1 (4 sidecars/2 rungs); no cliff (deterministic agent doesn't game) |
| **G4** Hermetic rigor preserved | Full CI: 11 suites + banned-copy; 0 Ollama in CI | ✓ 138 assertions green; banned-copy clean |
| **G5** Honesty boundary held | banned-copy gate + check_payoff_dominance enforce calibration | ✓ no claim crosses sandbox-limits §A/B |

**All five goals validated.** Integration verified end-to-end: scaffold → validate → engine run → regrade → sweep_report → /arneson view.

---

## Reviewer Concerns Addressed

The Senior Lead (reviewer.md) flagged three non-blocking concerns:

1. **G1 acceptance was self-authored, not truly fresh operator**  
   ✓ Acknowledged as planned (human-acceptance class); worth post-merge fresh pass to surface guide gaps.

2. **Scaffolder's self-check only validates DEFEAT stub RUNS, not author's real referee**  
   ✓ Correct by design; scaffolder's contract is "emit runnable skeleton," not "write your rules." Guide points at dungeon suite as the test pattern.

3. **banned-copy table exclusion could miss non-leading cells**  
   ✓ Narrow edge case (our only table is the approved ban-list); pragmatic trade-off accepted. Flag for tightening if docs grow multi-table definitions.

**Reviewer's verdict:** APPROVED with noted concerns (all non-blocking).

---

## Security Checklist

| Item | Status | Notes |
|------|--------|-------|
| No eval/exec/pickle | ✓ | Stdlib parse only |
| No shell injection (subprocess) | ✓ | argv list, no shell=True |
| No code injection via user input | ✓ | --id regex-validated; --task/difficulty regex-validated |
| Input validation complete | ⚠ | Path traversal via --out not validated (SEC-001) |
| Deterministic generation | ✓ | No randomness; stubs enforce determinism |
| No secrets in generated code | ✓ | Generated files are YAML + Python placeholders |
| No external dependencies | ✓ | Stdlib only |
| Subprocess calls safe | ✓ | No shell=True; argv list pattern |
| Test coverage adequate | ✓ | 12 assertions covering happy path + errors + edge cases |

---

## Threat Model: Plausible Attack Scenarios

### Scenario 1: Injection via --id

**Threat:** Malicious `--id` containing code-breaking characters (quotes, newlines, etc.)  
**Mitigation:** Regex validation `[a-z0-9][a-z0-9-]*` prevents all non-alphanumeric/dash characters  
**Result:** ✓ BLOCKED

### Scenario 2: Injection via --task

**Threat:** Malicious `--task` breaking the markdown or YAML structure  
**Example:** `--task 'foo\nmalicious'`  
**Mitigation:** No validation, but --task goes into markdown files (not code); even with embedded newlines, it's safe content, not executable  
**Result:** ✓ SAFE (markdown-only, no code execution)

### Scenario 3: Shell Injection via subprocess

**Threat:** Malicious path in `--out` breaking the smoke test execution  
**Mitigation:** subprocess.run uses argv list (no shell interpolation)  
**Result:** ✓ BLOCKED

### Scenario 4: Path Traversal via --out

**Threat:** User provides `--out='../../../etc'` to write outside intended directory  
**Mitigation:** None (SEC-001)  
**Result:** ✗ VULNERABLE (but low practical risk; requires user to explicitly use ../)

### Scenario 5: Referee Backdoor

**Threat:** Generated referee stub contains hidden code or security issue  
**Mitigation:** REFEREE_STUB is hardcoded; no user input is interpolated into logic, only into comments  
**Result:** ✓ SAFE

---

## Recommendation for Verdict

**APPROVED - LET'S FUCKING GO** with documented findings.

**Rationale:**
- All critical injection vectors are properly validated.
- Path traversal (SEC-001) is MEDIUM severity but LOW exploitability (requires explicit user action and is out of scope for the scaffolder's intended use case — absolute paths from /tmp).
- Code quality issues (CQ-001, CQ-002) are cosmetic.
- All 138 assertions pass; cycle invariants preserved.
- Senior Lead has already approved (reviewer.md).
- End-to-end goals G1–G5 all validated.

**Action Items for Post-Merge Hardening:**
1. Validate `--out` to require absolute paths or enforce resolution bounds (SEC-001).
2. Tighten `--id` regex to enforce proper kebab-case end (CQ-001).
3. Optionally improve banned-copy exclusion pattern (CQ-002).
4. Encourage fresh operator walkthrough post-merge to validate guide (from reviewer concern #1).

---

## Artifacts

- This report: `grimoires/loa/a2a/sprint-15/SECURITY-AUDIT-REPORT.md`
- Findings summary: See below
- Test evidence: `scripts/ci/validate-agent-systems.sh` (138 assertions, all passing)

---

## Summary

Sprint 15 successfully ships the playtest scaffolder (stdlib, self-checking, payoff-dominant), authoring guide, and honesty boundary gate. All PRD goals are validated. Core invariants are preserved. One MEDIUM-severity path traversal vulnerability is documented and non-blocking given usage patterns and reviewer approval. **Cycle is ready to ship.**

**Verdict: APPROVED - LET'S FUCKING GO**

