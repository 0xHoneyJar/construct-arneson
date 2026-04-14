# Sprint Plan: construct-arneson v1

**Version:** 1.0
**Date:** 2026-04-13
**Author:** Sprint Planner Agent (/sprint-plan)
**PRD Reference:** `grimoires/loa/prd.md`
**SDD Reference:** `grimoires/loa/sdd.md`

---

## Executive Summary

Seven sprints deliver construct-arneson v1 — eight skills with structured-sidecar admissibility, axis-split intent handling, standalone-plus-composable operation, and Gygax-community tradition coverage. Each sprint maps to a PRD milestone (M0–M7; M6 and M7 merge into one hardening+launch sprint).

Build ordering follows the PRD's **vertical-slice-first** directive (prd.md:694): ship `/braunstein` end-to-end in Sprint 2, prove admissibility in Sprint 3, then extract primitives from the vertical slice in Sprints 4–6, then harden and launch in Sprint 7.

**Total Sprints:** 7
**Cadence:** Quality-driven, no fixed dates (PRD §3 constraint). Progression gated on milestone acceptance criteria, not calendar.
**Minimum Viable Construct:** After Sprint 3 (M2), `/braunstein` + `/distill` demonstrates admissibility end-to-end. Sprint 7 (M7) ships v1.

---

## Sprint Overview

| Sprint | Theme (Milestone) | Key Deliverables | Size | Dependencies |
|--------|------------------|------------------|------|--------------|
| 1 | Foundation (M0) | construct.yaml, identity layer, 7 schemas, fallback archetypes, synthetic fixture, grimoire scaffold, CI scaffold | Large (10 tasks) | None |
| 2 | Vertical Slice (M1) | `/braunstein` end-to-end with safety, sidecar, intent, memory, dice | Large (10 tasks) | Sprint 1 |
| 3 | Admissibility (M2) | `/distill`, digest schema finalization, round-trip admissibility test | Medium (5 tasks) | Sprint 2 |
| 4 | Primitives (M3) | Refactor `/narrate` out, add `/voice` and `/scene` | Medium (6 tasks) | Sprint 2 (for code to extract) |
| 5 | GM-Side (M4) | `/improvise`, voice-pc schema, rule_of_cool + clarifying_question events | Small (3 tasks) | Sprint 4 (primitives available) |
| 6 | World-Building (M5) | `/fragment`, `/arneson` status, tradition fallback integration | Small (3 tasks) | Sprint 4 (scene primitive) |
| 7 | Hardening + Launch (M6+M7) | CI matrix, identity audit, blind-attribution, E2E goal validation, release | Medium (6 tasks) | All prior sprints |

---

## Sprint 1: Foundation (M0)

### Sprint Goal
Lay the structural bedrock so that Sprint 2 can implement `/braunstein` without touching shape decisions. At the end of this sprint, the construct loads in Loa, all schemas validate, and the synthetic fixture is ready for use as an acceptance testbed.

