# Implementation Report: Sprint 4 (global sprint-11) — Simulated Lane + E2E

**Date:** 2026-06-10 · **Sprint:** local 4 / global 11 (ledger cycle-001 agent-sandbox-v4.0)
**Implementer:** /implement (run mode, plan-20260609-agent-sandbox-v4)
**Branch:** feature/sprint-plan-20260609

## Executive Summary

Milestone (d) complete and the cycle's goals all validated. The simulated lane runs
hermetically end-to-end (native sidecar → projection → materialization → assembly →
validation: 14/14 new assertions, 66 total across 5 suites), and the OQ-1 probe resolved
POSITIVE live: Gygax's own `ladder score --batch` filled `observation: fixed` on a
materialized simulation batch while preserving `producer: simulation` /
`claim_strength: simulation-derived`, and the scored batch ingested into a gap report. The
bundled neutral persona + agent-import doc make the temperament axis usable. Task 4.E2E:
5/5 goals validated with evidence.

## AC Verification

**AC-1** — "Simulated `/playout` works with zero Gygax install: playout, native sidecar, and projection all complete; report labels the batch `standalone simulated batch — ungraded; not Gygax-ingestible until scored`"
✓ Met — hermetic pipeline green with no Gygax involvement (test-sim-pipeline.sh, 14/14, no network); the verbatim standalone label is mandated at SKILL.md State S5 and the matching honesty warning fires mechanically (validate_batch warning asserted in tests).

**AC-2** — "Dual emission: native sidecar (full fidelity) + deterministic projection with playout prose as `narration`; no LLM on the projection path"
✓ Met — project_trace.py (pure stdlib transform; narration assembled from agent_turn prose at :131-137); projected record validated against the vendored contract in-suite ("projected record conforms" assertion).

**AC-3** — "Preamble records provenance + context manifest so the rung's visibility claim is verifiable"
✓ Met — session-events-agent schema (preamble_extensions) + SKILL.md State S2 (computed, not asserted); fixture native sidecar now carries real computed sha256s (placeholders eliminated — Sprint 1 carried item discharged); projection hard-requires provenance (project_trace.py:63-66).

**AC-4** — "`artifact_declare` contents materialized verbatim into `runs/rung-R/trial-T/`, seeded from the fixture's `task-template/` so `protected_baseline` files are diffable"
✓ Met — materialize_artifacts.py (seed at :73-76, verbatim overlay at :78-97, content_sha256 verified, run-dir containment); tests assert seeded baseline + overlay present AND that materialized artifacts actually pass the fixture's reward command.

**AC-5** — "When engine present: `observation` filled only by Gygax's `ladder score --batch`; `producer` preserved as `simulation`; Arneson logic never authors a classification"
✓ Met — OQ-1 probe executed live: score filled `observation: fixed`, producer/claim preserved, scored batch re-validated exit 0 and ingested into a gap report. Arneson's projection never emits observation (asserted: "host must not grade").

