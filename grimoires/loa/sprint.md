# Sprint Plan: construct-arneson v3

**Version:** 3.0
**Date:** 2026-05-12
**Author:** Sprint Planner Agent (/sprint-plan)
**PRD Reference:** `grimoires/loa/prd.md` (v3, 2026-05-12)
**SDD Reference:** `grimoires/loa/sdd.md` (v3, 2026-05-12)

**Total Sprints:** 7
**Cadence:** Quality-driven, no fixed dates.
**Starting Point:** v2 complete (core/vertical split, extension interface, 4 protocols, 5 core schemas, TTRPG vertical, test-domain extension story, CI three-matrix).

---

## Goals

| ID | Goal | Validation |
|----|------|------------|
| G-1 | Anti-pattern suppression | Zero emdashes, zero assistant-mode leaks in persona output |
| G-2 | Engagement model works | Personas produce different engagement distributions per topic |
| G-3 | Silence is instrumented | `chose_not_to_respond` events in sidecars with reasoning |
| G-4 | v2 regression | All v2 CI green, 10 schemas validate, extension story passes |
| G-5 | Character-voice vertical ships | Second domain via extension interface, zero core file modifications |

---

## Sprint Dependencies

```
S-1 ──> S-2 ──> S-3 ──> S-4 ──> S-5 ──> S-6 ──> S-7
Anti    Engage  Silence Minimal CharVoice Workshop Regression
Pattern Model   Instr   Resp   Vertical  Enhance  + Release
```

Linear chain. Each sprint builds on the previous.

---

## Sprint 1: Anti-Pattern Protocol (M-1)

**Scope:** SMALL (3 tasks)
**Goal:** Define and wire the anti-pattern suppression infrastructure.

### Tasks

- [ ] **1.1** Author `protocols/anti-patterns.md`: default banned list (emdash, filler, assistant-mode, identity leak, hedge, servile, over-affirmation), register-aware grammar rule, enforcement semantics (audit-based, not generation-time) [G-1]
- [ ] **1.2** Add `anti_patterns` field to `schemas/core/voice-base.schema.yaml` per SDD 2.2: array of strings, required false, additive-only semantics documented [G-1]
- [ ] **1.3** Update `protocols/persona-hosting.md` Section 1 (Loading): add step 1.5 (load anti-pattern config --- merge protocol defaults + persona `anti_patterns` into effective list). Add anti-pattern enforcement to Section 3 (Voice Consistency) [G-1]

### Acceptance Criteria

- [ ] `protocols/anti-patterns.md` exists with 7+ banned patterns and enforcement rules
- [ ] `voice-base.schema.yaml` has `anti_patterns` field, `required: false`
- [ ] `persona-hosting.md` references anti-pattern loading and enforcement
- [ ] v2 CI still green (additive change only)

**Risk:** Anti-pattern list too aggressive. Mitigated: list is configurable, start conservative.

---

## Sprint 2: Engagement Model (M-2)

**Scope:** MEDIUM (4 tasks)
**Goal:** Per-persona engagement evaluation in voice-base and session lifecycle.

### Tasks

- [ ] **2.1** Add `engagement` block and `tensions` field to `schemas/core/voice-base.schema.yaml` per SDD 2.1 + 2.3b: engagement (default_mode, threshold, high_topics, low_topics, minimal_vocabulary) + tensions (says, does, context). All required: false [G-2]
- [ ] **2.2** Update `protocols/session-lifecycle.md` Active state: turn cycle gains engagement evaluation step (direction -> engagement_eval -> [full|minimal|silence]). Document the three routing paths [G-2]
- [ ] **2.3** Update `protocols/persona-hosting.md` Section 1 step 1.5: load engagement config alongside anti-pattern config [G-2]
- [ ] **2.4** Validate: existing voice YAMLs without `engagement` still validate (backward compat). Create a test voice fixture with engagement config to prove schema works [G-2, G-4]

### Acceptance Criteria

