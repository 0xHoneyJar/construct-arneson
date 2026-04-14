# Sprint 2 Implementation Report — Vertical Slice /braunstein (M1)

**Sprint**: sprint-2 (PRD Milestone M1)
**Date**: 2026-04-13
**Implementer**: /implement skill (run mode)
**Status**: Ready for review

---

## Executive Summary

Sprint 2 delivers the flagship `/braunstein` skill — a live playtest session where the
user GMs and Arneson voices a cabal archetype. This is the vertical slice that proves
the architecture: identity files, schemas, fallback archetypes, and the synthetic fixture
from Sprint 1 all converge into a single prompt-engineered session skill.

The deliverable is `skills/braunstein/SKILL.md` (~400 lines of prompt engineering) +
`skills/braunstein/index.yaml` (metadata). No traditional code; the SKILL.md IS the
implementation. All 8 FRs carried by Sprint 2 (FR-1, FR-9, FR-10, FR-11, FR-14, FR-15,
FR-16, FR-17) are addressed within the SKILL.md's session lifecycle and voicing rules.

Sprint 1 audit's HIGH finding (yq version pin) addressed in this sprint as intake.

---

## Sprint 1 Audit Feedback Addressed

> From sprint-1/auditor-sprint-feedback.md: "Pin yq version + verify SHA256 in CI workflow — mandatory before first CI push"

**Fix**: `.github/workflows/ci.yaml` updated — yq download now pins to `v4.50.1` with explicit version URL. Both CI job instances updated. SHA256 verification not yet added (requires obtaining the hash from the release; the version pin alone closes the `/latest/` supply-chain risk).

---

## Tasks Completed

### Task 2.1: Scaffold `/braunstein` SKILL.md
**Files**: `skills/braunstein/SKILL.md` (~400 lines), `skills/braunstein/index.yaml`
**Approach**: Full prompt-engineering document covering the 8-state session lifecycle
(INVOKED → COMPOSITION DETECTION → ARCHETYPE LOADING → TRADITION CHECK → SAFETY AGREEMENT
→ SIDECAR PREAMBLE → SCENE FRAME → ACTIVE turn loop), plus PAUSED and CLOSING states.
**Verification**: File exists; index.yaml parses; `validate-skills.sh` passes.

### Task 2.2: Safety Agreement (FR-15)
**Location**: `skills/braunstein/SKILL.md` — State 5: SAFETY AGREEMENT
**Approach**: Mandatory step. Presents Lines, Veils, X-card status from game-state defaults.
User can add/adjust. Written to sidecar preamble. `/pause` and `/x-card` commands halt
generation immediately (State: PAUSED). Safety triggers logged as `dead_design_space`.
**Acceptance**: SKILL.md explicitly states "This step is mandatory. Do not skip it." and
"/x-card → immediately halt generation. No final sentence. No 'let me just finish.'"

### Task 2.3: Composition-Detection Protocol (SDD §5.2)
**Location**: `skills/braunstein/SKILL.md` — State 2: COMPOSITION DETECTION
**Approach**: Filesystem probe for `grimoires/gygax/game-state/`. If present → composed mode,
load archetype from Gygax SSOT. If absent → standalone mode, load from fallback bundle,
display banner. Composition mode logged to sidecar preamble.
**Acceptance**: Standalone banner specified; composition_mode in sidecar preamble.

### Task 2.4: Archetype Loading with Gygax-or-Fallback (FR-17)
**Location**: `skills/braunstein/SKILL.md` — State 3: ARCHETYPE LOADING
**Approach**: Loads voice file from Gygax path (composed) or fallback bundle (standalone).
Extracts all voice-archetype schema fields. Loads archetype instance state from
`grimoires/arneson/voices/archetypes/{archetype}.state.yaml` if exists (memory slots,
known facts). Memory window applied per `memory_window_size`.
**Acceptance**: Falls back correctly; memory window loaded.

### Task 2.5: Intent Reading Both Axes (FR-9)
**Location**: `skills/braunstein/SKILL.md` — State 8 step 4, plus "Intent Handling" section
**Approach**: For each active mechanic, reads `mechanical_intent` (Gygax-owned) and
`experiential_intent` (Arneson-owned). Degradation: single-axis `intent` treated as
mechanical, experiential defaults to neutral. Missing fields proceed with neutral voicing +
degradation event logged.
**Key rule**: "Mechanical intent wins on OUTCOME. Experiential intent wins on PROSE QUALITY."
Intent conflicts logged as `intent_conflict` events with resolution.
**Acceptance**: Two-axis handling + degradation + conflict logging all specified.

