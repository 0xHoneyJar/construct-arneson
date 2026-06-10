# Implementation Report: Sprint 2 (global sprint-9) — Real Lane

**Date:** 2026-06-10 · **Sprint:** local 2 / global 9 (ledger cycle-001 agent-sandbox-v4.0)
**Implementer:** /implement (run mode, plan-20260609-agent-sandbox-v4)
**Branch:** feature/sprint-plan-20260609

## Executive Summary

The real lane works end-to-end, live-verified twice: Gygax's engine driven by a deterministic
no-spend agent → batch validated byte-untouched by Arneson's gate → `trace --regrade` →
full claim-tagged gap report (forecast argmax vs observed per rung, cliff analysis). Milestone
(b) zero-edit ingestion: **green** — and the sprint surfaced two real upstream seam bugs,
reported precisely (discovery/gygax-seam-bugs-cycle008.md), fixed by the operator in Gygax
PR #19, and re-verified here. Identity now states the locked-room model and both trust
invariants. `/playout` exists with the full 7-state real-lane machine.

## AC Verification

**AC-1** — "Engine discovery order: `--engine` flag → `ARNESON_GYGAX_ROOT` → sibling probe `../construct-gygax`; candidate valid iff `scripts/lib/ladder/index.ts` exists"
✓ Met — discover_engine.py:35-46 (candidates generator, marker at :22); explicit flag/env are authoritative (no silent fallthrough, :39,:43). Test: test-discover-engine.sh, 10/10 incl. all three resolution paths + hollow-dir no-fallback cases.

**AC-2** — "Absent engine fails immediately with the exact FR-6 message naming the dependency and pointing at simulated mode; no retries, no partial fallbacks"
✓ Met — discover_engine.py:24-28 (message constant matches the sdd.md §6.1 catalog shape); test assertions "MISSING DEPENDENCY: construct-gygax engine not found" + "Simulated mode works standalone" (test-discover-engine.sh:38-40).

**AC-3** — "Guardrail states `this will spawn N real agent runs (rungs × trials = R × T) via: <agent_cmd>` before spawning; `--yes` skips; `--dry-run` never reaches the prompt"
✓ Met — skills/playout/SKILL.md State 3: verbatim prompt form mandated, `--dry-run` short-circuits before the prompt, declined = clean abort ("Nothing spawned", exit-0 semantics). Skill-prose surface (LLM-executed); deterministic sub-steps are scripts.

**AC-4** — "Engine invoked via subprocess argv array (never shell=True), cwd = discovered Gygax root, stdout `--json` parsed, exit 2 mapped to `ENGINE SETUP FAILURE:` with engine stderr attached"
✓ Met — SKILL.md State 4 (argv-array mandate, verbatim agent_cmd as one argument, cwd rule, JSON parse, exit-2 mapping). Live-verified: engine dispatched exactly this way in the probe (scripts/ci/ingestion-probe.sh:24-30).

**AC-5** — "Batch handed over byte-untouched; report's next-step line is the literal `--regrade` command"
✓ Met — SKILL.md State 5 ("NEVER edit a sidecar… handed over byte-untouched") + State 7 (literal `--regrade` line, R-7 rationale inline). Probe asserts the regrade path end-to-end.

**AC-6** — "Playout record written to `grimoires/arneson/playouts/<playout-id>.yaml` with scenario sha256, lane, engine git sha, batch path, counts, validation outcome"
✓ Met — SKILL.md State 6 specifies the exact record shape (all sdd.md §3.5 fields); `output_paths.playouts` registered (construct.yaml). Record-writing is exercised live in Sprint 3's demo run (Task 3.1), the first real `/playout` invocation.

**AC-7** — "`identity/refusals.yaml` drops never-executes, adopts locked-room containment, states both invariants"
✓ Met — refusals.yaml: `host_execution` (locked-room + serialize-never-execute bright line + narration-attack behavior_on_conflict), `authoring_grades` (judge-never-produces-evidence, producer-never-judges), `claim_laundering` (forecast-never-a-sidecar-claim + banned-copy vocabulary). ARNESON.md "The locked room" section states both invariants in identity prose.

