# Product Requirements Document: construct-arneson v2

**Version:** 2.0
**Date:** 2026-05-12
**Author:** PRD Architect Agent (/plan-and-analyze)
**Status:** Draft

> **Sources used across this document:**
> - `grimoires/loa/context/00-READ-FIRST-proposal-issue-3.md` (GH issue 0xHoneyJar/construct-gygax#3)
> - `grimoires/loa/context/arneson-v1-concept.md`
> - `grimoires/loa/NOTES.md` (decision log, teammate feedback from v1 cycle)
> - Codebase analysis (/ride, 2026-05-12) — Sprint 1 implementation verified
> - /plan-and-analyze discovery interview, 2026-05-12 (Phases 1-7)

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

**construct-arneson v2** reframes the construct from a TTRPG-specific narrative companion into a **creative persona engine** — a tool that hosts personas grounded in practitioner-provided structured state and emits structured data from creative sessions. TTRPG design is the first vertical and reference implementation, not the identity.

The v1 cycle (2026-04-13) built strong foundations: 8 skills, 7 schemas, 9 archetypes, a safety-first session flow, and a working prototype. The codebase is clean (hygiene grade A, consistency 9/10) and the core capabilities — persona hosting, grounded fiction generation, structured event capture, transcript+sidecar output — are already more general than their TTRPG framing suggests. v2 makes that generality explicit by extracting a domain-agnostic core, defining an extension interface for domain verticals, and reframing the identity around creative persona work broadly.

The construct serves any creative practitioner — writers, game designers, worldbuilders, agent developers — who needs personas that do generative work against structured state and produce usable data. Named for Dave Arneson, whose improvisational approach to collaborative fiction-making transcends any single game or genre.

> **Sources**: issue-3:37-47, concept:1-19, Phase 1-7 synthesis (2026-05-12)

---

## Problem Statement

### The Problem

Creative practitioners across domains share a common gap: they lack tools where **personas can do generative work grounded in structured state and emit usable data from that work**.

Generic LLM chat generates fiction but is ungrounded — it doesn't read your world bible, your game state, your behavioral spec, or your intent declarations. Static profiles (character sheets, persona documents, agent configs) capture structure but don't generate. Nothing couples the two: structured state flowing into grounded fiction, structured data flowing back out.

> From issue-3:43-46: *"Gygax's identity is load-bearing. Its persona explicitly refuses to generate narrative prose, voice characters, or make final creative decisions. These refusals are what make Gygax trustworthy as an analyst."*

The original v1 framing identified this gap in TTRPG design specifically — Gygax handles structure, Arneson handles fiction. But the gap is universal: game writers need characters grounded in story bibles. Agent developers need persona calibration against behavioral specs. Worldbuilders need factions and NPCs grounded in established lore. The pattern is the same: **structured state in, grounded creative generation, structured data out**.

> **Sources**: issue-3:43-46, concept:130-133, Phase 1 (2026-05-12)

### User Pain Points

- **Grounding gap**: Creative generation happens in tools that don't read the practitioner's structured state. Output drifts from established facts, intent, and constraints.
- **Data loss**: Creative sessions produce prose but not structured data. Insights, decisions, and signals are trapped in narrative and must be manually extracted.
- **Persona inconsistency**: Characters and agents lose voice across sessions because there's no persistent persona state with memory and behavioral grounding.
- **Tool fragmentation**: Structure lives in spreadsheets/YAML/databases. Fiction lives in chat windows. Neither knows about the other.
- **No feedback loop**: Creative output doesn't round-trip back to structural analysis. Design-and-play (or write-and-test) remain separate activities.

> **Sources**: issue-3:50-60 (TTRPG-specific pain points, generalized), concept:130-133, Phase 1 (2026-05-12)

### Current State

Practitioners use:
- Generic LLM chats for fiction (ungrounded, no persistent state, no structured output)
- Static documents for character/agent profiles (no generative capability)
- Domain-specific tools that don't compose (TTRPG VTTs, writing software, agent frameworks)
- Manual processes to bridge structure and fiction (copy-paste, re-prompting, mental models)

### Desired State

A single construct that:
1. Reads any practitioner-provided structured state (game state, story bible, behavioral spec, world lore)
2. Hosts personas grounded in that state with persistent memory across sessions
3. Generates fiction that respects intent, constraints, and established facts
4. Emits structured session data (events, signals, decisions) alongside human-readable transcripts
5. Produces output consumable by both the practitioner and downstream tools
6. Supports new creative domains without core code changes

---

## Goals & Success Metrics

### Primary Goals

| ID | Goal | Measurement | Validation Method |
|----|------|-------------|-------------------|
| G-1 | **Persona believability** — personas are distinct, consistent, and grounded enough that practitioners trust the creative output | Qualitative: voice distinctness across sessions; quantitative: grounding citations per generated passage | Regression against Sprint 0 prototype quality bar (5/5 axes) |
| G-2 | **Structured output fidelity** — session data is machine-parseable and consumable by any downstream tool | Sidecar events validate against schema; round-trip test with at least one consumer | Schema validation pass rate; `/distill` output parseable by downstream |
| G-3 | **Domain extensibility** — a new domain vertical can be added without modifying core Arneson code | Extension story: add a hypothetical domain vertical using only the extension interface | Integration test: domain vertical loads, sessions run, output validates |
| G-4 | **TTRPG vertical regression** — existing TTRPG capabilities work at least as well as v1 | All v1 acceptance criteria still pass | CI suite from Sprint 1 + manual `/braunstein` regression |
| G-5 | **Dual-audience output** — all output is simultaneously human-readable and machine-parseable | Transcripts render as presentable markdown; sidecars parse as valid structured data | Manual review + schema validation |
| G-6 | **Safety universality** — safety infrastructure works in every domain, every session, every mode | Safety flow (agreement, X-card, pause) activates regardless of domain context | Test safety triggers across TTRPG and at least one non-TTRPG session |

> **Sources**: Phase 2 (2026-05-12) — success metrics; Phase 1 reframing; v1 NOTES.md decision log

### Key Performance Indicators

| Metric | Baseline (v1) | Target (v2) | Goal ID |
|--------|---------------|-------------|---------|
| Domain verticals supported | 1 (TTRPG) | 1 + extension point validated | G-3 |
| Core code changes for new domain | N/A (monolithic) | 0 files modified | G-3 |
| v1 TTRPG acceptance criteria passing | 100% | 100% | G-4 |
| Schema validation pass rate | Manual | Automated, 100% | G-2 |
| Safety coverage | TTRPG only | All domains | G-6 |

### Constraints

- **Quality-driven timeline**: No fixed ship date. Ship when it's right.
- **Standalone-plus-composable**: Arneson must work without Gygax installed. Gygax must work without Arneson installed. Composition is opt-in amplification, not dependency.
- **No private/upstream game references**: No HEKATE or other private game names in shippable files. The construct stands on its own.
- **Director/performer model**: The practitioner always directs. Arneson always performs within their constraints. No autonomous mode.

> **Sources**: Phase 2 (2026-05-12); NOTES.md decisions (standalone-plus-composable, HEKATE exclusion, director/performer)

---

## User Personas & Use Cases

### Persona: The Creative Practitioner

**Demographics:**
- Role: Writer, game designer, worldbuilder, agent developer, narrative designer, or any creative professional working with personas and structured state
- Technical Proficiency: Comfortable with CLI tools and YAML/markdown. Not necessarily a software engineer.
- Goals: Create believable, grounded creative output with structured data capture. Iterate between structure and fiction fluidly.

**Behaviors:**
- Maintains structured state (game state, story bibles, behavioral specs, world lore) in YAML/markdown
- Needs personas that stay consistent across sessions and respect established constraints
- Reviews both the creative output (prose) and the structured data (events, signals)
- Uses downstream tools to consume session data (analysis tools, other constructs, CI pipelines)

**Pain Points:**
- Creative generation drifts from established facts when the tool doesn't read their state
- Insights from creative sessions are lost because they're trapped in unstructured prose
- Persona voice degrades across sessions without persistent memory
- No single tool bridges structure and fiction

> **Sources**: Phase 3 (2026-05-12), generalized from v1 TTRPG designer persona

### Use Cases

#### UC-1: TTRPG Live Playtest (Reference Vertical)
**Actor:** Game designer
**Preconditions:** Game state YAML exists with mechanics, entities, intent declarations. Archetype definitions available (Gygax-provided or fallback).
**Flow:**
1. Designer invokes `/braunstein --newcomer` against their game state
2. Arneson loads the Newcomer archetype, reads game state and intent
3. Designer GMs; Arneson plays the Newcomer in-character
4. Session produces transcript (markdown) + sidecar (structured events)
5. Designer runs `/distill` to compress session into downstream-consumable format

**Postconditions:** Transcript is presentable markdown. Sidecar validates against session-events schema. Distill output is parseable by Gygax's `/cabal --from-session`.
**Acceptance Criteria:**
- [ ] Persona voice is distinct and grounded in archetype definition
- [ ] Intent fields are respected (non-negotiable mechanics played into, not against)
- [ ] Safety flow activates before creative generation begins
- [ ] Sidecar captures: dialogue, dice rolls, signal flags, intent conflicts, scene transitions
- [ ] Transcript + sidecar are a paired output

#### UC-2: Character Voice Workshop
**Actor:** Writer or game designer
**Preconditions:** Character profile exists (NPC definition, behavioral spec, or persona config).
**Flow:**
1. Practitioner invokes `/voice {character-id}`
2. Arneson loads the character profile and stays in-character
3. Practitioner conducts workshop dialogue — testing voice, reactions, consistency
4. Session produces transcript + sidecar with dialogue events and signal flags

**Postconditions:** Character voice is consistent with profile. Session data is structured.
**Acceptance Criteria:**
- [ ] Character voice matches profile traits (speech patterns, emotional register, knowledge level)
- [ ] Voice persists across conversation turns without drift
- [ ] Workshop produces structured dialogue events, not just prose

#### UC-3: Scene Generation From State
**Actor:** Worldbuilder or narrative designer
**Preconditions:** Structured state exists (world lore, location data, faction relationships, or equivalent).
**Flow:**
1. Practitioner invokes `/scene` with a seed (prompt, oracle result, or state reference)
2. Arneson reads structured state for grounding
3. Generates a scene: opening situation, sensory detail, immediate stakes
4. Scene is grounded in established state — no facts contradicted

**Postconditions:** Scene is presentable markdown. References to state are verifiable.
**Acceptance Criteria:**
- [ ] Scene respects all constraints from structured state
- [ ] Sensory detail and stakes are present
- [ ] No hallucinated facts that contradict established state

#### UC-4: Agent Persona Calibration (Grounded in Real Usage)
**Actor:** Agent developer / curator authoring a Discord NPC
**Preconditions:** Behavioral spec exists (persona config, voice parameters, constraint set). Lore source exists (grail entry, character bible, or equivalent structured state).

**Real-world grounding:** The construct-mongolian project (0xHoneyJar/construct-mibera-codex#76) is already using this pattern — a curator authors voice + judgment rubric for a Grail-entity Discord agent using arneson's `/voice` workshop to converge the NPC's voice register, then serializes the locked voice-state into a `persona.yaml` for a Discord bot. The two-tier doctrine (construct judges / substrate verifies) maps directly to arneson's director/performer model.

**Flow:**
1. Curator invokes `/voice {agent-id}` against their behavioral spec + lore source
2. Arneson hosts the persona and generates workshop dialogue across multiple sessions
3. Curator iterates until voice converges (register, judgment vocabulary, emotional range)
4. Locked voice-state.yaml is exported as the agent's persona definition
5. Optionally serialized into a static prompt for downstream bot/agent runtime

**Postconditions:** Workshopped voice-state captures the agent's behavioral profile. Output is both human-reviewable and machine-consumable.
**Acceptance Criteria:**
- [ ] Domain vertical loads without core code changes
- [ ] `/voice` workshop supports convergence tracking across sessions
- [ ] Locked voice-state.yaml is exportable for downstream agent runtimes
- [ ] Session uses the domain's event taxonomy and resolution mechanics
- [ ] Output format matches the domain's consumer spec

> **Sources**: 0xHoneyJar/construct-mibera-codex#76 (construct-mongolian Track A — real-world agent persona authoring using arneson)

#### UC-5: Extending Arneson to a New Domain
**Actor:** Construct developer or advanced practitioner
**Preconditions:** Arneson core is installed. New domain's structured state, persona definitions, event taxonomy, resolution mechanics, and consumer spec are prepared.
**Flow:**
1. Developer creates domain vertical files following Arneson's extension conventions
2. Arneson discovers the new domain configuration
3. Domain-specific skills become available
4. Sessions run against the new domain's structured state and produce domain-shaped output

**Postconditions:** New domain works without any modifications to Arneson core code.
**Acceptance Criteria:**
- [ ] Zero core files modified
- [ ] Domain's personas load and voice correctly
- [ ] Domain's event taxonomy is used in sidecar output
- [ ] Safety infrastructure activates in the new domain context

#### UC-6: Fiction-Mechanics-Fiction Loop
**Actor:** Game designer or narrative designer
**Preconditions:** A mechanical outcome has been determined (dice roll, rule resolution, stat check).
**Flow:**
1. Practitioner invokes `/narrate` with the mechanical outcome
2. Arneson reads the current state and the outcome
3. Generates the "new fiction" that flows from the mechanical result
4. Fiction respects intent declarations — a `non_negotiable: true` mechanic is narrated faithfully

**Postconditions:** Fiction bridges the mechanical outcome back into the narrative.
**Acceptance Criteria:**
- [ ] Generated fiction is grounded in the mechanical outcome
- [ ] Intent declarations are respected
- [ ] Output includes both prose and structured event capture

---

## Functional Requirements

### Core Requirements (Domain-Agnostic)

#### FR-C1: Persona Hosting Engine
**Priority:** Must Have
**Description:** Load, voice, and persist any persona definition from any domain. The hosting engine manages voice generation, memory (configurable sliding window), behavioral grounding against structured state, and session persistence. Persona definitions are domain-provided; the hosting engine is core.

**Acceptance Criteria:**
- [ ] Persona loads from any domain's definition format (via voice-base schema + domain extensions)
- [ ] Persona maintains consistent voice across turns within a session
- [ ] Persona memory persists across sessions (configurable window, default 3 sessions)
- [ ] Persona respects behavioral constraints from its definition
- [ ] Persona reads and grounds against practitioner-provided structured state

**Dependencies:** FR-C6 (domain extension point provides persona definitions)

> **Sources**: Phase 4 (2026-05-12); v1 FR-10 (archetype memory), FR-13 (voice schema)

#### FR-C2: Session Management
**Priority:** Must Have
**Description:** Start, stop, pause, and resume creative sessions with structured event capture. Every session produces a transcript+sidecar pair. Sessions are domain-aware — they load the active domain's event taxonomy and resolution mechanics.

**Acceptance Criteria:**
- [ ] Session lifecycle: start → active → pause/resume → end
- [ ] Session state persists (can be resumed after interruption)
- [ ] Events captured in real-time to sidecar
- [ ] Session metadata tracks: domain, personas involved, state references, timestamps
- [ ] Multiple sessions can coexist (different domains, different personas)

**Dependencies:** FR-C4 (safety integrates into session lifecycle)

> **Sources**: v1 `/braunstein` state machine (7 states); Phase 4 (2026-05-12)

#### FR-C3: Sidecar Event Schema
**Priority:** Must Have
**Description:** Base event types (dialogue, signal, decision, pause, scene_transition) that are present in every domain. Domains extend the base with domain-specific event types. The base schema defines the envelope; domains define the payload.

**Base Event Types:**
- `dialogue` — persona speaks (who, what, grounding references)
- `signal` — practitioner or persona flags something (safety trigger, insight, concern)
- `decision` — a creative decision is made (what, why, alternatives considered)
- `pause` — session paused (reason)
- `scene_transition` — context shifts (from, to, trigger)
- `state_reference` — output references structured state (what, where, how used)

**Acceptance Criteria:**
- [ ] Base schema validates across all domains
- [ ] Domain-specific event types extend the base without modifying it
- [ ] Every event includes: timestamp, event_type, actor, grounding_refs
- [ ] Sidecar is valid YAML that parseable independently of the transcript

**Dependencies:** FR-C6 (domains declare their event extensions)

> **Sources**: v1 `schemas/session-events.schema.yaml` (12+ event types); Phase 4 (2026-05-12)

#### FR-C4: Safety Infrastructure
**Priority:** Must Have
**Description:** Safety mechanics work in every domain, every session, every mode. No opt-out. Includes: pre-session agreement flow, in-session safety commands (/pause, /x-card, /resume), safety triggers logged as structured data (findings, not just interruptions), and configurable content boundaries (Lines & Veils equivalent).

**Acceptance Criteria:**
- [ ] Pre-session safety agreement is mandatory (cannot be skipped)
- [ ] /pause, /x-card, /resume work in any session regardless of domain
- [ ] Safety triggers are logged as `signal` events in the sidecar with `safety` classification
- [ ] Safety events are treated as data points (Dead Design Space findings), not just interruptions
- [ ] Content boundaries are configurable per session and per domain

**Dependencies:** None (safety is foundational)

> **Sources**: v1 FR-15 (safety as finding); issue-3:131-133 (safety as load-bearing); Phase 4 (2026-05-12)

#### FR-C5: Transcript + Sidecar Output
**Priority:** Must Have
**Description:** Every session produces a paired output: human-readable markdown transcript AND machine-parseable YAML sidecar. The transcript is presentable standalone (grimoire-as-deliverable). The sidecar is consumable by downstream tools. Neither is optional.

**Acceptance Criteria:**
- [ ] Transcript renders as clean, presentable markdown
- [ ] Sidecar validates against the session-events schema (base + domain extensions)
- [ ] Transcript and sidecar are paired (same session ID, co-located in grimoire)
- [ ] Transcript is readable without the sidecar; sidecar is parseable without the transcript
- [ ] Output paths follow grimoire conventions per domain

**Dependencies:** FR-C3 (sidecar schema)

> **Sources**: v1 FR-16 (structural tagging/sidecar); issue-3:151-153 (handoff format); Phase 2 (dual-audience)

#### FR-C6: Domain Extension Point
**Priority:** Must Have
**Description:** A new domain vertical can be added to Arneson without modifying any core code. A domain provides: structured state format, persona definitions, event taxonomy (extending base), resolution mechanics, and downstream consumer specification. The extension interface prioritizes maximum customizability for the practitioner.

**A domain vertical provides:**
1. **Structured state** — the format of the domain's grounding data (game state, story bible, behavioral spec)
2. **Persona definitions** — how personas are defined in this domain (archetypes, NPCs, agents, characters)
3. **Event taxonomy** — domain-specific event types extending the base sidecar schema
4. **Resolution mechanics** — how decisions are resolved in this domain (dice, oracle tables, deterministic rules, or none)
5. **Consumer specification** — what downstream tools expect from `/distill` output

**Acceptance Criteria:**
- [ ] Adding a domain vertical requires zero modifications to core Arneson files
- [ ] Domain is discoverable by Arneson (convention-based, maximum flexibility)
- [ ] Domain's persona definitions are loadable by the persona hosting engine (FR-C1)
- [ ] Domain's event types extend the base schema (FR-C3) without conflicts
- [ ] Domain's resolution mechanics are invocable during sessions
- [ ] Domain's consumer spec is used by `/distill` to shape output
- [ ] TTRPG vertical serves as reference implementation and documentation of the extension interface

**Dependencies:** All other core FRs (this is the integration point)

> **Sources**: Phase 2 proof point (extension story); Phase 4 (2026-05-12)

#### FR-C7: Status Dashboard (`/arneson`)
**Priority:** Should Have
**Description:** Domain-aware status display showing active sessions, voiced personas, recent output, and domain health across all installed verticals.

**Acceptance Criteria:**
- [ ] Shows active sessions grouped by domain
- [ ] Shows recently voiced personas with last-session timestamps
- [ ] Shows domain vertical status (installed, healthy, configuration issues)
- [ ] Works with zero domains installed (shows core status only)

**Dependencies:** FR-C6 (domain awareness)

> **Sources**: v1 FR-6 (`/arneson` status)

#### FR-C8: Workshop-Then-Serialize Pattern
**Priority:** Must Have
**Description:** The canonical flow for persona development is iterative workshop convergence, not one-shot generation. A practitioner invokes `/voice` (or equivalent domain skill) across multiple sessions until the persona's voice *locks* — producing a persisted voice-state that captures speech patterns, memory, register, and behavioral grounding. Only AFTER a workshop has converged may the voice-state be serialized for downstream consumption (e.g., static prompt for a Discord bot, agent config, character bible entry).

Skipping the workshop and extracting voice doctrine directly into a static prompt is a documented misuse pattern — the static embed loses the iteration loop, the grounding, and the sidecar emission that make arneson a workshop instrument rather than an IP-to-photocopy source.

**Two valid shapes:**

| Shape | What it is | What it produces | Valid? |
|-------|-----------|------------------|--------|
| **Workshop tool** (canonical) | Invoke `/voice` iteratively across sessions until voice converges | Locked voice-state.yaml with speech patterns, memory, register | Always |
| **Doctrine reference** (consumer) | Serialize a locked voice-state into a static prompt for downstream use | One-shot voice approximation grounded in workshopped state | Only after Shape 1 |

**Acceptance Criteria:**
- [ ] `/voice` (and equivalent domain workshop skills) support multi-session iteration with convergence tracking
- [ ] Voice-state.yaml is the canonical output of a completed workshop (exportable, serializable)
- [ ] Consumer-pattern documentation distinguishes the two valid shapes explicitly
- [ ] Arneson's identity/README flags that skipping the workshop is a misuse pattern

**Dependencies:** FR-C1, FR-C2

> **Sources**: 0xHoneyJar/construct-arneson#2 (text-embed vs workshop misuse pattern, filed by consumer, self-corrected); Phase 4 (2026-05-12)

#### FR-C9: Session Distillation (`/distill`)
**Priority:** Must Have
**Description:** Compress any session's transcript+sidecar into a downstream-consumable format, configured per domain's consumer specification. In the TTRPG vertical, this means Gygax-ingestible digest. In other domains, the consumer spec defines the shape.

**Acceptance Criteria:**
- [ ] Reads transcript + sidecar pair for any domain
- [ ] Applies domain's consumer specification to shape output
- [ ] Output validates against domain's expected digest format
- [ ] Produces useful output even without a consumer spec (generic structured summary)
- [ ] Identifies: key moments, persona signals, state conflicts, unresolved questions

**Dependencies:** FR-C5 (transcript+sidecar), FR-C6 (domain consumer spec)

> **Sources**: v1 FR-8 (`/distill`); teammate feedback §5 (`/distill` as composition glue)

### TTRPG Vertical Requirements (Reference Implementation)

#### FR-T1: `/braunstein` — Live Playtest Session
**Priority:** Must Have
**Description:** Flagship TTRPG skill. User GMs, Arneson plays an archetype (from Gygax's cabal definitions or fallback bundle) as an actual character. Dialogue, in-character reactions, dice rolls, real-time experience signal capture. Named after Arneson's 1969 proto-RPG.

**Acceptance Criteria:**
- [ ] Archetype loads from Gygax (if installed) or fallback bundle (standalone)
- [ ] State machine: SETUP → ARCHETYPE_SELECT → GAME_STATE_LOAD → INTENT_READ → SAFETY_AGREEMENT → ACTIVE_PLAY → WRAP_UP
- [ ] Dice resolution: user-configurable (user rolls / Arneson rolls / hybrid), default user rolls
- [ ] Intent-aware: `non_negotiable: true` mechanics played into, not against
- [ ] Experiential intent shapes narrative tone (desperate, triumphant, eerie, etc.)
- [ ] Produces transcript + sidecar pair per FR-C5
- [ ] Composition detection: checks for `grimoires/gygax/` at session start

**Dependencies:** FR-C1, FR-C2, FR-C3, FR-C4, FR-C5

> **Sources**: issue-3:73 (`/braunstein`); v1 FR-1; NOTES.md teammate feedback §1-4

#### FR-T2: `/voice` — NPC Workshop Dialogue
**Priority:** Must Have
**Description:** Embody a specific NPC for workshop-style dialogue. Arneson stays in character until the session ends. NPC state persists in `grimoires/arneson/voices/npcs/`.

**Acceptance Criteria:**
- [ ] NPC voice loads from voice definition (voice-npc schema)
- [ ] Voice is consistent with defined speech patterns, emotional register, knowledge level
- [ ] Workshop loop: practitioner speaks → Arneson responds in-character → iterate
- [ ] NPC state updates persist across workshop sessions

**Dependencies:** FR-C1, FR-C2

> **Sources**: issue-3:74; v1 FR-2; concept:42-44

#### FR-T3: `/scene` — Scene Generation
**Priority:** Must Have
**Description:** Generate a scene from game-state + seed (prompt, oracle table output, or state reference). Produces opening situation, sensory detail, immediate stakes. Grounded in game-state.

**Acceptance Criteria:**
- [ ] Reads game-state for grounding (locations, factions, tensions, constraints)
- [ ] Tradition-aware: adapts tone and detail to the game's tradition (if Gygax provides tradition lore)
- [ ] Scene includes: opening hook, sensory detail, immediate stakes
- [ ] Output is presentable markdown (grimoire-as-deliverable)

**Dependencies:** FR-C1, FR-C5

> **Sources**: issue-3:75-76; v1 FR-3; concept:46-47

#### FR-T4: `/narrate` — Fiction-Mechanics-Fiction Bridge
**Priority:** Must Have
**Description:** When a mechanic fires, generate the "new fiction" that flows from it. Implements the PbtA-derived fiction-mechanics-fiction loop. Callable by `/braunstein` and `/improvise`.

**Acceptance Criteria:**
- [ ] Reads mechanical outcome and current narrative context
- [ ] Generates fiction that bridges the mechanical result back into the narrative
- [ ] Intent-aware: respects `non_negotiable` and experiential intent
- [ ] Usable as a primitive by other skills (not just standalone)

**Dependencies:** FR-C1

> **Sources**: issue-3:76-77; v1 FR-4; concept:48-50

#### FR-T5: `/improvise` — Arneson GMs, User Plays PC
**Priority:** Must Have
**Description:** Inverse of `/braunstein`. Arneson runs the world, voices NPCs, interprets mechanics into fiction. User plays a PC. For testing the GM-facing side of a design.

**Acceptance Criteria:**
- [ ] Arneson GMs: sets scenes, voices NPCs, resolves mechanics into fiction
- [ ] User plays as PC: provides character actions, makes decisions
- [ ] Same session infrastructure as `/braunstein` (transcript + sidecar, safety, intent)
- [ ] Grounded in game-state (NPCs, locations, factions, mechanics)

**Dependencies:** FR-C1, FR-C2, FR-T4

> **Sources**: issue-3:77-78; v1 FR-5; concept:52-53

#### FR-T6: `/fragment` — Setting Material Generation
**Priority:** Should Have
**Description:** Generate setting fragments (locations, histories, factions, NPC sketches) grounded in game-state and tradition. Low-effort, high-value for designers building worlds.

**Acceptance Criteria:**
- [ ] Generates: locations, histories, factions, NPC sketches
- [ ] Grounded in existing game-state (no contradictions)
- [ ] Tradition-aware: adapts tone to the game's tradition
- [ ] Outputs presentable markdown to `grimoires/arneson/fragments/`

**Dependencies:** FR-C1, FR-C5

> **Sources**: issue-3:207; v1 FR-7

#### FR-T7: Two-Axis Intent
**Priority:** Must Have
**Description:** Experiential intent (how it should feel) + mechanical intent (what the math should do). Arneson owns experiential_intent; Gygax owns mechanical_intent. Arneson reads both axes. Never fudges fiction to overrule mechanical intent.

**Acceptance Criteria:**
- [ ] `experiential_intent.schema.yaml` defines: tone, pacing, stakes, register
- [ ] Both axes are read before any TTRPG session begins
- [ ] When intent changes (Lethal → Heroic), voicing shifts without manual prompt-tuning
- [ ] Mechanical intent is never overridden by narrative preference

**Dependencies:** None (schema-level concern)

> **Sources**: NOTES.md teammate feedback §2; v1 FR-9

#### FR-T8: Archetype Memory
**Priority:** Must Have
**Description:** 3-session sliding window for archetype memory. The Newcomer who was confused last session carries that memory. Archetype identity never fully extinguishes — the Newcomer remains a Newcomer regardless of experience.

**Acceptance Criteria:**
- [ ] Memory window configurable (default: 3 sessions)
- [ ] Recent sessions inform current behavior
- [ ] Core archetype identity persists regardless of accumulated experience
- [ ] Memory state stored in `grimoires/arneson/voices/archetypes/*.yaml`

**Dependencies:** FR-C1

> **Sources**: issue-3:139-141; v1 FR-10; concept:107-108

#### FR-T9: Gygax Composition
**Priority:** Should Have (amplification, not dependency)
**Description:** When Gygax is installed, Arneson reads game-state, archetype definitions, intent fields, and tradition lore from Gygax's grimoire. Arneson writes transcripts and voice state that Gygax can analyze. When Gygax is not installed, Arneson uses fallback archetypes and functions standalone.

**Acceptance Criteria:**
- [ ] Composition detection: checks for `grimoires/gygax/` at startup
- [ ] Reads: `grimoires/gygax/game-state/`, `skills/cabal/resources/archetypes.yaml`, intent fields, tradition lore
- [ ] Writes: `grimoires/arneson/sessions/*.md` consumable by `/cabal --from-session`
- [ ] Standalone mode: fallback archetype bundle in `resources/archetypes-fallback/`
- [ ] Gygax is never required — composition is opt-in amplification

**Dependencies:** None (standalone-plus-composable)

> **Sources**: issue-3:79-101; concept:59-69; NOTES.md (standalone-plus-composable decision)

### Cross-Domain Requirements

#### FR-X1: Persona Portability
**Priority:** Nice to Have
**Description:** A voice definition created in one domain can be loaded in another. The core voice schema (voice-base) is domain-agnostic; domain-specific extensions layer on top. A TTRPG NPC could be imported as a game-writing character; an agent persona could be tested in a TTRPG session.

**Acceptance Criteria:**
- [ ] Voice-base fields are readable by any domain's hosting engine
- [ ] Domain-specific extension fields are ignored (gracefully) when loaded in a different domain
- [ ] Persona memory does not transfer across domains (clean slate in new context)
- [ ] Portability is opt-in, not automatic

**Dependencies:** FR-C1, FR-C6

> **Sources**: Phase 4 (2026-05-12) — agent recommendation, confirmed by user

---

## Non-Functional Requirements

### Extensibility

- **NFR-1**: Adding a domain vertical requires zero changes to Arneson core code. The extension interface is the primary architectural constraint.
- **NFR-2**: All schemas use base + extension pattern. Base schemas are core; extensions are domain-provided. No domain-specific fields in base schemas.

> **Sources**: Phase 5 (2026-05-12); G-3

### Resilience

- **NFR-3**: Graceful degradation — if domain configuration is incomplete, Arneson falls back to sensible defaults (structural improvisation + user confirmation). Missing persona definitions → generic voice. Missing event taxonomy → base events only. Missing resolution mechanics → no resolution (pure narrative).
- **NFR-4**: If Gygax is not installed, all TTRPG capabilities work via fallback bundle. No error, no degraded UX — just standalone mode.

> **Sources**: v1 decisions (tradition fallback = structural improvisation); Phase 5 (2026-05-12)

### Safety

- **NFR-5**: Safety is non-negotiable. Every domain, every session, every mode. No opt-out. No "skip safety for this session" option.
- **NFR-6**: Safety triggers are data, not just interruptions. Every safety event is captured in the sidecar as a finding.

> **Sources**: issue-3:131-133; v1 FR-15; NOTES.md teammate feedback §4

### Output Quality

- **NFR-7**: All output is simultaneously human-readable AND machine-parseable. Transcripts are presentable standalone markdown. Sidecars are valid YAML.
- **NFR-8**: Grimoire-as-deliverable: every session transcript, every voiced persona, every generated scene is saved as presentable, exportable markdown.

> **Sources**: Phase 2 (dual-audience); issue-3:135 (grimoire-as-deliverable)

### Compatibility

- **NFR-9**: Construct validates at L0/L1/L2 (Loa construct validation levels).
- **NFR-10**: CI workflow validates all schemas, all verticals, standalone and composed modes.

> **Sources**: issue-3:192; v1 CI design

---

## User Experience

### Key User Flows

#### Flow 1: First Session (TTRPG)
```
/braunstein --newcomer → Safety Agreement → Game State Load → Intent Read → Active Play → Wrap Up → Transcript + Sidecar
```

#### Flow 2: Voice Workshop
```
/voice {character-id} → Safety Agreement → Workshop Dialogue → Iterate → End Session → Voice State Updated
```

#### Flow 3: Extend Arneson (New Domain)
```
Create domain files → Place in domain directory → Arneson discovers domain → Domain skills available → Run session → Domain-shaped output
```

### Interaction Patterns

- **Director/performer**: Practitioner always directs. Arneson always performs within their constraints.
- **Session-based**: All creative work happens within sessions. Sessions have explicit start/end.
- **Paired output**: Every session produces transcript + sidecar. The practitioner reads the transcript; tools read the sidecar.
- **Safety-first**: Safety agreement before any creative generation. Safety commands available at all times during session.

---

## Technical Considerations

### Architecture Notes

The core architectural shift from v1 to v2 is extracting a **domain-agnostic core** from TTRPG-specific code:

- **Core**: Persona hosting engine, session management, sidecar event schema (base), safety infrastructure, transcript+sidecar output, distillation engine, status dashboard
- **Domain vertical**: Structured state format, persona definitions, event taxonomy extensions, resolution mechanics, consumer specification
- **Extension interface**: Convention-based discovery with maximum practitioner flexibility (exact mechanism TBD in SDD)

The existing v1 codebase provides the reference implementation. The refactoring is primarily reorganization (clean separation of concerns), not rewrite — the codebase is clean (hygiene A) and the core capabilities are already more general than their TTRPG framing.

### Integrations

| System | Integration Type | Purpose | Required |
|--------|------------------|---------|----------|
| Gygax | Grimoire composition | TTRPG grounding (game-state, archetypes, intent, tradition) | No (opt-in) |
| Loa framework | Construct runtime | Skill invocation, grimoire management, CI | Yes |
| Domain verticals | Extension interface | Domain-specific capabilities | At least 1 (TTRPG ships as reference) |

### Technical Constraints

- Loa framework construct schema v3
- YAML for all structured data (schemas, state, configuration)
- Markdown for all prose output (transcripts, scenes, fragments)
- Filesystem-first architecture (no database, no server — grimoire IS the persistence)

---

## Scope & Prioritization

### In Scope (v2)

| Feature | Priority | Effort | Impact |
|---------|----------|--------|--------|
| Extract domain-agnostic core from TTRPG code | P0 | L | High |
| Define domain extension interface | P0 | M | High |
| Reframe identity layer (ARNESON.md, persona.yaml, refusals.yaml) | P0 | S | High |
| TTRPG vertical as reference implementation | P0 | M | High |
| Validate extension story (hypothetical second domain) | P0 | M | High |
| Base sidecar schema (domain-agnostic events) | P1 | M | Medium |
| Persona portability (FR-X1) | P2 | S | Low |
| Governance docs (CONTRIBUTING.md, SECURITY.md, CODEOWNERS) | P2 | S | Low |

### In Scope (Future / v3+)

- Ship a second domain vertical (game-writing or agent persona dev)
- Cross-domain workflows (output from one domain consumed by another)
- Domain marketplace / community verticals
- Campaign arc modeling beyond 3-session memory window
- Player-facing UX (practitioner-only in v2)

### Explicitly Out of Scope

- **Autonomous mode** — Arneson does not self-direct. Director/performer holds. (Reason: scope discipline; autonomy is a fundamentally different interaction model)
- **Shipping a second domain vertical** — the extension point ships, not a second vertical. (Reason: the proof is in the interface quality, not in building multiple domains ourselves)
- **Player-facing UX** — no end-user interaction. Practitioner-only. (Reason: same as v1; player UX is a v3+ concern)
- **Runtime dependencies on Gygax** — standalone-plus-composable. No Gygax required. (Reason: load-bearing design principle)

---

## Success Criteria

### Launch Criteria

- [ ] Domain-agnostic core is cleanly separated from TTRPG vertical
- [ ] Extension interface is defined and documented
- [ ] TTRPG vertical works as reference implementation (all v1 acceptance criteria pass)
- [ ] Extension story validated: a hypothetical domain vertical can be added with zero core code changes
- [ ] Identity layer reframed around creative persona engine (not Gygax-inverse)
- [ ] Safety infrastructure works across any domain context
- [ ] All output is dual-audience (human-readable + machine-parseable)
- [ ] Construct validates at L0/L1/L2
- [ ] CI passes (schemas, skills, standalone mode, composed mode)

### Post-Launch Validation

- [ ] A second domain vertical (game-writing, agent dev, or community-contributed) can be built using only the extension interface documentation
- [ ] No core code changes required for the second vertical
- [ ] Community feedback on extension interface usability

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **R-1: Over-abstraction** — making everything generic breaks the TTRPG vertical that already works | Medium | High | TTRPG is the reference implementation and regression test. If it breaks, the abstraction is wrong. All v1 acceptance criteria must continue to pass. |
| **R-2: Extension point too narrow** — designed around TTRPG patterns, doesn't actually fit other domains | Medium | High | Validate the interface against at least 2 hypothetical domains (game-writing, agent-dev) during architecture. Paper-test before code. |
| **R-3: Extension point too wide** — so generic it provides no value, no conventions, no guardrails | Medium | Medium | The extension interface should provide useful defaults and conventions. "Convention-based with sensible defaults" not "empty plugin API." |
| **R-4: Identity reframe weakens Arneson's voice** | Low | Medium | The Gygax-inversion is one facet of a broader identity, not removed entirely. Sprint 0 prototype quality (5/5 axes) is the regression bar. |
| **R-5: Existing code requires more refactoring than expected** | Low-Medium | Medium | The codebase is clean. Most changes are reorganization. Start with the boundary that requires least code movement. |
| **R-6: Schema generalization creates backwards incompatibility** | Low | Medium | Base+extension pattern preserves existing schemas. TTRPG-specific fields move to extensions; base fields remain stable. |

### Assumptions

- [ASSUMPTION] The existing voice-base + extension schema pattern generalizes well to non-TTRPG persona definitions. (If wrong: need a new base schema, moderate rework.)
- [ASSUMPTION] Convention-based discovery is sufficient for domain verticals — no formal manifest needed at v2. (If wrong: add a domain.yaml manifest, small effort.)
- [ASSUMPTION] The 5-part domain interface (state, personas, events, resolution, consumer) is complete. (If wrong: missing interface components surface during extension story validation.)

### Dependencies on External Factors

- Loa framework stability (construct schema v3 must remain stable)
- Gygax v3 archetype/intent interface stability (for TTRPG vertical composition)

---

## Milestones

Quality-driven — no fixed dates. Ordered by dependency.

| Milestone | Deliverables | Depends On |
|-----------|--------------|------------|
| M-1: Core/Vertical Boundary | Domain-agnostic core extracted. TTRPG vertical isolated. Extension interface defined. | — |
| M-2: Identity Reframe | ARNESON.md, persona.yaml, refusals.yaml reframed for creative persona engine. | M-1 |
| M-3: Schema Generalization | Base sidecar schema + TTRPG extensions. Voice-base confirmed domain-agnostic. | M-1 |
| M-4: TTRPG Regression | All v1 acceptance criteria pass against the refactored codebase. CI green. | M-1, M-3 |
| M-5: Extension Story | Hypothetical second domain validated against the extension interface. Zero core changes. | M-1, M-3, M-4 |
| M-6: Documentation & Governance | Extension interface documented. Consumer-pattern guide (workshop vs text-embed shapes). CONTRIBUTING.md, SECURITY.md, CODEOWNERS added. | M-5 |
| M-7: Release | Construct validates L0/L1/L2. Tagged release. | All |

---

## Appendix

### A. Real-World Consumer Evidence

Two issues provide grounding for the v2 generalization — they show arneson already being used (and misused) beyond its original TTRPG framing:

**0xHoneyJar/construct-arneson#2** — "doc clarity: workshop tool vs text-embed"
A consumer (zksoju) building a Discord persona-bot extracted arneson's voice doctrine into a static `SKILL.md` prompt instead of invoking `/voice` as an iterative workshop. Self-corrected: the docs were clear, the misuse was operator-side. But the pattern reveals that the **iteration loop is the product** — not the doctrine itself. Informed FR-C8 (workshop-then-serialize pattern) and consumer-pattern documentation.

**0xHoneyJar/construct-mibera-codex#76** — "construct-mongolian: curator authoring (Track A)"
The first real instance of the "mibera-as-npc" doctrine — a Grail entity (The Mongolian) becoming a Discord agent with curator-authored voice + judgment rubric. arneson's `/voice` workshop is proposed as the convergence instrument. The two-tier architecture (construct judges / substrate verifies) maps to arneson's director/performer model. This IS the agent-persona-development vertical in early production use. Informed UC-4 grounding.

### B. v1 Cycle Context

The v1 cycle (2026-04-13) produced:
- PRD v1 (853 lines, 17 FRs)
- SDD (1,150 lines, filesystem-first skill graph architecture)
- Sprint plan (7 sprints)
- Sprint 1 implemented and reviewed (identity layer, 7 schemas, 9 archetypes, 8 skill scaffolds, CI workflow, synthetic fixture)
- Sprint 0 prototype (hand-authored `/braunstein` turn, self-critique 5/5 axes)

Key v1 decisions that carry forward:
- Standalone-plus-composable (load-bearing design principle)
- No HEKATE references in shippable files
- Safety is non-negotiable
- Grimoire-as-deliverable
- Director/performer interaction model

Key v1 decisions revised in v2:
- Identity: was "Gygax's inverse" → now "creative persona engine with Gygax-inversion as one facet"
- Scope: was "TTRPG-only" → now "domain-agnostic core with TTRPG as reference vertical"
- Success metric: was "admissibility (Gygax can re-analyze)" → now "persona believability + structured output fidelity + extension story"
- Audience: was "Gygax community / TTRPG designers" → now "creative practitioners broadly"

### C. Historical Naming

The construct is named for **Dave Arneson** (1947-2009), co-creator of Dungeons & Dragons. Arneson brought improvisational GMing, the campaign structure, and collaborative fiction-within-rules to the hobby Gary Gygax then codified. The name evokes the fiction-generating, improvisational, persona-hosting side of creative work — a meaning that transcends TTRPG into any domain where personas do grounded creative generation.

### D. Glossary

| Term | Definition |
|------|------------|
| **Creative persona engine** | A tool that hosts personas grounded in structured state and emits structured data from creative sessions |
| **Structured state** | Practitioner-provided data that grounds creative generation (game state, story bible, behavioral spec, world lore) |
| **Sidecar** | Machine-parseable YAML file paired with a human-readable transcript, capturing structured events from a session |
| **Domain vertical** | A configuration package that adapts Arneson to a specific creative domain (TTRPG, game-writing, agent-dev) |
| **Extension point** | The interface through which new domain verticals plug into Arneson core |
| **Director/performer** | Interaction model where the practitioner directs and Arneson performs within their constraints |
| **Admissibility** | (TTRPG-specific) A session transcript trustworthy enough for Gygax to re-analyze as evidence |
| **Persona portability** | The ability to load a voice definition created in one domain into another domain |
| **Braunstein** | Dave Arneson's 1969 proto-RPG that led to D&D; namesake for the flagship TTRPG session skill |

---

*Generated by PRD Architect Agent (/plan-and-analyze), 2026-05-12*
