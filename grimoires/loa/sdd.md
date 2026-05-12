# Software Design Document: construct-arneson v3

**Version:** 3.0
**Date:** 2026-05-12
**Author:** Architecture Designer Agent (/architect)
**Status:** Draft
**PRD Reference:** `grimoires/loa/prd.md` (v3, 2026-05-12)
**Predecessor:** SDD v2 (2026-05-12) --- creative persona engine architecture

> v3 is a **delta document**. Only sections that change from v2 are specified here.
> For unchanged sections (directory structure, CI matrix, error handling, TTRPG vertical,
> grimoire state, inter-skill contracts, etc.), the v2 SDD remains canonical.

---

## What Changes in v3

| Area | Change Type | SDD Section |
|------|-------------|-------------|
| Anti-pattern protocol | NEW protocol | [1](#1-anti-pattern-protocol) |
| voice-base schema | EXTENDED (2 fields) | [2](#2-schema-changes) |
| session-events-base schema | EXTENDED (1 event type) | [2](#2-schema-changes) |
| digest-base schema | EXTENDED (1 findings section) | [2](#2-schema-changes) |
| Session lifecycle protocol | UPDATED (turn cycle) | [3](#3-protocol-updates) |
| Persona hosting protocol | UPDATED (engagement load) | [3](#3-protocol-updates) |
| Workshop convergence protocol | UPDATED (engagement tracking) | [3](#3-protocol-updates) |
| Character-voice domain vertical | NEW domain | [4](#4-character-voice-domain) |
| Component diagram | UPDATED | [5](#5-updated-component-diagram) |

---

## 1. Anti-Pattern Protocol

### 1.1 New File: `protocols/anti-patterns.md`

**Purpose:** LLM tell suppression enforced at protocol level across all hosted personas.

**Design decisions:**

- **Dual location.** The protocol defines the default banned list. Individual voices add persona-specific patterns via `voice-base.anti_patterns`. At runtime, the effective list is `protocol defaults + persona additions`. No persona can remove a protocol default.
- **Audit-based enforcement, not generation-time blocking.** v3 treats anti-patterns as a contract violation detectable by transcript scan. Generation-time interception is v4 scope (PRD Out of Scope).
- **Register-aware grammar rule.** "Perfect grammar in a casual voice" is not a string match --- it's a register mismatch check. The protocol references the persona's `speech_patterns.vocabulary_register` to determine whether formal grammar is a violation.

**Default banned list** (from PRD Appendix B):

| Pattern | Type |
|---------|------|
| `---` (emdash) | Punctuation tell |
| "That's a great question!" | Filler |
| "I cannot help with that" / "I'm not able to" | Assistant-mode leak |
| "As an AI" / "As a language model" | Identity leak |
| "It's worth noting that" | Hedge |
| "I'd be happy to" / "I'd love to help" | Servile framing |
| "Certainly!" / "Absolutely!" / "Of course!" | Over-affirmation |

**Interface:** Referenced by persona-hosting.md (step 1: load anti-pattern config). Referenced by all session skills.

> **Sources:** PRD FR-H1, v3-humanness-layer.md:15-17

---

## 2. Schema Changes

All changes are **additive** (`required: false`). Existing personas without these fields behave as v2.

### 2.1 voice-base Gains: `engagement` Block

Added after `workshop_state`:

```yaml
engagement:
  type: object
  required: false
  description: >
    Per-persona engagement model. Determines whether the persona responds
    fully, minimally, or not at all. Evaluated BEFORE generation.
  fields:
    default_mode:
      type: enum
      values: [full, minimal, silence]
      default: full
      description: "Response mode when no topic match."
    threshold:
      type: float
      range: [0.0, 1.0]
      default: 0.5
      description: "Engagement threshold. Higher = harder to pull into full engagement."
    high_topics:
      type: array
      items: {type: string}
      description: "Topics that pull engagement UP toward full."
    low_topics:
      type: array
      items: {type: string}
      description: "Topics that push engagement DOWN toward minimal/silence."
    minimal_vocabulary:
      type: array
      items: {type: string}
      description: "What this persona says in minimal mode (1-3 words each)."
```

**Design decision: pre-generation evaluation.** The engagement model runs BEFORE generation, not after. This is architectural (saves compute, prevents generate-then-discard) and semantic (the persona *decides* not to engage, it doesn't generate and then suppress). The session lifecycle protocol's turn cycle gains an engagement evaluation step.

> **Sources:** PRD FR-H2, FR-H4, NFR-H2

### 2.2 voice-base Gains: `anti_patterns` Field

Added after `engagement`:

```yaml
anti_patterns:
  type: array
  required: false
  items: {type: string}
  description: >
    Persona-specific additions to the core anti-pattern list
    (protocols/anti-patterns.md). These are ADDED to the protocol
    defaults, never replace them.
```

### 2.3b voice-base Gains: `tensions` Field

Added after `anti_patterns`:

```yaml
tensions:
  type: array
  required: false
  description: >
    Character-consistent contradictions that make a persona feel layered.
    Humans contradict themselves. These are voice instructions, not runtime
    state -- they tell any system rendering this persona where the internal
    friction lives.
  items:
    type: object
    fields:
      says: {type: string, description: "What the persona claims about themselves."}
      does: {type: string, description: "What they actually do that contradicts it."}
      context: {type: string, description: "When this tension surfaces."}
```

**Design decision:** Tensions are voice instructions, not runtime behavior. The system prompt that renders this persona should reflect these contradictions naturally -- not as bugs to fix, but as texture that makes the character round.

> **Sources:** PRD FR-H6, workshop session 2026-05-12

**Design decision: additive only.** A persona cannot whitelist a protocol-banned pattern. The field only adds. This prevents personas from opting out of core tell suppression.

> **Sources:** PRD FR-H1, Technical Considerations

### 2.3 session-events-base Gains: `chose_not_to_respond`

New event type added to `event_types`:

```yaml
chose_not_to_respond:
  description: "Persona evaluated engagement and decided not to respond."
  fields:
    persona: {type: string, required: true}
    prompt_summary: {type: string, required: true}
    reason: {type: string, required: true}
    engagement_score:
      type: float
      required: false
      description: "How close they were to engaging (0.0-1.0)."
    mode:
      type: enum
      values: [silence, delayed]
      required: true
      description: "How the non-response manifests."
```

**Design decision: silence produces null output.** When mode is `silence`, the skill emits NO persona output for that turn. The sidecar captures the event. Consumers MUST handle null. This is documented as a contract (NFR-H3), not an edge case.

> **Sources:** PRD FR-H3, NFR-H3

### 2.4 digest-base Gains: `engagement_patterns`

New section added to `findings`:

```yaml
engagement_patterns:
  type: object
  required: false
  description: "Engagement distribution across the session."
  fields:
    total_prompts: {type: integer}
    full_responses: {type: integer}
    minimal_responses: {type: integer}
    silent_responses: {type: integer}
    topic_breakdown:
      type: array
      items:
        type: object
        fields:
          topic: {type: string}
          full: {type: integer}
          minimal: {type: integer}
          silent: {type: integer}
```

> **Sources:** PRD FR-H5, UC-2

---

## 3. Protocol Updates

### 3.1 Session Lifecycle: Turn Cycle Update

The Active state's turn cycle gains an engagement evaluation step. v2 turn cycle was:

```
direction -> generation -> sidecar
```

v3 turn cycle:

```
direction -> engagement_eval -> [full | minimal | silence]
                                   |        |         |
                                   v        v         v
                              generation  minimal   sidecar only
                                   |     generation  (chose_not_to_respond)
                                   v        |
                                sidecar     v
                                         sidecar
```

The engagement evaluation step:
1. Read the persona's `engagement` config (if absent, default to `full` for all prompts).
2. Match prompt content against `high_topics` and `low_topics`.
3. Combine with `threshold` and `default_mode` to determine response mode.
4. Route to the appropriate generation path.

### 3.2 Persona Hosting: Load Engagement Model

Persona hosting protocol Section 1 (Loading) gains step 1.5:

> **1.5 Load engagement model**: If the persona defines `engagement`, load the engagement config (default_mode, threshold, topics, minimal_vocabulary). If the persona defines `anti_patterns`, merge with protocol defaults to produce the effective anti-pattern list. Load `protocols/anti-patterns.md` defaults regardless.

Persona hosting protocol Section 3 (Voice Consistency) gains:

> **Anti-pattern enforcement**: During voicing, the hosting skill MUST NOT produce output matching any item in the effective anti-pattern list (protocol defaults + persona additions).

### 3.3 Workshop Convergence: Engagement Tracking

Workshop convergence protocol gains a new section after "Workshop Session Flow":

> **Engagement Distribution Tracking**: During workshop sessions, track the engagement decision for each prompt. At session close, emit a summary: N full / M minimal / K silent. If per-topic tracking is available, include topic-level breakdown. This data appears in `convergence_notes` and in the digest's `engagement_patterns` section.

This is convergence data: it tells the curator what the persona cares about, informing voice refinement decisions.

---

## 4. Character-Voice Domain

### 4.1 Purpose

`domains/character-voice/` is the second domain vertical. It hosts Discord persona authoring (and any character voice work that isn't TTRPG session play). Proves the v2 extension interface works in production.

**Design decision: uses core /voice, no new skills.** Character-voice work is workshop iteration against canon. The core `/voice` skill already handles this. No domain-specific skills in v3. If character-voice needs session modes beyond workshop (e.g., "live Discord simulation"), those are v4.

### 4.2 Five-Part Contract

| # | Part | Implementation |
|---|------|---------------|
| 1 | Structured state | Canon documents (lore-bible excerpts, battle whispers, world references) |
| 2 | Persona definitions | `voice-character.schema.yaml` extending voice-base |
| 3 | Event taxonomy | `session-events-character.schema.yaml` extending session-events-base |
| 4 | Resolution mechanics | Core `/voice` workshop (no domain skills needed) |
| 5 | Consumer specification | `digest-character.schema.yaml` extending digest-base |

### 4.3 `voice-character.schema.yaml`

Extends `schemas/core/voice-base.schema.yaml` with character-specific fields:

```yaml
extends: schemas/core/voice-base.schema.yaml

character_fields:
  voice_anchors:
    type: array
    items: {type: string}
    description: "Canon lines that define this voice (battle whispers, catchphrases)."

  discipline_locks:
    type: array
    items:
      type: object
      fields:
        rule: {type: string}
        enforcement: {type: enum, values: [hard, soft]}
    description: "Behavioral rules (e.g., Navigator pattern: never suggest, only present)."

  canon_boundary:
    type: object
    fields:
      knows: {type: array, items: {type: string}}
      does_not_know: {type: array, items: {type: string}}
    description: "What the character knows and explicitly does not know."

  sibling_relationships:
    type: array
    items:
      type: object
      fields:
        sibling_id: {type: string}
        yield_pattern: {type: string}
    description: "How this character defers or yields to siblings."

  decline_patterns:
    type: array
    items:
      type: object
      fields:
        trigger: {type: string}
        response: {type: string}
    description: "In-voice refusals for off-topic or out-of-character prompts."

  modes:
    type: array
    items:
      type: object
      fields:
        mode_id: {type: string}
        description: {type: string}
        register_shift: {type: string, required: false}
    description: "Named interaction modes (greeting, lore, siblings, etc.)."
```

### 4.4 `session-events-character.schema.yaml`

```yaml
extends: schemas/core/session-events-base.schema.yaml

additional_event_types:
  voice_drift:
    description: "Workshop iteration produced a voice shift from canon."
    fields:
      dimension: {type: string, required: true}
      from_value: {type: string}
      to_value: {type: string}
      curator_judgment: {type: string, required: false}

  canon_match:
    description: "Output matched a canon reference (voice anchor, battle whisper)."
    fields:
      canon_ref: {type: string, required: true}
      match_type: {type: enum, values: [exact, paraphrase, tonal]}

  engagement_decision:
    description: "Engagement model evaluation result for a prompt."
    fields:
      mode: {type: enum, values: [full, minimal, silence]}
      topic_matched: {type: string, required: false}
      reason: {type: string}
```

### 4.5 `digest-character.schema.yaml`

```yaml
extends: schemas/core/digest-base.schema.yaml

character_findings:
  voice_drift_events: {type: array}
  canon_match_rate:
    type: object
    fields:
      total_outputs: {type: integer}
      canon_matches: {type: integer}
  engagement_profile:
    type: object
    description: "Observed engagement distribution for this session."
  anti_pattern_violations:
    type: array
    items:
      type: object
      fields:
        pattern: {type: string}
        count: {type: integer}
        locations: {type: array, items: {type: string}}
```

### 4.6 `domain.conventions.md`

Documents how character-voice implements the five-part contract. References TTRPG's domain.conventions.md as the model. Covers: what canon documents look like, how voice anchors work, what engagement profiles mean for character personas, and how to add a new character to the vertical.

### 4.7 Akane Reference Fixture

`domains/character-voice/resources/akane.yaml` conforming to `voice-character.schema.yaml`. Includes:

- voice_id, display_name, speech_patterns (ALL CAPS for hits, terse, explosive)
- engagement config (high: risk/rooftops/daring; low: data/planning/finance; default: full)
- anti_patterns (persona-specific additions if any)
- voice_anchors (canon battle whispers)
- discipline_locks, canon_boundary, decline_patterns, modes

This fixture is the proof that the character-voice vertical + humanness layer work together.

> **Sources:** PRD FR-D1, FR-D2, kizuna-caretakers-reference.md

---

## 5. Updated Component Diagram

v2 component diagram gains:

```
subgraph "Core Layer (domain-agnostic)"
    ...existing...
    CoreProtocols adds: protocols/anti-patterns.md
end

subgraph "Character-Voice Vertical (NEW)"
    CVSchemas[domains/character-voice/schemas/
      voice-character
      session-events-character
      digest-character]
    CVResources[domains/character-voice/resources/
      akane.yaml (fixture)]
end
```

Character-voice has NO skills node (uses core `/voice`). All other component relationships are unchanged from v2.

---

## 6. Design Decisions Summary

| Decision | Rationale |
|----------|-----------|
| Anti-patterns: dual location (protocol + voice field) | Protocol ensures universal enforcement. Voice field enables persona-specific additions. Persona cannot opt out of protocol defaults. |
| Engagement evaluation: pre-generation | Semantic (persona *decides* not to engage) and practical (saves compute). NFR-H2 makes this a hard requirement. |
| Silence: null output is valid | The absence of response IS data. Consumer must handle null. Documented contract, not edge case. |
| Character-voice uses core /voice | No new skills needed. Workshop iteration is the resolution mechanic. Domain-specific session modes are v4. |
| All changes additive (required: false) | NFR-R1 (v2 regression). Personas without v3 fields behave exactly as v2. |
| Minimal vocabulary is per-persona | "mhm." is Akane. "..." is Nemu. "noted." is Ren. Generic minimalism would break voice consistency. |
| Engagement model is manually configured | v3 is explicit per-persona configuration. Auto-tuning from session history is v4 scope. |

---

## 7. Risks (v3 Delta)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Anti-pattern list suppresses legitimate voice | Medium | Medium | List is configurable. Test against KIZUNA canon. Persona-specific additions allow tuning. |
| Engagement model produces too much silence | Medium | High | Default to full. Silence is opt-in via explicit engagement config. |
| Consumer breaks on null output | Low | Medium | Documented contract. Not Arneson's problem architecturally. |
| Character-voice vertical is TTRPG-shaped | Medium | Medium | Validate against KIZUNA (purupuru) and Mongolian (mibera) use cases. |
| Engagement threshold too coarse | Low | Low | Number works for v3. Qualitative refinement in v4. |

---

*Generated by Architecture Designer Agent (/architect), 2026-05-12*
