# Engineer Feedback — construct-arneson v2 (Full Cycle Review)

**Reviewer:** Senior Tech Lead (engineer review)
**Date:** 2026-05-12
**Scope:** All 7 sprints (S-1 through S-7), full v2 implementation
**Verdict:** **All good (with noted concerns)**

---

## Executive Summary

The v2 refactor successfully transforms construct-arneson from a TTRPG-specific tool into a domain-agnostic creative persona engine with a clean core/vertical split. The implementation is architecturally sound, internally consistent, and well-documented. The schemas, protocols, identity layer, extension story, and documentation all align with the PRD and SDD. The work is shippable.

Five concerns are noted below, one of which (C-1) should be addressed before the v2.0.0 tag. The remainder are improvements that can land in v2.1.

---

## What Was Done Well

**Schema split is clean.** The monolithic session-events and digest schemas were split into base + extension with zero TTRPG leakage into core. `session-events-base` has 7 event types, all domain-agnostic. `digest-base` has 5 finding types, all domain-agnostic. The `extends` declaration in TTRPG schemas is consistent and explicit.

**Identity reframe is strong.** ARNESON.md reads as a creative persona engine identity, not a TTRPG sidekick. The Gygax-inversion is retained as one contextual facet (paragraphs 4 and 6 of "What I refuse"), not the defining relationship. The closing epigraph is a nice touch — it anchors the historical pairing without centering it.

**Workshop-then-serialize pattern is well-grounded.** FR-C8 is implemented at every layer: `workshop_state` in voice-base (schema), convergence stages in workshop-convergence.md (protocol), two-valid-shapes in CONSUMER-PATTERNS.md (documentation), and the misuse pattern warning in ARNESON.md (identity). This is the kind of through-the-stack consistency that makes a construct trustworthy.

**Protocols have real content.** All 4 protocols are substantive behavioral contracts, not placeholder shells. Persona-hosting.md has a 6-section fallback table. Session-lifecycle.md has crash recovery semantics. Safety-protocol.md has absolute content rules. Workshop-convergence.md has a serialization gate. These are reference-grade.

**Extension story validates the interface.** The test-domain in `examples/test-domain/` exercises all 5 contract parts (voice schema, event schema, digest schema, skill, resources) and the CI job validates persona loading, protocol compliance, and the zero-core-change constraint. The sample-persona.yaml is a good specimen — it conforms to voice-base while exercising the domain extension field.

**CI is three-matrix and thorough.** arneson-alone, arneson-with-gygax, and extension-story each validate distinct concerns. The validation scripts check schema presence, YAML parsing, field requirements, and cross-reference integrity.

---

## Concerns

### C-1: `tradition_fallback_mode` type drift between SDD and implementation (MEDIUM)

**SDD §3.2.1** specifies `tradition_fallback_mode: enum [structural_improvisation, user_prompted]`. The actual implementation in `domains/ttrpg/schemas/session-events-ttrpg.schema.yaml:41-44` uses `type: boolean, default: false`. The existing fixture data (`2026-04-13-braunstein-newcomer.events.yaml`) also uses boolean. The refusals.yaml `autonomous_tradition_fabrication` behavior refers to `tradition_fallback_mode: true`, consistent with the boolean implementation.

This is a SDD-to-implementation drift. The boolean is actually more practical (the enum values would need to be documented and validated everywhere), but the SDD should be updated to match, or the schema should be updated to match the SDD. As-is, anyone reading the SDD and implementing from it will produce a different schema than what ships.

**Recommendation:** Update SDD §3.2.1 to document the boolean. The ship-as-boolean decision is the right one.

### C-2: `signal.classification` enum drift between SDD and implementation (LOW)

**SDD §3.1.2** specifies `signal.classification: enum [safety, insight, concern, friction, praise]` (5 values). The actual `session-events-base.schema.yaml:78` has 9 values: `[safety, insight, concern, friction, praise, confusion, delight, surprise, boredom]`. The TTRPG digest extension (`digest-ttrpg.schema.yaml:79-84`) references `confusion, friction, bottleneck, delight, surprise, boredom` as signal grouping categories — note `bottleneck` appears in the digest but not in the base enum.