### Deliverables
- [x] `construct.yaml` declaring slug `arneson`, schema_version 3, type `skill-pack`, domain `design`, 8 skills, composition paths to Gygax
- [x] `identity/` directory populated: `ARNESON.md`, `persona.yaml`, `expertise.yaml`, `refusals.yaml`
- [x] All 7 schemas written and validated (experiential_intent, voice-base + 3 extensions, session-events, digest)
- [x] Fallback archetype bundle at `resources/archetypes-fallback/` (9 YAMLs mirroring Gygax's cabal)
- [x] Synthetic reference fixture at `examples/synthetic-fixture/` (HEKATE-free, single directory)
- [x] `grimoires/arneson/` directory scaffold with `.gitkeep` files
- [x] CI scaffold (`.github/workflows/ci.yaml`) with both matrix modes; smoke tests may be placeholders

### Acceptance Criteria
- [x] `construct.yaml` validates against Loa's construct schema
- [x] All 7 Arneson schemas validate as valid YAML structure documents
- [x] Synthetic fixture's `game-state.yaml` validates against its declared schemas
- [x] Synthetic fixture contains entries exercising: both intent axes, ≥3 archetypes (including Chaos Agent), dice modes, safety triggers, tradition fallback
- [x] HEKATE audit passes: `grep -ri 'mibera\|hekate' .` returns zero hits
- [x] CI runs green in both modes against the smoke tests (local verification; GitHub Actions unverified until first push — see review feedback Concern #4)
- [-] `/arneson` skill dashboard can list zero sessions cleanly — DEFERRED to Sprint 6 per sprint.md conditional ("if needed to keep smoke tests green"). Smoke tests are green without it.

### Technical Tasks

- [x] Task 1.1: Author `construct.yaml` per SDD Appendix 11.A → **[G-4]**
- [x] Task 1.2: Author `identity/ARNESON.md` (prose identity, distinct from Gygax) → **[G-2]**
- [x] Task 1.3: Author `identity/persona.yaml`, `expertise.yaml`, `refusals.yaml` → **[G-2]**
- [x] Task 1.4: Write `schemas/experiential_intent.schema.yaml` per SDD 3.2.1 → **[G-3]**
- [x] Task 1.5: Write voice schemas: `voice-base` + `voice-archetype` + `voice-npc` + `voice-pc` per SDD 3.2.2–3.2.5 → **[G-6]**
- [x] Task 1.6: Write `schemas/session-events.schema.yaml` per SDD 3.2.6 — the admissibility-infrastructure schema → **[G-1]**
- [x] Task 1.7: Write `schemas/digest.schema.yaml` per SDD 3.2.7 → **[G-1, G-5]**
- [x] Task 1.8: Author 9 archetype fallback YAMLs at `resources/archetypes-fallback/` (newcomer, optimizer, chaos-agent, etc.) → **[G-4]**
- [x] Task 1.9: Author synthetic reference fixture at `examples/synthetic-fixture/` (game-state + tradition lore + scene seeds; HEKATE-free) → **[G-1, G-3, G-4, G-5, G-6]**
- [x] Task 1.10: Create `grimoires/arneson/` directory scaffold + CI scaffold with both matrix modes (arneson-alone, arneson-with-gygax) + HEKATE audit script + schema-validation test → **[G-4, G-5]**

### Review Status
- **Reviewed**: 2026-04-13 via `/review-sprint sprint-1`
- **Verdict**: **All good (with noted concerns)** — see `grimoires/loa/a2a/sprint-1/engineer-feedback.md`
- **7 concerns documented** for Sprint 2 intake; none blocking

### Dependencies
- None (first sprint)

### Security Considerations
- **Trust boundaries**: User-authored YAML (game-state, voice files) is trusted; schema validation is the guard. No network or credentialed inputs in this sprint.
- **External dependencies**: yq v4+ (already required by Loa). No new dependencies added.
- **Sensitive data**: None. Construct stores game-design data only; no PII. Synthetic fixture is public-shippable.
- **HEKATE isolation**: CI step greps for `MIBERA` and `HEKATE` strings across the entire construct; fails if found.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Fallback archetype bundle drifts from Gygax SSOT | Med | Med | Task 1.8 pins archetype definitions to Gygax v3.0.0 at sprint start; fallback-sync check deferred to Sprint 7 |
| Synthetic fixture too thin to exercise all skills | Med | Med | Task 1.9 requires fixture to exercise all 6 skill-touched data shapes; grow in Sprint 2 if gaps surface |
| Schema design decisions leak into Sprint 2 | Low | High | This sprint is explicitly about finalizing shapes; Sprint 2 refactoring requires re-opening Sprint 1 acceptance |

### Success Metrics
- All 7 schemas pass structural validation
- Synthetic fixture validates against its declared schemas
- CI green in both modes; HEKATE audit zero hits
- Smoke test for construct-load completes

---

## Sprint 2: Vertical Slice — `/braunstein` (M1)

### Sprint Goal
Implement `/braunstein` end-to-end. At sprint close, a designer can run `/braunstein --newcomer` against the synthetic fixture, play a session with safety agreement + intent-aware voicing + dice choice + sidecar event emission, and end with session state persisted. This sprint carries 8 functional requirements.

### Deliverables
- [ ] `skills/braunstein/SKILL.md` and `skills/braunstein/index.yaml`
- [ ] Safety agreement prompt machinery at session open (FR-15)
- [ ] Composition-detection protocol (SDD 5.2)
- [ ] Archetype loading: prefers Gygax SSOT when present, falls back otherwise (FR-17)
- [ ] Intent reading (both axes) with graceful degradation (FR-9)
- [ ] Dice resolution modes: user / arneson / hybrid (FR-11)
- [ ] Sidecar event emission — append-only during session (FR-16)
- [ ] Archetype memory 3-session sliding window (FR-10)
- [ ] Chaos Agent per-turn cap, empirically determined (FR-14)

### Acceptance Criteria
- [ ] `/braunstein --newcomer` runs full session against synthetic fixture in both CI modes
- [ ] Session writes `{date}-braunstein-newcomer.md` + `{date}-braunstein-newcomer.events.yaml`
- [ ] Sidecar validates against `session-events.schema.yaml`
- [ ] Every `archetype_decision` event includes `game_state_refs` (grounding check — R-2 mitigation)
- [ ] Every `archetype_decision` event includes `classification` of `fictional_friction` | `mechanical_bottleneck` (or both)
- [ ] Safety agreement displays at session open; declining aborts; `/pause` and `/x-card` halt generation
- [ ] Dice mode flag (`--dice=user|arneson|hybrid`) works; default is `user`
- [ ] Archetype memory state file at `grimoires/arneson/voices/archetypes/newcomer.state.yaml` updates across session boundary; 3-session sliding window enforced
- [ ] Standalone-mode banner displays when Gygax is absent
- [ ] Identity-refusal pattern check: no structural-analysis vocabulary in output
- [ ] Session interrupt (SIGINT) leaves readable partial transcript + sidecar (6.2)
- [ ] Chaos Agent per-turn sidecar event count stays under empirically-set cap

### Technical Tasks

- [ ] Task 2.1: Scaffold `skills/braunstein/SKILL.md` with Loa prompt-engineering conventions (persona, expertise, workflow sections) → **[G-1, G-2]**
- [ ] Task 2.2: Implement safety agreement at session open — present Lines & Veils + X-card; session state machine entry (SDD 4.2) → **[G-2]**
- [ ] Task 2.3: Implement composition-detection protocol per SDD 5.2 (filesystem probes for Gygax) → **[G-4, G-5]**
- [ ] Task 2.4: Implement archetype loading with Gygax-or-fallback resolution (FR-17) → **[G-4]**
- [ ] Task 2.5: Implement intent reading per SDD 5.3 — both axes, with single-axis degradation path → **[G-3]**
- [ ] Task 2.6: Implement dice mode selection and resolution protocol (FR-11) → **[G-1]**
- [ ] Task 2.7: Implement sidecar event emission — append-only writes for all 9 event types per `session-events.schema.yaml` → **[G-1]**
- [ ] Task 2.8: Implement archetype memory 3-session sliding window: read state file, apply memory to voicing, persist updated state on exit → **[G-6]**
- [ ] Task 2.9: Empirically determine Chaos Agent per-turn sidecar event cap during test sessions; record in `voice-archetype.schema.yaml::chaos_axis_config.per_turn_sidecar_event_cap` default → **[G-6]**
- [ ] Task 2.10: Crash-recovery test — SIGINT mid-session leaves valid partial transcript and sidecar readable by future `/distill` (R-12 mitigation) → **[G-1]**

### Dependencies
- Sprint 1: all schemas, fallback bundle, synthetic fixture, identity files

### Security Considerations
- **Trust boundaries**: user turn-input is untrusted free text; Arneson must not execute user input as commands. All user input is treated as session content.
- **Safety triggers**: X-card must halt generation immediately; no delayed processing. Halts are logged; never silenced.
- **Sidecar integrity**: append-only writes; no sidecar mutation after a turn is complete.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Sprint overload (8 FRs are co-dependent) | Med | High | FRs fire together in a session; splitting creates untestable intermediates. Accept sprint is high-risk; designate this the pressure-test sprint. |
| Narration logic gets entangled, hard to extract in Sprint 4 | Med | Med | Task 2.1 requires modular narration-function boundaries with `/narrate` signature pre-declared in comments; Sprint 4 extracts this shape |
| Chaos Agent cap too tight / too loose | Med | Med | Task 2.9 runs test sessions with Chaos Agent; cap value is data-driven, revisit in Sprint 7 hardening |
| Hollow fiction — sidecar valid but decisions ungrounded | Med | High | Task 2.7 enforces required `game_state_refs` at emit time; grounding violations fail sprint acceptance |

### Success Metrics
- Full session transcript + sidecar produced against synthetic fixture (both CI modes)
- Sidecar schema-valid; all archetype_decision events grounded
- Identity-refusal check passes on session output

---

## Sprint 3: Admissibility — `/distill` (M2)

### Sprint Goal
Make admissibility mechanically verifiable. `/distill` reads `/braunstein` outputs and emits a Gygax-ingestible digest. The round-trip test (`/braunstein` → `/distill` → Gygax `/cabal --from-session`) becomes the binary pass/fail for PRD goal G-1.

### Deliverables
- [ ] `skills/distill/SKILL.md` and `skills/distill/index.yaml`
- [ ] Digest schema finalized (may require revision after implementation)
- [ ] Round-trip admissibility test automated in CI
- [ ] Gygax schema PR filed (external coordination; tracked as dependency)

### Acceptance Criteria
- [ ] `/distill {session}` produces a valid digest in `grimoires/arneson/digests/`
- [ ] Digest includes: rule_invocations, rule_of_cool_overrides, clarifying_questions, signal_flags, intent_conflicts, dead_design_space, experiential_intent_observations, archetype_memory_updates
- [ ] Digest is self-describing (readable without Gygax installed — standalone mode)
- [ ] Round-trip test: `arneson-with-gygax` CI mode runs `/braunstein` → `/distill` → Gygax `/cabal --from-session` end-to-end without manual reformatting
- [ ] Partial-session digest flag set correctly when `/distill` is invoked on a crashed/incomplete session
- [ ] `digest_preamble.gygax_ingestible` flag is accurate (true when schema matches current Gygax contract)

### Technical Tasks

- [ ] Task 3.1: Scaffold `skills/distill/SKILL.md` with batch (non-interactive) workflow → **[G-1]**
- [ ] Task 3.2: Implement session ingestion — read `{session}.md` prose + `{session}.events.yaml` sidecar; handle partial-session cases → **[G-1]**
- [ ] Task 3.3: Implement digest extraction — map all 9 sidecar event types into digest's 8 findings categories per `digest.schema.yaml` → **[G-1, G-5]**
- [ ] Task 3.4: File Gygax schema PR (or issue) coordinating the `/cabal --from-session` contract; document compatibility note in digest preamble → **[G-5]**
- [ ] Task 3.5: Integrate round-trip test into `arneson-with-gygax` CI; fail build on mismatch → **[G-1, G-5]**

### Dependencies
- Sprint 2: `/braunstein` emits valid sessions and sidecars
- Gygax v3 installed in `arneson-with-gygax` CI mode

### Security Considerations
- **Trust boundaries**: session files are Arneson-authored (trusted). No external inputs processed.
- **Output**: digest is YAML, consumed by Gygax which runs in the user's local Loa. No network transmission.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gygax schema PR merge-timing blocks round-trip test | Med | Med | FR-9 degradation path allows unilateral Arneson ship; Sprint 3 passes with `gygax_ingestible: false` + documented compatibility note if Gygax not ready |
| Digest schema needs revision after implementation reveals gaps | Med | Low | Sprint 3 is explicitly the schema-refinement sprint; revisions expected |

### Success Metrics
- Round-trip test green in `arneson-with-gygax` mode (or documented degradation if Gygax PR pending)
- Digest readable and self-describing in `arneson-alone` mode

---

## Sprint 4: Primitives Extracted — `/narrate`, `/voice`, `/scene` (M3)

### Sprint Goal
Extract `/narrate` as the foundational fiction-mechanics-fiction primitive from `/braunstein`'s code. Build `/voice` (NPC workshop) and `/scene` (one-shot scene generator) on top of it. After Sprint 4, three user-facing one-shot-or-workshop skills exist, and `/braunstein` uses `/narrate` internally without regression.

### Deliverables
- [ ] `skills/narrate/SKILL.md` and `skills/narrate/index.yaml`
- [ ] `skills/voice/SKILL.md` and `skills/voice/index.yaml`
- [ ] `skills/scene/SKILL.md` and `skills/scene/index.yaml`
- [ ] `/braunstein` refactored to call `/narrate` internally
- [ ] Voice-NPC state persistence working

### Acceptance Criteria
- [ ] `/narrate {mechanic-outcome} {game-state-ref}` produces grounded narration (intent-aware, no fudging)
- [ ] `/voice {npc-id}` opens workshop session, holds character, exits with state diff
- [ ] `/scene {seed}` produces a scene grounded in game-state; flags "improvised against structural-only context" when no tradition file
- [ ] Refactored `/braunstein` still passes Sprint 2 acceptance (regression)
- [ ] NPC state persists correctly: `grimoires/arneson/voices/npcs/{id}.yaml` updates atomically on `/voice` session exit
- [ ] Intent-flip A/B test: same mechanic outcome, different `experiential_intent` → `/narrate` produces materially different prose

### Technical Tasks

- [ ] Task 4.1: Extract narration logic from `/braunstein` into `skills/narrate/SKILL.md` as a library primitive; preserve modular function boundaries → **[G-3]**
- [ ] Task 4.2: Refactor `/braunstein` to invoke `/narrate` internally; regression-test Sprint 2 acceptance → **[G-1, G-3]**
- [ ] Task 4.3: Implement `/voice` session skill with voice-npc schema integration (FR-2, FR-13) → **[G-6]**
- [ ] Task 4.4: Implement atomic state persistence for `/voice` (write-to-temp + rename) → **[G-6]**
- [ ] Task 4.5: Implement `/scene` one-shot skill with tradition fallback-aware flagging (FR-3) → **[G-3]**
- [ ] Task 4.6: Automate intent-flip A/B test — same game-state, flip `experiential_intent`, diff narrations → **[G-3]**

### Dependencies
- Sprint 2: `/braunstein` implementation provides the extraction source
- Sprint 1: voice-npc schema, voice-base schema

### Security Considerations
- **Trust boundaries**: same as Sprint 2 — user turn-input untrusted free text.
- **Atomic writes**: voice state files use temp + rename to prevent partial-write corruption on crash.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `/narrate` extraction reveals hidden `/braunstein` coupling | Med | Med | Task 4.2 regression-tests Sprint 2 acceptance; coupling fixes loop back into `/braunstein` |
| `/voice` persona memory leaks into subsequent `/braunstein` (R-9) | Med | Med | Session boundaries are explicit state-machine transitions; cross-voice isolation test added in Sprint 7 |

### Success Metrics
- All three new skills operational
- `/braunstein` regression suite green
- Intent-flip A/B produces detectable differences

---

## Sprint 5: GM-Side — `/improvise` (M4)

### Sprint Goal
Implement `/improvise` as the inverse of `/braunstein`. Shares infrastructure (session machinery, sidecar emission, safety). Adds GM-side-only event types: `rule_of_cool` and `clarifying_question`.

### Deliverables
- [ ] `skills/improvise/SKILL.md` and `skills/improvise/index.yaml`
- [ ] Voice-PC schema integration
- [ ] `rule_of_cool` and `clarifying_question` event types emitted during sessions

### Acceptance Criteria
- [ ] `/improvise --pc {pc-id}` runs a full GM-side session against synthetic fixture
- [ ] Session produces transcript + sidecar with preamble `mode: improvise`
- [ ] Arneson-as-GM rule-of-cool overrides logged as `rule_of_cool` events (not hidden)
- [ ] User clarifying questions logged as `clarifying_question` events
- [ ] `/distill` ingests `/improvise` sessions cleanly (no special-casing beyond mode flag)
- [ ] Voice-pc state file persists correctly for returning PCs

### Technical Tasks

- [ ] Task 5.1: Implement `/improvise` skill with shared session infrastructure from `/braunstein`; preamble mode flag distinguishes directory-unified sessions → **[G-1, G-2]**
- [ ] Task 5.2: Integrate voice-pc schema with `player_consent_metadata` honored at session open (lines/veils/x-card) → **[G-2]**
- [ ] Task 5.3: Implement `rule_of_cool` and `clarifying_question` event emission; verify `/distill` consumes them → **[G-1, G-5]**

### Dependencies
- Sprint 4: `/narrate` primitive available
- Sprint 2: session machinery extracted for reuse
- Sprint 3: `/distill` consumes new event types

### Security Considerations
- **Trust boundaries**: designer-as-PC input is user content; Arneson-as-GM output must honor `lines`/`veils`/`x-card` from pc voice file.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shared code between /braunstein and /improvise diverges | Med | Low | Task 5.1 uses the same session-infrastructure module; diverging would require an explicit refactor ticket |

### Success Metrics
- `/improvise` runs full session; distill consumes it
- Mode-unified directory structure works (both transcript types readable by `/arneson` status in Sprint 6)

---

## Sprint 6: World-Building — `/fragment`, `/arneson` (M5)

### Sprint Goal
Complete the 8-skill surface area. Add setting-material generation (`/fragment`) and status-dashboard (`/arneson`). Fully integrate tradition fallback (FR-12) across skills that need it.

### Deliverables
- [ ] `skills/fragment/SKILL.md` and `skills/fragment/index.yaml`
- [ ] `skills/arneson/SKILL.md` and `skills/arneson/index.yaml`
- [ ] Tradition fallback (FR-12) consistently applied across `/scene`, `/fragment`, `/narrate`, `/voice`, `/braunstein`, `/improvise`

### Acceptance Criteria
- [ ] `/fragment location|faction|history|item|...` produces grounded fragments
- [ ] `/arneson` status reports: Gygax composition state, sessions, voices, scenes, fragments, archetype memory windows, safety-findings count
- [ ] `/arneson` is read-only; writes nothing
- [ ] Tradition-absent invocations display the FR-12 banner consistently across all skills
- [ ] Improvised-tradition notes saved to `fragments/improvised-tradition-*.md` when user confirms improvisation

### Technical Tasks

- [ ] Task 6.1: Implement `/fragment` one-shot skill (FR-7) → **[G-3]**
- [ ] Task 6.2: Implement `/arneson` status-only read skill (FR-6) → **[G-2, G-4]**
- [ ] Task 6.3: Sweep all skills for consistent FR-12 tradition-fallback integration; add shared helper if duplication exceeds 2 skills → **[G-3, G-4]**

### Dependencies
- Sprint 4: `/scene` pattern for one-shot with tradition awareness
- All prior sprints: `/arneson` reads grimoire artifacts produced by them

### Security Considerations
- **/arneson read-only**: no write paths allowed; enforced by skill prompt + acceptance test.
- **Fragment injection**: `/fragment` never auto-injects into game-state; user must act explicitly.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Tradition-fallback integration duplicates across skills | Med | Low | Task 6.3 extracts shared helper if needed; otherwise accept mild duplication for v1 |

### Success Metrics
- All 8 skills operational
- `/arneson` reports accurate state against fixtures
- Tradition-fallback behavior consistent across skills

---

## Sprint 7 (Final): Hardening + Launch (M6 + M7)

### Sprint Goal
Harden the construct and ship v1. Stabilize CI matrix, lock identity-refusal audit, validate all 6 goals end-to-end, write README + demo artifacts, tag v1 release.

### Deliverables
- [ ] CI matrix stable (both modes green on main)
- [ ] Identity-refusal audit integrated into `/audit-sprint` workflow
- [ ] Blind-attribution protocol documented; self-test data recorded
- [ ] Intent-flip A/B test green
- [ ] E2E goal validation against all 6 goals
- [ ] README.md, demo transcript, demo digest
- [ ] v1.0.0 release tag + CHANGELOG entry
- [ ] Gygax schema PR merged (closes A-1) — *may trail release if Gygax timeline differs*

### Acceptance Criteria
- [ ] Both CI modes green on main for ≥3 consecutive commits
- [ ] Identity-refusal audit finds zero violations in acceptance outputs
- [ ] Blind-attribution self-test (designer rates transcript excerpts): ≥ chance accuracy on ≥3 archetypes
- [ ] Intent-flip A/B automated; two A/B pairs per tone variation pass
- [ ] Zero MIBERA/HEKATE hits across full construct tree
- [ ] Demo transcript + digest published in `examples/` or README
- [ ] Release tagged; CHANGELOG describes changes from "initial release"

### Task 7.E2E: End-to-End Goal Validation

**Priority:** P0 (Must Complete)
**Goal Contribution:** All goals (G-1 through G-6)

**Description:**
Validate that all PRD goals are achieved through the complete implementation. Each goal receives explicit pass/fail with documented evidence.

**Validation Steps:**

| Goal ID | Goal | Validation Action | Expected Result |
|---------|------|-------------------|-----------------|
| G-1 | Admissibility (round-trip) | Run `/braunstein` on synthetic fixture → `/distill` → Gygax `/cabal --from-session` (arneson-with-gygax CI mode) | Round-trip completes without manual reformatting |
| G-2 | Identity contract (refusals) | Grep session outputs for structural-analysis vocabulary from `identity/refusals.yaml` | Zero matches |
| G-3 | Intent fidelity (voicing shift) | Intent-flip A/B — same game-state, flip `experiential_intent`, diff narrations | Materially different voicing detectable |
| G-4 | Standalone viability | Run all 8 skills in `arneson-alone` CI mode | All skills complete primary task without Gygax paths |
| G-5 | Composition amplification | Bidirectional test: scry-fork (Gygax) → braunstein (Arneson) → distill → cabal (Gygax) | End-to-end round-trip green |
| G-6 | Archetype distinctness | Designer blind-attribution on ≥3 archetypes, N excerpts each | Accuracy above chance |

**Acceptance Criteria:**
- [ ] Each goal validated with documented evidence (linked from this row to the actual test output)
- [ ] Integration points verified (data flows end-to-end through both CI modes)
- [ ] No goal marked as "not achieved" without explicit justification in this table

### Technical Tasks

- [ ] Task 7.1: Stabilize CI matrix — fix flakes; both modes must run green on ≥3 consecutive main commits → **[G-4, G-5]**
- [ ] Task 7.2: Integrate identity-refusal audit into `/audit-sprint` workflow; audit runs against all acceptance-test outputs → **[G-2]**
- [ ] Task 7.3: Author + run blind-attribution self-test protocol; record results in `grimoires/arneson/launch-evidence/blind-attribution.md` → **[G-6]**
- [ ] Task 7.4: Author composition-amplification test (bidirectional scry-fork → braunstein → distill → cabal round-trip) → **[G-5]**
- [ ] Task 7.5: E2E Goal Validation — run Task 7.E2E above; document evidence per goal → **[G-1, G-2, G-3, G-4, G-5, G-6]**
- [ ] Task 7.6: Author README.md, demo session transcript + digest, tag v1.0.0, publish release → **[all goals]**

### Dependencies
- All prior sprints

### Security Considerations
- **Launch artifacts**: demo transcript + digest ship publicly; HEKATE audit gates the release
- **Release signing**: follow Loa-framework release conventions; no new secrets introduced

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gygax schema PR not merged at launch time | Med | Med | FR-9 degradation path allows ship; compatibility_note in digest makes the gap visible; post-launch success criterion tracks the eventual merge |
| Blind-attribution self-test inconclusive (A-5 validation) | Med | Med | If inconclusive, document limitation explicitly; ship v1 with G-6 flagged as "partial"; plan external rater for v1.1 |
| Empirically-set Chaos Agent cap proves wrong at scale | Low | Low | Sprint 7 reviews accumulated cap data from Sprints 2–6; adjusts if needed before release |

### Success Metrics
- All 6 goals marked "achieved" with linked evidence
- v1.0.0 tag present; CHANGELOG complete
- CI stable on main

---

## Risk Register

| ID | Risk | Sprint | Probability | Impact | Mitigation | Owner |
|----|------|--------|-------------|--------|------------|-------|
| R-1 | Identity drift | 2, 7 | High | High | `refusals.yaml` + audit hook in /audit-sprint; prevents structural-analysis vocabulary in output | Author |
| R-2 | Hollow fiction (admissibility failure) | 2, 3 | Med | High | Sidecar requires `game_state_refs` on every archetype_decision; round-trip test is launch criterion | Author |
| R-3 | Intent contract violation (fudging) | 2, 4 | Med | High | §5.3 intent protocol + intent-flip A/B test automated in Sprint 4 + validated in Sprint 7 | Author |
| R-4 | Chaos Agent context-window blowup | 2 | Med | Med | Per-turn cap in voice-archetype schema; cap value empirically set in Sprint 2 | Author |
| R-5 | Tradition coverage gap | 6 | Med | Med | Structural-improvisation fallback + user confirmation (FR-12); swept in Sprint 6 | Author |
| R-6 | Safety failure (missed trigger, inadequate pause) | 2 | Med | High | Safety agreement mandatory in session state machine; community-standard taxonomy; events logged to project-level file | Author |
| R-7 | Gygax schema-bump coordination | 3, 7 | Med | Med | FR-9 degradation path; Arneson ships unilateral; digest compatibility_note surfaces the gap | Author + Gygax maintainer |
| R-8 | LLM voice drift (model updates) | 7 | High | Med | Pin identity prose; periodic manual regression against recorded voice samples; automation is v2 | Author |
| R-9 | Persona memory leakage across skills | 4, 7 | Med | Med | Session boundaries are state-machine transitions; cross-voice isolation test in Sprint 7 | Author |
| R-10 | Composition coupling bit-rot (standalone mode degrades) | 1–7 | Med | High | CI matrix REQUIRES arneson-alone green on every PR; first-class, not supplementary | Author |
| R-11 | N=1 founder effect (all validation internal) | 7 | High | Med | Publish demo artifacts at release; external-designer report is post-launch success criterion, not launch blocker | Author |
| R-12 | Scope ballooning (quality-driven cadence becomes "never ships") | 2+ | Med | High | Sprint 3 milestone (M2) is minimum-viable construct; /braunstein + /distill alone demonstrates admissibility | Author |

---

## Success Metrics Summary

| Metric | Target | Measurement Method | Sprint |
|--------|--------|-------------------|--------|
| Schemas implemented | 7/7 | File presence + yq validation | 1 |
| Skills operational | 8/8 | Smoke tests pass | 1 (stubs) → 6 (complete) |
| Round-trip admissibility | Green | CI test in `arneson-with-gygax` mode | 3 |
| Standalone viability | All 8 skills complete | CI test in `arneson-alone` mode | 1 (scaffold) → 7 (stable) |
| Identity-refusal audit violations | 0 | Grep against refusals vocabulary | 2 (first pass) → 7 (final) |
| Intent-flip A/B detectability | 100% of tested pairs | Automated diff on narration | 4 (automation) → 7 (final) |
| Archetype blind-attribution | Above chance | Designer self-test | 7 |
| HEKATE references | 0 hits | `grep -ri 'mibera\|hekate' .` | 1 (CI) → 7 (final) |

---

## Dependencies Map

```
Sprint 1 ──▶ Sprint 2 ──▶ Sprint 3 ──▶ Sprint 7
   │             │            │           ▲
   │             └─▶ Sprint 4 ─▶ Sprint 5 │
   │                    │                 │
   └───────────────────▶└─▶ Sprint 6 ─────┘
   Foundation    Vertical    Admissibility   Primitives   GM-Side   World-Building   Launch
                  Slice
```

- Sprint 2 depends on Sprint 1 (schemas, identity, fixture)
- Sprint 3 depends on Sprint 2 (sessions to distill)
- Sprint 4 depends on Sprint 2 (extracts from it)
- Sprint 5 depends on Sprint 4 (uses /narrate primitive)
- Sprint 6 depends on Sprint 4 (uses /scene pattern)
- Sprint 7 depends on all prior

---

## Appendix

### A. PRD Feature Mapping

| PRD FR | Feature | Sprint | Status |
|--------|---------|--------|--------|
| FR-1 | `/braunstein` flagship | 2 | Planned |
| FR-2 | `/voice` NPC workshop | 4 | Planned |
| FR-3 | `/scene` scene generator | 4 | Planned |
| FR-4 | `/narrate` primitive | 4 (extracted from 2) | Planned |
| FR-5 | `/improvise` GM-side | 5 | Planned |
| FR-6 | `/arneson` status | 6 | Planned |
| FR-7 | `/fragment` setting material | 6 | Planned |
| FR-8 | `/distill` session compressor | 3 | Planned |
| FR-9 | Intent interface (two-axis) | 1 (schema), 2 (reading) | Planned |
| FR-10 | Archetype memory 3-session window | 2 | Planned |
| FR-11 | Dice resolution authority | 2 | Planned |
| FR-12 | Tradition fallback | 6 (integration sweep) | Planned |
| FR-13 | Voice schema (base + extensions) | 1 (schemas), 4 (NPC), 5 (PC) | Planned |
| FR-14 | Chaos Agent bounding | 2 (empirical cap) | Planned |
| FR-15 | Safety as load-bearing | 2 | Planned |
| FR-16 | Structural tagging (sidecar) | 2 | Planned |
| FR-17 | Standalone fallback archetype bundle | 1 | Planned |

### B. SDD Component Mapping

| SDD Component | Sprint | Status |
|---------------|--------|--------|
| Construct manifest (`construct.yaml`) | 1 | Planned |
| Identity layer | 1 | Planned |
| Schema layer (7 schemas) | 1 | Planned |
| Fallback resources bundle | 1 | Planned |
| Synthetic fixture | 1 | Planned |
| Skills layer — `/braunstein` | 2 | Planned |
| Skills layer — `/distill` | 3 | Planned |
| Skills layer — `/narrate`, `/voice`, `/scene` | 4 | Planned |
| Skills layer — `/improvise` | 5 | Planned |
| Skills layer — `/fragment`, `/arneson` | 6 | Planned |
| CI matrix (both modes) | 1 (scaffold), 7 (stable) | Planned |
| Composition-detection protocol | 2 | Planned |
| Intent-reading protocol | 2 | Planned |
| Digest schema version negotiation | 3 | Planned |

### C. PRD Goal Mapping

| Goal ID | Goal Description | Contributing Tasks | Validation Task |
|---------|------------------|--------------------|-----------------|
| G-1 | Admissibility: transcript trustworthy as Gygax re-analysis evidence | Sprint 1: 1.6, 1.7, 1.9, 1.10 · Sprint 2: 2.1, 2.6, 2.7, 2.10 · Sprint 3: 3.1, 3.2, 3.3, 3.5 · Sprint 4: 4.2 · Sprint 5: 5.1, 5.3 | Sprint 7: 7.E2E |
| G-2 | Identity contract (refusals) | Sprint 1: 1.2, 1.3 · Sprint 2: 2.1, 2.2 · Sprint 5: 5.1, 5.2 · Sprint 6: 6.2 · Sprint 7: 7.2 | Sprint 7: 7.E2E |
| G-3 | Intent fidelity (voicing shifts on intent change) | Sprint 1: 1.4, 1.9 · Sprint 2: 2.5 · Sprint 4: 4.1, 4.2, 4.5, 4.6 · Sprint 6: 6.1, 6.3 | Sprint 7: 7.E2E |
| G-4 | Standalone viability | Sprint 1: 1.1, 1.8, 1.9, 1.10 · Sprint 2: 2.3, 2.4 · Sprint 6: 6.2, 6.3 · Sprint 7: 7.1 | Sprint 7: 7.E2E |
| G-5 | Composition amplification | Sprint 1: 1.7, 1.9, 1.10 · Sprint 2: 2.3 · Sprint 3: 3.3, 3.4, 3.5 · Sprint 5: 5.3 · Sprint 7: 7.1, 7.4 | Sprint 7: 7.E2E |
| G-6 | Archetype distinctness (≥3 archetypes voiced) | Sprint 1: 1.5, 1.9 · Sprint 2: 2.8, 2.9 · Sprint 4: 4.3, 4.4 · Sprint 7: 7.3 | Sprint 7: 7.E2E |

**Goal Coverage Check:**
- [x] All 6 PRD goals have at least one contributing task per sprint they appear in
- [x] All goals have a validation task in final sprint (7.E2E)
- [x] No orphan tasks (every task maps to at least one goal)

**Per-Sprint Goal Contribution:**

- **Sprint 1**: G-1 (partial: infra), G-2 (partial: identity files), G-3 (partial: intent schema), G-4 (partial: fallback bundle + fixture + CI), G-5 (partial: digest schema + fixture), G-6 (partial: voice schemas + fixture)
- **Sprint 2**: G-1 (vertical slice), G-2 (first refusal check), G-3 (intent reading), G-4 (composition detection + fallback), G-5 (composition detection), G-6 (memory + empirical cap)
- **Sprint 3**: G-1 (complete — round-trip), G-5 (complete — composition)
- **Sprint 4**: G-1 (regression), G-3 (complete — automated A/B), G-6 (voice workshops)
- **Sprint 5**: G-1 (new event types), G-2 (refusal check on /improvise), G-5 (distill consumes new events)
- **Sprint 6**: G-2 (read-only /arneson), G-3 (tradition consistency), G-4 (tradition consistency)
- **Sprint 7**: E2E validation of all 6 goals (Task 7.E2E)

---

## Beads Initialization Note

Beads is installed (`.beads/` directory exists) but tasks are not yet materialized. Sprint 1 Task 1.10 should include beads initialization (`br init` or equivalent per CLAUDE.loa.md §Beads-First Architecture) and materialize Sprint 1 tasks as the first batch. Subsequent sprints materialize their tasks at sprint-start per `/implement` skill's workflow.

---

*Generated by Sprint Planner Agent (/sprint-plan), 2026-04-13*
*Traces to PRD v1.0 and SDD v1.0 (both 2026-04-13)*
