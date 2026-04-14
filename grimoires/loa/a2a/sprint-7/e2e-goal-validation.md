# E2E Goal Validation — construct-arneson v1

**Sprint**: sprint-7 (Hardening + Launch / M6+M7)
**Date**: 2026-04-13

## Goal Validation Matrix

| Goal | Description | Validation Method | Status | Evidence |
|------|-------------|-------------------|--------|----------|
| G-1 | Admissibility (round-trip) | `/braunstein` → `/distill` → Gygax `/cabal --from-session` | **SCHEMA-READY** | `schemas/session-events.schema.yaml` + `schemas/digest.schema.yaml` specify the contract. `/distill` SKILL.md maps all 9 event types to 8 findings categories. Round-trip requires live invocation + Gygax v3. |
| G-2 | Identity contract (refusals) | Grep outputs for refusal vocabulary | **SPECIFIED** | `identity/refusals.yaml` defines 7 refusal categories with `vocabulary_to_avoid` lists. Every SKILL.md includes "What You Must Not Do" / refusal section. Audit integration deferred to first live session. |
| G-3 | Intent fidelity (voicing shift) | Intent-flip A/B on `/narrate` | **SPECIFIED** | `skills/narrate/SKILL.md` explicitly documents intent-flip sensitivity: "same mechanic outcome + different experiential_intent MUST produce materially different prose." Fixture `scene-seeds.md` Seed 4 provides the test protocol. |
| G-4 | Standalone viability | All 8 skills in arneson-alone CI mode | **CI-VERIFIED** | `validate-skills.sh`: 8/8 skills have SKILL.md + index.yaml. CI `arneson-alone` job verifies no Gygax paths present. Full behavioral test requires live invocation. |
| G-5 | Composition amplification | Bidirectional scry-fork round-trip | **SCHEMA-READY** | Composition-detection probe in `/braunstein` SKILL.md. `/distill` output format specified for Gygax ingestion. Gygax not available in workspace for live round-trip. |
| G-6 | Archetype distinctness | Blind-attribution test | **SPECIFIED** | 9 archetype fallbacks with distinct voice profiles (speech_patterns, reaction_tempo, emotional_register, experiential_intent_weights). Sprint 0 prototype demonstrated Newcomer distinctness. Blind-attribution protocol requires 3+ live sessions. |

### Validation Status Legend

| Status | Meaning |
|--------|---------|
| **CI-VERIFIED** | Automated check passes in CI |
| **SCHEMA-READY** | Schema contract in place; behavioral test requires live invocation |
| **SPECIFIED** | Protocol documented; execution requires manual invocation or external tooling |

### What Blocks Full Validation

1. **Live `/braunstein` invocation** — No session has been run yet. The SKILL.md is the prompt; the test is "invoke it." This is the single highest-value next action.
2. **Gygax v3 availability** — Round-trip (G-1) and composition (G-5) require Gygax installed. Tracked as external dependency.
3. **Multiple archetype sessions** — Blind-attribution (G-6) needs 3+ sessions with different archetypes against the same fixture.

### Recommended First Validation Sequence

```bash
# 1. Run one /braunstein session (proves G-2, G-4 partially, G-6 starts)
/braunstein --newcomer --game-state examples/synthetic-fixture/game-state.yaml

# 2. Distill the session (proves G-1 schema-level)
/distill grimoires/arneson/sessions/{session}.md

# 3. Run /braunstein with a different archetype (G-6 attribution data)
/braunstein --optimizer --game-state examples/synthetic-fixture/game-state.yaml

# 4. Run intent-flip test (G-3)
# Edit game-state: change water_touch.experiential_intent.tone from uncanny to mundane
/braunstein --newcomer --game-state examples/synthetic-fixture/game-state.yaml
# Compare transcripts

# 5. Check composition (G-5) — requires Gygax v3 install
# /cabal --from-session grimoires/arneson/digests/{session}.digest.yaml
```

---

## CI Verification (All 6 checks green)

```
OK: HEKATE audit clean
OK: construct.yaml validates (8 skills declared)
OK: all 7 schemas parse
OK: 9 fallback archetypes validate
OK: synthetic fixture validates
OK: all 8 implemented skills have SKILL.md + index.yaml
```

Zero MIBERA/HEKATE references. All schemas structural. All skills present.