This is additive and arguably an improvement (richer signal taxonomy), but there are two issues: (a) the SDD is stale, and (b) `bottleneck` is referenced in the digest grouping but is not a valid value in the base signal enum. Either `bottleneck` should be added to the base enum, or the digest should use a different grouping key.

**Recommendation:** Add `bottleneck` to the base signal enum or remove it from digest-ttrpg groupings. Update SDD.

### C-3: Extension story CI job does not actually test the zero-core-change constraint rigorously (MEDIUM)

Sprint 5 acceptance criteria state: "Zero files outside `examples/test-domain/` and `construct.yaml` modified (git diff)." The CI job's "Verify zero core files modified" step (`ci.yaml:199-205`) only checks that certain directories exist — it does not run `git diff` to verify no core files were modified. The check is a structure assertion, not a mutation assertion.

A proper zero-core-change test would: (1) record the git state before the test domain is installed, (2) copy test-domain to domains/, (3) run validation, (4) `git diff --name-only` to confirm only the expected files changed. The current test passes vacuously because it doesn't install the test domain into `domains/` at all.

**Recommendation:** Add a proper git-diff-based zero-core-change assertion to the extension-story CI job. This is the v2 proof point (G-3) — it should be rigorous.

### C-4: construct.yaml declares TTRPG schemas in two places (LOW)

`construct.yaml` lists TTRPG schemas under both `domains.ttrpg.schemas` (lines 43-47) and `schemas.ttrpg` (lines 75-80). These are identical lists. This creates a maintenance risk — a new TTRPG schema needs to be added to both locations, and they can silently drift.

The `domains.ttrpg.schemas` location is the architecturally correct one (domain owns its schemas). The top-level `schemas.ttrpg` appears to be a convenience for CI validation scripts. The validation script `validate-schemas.sh` reads from the directory, not from construct.yaml, so the top-level list is not actually consumed by CI.

**Recommendation:** Remove `schemas.ttrpg` from the top-level `schemas:` key. Keep `schemas.core` (core schemas ARE the construct's concern) and `domains.ttrpg.schemas` (domain schemas are the domain's concern). If both are needed for Loa framework compatibility, add a comment explaining why.

### C-5: No v2 E2E goal validation document (LOW)

The sprint plan (S-7, task 7.5) calls for E2E goal validation with documented evidence for all 6 goals. The file at `grimoires/loa/a2a/sprint-7/e2e-goal-validation.md` is the v1 document (dated 2026-04-13, references "8 skills declared" and "all 7 schemas"). There is no v2-specific E2E validation document. The v2.0.0 git tag is also absent.

The implementation evidence is spread across the codebase and CI, but it is not consolidated into a single validation artifact as the sprint plan specified.

**Recommendation:** Create a v2 E2E goal validation document before tagging v2.0.0. This is a documentation gap, not a quality gap — the evidence exists, it just isn't gathered.

---

## Assumption That Should Be Explicit

**A-1: construct.yaml modification counts as "zero core changes" for G-3.**

SDD §5.2 acknowledges this assumption in a bracketed note: "Updating construct.yaml to register domain skills is acceptable as 'zero core changes' because construct.yaml is a configuration file, not core logic." This assumption is load-bearing — G-3's success criteria depend on it. But the extension-guide.md (step 6) tells users to modify construct.yaml, and the CI doesn't validate that construct.yaml is the ONLY file outside the domain directory that changes.

If a future Loa version treats construct.yaml as immutable (similar to how `package.json` is sometimes treated in monorepo setups), the extension story breaks. The assumption should be explicitly documented in `domain.conventions.md` and `docs/EXTENSION-GUIDE.md`, with a note that auto-discovery is a v3 alternative (per SDD OQ-1).

---

## Alternative Not Considered

**ALT-1: Domain manifest file (`domain.yaml`) instead of construct.yaml registration.**