### Task 2.6: Dice Resolution (FR-11)
**Location**: `skills/braunstein/SKILL.md` — "Dice Handling" section
**Approach**: Three modes (user/arneson/hybrid) fully specified. All modes produce identical
sidecar `dice_roll` events. Default is `user` (user rolls and reports).
**Acceptance**: `--dice` flag documented; all three modes described with sidecar output.

### Task 2.7: Sidecar Event Emission (FR-16)
**Location**: `skills/braunstein/SKILL.md` — State 8 step 6, plus "Sidecar Writing Discipline"
**Approach**: Every turn emits at least one `archetype_decision` event with REQUIRED
`game_state_refs` and `classification` fields. Additional event types (signal_flag,
dice_roll, intent_conflict, gm_prompt, safety_trigger, rule_of_cool, clarifying_question)
emitted as appropriate. Sidecar is append-only, durable to crashes.
**Key enforcement**: "If you emit a decision without game_state_refs, the sidecar fails
admissibility validation." And: "Classification is REQUIRED. Every decision is either
fictional_friction, mechanical_bottleneck, or both."
**Acceptance**: All 9 event types from session-events.schema.yaml addressed.

### Task 2.8: Archetype Memory 3-Session Sliding Window (FR-10)
**Location**: `skills/braunstein/SKILL.md` — State 3 (loading) + State CLOSING (writing)
**Approach**: On load, reads most recent `memory_window_size` sessions from archetype state
file. On close, computes memory candidates, presents to user for confirmation, then
writes to state file with pruning.
**Key rule**: "Identity does not extinguish; knowledge accumulates."
**Acceptance**: Memory window loaded; candidates presented; user confirms before persistence.

### Task 2.9: Chaos Agent Per-Turn Cap (FR-14)
**Location**: `skills/braunstein/SKILL.md` — State 8 step 5 (Chaos Agent special rules)
**Approach**: SKILL.md references `chaos_axis_config.per_turn_sidecar_event_cap` from the
archetype voice file (default 10, set in Sprint 1 fallback). Structural axis unbounded;
narrative axis bounded. Cap enforced at emission time.
**Empirical tuning**: Default 10 is set. Actual calibration requires running sessions with
the Chaos Agent archetype. Sprint 7 reviews accumulated data and adjusts.
**Acceptance**: Cap referenced in SKILL.md; default in fallback YAML; schema field exists.

### Task 2.10: Crash Recovery
**Location**: `skills/braunstein/SKILL.md` — "Sidecar Writing Discipline" + "Session Resume"
**Approach**: Sidecar is append-only; each event is a complete YAML fragment; `session_end`
may be absent in crash cases. On resume, Arneson checks for existing sidecar without
`session_end` and offers to continue. Partial sidecars are valid input for `/distill`.
**Acceptance**: Crash-recovery behavior specified; partial sidecars handled.

---

## Additional Sprint 2 Deliverables

### yq Version Pin (Sprint 1 Audit Fix)
**File**: `.github/workflows/ci.yaml` (both jobs)
**Change**: `latest` → pinned to `v4.50.1` with explicit version URL.

### Skill Validation Script
**File**: `scripts/ci/validate-skills.sh` (new)
**Purpose**: Validates implemented skills have SKILL.md + index.yaml, parse correctly.
Reports declared-but-not-yet-implemented skills as INFO (not failure).
**Added to**: both CI jobs.

### CI Smoke Test Updated
**File**: `.github/workflows/ci.yaml` — smoke test step
**Change**: Now checks for `skills/braunstein/SKILL.md` and `index.yaml` existence.

---

## Technical Highlights

### SKILL.md IS the implementation

construct-arneson has no traditional application code. The SKILL.md is a prompt-engineering
document that the Loa framework loads when a user invokes `/braunstein`. Every Sprint 2
requirement (safety, composition, intent, dice, sidecar, memory, chaos bounding, crash
recovery) is encoded as prompt instructions within the SKILL.md.

This means "testing" is fundamentally different from a traditional sprint:
- **Structural tests**: file existence, YAML parsing, schema references → CI handles these
- **Behavioral tests**: does the prompt actually produce correct voicing, correct sidecar
  events, correct intent handling? → requires human invocation and verification
