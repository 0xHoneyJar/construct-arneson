# API Surface

> The construct's "API" is its skill commands and script CLIs. Sources cited as file:line.

## Core Skill Commands (domain-agnostic)

| Command | Type | Behavior | Source |
|---------|------|----------|--------|
| `/voice {persona}` | session | Workshop a persona iteratively; supports `--source <path>` external ingest with format detection (persona.md vs YAML) | `skills/voice/index.yaml`, `skills/voice/SKILL.md:15-19` |
| `/distill {session}` | one-shot | Compress prose transcript + sidecar into downstream digest (Gygax-ingestible in TTRPG) | `skills/distill/index.yaml` |
| `/arneson` | read-only | Status dashboard: sessions, voices, domains, safety findings, composition state | `skills/arneson/index.yaml` |

## TTRPG Skill Commands (reference vertical)

| Command | Type | Behavior | Source |
|---------|------|----------|--------|
| `/braunstein` | session (flagship) | User GMs; Arneson plays a cabal archetype. Dice, dialogue, real-time sidecar | `domains/ttrpg/skills/braunstein/index.yaml` (PRD-v2 FR-1, FR-9..FR-17) |
| `/scene {seed}` | one-shot | Scene from game-state + seed/oracle | `domains/ttrpg/skills/scene/index.yaml` (FR-3) |
| `/narrate {outcome}` | one-shot / library primitive | Fiction-mechanics-fiction atom under braunstein/improvise | `domains/ttrpg/skills/narrate/index.yaml` (FR-4) |
| `/improvise` | session | Inverse of braunstein: Arneson GMs, user plays PC | `domains/ttrpg/skills/improvise/index.yaml` (FR-5) |
| `/fragment {scope}` | one-shot | Setting material: locations, factions, histories, items | `domains/ttrpg/skills/fragment/index.yaml` (FR-7) |

## In-Session Safety Commands

`/pause`, `/x-card`, `/resume`, `/break` — declared in session-skill index.yaml files (`skills/voice/index.yaml:29-32`, `braunstein/index.yaml:47-49`, `improvise/index.yaml:34-36`). Safety is no-opt-out (`schemas/core/safety.schema.yaml:3`).

## Script CLIs

| Script | Usage | Exit codes | Source |
|--------|-------|-----------|--------|
| `ingest_persona.py` | `python3 ingest_persona.py <persona.md>` → voice-character YAML on stdout (file arg or stdin) | 0 ok, 1 parse error, 2 sync violation | `domains/character-voice/scripts/ingest_persona.py:1-13` |
| `emit_persona.py` | `python3 emit_persona.py --template <md> --state <yaml>` → persona.md on stdout; section-level editor, both layers atomic | 0/1/2 same | `domains/character-voice/scripts/emit_persona.py:1-13` |
| `test-roundtrip.sh` | `./test-roundtrip.sh` | 0 pass, 1 fail | `domains/character-voice/scripts/test-roundtrip.sh` |
| `scripts/ci/validate-{construct,schemas,fallbacks,fixture,skills}.sh` | no args; run from repo root | 0/1 | `scripts/ci/` |
