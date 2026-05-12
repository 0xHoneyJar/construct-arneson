# Product Requirements Document: construct-arneson v3

**Version:** 3.0
**Date:** 2026-05-12
**Author:** PRD Architect Agent (/plan-and-analyze)
**Status:** Draft
**Predecessor:** PRD v2 (2026-05-12) — creative persona engine architecture

> **Sources used across this document:**
> - `grimoires/loa/context/v3-humanness-layer.md` (v3 direction doc)
> - `grimoires/loa/context/kizuna-caretakers-reference.md` (KIZUNA QA pack)
> - KIZUNA caretaker gist (zkSoju/2c359e8fc7315bc00190e0b337d80949)
> - `/voice akane` workshop session, 2026-05-12
> - 0xHoneyJar/construct-arneson#2 (text-embed vs workshop misuse pattern)
> - 0xHoneyJar/construct-mibera-codex#76 (construct-mongolian agent persona)
> - /plan-and-analyze discovery interview, 2026-05-12

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

**construct-arneson v3** adds the **humanness layer** to the creative persona engine. v2 built the architecture for hosting personas grounded in structured state. v3 makes those personas feel human by giving them the behavioral infrastructure to vary their engagement, avoid LLM surface tells, respond minimally or not at all, and have topics they care about versus topics they ghost.

Three problems surfaced during a `/voice akane` workshop session with the KIZUNA caretakers (5 Discord personas for the purupuru world):

1. **LLM anti-patterns** break immersion. The emdash (`---`) is the biggest tell. So are phrases like "That's a great question!" and perfect grammar in casual contexts.
2. **Obligatory responsiveness** makes personas feel robotic. Every input getting a full response is not how humans work. Real characters have engagement thresholds.
3. **Silence has no representation.** When a persona chooses not to respond, that decision is invisible. But the absence of response IS data --- it tells you what the persona cares about.

v3 also ships the **character-voice domain vertical** (`domains/character-voice/`) --- the first non-TTRPG vertical, proving the v2 extension interface works in production. Akane (KIZUNA, Fire element) is the reference fixture.

> **Sources**: v3-humanness-layer.md, workshop session 2026-05-12, kizuna-caretakers-reference.md

---

## Problem Statement

### The Problem

Arneson v2 can host personas, ground them in structured state, and emit structured data. But the personas it produces still *feel like chatbots*. Three surface-level behaviors betray the illusion:

**1. LLM punctuation and phrasing tells.** The emdash, the hedge ("It's worth noting..."), the filler ("That's a great question!"), the assistant-mode leak ("I cannot help with that"). These are recognizable patterns that break immersion instantly for anyone who has spent time with AI-generated text.

> From v3-humanness-layer.md:15: "The `---` emdash is the single biggest tell that output is AI-generated."

**2. Always-on responsiveness.** Every prompt gets a full, engaged, in-voice response. Real humans don't work this way. Akane wouldn't dignify a question about data with a full sentence. Nemu might just... not answer. The current architecture has no concept of "this persona doesn't care enough to respond."

> From v3-humanness-layer.md:22: "Not every input deserves a response."

**3. Invisible non-engagement.** When a persona *would* choose not to respond, there's no way to represent that choice. No sidecar event, no consumer signal, no workshop data. The decision to not-engage is lost.

> From v3-humanness-layer.md:30: "When a persona chooses not to respond, that IS data"

### Why This Matters Now

The KIZUNA caretakers are shipping to a Discord community. Real users will interact with these personas daily. The gap between "technically grounded voice" and "feels like a person" is exactly these three problems. The gist author's QA prompts (QA-PROMPTS.md) include stress tests designed to catch exactly these failures.

> **Sources**: v3-humanness-layer.md, kizuna-caretakers-reference.md, workshop session

---

## Goals & Success Metrics

### Primary Goals

| ID | Goal | Measurement | Validation |
|----|------|-------------|------------|
| G-1 | **Anti-pattern suppression** | Zero emdashes, zero assistant-mode leaks, zero filler phrases in hosted persona output | Automated scan of session transcripts against anti-pattern list |
| G-2 | **Engagement model works** | Personas have measurably different engagement profiles across prompt types | Run KIZUNA QA prompts against Akane, verify she ghosts data questions and engages on risk |
| G-3 | **Silence is instrumented** | `chose_not_to_respond` events appear in sidecars with reasoning | Sidecar contains non-response events for low-engagement prompts |
| G-4 | **v2 regression** | All v2 capabilities pass unchanged | CI green, all 10 schemas validate, extension story passes |
| G-5 | **Character-voice vertical ships** | Second domain vertical works via extension interface, zero core changes beyond schema additions | CI extension-story validates character-voice domain |