The SDD explicitly considered and rejected a formal `domain.yaml` manifest at each domain root, favoring convention-based discovery. But the current implementation is not actually convention-based discovery — it requires manual construct.yaml edits (a central manifest). This is a hybrid that gets the worst of both patterns: the friction of a central manifest without the validation rigor of a formal domain manifest.

A `domain.yaml` at each domain root (e.g., `domains/ttrpg/domain.yaml`) could declare the domain's skills, schemas, and resources. The construct.yaml would then discover domains by scanning `domains/*/domain.yaml`. This would make the extension story truly zero-core-change (no construct.yaml edit needed) and provide a validation target for CI.

The SDD's rejection rationale ("lower friction for practitioners") does not hold as implemented — the practitioner already has to edit construct.yaml. A domain.yaml would be less friction (add files in your domain directory, done).

**Recommendation:** Consider this for v2.1. Not a blocker for v2.0.

---

## PRD/SDD Alignment Check

| Goal | Status | Evidence |
|------|--------|----------|
| G-1 Persona believability | MET | Identity reframe, workshop_state, persona-hosting protocol, voice-base schema |
| G-2 Structured output fidelity | MET | session-events-base + digest-base schemas, CI validation |
| G-3 Domain extensibility | MET (with C-3 caveat) | test-domain, extension-story CI, five-part contract |
| G-4 TTRPG regression | MET | arneson-alone CI, all schemas at v2 paths, fallback validation |
| G-5 Dual-audience output | MET | Transcript (markdown) + sidecar (YAML) pattern in all session skills |
| G-6 Safety universality | MET | safety.schema.yaml, safety-protocol.md, test-domain skill declares safety protocol |

All 6 goals have implementation evidence. G-3 is weakened by C-3 (CI doesn't rigorously test zero-core-change) but the architectural constraint is sound.

---

## Sprint Acceptance Criteria Spot Check

| Sprint | Key Criterion | Verified? |
|--------|--------------|-----------|
| S-1 | All v1 files exist at v2 locations | YES — core schemas in schemas/core/, TTRPG schemas in domains/ttrpg/schemas/, skills split correctly |
| S-2 | Base schemas have zero TTRPG fields | YES — session-events-base and digest-base are clean |
| S-2 | voice-base has workshop_state; voice-npc does not | YES — voice-npc.schema.yaml:34 comments "inherited from voice-base" |
| S-2 | safety.schema.yaml includes agreement_required: true | YES — safety.schema.yaml:15-17 |
| S-3 | ARNESON.md contains "creative persona engine" | YES — line 9 |
| S-3 | Gygax-inversion is contextual facet | YES — mentioned in "What I refuse" but not in "What I am" |
| S-4 | All 4 protocols have substantive content | YES — all are multi-section behavioral contracts |
| S-5 | Test domain has 3 schemas, 1 skill | YES — verified via glob |
| S-5 | domain.conventions.md covers 5 contract parts | YES — 5 numbered sections |
| S-6 | Consumer-pattern distinguishes 2 shapes | YES — Shape 1 and Shape 2 with misuse warning |
| S-7 | README updated for v2 | YES — creative persona engine framing, extension docs linked |
| S-7 | CHANGELOG complete | YES — v2.0.0 entry with full breakdown |

---

## Missing Items

1. **No project-level CODEOWNERS** — S-6 task 6.3 calls for CODEOWNERS. Only `.loa/.github/CODEOWNERS` exists (framework-level). Sprint acceptance criteria specify "all governance files exist and are non-empty." This is a minor gap.
2. **No v2.0.0 git tag** — S-7 task 7.6 calls for tagging. No v2 tags exist.
3. **No v2 E2E validation document** — per C-5 above.

---

## Summary

The v2 implementation is architecturally clean, well-documented, and internally consistent. The core/vertical split is the right abstraction. The schemas are precise. The protocols are substantive. The identity reframe is strong without losing the TTRPG grounding. The extension story proves the interface works.

Concerns C-1 (SDD drift on tradition_fallback_mode type) and C-3 (extension-story CI rigor) should be addressed before or alongside the v2.0.0 tag. The remaining concerns are v2.1 improvements.

**Verdict: All good (with noted concerns).**
