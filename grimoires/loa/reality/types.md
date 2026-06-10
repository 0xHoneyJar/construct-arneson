# Types (Schema Surface)

> Declarative YAML schemas (`schema.name` + `schema.version` headers), not JSON Schema. Extension via `schema.extends`.

## Core (domain-agnostic) — `schemas/core/`

| Schema | Version | Purpose |
|--------|---------|---------|
| `voice-base` | 2 | Common fields for any hosted voice (speech_patterns, registers, anti_patterns additions) |
| `session-events-base` | 2 | Base event envelope for the structured sidecar; every domain extends |
| `digest-base` | 2 | Output of `/distill`; `digest_schema_version` required integer |
| `safety` | 1 | Non-negotiable safety config: every domain, every session, no opt-out |
| `experiential_intent` | 1 | Arneson-owned axis of two-axis intent contract (Gygax owns mechanical_intent) — snake_case filename outlier (see consistency C1) |

## TTRPG vertical — `domains/ttrpg/schemas/`

| Schema | Version | Extends |
|--------|---------|---------|
| `voice-archetype` | 1 | voice-base |
| `voice-npc` | 1 | voice-base |
| `voice-pc` | 1 | voice-base |
| `session-events-ttrpg` | 2 | session-events-base |
| `digest-ttrpg` | 2 | digest-base |

## character-voice vertical — `domains/character-voice/schemas/`

| Schema | Version | Extends |
|--------|---------|---------|
| `voice-character` | 1 | voice-base |
| `session-events-character` | 1 | session-events-base |
| `digest-character` | 1 | digest-base |

NOT covered by `scripts/ci/validate-schemas.sh` (core+ttrpg only — DRIFT-3).

## test-domain (extension-story fixture) — `examples/test-domain/schemas/`

`voice-test`, `session-events-test`, `digest-test` — all declare `extends`; validated by the extension-story CI job.

## Identity types — `identity/`

`persona.yaml` (Arneson's meta-role voice), `expertise.yaml`, `refusals.yaml` (load-bearing refusal list with `vocabulary_to_avoid` greppable by /audit-sprint — `identity/refusals.yaml:6-8`).
