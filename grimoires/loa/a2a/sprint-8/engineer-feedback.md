# Senior Lead Review — Sprint 1 (global sprint-8): CHANGES REQUIRED

**Date:** 2026-06-09 · **Reviewer:** /review-sprint (run mode, cycle 1)
**Verdict:** CHANGES_REQUIRED — 3 items, all addressable in one iteration

## Overall Assessment

Strong sprint. The AC Verification section is complete and honest — all 7 ACs walked verbatim
with file:line evidence, and I verified the claims against the code: drift refusal fires (exit 2
+ `CONTRACT DRIFT`, validate_sidecar.py:55-99), the laundering pair is rejected
(validate_sidecar.py:217-225 + fixtures), the unbounded scenario message is exact
(validate_scenario.py:254), the committed batch passes, the vendored bytes match upstream AND the
pin, and all 40 shell-test assertions are green. Zero core diffs confirmed — FR-1 holds. The
drift-test design (tamper a copied tree rather than introduce a test-only env override) is the
right call.

Three issues block approval; none are architectural.

## Critical Issues (must fix)

### 1. No CHANGELOG.md in the construct repo
- **Where:** repo root — only `.loa/CHANGELOG.md` (the framework submodule's) exists.
- **Issue:** Documentation gate: "CHANGELOG entry for each task — blocking." The construct is
  versioned (construct.yaml:12, `3.3.0`) and this sprint opens v4.0 work with a new public
  surface (a vertical, three schemas, three validator CLIs); there is no changelog recording it.
- **Fix:** Create `CHANGELOG.md` with an `[Unreleased] — 4.0.0-dev` section summarizing Sprint 1
  (vertical scaffold, vendored contract + pin, schemas, validators, fixtures, CI). One stanza is
  enough; subsequent sprints append.

### 2. Unknown scenario keys are silently accepted
- **Where:** domains/agent-systems/scripts/validate_scenario.py (main field walk).
- **Issue:** Verified by probe: a scenario with `memorry: continuing` (typo'd optional field)
  validates exit 0 and the run proceeds with `memory: fresh` default — the operator's intent is
  silently dropped. For an experiment artifact whose whole point is pinned, reproducible setup
  (FR-7), silent key-dropping undermines the contract. The sidecar validator rejects unknown keys
  (`additionalProperties` mirror); the scenario gate should at minimum warn.
- **Fix:** After parsing, diff top-level keys against the known set
  ({scenario_id, fixture, rungs, trials, stopping, memory, safety, visibility, agent_cmd,
  persona}) and emit `WARNING: unknown field 'X' ignored` to stderr. Add a test assertion.
  (WARN, not reject — additive evolution of scenario.schema.yaml stays possible.)

### 3. `validate_obj` is a 140-line function
- **Where:** domains/agent-systems/scripts/validate_sidecar.py:103-243.
- **Issue:** Complexity gate (>50 lines). More practically: when the contract is re-vendored
  (v1 minor revisions are expected — the schema's own evolution policy), a future editor must
  navigate one monolith to find the section to update.
- **Fix:** Split into per-block helpers mirroring the contract's own structure —
  `_validate_producer`, `_validate_experiment`, `_validate_run`, `_validate_observation`,
  `_validate_allof` — each appending to the shared violations list. Behavior identical;
  all existing tests must still pass unmodified.

## Adversarial Analysis

### Concerns Identified (non-blocking, documented)
1. **CI cross-repo checkout may fail on private upstream** (.github/workflows/ci.yaml:99-105):
   `GYGAX_CHECKOUT_TOKEN || github.token` — if the Gygax repo is private and no PAT secret is
   configured, the with-gygax leg fails until the operator adds it. Loud-by-design and documented
   in reviewer.md Known Limitations, but it is a red-CI risk the operator should resolve before
   the PR lands. **Action: operator, not engineer.**
2. **Committed native sidecar carries placeholder hashes**
   (resources/fixtures/native-sidecar.events.yaml: `fixture-hash-not-computed-in-sprint-1`).
   Acceptable now; becomes a real bug if Sprint 4's materializer treats them as verifiable.
   Sprint 4 MUST replace with computed sha256s when the consumer lands — tracked in the report,
   re-flagged here so it survives to Sprint 4's reviewer.
3. **Restricted parser's quiet limits** (validate_scenario.py:55-130): no anchors/multiline
   scalars; an all-digit unquoted sha parses as int (hit and documented via the bad-checksum
   fixture). The schema header documents "keep shapes flat and simple," which is the right
   mitigation; the unknown-key warning (Critical #2) closes the worst silent case.

### Assumption Challenged
- **Assumption:** batch.json may carry extra fields without rejection (validate_batch.py checks
  only schema/fixture/reward_command types).
- **Risk if wrong:** none — verified against the vendored batch doc: "Gygax's own runner also
  writes agent_cmd_template … informational for the grader and may be omitted"
  (observed-trace-batch.v1.md:53-54). Leniency here is contract-correct, strictness on sidecars
  is contract-correct. Asymmetry is intentional; keep it.

### Alternative Not Considered
- **Alternative:** invoke Gygax's own TS `validateSidecar` (via `npx tsx`) in tests instead of
  re-implementing validation in Python.
- **Tradeoff:** would eliminate R-6 (validator divergence) entirely, but breaks NFR-5
  (standalone, stdlib-only — arneson-alone leg can't run node) and makes the hermetic CI leg
  depend on the sibling.
- **Verdict:** current approach justified; the sha256-pin refusal + with-gygax byte-diff is an
  adequate R-6 mitigation. Revisit only if validator drift actually bites.

## Karpathy Check

- Think-before-coding: assumptions surfaced in reviewer.md (vendored_contracts stanza flagged) ✓
- Simplicity: no speculative abstractions found; agent-import correctly left as docs (SDD §3.3) ✓
- Surgical: diff confined to new vertical + the two scoped exceptions; `__pycache__` gitignore
  addition is justified (engineer's own scripts generate it) ✓
- Goal-driven: every AC has a test or mechanical check ✓

## Next Steps

Address items 1-3, re-run `./scripts/ci/validate-agent-systems.sh` (expect 40+ green incl. the
new unknown-key assertion), update reviewer.md with a "Feedback Addressed" section, and return
for re-review.
