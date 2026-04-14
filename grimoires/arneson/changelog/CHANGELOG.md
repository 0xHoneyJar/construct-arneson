# Changelog — construct-arneson

All notable changes to this construct are documented here. Follows [Keep a Changelog](https://keepachangelog.com/).
Versioning follows SemVer: MAJOR.MINOR.PATCH.

## [1.0.0-alpha] — 2026-04-13 (Sprint 1 Foundation)

### Added
- Construct manifest (`construct.yaml`)
- Identity layer: `ARNESON.md`, `persona.yaml`, `expertise.yaml`, `refusals.yaml`
- 7 schemas: experiential_intent, voice-base + 3 extensions (archetype/npc/pc), session-events, digest
- Archetype fallback bundle: 9 archetypes (newcomer, optimizer, chaos-agent, storyteller, rules-lawyer, explorer, min-maxer, casual, contrarian)
- Synthetic reference fixture: Threshold game + folk-horror-minimalist tradition + scene seeds
- Grimoire directory scaffolding
- CI workflow scaffold with two modes (arneson-alone, arneson-with-gygax)
- Schema validation, HEKATE audit, construct load checks

### Notes
- Fallback archetype bundle is pinned against Gygax v3.0.0 (anticipated shape). Sync check in Sprint 7.
- Skills not yet implemented; Sprint 1 is scaffolding only.
- Sprint 0 prototype (`grimoires/loa/prototypes/sprint-0/`) informed Newcomer voice fallback.
