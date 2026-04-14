# Sprint 1 Implementation Report — Foundation (M0)

**Sprint**: sprint-1 (PRD Milestone M0)
**Date**: 2026-04-13
**Implementer**: /implement skill
**Status**: Ready for review

---

## Executive Summary

Sprint 1 (Foundation) lays the structural bedrock for construct-arneson v1. Ten tasks
delivered: construct manifest, four identity files, seven YAML schemas, nine fallback
archetypes, a synthetic reference fixture (Threshold game), grimoire directory
scaffolding, and a CI workflow with two-matrix build (`arneson-alone` +
`arneson-with-gygax`). All five CI validation scripts pass locally.

The sprint scope is wide but shallow — no skills implemented yet; that is Sprint 2.
What's here is the shape into which Sprint 2 will write `/braunstein`.

Two Sprint 0 findings are carried through: (1) the Threshold fixture is HEKATE-free
per user directive, (2) the "no narrator omniscience inside archetype voice" rule is
encoded in `identity/ARNESON.md` and the Newcomer fallback's authoring notes.

---

## Tasks Completed

### Task 1.1 — Construct Manifest
**File**: `construct.yaml` (57 lines)
**Approach**: Authored per SDD Appendix 11.A. Declares slug `arneson`, schema_version 3,
type `skill-pack`, domain `design`, 8 skills, composition-path probes with `required: false`
to honor standalone-plus-composable, fallback bundle location, all 7 schemas, output paths.
**Acceptance**: `validate-construct.sh` green (all required fields present, 8 skills
declared, schemas + identity files referenced and existing).

### Task 1.2 — Identity Prose (`identity/ARNESON.md`)
**File**: `identity/ARNESON.md` (~90 lines)
**Approach**: Prose identity narrative. Distinct from Gygax. Covers: what Arneson does,
what it refuses, what it emits (prose + sidecar), how it speaks, safety, memory discipline,
and what it is not. Encodes the Sprint 0 prototype finding: narrator omniscience belongs
only in scene-frame openings/endings, never inside archetype voice.

### Task 1.3 — Identity YAMLs
**Files**:
- `identity/persona.yaml` — Arneson's meta-role voice (warm-improvisational)
- `identity/expertise.yaml` — primary/secondary areas + out-of-scope (Gygax boundary)
- `identity/refusals.yaml` — 7 refusal categories with `vocabulary_to_avoid` lists; configured for Sprint 7 identity-refusal audit
**Approach**: Structured declarations that downstream skills and the Sprint 7 audit tooling
read. Refusals carry both the "what" and the "why" (so the refusal can be adapted to edge
cases without being broken).

### Task 1.4 — Experiential Intent Schema
**File**: `schemas/experiential_intent.schema.yaml`
**Approach**: Per SDD §3.2.1. Controlled vocabulary for tone (9 enum values), pacing (4),
stakes (5), register (6), plus free-text notes field. Extensible via
`experiential_intent_extensions` in tradition lore. Degradation path documented for
both field-missing and single-axis-intent-only cases.

### Task 1.5 — Voice Schemas (4 files)
**Files**: `schemas/voice-{base,archetype,npc,pc}.schema.yaml`
**Approach**: Per SDD §3.2.2–3.2.5. Base schema provides shared fields (speech_patterns,
reaction_tempo, emotional_register, memory_slots, known_facts). Three extensions add
type-specific fields: archetype adds `experiential_intent_weights` (9-tone map),
`memory_window_size`, `chaos_axis_config` (required for chaos-agent, optional otherwise);
npc adds location/faction/role/workshop_state; pc adds `player_consent_metadata` with
lines/veils/x_card_active.

### Task 1.6 — Session Events Schema (admissibility infrastructure)
**File**: `schemas/session-events.schema.yaml`
**Approach**: Per SDD §3.2.6 — the load-bearing schema that makes G-1 admissibility
mechanically verifiable. Defines session preamble (mode, game_state_checksum for
replay/forensics, composition_mode, safety_agreement) + 9 event types (scene_frame,
dice_roll, archetype_decision, signal_flag, intent_conflict, gm_prompt, safety_trigger,
rule_of_cool, clarifying_question) + session_end. Validation rules enforce R-2 mitigation:
every archetype_decision and scene_frame MUST have `game_state_refs` populated.

