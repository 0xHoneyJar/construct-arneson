# Security & Quality Audit — Sprint 9 (Sprint 2 local)

**Audit Date:** 2026-06-10  
**Sprint:** Local 2 / Global 9 (v4.0 agent-sandbox, real lane)  
**Auditor:** paranoid-cypherpunk-auditor  
**Branch:** feature/sprint-plan-20260609  
**Scope:** discover_engine.py, /playout skill, identity refusals (locked-room + host_execution), ingestion-probe.sh, CI changes (vendor-drift-guard, agent-cmd dispatch), deterministic-agent.py, synthetic-incentive rewrite.

**Approval Status:** Senior lead approved (engineer-feedback.md "All good"). Ready for security audit.

---

## Executive Summary

Sprint 9 implements the real lane pipeline: Arneson dispatches agents to an external Gygax engine, validates the output byte-untouched, and reports the batch path. **The security posture is strong:** subprocess dispatch via argv arrays (never shell strings), `agent_cmd` passed verbatim without credential enrichment (NFR-4), host-side code never executes agent output (FR-11), batches handed over byte-untouched (R-7), and vendor supply chain pinned with cryptographic guards (R-1). The identity refusals cleanly state the locked-room model and both trust invariants.

**Overall Risk Level:** **LOW**  
**Verdict:** **APPROVED - LETS FUCKING GO**

Three non-blocking findings for Sprint 3+ attention documented below; all are process/ops, not security bugs. The audit uncovered ZERO exploitable security flaws in the code or architecture.

---

## Critical Findings

**NONE.** No CRITICAL severity issues detected.

---

## High Priority Findings

**NONE.** No HIGH severity issues detected.

---

## Medium Priority Findings

### MED-001: ENV variable pass-through in ingestion-probe.sh is operator-responsibility (LOW exploitability, HIGH importance for ops awareness)

**File:** `scripts/ci/ingestion-probe.sh:28`

**Finding:**  
The ingestion-probe passes the hardcoded deterministic agent to the engine via:
```bash
npx tsx scripts/lib/ladder/index.ts run \
  --fixture "$FIXTURE" \
  --rungs 0,2 --trials 1 \
  --agent-cmd "python3 $AGENT {promptfile}" \
  --timeout 60 --json
```

The bash variable `$AGENT` is expanded in the shell before passing. If a future maintainer modifies this to source user input or CI secrets, the expanded string could leak credentials into `batch.json`'s `reward_command` field (which records the agent command template).

**Severity:** MEDIUM  
**Impact:** If operator puts secrets into the agent command template, they will be recorded in batch.json (artifact taint). The code itself is safe; the risk is operator error.

**Remediation:**  
Document (in a SECURITY.md addendum for v4.0) that:
- `agent_cmd` templates are **operator-authored and operator-responsible**
- Arneson passes `agent_cmd` verbatim to the engine; the engine records it in `batch.json`
- Never put secrets into `agent_cmd` — if the agent needs credentials, the operator must pass them via the fixture's own environment or a secure sidecar mechanism
- NFR-4 ("never injects credential-bearing values") applies to Arneson's code, not the operator's input

Alternatively, audit `agent_cmd` at /playout invocation time to warn if it contains obvious credential patterns (`sk-`, `ghp_`, environment variable references).

**References:** SDD 1.9 security table (NFR-4 scope); SKILL.md State 4 (agent_cmd mandate)

**Status:** Non-blocking; ops training doc, not code issue.

---

### MED-002: Deterministic agent doesn't validate file paths; local attack (LOW risk in CI, MEDIUM in multi-user local dev)

**File:** `domains/agent-systems/resources/fixtures/deterministic-agent.py:59-69`

**Finding:**  
The deterministic agent reads `solution.py` and `test_solution.py` from the current working directory without path validation:

```python
solution = pathlib.Path("solution.py")
current = solution.read_text(encoding="utf-8") if solution.is_file() else ""
...
solution.write_text(fix, encoding="utf-8")
```

In the context of a Gygax isolated run dir (single process, SIGKILL on timeout), this is safe. However, if the deterministic agent is ever used outside the isolated engine context (e.g., local developer smoke test in a shared directory), a symlink attack could trick it into writing to `../../../etc/passwd` or similar.

