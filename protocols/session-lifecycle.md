# Session Lifecycle Protocol

> Domain-agnostic session state machine. All session skills MUST follow this lifecycle.
> Generalized from /braunstein's 7-state machine.

**Version:** 1.0
**SDD Reference:** sdd.md Section 6.1
**PRD Reference:** FR-C2

---

## State Machine

```
[*] --> Invoked
Invoked --> SafetyPrompt          : skill invocation
SafetyPrompt --> DomainLoad       : practitioner confirms safety agreement
DomainLoad --> PersonaLoad        : domain state loaded
PersonaLoad --> Active            : persona loaded and grounded
Active --> Active                 : turn cycle (direction -> generation -> sidecar)
Active --> Paused                 : /pause or /x-card
Paused --> Active                 : /resume
Active --> Closing                : practitioner exits
Closing --> Persisted             : state diff computed, files written
Persisted --> [*]
```

## States

### Invoked
The practitioner invokes a session skill (e.g., `/voice`, `/braunstein`, or any domain session skill). The skill identifies which domain it belongs to.

### SafetyPrompt
**Mandatory.** Cannot be skipped. The safety-protocol.md governs this state.
- Present safety agreement (Lines, Veils, X-card, domain-specific boundaries).
- Practitioner must explicitly confirm before any creative generation begins.
- Write `safety_agreement` to sidecar preamble.

### DomainLoad
Load the domain's structured state:
- Read the state file(s) specified by the domain vertical.
- Compute checksums for forensic validation.
- Detect composition partners (e.g., Gygax in TTRPG mode).
- Domain-specific extensions to this state (e.g., tradition check, game-state load) are internal to the domain skill.

### PersonaLoad
Load the persona per persona-hosting.md protocol:
- Read voice-base + domain extensions.
- Load memory window.
- Ground against structured state.

### Active
The turn cycle. Each turn:
1. **Direction**: Practitioner provides input (dialogue, action, prompt).
2. **Generation**: Arneson generates grounded response in the persona's voice.
3. **Sidecar**: Capture events (dialogue, decisions, signals, state_references) to the sidecar.

Safety commands (/pause, /x-card, /resume) are available at all times.

### Paused
Session is halted. Sidecar records a `pause` event. No creative generation occurs.
- `/resume` returns to Active state.
- Safety triggers that caused the pause are logged as `safety_trigger` events.

### Closing
Practitioner exits the session:
- Compute state diff (what changed in the persona this session).
- Present summary to practitioner if relevant.

### Persisted
Write all session artifacts:
- Finalize transcript (markdown).
- Finalize sidecar (YAML) with `session_end` event.
- Update persona state per persona-hosting.md §5.
- All writes are atomic (temp file + rename).

## Session Metadata

Every session sidecar preamble includes (per session-events-base):
- `session_id`: unique identifier
- `domain`: which vertical produced this session
- `mode`: which skill produced this session
- `started_at`: ISO8601 timestamp
- `state_path`: path to structured state (if any)
- `state_checksum`: SHA256 of state file
- `safety_agreement`: the agreement made

Domain-specific preamble extensions are added by the domain's session-events extension schema.

## Crash Recovery

If a session terminates without reaching Closing:
- The sidecar is valid but lacks `session_end`.
- `/distill` marks the digest as `partial_session: true`.
- State updates are NOT applied (persona reverts to pre-session state).