### Task 1.7 — Digest Schema
**File**: `schemas/digest.schema.yaml`
**Approach**: Per SDD §3.2.7. Output shape of `/distill` — Gygax-ingestible AND
self-describing. Preamble carries `gygax_ingestible: bool` + `compatibility_note` for
cross-version negotiation. 8 findings categories (rule_invocations, rule_of_cool_overrides,
clarifying_questions, signal_flags grouped by type, intent_conflicts, dead_design_space,
experiential_intent_observations) + `archetype_memory_updates` for write-back candidates.
The `dead_design_space` category implements the teammate-feedback principle: safety triggers
are design findings, not only social events.

### Task 1.8 — Fallback Archetype Bundle (9 YAMLs + README)
**Files**: `resources/archetypes-fallback/{newcomer,optimizer,chaos-agent,storyteller,rules-lawyer,explorer,min-maxer,casual,contrarian}.yaml` + `README.md`
**Approach**: Each archetype is schema-valid against `voice-archetype.schema.yaml` and
carries `fallback_source: true`. Newcomer gets the full voice treatment from Sprint 0
prototype (including "describes before interpreting" marker, "spills perception before
noticing" trigger). Optimizer, Chaos Agent, Storyteller, Rules Lawyer, Explorer,
Min-Maxer, Casual, Contrarian get genuinely distinct voice texture (each with 4–6
distinctive_markers and tone-weight profiles that materially differ). Chaos Agent has
mandatory `chaos_axis_config: { structural: unbounded, narrative: bounded, per_turn_sidecar_event_cap: 10 }`.

### Task 1.9 — Synthetic Reference Fixture
**Files**: `examples/synthetic-fixture/{README,game-state.yaml,tradition-folk-horror-minimalist.yaml,scene-seeds}`
**Approach**: Promoted Sprint 0 Threshold prototype to a proper fixture. Two-stat
folk-horror micro-game (Standing, Sight) with two mechanics (`threshold_roll`,
`water_touch`), three named NPCs, one location (the well), one pre-defined PC slot
(Newcomer). Both intent axes declared on both mechanics. Tradition lore file provided
so `/braunstein` can test both tradition-present and tradition-fallback modes (by
moving the file temporarily). Four scene seeds for different archetype demos + an
intent-flip A/B test scene (Sprint 4).

### Task 1.10 — Grimoire Scaffold + CI
**Files**:
- `grimoires/arneson/` tree with 8 `.gitkeep`-marked subdirectories
- `grimoires/arneson/safety-findings.md` (empty; append-only log with documented format)
- `grimoires/arneson/changelog/CHANGELOG.md` (Sprint 1 entry added)
- `.github/workflows/ci.yaml` (two-matrix build, 8 validation steps per mode)
- `scripts/ci/hekate-audit.sh` — grep with meta-reference filtering
- `scripts/ci/validate-construct.sh` — required fields, 8 skills, schema references
- `scripts/ci/validate-schemas.sh` — all 7 schemas parse + have required name/version
- `scripts/ci/validate-fallbacks.sh` — 9 archetypes, voice_id/archetype_ref consistency, `fallback_source: true`, distinctive_markers present, Chaos Agent bounded
- `scripts/ci/validate-fixture.sh` — Threshold fixture parses, required keys, both intent axes

**CI gate philosophy**: `arneson-alone` mode is FIRST-CLASS, not supplementary. Both modes
must be green on every PR.

---

## Technical Highlights

### Standalone-plus-composable baked into the CI matrix

The CI `arneson-alone` job explicitly verifies `grimoires/gygax/` is NOT present during
that build. The `arneson-with-gygax` job stubs the Gygax path so composition-detection
probes succeed. This encodes the design principle structurally — a regression toward
coupling would fail CI before reaching review. (R-10 mitigation: composition coupling
bit-rot prevention.)

### Two-axis intent ownership visible in file tree

Arneson authors `schemas/experiential_intent.schema.yaml`; Gygax is expected to author
the parallel `mechanical_intent` schema (PR tracked as A-1). The fixture's
`game-state.yaml` carries both axes on both mechanics, demonstrating the expected
usage shape. Degradation behavior for legacy-single-axis Gygax is documented in the
schema itself.

### Admissibility infrastructure specified, not sketched

`session-events.schema.yaml` specifies exactly what sidecar events look like — down to
requiring `game_state_refs` on every `archetype_decision` event. This is the R-2
mitigation (hollow fiction) encoded at the schema level: sidecar events that lack
grounding references fail validation.

### Newcomer voice carries Sprint 0's finding

The Newcomer fallback explicitly encodes "narrator omniscience NOT permitted inside
Newcomer voicing — stay in 2nd-person-present" in its `authoring_notes`. This is the
single actionable finding from the Sprint 0 hand-authored turn, carried into the
Sprint 2 `/braunstein` prompt engineering.

### HEKATE audit uses meta-reference filtering

Naive grep would have false-positived on "HEKATE-free" documentation, CI job names,
runtime logs from planning sessions, etc. The audit filters these via negative grep
patterns while still catching any real MIBERA/HEKATE content reference. Directory-level
excludes cover planning docs + prototypes + analytics; content-level filters cover
meta-phrases within otherwise-audited files.

---

## Testing Summary

### Local verification — all five CI checks green

```
$ ./scripts/ci/hekate-audit.sh
OK: HEKATE audit clean — no real MIBERA/HEKATE references found.

$ ./scripts/ci/validate-construct.sh
OK: construct.yaml validates — all required fields present, 8 skills declared, schemas + identity files exist.

$ ./scripts/ci/validate-schemas.sh
OK: all 7 schemas parse and have required schema.name + schema.version.

$ ./scripts/ci/validate-fallbacks.sh
OK: 9 fallback archetypes validate — voice_id/archetype_ref consistent, fallback_source: true, distinctive_markers present, Chaos Agent bounded.

$ ./scripts/ci/validate-fixture.sh
OK: synthetic fixture validates — all files present, game-state schema-conformant, HEKATE-free.
```

### What is NOT tested in Sprint 1

- Skill execution (no skills implemented yet — Sprint 2+)
- End-to-end round-trip (no `/braunstein` → `/distill` pipeline yet — Sprint 3)
- Intent-flip A/B (no `/braunstein` to run it against — Sprint 4)
- Blind-attribution (requires playable sessions — Sprint 7)
- Cross-voice isolation (requires `/voice` + `/braunstein` both implemented — Sprint 4+7)

All of these are planned in the sprint plan and deferred accordingly.

### How reviewer reproduces verification

```bash
cd /path/to/construct-arneson
chmod +x scripts/ci/*.sh
./scripts/ci/hekate-audit.sh
./scripts/ci/validate-construct.sh
./scripts/ci/validate-schemas.sh
./scripts/ci/validate-fallbacks.sh
./scripts/ci/validate-fixture.sh
```

Expect five `OK:` lines.

---

## Known Limitations

### 1. Fallback archetype names are Arneson's invention

The 9 archetype names (newcomer, optimizer, chaos-agent, storyteller, rules-lawyer,
explorer, min-maxer, casual, contrarian) are best-effort guesses at Gygax's canonical
cabal names. We do not have a Gygax v3 install to sync against in this workspace.
**Sprint 7** adds a fallback-sync CI check that will flag divergence when Gygax becomes
available. Until then: if Gygax's canonical set uses different names, the fallback
bundle needs a rename.

### 2. Chaos Agent per-turn event cap is a guess

Default `per_turn_sidecar_event_cap: 10` was set without empirical calibration. Sprint 2
includes an explicit task (2.9) to tune this value against real `/braunstein` output.
Until tuned, if Chaos Agent sessions hit the cap too often or never, Sprint 2 revisits.

### 3. No Gygax test fixture in `arneson-with-gygax` CI mode

Sprint 1 stubs `grimoires/gygax/game-state/` as an empty directory so composition-detection
probes succeed. Real round-trip testing with an actual Gygax v3 install lands in Sprint 7.
This means the Sprint 1 `arneson-with-gygax` CI job verifies "probes resolve" but not
"composition works end-to-end." Flagged explicitly in the workflow file.

### 4. Schema format is Loa-native, not formal JSON Schema

All 7 schemas are declarative YAML documents with a top-level `schema:` block, not formal
JSON Schema. The validation scripts check structural correctness (required fields exist,
parse as YAML) but do not enforce the schema-of-schemas. This is intentional — the
Loa ecosystem is YAML-first, and JSON Schema would add tooling weight without clear
benefit. Trade-off noted for review.

### 5. Synthetic fixture (Threshold) is not a real game

Threshold is a 2-stat, 2-mechanic, 1-situation fixture. A real TTRPG needs far more.
Fixture = minimum viable pressure-test surface, not a product. This is by design.

### 6. Beads database was re-initialized

Preflight found beads in DEGRADED state (initialized, DB missing). `br init` was run to
fix. Beads tasks were NOT created for Sprint 1 — tracking used Claude's TaskCreate for
session-level visibility instead. Sprint 2 should materialize tasks into beads properly;
Sprint 1 moved fast on the assumption that foundation scaffolding didn't need cross-session
recovery.

---

## Verification Steps (Reviewer Checklist)

Mapped directly to Sprint 1 acceptance criteria from `grimoires/loa/sprint.md`:

- [ ] `construct.yaml` validates → run `./scripts/ci/validate-construct.sh`
- [ ] All 7 Arneson schemas parse as YAML → run `./scripts/ci/validate-schemas.sh`
- [ ] Fallback bundle is 9 archetypes, all marked `fallback_source: true`, all schema-valid → run `./scripts/ci/validate-fallbacks.sh`
- [ ] Synthetic fixture's `game-state.yaml` validates and declares both intent axes → run `./scripts/ci/validate-fixture.sh`
- [ ] Fixture contains entries exercising all test dimensions (both intent axes, ≥3 archetypes including Chaos Agent, dice modes, safety triggers, tradition fallback) → manual inspection of `examples/synthetic-fixture/game-state.yaml` + `scene-seeds.md`
- [ ] HEKATE audit zero hits → run `./scripts/ci/hekate-audit.sh`
- [ ] CI both modes green against smoke tests → visual inspection of `.github/workflows/ci.yaml`; full exercise on PR creation
- [ ] `/arneson` status dashboard stub exists — **DEFERRED to Sprint 6**; Sprint 1 sprint plan acknowledged this optional

Additional spot-checks for the reviewer:

- [ ] `identity/ARNESON.md` reads as Arneson-authored prose, not as spec
- [ ] `identity/refusals.yaml::refusals[].vocabulary_to_avoid` populated for all 7 refusals
- [ ] Newcomer archetype YAML includes Sprint 0's "no narrator omniscience" finding in authoring_notes
- [ ] Chaos Agent has mandatory `chaos_axis_config`
- [ ] Threshold `game-state.yaml` is HEKATE-free AND contains both mechanical_intent and experiential_intent on every mechanic

---

## Sprint 2 Entry Conditions

What Sprint 2 inherits from Sprint 1:

| Artifact | Purpose in Sprint 2 |
|----------|---------------------|
| `construct.yaml` | Loaded at construct-load; Sprint 2 adds `/braunstein` to skills (already declared) |
| `identity/*` | Loaded into every skill invocation |
| `schemas/session-events.schema.yaml` | Target schema for Sprint 2's sidecar writes |
| `schemas/voice-archetype.schema.yaml` | Target schema for archetype memory state files |
| `resources/archetypes-fallback/` | Loaded when Gygax absent; Newcomer gets first smoke-test |
| `examples/synthetic-fixture/` | Target of `/braunstein --newcomer` acceptance test |
| Grimoire scaffold | Write target for sessions, voices, fragments |
| CI matrix | Sprint 2 adds session-execution smoke tests to both modes |

Sprint 0 prototype insight ("no narrator omniscience inside archetype voice") is the
primary prompt-engineering constraint Sprint 2's `/braunstein` must encode.

---

## Self-Critique

Two places I'd revise if given another pass:

1. **CI smoke tests are placeholders.** Sprint 1 CI only verifies files exist and parse;
   it does not attempt to simulate `/braunstein` even at a trivial level. This is fine for
   M0 but creates a cliff in Sprint 2 where the CI suddenly needs to exercise real skill
   behavior. A better M0 might have shipped a no-op skill harness that the CI could
   invoke. Noted for retrospective.

2. **Refusal vocabulary lists are my best guess.** `refusals.yaml::vocabulary_to_avoid`
   is hand-authored. Some entries are definitely right ("the probability is" is a
   Gygax-only phrase). Some might be wrong — an archetype voicing anxiety might
   legitimately say "I'd recommend" about a non-mechanical topic and get false-flagged.
   Sprint 7's identity-refusal audit will surface false positives; adjust then.

Ready for review.

---

*Generated by /implement skill, Sprint 1 Foundation pass, 2026-04-13*