### Timeline

Quality-driven, no fixed date. Carrying from v2.

> **Sources**: Phase 2 synthesis, v3-humanness-layer.md

---

## User Personas & Use Cases

### Primary Persona: The Voice Curator

Carried from v2 (creative practitioner broadly), sharpened by the KIZUNA case:

**gumi** --- iterating Discord character voices until "yes, that's Akane." Tests each persona against canon battle whispers. Captures voice friction when something feels off. The bar is not "sounds good" but "sounds like *them*."

### Use Cases

#### UC-1: Workshop a Discord Persona (Akane)
**Actor:** Voice curator
**Preconditions:** Canon exists (lore-bible, battle whispers). Voice-state YAML created.
**Flow:**
1. Curator invokes `/voice akane`
2. Arneson loads Akane's voice-state + grounding canon
3. Curator sends test prompts (from QA-PROMPTS.md)
4. Arneson responds in Akane's voice --- short, explosive, ALL CAPS for hits
5. On boring prompts (data, planning), Akane's engagement model triggers: minimal response or silence
6. Sidecar captures: dialogue events, engagement decisions, non-response events
7. Curator reviews: "did she ghost the boring ones? did she fire up on the risky ones?"

**Acceptance Criteria:**
- [ ] Akane never uses emdash
- [ ] Akane responds minimally or not at all to data/planning prompts
- [ ] Akane responds with HIGH energy to risk/action prompts
- [ ] Sidecar captures `chose_not_to_respond` for ghosted prompts
- [ ] Voice matches canon battle whispers register

#### UC-2: Silence as Workshop Signal
**Actor:** Voice curator
**Preconditions:** Workshop session in progress.
**Flow:**
1. Curator sends 10 test prompts across different topics
2. Persona responds fully to 6, minimally to 2, silently to 2
3. Curator reviews sidecar: the 2 silences reveal what the persona doesn't care about
4. This informs voice refinement --- "Akane should ghost this topic but engage on that one"

**Acceptance Criteria:**
- [ ] Sidecar shows engagement distribution across prompts
- [ ] Non-response events include reasoning ("low engagement: topic is data/planning")
- [ ] Workshop convergence tracking includes engagement pattern data

---

## Functional Requirements

### Humanness Layer (Core)

#### FR-H1: Anti-Pattern Protocol
**Priority:** Must Have
**Description:** Core-level LLM tell suppression applied to ALL personas Arneson hosts. Configurable anti-pattern list enforced at the protocol level.

**Default anti-patterns (banned from all persona output):**
- `---` (emdash --- use `...` or `-` or sentence break instead)
- "I cannot help with that" / "I'm not able to" (assistant-mode leak)
- "As an AI" / "As a language model" (identity leak)
- "That's a great question!" / "Great question!" (filler)
- "It's worth noting that" / "It's important to note" (hedge)
- "I'd be happy to" / "I'd love to help" (servile framing)
- "Certainly!" / "Absolutely!" / "Of course!" (over-affirmation)
- Perfect grammar in a persona defined as casual/colloquial

**Acceptance Criteria:**
- [ ] Anti-pattern list defined in a core protocol or schema
- [ ] List is configurable (personas can add domain-specific anti-patterns)
- [ ] Enforcement is at protocol level, not advisory
- [ ] Scan tool can audit transcripts against the list

**Dependencies:** None (protocol-level)

> **Sources**: v3-humanness-layer.md:15-17, workshop session

#### FR-H2: Engagement Model
**Priority:** Must Have
**Description:** Per-persona engagement threshold with topic sensitivity. Determines whether a persona responds fully, minimally, or not at all --- BEFORE generation begins.

**Schema additions to voice-base:**
```yaml
engagement:
  default_mode: enum [full, minimal, silence]  # default response mode
  threshold: float (0.0-1.0)                   # how much prompting before full engagement
  high_topics: list[string]                     # topics that pull engagement UP
  low_topics: list[string]                      # topics that push engagement DOWN
  minimal_vocabulary: list[string]              # what this persona says when barely engaging
```

**Engagement decision flow:**
1. Prompt arrives
2. Engagement model evaluates: does this topic match `high_topics`, `low_topics`, or neither?
3. Combined with `threshold` and `default_mode`, determines response mode
4. If `silence`: no output generated, sidecar captures decision event
5. If `minimal`: generate from `minimal_vocabulary` only
6. If `full`: generate normally

