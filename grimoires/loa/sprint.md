# Sprint Plan: construct-arneson v2

**Version:** 2.0
**Date:** 2026-05-12
**Author:** Sprint Planner Agent (/sprint-plan)
**PRD Reference:** `grimoires/loa/prd.md` (v2, 2026-05-12)
**SDD Reference:** `grimoires/loa/sdd.md` (v2, 2026-05-12)

**Total Sprints:** 7
**Cadence:** Quality-driven, no fixed dates. Progression gated on milestone acceptance criteria, not calendar.
**Starting Point:** v1 Sprint 1 complete (identity layer, 7 schemas, 8 skill scaffolds, fallback archetypes, synthetic fixture, CI scaffold). v1 Sprints 2-7 superseded by this plan.

---

## Sprint Dependencies

```
S-1 ──> S-2 ──> S-3 ──> S-4 ──> S-5 ──> S-6 ──> S-7
Dir     Schema  Identity Regression Extension Docs  Release
Struct  Split   Reframe  Gate       Story
```

Linear chain. Each sprint builds on the previous.

---

## Sprint 1: Directory Restructure (M-1 partial)

**Scope:** MEDIUM (6 tasks)
**Goal:** Create the core/vertical directory boundary. Move all files to v2 locations. Update all inter-file references. No logic changes, no schema splits, no content rewrites.

### Tasks

- [ ] **1.1** Create v2 directory structure: `schemas/core/`, `domains/ttrpg/schemas/`, `domains/ttrpg/skills/`, `domains/ttrpg/resources/`, `protocols/` [G-3]
- [ ] **1.2** Move domain-agnostic schemas to `schemas/core/` (`voice-base`, `experiential_intent`). Move TTRPG-specific schemas to `domains/ttrpg/schemas/` (`voice-archetype`, `voice-npc`, `voice-pc`). Move `session-events` and `digest` to `domains/ttrpg/schemas/` temporarily (split in S-2) [G-3, G-4]
- [ ] **1.3** Move TTRPG skills to `domains/ttrpg/skills/` (`braunstein`, `improvise`, `scene`, `narrate`, `fragment`). Core skills (`arneson`, `distill`, `voice`) remain in `skills/` [G-3, G-4]
- [ ] **1.4** Move `resources/archetypes-fallback/` to `domains/ttrpg/resources/archetypes-fallback/` [G-3, G-4]
- [ ] **1.5** Create empty protocol shells: `protocols/persona-hosting.md`, `protocols/session-lifecycle.md`, `protocols/safety-protocol.md`, `protocols/workshop-convergence.md` [G-3]
- [ ] **1.6** Update `construct.yaml`: domain from `design` to `creative-persona`, add `domains:` section, update all schema and skill paths. Update CI workflow and `scripts/ci/` validation scripts for new paths [G-3, G-4]

### Acceptance Criteria

- [ ] All v1 files exist at v2 locations (no file missing)
- [ ] No v1 files remain at old locations (except core skills staying in `skills/`)
- [ ] CI runs green with updated paths
- [ ] `construct.yaml` validates against Loa construct schema
- [ ] HEKATE audit zero hits
- [ ] No logic changes in any SKILL.md or schema file (diff shows moves only)

**Risk:** R-8 (restructure breaks references). Mitigated by atomic reference updates + CI validation.

---

## Sprint 2: Schema Split (M-1 continued + M-3)

**Scope:** MEDIUM (6 tasks)
**Goal:** Split monolithic schemas into base + extension. Create new core schemas. After this sprint, every schema has a clear core-or-domain designation.

### Tasks

- [ ] **2.1** Extract base event types from `session-events.schema.yaml` into `schemas/core/session-events-base.schema.yaml` per SDD 3.1.2 (dialogue, signal, decision, pause, scene_transition, state_reference, safety_trigger) [G-2, G-3]
- [ ] **2.2** Create `domains/ttrpg/schemas/session-events-ttrpg.schema.yaml` extending base per SDD 3.2.1 (dice_roll, archetype_decision, intent_conflict, gm_prompt, rule_of_cool, clarifying_question) [G-2, G-4]
- [ ] **2.3** Extract base digest format into `schemas/core/digest-base.schema.yaml` per SDD 3.1.3 (key_moments, persona_signals, state_conflicts, unresolved_questions, safety_findings) [G-2, G-3]
- [ ] **2.4** Create `domains/ttrpg/schemas/digest-ttrpg.schema.yaml` extending base per SDD 3.2.3 (rule_invocations, rule_of_cool_overrides, dead_design_space, archetype_memory_updates, gygax_consumption_ready) [G-2, G-4]
- [ ] **2.5** Create `schemas/core/safety.schema.yaml` per SDD 3.1.4 (pre_session agreement, in_session commands, safety_as_data logging) [G-6]
- [ ] **2.6** Add `workshop_state` to `schemas/core/voice-base.schema.yaml` per SDD 3.1.1 (stage enum, iteration_count, last_workshop_session, convergence_notes). Remove local `workshop_state` from `domains/ttrpg/schemas/voice-npc.schema.yaml` [G-1, G-3]

