# construct-arneson

A narrative construct for TTRPG designers. Voices characters, stages scenes, runs playtests, instruments fiction.

Named for [Dave Arneson](https://en.wikipedia.org/wiki/Dave_Arneson) — co-creator of D&D, who brought the first dungeon crawl (Blackmoor, 1971), campaign structure, and improvisational GMing to the hobby Gary Gygax then codified.

**Pairs with [construct-gygax](https://github.com/0xHoneyJar/construct-gygax).** Gygax analyzes. Arneson plays. Together they form a complete design-and-play workbench. Apart, each works on its own.

---

## What Arneson Does

Arneson generates fiction that is grounded in your game-state and instrumented for analysis. Every session produces two outputs:

- A **prose transcript** — the session itself, readable as a standalone document
- A **structured sidecar** — every decision, signal, roll, and friction point tagged with game-state references

This makes playtests **admissible as evidence** in design analysis. Gygax (or any tool that reads YAML) can ingest the sidecar and extract findings without reading the prose.

## Skills

| Command | What it does |
|---------|-------------|
| `/braunstein` | **Flagship.** Live playtest. You GM, Arneson plays an archetype from the cabal as an actual character. Dialogue, in-character reactions, dice rolls, structured sidecar emission. |
| `/voice {npc}` | Embody a specific NPC for workshop-style dialogue. Voice state persists across sessions. |
| `/scene {seed}` | Generate a scene from a seed, oracle result, or prompt. Grounded in game-state. |
| `/narrate {outcome}` | When a mechanic fires, generate the fiction that flows from it. The fiction-mechanics-fiction atom. |
| `/improvise` | Inverse of `/braunstein` — Arneson GMs, you play a PC. For testing the GM-facing side of a design. |
| `/distill {session}` | Compress a session into a Gygax-ingestible digest. Rule invocations, rule-of-cool overrides, clarifying questions, dead design space. |
| `/fragment {scope}` | Generate setting material — locations, factions, histories, items. |
| `/arneson` | Status dashboard. What sessions exist, which NPCs are voiced, archetype memory state. |

## Quick Start

```
/braunstein --newcomer --game-state path/to/your/game-state.yaml
```

Arneson loads the Newcomer archetype, reads your game-state, opens with a safety agreement (Lines & Veils, X-card), and plays. You GM. The Newcomer responds in character.

When you're done, `/distill` the session to extract findings.

## Identity

Arneson is the inverse of Gygax. Where Gygax refuses to generate fiction, Arneson embraces it. Where Arneson refuses to analyze structure, Gygax embraces it.

| Arneson embraces | Arneson refuses |
|-----------------|-----------------|
| Writing fiction | Structural analysis |
| Voicing characters | Probability math |
| In-fiction decisions | Mechanical recommendations |
| Narrative prose | Pattern-matching against anti-patterns |

The refusals are load-bearing. They are what make Arneson trustworthy as a playtest instrument — the fiction is bounded by the designer's intent, not bent by analytical opinion.

## Two-Axis Intent

Arneson reads two intent axes on every mechanic:

- **Mechanical intent** (owned by Gygax) — what the math should do
- **Experiential intent** (owned by Arneson) — how it should feel

When `mechanical_intent` says lethal, the fiction is lethal. When `experiential_intent` says uncanny, the prose breathes uncanny. When they conflict, mechanical intent wins on outcome; experiential intent wins on prose quality.

## Composition with Gygax

When Gygax is installed alongside Arneson, the constructs compose:

```
Gygax /cabal analysis
  -> designer edits mechanic
  -> Arneson /braunstein plays the change
  -> Arneson /distill compresses the session
  -> Gygax /cabal --from-session analyzes the transcript
  -> next iteration
```

Without Gygax, Arneson runs standalone. Fallback archetypes ship with the construct. The sidecar and digest are self-describing — readable by any YAML consumer.

## Safety

Session-length skills (`/braunstein`, `/voice`, `/improvise`) open with a safety agreement:

- **Lines** — topics that will not appear
- **Veils** — topics handled off-stage
- **X-card** — type `/x-card` to halt immediately

When a safety tool fires, the trigger is logged as a **dead design space** finding — a region of the game-state that this table cannot render. Safety events are design data, not only social events.

## Architecture

construct-arneson is a [Loa framework](https://github.com/0xHoneyJar/loa) skill-pack construct (schema_version 3). No traditional backend — the skills are prompt-engineering documents that run in Claude Code via the Loa harness. State is YAML and markdown in `grimoires/arneson/`.

```
construct-arneson/
  construct.yaml            # manifest
  identity/                 # who Arneson is
  schemas/                  # 7 YAML schemas (intent, voice, events, digest)
  skills/                   # 8 skills (SKILL.md + index.yaml each)
  resources/                # fallback archetype bundle (9 archetypes)
  examples/                 # synthetic test fixture (Threshold game)
  grimoires/arneson/        # runtime state (sessions, voices, scenes, fragments, digests)
```

## Requirements

- [Loa framework](https://github.com/0xHoneyJar/loa) mounted (submodule or standard)
- [Claude Code](https://claude.ai/claude-code) CLI
- `yq` v4+ for YAML processing
- Gygax v3+ for composition (optional — Arneson works standalone)

## License

See LICENSE file.

---

*"Together they invented the hobby. Apart they specialized."*
