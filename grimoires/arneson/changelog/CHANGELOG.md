# Changelog — construct-arneson

All notable changes to this construct are documented here. Follows [Keep a Changelog](https://keepachangelog.com/).
Versioning follows SemVer: MAJOR.MINOR.PATCH.

## [1.0.0] — 2026-04-13 (v1 Release)

### Added
- **8 skills** — full v1 surface area:
  - `/braunstein` (flagship): live playtest session, archetype-as-character, 8-state lifecycle, structured sidecar emission
  - `/voice`: NPC workshop with persistent voice state across sessions
  - `/scene`: one-shot scene generator grounded in game-state
  - `/narrate`: fiction-mechanics-fiction primitive (intent-flip sensitive)
  - `/improvise`: GM-side design test (inverse of braunstein)
  - `/arneson`: read-only status dashboard
  - `/fragment`: setting material generator (locations, factions, histories, items)
  - `/distill`: session compressor — Gygax-ingestible digest (composition glue)
- **Construct manifest** (`construct.yaml`): slug `arneson`, schema_version 3, skill-pack, 8 skills, composition paths
- **Identity layer**: `ARNESON.md` (prose identity), `persona.yaml`, `expertise.yaml`, `refusals.yaml` (7 load-bearing refusals with vocabulary_to_avoid)
- **7 schemas**: experiential_intent (Arneson-owned axis), voice-base + 3 extensions (archetype/npc/pc), session-events (admissibility infrastructure), digest
- **Archetype fallback bundle**: 9 archetypes for standalone mode (newcomer, optimizer, chaos-agent, storyteller, rules-lawyer, explorer, min-maxer, casual, contrarian)
- **Synthetic reference fixture**: Threshold (folk-horror microgame, HEKATE-free) with tradition lore + 4 scene seeds
- **Grimoire structure**: `grimoires/arneson/` with sessions, voices, scenes, fragments, digests, safety-findings, changelog
- **CI workflow**: two-matrix build (arneson-alone + arneson-with-gygax), 6 validation scripts
- **Sprint 0 prototype**: hand-authored `/braunstein` turn proving fiction quality before schema commitment

### Design Principles
- **Standalone-plus-composable**: works without Gygax; amplified by Gygax
- **Two-axis intent**: Gygax owns `mechanical_intent`; Arneson owns `experiential_intent`
- **Admissibility**: every session produces a structured sidecar that makes findings mechanically extractable
- **Data-emitting fiction**: Arneson's identity is fiction-that-instruments, not just fiction
- **Safety as load-bearing mechanic**: X-card/Lines/Veils → dead-design-space findings

### Architecture
- Filesystem-first skill graph with shared-state grimoire
- Session-length skills (braunstein, voice, improvise) with state-machine lifecycle
- One-shot skills (narrate, scene, fragment) with tradition-fallback awareness
- Meta skills (arneson, distill) for status and post-processing
- Sidecar event schema (9 event types, append-only, crash-durable)

### Functional Requirements Addressed
- FR-1 through FR-17 (all 17 PRD requirements)

### Known Limitations
- Fallback archetype names are Arneson-authored; may diverge from Gygax v3 SSOT
- Chaos Agent per-turn event cap (10) is untuned — needs empirical calibration
- No automated behavioral tests (skill-pack paradigm — prompt output verified by invocation)
- Gygax schema PR for two-axis intent split not yet filed
- SHA256 checksum not yet added to yq CI download (version is pinned)

## [1.0.0-alpha] — 2026-04-13 (Sprint 1 Foundation)

### Added
- Initial scaffolding: manifest, identity, schemas, fallback bundle, fixture, grimoire, CI
- Sprint 0 prototype informed Newcomer voice fallback