### Acceptance Criteria

- [ ] All base schemas validate as valid YAML with zero TTRPG-specific fields
- [ ] All TTRPG extension schemas validate and declare `extends` relationship to base
- [ ] Existing fixture data validates against updated schema paths
- [ ] `voice-base` has `workshop_state`; `voice-npc` does not duplicate it
- [ ] `safety.schema.yaml` includes: `agreement_required: true`, pause/x-card/resume commands, `safety_as_data: true`

**Risk:** R-6 (schema backwards incompatibility). Mitigated by additive-only changes in base schemas.

---

## Sprint 3: Identity Reframe (M-2)

**Scope:** SMALL (3 tasks)
**Goal:** Reframe Arneson's identity from "Gygax's inverse" to "creative persona engine." Gygax-inversion retained as one contextual facet.

### Tasks

- [ ] **3.1** Rewrite `identity/ARNESON.md` per SDD 1.4.2: creative persona engine identity. Retain Gygax-inversion as one facet. Reference director/performer model. No TTRPG-specific language in core identity claims [G-1, G-3]
- [ ] **3.2** Update `identity/persona.yaml` and `identity/expertise.yaml`: generalize voice parameters, add domain-agnostic expertise items (persona hosting, workshop convergence, session instrumentation, safety-as-data) [G-1, G-3]
- [ ] **3.3** Update `identity/refusals.yaml`: generalize structural analysis refusals beyond TTRPG vocabulary. TTRPG-specific items documented as domain-contextual examples [G-1, G-3]

### Acceptance Criteria

- [ ] `ARNESON.md` contains "creative persona engine" framing (not "Gygax's inverse" as primary identity)
- [ ] Gygax-inversion mentioned as a contextual facet, not the defining relationship
- [ ] No TTRPG-only vocabulary in core identity claims
- [ ] Sprint 0 prototype quality bar (5/5 axes) remains achievable
- [ ] Refusals still refuse structural analysis, probability math, mechanical recommendations

**Risk:** R-4 (identity reframe weakens voice). Mitigated by retaining Gygax-inversion as facet and regression against Sprint 0 quality bar.

---

## Sprint 4: TTRPG Regression + Protocol Population (M-4)

**Scope:** MEDIUM (5 tasks)
**Goal:** Prove the restructure didn't break anything. CI green. All v1 acceptance criteria verified. Core protocols populated with behavioral content.

### Tasks

- [ ] **4.1** Update `.github/workflows/ci.yaml` for three-matrix CI (arneson-alone, arneson-with-gygax, extension-story placeholder). Update `scripts/ci/` validation scripts for new paths [G-4]
- [ ] **4.2** Run full v1 Sprint 1 acceptance suite against refactored codebase: schema validation, fixture validation, HEKATE audit, construct validation, skill validation [G-4]
- [ ] **4.3** Populate `protocols/persona-hosting.md`: extract persona loading, memory management, grounding, voice consistency, state persistence patterns from `/braunstein` and `/voice` SKILL.md files. Generalize beyond TTRPG [G-1, G-3]
- [ ] **4.4** Populate `protocols/session-lifecycle.md` (generalized state machine per SDD 6.1) and `protocols/safety-protocol.md` (mandatory safety agreement, in-session commands, safety-as-data per SDD 3.1.4) [G-2, G-6]
- [ ] **4.5** Populate `protocols/workshop-convergence.md`: workshop-then-serialize pattern per SDD 6.2 (Drafting -> Refining -> Locked stages, convergence criteria, serialization gate) [G-1, G-3]

### Acceptance Criteria

- [ ] CI green in arneson-alone and arneson-with-gygax modes
- [ ] All schemas validate at new paths
- [ ] Synthetic fixture validates against updated schema references
- [ ] HEKATE audit zero hits
- [ ] All 4 protocols have substantive behavioral content (not empty shells)
- [ ] Protocols reference core schemas, not TTRPG-specific schemas
- [ ] Each protocol is self-contained (readable without TTRPG context)

**Risk:** R-1 (over-abstraction breaks TTRPG vertical). If v1 criteria break here, fix the abstraction, not the tests.

---

## Sprint 5: Extension Story (M-5)

**Scope:** MEDIUM (5 tasks)
**Goal:** Validate the domain extension interface by building a minimal test domain. Zero core files modified. The v2 proof point.

### Tasks

- [ ] **5.1** Author `domains/ttrpg/domain.conventions.md`: document how the TTRPG vertical implements each of the 5 extension contract parts [G-3]
- [ ] **5.2** Create `examples/test-domain/schemas/`: `voice-test.schema.yaml` (extends voice-base), `session-events-test.schema.yaml` (extends base), `digest-test.schema.yaml` (extends base) [G-3]
- [ ] **5.3** Create `examples/test-domain/skills/test-workshop/`: minimal workshop skill following core protocols [G-3, G-6]
- [ ] **5.4** Create `examples/test-domain/resources/`: `sample-state.yaml` and `sample-persona.yaml` conforming to voice-base + voice-test extension [G-3]
- [ ] **5.5** Implement extension story CI job: copy test-domain to `domains/`, register in construct.yaml, validate persona loads, session runs, sidecar captures base + test events, distill produces output. Assert zero core files modified (git diff) [G-3, G-4]