- [ ] `voice-base.schema.yaml` has `engagement` block with all 5 sub-fields
- [ ] `session-lifecycle.md` documents engagement evaluation in turn cycle
- [ ] Personas without `engagement` default to full response (v2 behavior)
- [ ] v2 CI green

**Risk:** Engagement threshold too coarse (single float). Acceptable for v3; qualitative model is v4.

---

## Sprint 3: Silence Instrumentation (M-3)

**Scope:** SMALL (3 tasks)
**Goal:** Capture non-engagement as structured data.

### Tasks

- [ ] **3.1** Add `chose_not_to_respond` event type to `schemas/core/session-events-base.schema.yaml` per SDD 2.3: persona, prompt_summary, reason, engagement_score, mode [G-3]
- [ ] **3.2** Add `engagement_patterns` section to `schemas/core/digest-base.schema.yaml` per SDD 2.4: total_prompts, full/minimal/silent counts, topic_breakdown [G-3]
- [ ] **3.3** Document null output contract: update `protocols/session-lifecycle.md` silence path --- no persona output, sidecar captures `chose_not_to_respond`, consumer must handle null [G-3]

### Acceptance Criteria

- [ ] `session-events-base.schema.yaml` has `chose_not_to_respond` event type
- [ ] `digest-base.schema.yaml` has `engagement_patterns` findings section
- [ ] Session lifecycle documents silence as valid output state
- [ ] v2 CI green (additive schema changes)

**Risk:** Consumers break on null output. Mitigated: documented contract, not Arneson's problem.

---

## Sprint 4: Minimal Response (M-4)

**Scope:** SMALL (2 tasks)
**Goal:** Wire the middle path between full engagement and silence.

### Tasks

- [ ] **4.1** Document minimal response behavior in `protocols/session-lifecycle.md`: minimal path generates from `engagement.minimal_vocabulary` only, 1-3 words max, captured as `dialogue` event with engagement context [G-2]
- [ ] **4.2** Create test fixture: voice with `minimal_vocabulary` defined. Validate that minimal-mode dialogue events are distinguishable from full-mode in the sidecar [G-2, G-3]

### Acceptance Criteria

- [ ] Session lifecycle documents minimal generation path
- [ ] Minimal responses stay in-voice (per-persona vocabulary)
- [ ] Sidecar can distinguish minimal from full dialogue events
- [ ] v2 CI green

**Risk:** Minimal. Small sprint, additive only.

---

## Sprint 5: Character-Voice Vertical (M-5)

**Scope:** MEDIUM (5 tasks)
**Goal:** Ship the second domain vertical. Prove extension interface works in production.

### Tasks

- [ ] **5.1** Create `domains/character-voice/schemas/voice-character.schema.yaml` per SDD 4.3: extends voice-base with voice_anchors, discipline_locks, canon_boundary, sibling_relationships, decline_patterns, modes [G-5]
- [ ] **5.2** Create `domains/character-voice/schemas/session-events-character.schema.yaml` per SDD 4.4: extends session-events-base with voice_drift, canon_match, engagement_decision events [G-5]
- [ ] **5.3** Create `domains/character-voice/schemas/digest-character.schema.yaml` per SDD 4.5: extends digest-base with voice_drift_events, canon_match_rate, engagement_profile, anti_pattern_violations [G-5]
- [ ] **5.4** Author `domains/character-voice/domain.conventions.md`: five-part contract documentation, how to add a character, canon document conventions [G-5]
- [ ] **5.5** Create `domains/character-voice/resources/akane.yaml`: Akane fixture conforming to voice-character schema. Engagement config (high: risk/rooftops/daring; low: data/planning/finance). Voice anchors from canon battle whispers. At least 2 tensions (e.g., "says she doesn't plan / clearly cases buildings before breaking in"). Anti-patterns if persona-specific [G-2, G-5]

### Acceptance Criteria

