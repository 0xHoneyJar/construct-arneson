# Arneson — Companion Construct Concept

Captured 2026-04-13 for future construct-arneson cycle. This document stages the design direction for a companion construct to Gygax.

## The Framing

Dave Arneson — co-creator of D&D alongside Gary Gygax. Arneson brought:
- The first dungeon crawl (Blackmoor, 1971)
- The campaign structure (returning to the same world)
- Improvisational GMing approach
- Freeform narrative within structural rules

Where Gygax was the rules-codifier and wargaming systematizer, Arneson was the fiction-generator and campaign-runner. Together they invented the hobby. Apart they specialized.

The construct pair mirrors this historical complementarity:
- **Gygax**: analyzes, balances, stress-tests, compares — refuses to write fiction
- **Arneson**: voices, narrates, generates, improvises — refuses to do structural analysis

## Identity Inversion

| Gygax refuses | Arneson embraces |
|---------------|------------------|
| Writing fiction | Writing fiction as its primary work |
| Final creative decisions | Making in-fiction decisions (as characters, as the world) |
| Voicing NPCs | Voicing NPCs is the core skill |
| Narrative prose | Narrative prose is the output format |

| Gygax embraces | Arneson refuses |
|----------------|-----------------|
| Structural analysis | System analysis (that's Gygax) |
| Balance math | Probability analysis |
| Cross-system consistency | Consistency checking |
| Design heuristics | Pattern matching against anti-patterns |
| Recommending mechanical changes | Making mechanical recommendations |

## Core Skill Concepts

### /braunstein (the flagship)
Live playtest session. User GMs, Arneson plays an archetype (from Gygax's cabal definitions). Dialogue, in-character reactions, dice rolls, real-time experience signal capture.

Named after Arneson's 1969 proto-RPG Braunstein, which led directly to D&D.

### /voice {npc-id}
Embody a specific NPC for workshop-style dialogue. Useful when a designer wants to test a social encounter or NPC voice. Arneson stays in character until the session ends.

### /scene {seed or oracle result}
Generate a scene from a prompt or oracle table output. Produces opening situation, sensory detail, immediate stakes. Grounded in game-state.

### /narrate {mechanic outcome}
When a mechanic fires, generate the "new fiction" that flows from it. Implements the PbtA-derived fiction-mechanics-fiction loop at the tooling level.

### /improvise
Inverse of braunstein — Arneson GMs, user plays a PC. For testing the GM-facing side of a design. Arneson runs the world, voices NPCs, interprets mechanics into fiction.

### /arneson
Status dashboard — active sessions, voiced NPCs, recent scenes, campaign continuity state.

## Composition with Gygax

**Arneson reads Gygax's outputs:**
- `grimoires/gygax/game-state/` — mechanics, stats, resources, tensions (for grounding)
- `skills/cabal/resources/archetypes.yaml` — for embodying playtesting archetypes authentically
- Entity `intent` fields — to play into deliberate asymmetries, not against them
- `skills/lore/resources/{tradition}.yaml` — to understand what makes this tradition's fiction feel right

**Gygax reads Arneson's outputs:**
- `grimoires/arneson/sessions/*.md` — live session transcripts, consumable by `/cabal --from-session`
- `grimoires/arneson/voices/*.yaml` — NPC state that affects game-state

**Combined workflows:**

1. **Design iteration closed loop:**
   Gygax analyzes → designer changes → Arneson plays the change in braunstein → Gygax re-analyzes the transcript → next iteration.

2. **Scry + Arneson:**
   `/scry "what if threshold was 4?"` forks game-state. `/braunstein --fork threshold-4 --newcomer` plays the forked version. Designer experiences the change fictionally, not just numerically.

3. **Intent validation:**
   Gygax's intent fields say "the inversion IS the game." Arneson plays INTO that inversion — the Newcomer experiencing the drama of succeeding against type, not just noting its statistical shape.

## Grimoire Structure

```
grimoires/arneson/
  voices/
    archetypes/           # Archetype-as-character state (memory across sessions)
      newcomer.yaml
      optimizer.yaml
      ...
    npcs/                 # Workshop NPCs
      masked-mibera.yaml
    pcs/                  # PC voices when user needs Arneson to play a party member
  scenes/                 # Generated scenes (can be replayed or fed to cabal)
    {date}-{scope}.md
  sessions/               # Live playtest transcripts
    {date}-{mode}-{archetype-or-pc}.md
  improv/                 # Freeform Arneson-as-GM sessions
  fragments/              # Setting fragments, location descriptions, NPC sketches
  changelog/
```

## Key Design Decisions to Make in v4 Cycle

### 1. Safety mechanics integration
Arneson generates fiction. For games touching sensitive content, it MUST support X-card/Lines-and-Veils equivalents. Probably needs a pre-session agreement step and session-level pause commands.

### 2. Archetype memory across sessions
If the Newcomer was confused by CROSSROADS last session, do they carry that memory? State lives in voices/archetypes/*.yaml. Needs design: how aggressive is the learning? Does the Newcomer stop being a Newcomer after 5 sessions?

### 3. Experience signals in live vs post-hoc
Current cabal captures signals post-hoc from the walkthrough. Arneson needs to capture them live — flagged by the archetype as they emerge. "I hit confusion here because the trigger references DOSE and I don't know what DOSE means."

### 4. Dice resolution authority
Who rolls? Options:
- Arneson rolls (faster, but user loses agency over randomness)
- User rolls and reports (maintains user control, slower)
- Arneson rolls but user confirms (hybrid)

Probably configurable per session.

### 5. Handoff format to Gygax
Live session transcripts need a structured format Gygax can analyze. Not just prose — structured events (scene frames, dice rolls with context, signal flags, intent conflicts, GM prompts). Compatible with `/cabal --from-session` consumption.

### 6. Construct slug and identity
Slug: `arneson`. Persona: warm, collaborative, improvisational. Voice: generous with possibility, grounded in whatever game you're playing, respectful of the designer's vision.

Consider: `identity/ARNESON.md` as prose identity narrative, distinct from Gygax's.

## The Bigger Picture

Together, Gygax + Arneson become something larger than either: a complete design-and-play workbench. Gygax tells you what's happening structurally. Arneson lets you feel what's happening fictionally. The designer can iterate between the two modes fluidly.

No other TTRPG tooling does this. Spreadsheets handle structure. LLM chats handle fiction. Neither grounds in a persistent game-state that flows both ways. A Gygax+Arneson pair would be the first tooling to treat design and play as iterative partners at the tool level.

This is a v4 (or v1 for construct-arneson) concept. Not v3 work. Captured now to stage the direction.