**AC-6** — "Host serializes, never executes: no agent-narrated content is run by Arneson-side tooling"
✓ Met — materialize writes bytes only (no exec/eval/subprocess in any pipeline script — same posture sprint-9's audit verified); the one place artifacts ARE executed is the fixture's reward command run by the TEST harness and by Gygax's scorer — the analyst's flow, inside the run dir, per contract.

**AC-7** — "`/pause` + safety commands + stopping condition honored mid-playout"
✓ Met — SKILL.md State S3 (max_turns → trial_end stop_reason, pause/safety as base events, append-only); stopping is hard-gated upstream by validate_scenario (UNBOUNDED REJECTED, Sprint 1).

**AC-8** — "Projection round-trip + hermetic playout CI jobs green on the arneson-alone leg"
✓ Met — both folded into test-sim-pipeline.sh, wired in validate-agent-systems.sh (alone leg); local full run: 66/66 assertions + committed-batch conformance green.

## Task 4.E2E: Goal Validation (5/5)

| Goal | Validation performed | Result |
|------|----------------------|--------|
| G-1 real-lane loop closure | Sprint 3 evidence re-verified: playout record awareness-ladder-demo-20260610T045207Z.yaml on disk; batch re-validatable; regrade re-renderable | ✓ zero edits anywhere |
| G-2 every layer observable | 7-layer walk vs the simulated playout artifacts: L1 scenario pins (checksum-gated) / L2 provenance preamble (projection-required) / L3 agent_turn+seq+at (schema) / L4 timeline (seq/at enforced envelope) / L5 scenario-level safety + pause events (gated required) / L6 artifact_declare hash-verified at materialization (tested) / L7 validate_sidecar+validate_batch+drift guard+CI | ✓ each layer has a capture AND a machine validator |
| G-3 stranger-operable | Sprint 3 fresh-operator walkthrough (REACHED GAP REPORT) remains the gate evidence; quickstart extended with the preview-lane section (additive pointer-level change) | ✓ |
| G-4 honest labeling | 100% of records across both lanes' live batches carry producer+claim (3/3 checked: 2 real-agent-observed, 1 simulation-derived); banned-copy grep over docs/: 0 hits | ✓ |
| G-5 pairing compounds | docs/pairing-workflow.md: 6-step loop, literal commands for /playout, /voice, trace ingest | ✓ |

Integration check: real batch AND simulated batch both passed `validate_batch.py` and both
reached Gygax grading (regrade / score respectively). No goal marked not-achieved.

## Tasks Completed

| Task | Deliverable |
|------|-------------|
| 4.1 | Persona-host wiring (SKILL.md States S1-S3: mask, manifest, provenance, memory, append-only, safety) |
| 4.2 | neutral-agent.yaml + pinned source spec + docs/importing-an-agent.md |
| 4.3 | project_trace.py + round-trip assertions |
| 4.4 | materialize_artifacts.py + assemble_batch.py + tests (incl. run-dir containment hardening found BY the test) |
| 4.5 | Simulated lane in /playout (States S4-S6: pipeline, score-on-assemble, honest labels, record) |
| 4.6 | OQ-1 probe POSITIVE (live); CI suites wired (alone leg) |
| 4.E2E | 5/5 goals validated (table above) |
| — | restricted_yaml.py extracted as shared parser (+literal blocks, +inline maps); validate_scenario refactored onto it, 16/16 unchanged; fixture hashes computed (carried item) |

## Known Limitations

1. The host loop (States S2-S3) is skill-prose like the real lane's glue — its first live
   exercise is post-cycle (no spend was warranted for a hosted-persona demo this sprint;
   the deterministic pipeline downstream of the host is fully tested).
2. OQ-1 probe ran against the local Gygax checkout (PR #19 state); if upstream's scorer
   semantics change, the with-gygax CI leg is the tripwire.
3. `restricted_yaml.py` literal-block support covers `key: |` only (not `|-`/`|+` chomping
   variants) — sufficient for committed shapes, documented in the module header.

## Verification Steps

```bash
./scripts/ci/validate-agent-systems.sh            # 66 assertions, 5 suites, hermetic
python3 domains/agent-systems/scripts/project_trace.py \
  --native domains/agent-systems/resources/fixtures/native-sidecar.events.yaml --out /tmp/t
python3 domains/agent-systems/scripts/validate_sidecar.py /tmp/t/rung-0-trial-1.json
```

## Audit Feedback Addressed (cycle 2)

Sprint-11 audit returned CHANGES_REQUIRED with two findings; both fixed + both demanded test cases added:

1. **MEDIUM CWE-22 — unvalidated `state_path`** → project_trace.py now rejects absolute/`~` paths (exit 2) and resolves+containment-checks against the sidecar's own directory (`is_relative_to`); paths can no longer escape or inject. Tests: "escaping state_path rejected" + "absolute state_path rejected" + message assertion.
2. **MEDIUM — uncaught timestamp ValueError** → `_iso_ms_delta` raises a named ValueError; the call site catches it and emits a catalog-style `ERROR: … invalid timestamp …` with exit 2, no traceback. Test: "malformed timestamp fails with named error" + message assertion.

Suite after fixes: 19/19 (sim-pipeline), 71 assertions total across 5 suites; full hermetic check green.
