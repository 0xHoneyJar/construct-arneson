# TTRPG Domain Conventions

> How the TTRPG vertical implements the five-part domain extension contract.
> This document IS the extension interface documentation — other domains follow this pattern.

**Domain name:** `ttrpg`
**Status:** Reference implementation

---

## 1. Structured State

**What it is:** Game-state YAML files describing mechanics, locations, factions, entities, intents, and traditions.

**Convention:** The practitioner provides a path to their game-state directory. Skills read it at DomainLoad.

**Example:** `examples/synthetic-fixture/game-state.yaml` — a neutral reference game with mechanics, villagers, locations, scene seeds, and a folk-horror tradition file.

**Key fields consumed:**
- `mechanics.*` — rules, stats, resources
- `locations.*` — setting elements
- `villagers.*` — NPC references
- `intents.*` — mechanical_intent + experiential_intent declarations
- `traditions.*` — tradition-specific lore and tone guidance

---

## 2. Persona Definitions

**Schemas extending voice-base:**
- `voice-archetype.schema.yaml` — cabal archetypes (Newcomer, Optimizer, Chaos Agent, etc.)
- `voice-npc.schema.yaml` — workshopped NPCs
- `voice-pc.schema.yaml` — player characters (for /improvise mode)

**Fallback bundle:** `resources/archetypes-fallback/` — 9 archetype YAMLs used when Gygax is not installed. Marked `fallback_source: true`.

**Key additions over voice-base:**
- Archetypes: `archetype_ref`, `experiential_intent_weights`, `memory_window_size`, `chaos_axis_config`
- NPCs: `npc_ref`, `location`, `faction`, `role`, `tradition_affinity`
- PCs: `pc_ref`, `player_name`, `player_consent`

---

## 3. Event Taxonomy

**Schema:** `session-events-ttrpg.schema.yaml` extends `session-events-base`

**Preamble extensions:** `archetype`, `pc_ref`, `game_state_path`, `game_state_checksum`, `composition_mode`, `tradition`, `tradition_fallback_mode`, `dice_mode`

**Domain-specific event types:**
- `scene_frame` — scene opening with game-state grounding refs
- `dice_roll` — mechanical roll with intent observations
- `archetype_decision` — in-character decision with classification (fictional_friction / mechanical_bottleneck)
- `intent_conflict` — tension between mechanical and experiential intent
- `gm_prompt` — Arneson handing control to user-as-GM
- `rule_of_cool` — a rule was bent for fiction
- `clarifying_question` — question about rules or mechanics

---

## 4. Resolution Mechanics

**Skills implementing resolution:**
- `/braunstein` — user GMs, Arneson plays archetype. Dice resolution (user/arneson/hybrid).
- `/improvise` — Arneson GMs, user plays PC. Arneson resolves mechanics into fiction.
- `/narrate` — fiction-mechanics-fiction bridge. Given a mechanical outcome, generates causal fiction.
- `/scene` — generates a scene from game-state + seed. No dice.
- `/fragment` — generates setting material. No dice.

**Dice modes:** Configurable per session (`user`, `arneson`, `hybrid`). Default: `user` (practitioner rolls).

---

## 5. Consumer Specification

**Schema:** `digest-ttrpg.schema.yaml` extends `digest-base`

**Downstream consumer:** Gygax v3's `/cabal --from-session` command.

**TTRPG-specific digest findings:**
- `rule_invocations` — every rule that fired, with contexts and outcomes
- `rule_of_cool_overrides` — rules bent for fiction
- `clarifying_questions` — questions about mechanics
- `signal_flags` — grouped by type (confusion, friction, delight, etc.)
- `intent_conflicts` — mechanical vs experiential tensions
- `dead_design_space` — safety triggers as design constraints
- `experiential_intent_observations` — how well declared intent landed
- `archetype_memory_updates` — what the archetype learned this session

**Admissibility flag:** `gygax_ingestible: true/false` — whether this digest matches the current Gygax contract.

---

## Adding a New Domain

To add a new domain vertical to Arneson, create a directory at `domains/{name}/` with:

```
domains/{name}/
  domain.conventions.md     # Document your vertical (recommended)
  schemas/
    voice-{type}.schema.yaml          # Extends schemas/core/voice-base
    session-events-{name}.schema.yaml # Extends schemas/core/session-events-base
    digest-{name}.schema.yaml         # Extends schemas/core/digest-base
  skills/
    {skill-name}/
      SKILL.md              # Follow core protocols
      index.yaml            # Declare domain, type, protocols
  resources/
    {whatever your domain needs}
```

Then register your domain's skills in `construct.yaml` under `domains.{name}.skills`.

See `examples/test-domain/` for a minimal working example.
