# Test Workshop Skill

> Minimal workshop skill for extension story validation.
> Follows all core protocols: persona-hosting, session-lifecycle, safety-protocol, workshop-convergence.

## Purpose

This skill validates that a new domain can be added to Arneson without touching core code.
It implements a minimal character-interview workshop where a practitioner converses with
a test persona to validate the extension interface.

## Protocol Compliance

This skill follows:
- `protocols/persona-hosting.md` — persona loading, grounding, persistence
- `protocols/session-lifecycle.md` — Invoked → Safety → DomainLoad → PersonaLoad → Active → Closing → Persisted
- `protocols/safety-protocol.md` — mandatory agreement, /pause, /x-card, /resume
- `protocols/workshop-convergence.md` — iterative convergence, drafting → refining → locked

## Flow

1. Load test persona from `resources/sample-persona.yaml`
2. Load test state from `resources/sample-state.yaml`
3. Run safety agreement (mandatory)
4. Enter workshop dialogue (practitioner directs, persona performs)
5. Emit sidecar with base events + `test_observation` domain events
6. At close: update persona state, finalize transcript + sidecar
