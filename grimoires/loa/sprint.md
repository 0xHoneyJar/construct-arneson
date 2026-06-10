# Sprint Plan: construct-arneson v4.0 — The Agent Sandbox

**Version:** 4.0
**Date:** 2026-06-09
**Author:** Sprint Planner Agent (/sprint-plan)
**PRD Reference:** `grimoires/loa/prd.md` (v4.0, 2026-06-09)
**SDD Reference:** `grimoires/loa/sdd.md` (v4.0, 2026-06-09)
**Predecessor:** Sprint Plan v3.4 (complete — freeside adapter shipped, verified by /ride 2026-06-09)
**Ledger:** cycle-001 `agent-sandbox-v4.0` — local sprints 1–4 = global sprints 8–11

---

## Executive Summary

Ship `domains/agent-systems/` — one new vertical, one skill (`/playout`), zero core changes
(FR-1). **Real mode is the primary lane** and G-1 is the gate:

> "A real agent runs via `/playout --real` → batch conforming to `observed-trace-batch/v1`,
> ungraded sidecars + artifacts → Gygax grades on ingest and produces the predicted-vs-observed
> diff. Zero manual edits anywhere." (prd.md:55)

Four sprints map 1:1 to the PRD milestones: "(a) sidecar/batch conformance → (b) zero-edit
ingestion by Gygax's trace CLI → (c) G-1 loop closure. Simulated lane follows as milestone (d)"
(prd.md:61-63).

**Total Sprints:** 4
**Timeline:** quality-driven, no fixed date — "Timeline: quality-driven, no fixed date (Phase 2 Q2)" (prd.md:63). Sprints gate on milestone evidence, not dates.

---

## Sprint Overview

| Sprint | Theme | Milestone | Scope | Dependencies |
|--------|-------|-----------|-------|--------------|
| 1 | Conformance substrate | (a) conformance | LARGE (7 tasks) | None |
| 2 | Real lane | (b) zero-edit ingestion | MEDIUM (4 tasks) | Sprint 1 |
| 3 | Loop closure + docs | (c) G-1 gate | MEDIUM (4 tasks) | Sprint 2 + Gygax checkout |
| 4 | Simulated lane | (d) secondary milestone | LARGE (7 tasks) | Sprint 1 (3 hard), Sprint 3 (sequencing) |

---

## Sprint 1: Conformance Substrate (milestone a)

**Scope:** LARGE (7 tasks)

### Sprint Goal
Stand up the `domains/agent-systems/` vertical with the vendored contract, the three domain
schemas, and deterministic validators — so that anything claiming to be a batch can be
machine-checked before any agent ever runs.

### Deliverables
- [x] `domains/agent-systems/` scaffold registered in construct.yaml, extension-story CI still green
- [x] Vendored `observed-trace.v1` contract with `VENDOR.yaml` sha256 pin
- [x] Three domain schemas: `scenario`, `session-events-agent`, `agent-persona`
- [x] Three validators (`validate_scenario.py`, `validate_sidecar.py`, `validate_batch.py`) with shell tests
- [x] Synthetic incentive fixture + committed fixture batch + fixture native sidecar
- [x] CI: schema validation + batch conformance (arneson-alone) + vendor drift guard (arneson-with-gygax)