### Acceptance Criteria

- [ ] Test domain loads and is discoverable by Arneson
- [ ] Test domain persona loads via voice-base + voice-test extension
- [ ] Test domain session produces sidecar with both base and test-domain event types
- [ ] Safety flow activates in test domain context
- [ ] Zero files outside `examples/test-domain/` and `construct.yaml` modified (git diff)
- [ ] `domain.conventions.md` covers all 5 extension contract parts with TTRPG examples

**Risk:** R-2 (extension too narrow). R-3 (extension too wide). If test domain can't work cleanly, the abstraction needs adjustment.

---

## Sprint 6: Documentation & Governance (M-6)

**Scope:** SMALL (3 tasks)
**Goal:** Document everything a practitioner needs to use, extend, and contribute to Arneson.

### Tasks

- [ ] **6.1** Author consumer-pattern guide: two valid shapes (workshop tool vs doctrine reference) per FR-C8 and arneson#2. Include misuse pattern warning [G-1]
- [ ] **6.2** Author extension interface reference: expand domain.conventions.md into standalone guide with step-by-step "add a new domain" walkthrough [G-3]
- [ ] **6.3** Author CONTRIBUTING.md, SECURITY.md, CODEOWNERS per governance standards [G-4]

### Acceptance Criteria

- [ ] Consumer-pattern guide distinguishes Shape 1 (workshop) from Shape 2 (doctrine reference)
- [ ] Consumer-pattern guide flags skipping the workshop as documented misuse
- [ ] Extension interface reference includes complete walkthrough with examples
- [ ] All governance files exist and are non-empty

**Risk:** Minimal. Documentation sprint.

---

## Sprint 7: Release (M-7)

**Scope:** MEDIUM (6 tasks)
**Goal:** Ship v2. Validate all goals end-to-end. Tag release.

### Tasks

- [ ] **7.1** Stabilize CI matrix: all three modes green on main for 3+ consecutive commits [G-4]
- [ ] **7.2** L0/L1/L2 construct validation per Loa framework requirements [G-4]
- [ ] **7.3** Update README.md for v2: creative persona engine framing, extension story, quick-start for new domains [G-3]
- [ ] **7.4** Update CHANGELOG with v2 changes [G-4]
- [ ] **7.5** E2E Goal Validation (see table below) [All goals]
- [ ] **7.6** Tag v2.0.0 release [All goals]

### E2E Goal Validation (Task 7.5)

| Goal | Validation | Expected Result |
|------|-----------|-----------------|
| G-1 Persona believability | Sprint 0 prototype quality regression (5/5 axes) against v2 identity | 5/5 axes pass |
| G-2 Structured output fidelity | Schema validation pass rate across all domains | 100% |
| G-3 Domain extensibility | Extension story CI: test-domain loads, runs, zero core changes | CI green, zero-core-diff |
| G-4 TTRPG regression | All v1 acceptance criteria pass, both modes | CI green both modes |
| G-5 Dual-audience output | Transcripts render as markdown; sidecars parse as YAML | Pass |
| G-6 Safety universality | Safety flow activates in TTRPG AND test-domain | Safety events in both sidecars |

### Acceptance Criteria

- [ ] All 6 goals validated with documented evidence
- [ ] All three CI modes green on main
- [ ] v2.0.0 tag present
- [ ] CHANGELOG and README complete

---

## Goal Traceability Matrix

| Goal | Contributing Tasks | Validation |
|------|-------------------|------------|
| G-1 Persona believability | 2.6, 3.1, 3.2, 3.3, 4.3, 4.5, 6.1 | 7.5 |
| G-2 Structured output fidelity | 2.1, 2.2, 2.3, 2.4, 4.4 | 7.5 |
| G-3 Domain extensibility | 1.1-1.6, 2.1, 2.3, 2.6, 3.1-3.3, 4.3, 4.5, 5.1-5.5, 6.2, 7.3 | 7.5 |
| G-4 TTRPG regression | 1.2-1.4, 1.6, 2.2, 2.4, 4.1, 4.2, 5.5, 7.1, 7.2, 7.4 | 7.5 |
| G-5 Dual-audience output | 2.1, 2.3, 4.4 | 7.5 |
| G-6 Safety universality | 2.5, 4.4, 5.3, 5.5 | 7.5 |

All 6 goals have contributing tasks. All goals validated in Sprint 7. No orphan tasks.

---

## Summary

| Sprint | Milestone | Tasks | Scope |
|--------|-----------|-------|-------|
| S-1 | Directory Restructure | 6 | Medium |
| S-2 | Schema Split | 6 | Medium |
| S-3 | Identity Reframe | 3 | Small |
| S-4 | Regression + Protocols | 5 | Medium |
| S-5 | Extension Story | 5 | Medium |
| S-6 | Documentation | 3 | Small |
| S-7 | Release | 6 | Medium |
| **Total** | | **34 tasks** | |

---

*Generated by Sprint Planner Agent (/sprint-plan), 2026-05-12*