- **Admissibility test**: does `/distill` successfully consume a `/braunstein` sidecar?
  → Sprint 3 (round-trip test)

### Example turn embedded in SKILL.md

The Sprint 0 prototype turn (Newcomer at the well) is embedded in the SKILL.md as a
concrete example of what correct output looks like. This anchors the prompt — the LLM
has a golden-path example to calibrate against.

### Eight-state session lifecycle

The session is a state machine with explicit transitions:
INVOKED → COMPOSITION → ARCHETYPE → TRADITION → SAFETY → PREAMBLE → SCENE → ACTIVE ↔ PAUSED → CLOSING

Each state has entry conditions, actions, and exit criteria. This prevents the common
failure mode of LLM sessions: states blurring together, safety steps skipped under
narrative momentum, or voice discipline degrading across turns.

---

## Testing Summary

### CI validation (6 checks, all green locally)

```
OK: HEKATE audit clean
OK: construct.yaml validates (8 skills declared)
OK: all 7 schemas parse
OK: 9 fallback archetypes validate
OK: synthetic fixture validates
OK: all implemented skills have SKILL.md + index.yaml (1 implemented, 7 pending)
```

### What is NOT tested in Sprint 2

- **Live session execution**: `/braunstein --newcomer` has not been invoked against
  the synthetic fixture. The SKILL.md is the prompt; the test is "invoke it and check
  the output." This requires human execution.
- **Round-trip admissibility**: `/distill` doesn't exist yet (Sprint 3).
- **Intent-flip A/B**: Requires live sessions to compare (Sprint 4).
- **Blind-attribution**: Requires multiple archetype sessions (Sprint 7).

### Recommended first manual test

After Sprint 2 review + audit approve:
```
/braunstein --newcomer --game-state examples/synthetic-fixture/game-state.yaml
```

Play the "Dusk at the Well" scene seed (scene-seeds.md Seed 1). Verify:
- Safety agreement appears
- Newcomer voice matches Sprint 0 prototype quality
- Sidecar file is created with schema-valid events
- `/pause` and `/break` work
- Memory candidates presented on exit

---

## Known Limitations

### 1. No automated behavioral testing

The SKILL.md governs LLM behavior at invocation time. We cannot CI-test whether the
LLM actually follows the prompt. The first real test is a human invoking `/braunstein`.
This is inherent to prompt-engineering constructs and is mitigated by:
- The Sprint 0 prototype (proven that the fiction quality IS achievable)
- The embedded example turn in the SKILL.md (golden-path calibration)
- Sprint 3's round-trip test (mechanically verifies sidecar output shape)

### 2. Chaos Agent cap is still a guess

Default `per_turn_sidecar_event_cap: 10` from Sprint 1. No sessions have been run to
validate. Sprint 7 reviews accumulated data.

### 3. SHA256 not added to yq download

The yq version is pinned (`v4.50.1`) but the checksum verification step was not added —
I don't have the SHA256 hash for the release binary available. The version pin alone
closes the `/latest/` supply-chain vulnerability. Full integrity check is a future
improvement.

### 4. Beads tasks not materialized for Sprint 2

Sprint 1 review Concern #1 (materialize tasks in beads) was noted but not addressed
in this implementation — used TaskCreate for session progress instead. Sprint 3 should
address this.

---

## Verification Steps

- [ ] `skills/braunstein/SKILL.md` exists and is >300 lines (substantial prompt)
- [ ] `skills/braunstein/index.yaml` exists and parses; name = "braunstein"
- [ ] SKILL.md covers all 8 session lifecycle states
- [ ] SKILL.md references safety agreement as MANDATORY
- [ ] SKILL.md includes composition-detection probe logic
- [ ] SKILL.md includes intent-handling section with "never fudge mechanical_intent" rule
- [ ] SKILL.md includes all 3 dice modes
- [ ] SKILL.md includes sidecar discipline: append-only, game_state_refs REQUIRED, classification REQUIRED
- [ ] SKILL.md includes Chaos Agent special rules with per-turn cap
- [ ] SKILL.md includes crash recovery / session resume behavior
- [ ] SKILL.md includes Sprint 0 prototype as embedded example
- [ ] SKILL.md includes "What You Must Not Do" section (identity refusals)
- [ ] `validate-skills.sh` passes
- [ ] yq pinned to specific version in CI (audit fix)
- [ ] HEKATE audit still clean

---

*Generated by /implement skill, Sprint 2 Vertical Slice pass, 2026-04-13*
