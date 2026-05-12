# Changelog — construct-arneson

All notable changes to this construct are documented here. Follows [Keep a Changelog](https://keepachangelog.com/).
Versioning follows SemVer: MAJOR.MINOR.PATCH.

## [3.0.0] — 2026-05-12 (v3 — Humanness Layer)

### Added
- **Anti-pattern protocol** (`protocols/anti-patterns.md`): Core-level LLM tell suppression. Emdash ban, assistant-mode leak detection, filler phrase prohibition. Enforced across all hosted personas.
- **Engagement model** in voice-base: `engagement` block with `default_mode`, `threshold`, `high_topics`, `low_topics`, `minimal_vocabulary`. Pre-generation evaluation determines full/minimal/silence response.
- **Silence instrumentation**: `chose_not_to_respond` event in session-events-base. The absence of response is data — captures what was asked, why engagement was low, engagement score.
- **Minimal response mode**: Between full response and silence. Per-persona `minimal_vocabulary` (1-3 words, in-voice).
- **Engagement patterns** in digest-base: Distribution data (full/minimal/silent counts + topic breakdown).
- **Character tensions** in voice-base: `tensions` field for character-consistent contradictions. "She says she doesn't plan but clearly cases buildings."
- **Character-voice domain vertical** (`domains/character-voice/`): Second non-TTRPG domain. Schemas for Discord personas, agent NPCs, character authoring. Three extension schemas (voice-character, session-events-character, digest-character).
- **Akane reference fixture** (`domains/character-voice/resources/akane.yaml`): KIZUNA Fire caretaker. Full character-voice persona with engagement config, tensions, voice anchors, discipline locks, navigator pattern, yield map, decline patterns.
- **Workshop engagement tracking**: Convergence data includes per-prompt engagement distribution.

### Design Principles (new for v3)
- **Emdash ban**: The `—` is the single biggest LLM tell. Banned at protocol level.
- **Silence is data**: When a persona doesn't respond, the decision is captured and instrumented.
- **Tensions make characters round**: Contradictions are voice instructions, not bugs to fix.
- **Engagement before generation**: The persona decides whether to care before it speaks.

---

## [2.0.0] — 2026-05-12 (v2 — Creative Persona Engine)

### Changed
- **Identity reframe**: Arneson is now a *creative persona engine*, not TTRPG-specific. Gygax-inversion retained as one contextual facet, not the defining identity. `ARNESON.md`, `persona.yaml`, `expertise.yaml`, `refusals.yaml` all updated.
- **Domain broadened**: `construct.yaml` domain changed from `design` to `creative-persona`.
- **construct.yaml v2**: Skills split into core (3) + domain-registered (5 TTRPG). New `domains:` section. Schemas split into `core` + `ttrpg`.

### Added
- **Core/vertical architecture**: Domain-agnostic core (`schemas/core/`, `protocols/`, core skills) + domain verticals (`domains/ttrpg/`).
- **3 new core schemas**: `session-events-base` (domain-agnostic events), `digest-base` (domain-agnostic digest), `safety` (non-negotiable safety config).
- **4 core protocols**: `persona-hosting.md`, `session-lifecycle.md`, `safety-protocol.md`, `workshop-convergence.md`.
- **Domain extension interface**: Five-part contract (state, personas, events, resolution, consumer). Convention-based discovery via `domains/*/`.
- **TTRPG reference vertical**: `domains/ttrpg/` with domain conventions doc, extension schemas (`session-events-ttrpg`, `digest-ttrpg`), 5 skills, fallback archetypes.
- **Workshop-then-serialize pattern** (FR-C8): `workshop_state` field added to `voice-base` schema. Two valid shapes documented. Informed by arneson#2.
- **Extension story**: `examples/test-domain/` with minimal domain (3 schemas, 1 skill, sample state + persona). CI validates zero-core-change constraint.
- **Consumer-pattern guide** (`docs/CONSUMER-PATTERNS.md`): Distinguishes workshop tool vs doctrine reference shapes.
- **Extension guide** (`docs/EXTENSION-GUIDE.md`): Step-by-step guide for adding new domains.
- **Governance**: `CONTRIBUTING.md`, `SECURITY.md`.
- **Three-matrix CI**: arneson-alone, arneson-with-gygax, extension-story.

### Architecture
- Core skills (domain-agnostic): `/arneson`, `/distill`, `/voice`
- TTRPG skills (reference vertical): `/braunstein`, `/scene`, `/narrate`, `/improvise`, `/fragment`
- `/voice` elevated to core (workshop convergence is domain-agnostic)
- Gygax remains a sibling composition, not a domain
- Base+extension schema pattern for all structured data

### Functional Requirements Addressed
- FR-C1 through FR-C9 (9 core requirements)
- FR-T1 through FR-T9 (9 TTRPG requirements, regression from v1)
- FR-X1 (persona portability, Nice to Have)

### Design Principles (carried from v1, expanded)
- **Standalone-plus-composable**: works without Gygax; amplified by Gygax
- **Director/performer**: practitioner always directs; Arneson always performs
- **Workshop-then-serialize**: the iteration loop IS the product
- **Safety is non-negotiable**: every domain, every session, every mode
- **Dual-audience output**: human-readable transcripts + machine-parseable sidecars

---

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
- **Synthetic reference fixture**: Threshold (folk-horror microgame) with tradition lore + 4 scene seeds
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
