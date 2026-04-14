# Product Requirements Document: construct-arneson v1

**Version:** 1.0
**Date:** 2026-04-13
**Author:** PRD Architect Agent (/plan-and-analyze)
**Status:** Draft

> **Sources used across this document:**
> - `grimoires/loa/context/00-READ-FIRST-proposal-issue-3.md` (GH issue 0xHoneyJar/construct-gygax#3)
> - `grimoires/loa/context/arneson-v1-concept.md`
> - `grimoires/loa/NOTES.md` (decision log, teammate feedback)
> - /plan-and-analyze discovery interview, 2026-04-13 (Phases 1–7)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Goals & Success Metrics](#goals--success-metrics)
4. [User Personas & Use Cases](#user-personas--use-cases)
5. [Functional Requirements](#functional-requirements)
6. [Non-Functional Requirements](#non-functional-requirements)
7. [User Experience](#user-experience)
8. [Technical Considerations](#technical-considerations)
9. [Scope & Prioritization](#scope--prioritization)
10. [Success Criteria](#success-criteria)
11. [Risks & Mitigation](#risks--mitigation)
12. [Milestones](#milestones)
13. [Appendix](#appendix)

---

## Executive Summary

**construct-arneson v1** is a Loa-framework skill-pack construct for tabletop-RPG designers. It is the narrative-generation companion to [construct-gygax](https://github.com/0xHoneyJar/construct-gygax) — named for Dave Arneson (Blackmoor, 1971), whose historical complementarity with Gary Gygax the construct pair deliberately mirrors. Arneson embraces exactly what Gygax refuses: fiction generation, NPC voicing, scene framing, live playtesting, and improvisational GMing.

The construct's identity is **data-emitting fiction**, not merely fiction. Every session transcript is instrumented with a structured sidecar and distillable into a Gygax-ingestible digest, making narrative play *admissible as evidence* in structural re-analysis. This closes the design-iteration loop at the tool level: Gygax analyzes → designer changes → Arneson plays the change → Gygax re-analyzes the transcript → next iteration.

v1 ships **eight skills** (`/braunstein`, `/voice`, `/scene`, `/narrate`, `/improvise`, `/arneson`, `/fragment`, `/distill`), with the flagship `/braunstein` proving admissibility end-to-end against a synthetic neutral reference fixture. The construct works **standalone** (without Gygax installed) and is **amplified** by Gygax composition when present.

> **Sources**: issue-3:37-47, concept:1-19, Phase 1–6 synthesis

---

## Problem Statement

### The Problem

TTRPG designers have no tool that grounds *fictional play* in the same persistent game-state used for *structural analysis*. Spreadsheets and probability scripts model mechanics; LLM chats improvise fiction. Neither couples to the other. Neither respects designer intent as a load-bearing input.

The sibling construct [Gygax v3](https://github.com/0xHoneyJar/construct-gygax) handles the structural half with a deliberately narrow identity — it refuses to write fiction, refuses to voice characters, refuses final creative decisions. Those refusals are *load-bearing*: they are what make Gygax trustworthy as an analyst.

> From issue-3:43-46: *"Gygax's identity is load-bearing. Its persona explicitly refuses to generate narrative prose, voice characters, or make final creative decisions. These refusals are what make Gygax trustworthy as an analyst... Adding fiction-generation capabilities inside Gygax would weaken that contract."*

The cleanest architectural answer is an inverse-identity companion whose refusals are equally load-bearing in the opposite direction.

### User Pain Points

- **Design-and-play rupture**: Designers iterate mechanics in spreadsheets, then test the resulting *feel* in separate LLM chats with no persistent grounding. Findings from play do not round-trip back into analysis.
- **Hollow LLM fiction**: General-purpose LLMs improvise plausibly but ignore game-state — they "fudge" outcomes to serve narrative satisfaction, which destroys admissibility for design analysis.
- **Intent erasure**: Designers flag mechanics with deliberate intent ("lethal by design," "heroic," "desperate"). Current fiction tools ignore these signals and smooth them away.
- **Post-hoc-only signal capture**: Gygax v3's cabal captures experience signals only from analytical walkthroughs, not from the moment-of-play where they actually emerge.
- **Voice inconsistency**: A designer workshopping an NPC across multiple sessions has no tool that preserves that NPC's voice state; every session starts from zero.

### Current State

Designers cobble together spreadsheets + generic LLM chats + hand-written session notes. The three don't compose. Evidence from play is anecdotal; evidence from analysis is structural; they rarely meet.

### Desired State

A designer can move fluidly between structural analysis (Gygax) and narrative play (Arneson) on a *single* persistent game-state. Transcripts produced in play are mechanically instrumented and feed directly back into analysis. Intent (both mechanical and experiential) is respected across the boundary. Safety triggers become design findings, not just social events.

> **Sources**: issue-3:43-102, concept:19-34, concept:129-133, Phase 1–2 synthesis

---

## Goals & Success Metrics

### Primary Goals

| ID | Goal | Measurement | Validation Method |
|----|------|-------------|-------------------|
| G-1 | **Admissibility**: A `/braunstein` transcript is trustworthy enough to be cited as evidence in Gygax re-analysis. | Binary: Gygax's `/cabal --from-session` can ingest a `/distill`ed Arneson transcript without manual reformatting. | Round-trip integration test against synthetic fixture. |
| G-2 | **Identity contract**: Arneson refuses structural analysis, probability math, mechanical recommendations, and pattern-matching against anti-patterns. | Audit: no refusal-target vocabulary appears in output during acceptance scenarios. | Identity audit during `/audit-sprint`, modeled on Gygax's refusal audit. |
| G-3 | **Intent fidelity**: When `mechanical_intent` or `experiential_intent` is non-default, Arneson's voicing shifts accordingly *without prompt-tuning*. | Comparative: same game-state with intent flipped (Lethal → Heroic) produces materially different voicing on the same roll outcome. | Paired acceptance test — A/B intent transcripts, blind-read differentiated. |
| G-4 | **Standalone viability**: Arneson produces useful output when Gygax is not installed. | Binary: all eight skills complete their primary task with Gygax paths absent. | CI matrix: `arneson-alone` and `arneson-with-gygax` both green. |
| G-5 | **Composition amplification**: When Gygax is installed, Arneson's outputs feed Gygax's analyzers and vice versa. | Binary: bidirectional round-trip (scry-fork → braunstein → distill → cabal → re-scry). | End-to-end composition test in CI. |
| G-6 | **Archetype distinctness**: ≥3 archetypes produce voices identifiable by blind attribution. | Designer (or rater) correctly attributes transcript excerpts to archetypes at rate clearly above chance. | Blind-attribution protocol documented in acceptance tests. |

### Key Performance Indicators (KPIs)

This is a tool, not a SaaS product — traditional user-engagement KPIs do not apply. The KPIs are build-completion indicators tied to goals.

| Metric | Baseline | Target | Source Goal |
|--------|----------|--------|-------------|
| Skills implemented at v1 | 0 | 8 | — |
| Round-trip `/braunstein` → `/distill` → Gygax `/cabal --from-session` passes | 0 | 1 | G-1 |
| Archetypes voiced with distinct speech patterns | 0 | ≥3 (target: all 9) | G-6 |
| Blind-attribution accuracy for archetype-to-transcript | chance | > chance significantly | G-6 |
| CI modes green | 0/2 | 2/2 (alone + composed) | G-4, G-5 |
| Identity-refusal audit violations in acceptance scenarios | — | 0 | G-2 |

### Constraints

- **Timeline**: Quality-driven, no fixed ship date. Ship when admissibility is real, not when the calendar says so. (Phase 2 decision.)
- **No MIBERA: HEKATE**: HEKATE is private/upstream. Zero references in Arneson code, examples, tests, or docs. v1 ships HEKATE-free for community shippability. (Phase 6 user directive.)
- **Standalone-plus-composable**: Neither construct may hard-depend on the other. (Phase 4 design principle.)
- **Designer-only UX for v1**: No direct player-at-table interaction surface. (Phase 3 decision.)

> **Sources**: issue-3:192-200 (original success criteria, reframed), Phase 2 (admissibility), Phase 3 (audience + player scope), Phase 4 (teammate feedback), Phase 6 (HEKATE exclusion, build ordering)

---

## User Personas & Use Cases

### Primary Persona: The TTRPG Designer

**Demographics:**
- Role: Designer of tabletop RPGs — anything from one-page dungeon-crawlers to multi-year campaign systems
- Technical proficiency: comfortable with markdown, YAML, git, and CLI tools (Loa-framework literate)
- Scope: any designer using a Gygax-supported tradition from day one of v1 (Phase 3 decision: "Gygax community from day one")

**Goals:**
- Close the loop between structural analysis and experiential playtesting
- Preserve NPC voice state across design sessions
- Test mechanical changes *fictionally* (not only numerically) before committing to them
- Generate design findings from play, not only from analysis

**Behaviors:**
- Iterates on a single game design over months or years, returning to the same game-state
- Uses Gygax for probability math, cabal archetype analysis, and cross-system comparison
- Flags mechanics with intent (both axes, once v1 ships)
- Reads sidecar data to identify friction hotspots

**Pain Points:**
- (See Problem Statement → User Pain Points)

### Secondary Persona: The Gygax Analyzer (non-human)

The sibling Gygax v3 construct itself, treated as a stakeholder because its analyzers (`/cabal --from-session`, future `/scry --from-session`, etc.) consume Arneson's outputs. Arneson's API shape must satisfy Gygax's ingestion contracts.

### Use Cases

#### UC-1: Closed-loop design iteration
**Actor:** Designer (with Gygax + Arneson both installed)
**Preconditions:** Game-state YAML exists; Gygax v3 installed; Arneson installed.
**Flow:**
1. Designer runs Gygax `/cabal` to analyze the current game-state — receives structural findings.
2. Designer edits a mechanic in response.
3. Designer runs `/braunstein --newcomer` against the updated game-state; plays the scene (Arneson voices the Newcomer archetype; designer GMs).
4. Arneson writes `{session}.md` (prose transcript) + `{session}.events.yaml` (structured sidecar) atomically during the session.
5. Designer runs `/distill {session}` → produces a Gygax-ingestible digest.
6. Designer runs Gygax `/cabal --from-session {digest}` — receives experiential findings reflecting the change.
7. Loop: designer iterates.

**Postconditions:** Session and digest persist in `grimoires/arneson/sessions/` and `grimoires/arneson/digests/`. Game-state unchanged by default.
**Acceptance Criteria:**
- [ ] Digest parses cleanly in Gygax's `/cabal --from-session` without manual reformatting
- [ ] Intent changes between steps 2–3 visibly affect step 3's voicing
- [ ] Sidecar events correctly distinguish "fictional friction" from "mechanical bottleneck"

#### UC-2: Standalone playtest (no Gygax)
**Actor:** Designer (Arneson only)
**Preconditions:** Game-state YAML exists; Arneson installed; Gygax NOT installed.
**Flow:**
1. Arneson detects absence of `grimoires/gygax/`; uses its fallback archetype bundle (Arneson-authored mirror of Gygax's 9 archetypes, marked as fallback).
2. Designer runs `/braunstein --newcomer`; plays the scene.
3. Arneson writes prose transcript + sidecar.
4. `/distill` produces a self-contained digest (consumable by any reader, not just Gygax).

**Postconditions:** Digest is useful on its own — readable, structured, complete.
**Acceptance Criteria:**
- [ ] All paths execute without reference to Gygax files
- [ ] Output format is self-describing (no external schema required to read)
- [ ] Banner in output clearly notes standalone mode

#### UC-3: NPC voice workshop
**Actor:** Designer
**Preconditions:** Optional existing NPC state file (`grimoires/arneson/voices/npcs/{id}.yaml`); session-level safety agreement.
**Flow:**
1. Designer runs `/voice {npc-id}` (or new-id; creates fresh NPC).
2. Arneson embodies the NPC for workshop-style dialogue; holds character until session ends.
3. NPC state evolves (voice parameters, memory, known facts); persists to `voices/npcs/{id}.yaml` on exit.

**Postconditions:** NPC voice state is preserved for next session.
**Acceptance Criteria:**
- [ ] NPC stays in character for the full session
- [ ] State diff is legible on exit; designer can review before committing
- [ ] Re-invoking `/voice {npc-id}` reloads the voice with continuity

#### UC-4: Scry-fork playtest
**Actor:** Designer (Gygax + Arneson)
**Preconditions:** Gygax `/scry` fork exists at an alternate game-state.
**Flow:**
1. Designer runs `/scry "what if threshold was 4?"` (Gygax) — produces forked game-state.
2. Designer runs `/braunstein --fork threshold-4 --newcomer` — plays the fork.
3. Designer reads both transcripts (base + fork) side by side to feel the change.
4. Optional: `/distill` both; Gygax cross-compares.

**Postconditions:** Designer has experiential evidence of the fork's effect.
**Acceptance Criteria:**
- [ ] `--fork` flag correctly loads the forked game-state
- [ ] Session transcript is tagged with fork identifier
- [ ] Digest makes the fork comparison legible to Gygax analyzers

#### UC-5: Setting fragment generation
**Actor:** Designer
**Preconditions:** Game-state with setting-context fields (or user-provided prompt).
**Flow:**
1. Designer runs `/fragment location` (or `/fragment faction`, etc.).
2. Arneson produces a one-shot setting fragment grounded in game-state.
3. Fragment saved to `grimoires/arneson/fragments/{date}-{scope}.md`.

**Postconditions:** Fragment is presentable, exportable, and tagged by scope.
**Acceptance Criteria:**
- [ ] Fragment references at least one game-state element verbatim (grounding check)
- [ ] Fragment respects tradition conventions when a tradition lore file is present
- [ ] Fragment flags itself as "improvised against structural-only context" when no tradition file is present

#### UC-6: GM-side design test
**Actor:** Designer
**Preconditions:** Playable game-state.
**Flow:**
1. Designer runs `/improvise --pc` (or with a named PC).
2. Arneson GMs; designer plays a PC.
3. Same sidecar + digest pipeline as `/braunstein`.

**Postconditions:** Transcript tests the GM-facing side of the design.
**Acceptance Criteria:**
- [ ] Arneson voices world and NPCs distinctly from each other and from archetypes
- [ ] Designer actions as PC are captured faithfully in the sidecar
- [ ] Rule-of-cool overrides (where Arneson-as-GM bent a rule for fiction) are flagged

> **Sources**: issue-3:68-102 (flows), concept:36-79 (composition), Phase 3 Q1-Q2 (audience), Phase 4 (teammate feedback), Phase 5 decisions

---

## Functional Requirements

### FR-1: `/braunstein` — Flagship Live Playtest
**Priority:** Must Have (P0)
**Description:** Interactive session skill. User GMs; Arneson plays an archetype (from Gygax's cabal definitions, or Arneson's fallback bundle) as an actual character. Dialogue, in-character reactions, dice rolls (per FR-6), and real-time sidecar emission.

**Acceptance Criteria:**
- [ ] Opens with a session safety agreement (per FR-10)
- [ ] Loads archetype from Gygax's `identity/persona.yaml` when available; from Arneson fallback bundle otherwise
- [ ] Reads both `mechanical_intent` and `experiential_intent` fields from game-state
- [ ] Writes prose transcript to `grimoires/arneson/sessions/{date}-braunstein-{archetype}.md`
- [ ] Writes structured sidecar to `grimoires/arneson/sessions/{date}-braunstein-{archetype}.events.yaml`
- [ ] Sidecar events include: scene frames, dice rolls with context, archetype decisions with "why" grounding, signal flags, intent conflicts, GM prompts (`"I don't know how this mechanic resolves"`), safety triggers
- [ ] Each archetype decision includes a classification tag: `fictional_friction` or `mechanical_bottleneck` (or both)
- [ ] `--fork` flag supports scry-forked game-state
- [ ] Archetype-instance memory applies 3-session sliding window (per FR-8)
- [ ] Session is resumable — state written on any exit, including user interrupt

**Dependencies:** FR-6 (dice), FR-7 (intent), FR-8 (memory), FR-10 (safety), FR-11 (sidecar schema)

### FR-2: `/voice {npc-id}` — NPC Workshop
**Priority:** Must Have (P0)
**Description:** Embody a specific NPC for workshop-style dialogue. Arneson stays in character until session ends. NPC voice state evolves and persists.

**Acceptance Criteria:**
- [ ] Accepts existing npc-id OR fresh id (creates new NPC YAML)
- [ ] Opens with session safety agreement
- [ ] NPC state uses shared voice base schema + NPC-specific extensions (per FR-12)
- [ ] Holds character throughout session; leaving character requires explicit `/break` command
- [ ] On exit, displays state diff and asks for confirmation before persisting
- [ ] Persists to `grimoires/arneson/voices/npcs/{id}.yaml`
- [ ] Sidecar emission for substantial turns (voice drift moments, factual reveals, memory additions)

**Dependencies:** FR-10 (safety), FR-12 (voice schema)

### FR-3: `/scene` — Scene Generator
**Priority:** Must Have (P0)
**Description:** Generate a scene from a seed, oracle-table output, or user prompt. Produces opening situation, sensory detail, immediate stakes. One-shot by default; re-runnable with variation flags.

**Acceptance Criteria:**
- [ ] Accepts seed text, oracle result, or structured prompt
- [ ] References at least one game-state element verbatim (grounding check)
- [ ] Respects tradition conventions when a tradition lore file is present
- [ ] Output flags itself as "improvised against structural-only context" when no tradition match
- [ ] Writes to `grimoires/arneson/scenes/{date}-{scope}.md`
- [ ] Inherits project-level safety config (no per-invocation prompt)

**Dependencies:** FR-9 (tradition fallback), FR-10 (safety)

### FR-4: `/narrate` — Fiction-Mechanics-Fiction Primitive
**Priority:** Must Have (P0)
**Description:** When a mechanic fires, generate the "new fiction" that flows from it. Implements the PbtA-derived fiction-mechanics-fiction loop at the tooling level. The foundational primitive underneath `/braunstein`, `/voice`, `/scene`.

**Acceptance Criteria:**
- [ ] Accepts a mechanic outcome (roll result, triggered move, resource change, etc.) + game-state context
- [ ] Produces narration grounded in both `mechanical_intent` (what happened mechanically) and `experiential_intent` (how it should feel)
- [ ] Does not fudge: if `mechanical_intent: lethal`, narration does not soften the mechanical outcome to save a PC
- [ ] Returns structured output: prose + optional sidecar fragment (for callers like `/braunstein` to concatenate)
- [ ] One-shot by default; callable as a library primitive by other skills

**Dependencies:** FR-7 (intent)

### FR-5: `/improvise` — GM-Side Design Test
**Priority:** Must Have (P0)
**Description:** Inverse of `/braunstein`. Arneson GMs; user plays a PC. For testing the GM-facing side of a design.

**Acceptance Criteria:**
- [ ] Opens with session safety agreement
- [ ] Arneson voices world and NPCs; user inputs as PC
- [ ] Same sidecar + transcript pipeline as `/braunstein`
- [ ] Rule-of-cool overrides (Arneson bent a rule for fiction) flagged in sidecar as `rule_of_cool` events
- [ ] Clarifying questions from user (as PC or as designer-stepping-out) flagged as `clarifying_question` events
- [ ] Distinguishes its transcripts with mode tag (`mode: improvise` in sidecar preamble)

**Dependencies:** FR-1 (shares infrastructure)

### FR-6: `/arneson` — Status Dashboard
**Priority:** Must Have (P0)
**Description:** Status-only read skill. Lists active sessions, voiced NPCs, recent scenes, and campaign continuity state (archetype memory windows).

**Acceptance Criteria:**
- [ ] Reports Gygax composition state (detected / absent)
- [ ] Lists sessions with timestamps, mode, archetype/PC
- [ ] Lists NPC state files with last-edit timestamps
- [ ] Lists scene and fragment files
- [ ] Reports archetype memory windows (which archetypes have N/3 sessions in recent memory)
- [ ] Reports safety-findings count (if any)
- [ ] Read-only; writes nothing

**Dependencies:** none (reads from `grimoires/arneson/*`)

### FR-7: `/fragment` — Setting Material Generator
**Priority:** Must Have (P0)
**Description:** Generate setting material (locations, histories, factions, items). Low-effort, high-value for world-building.

**Acceptance Criteria:**
- [ ] Accepts scope argument: `location`, `faction`, `history`, `item`, or free-form
- [ ] References at least one game-state element (grounding check)
- [ ] Respects tradition conventions when available
- [ ] Writes to `grimoires/arneson/fragments/{date}-{scope}.md`
- [ ] Fragment can be injected back into game-state YAML via explicit user action (no auto-injection)

**Dependencies:** FR-9 (tradition fallback)

### FR-8: `/distill` — Session Compressor
**Priority:** Must Have (P0) — composition glue
**Description:** Post-playtest skill. Converts a session's prose transcript + structured sidecar into a Gygax-ingestible digest. Identifies every rule invocation, every rule-of-cool override, every clarifying question, every signal flag, every safety trigger.

**Acceptance Criteria:**
- [ ] Accepts session path (either `{session}.md` or sibling `.events.yaml`)
- [ ] Extracts: rule invocations (tagged by mechanic), rule-of-cool overrides, clarifying questions, signal flags (friction/bottleneck), safety triggers (as `dead_design_space` findings), intent conflicts
- [ ] Writes digest to `grimoires/arneson/digests/{session}.digest.yaml`
- [ ] Digest is self-describing (readable without Gygax installed)
- [ ] When Gygax is installed, digest format is schema-compatible with `/cabal --from-session` (binary round-trip test)
- [ ] When Gygax is absent, digest still compresses the session usefully (standalone success)

**Dependencies:** FR-1 (sidecar format contract)

### FR-9: Intent Interface (Two-Axis Schema)
**Priority:** Must Have (P0) — composition contract
**Description:** Formal schema for intent blocks in game-state YAML. Two axes: `mechanical_intent` (owned by Gygax) and `experiential_intent` (owned by Arneson).

**Acceptance Criteria:**
- [ ] Arneson ships `schemas/experiential_intent.schema.yaml` with full field definitions and controlled vocabulary
- [ ] Arneson reads both axes when present; gracefully degrades when only one is present
- [ ] Degradation path: if only single-axis `intent` present (pre-split Gygax), Arneson treats it as `mechanical_intent` and defaults `experiential_intent` to neutral
- [ ] A file Gygax-side PR is authored to extend Gygax's schema to split single-axis `intent` into `mechanical_intent` + `experiential_intent` (tracked as external dependency)
- [ ] Changing only `experiential_intent` (same mechanical_intent) produces materially different voicing in acceptance test (G-3 validation)

**Dependencies:** external Gygax schema PR (tracked as assumption)

### FR-10: Archetype Memory (3-Session Sliding Window)
**Priority:** Must Have (P0)
**Description:** Archetype-instances carry memory across sessions within a capped sliding window.

**Acceptance Criteria:**
- [ ] Most recent 3 sessions inform archetype behavior on subsequent invocations
- [ ] Archetype identity never fully extinguishes (the Newcomer stays a Newcomer regardless of memory)
- [ ] Memory lives in `grimoires/arneson/voices/archetypes/{archetype}.state.yaml` (separate from the SSOT archetype definition)
- [ ] Memory is pruned automatically as new sessions enter the window
- [ ] User can inspect and edit the memory state file directly
- [ ] User can clear memory with explicit command (scoped to single archetype or all)

**Dependencies:** none

### FR-11: Dice Resolution Authority
**Priority:** Must Have (P0)
**Description:** Dice resolution during `/braunstein` and `/improvise` is user-configurable. Default: user rolls and reports.

**Acceptance Criteria:**
- [ ] Per-session flag: `--dice=user|arneson|hybrid` (default `user`)
- [ ] Mode `user`: Arneson prompts user for roll outcome; Arneson does not generate random numbers
- [ ] Mode `arneson`: Arneson resolves rolls using Gygax probability scripts (when available) or standalone RNG; outcome logged deterministically in sidecar
- [ ] Mode `hybrid`: Arneson proposes a roll outcome; user confirms or re-rolls
- [ ] All three modes log roll events identically in sidecar (same schema)

**Dependencies:** optional Gygax probability scripts

### FR-12: Tradition Fallback (Structural Improvisation)
**Priority:** Must Have (P0)
**Description:** When a tradition lore file is absent or thin, Arneson improvises from game-state structure and flags the improvisation to the user.

**Acceptance Criteria:**
- [ ] At session start: if tradition YAML matches exactly, proceed silently
- [ ] If tradition YAML missing or thin: display banner (`"I don't have a lore file for this tradition — I'll improvise from mechanics. Okay to proceed?"`), prompt user
- [ ] If user confirms: proceed in "improvised tradition" mode; tag sidecar preamble accordingly
- [ ] Improvisation notes saved back to `grimoires/arneson/fragments/improvised-tradition-{tradition}-{date}.md` for designer review
- [ ] User can reject and abort the session

**Dependencies:** FR-9 (intent), read-only access to `skills/lore/resources/` when Gygax installed

### FR-13: Voice Schema (Shared Base + Type-Specific Extensions)
**Priority:** Must Have (P0)
**Description:** Voice files share a common base schema. Archetypes, NPCs, and PCs extend the base with type-specific fields.

**Acceptance Criteria:**
- [ ] `schemas/voice-base.schema.yaml` defines: speech_patterns, reaction_tempo, emotional_register, memory_slots, known_facts
- [ ] `schemas/voice-archetype.schema.yaml` extends base with: experiential_intent_weights, memory_window_size, chaos_axis_config (for Chaos Agent)
- [ ] `schemas/voice-npc.schema.yaml` extends base with: location, faction, workshop_state
- [ ] `schemas/voice-pc.schema.yaml` extends base with: player_consent_metadata, pc_class (or tradition-equivalent)
- [ ] All three extensions validate as valid instances of the base

**Dependencies:** none

### FR-14: Chaos Agent Bounding
**Priority:** Must Have (P0)
**Description:** The Chaos Agent archetype is narratively bounded and structurally unbounded. Mechanically unpredictable decisions; intelligible narration.

**Acceptance Criteria:**
- [ ] Chaos Agent voice YAML (`voice-archetype` extension) declares `chaos_axis_config: { structural: unbounded, narrative: bounded }`
- [ ] Structural axis: archetype decision distribution across legal moves is unconstrained (may pick any move with any probability per turn)
- [ ] Narrative axis: speech remains intelligible in-fiction (no reality-breaks, no frame-shatter, no meta-awareness); narration stays grounded in the game-state's fiction
- [ ] Sidecar emission hard-capped per turn to prevent context-window blow-up
- [ ] Per-turn cap is configurable; default set based on empirical testing during vertical-slice build

**Dependencies:** FR-13 (voice schema)

### FR-15: Safety as Load-Bearing Mechanic
**Priority:** Must Have (P0)
**Description:** Session-length skills (`/braunstein`, `/voice`, `/improvise`) open with a safety agreement. Triggered safety events are logged as `dead_design_space` findings.

**Acceptance Criteria:**
- [ ] Session-length skills prompt Lines & Veils / X-card at session open
- [ ] Session-level pause command (`/pause` or `/x-card`) works at any time
- [ ] Pause halts generation immediately; resume is explicit (`/resume`)
- [ ] Triggered events log as `dead_design_space` events in sidecar
- [ ] Project-level aggregation: safety events also append to `grimoires/arneson/safety-findings.md` (human-readable, stays out of normal transcripts)
- [ ] One-shot skills (`/scene`, `/narrate`, `/fragment`) inherit project-level safety config; do not re-prompt
- [ ] Safety taxonomy follows TTRPG community conventions (Lines & Veils, X-card, Script Change) — no proprietary terminology

**Dependencies:** none

### FR-16: Structural Tagging (Sidecar Event Schema)
**Priority:** Must Have (P0) — admissibility infrastructure
**Description:** The `{session}.events.yaml` sidecar is a structured event log that makes admissibility mechanically verifiable.

**Acceptance Criteria:**
- [ ] `schemas/session-events.schema.yaml` defines event types: `scene_frame`, `dice_roll`, `archetype_decision`, `signal_flag`, `intent_conflict`, `gm_prompt`, `safety_trigger` (= `dead_design_space`), `rule_of_cool`, `clarifying_question`
- [ ] Each `archetype_decision` event includes: archetype id, decision text, classification (`fictional_friction` | `mechanical_bottleneck` | both), game-state reference(s) that informed the decision
- [ ] Each `dice_roll` event includes: mechanic id, outcome, mode (`user`/`arneson`/`hybrid`), reference to game-state mechanic
- [ ] Each `signal_flag` event includes: signal type (confusion, friction, bottleneck, delight, etc.), source (user-flagged or Arneson-inferred), scene_frame back-reference
- [ ] Sidecar is written incrementally during the session (durable across crashes)

**Dependencies:** FR-1 (/braunstein emits), FR-5 (/improvise emits), FR-8 (/distill consumes)

### FR-17: Standalone Fallback Archetype Bundle
**Priority:** Must Have (P0) — standalone-plus-composable
**Description:** When Gygax is absent, Arneson ships a minimal fallback copy of the 9 archetypes (marked as fallback) so that archetype-dependent skills still function.

**Acceptance Criteria:**
- [ ] Arneson ships `resources/archetypes-fallback/*.yaml` — mirrors Gygax's 9 archetypes
- [ ] Each fallback file includes a comment: `# FALLBACK: overridden by Gygax's identity/persona.yaml when Gygax is installed`
- [ ] Archetype-dependent skills (`/braunstein`, `/improvise`) prefer Gygax's SSOT when present; fall back when absent
- [ ] Fallback files are kept semantically in sync with Gygax's SSOT (test: fallback loads without errors against current Gygax version) — divergence flagged in release notes

**Dependencies:** Gygax v3 (as SSOT source; but construct works without it)

> **Sources**: issue-3:68-78 (skill list), issue-3:125-135 (principles), Phase 4 (teammate feedback, skill ordering), Phase 5 (all technical decisions), NOTES.md Decision Log

---

## Non-Functional Requirements

### Performance
- Interactive sessions (`/braunstein`, `/voice`, `/improvise`) must respond to each user turn within a time budget that keeps conversation flowing. Target: initial response begins within 10 seconds of user input; full turn completes within 60 seconds for typical turns. Chaos Agent turns may be longer but are bounded by FR-14's per-turn cap.
- One-shot skills (`/scene`, `/narrate`, `/fragment`) complete within a single LLM turn. Target: <60 seconds typical.
- `/distill` is batch — no interactive performance requirement.

### Reliability
- Session state must be durable to crashes. `{session}.md` and `.events.yaml` must be written incrementally (append-only during session) so that an interrupted session leaves a readable partial transcript.
- Memory-window files (`voices/archetypes/*.state.yaml`) must be written atomically (temp-file + rename) to prevent corruption on crash.

### Scalability
- Construct operates on a single designer's game-state. No multi-tenant, no concurrent-session requirements for v1.
- Sidecar files must remain tractable. Target: typical session sidecar <500KB YAML. Hard cap: per-turn event emission (FR-14 prevents blow-up).

### Security / Privacy
- No outbound network calls from Arneson code except the LLM provider call (inherited from the Loa framework).
- Game-state and session transcripts stay local to the user's repository. No telemetry beyond what Loa provides at the framework level.
- Safety-findings are local-only; they appear only in `grimoires/arneson/safety-findings.md` and the sidecar. Never transmitted externally.

### Compliance
- Safety taxonomy must follow TTRPG community conventions (Lines & Veils, X-card, Script Change). No proprietary invention here.
- No personal player data stored in v1 (designer-only UX means no player-identifiable information enters the system).

### Accessibility
- Markdown-native output. No non-text-required modes.
- All skills must operate from a text terminal without visual-only cues.

### Portability
- Arneson installs as a Loa-framework skill-pack. Supported platforms match Loa's supported platforms (darwin, linux). Windows: untested in v1.

> **Sources**: issue-3:125-135 (principles), Phase 5 (technical decisions), Phase 6 (scope)

---

## User Experience

### Key User Flows

#### Flow 1: Closed-loop design iteration (UC-1)
```
Gygax /cabal analysis
  → designer edits mechanic
  → /braunstein --newcomer
  → [prose transcript + events.yaml written incrementally]
  → /distill {session}
  → Gygax /cabal --from-session {digest}
  → next iteration
```

#### Flow 2: Standalone playtest (UC-2)
```
/braunstein --newcomer
  → [Arneson detects no Gygax; uses fallback archetypes; banner notes standalone mode]
  → session proceeds
  → /distill {session}
  → self-describing digest written
```

#### Flow 3: NPC voice workshop (UC-3)
```
/voice masked-mibera
  → [safety agreement]
  → [Arneson loads npc state, or creates new]
  → workshop dialogue
  → /break (or session exit)
  → [diff displayed, user confirms]
  → state persisted
```

#### Flow 4: Intent-flip comparison test (G-3 validation)
```
game-state with experiential_intent: desperate
  → /braunstein (capture transcript A)
edit game-state: experiential_intent: heroic (mechanical_intent unchanged)
  → /braunstein --same-scene (capture transcript B)
blind-read A vs B
  → voicing materially differs
```

### Interaction Patterns

- **Session-length skills** (`/braunstein`, `/voice`, `/improvise`): open with safety agreement, sustain character/scene across many user turns, exit cleanly with state diff preview.
- **One-shot skills** (`/scene`, `/narrate`, `/fragment`): single request → single response; re-invoke for variation.
- **Meta skills** (`/arneson`, `/distill`): read or batch-process existing files; no interactive state.
- **Graceful degradation**: all skills detect missing composition targets (Gygax, tradition lore, game-state fields) and either degrade with a banner or prompt the user for confirmation.

### Accessibility Requirements

- Text-only. All outputs are markdown and YAML, legible in any editor or terminal.
- No time-pressured interaction patterns (user sets the pace).

> **Sources**: Phase 3 (designer-only), Phase 4 (interactivity: hybrid per skill), Phase 5 (interaction decisions)

---

## Technical Considerations

### Architecture Notes

construct-arneson is a **Loa-framework skill-pack construct** (schema_version 3). It operates within the State Zone (`grimoires/arneson/`) and does not modify the System Zone (`.claude/`). All interactive behavior is implemented as Skills with SKILL.md entry points; no custom runtime is required.

**Composition model**: standalone-plus-composable. Arneson runs as a self-contained construct and detects sibling construct (Gygax v3) presence at runtime via filesystem checks (e.g., existence of `grimoires/gygax/` and `skills/cabal/`). When Gygax is detected, Arneson upgrades from fallback mode (using `resources/archetypes-fallback/`) to composed mode (reading Gygax's SSOT files).

**Identity files**: `identity/ARNESON.md` (prose identity narrative), `identity/persona.yaml` (warm, improvisational, collaborative), `identity/expertise.yaml` (voice work, scene framing, narrative causality, oracle interpretation, campaign continuity), `identity/refusals.yaml` (structural analysis, probability math, mechanical recommendations, pattern-matching).

**Schemas**: `schemas/experiential_intent.schema.yaml`, `schemas/voice-base.schema.yaml` + extensions, `schemas/session-events.schema.yaml`, `schemas/digest.schema.yaml`.

**Grimoire structure** (per issue-3:105-123, extended):
```
grimoires/arneson/
  voices/
    archetypes/           # Instance state (memory, scars, preferences)
    npcs/                 # Workshop NPCs
    pcs/                  # PC voices for /improvise mode
  scenes/                 # /scene outputs
  sessions/               # /braunstein + /improvise transcripts (.md + .events.yaml pairs)
  digests/                # /distill outputs
  improv/                 # /improvise-only session logs (if distinct from sessions/)
  fragments/              # /fragment outputs + improvised-tradition notes
  safety-findings.md      # Project-level safety event log
  changelog/
```

### Integrations

| System | Integration Type | Purpose |
|--------|------------------|---------|
| Gygax v3 `grimoires/gygax/game-state/` | Read-only filesystem | Mechanics, stats, intent fields |
| Gygax v3 `skills/cabal/resources/archetypes.yaml` | Read-only filesystem | Archetype behavioral SSOT (with Arneson fallback) |
| Gygax v3 `identity/persona.yaml` + `expertise.yaml` | Read-only filesystem | Archetype voice SSOT |
| Gygax v3 `skills/lore/resources/{tradition}.yaml` | Read-only filesystem | Tradition conventions (with structural-improvisation fallback) |
| Gygax v3 probability scripts | Read-only filesystem + subprocess | Dice mode `arneson` roll resolution (when Gygax present) |
| Gygax v3 `/cabal --from-session` | File handoff | Consumes `/distill` digest output |
| Loa framework | Skill harness | Skill loading, permission prompts, hooks, memory, trajectory logging |

### Dependencies

- **Loa framework** (mounted as submodule; currently v1.71.1)
- **Gygax v3** — *optional amplifier* per standalone-plus-composable; not hard-required
- **yq v4+** (configurable-paths feature; already required by Loa)
- **Beads** for task tracking (present in `.beads/`)

### Technical Constraints

- All output is markdown + YAML. No binary formats.
- No outbound network calls outside the LLM provider (framework-level).
- MIBERA: HEKATE must not appear anywhere in code, examples, tests, or docs.
- Standalone mode must be a tested CI configuration, not an afterthought.

> **Sources**: issue-3:104-166 (grimoire structure + identity files), Phase 4–5 (composition + schema decisions), NOTES.md Decision Log

---

## Scope & Prioritization

### In Scope (v1)

All 17 functional requirements (FR-1 through FR-17). The eight user-facing skills:
- `/braunstein` (flagship, P0)
- `/voice` (P0)
- `/scene` (P0)
- `/narrate` (P0)
- `/improvise` (P0)
- `/arneson` (P0, status-only read)
- `/fragment` (P0)
- `/distill` (P0, composition glue)

Plus supporting infrastructure: intent schema, voice schema, session-event schema, digest schema, archetype fallback bundle, safety machinery.

### In Scope (Future Iterations)

| Item | Why deferred |
|------|--------------|
| Direct player-at-table UX | v2 — needs multi-actor session format; designer-only is already full v1 |
| Campaign arc modeling beyond 3-session archetype memory | v2+ — sliding window covers immediate designer needs |
| Non-text output modes (audio, image, VTT integration) | v2+ — markdown-native v1 is sufficient for admissibility |
| Auto-generated tradition lore YAMLs | v2+ — risky (might fabricate tradition details); user must author |
| External rater protocol for blind-attribution tests | v2 — designer self-test suffices for v1 if successful (see assumption #5) |
| Multi-model voice consistency regression suite | v2 — nice-to-have; tracked as risk R-8 |

### Explicitly Out of Scope

| Item | Reason |
|------|--------|
| Structural analysis features | Arneson's identity refusal — that's Gygax |
| Probability math | Arneson's identity refusal |
| Mechanical recommendations | Arneson's identity refusal |
| Pattern-matching against anti-patterns | Arneson's identity refusal |
| MIBERA: HEKATE references of any kind | User directive — private/upstream |
| Cross-construct schema package (shared package both depend on) | Rejected in Phase 4; axis-split ownership is cleaner |

### Priority Matrix

| Feature | Priority | Effort | Impact |
|---------|----------|--------|--------|
| FR-1 `/braunstein` | P0 | L | High (flagship) |
| FR-16 Sidecar event schema | P0 | M | High (admissibility infra) |
| FR-9 Intent interface | P0 | M | High (composition contract) |
| FR-8 `/distill` | P0 | M | High (composition glue) |
| FR-15 Safety machinery | P0 | M | High (load-bearing principle) |
| FR-17 Fallback archetype bundle | P0 | S | High (standalone viability) |
| FR-4 `/narrate` | P0 | M | High (primitive, extracted after vertical slice) |
| FR-2 `/voice` | P0 | M | Med-High |
| FR-3 `/scene` | P0 | S | Med |
| FR-5 `/improvise` | P0 | M | Med |
| FR-6 `/arneson` status | P0 | S | Med (meta) |
| FR-7 `/fragment` | P0 | S | Med |
| FR-10 Archetype memory | P0 | S | Med |
| FR-11 Dice authority | P0 | S | Med |
| FR-12 Tradition fallback | P0 | S | Med |
| FR-13 Voice schema | P0 | S | Med |
| FR-14 Chaos Agent bounding | P0 | S | Low-Med (single archetype) |

**Build ordering**: Vertical slice first, then extract. Ship `/braunstein` end-to-end against the synthetic fixture (with sidecar + safety + intent) first, then refactor out `/narrate`, `/voice`, `/scene`, `/distill` from real usage, then `/improvise`, `/fragment`, `/arneson`.

> **Sources**: issue-3:70-78 (skills), Phase 4 (scope tier, teammate feedback), Phase 6 (build ordering, HEKATE exclusion, explicit out-of-scope)

---

## Success Criteria

### Launch Criteria (v1 ship)

- [ ] Construct validates at Loa L0/L1/L2
- [ ] All 17 functional requirements implemented with acceptance criteria green
- [ ] All eight skills execute against the synthetic reference fixture
- [ ] `/braunstein` → `/distill` → Gygax `/cabal --from-session` round-trip passes (G-1, G-5)
- [ ] Identity-refusal audit passes: no structural-analysis, probability-math, or mechanical-recommendation output in acceptance scenarios (G-2)
- [ ] Intent-flip comparative test passes: identical game-state with `experiential_intent` changed produces materially different voicing (G-3)
- [ ] CI matrix: `arneson-alone` and `arneson-with-gygax` both green (G-4, G-5)
- [ ] ≥3 archetypes voiced distinctly per blind-attribution protocol (G-6)
- [ ] Safety machinery tested: opt-in agreement, pause/resume, `dead_design_space` logging all work
- [ ] Chaos Agent per-turn cap empirically set based on vertical-slice data; no context blow-up in acceptance
- [ ] Zero MIBERA: HEKATE references anywhere in construct files (grep audit)
- [ ] Synthetic reference fixture authored and shipped in `examples/`
- [ ] README + identity prose + `/arneson` status message all avoid framing Arneson as "half of" anything — construct stands on its own

### Post-Launch Success

- [ ] At least one published demo session transcript + digest (demonstrates admissibility to community)
- [ ] Gygax schema PR for two-axis intent merged, closing assumption #1
- [ ] At least one designer outside the author reports successful `/braunstein` run against their own game-state

### Long-term Success

- [ ] Closed-loop design iteration (UC-1) used repeatedly by the author over sustained design cycles
- [ ] Structural-tagging sidecar schema stable across a minor version with no breaking changes
- [ ] Community adoption: at least one non-author construct builds on Arneson's event schema or digest schema

> **Sources**: issue-3:192-200 (original criteria, reframed), Goals G-1 through G-6, Phase 6 (out-of-scope)

---

## Risks & Mitigation

| ID | Risk | Probability | Impact | Mitigation Strategy |
|----|------|-------------|--------|---------------------|
| R-1 | **Identity drift** — Arneson edges into Gygax territory (makes mechanical recommendations, analyzes structure, fudges dice) | High | High | `identity/refusals.yaml` + identity-refusal audit in `/audit-sprint`, modeled on Gygax's pattern |
| R-2 | **Hollow fiction** (admissibility failure) — plausible prose not grounded in game-state; sidecar present but vacuous | Med | High | Sidecar event schema (FR-16) requires grounding references per decision; round-trip round-trip test is launch criterion |
| R-3 | **Intent contract violation** — Arneson voices away from `mechanical_intent` (fudges a lethal roll) | Med | High | Intent respect is architectural principle + paired A/B acceptance test; refusal audit catches fudging patterns |
| R-4 | **Chaos Agent context-window blowup** | Med | Med | Per-turn sidecar emission cap (FR-14); narrative-bounded design reduces token pressure |
| R-5 | **Tradition coverage gap** — community-from-day-one v1 lacks depth for every supported tradition | Med | Med | Structural-improvisation fallback (FR-12); user confirmation prevents silent hallucination |
| R-6 | **Safety failure mode** — missed trigger, inadequate pause, safety log not surfaced | Med | High | Session-open agreement mandatory; project-level `safety-findings.md` visible; community-standard taxonomy |
| R-7 | **Gygax schema-bump coordination** — intent axis split requires Gygax minor version | Med | Med | Arneson ships unilateral `experiential_intent`; graceful degradation path in FR-9; concurrent Gygax issue filed |
| R-8 | **LLM voice drift** — model updates shift voice consistency across sessions (drift not caused by code) | High | Med | Pin identity prose; periodic regression test against recorded baseline voice samples; tracked for v2 regression suite |
| R-9 | **Persona memory leakage** — `/voice` workshop state bleeds into subsequent `/braunstein` archetype voicing | Med | Med | Explicit session boundaries; state cleared between sessions by default; cross-voice isolation test in acceptance |
| R-10 | **Composition coupling** (bit-rot) — standalone mode degrades because dev always runs with Gygax present | Med | High | CI matrix REQUIRES `arneson-alone` mode green at every PR; treated as first-class not afterthought |
| R-11 | **N=1 founder effect** — designer-only v1 with synthetic fixture means all validation is internal | High | Med | Publish demo transcript + digest publicly early; at least one external designer report is post-launch success criterion |
| R-12 | **Scope ballooning** (8 skills is a lot) — quality-driven cadence becomes "never ships" | Med | High | Vertical-slice ordering creates a shippable milestone at `/braunstein` + sidecar + `/distill` even if other skills incomplete |

### Assumptions

- **A-1**: Gygax will accept a PR to split single-axis `intent` into `mechanical_intent` + `experiential_intent`. *If wrong*: Arneson ships unilateral `experiential_intent` and reads Gygax's existing `intent` as `mechanical_intent` (FR-9 graceful degradation covers this).
- **A-2**: A synthetic reference fixture can stay small (single-file, readable in one sitting) and still exercise all 8 skills. *If wrong*: grow fixture; split into multiple; accept that some skills exercise against stubs during acceptance.
- **A-3**: Gygax v3's `identity/persona.yaml` + `expertise.yaml` (current shape) are sufficient SSOT for Arneson's voicing needs. *If wrong*: propose Gygax schema extension for voice fields; Arneson fallback bundle temporarily carries the delta.
- **A-4**: Safety-as-data-point doesn't conflict with TTRPG community safety-tool conventions (Lines & Veils, X-card, Script Change). *If wrong*: adapt logging schema to match accepted formats; do not invent proprietary safety taxonomy.
- **A-5**: Blind-attribution archetype-voice testing can be run by the designer alone (self-test, no external rater). *If wrong*: admissibility is harder to verify in v1; need pairwise or delayed-reading protocol; may downgrade G-6 validation.

### Dependencies on External Factors

- **Loa framework** maintenance and stability (v1.71.1+; submodule mounted)
- **Gygax v3** availability for composition tests (not required for core function per standalone rule, but required for CI `arneson-with-gygax` mode)
- **LLM provider** behavior consistency (see R-8)
- **TTRPG community safety-tool conventions** remain stable (new major revisions to X-card etc. would require schema update)

> **Sources**: Phase 7 (full risk register + user-added R-8, R-9, R-10), Phase 4 teammate feedback, Phase 6 (A-2)

---

## Milestones

Timeline is **quality-driven, no fixed ship date** (Phase 2 decision). Milestones are logical checkpoints, not calendar targets.

| Milestone | Gate | Deliverables |
|-----------|------|--------------|
| M0 — Foundation | Loa construct scaffolded, identity files drafted, synthetic fixture authored | `construct.yaml`, `identity/` directory, `examples/{fixture}.yaml`, `schemas/` scaffolded |
| M1 — Vertical Slice | `/braunstein` runs end-to-end against fixture with sidecar + safety + intent | `/braunstein` SKILL.md, FR-1/FR-15/FR-16/FR-17 implemented, round-trip-test-ready |
| M2 — Admissibility | `/distill` implemented; Gygax round-trip passes | FR-8 complete, G-1 launch criterion green |
| M3 — Primitives Extracted | `/narrate`, `/voice`, `/scene` refactored out of `/braunstein` code | FR-2, FR-3, FR-4 implemented |
| M4 — GM-Side | `/improvise` symmetric to `/braunstein` | FR-5 implemented |
| M5 — World-Building | `/fragment` shipped; `/arneson` status dashboard | FR-6, FR-7 implemented |
| M6 — Composition Hardening | CI matrix green in both modes; identity-refusal audit clean | G-4, G-5, G-2 launch criteria green |
| M7 — Launch | All launch criteria green | v1 release |

> **Sources**: Phase 2 (no fixed timeline), Phase 6 (vertical-slice ordering)

---

## Appendix

### A. Stakeholder Insights

**From the author (Phases 1–7, 2026-04-13):**
- The inverse-identity framing is load-bearing, not aesthetic
- Standalone-plus-composable is a design principle that outlives this construct
- HEKATE stays upstream; Arneson must be publicly shippable without private context
- Trust grant: agent has permission to shift course and allocate 20% effort to intuition-led exploration (saved to project memory)

**From the Gygax-side teammate (Phase 4 feedback):**
- Arneson's value is **data-emitting fiction**, not fiction alone. Transcripts must be mechanically instrumented.
- Intent is two-axis (mechanical / experiential); designers flip axes and expect voicing to follow without prompt-tuning
- Archetypes are a Gygax SSOT; Arneson consumes the same behavioral definitions Gygax uses for math-sim
- Safety triggers are design findings ("dead design space"), not only social events
- `/distill` is required — Gygax needs a structured digest, not prose, to close the loop

### B. Competitive Analysis

| Tool class | Does structural analysis | Does grounded fiction | Couples both |
|------------|-------------------------|----------------------|---------------|
| Spreadsheets (Google Sheets, Excel) | Yes | No | No |
| Probability calculators (AnyDice etc.) | Yes (narrow) | No | No |
| General-purpose LLM chats | No (pretends to) | Yes (ungrounded) | No |
| Virtual tabletops (Roll20, Foundry) | Narrow (dice) | No | No (player-facing, not designer-facing) |
| Gygax v3 alone | Yes | No (refuses) | No |
| **Gygax + Arneson** | **Yes** | **Yes (grounded)** | **Yes (via game-state + sidecar + digest)** |

No existing TTRPG tooling grounds fiction in a persistent, bidirectionally-composable game-state.

### C. Bibliography

**Internal / project:**
- Issue #3 (proposal): https://github.com/0xHoneyJar/construct-gygax/issues/3
- Concept doc: `grimoires/loa/context/arneson-v1-concept.md`
- Session NOTES: `grimoires/loa/NOTES.md`

**External:**
- Lines & Veils / X-card safety tools: community-standard documents (Ron Edwards, John Stavropoulos, et al.)
- Dave Arneson / Blackmoor (1971): historical context for naming
- Braunstein (1969): historical context for flagship naming
- PbtA fiction-mechanics-fiction loop: Baker (2008) *Apocalypse World*

### D. Glossary

| Term | Definition |
|------|------------|
| **Admissibility** | The property that a `/braunstein` transcript is structured and grounded enough to be cited as evidence in Gygax re-analysis. Binary test: round-trip through `/distill` → Gygax `/cabal --from-session` without manual reformatting. |
| **Archetype** | A behavioral profile from Gygax's cabal system (Newcomer, Optimizer, Chaos Agent, etc.). Arneson voices these as actual characters during `/braunstein`. |
| **Braunstein** | Arneson's flagship skill; named after Dave Arneson's 1969 proto-RPG. Live playtest session where user GMs and Arneson plays an archetype. |
| **Dead Design Space** | A region of the game-state where safety triggers fire, marking it as unsuitable for the current design frame. Logged as a design constraint, not only a social event. |
| **Distill** | Skill that converts a session's prose + structured sidecar into a Gygax-ingestible digest. |
| **Experiential Intent** | Designer-authored field declaring how a mechanic should *feel* (desperate, heroic, tragic, etc.). Owned by Arneson's schema. |
| **Fallback bundle** | Arneson-shipped minimal copy of archetype YAMLs used when Gygax is not installed. Overridden by Gygax's SSOT when present. |
| **Fictional friction** vs **Mechanical bottleneck** | Two classifications for in-session observed problems. Fictional friction = narrative awkwardness; mechanical bottleneck = structural constraint. Both are tagged in sidecar events. |
| **Grimoire** | Persistent state-zone directory (`grimoires/arneson/`) where all session, voice, scene, fragment, and digest artifacts live. |
| **Mechanical Intent** | Designer-authored field declaring what a mechanic should *do* numerically (this roll is hard, this resource depletes fast, etc.). Owned by Gygax's schema. |
| **Narrative Chaos** vs **Structural Chaos** | Two axes of chaos-agent behavior. In v1, narrative is bounded (intelligible), structural is unbounded (unpredictable moves). |
| **Sidecar** | `{session}.events.yaml` — structured event log written atomically alongside the prose transcript. |
| **Standalone-plus-composable** | Design principle: constructs work independently AND compose into greater value. No hard dependencies on siblings. |
| **Synthetic reference fixture** | A minimal public-shippable testbed game authored for Arneson; replaces MIBERA: HEKATE for examples and acceptance tests. |

---

*Generated by PRD Architect Agent (/plan-and-analyze), 2026-04-13*