**Acceptance Criteria:**
- [ ] voice-base schema includes `engagement` field block
- [ ] Engagement decision happens before generation
- [ ] Different personas produce measurably different engagement distributions
- [ ] Akane ghosts data/planning prompts, fires on risk/action prompts
- [ ] Nemu defaults to minimal, with rare full engagement

**Dependencies:** FR-H3 (silence instrumentation)

> **Sources**: v3-humanness-layer.md:22-40, kizuna-caretakers-reference.md (engagement profiles table)

#### FR-H3: Silence Instrumentation
**Priority:** Must Have
**Description:** New `chose_not_to_respond` event in session-events-base. When a persona decides not to engage, the decision is captured as structured data.

**Event schema:**
```yaml
chose_not_to_respond:
  persona: string (required)
  prompt_summary: string (required)    # what they were asked
  reason: string (required)            # why they didn't engage
  engagement_score: float              # how close they were to engaging
  mode: enum [silence, delayed]        # how the non-response manifests
```

**Acceptance Criteria:**
- [ ] Event type exists in session-events-base schema
- [ ] Sidecar captures the event when a persona chooses not to respond
- [ ] Event includes reasoning (not just "didn't respond")
- [ ] `/distill` includes non-response patterns in digest

**Dependencies:** None (schema addition)

> **Sources**: v3-humanness-layer.md:30-38

#### FR-H4: Minimal Response Mode
**Priority:** Should Have
**Description:** Between full response and silence. The persona acknowledges presence without engaging substantively. Per-persona minimal vocabulary.

**Examples by persona:**
- Akane: "mhm." / "okay." / (single emoji-equivalent)
- Nemu: "..." / "mm." / (silence that becomes presence)
- Ren: "noted." / "different domain."
- Ruan: (a beat, then nothing)

**Acceptance Criteria:**
- [ ] `engagement.minimal_vocabulary` field in voice-base
- [ ] Minimal responses stay in-voice (not generic)
- [ ] Sidecar captures minimal responses as `dialogue` events with `engagement_mode: minimal` tag
- [ ] Minimal responses are SHORT (1-3 words max)

**Dependencies:** FR-H2 (engagement model)

> **Sources**: workshop session, kizuna decline patterns

#### FR-H5: Workshop Engagement Tracking
**Priority:** Should Have
**Description:** During `/voice` workshop sessions, track which prompts the persona engages with, minimally responds to, and ghosts. This is convergence data that tells the curator what the persona cares about.

**Acceptance Criteria:**
- [ ] Workshop summary includes engagement distribution (N full / M minimal / K silent)
- [ ] Per-topic engagement is visible ("risk: 5/5 full, data: 0/5 full, 3/5 silent")
- [ ] Convergence notes can reference engagement patterns
- [ ] This data informs voice refinement ("Akane should ghost this topic")

**Dependencies:** FR-H2, FR-H3

> **Sources**: v3-humanness-layer.md:45-47

#### FR-H6: Character Tensions
**Priority:** Should Have
**Description:** A `tensions` field in voice-base capturing small, character-consistent contradictions that make a persona feel layered rather than flat. Humans contradict themselves. Akane says "i don't plan" but she clearly cased that abandoned building before breaking in. Ruan says "numbers feel cold" but tracks her BPM obsessively when producing. These are voice instructions, not runtime state --- they tell any system rendering this persona where the internal friction lives.

**Schema addition to voice-base:**
```yaml
tensions:
  type: array
  required: false
  items:
    type: object
    fields:
      says: string        # what the persona claims about themselves
      does: string        # what they actually do that contradicts it
      context: string     # when this surfaces
```

**Acceptance Criteria:**
- [ ] `tensions` field in voice-base schema
- [ ] Field is optional (not all personas need contradictions)
- [ ] Akane fixture includes at least 2 tensions
- [ ] Workshop can surface tensions as convergence data ("she says X but does Y")

**Dependencies:** None (schema addition)

> **Sources**: workshop session 2026-05-12, design discussion

---

### Character-Voice Domain Vertical

