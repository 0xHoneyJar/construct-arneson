# Project Description (from /plan)
> Auto-generated from user's initial project description.

Freeside-characters adapter implementation — closing the blocking gaps between spec and execution.

The v3.2 cycle delivered the adapter specification, consumer declaration, and SKILL.md documentation. All spec work is complete and committed. What's missing is the actual executable implementation that makes the spec real.

## Scope: 4 Blocking Gaps

1. **Format detection + adapter loading** — `/voice --source` needs to detect persona.md format (markdown with YAML frontmatter vs pure YAML), select the freeside adapter from construct.yaml consumers, and load ingest rules dynamically.

2. **Persona.md ingest parsing** — extract voice-character state from persona.md sections per the adapter spec in `domains/character-voice/adapters/freeside.yaml`. Parse markdown sections (OG voice anchor, battle whispers, voice discipline lock, decline patterns, yield patterns, modes, world presence) into voice-character schema fields.

3. **Atomic two-layer emit** — serialize voice-character state back to persona.md updating BOTH the reference body sections AND the system prompt template sections in a single atomic write. The sync contract in the adapter spec defines which fields map to which locations in both layers.

4. **Real persona.md fixture** — create a synthetic but realistic persona.md file in freeside format (based on akane.yaml reference data) and round-trip test it through ingest → modify → emit to validate the adapter works end-to-end.

## Key Files (already exist)
- Adapter spec: `domains/character-voice/adapters/freeside.yaml`
- Voice-character schema: `schemas/core/voice-character.schema.yaml`
- Reference fixture (YAML): `domains/character-voice/resources/akane.yaml`
- Canon data: `domains/character-voice/resources/akane-canon.yaml`
- Consumer declaration: `construct.yaml` (consumers section)
- Voice skill doc: `skills/voice/SKILL.md`
- Distill skill doc: `skills/distill/SKILL.md`

## Important Context
- This is a construct (persona engine framework), not a traditional app
- "Implementation" means skill logic, adapter tooling, and test fixtures — not a web app or API
- The construct is consumed by freeside-characters (Discord bot) via persona.md files
- The adapter must be bidirectional: read persona.md → workshop → write persona.md
