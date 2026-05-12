# Persona Hosting Protocol

> Domain-agnostic behavioral contract for persona loading, voicing, and persistence.
> All domain skills that host personas MUST follow this protocol.
> Extracted from /braunstein and /voice SKILL.md; generalized beyond TTRPG.

**Version:** 1.0
**SDD Reference:** sdd.md Section 1.4.5, Section 6.1
**PRD Reference:** FR-C1

---

## 1. Loading

Before a persona can speak, the hosting skill MUST:

1. **Read voice-base fields**: Load `voice_id`, `display_name`, `speech_patterns`, `reaction_tempo`, `emotional_register`, `memory_slots`, `known_facts` from the persona's YAML file.
2. **Read domain extensions**: If the domain provides extension schemas (e.g., `voice-archetype`, `voice-npc`), load those fields on top of the base. Unknown extension fields are ignored gracefully.
3. **Load memory window**: Read the most recent N sessions (configurable, default 3) from the persona's `memory_slots`. Memory beyond the window exists as record but does NOT shape voicing.
4. **Read grounding state**: If `grounding_state_path` is set, load the structured state the persona grounds against. If the path doesn't exist, warn the practitioner: "Structured state not found at {path}. Proceeding ungrounded."

## 2. Grounding

Every persona utterance MUST be grounded in the practitioner's structured state:

- **Available state**: Fiction MUST NOT introduce facts the state hasn't made available. If the state is thin, the persona flags the improvisation.
- **Intent respect**: If the state declares intent fields (experiential, mechanical, behavioral), the persona plays INTO them. Never fudges fiction to overrule declared intent.
- **State references**: Significant grounding events are captured in the sidecar as `state_reference` events.

## 3. Voice Consistency

During a session, the persona's voice MUST remain consistent:

- **Speech patterns** hold across all turns (sentence length, vocabulary register, distinctive markers).
- **Reaction tempo** is maintained (an `immediate` reactor does not become `deliberate` mid-session).
- **Emotional register** shifts only in response to in-fiction stimuli, not drift.
- **No narrator omniscience**: Inside a persona's turn, the voice is theirs. The hosting skill does not narrate from outside the persona's perception unless framing or closing a scene.

## 4. Persona Boundaries

- The hosting skill speaks AS the persona during session turns.
- The hosting skill speaks AS Arneson (construct persona) during banners, safety events, refusals, and status messages.
- These two voices NEVER mix in the same paragraph.

## 5. State Persistence

At session close, the hosting skill MUST:

1. **Update memory_slots**: Add new memories from this session. Evict oldest if beyond window.
2. **Update known_facts**: Add any facts the persona learned this session.
3. **Update workshop_state** (if applicable): Increment `iteration_count`, update `last_workshop_session`, update `stage` if convergence warrants.
4. **Write atomically**: State file updates use atomic rename pattern (write to temp, rename).
5. **Finalize sidecar**: Ensure sidecar has `session_end` event with summary counts.

## 6. Fallback Behavior

| Condition | Handling |
|-----------|---------|
| Persona file missing | Error: "Persona {id} not found." Do not improvise a voice from nothing. |
| Extension fields unrecognized | Ignore gracefully. Log info. |
| Memory sessions missing | Load what's available. Warn if fewer than window size. |
| Grounding state missing | Warn practitioner. Proceed ungrounded with explicit notice. |
| Domain not recognized | Load voice-base fields only. Domain extensions skipped. |
