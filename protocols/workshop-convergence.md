# Workshop Convergence Protocol

> The canonical flow for persona development: iterative workshop, then serialization.
> Grounded in real consumer evidence (arneson#2).

**Version:** 1.0
**SDD Reference:** sdd.md Section 6.2
**PRD Reference:** FR-C8

---

## Principle

The iteration loop IS the product. What makes Arneson a workshop instrument — not an IP-to-photocopy source — is the multi-session convergence loop that produces a locked voice-state.

## Two Valid Shapes

| Shape | What it is | What it produces | Valid? |
|-------|-----------|------------------|--------|
| **Workshop tool** (canonical) | Invoke `/voice` iteratively across sessions until voice converges | Locked `voice-state.yaml` with speech patterns, memory, register | Always |
| **Doctrine reference** (consumer) | Serialize a locked voice-state into a static prompt for downstream use | One-shot voice approximation grounded in workshopped state | Only after Shape 1 |

**Misuse pattern**: Skipping Shape 1 and going directly to Shape 2 — extracting Arneson's voice doctrine into a static embed without running the workshop. The static embed loses the iteration loop, the grounding, and the sidecar emission.

## Convergence Stages

Tracked via `voice-base.workshop_state`:

```
[*] --> Drafting          : first /voice session
Drafting --> Drafting     : voice shifts significantly between turns
Drafting --> Refining     : voice stabilizes (practitioner confirms direction)
Refining --> Refining     : fine-tuning register, tics, emotional range
Refining --> Locked       : practitioner confirms convergence
Locked --> [*]            : voice-state finalized
```

### Stage Definitions

| Stage | Meaning | Typical Sessions |
|-------|---------|-----------------|
| `drafting` | Voice is still finding itself. Speech patterns shift between sessions. | 1-3 |
| `refining` | Voice is recognizable. Fine-tuning specifics — verbal tics, emotional triggers, grounding depth. | 3-5 |
| `locked` | Practitioner has confirmed the voice is done. No further drift expected. | 5+ |

Stage transitions are practitioner-driven, not automatic. Arneson does not self-promote a voice from `refining` to `locked`.

## Workshop Session Flow

Each `/voice` workshop session follows the session-lifecycle.md protocol, plus:

1. **Load existing voice-state** (or create new if first session).
2. **Present current stage**: "This voice is in {stage} (iteration {N})."
3. **Run workshop dialogue**: Practitioner directs, Arneson performs in the persona's voice.
4. **Capture convergence signals**: What's stabilizing? What's still shifting?
5. **At session close**:
   - Increment `iteration_count`.
   - Update `last_workshop_session`.
   - If practitioner confirms stage transition, update `stage`.
   - Record `convergence_notes` (practitioner's observations on what's working).

## Serialization Gate

A voice-state MAY be serialized for downstream consumption (static prompt, agent config, character bible) **only when**:

- `workshop_state.stage == locked`
- The serialization is explicitly a representation of the workshopped voice, not a substitute for workshopping

The serialized form should reference the source voice-state file and the number of workshop iterations.

## Consumer Documentation

Arneson's README and consumer-pattern guide (Sprint 6) MUST document:
- The two valid shapes
- The misuse pattern (skipping workshop)
- When serialization is valid
- How to invoke the workshop correctly

## Schema Integration

The `workshop_state` field lives in `schemas/core/voice-base.schema.yaml`:

```yaml
workshop_state:
  required: false  # not all voices go through workshop
  fields:
    stage: enum [drafting, refining, locked]
    iteration_count: integer (default 0)
    last_workshop_session: string
    convergence_notes: list[string]
```

Domain-specific voice schemas inherit this field. No domain override needed.
