# Character-Voice Domain Conventions

> How the character-voice vertical implements the five-part domain extension contract.
> For Discord personas, agent NPCs, and character authoring.

**Domain name:** `character-voice`
**Status:** v3 addition

---

## 1. Structured State

**What it is:** Canon documents that ground the persona's voice. Lore bibles, battle whispers, world references, behavioral specifications.

**Convention:** Place canon documents as YAML in `resources/`. The persona's `grounding_state_path` points to the canon file.

**Example:** `resources/akane-canon.yaml` with identity, biography, world knowledge, and constraints.

---

## 2. Persona Definitions

**Schema:** `voice-character.schema.yaml` extends `voice-base` with:
- `voice_anchors` - canon lines that define the voice signature (og_line, win, lose, draw)
- `discipline_locks` - non-negotiable behavioral rules
- `navigator_pattern` - player-side constraint (if applicable)
- `canon_boundary` - what the persona knows vs doesn't know
- `yield_map` - sibling/peer yield patterns
- `decline_patterns` - in-voice refusals for out-of-scope topics
- `modes` - operational modes (greeting, lore, siblings, etc.)

Plus all voice-base fields: speech_patterns, engagement, anti_patterns, tensions, workshop_state, etc.

---

## 3. Event Taxonomy

**Schema:** `session-events-character.schema.yaml` extends `session-events-base` with:
- `voice_drift` - drift from canon detected
- `canon_match` - output closely matches a voice anchor (positive signal)
- `engagement_decision` - record of each turn's engagement evaluation

---

## 4. Resolution Mechanics

No domain-specific skills in v3. The core `/voice` skill handles workshop sessions. Character-voice uses `/voice` with its schema extensions.

Future (v4): `/serialize-character` for generating consumer-ready system prompts from locked voice-state.

---

## 5. Consumer Specification

**Schema:** `digest-character.schema.yaml` extends `digest-base` with:
- `voice_drift_events` - all drift events grouped by type
- `canon_match_rate` - how well the persona matched its anchors
- `engagement_profile` - engagement distribution snapshot
- `anti_pattern_violations` - any LLM tells detected

---

## Adding a Character

1. Create a canon file in `resources/` (YAML with identity, biography, world knowledge)
2. Create a voice-character persona in `resources/` or `grimoires/arneson/voices/npcs/`
3. Fill in: voice_anchors (at minimum og_line), speech_patterns, engagement config
4. Run `/voice {character-id}` to workshop iteratively
5. When locked, serialize for your consumer (Discord bot, agent framework, etc.)

---

## Consumer Adapters

When Arneson workshops a persona that lives in an external system (Discord bot, agent framework, etc.), an **adapter** handles the bidirectional format translation.

### How Adapters Work

An adapter is a YAML file in `adapters/` that declares:
- **Ingest rules**: How to read the consumer's format and extract voice-character fields
- **Emit rules**: How to write voice-character state back to the consumer's format
- **Sync contract**: Which fields must update multiple locations atomically

### Available Adapters

| Adapter | Consumer | Format | Path |
|---------|----------|--------|------|
| `freeside.yaml` | freeside-characters | markdown persona.md with system prompt template | `adapters/freeside.yaml` |

### Adding an Adapter

Create a YAML file in `adapters/` following the freeside adapter structure:

```yaml
adapter:
  name: your-consumer
  format: your-format
  
  ingest:
    # consumer format -> voice-character fields
    
  emit:
    # voice-character fields -> consumer format
    
  sync_contract:
    # which fields must update multiple locations
```

Then register in `construct.yaml` under `domains.character-voice.consumers`.

---

## Scripts

Adapter scripts handle deterministic parsing and serialization. The LLM workshop handles creative voice development — scripts are tools, not participants.

| Script | Purpose | Interface |
|--------|---------|-----------|
| `scripts/ingest_persona.py` | persona.md -> voice-character YAML | `python3 ingest_persona.py <path>` (stdout: YAML) |
| `scripts/emit_persona.py` | voice-character YAML -> persona.md | `python3 emit_persona.py --template <md> --state <yaml>` (stdout: md) |
| `scripts/test-roundtrip.sh` | Validate ingest -> emit round-trip | `./test-roundtrip.sh` (exit 0/1) |

**Dependencies:** Python 3.10+, standard library only (no pip installs).

**Exit codes:** 0 success, 1 parse error, 2 sync contract violation.

---

## Reference Fixtures

- `resources/akane.yaml` - Akane (KIZUNA, Fire element, Naughty). Full character-voice persona in YAML format.
- `resources/fixtures/test-persona.md` - Compass (Guild Cartographer). Synthetic character in freeside persona.md format for round-trip testing.
