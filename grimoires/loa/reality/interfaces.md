# External Interfaces

## Sibling: construct-gygax (optional composition)

- Declared at `construct.yaml:64-77`: `required: false`, `minimum_version: 3.0.0`
- **Detection probe**: directory-exists check on `grimoires/gygax/game-state/`
- **Read paths** (Arneson reads, never writes): gygax game-state, identity, cabal archetypes, lore resources
- **Fallback** when absent: 9 bundled archetypes at `domains/ttrpg/resources/archetypes-fallback/` (construct.yaml:78-79)
- **Composition glue**: `/distill` emits Gygax-ingestible digests (skills/distill/index.yaml)
- CI: `arneson-with-gygax` job currently uses a **stub** fixture, not real Gygax (ci.yaml; DRIFT-7)

## Consumer: freeside-characters (Discord bot)

- Declared at `construct.yaml:57-62`: repo `0xHoneyJar/freeside-characters`, persona path pattern `apps/character-{id}/persona.md`, loader `packages/persona-engine/src/persona/loader.ts:33` (external — unverified locally)
- **Adapter**: `domains/character-voice/adapters/freeside.yaml` (238 lines) — bidirectional persona.md ⇄ voice-character YAML
- **Two-layer sync contract** (`freeside.yaml:212-238`): reference body (human-read) + system prompt template (bot-read) must update atomically; `atomic_write: true` — compute entire file before writing
- **Tooling**: `ingest_persona.py` (md → YAML), `emit_persona.py` (YAML → md, section-level editor preserving unmapped sections verbatim)
- **Reference data**: `akane.yaml`, `akane-canon.yaml` (domains/character-voice/resources/); synthetic fixture `fixtures/test-persona.md` ("Compass")

## Loa framework (host)

- Mounted v1.71.1 as submodule `.loa/` (`.loa-version.json`); construct manifest `construct.yaml` schema_version 3, type skill-pack
- Runtime state written under `grimoires/arneson/` (output_paths, construct.yaml:101-112)

## Consumption shapes (docs/CONSUMER-PATTERNS.md)

1. **Workshop tool** (canonical) — iterative `/voice` until convergence
2. **Doctrine reference** — serialize locked voice-state to static prompt, valid only post-convergence