**AC-8** — "CI probe: assembled fixture batch → Gygax `trace/index.ts` → grade + diff complete, zero manual edits (milestone b)"
✓ Met — scripts/ci/ingestion-probe.sh (engine run → validate_batch byte-untouched → `--regrade` → report assertions), wired into the with-gygax leg with node setup (.github/workflows/ci.yaml). Local run: "OK: zero-edit ingestion probe complete — engine batch graded + diffed, no edits anywhere." Verified against upstream PR #19 (both seam bugs fixed).

## Tasks Completed

| Task | Deliverable | Evidence |
|------|-------------|----------|
| 2.1 | discover_engine.py + 10-assertion shell test | scripts/discover_engine.py; test-discover-engine.sh 10/10 |
| 2.2 | /playout SKILL.md (7-state real-lane machine, bright lines) + index.yaml; OQ-4 resolved per SDD recommendation (producer.id stays engine truth — NOTES.md Decision Log 2026-06-10, operator may veto at review) | domains/agent-systems/skills/playout/ |
| 2.3 | Identity reframe: 3 new refusal stanzas + ARNESON.md locked-room section | identity/refusals.yaml; identity/ARNESON.md |
| 2.4 | ingestion-probe.sh + CI wiring (node setup, npm ci, probe step on with-gygax leg); validate-skills.sh covers playout | scripts/ci/; .github/workflows/ci.yaml |

## Unplanned-but-necessary (discovered during integration)

- **Seam bug report → upstream fixes:** driving the engine per its README surfaced two
  contract violations in Gygax itself (containment default ignoring `--fixture`; batch.json
  missing its required `schema` field). Reported with file:line + repro
  (discovery/gygax-seam-bugs-cycle008.md), fixed upstream in PR #19 by the operator,
  re-verified here — including the external-fixture path (synthetic fixture now runs
  through the engine: ok=true, 1/1 completed).
- **Synthetic incentive-state rewritten format-true:** Sprint 1's invented shape failed real
  ingestion; now mirrors the upstream format (index.yaml + actions/{fix-code,delete-test} +
  reward/pass-rate.yaml with `intent.intended_action`). Verified: full gap report produced
  against the synthetic fixture (argmax `delete-test`, intended `fix-code`, observed 1/1 fixed).
- **deterministic-agent.py:** task-aware no-spend probe agent (solves both fixtures' tasks
  honestly); test plumbing, clearly documented as not-a-persona.

## Testing Summary

- test-discover-engine.sh — 10/10 (three resolution paths, authoritative-no-fallback cases,
  FR-6 message assertions, usage errors)
- Sprint 1 suites re-run green after incentive-state changes (42/42; scenario pins unaffected —
  manifest.yaml bytes unchanged)
- Live integration ×3: awareness-ladder probe (green end-to-end), external synthetic fixture
  engine run (green), synthetic batch regrade (full report after intent stamp)

## Known Limitations

1. AC-3/4/5/6 are skill-prose mandates executed by the LLM at invocation time; the
   deterministic substeps (gates, discovery, validation) are scripts with tests, but the
   state-machine glue is exercised first in Sprint 3's live demo run (Task 3.1).
2. CI probe requires node + the sibling checkout on the with-gygax leg (npm ci step added);
   first Actions run will confirm the leg end-to-end (same operator-token caveat as Sprint 1).
3. VENDOR.yaml still records upstream git_sha b8dd409 (pre-PR-#19): correct for the vendored
   contract bytes (unchanged by PR #19 — code-only fixes; drift guard green), but worth a
   refresh at next re-vendor.

## Feedback Addressed (cycle 2)

1. **CHANGELOG Sprint 2 entry** → Added under Unreleased: `/playout` real-lane block (Added)
   + identity reframe block (Changed). Pattern adopted: CHANGELOG stanza ships with the
   sprint's implementation from Sprint 3 on.
2. **Probe fixture + stale comment** → Probe now targets the bundled synthetic-incentive
   fixture via $REPO_ROOT (decoupled from upstream fixture churn); stale Bug-1 comment
   replaced. Re-run green: "OK: zero-edit ingestion probe complete."
3. **Double-env prefix in test case 2** → Leading assignment dropped; env-form invocation
   kept with a clarifying comment. Suite re-run: 10/10.

## Verification Steps

```bash
./domains/agent-systems/scripts/test-discover-engine.sh   # 10/10
./scripts/ci/ingestion-probe.sh                           # milestone (b), needs sibling + node
./scripts/ci/validate-skills.sh                           # includes playout
./scripts/ci/vendor-drift-guard.sh                        # still green post-PR-#19
```
