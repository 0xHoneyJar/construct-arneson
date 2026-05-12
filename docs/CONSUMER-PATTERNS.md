# Consumer Patterns — How to Use Arneson

> There are two valid shapes for using Arneson, and they are NOT interchangeable.

---

## Shape 1: Workshop Tool (Canonical)

Run `/voice {persona-id}` interactively across multiple sessions. The practitioner talks TO the persona; the persona talks back; voice converges over iterations. Produces a `voice-state.yaml` that captures speech patterns, memory slots, register, and per-session refinements.

**This is what Arneson IS designed for.** It is a workshop instrument.

### The Flow

```
Session 1 (Drafting)    → voice is rough, finding its shape
Session 2 (Drafting)    → voice shifts, patterns start emerging
Session 3 (Refining)    → voice is recognizable, fine-tuning
Session 4 (Refining)    → register, tics, emotional range dialed in
Session 5 (Locked)      → practitioner confirms: this voice is done
```

### What You Get

A locked `voice-state.yaml` with:
- Stable speech patterns (sentence length, vocabulary, distinctive markers)
- Calibrated emotional register (baseline + triggers)
- Memory from workshop sessions
- Known facts and grounding references
- Workshop provenance (iteration count, convergence notes)

---

## Shape 2: Doctrine Reference (Consumer)

A downstream consumer (Discord bot, narrative agent, character pipeline) MAY extract the workshopped voice into a static prompt or config file. This is fine **IF AND ONLY IF** the underlying voice has already been workshopped via Shape 1 and the prompt is a serialization of that workshop's output.

### Valid Consumer Pattern

```
1. Run /voice workshop (Shape 1)     → produces locked voice-state.yaml
2. Serialize voice-state into prompt   → static embed grounded in workshopped state
3. Consumer bot reads the prompt       → one-shot approximation of the workshopped voice
```

### Invalid Consumer Pattern (Misuse)

```
1. Read Arneson's identity docs        → extract voice doctrine
2. Paste into a static prompt          → doctrine-photocopy with no underlying voice-state
3. Consumer bot reads the prompt       → ungrounded approximation that won't converge
```

The second pattern loses the iteration loop, the grounding, and the sidecar emission. It treats Arneson as IP-to-photocopy rather than a tool to invoke.

---

## What Arneson is NOT

- A static text-embed dropped into another agent's prompt without prior workshop work
- A general-purpose fiction-generation engine
- A replacement for the iterative loop that converges voice
- A doctrine library to copy from

---

## When to Use Each Shape

| Situation | Shape | Why |
|-----------|-------|-----|
| Developing a new character/agent voice | Shape 1 | The workshop IS the product |
| Calibrating an existing voice | Shape 1 | Iteration refines what a static prompt cannot |
| Deploying a workshopped voice to production | Shape 2 | Serialization of a converged voice is valid |
| Quick one-shot voice for a throwaway context | Shape 1 (short) | Even a 1-session workshop is better than a doctrine-copy |
| Referencing Arneson's voice philosophy | Neither | Read the identity docs for understanding, but don't copy them into a prompt |

---

*This guide was informed by [arneson#2](https://github.com/0xHoneyJar/construct-arneson/issues/2) — a real consumer who encountered the misuse pattern and self-corrected.*