### Acceptance Criteria
- [x] `extension-story` CI job passes with the new vertical present and **zero core diffs** — FR-1's proof (sdd.md §7.1)
- [x] `validate_sidecar.py` refuses to run (exit 2) when vendored schema sha256 ≠ `VENDOR.yaml` (sdd.md §5.2.1)
- [x] Each `allOf` conditional has a rejection fixture pair — e.g. `producer.kind: simulation` + `claim_strength: real-agent-observed` is rejected ("the laundering case the schema exists to stop" — sdd.md §7.2)
- [x] Scenario without `stopping.max_turns` rejected: `UNBOUNDED SCENARIO REJECTED` (NFR-2, sdd.md §6.1)
- [x] Committed fixture batch passes `validate_batch.py` exit 0
- [x] All validators are Python 3.10+ stdlib only — no PyYAML, no JSON-Schema library (NFR-5, sdd.md §2)
- [x] `domains/agent-systems/schemas/` covered by `scripts/ci/validate-schemas.sh` (closes the character-voice zero-coverage pattern for this domain — drift-report finding #3)

### Technical Tasks
- [x] Task 1.1: Scaffold `domains/agent-systems/` (skills/, schemas/, scripts/, resources/, docs/) + `domain.conventions.md` stub under the five-part extension contract; register `domains.agent-systems` + `output_paths.playouts: grimoires/arneson/playouts/` in construct.yaml. New files only (FR-1). → **[G-1]**
- [x] Task 1.2: Vendor the contract: byte-exact copies of `construct-gygax/schemas/observed-trace.v1.schema.json` + `observed-trace-batch.v1.md` into `domains/agent-systems/schemas/vendor/` + `VENDOR.yaml` recording upstream repo, path, git sha, sha256 per file (FR-9, R-1, sdd.md §3.4). → **[G-1, G-4]**
- [x] Task 1.3: Author the three domain schemas: `scenario.schema.yaml` (fixture+checksum, rungs, trials, REQUIRED stopping, memory policy, safety agreement block, per-rung visibility mask, `agent_cmd`/persona per lane — FR-7, sdd.md §3.1), `session-events-agent.schema.yaml` (preamble: scenario_id, run_id, provenance, context_manifest, visibility_rung, memory_policy; events: rung_start, agent_turn, artifact_declare, trial_end; per-event seq+at required — FR-8, FR-10, sdd.md §3.2), `agent-persona.schema.yaml` (source ref+sha256+kind, disposition, capabilities, knowledge, rung_overlays — FR-5, FR-12, sdd.md §3.3). → **[G-2]**
- [x] Task 1.4: Implement `validate_scenario.py` (`--lane real|simulated`; checksum verification; stopping-condition gate; one-variable INFO note) + `test-validate-scenario.sh` covering happy path, each exit-1, each exit-2 (sdd.md §5.3, §7.2). → **[G-2]**
- [x] Task 1.5: Implement `validate_sidecar.py` (contract-specific: required keys, enums, additionalProperties rejection, three allOf conditionals, sha256 self-check against VENDOR.yaml) + `validate_batch.py` (batch.json fields, sidecars/ present, run_dir containment, per-sidecar delegation) + shell tests incl. drift-guard refusal and allOf fixture pairs (FR-9, sdd.md §5.2.1, §7.2). → **[G-1, G-4]**
- [x] Task 1.6: Author bundled synthetic incentive fixture (mirrors Gygax's fixture manifest shape — manifest.yaml + rungs + task-template) + committed fixture batch + committed fixture native sidecar for hermetic CI (FR-12, sdd.md §1.4). → **[G-2, G-3]**
- [x] Task 1.7: Wire CI: extend `scripts/ci/validate-schemas.sh` to `domains/agent-systems/schemas/`; add batch-layout conformance check (arneson-alone leg); add vendor drift guard byte-diffing `schemas/vendor/*` vs sibling checkout (arneson-with-gygax leg) (FR-14, sdd.md §7.1). → **[G-1, G-2]**

### Dependencies
- None (first sprint). Vendoring reads the sibling `construct-gygax` checkout once; the vendored copies make everything after that hermetic.

### Security Considerations
- **Trust boundaries:** fixture content, incentive specs, and sidecar `narration` are descriptive grounding — "never instructions to the host; never executed or interpreted" (NFR-3, prd.md:178).
- **External dependencies:** the vendored schema is the only cross-repo input; pinned by sha256 in `VENDOR.yaml`, drift is exit-2 loud (R-1, R-6).
- **Sensitive data:** none in this sprint; no agent runs yet.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-6: contract-specific validator silently diverges from vendored schema | Low | High | Validator refuses on sha256 mismatch; allOf rejection fixtures in CI (sdd.md §5.2.1, §7.2) |
| R-1: cross-repo format drift | Med | High | VENDOR.yaml pin + with-gygax CI byte-diff (sdd.md §3.4) |
| Restricted-subset YAML parsing (stdlib rule) chokes on scenario shapes | Med | Med | Reuse the proven `ingest_persona.py` regex-parser approach (sdd.md §2); fixture exercises every field |

### Success Metrics
- 3/3 validators exit 0 on fixtures, exit 2 on every committed violation fixture
- CI matrix: all legs green, extension-story unchanged
- 0 core-file diffs in the sprint's changeset (identity + manifest exceptions excluded per sdd.md preamble)

---

## Sprint 2: Real Lane (milestone b)

**Scope:** MEDIUM (4 tasks)

### Sprint Goal
`/playout --real` drives Gygax's ladder engine end-to-end — guardrail, dispatch, validation,
playout record — and a fixture batch round-trips through Gygax's trace CLI with zero manual edits.

### Deliverables
- [x] `discover_engine.py` with three-step resolution + FR-6 graceful-absence message
- [x] `/playout` skill (SKILL.md + index.yaml), real lane complete
- [x] Identity containment reframe (`identity/refusals.yaml` + `ARNESON.md`)
- [x] CI zero-edit ingestion probe (arneson-with-gygax leg)

### Acceptance Criteria
- [x] Engine discovery order: `--engine` flag → `ARNESON_GYGAX_ROOT` → sibling probe `../construct-gygax`; candidate valid iff `scripts/lib/ladder/index.ts` exists (sdd.md §1.6)
- [x] Absent engine fails immediately with the exact FR-6 message naming the dependency and pointing at simulated mode (sdd.md §6.1); no retries, no partial fallbacks
- [x] Guardrail states `this will spawn N real agent runs (rungs × trials = R × T) via: <agent_cmd>` before spawning; `--yes` skips; `--dry-run` never reaches the prompt (FR-3, sdd.md §4.3)
- [x] Engine invoked via subprocess argv array (never `shell=True`), `cwd` = discovered Gygax root, stdout `--json` parsed, exit 2 mapped to `ENGINE SETUP FAILURE:` with engine stderr attached (sdd.md §5.1)
- [x] Batch handed over byte-untouched; report's next-step line is the literal `--regrade` command (R-7, sdd.md §5.2.2)
- [x] Playout record written to `grimoires/arneson/playouts/<playout-id>.yaml` with scenario sha256, lane, engine git sha, batch path, counts, validation outcome (sdd.md §3.5)
- [x] `identity/refusals.yaml` drops never-executes, adopts locked-room containment, states both invariants: judge-never-produces-evidence + forecast-never-a-sidecar-claim (FR-11)
- [x] CI probe: assembled fixture batch → Gygax `trace/index.ts` → grade + diff complete, zero manual edits (milestone b, sdd.md §7.1)

### Technical Tasks
- [x] Task 2.1: Implement `discover_engine.py` (flag → env → sibling probe; engine root to stdout, or exit 1 with FR-6 message) + shell test covering all three resolution paths and the absence case (sdd.md §1.6, §5.3). → **[G-1, G-3]**
- [x] Task 2.2: Author `/playout` SKILL.md + index.yaml, real lane: scenario gate via `validate_scenario.py --lane real`; cost guardrail + `--yes` + `--dry-run` pass-through (FR-3); engine dispatch per sdd.md §5.1 (argv array, `--json`, cwd=engine root, timeout forwarding); post-run `validate_batch.py` conformance gate before the path is reported (FR-9); playout record write; success/loud-failure report per sdd.md §4.4. Confirm OQ-4 with operator in-sprint (recommendation: leave `producer.id: "claude-cli"` as engine truth). → **[G-1, G-4]**
- [x] Task 2.3: Identity reframe: rewrite the containment stanza in `identity/refusals.yaml` + `ARNESON.md` — locked-room isolation (isolated run dirs, time limits, full logging, labeled output), persona-host-never-executes bright line, both invariants stated explicitly (FR-11, prd.md:146-151). → **[G-4]**
- [x] Task 2.4: Add CI zero-edit ingestion probe to the arneson-with-gygax leg: fixture batch → `npx tsx scripts/lib/trace/index.ts <batch> --regrade` → assert grade + diff complete with zero manual edits (FR-14, sdd.md §7.1 check 6). → **[G-1]**

### Dependencies
- Sprint 1: validators, vendored contract, fixture batch (Tasks 1.2, 1.5, 1.6)
- External: a working sibling `construct-gygax` checkout with node + `npx tsx` resolvable (engine-owned dependency, NFR-5) — required for Task 2.4 and live dispatch testing

### Security Considerations
- **Trust boundaries:** real agents execute **engine-side only**, inside isolated run dirs with SIGKILL timeouts; Arneson dispatches and validates, never executes (FR-11, sdd.md §1.9).
- **External dependencies:** engine driven via subprocess argv arrays, never `shell=True`; `agent_cmd` passed verbatim as a template, never expanded by Arneson.
- **Sensitive data:** NFR-4 — Arneson never injects credential-bearing values into `agent_cmd` or run-dir environments; `batch.json` stores the command template, never the expanded environment (sdd.md §1.9).

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-3: real-run cost | Med | Med | Guardrail with explicit N + `--dry-run` + required stopping condition (FR-3, NFR-2) |
| R-4: Gygax absent | Med | Low | Three-step discovery, immediate named failure, simulated lane pointer (FR-6) |
| R-7: engine inline-grading misread as "Arneson graded it" | Low | Med | Canonical ingest is `--regrade` everywhere; batch byte-untouched (sdd.md §5.2.2) |
| Engine CLI/JSON shape changes upstream | Low | High | Contract verified 2026-06-09 (sdd.md §5.1); CI probe catches breakage on the with-gygax leg |

### Success Metrics
- 1 fixture batch graded + diffed by Gygax's trace CLI in CI with 0 manual edits (milestone b)
- 100% of error-catalog conditions (sdd.md §6.1) reachable in tests produce the specified exit code + message shape
- Guardrail-declined invocation exits 0 with nothing spawned

---

## Sprint 3: Loop Closure + Docs (milestone c — the G-1 gate)

**Scope:** MEDIUM (4 tasks)

### Sprint Goal
Close the real-lane loop for real — one live `/playout --real` against Gygax's
`evals/awareness-ladder`, graded via `--regrade`, diffed against forecast, zero manual edits —
and document it so a stranger can do the same from the quick-start alone.

### Deliverables
- [ ] Canonical demo run: live real-lane batch graded + diffed (G-1 evidence)
- [ ] `docs/quickstart.md` (stranger-grade), `docs/walls-of-the-room.md`, `docs/pairing-workflow.md`
- [ ] Banned-copy list + one-variable discipline in `domain.conventions.md`
- [ ] G-1 + G-3 acceptance evidence in playout record + NOTES.md

### Acceptance Criteria
- [ ] Acceptance per the contract's own definition: "a batch produced entirely outside Gygax … is graded and diffed with zero manual edits" (observed-trace-batch.v1.md:107-109, quoted sdd.md §7.3)
- [ ] G-1 gate: one real `/playout --real` against `evals/awareness-ladder`, `--regrade` ingest, diff produced, zero manual edits anywhere
- [ ] G-3 gate: a fresh operator executes `docs/quickstart.md` verbatim (install → scenario → `/playout --real` → grade/diff) and reaches the gap report
- [ ] `walls-of-the-room.md` states what isolation does AND does not stop (R-2, prd.md:203)
- [ ] `pairing-workflow.md` documents gap report → `/voice` workshop → next playout as the canonical combined workflow (G-5, FR-13)
- [ ] Banned-copy list enforced in docs: no "hard metrics", "zero hallucination", fidelity claims (G-4, prd.md:58); pretend-is-preview/real-is-proof framing throughout (R-5)

### Technical Tasks
- [ ] Task 3.1: Author the canonical demo scenario.yaml pinned to `construct-gygax/evals/awareness-ladder` and execute the live G-1 run: `/playout --real` → batch → `trace/index.ts <batch> --regrade` → gap report. Record counts, batch path, engine sha in the playout record. → **[G-1]**
- [ ] Task 3.2: Write `docs/quickstart.md` (stranger-grade: install both constructs → write scenario → run → confirm guardrail → grade → read diff; every command literal), `docs/walls-of-the-room.md` (engine-owned isolation: run dirs + timeouts; what is NOT stopped — operator's own `agent_cmd` contents are theirs), `docs/pairing-workflow.md` (Flow 3, sdd.md §4.1) (FR-13). → **[G-3, G-5]**
- [ ] Task 3.3: Finalize `domain.conventions.md`: banned-copy list (prd.md:58), one-variable-per-scenario-family discipline (rung varies inside; temperament/persona varies across — FR-7), claim_strength framing rules. → **[G-4]**
- [ ] Task 3.4: Record acceptance evidence: G-1 run artifacts referenced from the playout record; G-3 fresh-operator walkthrough performed against quickstart.md verbatim, gaps fixed, outcome logged to NOTES.md (sdd.md §7.3). → **[G-1, G-3]**

### Dependencies
- Sprint 2: working real lane (Tasks 2.1, 2.2), identity reframe shipped
- External: live Gygax checkout with `evals/awareness-ladder` + a real `agent_cmd` (spend approved by operator — FR-3 guardrail applies to the demo run too)

### Security Considerations
- **Trust boundaries:** the demo run executes a real agent — engine-side isolation only; quickstart instructs operators that `agent_cmd` contents are their responsibility (walls-of-the-room).
- **External dependencies:** none new; docs reference the pinned contract version.
- **Sensitive data:** demo scenario uses no credentials; NFR-4 posture restated in quickstart.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-5: overclaim poisons trust | Low | High | Banned-copy list lands in the same sprint as the docs it polices (Task 3.3) |
| Live run hits engine/fixture mismatch CI didn't catch | Med | Med | Run early in sprint; gap feeds back to Sprint 2 surfaces before docs freeze |
| Quickstart assumes context a stranger lacks | Med | Med | G-3 walkthrough is a gate, not a suggestion (Task 3.4) |

### Success Metrics
- G-1: 1 live run, 0 manual edits, diff produced (binary gate)
- G-3: 1 fresh-operator walkthrough completes from docs alone; every friction point fixed or filed
- 0 banned-copy phrases in `domains/agent-systems/docs/` + `domain.conventions.md` (grep check)

---

## Sprint 4 (Final): Simulated Lane (milestone d)

**Scope:** LARGE (7 tasks)

### Sprint Goal
Arneson hosts the agent persona itself — dual emission, deterministic projection, artifact
materialization, analyst-scored observation — producing the same batch shape with
`producer.kind: simulation`, standalone-safe without Gygax.

### Deliverables
- [ ] Persona host wiring: visibility mask, context manifest, provenance preamble, memory policy
- [ ] Bundled agent-under-incentive persona (rung overlays) + `docs/importing-an-agent.md`
- [ ] `project_trace.py`, `materialize_artifacts.py`, `assemble_batch.py` + shell tests
- [ ] Score-on-assemble via `ladder score --batch` when engine present; honest standalone labeling
- [ ] OQ-1 probe resolved (or escalated to the Gygax seam)
- [ ] CI: projection round-trip + hermetic playout jobs
- [ ] E2E validation of all 5 PRD goals

### Acceptance Criteria
- [ ] Simulated `/playout` works with zero Gygax install: playout, native sidecar, and projection all complete; report labels the batch `standalone simulated batch — ungraded; not Gygax-ingestible until scored` (FR-4, sdd.md §5.2.3)
- [ ] Dual emission: native sidecar (full fidelity) + deterministic projection to `observed-trace/v1` with playout prose as `narration`; **no LLM on the projection path** (FR-8)
- [ ] Preamble records provenance (model id, construct git sha, skill/schema versions, protocols loaded) + context manifest (`[{ref, sha256}]`) so the rung's visibility claim is verifiable (FR-10)
- [ ] `artifact_declare` contents materialized verbatim into `runs/rung-R/trial-T/`, seeded from the fixture's `task-template/` so `protected_baseline` files are diffable (sdd.md §5.2.3 item 2)
- [ ] When engine present: `observation` filled only by Gygax's `ladder score --batch`; `producer` preserved as `simulation`; Arneson logic never authors a classification (FR-9 trust rule)
- [ ] Host serializes, never executes: no agent-narrated content is run by Arneson-side tooling (FR-11 bright line, NFR-3)
- [ ] `/pause` + safety commands + stopping condition honored mid-playout (FR-4, NFR-2)
- [ ] Projection round-trip + hermetic playout CI jobs green on the arneson-alone leg (FR-14)

### Technical Tasks
- [ ] Task 4.1: Wire the persona host (existing core engine, parameterized): apply per-rung visibility mask, record context manifest + provenance preamble + memory_policy stamp, emit append-only native sidecar per `session-events-agent`, honor stopping/`/pause`/safety (FR-4, FR-10, sdd.md §1.4). → **[G-2]**
- [ ] Task 4.2: Author the bundled neutral agent-under-incentive persona with blind/reward-aware/adversarial rung overlays (FR-12) + `docs/importing-an-agent.md` documented procedure: source spec → schema fields → `source.ref` + `source.sha256` (FR-5, sdd.md §3.3). → **[G-2, G-3]**
- [ ] Task 4.3: Implement `project_trace.py` (native sidecar → one `observed-trace/v1` JSON per trial, deterministic, prose as `narration`) + shell test (FR-8, sdd.md §5.3). → **[G-2, G-4]**
- [ ] Task 4.4: Implement `materialize_artifacts.py` (seed run dirs from task-template, overlay `artifact_declare` contents verbatim, content_sha256 verified) + `assemble_batch.py` (batch.json + layout under `grimoires/arneson/playouts/<playout-id>/batch/`) + shell tests (sdd.md §5.3, §3.5). → **[G-2]**
- [ ] Task 4.5: Wire simulated lane into `/playout` SKILL.md: host → project → materialize → assemble → validate → score-on-assemble via `ladder score --batch` when engine discoverable; honest ungraded labeling standalone; playout record (FR-4, sdd.md §1.5, §5.2.3). → **[G-1, G-4]**
- [ ] Task 4.6: OQ-1 probe: run a materialized simulation batch through `ladder score --batch` + Gygax ingest end-to-end; verify `observation` filled with `producer` preserved (index.ts:204). If it fails: document, escalate to the Gygax seam, keep standalone labeling as the shipped behavior (sdd.md OQ-1). Add CI: projection round-trip + hermetic playout (FR-14, sdd.md §7.1 checks 2+4). → **[G-1, G-2]**
- [ ] Task 4.E2E: End-to-End Goal Validation (P0, all goals) — see below. → **[G-1, G-2, G-3, G-4, G-5]**

### Task 4.E2E: End-to-End Goal Validation

**Priority:** P0 (Must Complete)
**Goal Contribution:** All goals (G-1 … G-5)

| Goal ID | Goal | Validation Action | Expected Result |
|---------|------|-------------------|-----------------|
| G-1 | Real-lane loop closure | Re-verify Sprint 3 evidence: live `/playout --real` batch → `--regrade` → diff | Zero manual edits anywhere; playout record cites batch + diff |
| G-2 | Every layer observable | Walk the 7 layers (discovery/observability-layers.md) against a simulated playout's artifacts | Each layer has a capture AND a machine validator — "a capture without a validator is a claim" |
| G-3 | Stranger-operable | Fresh-operator quickstart walkthrough (Sprint 3) still passes with simulated-lane sections added | Loop reached from docs alone |
| G-4 | Honest labeling | Grep batches for producer + claim_strength on every record; grep docs for banned-copy list | 100% records labeled; 0 banned phrases |
| G-5 | The pairing compounds | `docs/pairing-workflow.md` exists and names the gap-report → `/voice` → next-playout loop with literal commands | Canonical combined workflow documented |

**Acceptance Criteria:**
- [ ] Each goal validated with documented evidence (playout records, CI runs, walkthrough log in NOTES.md)
- [ ] Integration points verified: real batch and simulated batch both pass `validate_batch.py` and both reach Gygax grading
- [ ] No goal marked "not achieved" without explicit justification

### Dependencies
- Sprint 1: schemas + validators + synthetic fixture (hard dependency for Tasks 4.1–4.4)
- Sprint 3: docs exist for E2E to extend; sequencing keeps the gate (G-1) ahead of the secondary milestone per the PRD's lane priority
- External (Task 4.6 only): Gygax checkout for the OQ-1 probe; everything else is hermetic

### Security Considerations
- **Trust boundaries:** persona specs and narrated content are untrusted descriptive grounding; `materialize_artifacts.py` serializes bytes to files, never executes or interprets them (NFR-3, FR-11 bright line).
- **External dependencies:** `ladder score` is the analyst's code, invoked the same subprocess-argv way as the engine; absent engine degrades to labeled-ungraded, never to Arneson-authored grades.
- **Sensitive data:** none enters run rooms; context manifest records refs + hashes, not secrets (NFR-4).

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OQ-1: `ladder score` doesn't fill observation on simulation batches | Med | Med | Probe early (Task 4.6); fallback = honest standalone labeling ships regardless; escalate seam ask to Gygax |
| Projection drops fidelity the native sidecar had | Med | Med | Round-trip CI vs vendored contract; native sidecar remains the full-fidelity record (FR-8) |
| Hosted persona drifts into executing instead of narrating | Low | High | Bright line in identity (FR-11) + serialize-only tooling + NFR-3 framing in persona preamble |

### Success Metrics
- Hermetic CI playout: fixture native sidecar → project → materialize → assemble → validate, exit 0, no network, no Gygax
- 1 simulation batch scored by `ladder score` with `producer.kind: simulation` preserved (or OQ-1 escalation filed)
- Task 4.E2E table: 5/5 goals validated with evidence

---

## Risk Register

| ID | Risk | Sprint | Probability | Impact | Mitigation | Source |
|----|------|--------|-------------|--------|------------|--------|
| R-1 | Cross-repo format drift | 1, all | Med | High | Vendored contract + VENDOR.yaml pin + validator self-check + CI sibling diff | prd.md:202, sdd.md §3.4 |
| R-2 | Locked room has limits | 2–3 | Med | Med | Engine-side execution only; no secrets injected; walls-of-the-room doc | prd.md:203, sdd.md §1.9 |
| R-3 | Real-run cost | 2–3 | Med | Med | Guardrail prompt with explicit N, `--yes`, `--dry-run`, required stopping condition | prd.md:204 |
| R-4 | Gygax absent | 2, 4 | Med | Low | Three-step discovery, named-dependency failure, simulated lane standalone | prd.md:205 |
| R-5 | Overclaim poisons trust | 3 | Low | High | producer↔claim binding validated pre-handoff; banned-copy list; preview/proof framing | prd.md:206 |
| R-6 | Validator diverges from vendored schema | 1 | Low | High | sha256 refusal (exit 2); allOf rejection fixtures | sdd.md §9 |
| R-7 | Engine inline-grading misread as Arneson's | 2 | Low | Med | `--regrade` canonical everywhere; batch byte-untouched | sdd.md §9 |

---

## Success Metrics Summary

| Metric | Target | Measurement Method | Sprint |
|--------|--------|-------------------|--------|
| Conformance | Validators reject every committed violation fixture | shell tests + CI | 1 |
| Zero-edit ingestion | Fixture batch graded+diffed by trace CLI, 0 edits | CI probe (with-gygax) | 2 |
| G-1 loop closure | 1 live real run → `--regrade` → diff, 0 edits | playout record evidence | 3 |
| Stranger-operability | Quickstart walkthrough completes from docs alone | fresh-operator gate | 3, 4 |
| Hermetic simulated lane | Full pipeline exit 0 with no Gygax install | CI (arneson-alone) | 4 |
| Goal coverage | 5/5 PRD goals validated | Task 4.E2E table | 4 |

---

## Dependencies Map

```
Sprint 1 ────────────▶ Sprint 2 ────────────▶ Sprint 3 ────────────▶ Sprint 4
(conformance           (real lane:             (G-1 gate:             (simulated lane:
 substrate:             dispatch, guardrail,    live run, docs,        host, projection,
 vendor, schemas,       identity reframe,       acceptance             scoring, E2E
 validators, fixture)   zero-edit CI probe)     evidence)              validation)
        │                      │                      │
        └── hermetic           └── needs Gygax        └── needs Gygax + real agent_cmd
```

Sprint 4's hard dependency is Sprint 1 (Tasks 4.1–4.5 are hermetic); it sequences after
Sprint 3 because the PRD makes the real lane the gate and the simulated lane "a secondary
milestone" (prd.md:26-27).

---

## Appendix

### A. PRD Feature Mapping

| PRD Feature | Sprint | Task(s) |
|-------------|--------|---------|
| FR-1: agent-systems vertical, zero core changes | 1 | 1.1, 1.7 (extension-story proof) |
| FR-2: `/playout --real` | 2 | 2.2 |
| FR-3: cost guardrail | 2 | 2.2 |
| FR-4: simulated mode | 4 | 4.1, 4.5 |
| FR-5: agent import | 4 | 4.2 |
| FR-6: graceful absence | 2 | 2.1 |
| FR-7: scenario.yaml first-class | 1 | 1.3, 1.4 |
| FR-8: dual emission | 4 | 4.3, 4.4 |
| FR-9: self-validation + trust rule | 1, 4 | 1.2, 1.5, 4.5 |
| FR-10: provenance + context manifest | 1, 4 | 1.3, 4.1 |
| FR-11: containment reframe | 2 | 2.3 |
| FR-12: bundled resources | 1, 4 | 1.6, 4.2 |
| FR-13: documentation set | 3 | 3.2, 3.3 |
| FR-14: CI lands in same change | 1, 2, 4 | 1.7, 2.4, 4.6 |

### B. SDD Component Mapping

| SDD Component | Sprint | Status |
|---------------|--------|--------|
| Vendored contract + drift guard (§3.4) | 1 | Planned |
| Domain schemas (§3.1–3.3) | 1 | Planned |
| Deterministic validators (§5.2.1, §5.3) | 1 | Planned |
| Engine discovery (§1.6) | 2 | Planned |
| `/playout` real lane (§4.2, §5.1) | 2 | Planned |
| Identity reframe (§1.9) | 2 | Planned |
| Docs set (§4.1 flows) | 3 | Planned |
| Persona host wiring (§1.4) | 4 | Planned |
| Projection/materialize/assemble pipeline (§1.5, §5.2.3) | 4 | Planned |
| CI matrix extensions (§7.1) | 1, 2, 4 | Planned |

### C. PRD Goal Mapping

| Goal ID | Goal Description | Contributing Tasks | Validation Task |
|---------|------------------|-------------------|-----------------|
| G-1 | Real-lane loop closure (the gate) | 1.1, 1.2, 1.5, 1.7, 2.1, 2.2, 2.4, 3.1, 3.4, 4.5, 4.6 | Sprint 4: Task 4.E2E (gate evidence from 3.1/3.4) |
| G-2 | Every layer observable | 1.3, 1.4, 1.6, 1.7, 4.1, 4.2, 4.3, 4.4, 4.6 | Sprint 4: Task 4.E2E (7-layer walk) |
| G-3 | Stranger-operable | 1.6, 2.1, 3.2, 3.4, 4.2 | Sprint 4: Task 4.E2E (quickstart walkthrough) |
| G-4 | Honest labeling | 1.2, 1.5, 2.2, 2.3, 3.3, 4.3, 4.5 | Sprint 4: Task 4.E2E (label + banned-copy grep) |
| G-5 | The pairing compounds | 3.2 (pairing-workflow.md) | Sprint 4: Task 4.E2E (workflow doc check) |

**Goal Coverage Check:**
- [x] All PRD goals have at least one contributing task
- [x] All goals have a validation task in the final sprint (Task 4.E2E)
- [x] No orphan tasks (every task annotated with at least one goal)

**Per-Sprint Goal Contribution:**

- Sprint 1: G-1 (foundation: contract + validators), G-2 (schemas + fixture), G-4 (vendored pin + laundering rejection)
- Sprint 2: G-1 (zero-edit ingestion), G-3 (discovery UX), G-4 (identity + `--regrade` framing)
- Sprint 3: G-1 (gate closed), G-3 (gate closed), G-4 (banned-copy), G-5 (pairing doc)
- Sprint 4: G-2 (complete), G-1/G-3/G-4 (extended to simulated lane), E2E validation of all goals

---

## Assumptions (explicit, per uncertainty protocol)

1. **[ASSUMPTION]** The sibling `construct-gygax` checkout at `../construct-gygax` stays at (or compatible with) the contract state verified 2026-06-09 (prd.md Dependencies, all five verified present). If Gygax moves the CLI or schema, R-1 machinery catches it but Sprints 2–3 stall until re-vendored.
2. **[ASSUMPTION]** The Sprint 3 demo run's real-agent spend is operator-approved at run time via the FR-3 guardrail; no separate budget sign-off process exists.
3. **[ASSUMPTION]** Sprint ordering 3→4 (gate before secondary milestone) is intended even though Sprint 4's hard dependencies are met after Sprint 1 — per "Real mode is the primary lane" (prd.md:22-23). If the operator wants the cheap simulated lane earlier (e.g., no real agent available yet), Sprint 4 can be pulled ahead of Sprint 3 without rework.

---

*Generated by Sprint Planner Agent, 2026-06-09. Supersedes Sprint Plan v3.4 (complete).*