- [ ] All 3 schemas validate and declare `extends` to correct core schema
- [ ] `domain.conventions.md` covers all 5 contract parts
- [ ] `akane.yaml` conforms to `voice-character.schema.yaml`
- [ ] Akane has engagement config that would ghost data and fire on risk
- [ ] Zero core files modified (extension story constraint) --- only `construct.yaml` updated
- [ ] CI extension-story validates the new domain

**Risk:** R: character-voice is TTRPG-shaped. Mitigated: validate against KIZUNA + Mongolian use cases.

---

## Sprint 6: Workshop Enhancement (M-6)

**Scope:** SMALL (2 tasks)
**Goal:** Make engagement visible as workshop convergence data.

### Tasks

- [ ] **6.1** Update `protocols/workshop-convergence.md`: add engagement distribution tracking section per SDD 3.3. Workshop session close emits N full / M minimal / K silent. Per-topic breakdown when available [G-2, G-3]
- [ ] **6.2** Document convergence integration: how engagement patterns feed into `convergence_notes`, how curators use distribution data to refine voice ("Akane should ghost this topic") [G-2]

### Acceptance Criteria

- [ ] Workshop convergence protocol includes engagement tracking section
- [ ] Engagement distribution format documented (total + per-topic)
- [ ] Clear curator workflow: see distribution -> adjust engagement config -> re-workshop

**Risk:** Minimal. Documentation sprint building on wired infrastructure.

---

## Sprint 7: Regression + Release (M-7)

**Scope:** MEDIUM (5 tasks)
**Goal:** Ship v3. All goals validated. v2 regression green.

### Tasks

- [ ] **7.1** Run full v2 regression: all schemas validate, CI three-matrix green (arneson-alone, arneson-with-gygax, extension-story), TTRPG vertical unaffected [G-4]
- [ ] **7.2** Run character-voice extension story: domain discovered, schemas validate, Akane fixture loads, zero core modifications [G-5]
- [ ] **7.3** E2E goal validation (see table below) [All goals]
- [ ] **7.4** Update CHANGELOG with v3 changes. Update README if needed [G-4]
- [ ] **7.5** Tag v3.0.0 release [All goals]

### E2E Goal Validation (Task 7.3)

| Goal | Validation | Expected Result |
|------|-----------|-----------------|
| G-1 | Transcript scan against anti-pattern list | Zero matches |
| G-2 | Run Akane against QA prompts, check engagement distribution | Ghosts data, fires on risk |
| G-3 | Check sidecar for `chose_not_to_respond` events | Present with reasoning |
| G-4 | v2 CI three-matrix | All green |
| G-5 | Character-voice extension story CI | Green, zero core diff |

### Acceptance Criteria

- [ ] All 5 goals validated with evidence
- [ ] All CI modes green
- [ ] v3.0.0 tag present
- [ ] CHANGELOG updated

---

## Goal Traceability Matrix

| Goal | Contributing Tasks | Validation |
|------|-------------------|------------|
| G-1 Anti-pattern suppression | 1.1, 1.2, 1.3 | 7.3 |
| G-2 Engagement model | 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 5.5, 6.1, 6.2 | 7.3 |
| G-3 Silence instrumented | 3.1, 3.2, 3.3, 4.2, 6.1 | 7.3 |
| G-4 v2 regression | 2.4, 7.1 | 7.3 |
| G-5 Character-voice ships | 5.1, 5.2, 5.3, 5.4, 5.5, 7.2 | 7.3 |

All 5 goals have contributing tasks. All validated in Sprint 7.

---

## Summary

| Sprint | Milestone | Tasks | Scope |
|--------|-----------|-------|-------|
| S-1 | Anti-Pattern Protocol | 3 | Small |
| S-2 | Engagement Model | 4 | Medium |
| S-3 | Silence Instrumentation | 3 | Small |
| S-4 | Minimal Response | 2 | Small |
| S-5 | Character-Voice Vertical | 5 | Medium |
| S-6 | Workshop Enhancement | 2 | Small |
| S-7 | Regression + Release | 5 | Medium |
| **Total** | | **24 tasks** | |

---

*Generated by Sprint Planner Agent (/sprint-plan), 2026-05-12*
