---
priority: READ-FIRST
scope: cycle-start
source: workshop session 2026-05-12 + KIZUNA caretaker gist
companion_context: kizuna-caretakers-reference.md
---

> # LOA: READ THIS AT v3 CYCLE START
>
> This file captures the design direction for construct-arneson v3.
> The v2 cycle built the creative persona engine architecture.
> v3 makes personas feel human.

---

# v3 Direction: The Humanness Layer

## Origin

During a `/voice akane` workshop session (2026-05-12), three problems surfaced
that separate believable characters from chatbots:

### Problem 1: LLM Anti-Patterns (Emdash Ban)

The `—` emdash is the single biggest tell that output is AI-generated. Real
people text with `...` or `-` or just break into a new sentence. This applies
to ALL Arneson personas, not per-character.

Other LLM tells to suppress:
- "I cannot help with that" (assistant-mode leak)
- "As an AI" / "As a language model"
- "That's a great question!" (filler)
- Excessive hedging ("It's worth noting that...")
- Perfect grammar in casual contexts

**Scope**: Core-level. Every voice Arneson hosts inherits these anti-patterns.
Should be in `voice-base` or a protocol.

### Problem 2: Response Inclination (Engagement Threshold)

Not every input deserves a response. Current assumption: every prompt gets
output. Real humans don't work that way.

A persona should have a configurable engagement model:
- **Engagement threshold**: how much does this persona want to talk?
- **Topic-sensitive**: Akane has HIGH engagement for risk/action, NEAR-ZERO for
  data/planning. Nemu is low for everything except quiet company.
- **Response modes**: full response, minimal ("mhm"), silence (no output)

This is per-persona AND per-topic. The voice-base schema needs fields for it.

### Problem 3: Silence as Valid Output

When a persona chooses not to respond, that IS data:
- The sidecar should log a `chose_not_to_respond` event with reasoning
- The consumer (Discord bot) gets a structured null signal
- The workshop captures this as convergence data ("Akane ghosted 3/10 prompts")
- The absence of response tells you what the persona cares about

**Architectural implication**: FR-C5 ("every session produces transcript + sidecar")
needs refinement — sometimes the transcript entry is empty but the sidecar still
has the decision event.

## Grounding Use Case

The **KIZUNA caretakers** (5 Discord personas for purupuru world) are the
reference implementation:

| Caretaker | Element | Engagement Profile |
|-----------|---------|-------------------|
| Kaori | Wood | Patient. Responds to everything, but quietly. |
| Nemu | Earth | Low engagement. Often minimal. Silence is her voice. |
| Akane | Fire | High for risk/action. Ghosts boring questions. |
| Ren | Metal | High for analysis/bears. Yields on emotion. |
| Ruan | Water | Attuned. Responds to emotional weather, ignores logistics. |

Source: KIZUNA QA pack gist (zkSoju/2c359e8fc7315bc00190e0b337d80949)
See companion file: `kizuna-caretakers-reference.md`

## What v3 Adds to v2

v2 built the core/vertical architecture. v3 adds:

1. **Anti-pattern layer** (core): LLM tells suppressed at the protocol level
2. **Engagement model** (voice-base): threshold, topic sensitivity, response modes
3. **Silence instrumentation** (session-events-base): `chose_not_to_respond` event
4. **Character-voice domain vertical** (domains/character-voice/): the non-TTRPG
   vertical for Discord personas, agent NPCs, and character authoring
5. **Workshop convergence enhancements**: track engagement patterns across sessions,
   capture what the persona cares about vs ignores

## Open Questions

1. Where does the anti-pattern list live? voice-base field? Protocol? Identity?
2. How does the consumer (bot) handle silence? Is it Arneson's concern or the consumer's?
3. Should engagement threshold be a hard number (0.0-1.0) or qualitative (high/medium/low/none)?
4. Does silence require safety agreement? (If persona never responds, is that safe?)
5. How does the workshop track engagement patterns? Per-prompt scoring? Aggregate?