#### FR-D1: Character-Voice Domain
**Priority:** Should Have
**Description:** `domains/character-voice/` --- the second domain vertical. Schemas for Discord persona authoring extending voice-base with: voice anchors (canon lines), discipline locks (behavioral rules like Navigator pattern), canon boundaries (what the persona knows/doesn't), sibling relationships (yield maps), decline patterns (in-voice refusals), and mode definitions (greeting, lore, siblings, etc.).

**Five-part contract implementation:**
1. **Structured state**: Canon documents (lore-bible, battle whispers, world references)
2. **Persona definitions**: `voice-character.schema.yaml` extending voice-base with voice anchors, discipline locks, modes, yields, declines, canon boundary
3. **Event taxonomy**: `session-events-character.schema.yaml` with voice-drift events, canon-match events, engagement tracking
4. **Resolution mechanics**: Workshop iteration (compare to canon, refine, converge)
5. **Consumer specification**: System prompt template generation (serialized for Discord bot)

**Acceptance Criteria:**
- [ ] `domains/character-voice/` directory with all 5 contract parts
- [ ] Schemas extend core (voice-base, session-events-base, digest-base)
- [ ] Zero core files modified (extension story constraint)
- [ ] `domain.conventions.md` documents the vertical

**Dependencies:** v2 extension interface (shipped)

> **Sources**: kizuna-caretakers-reference.md, workshop session, gist persona.md structure

#### FR-D2: Akane Reference Fixture
**Priority:** Should Have
**Description:** Akane (KIZUNA, Fire element, Naughty) as a complete character-voice persona conforming to the domain vertical schemas. Proves the vertical works end-to-end.

**Acceptance Criteria:**
- [ ] `akane.yaml` conforms to `voice-character.schema.yaml`
- [ ] Canon grounding state (lore-bible excerpt, battle whispers) included
- [ ] Workshop session can run against the fixture
- [ ] Engagement model produces expected behavior (ghosts data, fires on risk)
- [ ] Anti-pattern protocol enforced (no emdashes in output)

**Dependencies:** FR-D1, FR-H1, FR-H2

> **Sources**: KIZUNA gist akane.md, workshop session, akane.yaml (grimoires/arneson/voices/npcs/)

---

## Non-Functional Requirements

### Enforcement

- **NFR-H1**: Anti-pattern enforcement is protocol-level, not advisory. A persona that outputs an emdash has violated its contract. The anti-pattern list is auditable.
- **NFR-H2**: Engagement decisions happen BEFORE generation, not after. The persona decides whether to engage, then generates (or doesn't). This saves compute and prevents "generate then discard."
- **NFR-H3**: Silence must not break consumer integrations. The output contract includes "no output" as a valid state. Consumers must handle null gracefully.

### Regression

- **NFR-R1**: All v2 capabilities pass unchanged. The humanness layer is additive to voice-base, session-events-base, and protocols. No existing fields removed or changed.

---

## User Experience

### Engagement Decision Flow

```
Prompt arrives
    ↓
Engagement model evaluates
    ↓
┌─────────────┬──────────────┬──────────────┐
│ HIGH topic   │ NEUTRAL      │ LOW topic    │
│ → full mode  │ → default    │ → minimal    │
│              │   mode       │   or silence │
└─────┬───────┴──────┬───────┴──────┬───────┘
      ↓              ↓              ↓
  Generate       Generate or    Log decision
  full response  minimal         to sidecar
  + sidecar      + sidecar      (no output)
```

---

## Technical Considerations

### Schema Changes (Additive)

**voice-base gains:**
- `engagement` field block (threshold, topics, modes, minimal vocabulary)
- `anti_patterns` field (persona-level additions to core anti-pattern list)

**session-events-base gains:**
- `chose_not_to_respond` event type

**New protocol:**
- `protocols/anti-patterns.md` --- LLM tell suppression rules

**New domain:**
- `domains/character-voice/` --- full five-part contract

### Backwards Compatibility

All changes are additive. `engagement` and `anti_patterns` are optional fields (`required: false`). Personas without engagement fields behave as before (always full response). The humanness layer is opt-in per persona but enforced when present.

---

## Scope & Prioritization

### In Scope (v3)

| Feature | Priority | Effort |
|---------|----------|--------|
| Anti-pattern protocol | P0 | S |
| Engagement model in voice-base | P0 | M |
| Silence instrumentation (chose_not_to_respond) | P0 | S |
| Minimal response mode | P1 | S |
| Workshop engagement tracking | P1 | M |
| Character-voice domain vertical | P1 | M |
| Akane reference fixture | P1 | S |

### Out of Scope

- **Full KIZUNA implementation** (all 5 caretakers) --- Akane only as proof
- **Consumer-side silence handling** --- that's the bot's problem, documented but not built
- **Engagement model auto-tuning** --- v4; v3 is manually configured per persona
- **Cross-persona chorus composition** --- v4+; each persona speaks independently
- **Anti-pattern enforcement at generation time** --- v3 is audit-based; v4 may add generation-time blocking

---

## Success Criteria

### Launch Criteria

- [ ] Anti-pattern protocol defined and auditable
- [ ] Engagement model fields in voice-base, demonstrated with Akane
- [ ] `chose_not_to_respond` event in session-events-base
- [ ] Character-voice domain vertical passes extension story validation
- [ ] Akane fixture produces expected engagement behavior
- [ ] All v2 CI passes (regression)
- [ ] Zero emdashes in any workshop session transcript

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Anti-pattern list too aggressive (suppresses legitimate voice) | Medium | Medium | List is configurable per-persona. Start conservative. Test against KIZUNA canon. |
| Engagement model produces too much silence (persona feels dead) | Medium | High | Default to full engagement. Silence is opt-in. Nemu is the extreme case, not the default. |
| Consumer can't handle null output | Low | Medium | Not Arneson's problem architecturally, but document the contract. Consumer must check for null. |
| Character-voice vertical is TTRPG-shaped in disguise | Medium | Medium | Validate against both KIZUNA (purupuru) AND Mongolian (mibera) use cases. |
| Engagement threshold is too coarse (0.0-1.0 number) | Low | Low | Can refine to qualitative in v4. Number works for v3 MVP. |

### Assumptions

- [ASSUMPTION] Engagement decisions can be made from prompt content alone (no conversation history needed). If wrong: need multi-turn engagement tracking, moderate rework.
- [ASSUMPTION] A single anti-pattern list works for all personas. If wrong: need per-persona override lists, small effort.
- [ASSUMPTION] `chose_not_to_respond` is sufficient for silence (no need for "delayed response" mechanics in v3). If wrong: add delay mode in v4.

---

## Milestones

Quality-driven, no fixed dates.

| Milestone | Deliverables | Depends On |
|-----------|-------------|------------|
| M-1: Anti-Pattern Protocol | `protocols/anti-patterns.md` defined. Anti-pattern list in voice-base or protocol. Audit script. | --- |
| M-2: Engagement Model | `engagement` fields in voice-base. Engagement decision flow in session-lifecycle protocol. | M-1 |
| M-3: Silence Instrumentation | `chose_not_to_respond` in session-events-base. Sidecar captures non-response. | M-2 |
| M-4: Minimal Response | `minimal_vocabulary` in voice-base. Minimal mode in engagement flow. | M-2 |
| M-5: Character-Voice Vertical | `domains/character-voice/` with schemas, conventions doc. Akane fixture. | M-2, M-3 |
| M-6: Workshop Enhancement | Engagement tracking in workshop sessions. Distribution visible in convergence data. | M-2, M-3 |
| M-7: Regression + Release | v2 CI green. v3 additions validated. Tagged release. | All |

---

## Appendix

### A. KIZUNA Engagement Profiles (from gist)

| Caretaker | Default Mode | High Topics | Low Topics |
|-----------|-------------|-------------|------------|
| Kaori | full (quiet) | garden, growth, seasons, siblings | data, finance, urgency |
| Nemu | minimal | quiet company, kitchen, Puru | urgency, planning, loud action |
| Akane | full (explosive) | risk, rooftops, daring, trouble | data, planning, finance, patience |
| Ren | full (analytical) | bears, analysis, Wuxing, citation | emotional content, urgency |
| Ruan | full (attuned) | feelings, music, emotional weather | logistics, data, planning |

### B. Anti-Pattern Reference

| Pattern | Why It Breaks Immersion | Replacement |
|---------|------------------------|-------------|
| `---` (emdash) | Biggest LLM tell | `...` or `-` or sentence break |
| "That's a great question!" | Filler, servile | Just answer (or don't) |
| "I cannot help with that" | Assistant-mode | In-voice decline pattern |
| "It's worth noting" | Hedge | State it or don't |
| "Certainly!" / "Absolutely!" | Over-affirmation | Respond naturally |
| Perfect grammar in casual voice | Register mismatch | Match the persona's grammar field |

### C. Predecessor Documents

- PRD v2 (2026-05-12): creative persona engine architecture
- SDD v2 (2026-05-12): core/vertical split, extension interface
- Sprint plan v2 (2026-05-12): 7 sprints, 34 tasks (completed)

---

*Generated by PRD Architect Agent (/plan-and-analyze), 2026-05-12*