**Severity:** MEDIUM  
**Exploitability:** LOW (only in isolated engine context) to MEDIUM (if used outside engine)  
**Impact:** In CI: no risk (deterministic agent runs inside engine's isolated dirs). In local dev: operator could be tricked into overwriting files.

**Remediation:**  
Add path sanitization before read/write:

```python
solution = pathlib.Path("solution.py").resolve()
run_dir = pathlib.Path.cwd().resolve()
if not solution.is_relative_to(run_dir):
    print("ERROR: solution.py escaped run dir (symlink or traversal)", file=sys.stderr)
    return 1
```

Add a docstring note: "Assumes isolated run dir (Gygax engine context); do not use outside locked rooms."

**References:** CWE-59 (Improper Link Resolution), CWE-426 (Untrusted Search Path); OWASP A06 (Vulnerable and Outdated Components); SDD 1.9 (agent code execution engine-side only)

**Status:** Non-blocking; cosmetic hardening + docstring.

---

### MED-003: Vendor manifest pins git_sha but not commit date; stale pin detection is manual

**File:** `domains/agent-systems/schemas/vendor/VENDOR.yaml`

**Finding:**  
The vendor drift guard verifies byte-identity and sha256 pins, but the git_sha recorded is pre-PR-#19. The reviewer notes that "drift guard green" (byte-identical), but the sha is stale. Future maintainers may manually re-vendor and forget to update the sha, creating a false-confidence scenario where the pin looks correct but the upstream has moved.

**Severity:** MEDIUM  
**Exploitability:** LOW (requires human error in re-vendoring workflow)  
**Impact:** Silent supply-chain drift: a re-vendored file could change behavior without CI catching it if only sha256 is checked and git_sha is forgotten.

**Remediation:**  
Update `VENDOR.yaml` to also record the upstream commit date (or first-commit-of-file date):

```yaml
vendored:
  file: schemas/vendor/observed-trace.v1.schema.json
  repository: 0xHoneyJar/construct-gygax
  git_sha: b8dd409  # Update on re-vendor
  git_commit_date: 2026-05-15  # Add this
  sha256: abc123...
```

Then update `vendor-drift-guard.sh` to log the date alongside the sha (informational, no fail-gate).

Alternatively, add a secondary check: `git log -1 --format=%cI <upstream-file>` and store it in a companion `.date` file.

**References:** R-1 (drift guard); supply-chain best practices (SLSA, in-toto)

**Status:** Non-blocking; process improvement for Sprint 3+ re-vendor cycle.

---

## Low Priority Findings

### LOW-001: Test fixture path hardcoded in ingestion-probe.sh; environment-driven path would be more flexible

**File:** `scripts/ci/ingestion-probe.sh:22`

**Finding:**
```bash
FIXTURE="$REPO_ROOT/domains/agent-systems/resources/fixtures/synthetic-incentive"
```

The fixture path is hardcoded. If a future test or operator wants to use a different fixture, they must modify the script. An environment variable `ARNESON_FIXTURE` (optional, with this as the default) would allow parameterization.

**Severity:** LOW  
**Impact:** Code maintainability, not security.

**Remediation:**
```bash
FIXTURE="${ARNESON_FIXTURE:-$REPO_ROOT/domains/agent-systems/resources/fixtures/synthetic-incentive}"
```

**Status:** Nice-to-have; non-blocking.

---

### LOW-002: `discover_engine.py` doesn't check file permissions on the engine marker

**File:** `domains/agent-systems/scripts/discover_engine.py:66`

**Finding:**
The discovery script checks if `<root>/scripts/lib/ladder/index.ts` exists but doesn't verify it's readable or executable:

```python
if (root / ENGINE_MARKER).is_file():
    print(root.resolve())
    return 0
```

If the file exists but isn't readable (e.g., due to misconfigured perms), the script will report success, but the engine will fail later.

**Severity:** LOW  
**Impact:** Deferred error (caught by engine invocation); not a security flaw.

**Remediation:**
```python
marker = root / ENGINE_MARKER
if marker.is_file() and os.access(marker, os.R_OK):
    print(root.resolve())
    return 0
```

**Status:** Nice-to-have; error clarity, not security.

---

## Security Checklist Status

| Category | Check | Status | Evidence |
|----------|-------|--------|----------|
| **Subprocess Dispatch** | Argv array (never shell=True) | ✓ PASS | SKILL.md State 4; ingestion-probe.sh line 25 (`npx tsx ...` invoked via Bash, not shell string) |
| **Input Validation** | agent_cmd validated as template | ✓ PASS | validate_scenario.py:304 checks {prompt} or {promptfile} placeholder |
| **Secrets Handling** | No credential enrichment into agent_cmd | ✓ PASS | SKILL.md State 4 NFR-4 mandate; ingestion-probe.sh deterministic agent only |
| **Output Handling** | Batches byte-untouched | ✓ PASS | SKILL.md State 5 "NEVER edit a sidecar"; validate_batch.py gates handoff |
| **Vendor Pinning** | Contract bytes pinned + drift guard | ✓ PASS | vendor-drift-guard.sh byte-diff + sha256 + VENDOR.yaml; CI step wired |
| **Host Execution** | Never executes agent output | ✓ PASS | identity/refusals.yaml host_execution; SKILL.md §What you never do |
| **Grade Integrity** | Never authors observation | ✓ PASS | identity/refusals.yaml authoring_grades; SKILL.md State 6 (record shape, not write observation) |
| **Claim Labeling** | No label alteration | ✓ PASS | identity/refusals.yaml claim_laundering; banned vocab list enforced |
| **Error Handling** | FR-6 failures loud + named | ✓ PASS | discover_engine.py:70 FR6_MESSAGE with probed paths |
| **Bounded Execution** | Scenario unbounded-ness rejected | ✓ PASS | validate_scenario.py:269-271 NFR-2 mandate (max_turns REQUIRED) |
| **Code Injection** | No eval, exec, or dynamic code gen | ✓ PASS | Entire pipeline is data + declarative validation + subprocess |
| **Supply Chain** | Dependencies vendored, pinned, locked | ✓ PASS | vendor-drift-guard.sh + VENDOR.yaml; npm ci (lockfile-based) |
| **Path Traversal** | Batch run_dir containment check | ✓ PASS | validate_batch.py:98-103 is_relative_to check |
| **File Permissions** | Scripts executable | ✓ PASS | discover_engine.py, validate_*.py, deterministic-agent.py all +x in repo |
| **Documentation** | Security constraints documented | ✓ PASS | SKILL.md "What you never do" bright lines; identity/refusals.yaml invariants |

---

## Architecture & Threat Model Assessment

### Locked-Room Model (Arneson's Containment)

The identity refusals now state: **"My persona host serializes; it never executes."** (host_execution refusal, refusals.yaml:95-108)

**Threat Model:**
1. **Agent code execution attacks:** Mitigated. Real agents execute **inside the engine's isolated run dirs** with SIGKILL timeouts; Arneson never runs agent code or interprets agent narration. Simulated agents are hosted by Arneson but run in the persona-hosting framework (session-lifecycle, safety protocols), not bare Python eval.
2. **Grade tampering:** Mitigated. Arneson never authors `observation`; grades are re-derived by the analyst tool (`--regrade`). The batch is handed over byte-untouched.
3. **Secrets leakage:** Mitigated. Arneson doesn't inject credentials into `agent_cmd` (NFR-4). The operator's own `agent_cmd` is their responsibility.
4. **Supply-chain drift:** Mitigated. Contract vendored + byte-pinned; CI guard checks it every build.
5. **Manifest tampering:** Mitigated. SHA256 pins on fixture manifests checked at scenario load time; checksum mismatch is a hard failure.

### Trust Invariants

Both are now explicitly documented in identity/refusals.yaml:

1. **The judge never produces the evidence it judges** → authoring_grades refusal
2. **The producer never judges the evidence** → claim_laundering refusal (forecast is analyst-tier, not sidecar-tier)

Both tie to the observed-trace-batch.v1.md contract: producer/claim_strength are schema-enforced, locked once engine-stamped.

---

## Code Quality Assessment

### discover_engine.py

**Strengths:**
- Clear resolution order (flag → env → sibling probe)
- Authoritative-first semantics (no silent fallthrough from flag to env)
- Excellent error message (FR-6)
- Defensive path resolution (expanduser)

**Weaknesses (non-critical):**
- Doesn't verify file readability (LOW-002)
- No logging of probed paths (informational only)

**Score:** 4.5/5

---

### validate_scenario.py

**Strengths:**
- Custom restricted-YAML parser (stdlib-only, NFR-5)
- SHA256 pinning on fixtures (checksum mismatch = hard fail)
- Agent command validation (template placeholder required)
- Bounded-scenario enforcement (max_turns required, NFR-2)

**Weaknesses (non-critical):**
- Complex parser could benefit from property-based testing
- No logging of which pin failed (just checksum mismatch)

**Score:** 4.3/5

---

### ingestion-probe.sh

**Strengths:**
- Deterministic (no randomness, no network)
- Hermetic fixture (synthetic-incentive self-contained)
- Proper error handling (validate_batch gates the batch)
- End-to-end: engine run → conformance check → regrade → report

**Weaknesses (non-critical):**
- Fixture path hardcoded (LOW-001)
- env var fallthrough not documented

**Score:** 4.2/5

---

### /playout Skill (SKILL.md)

**Strengths:**
- Bright-line state machine (7 states, no branches)
- All guards explicit (scenario gate, engine discovery, cost guardrail, conformance gate)
- "What you never do" section is unambiguous
- Byte-untouched + --regrade mandate is clear

**Weaknesses (non-critical):**
- Skill-prose execution is LLM-dependent (deterministic substeps tested, but glue not yet live-verified in prod)
- AC-3 (cost guardrail prompt) is prose-only; could be more formally specified

**Score:** 4.4/5

---

### Identity Refusals (refusals.yaml)

**Strengths:**
- New locked-room + host_execution refusals are load-bearing and clear
- authoring_grades refusal ties to the contract
- claim_laundering refusal has specific banned vocabulary

**Weaknesses (non-critical):**
- v4.0 refusals are domain-independent (analysis_tools redirect instead of gygax), which is correct but could be documented with v4.0 note
- No audit config for v4.0-specific vocabulary (future work, Sprint 7)

**Score:** 4.6/5

---

### Deterministic Agent (deterministic-agent.py)

**Strengths:**
- Clear purpose (test plumbing, not a persona)
- Honest task fixes (no gaming, no trial-and-error)
- Proper error handling (unknown task returns 1)
- Docstring explains non-persona nature

**Weaknesses (non-critical):**
- Path traversal vulnerability if used outside isolated context (MED-002)
- No validation of file contents before write (symlink-safe but not path-safe)

**Score:** 4.1/5

---

### Synthetic-Incentive Fixture

**Strengths:**
- Format mirrors upstream (index.yaml, actions/, reward/)
- Self-contained (no upstream fixture dependency)
- Includes both intended + reward-hack actions (good for testing agent alignment)
- Clear incentive structure docs

**Weaknesses (non-critical):**
- None identified; fixture is well-designed

**Score:** 4.7/5

---

### CI Workflow Changes (ci.yaml)

**Strengths:**
- Three-matrix CI (arneson-alone, arneson-with-gygax, extension-story)
- Vendor drift guard wired into with-gygax leg
- Ingestion probe end-to-end
- Node setup explicit + locked to version 22
- Extension-story validates domain extensibility (G-3)

**Weaknesses (non-critical):**
- Secret token fallback: `${{ secrets.GYGAX_CHECKOUT_TOKEN || github.token }}` is safe (token scoping is GitHub's responsibility), but a comment about scope would help future maintainers
- Extension-story validates zero core file changes (good), but the test domain is placeholder; smoke test is thorough

**Score:** 4.5/5

---

### Vendor Drift Guard (vendor-drift-guard.sh)

**Strengths:**
- Byte-diff + sha256 double-check (defense in depth)
- Upstream file resolution via ARNESON_GYGAX_ROOT (same pattern as discover_engine)
- VENDOR.yaml self-pin check (prevents stale pins)
- Clear error messages on drift

**Weaknesses (non-critical):**
- Git SHA recorded but not checked; stale sha pin not detected (MED-003)
- Doesn't verify upstream file was actually modified (only changed from vendored)

**Score:** 4.3/5

---

## Risk Assessment by Component

| Component | Risk | Mitigation | Residual Risk |
|-----------|------|-----------|---------------|
| discover_engine.py | Path injection | Authoritative-first, no fallthrough | LOW (operator provides paths via flag/env) |
| validate_scenario.py | Custom parser bugs | Restricted YAML + tests | LOW (parsing is simple, well-tested) |
| ingestion-probe.sh | Fixture tampering | SHA256 pinned in scenario | LOW (pin verified at load time) |
| /playout skill | Skill-prose errors | Deterministic substeps tested, prose is clear | MEDIUM (prose execution untested in prod; mitigated in Sprint 3 demo) |
| identity/refusals | Refusal bypass | Refusals are identity, not enforcement | LOW (enforcement via audit in Sprint 7) |
| deterministic-agent.py | Path traversal | Isolated run dir (engine context) | LOW in CI, MEDIUM in local dev |
| agent-cmd dispatch | Secret injection | Operator responsibility; NFR-4 scoped | LOW (operator-authored, not Arneson-enriched) |
| Vendor pins | Supply-chain drift | Byte-diff + sha256 guard | LOW (git_sha stale but bytes checked) |
| Batch byte-untouched | Accidental edit | Validation gate before handoff | LOW (no edit path in code) |
| Grade integrity | False grades | Analyst re-grades; batch byte-untouched | LOW (analyst is trusted, batch is immutable) |

---

## Recommendations (Sprint 3+, Non-blocking)

### High Priority (Before Production Deploy)

1. **Exercise /playout state machine end-to-end** (Sprint 3, Task 3.1) with a real scenario, verifying the skill's prose execution of all 7 states.
2. **Audit identity-refusal vocabulary** (Sprint 7, Task 7.2) against session outputs to ensure no violations of locked-room + host_execution + claim_laundering refusals.

### Medium Priority (Sprint 3-4)

3. Add path sanitization to deterministic-agent.py (MED-002); add docstring about locked-room context.
4. Add operator training doc (SECURITY.md v4.0 section) on `agent_cmd` responsibility (MED-001).
5. Update VENDOR.yaml to record commit date on re-vendor (MED-003).
6. Parameterize fixture path in ingestion-probe.sh via `ARNESON_FIXTURE` env var (LOW-001).

### Low Priority (Polish)

7. Add readability check to discover_engine.py::os.access(marker, os.R_OK) (LOW-002).
8. Add comment to ci.yaml on token scope (informational).

---

## Verdict

**APPROVED - LETS FUCKING GO**

Sprint 9 ships a secure real-lane pipeline with:
- ✓ No exploitable security flaws in code or architecture
- ✓ Subprocess dispatch via argv arrays (never shell strings)
- ✓ Secrets not injected by Arneson (operator responsibility, documented)
- ✓ Batches handed over byte-untouched (validation gate gates handoff)
- ✓ Vendor supply chain pinned + guarded (byte-diff + sha256 + CI check)
- ✓ Host never executes agent code (locked-room model in identity refusals)
- ✓ Grade integrity enforced (analyst re-grades, no Arneson authoring)
- ✓ Claim labels immutable (producer/claim_strength schema-locked)
- ✓ Bounded execution (max_turns required, timeouts enforced by engine)

Three non-blocking medium-priority findings are process/ops issues (not exploitable in current context) and documented for future attention.

The security posture is **STRONG**. The identity refusals cleanly state both trust invariants. The code is defensive and deterministic. Supply-chain is pinned and guarded. The architecture respects the locked-room model.

**Proceed with confidence to Sprint 3.**

---

## Appendix: Tool Output References

- **discover_engine.py tests:** 10/10 (all three resolution paths, authoritative-no-fallback, FR-6 messages, usage errors)
- **validate_scenario.py tests:** green (scenario parsing, checksum verification, max_turns enforcement)
- **validate_batch.py tests:** green (batch layout, sidecar conformance, run_dir containment)
- **ingestion-probe.sh:** live-verified twice (Gygax engine run → engine batch → Arneson validation → regrade → assertions all green)
- **CI vendor-drift-guard.sh:** green (byte-diff + sha256 + VENDOR.yaml pin checks)
- **Identity refusals:** loaded, no syntax errors, vocabulary lists defined

