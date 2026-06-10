# Senior Lead Review — Sprint 2 (global sprint-9): CHANGES REQUIRED

**Date:** 2026-06-10 · **Reviewer:** /review-sprint (run mode, cycle 1)
**Verdict:** CHANGES_REQUIRED — 3 items, one iteration

## Overall Assessment

The lane works and the evidence is live, not claimed: probe green end-to-end post-upstream-fix,
external fixture verified, synthetic fixture produces a full gap report. The seam-bug detour was
handled exactly right — precise upstream report, no local patching-over, re-verified after the
operator's fix. AC Verification walks all 8 ACs with honest evidence, including the honest
limitation that the skill's state-machine glue is prose executed at invocation time.

## Critical Issues (must fix)

### 1. CHANGELOG has no Sprint 2 entry
- **Where:** CHANGELOG.md — `[Unreleased] — 4.0.0-dev` covers Sprint 1 only.
- **Issue:** Same gate as last sprint: every sprint appends. Sprint 2 added a user-facing
  command (`/playout`), identity changes, and CI surface.
- **Fix:** Append a Sprint 2 block under Unreleased (playout real lane, engine discovery,
  locked-room identity reframe, ingestion probe, seam bugs found+fixed-upstream note).
  Pattern note for the remaining sprints: the CHANGELOG stanza is part of the sprint's
  definition of done — write it with the implementation, not after review.

### 2. Ingestion probe still targets Gygax's fixture; its justifying comment is stale
- **Where:** scripts/ci/ingestion-probe.sh:10-12 ("until upstream Bug 1 … allows external
  fixtures") and the `--fixture evals/awareness-ladder` invocation.
- **Issue:** Bug 1 is fixed and externally verified this sprint — the stated reason for using
  Gygax's fixture no longer exists. Probing on their fixture couples our CI to their task
  content (their fixture churn breaks our leg); the bundled synthetic fixture is ours,
  format-true, and now proven through the full pipeline including the gap report.
- **Fix:** Point the probe at `domains/agent-systems/resources/fixtures/synthetic-incentive`
  (absolute path via $REPO_ROOT), drop the stale comment, keep everything else identical.
  Local run must stay green.

### 3. test-discover-engine.sh case 2 has a redundant double-env prefix
- **Where:** test-discover-engine.sh:36-37 — `ARNESON_GYGAX_ROOT="$FAKE/engine" check … env
  ARNESON_GYGAX_ROOT="$FAKE/engine" python3 …`.
- **Issue:** The leading assignment applies to `check` (a shell function) and is then shadowed
  by the explicit `env` — works, but reads as if both matter. Test intent (flag beats env,
  no fallback) deserves unambiguous form.
- **Fix:** Drop the leading `ARNESON_GYGAX_ROOT=…` prefix; keep the `env`-form invocation.

## Adversarial Analysis

### Concerns Identified (non-blocking)
1. **AC-6 is a mandate, not yet an artifact** (SKILL.md State 6): no playout record exists on
   disk yet. Acceptable because the plan's own sequencing puts the first live `/playout` in
   Sprint 3 (Task 3.1) — but Sprint 3's review MUST verify the record against the State 6 shape.
   Carried forward explicitly.
2. **npm ci on the with-gygax leg** adds runtime + a lockfile compatibility dependency on
   upstream's node version matrix. Acceptable (engine-owned dependency, NFR-5), watch the
   first Actions run.
3. **claim_laundering vocabulary** ("hard metrics", "zero hallucination") now in refusals —
   the identity-refusal audit greps Arneson-generated prose for these. Make sure Sprint 3's
   docs use them only in quoted banned-copy lists (scan_mode covers archetype voice, but
   docs land in-repo; keep the banned-list framing explicit).

### Assumption Challenged
- **Assumption:** the LLM executing /playout will follow SKILL.md's 7-state machine faithfully.
- **Risk if wrong:** guardrail skipped or batch edited — exactly the failure classes the
  bright lines exist to stop.
- **Recommendation:** Sprint 3's live demo run doubles as the behavioral test; its review
  must check the transcript against the state machine. (Deterministic gates already bound
  the blast radius: validators refuse independently of the LLM.)

### Alternative Not Considered
- **Alternative:** a deterministic `playout.py` orchestrator (argparse CLI) instead of
  skill-prose glue.
- **Tradeoff:** stronger guarantees on sequencing; but loses the skill-pack architecture's
  operator interaction (guardrail conversation, pause semantics) and diverges from how every
  other Arneson skill works.
- **Verdict:** current approach justified by construct architecture; revisit only if Sprint 3
  shows state-machine drift.

## Next Steps

Fix 1-3, re-run the probe locally, append "Feedback Addressed" to reviewer.md, return.
