# agent-systems — Domain Conventions

**Status:** Sprint 1 stub — finalized in Sprint 3 (banned-copy list, one-variable
discipline, claim_strength framing rules land with the docs they police).

## The five-part extension contract (how this domain plugs in)

| Part | This domain's answer |
|------|----------------------|
| State | A committed `scenario.yaml` (agent-scenario v1) + the fixture it pins |
| Personas | `agent-persona` v1 specs (NOT voice-base — you don't workshop an agent's voice) |
| Events | `session-events-agent` v1 (extends session-events-base v2; per-event seq + at) |
| Resolution | Real lane: Gygax's ladder engine. Simulated lane: persona host, serialize-only |
| Consumer | Gygax's trace CLI, via the vendored `observed-trace/v1` + batch contracts |

## Conventions (Sprint 1 set)

1. **The vendored contract is Gygax's file.** Never edit anything under
   `schemas/vendor/`; re-vendor + update `VENDOR.yaml` + revisit the validators.
2. **Validators are the gate.** No batch path is reported as Gygax-ready unless
   `validate_batch.py` exits 0. A capture without a validator is a claim.
3. **One variable per scenario family** (documented convention): rung varies
   *inside* a scenario; temperament/persona/agent_cmd varies *across* scenarios.
   Varying both at once produces a diff Gygax can't attribute.
4. **Honest labels always:** producer ↔ claim_strength binding is checked before
   handoff; forecast-without-playing is never a sidecar claim.

## To be finalized in Sprint 3

- Banned-copy list (no "hard metrics", "zero hallucination", fidelity claims)
- claim_strength framing rules for docs ("pretend is a preview, real is the proof")
- Local-model `agent_cmd` guidance (Ollama-backed agentic CLIs)
