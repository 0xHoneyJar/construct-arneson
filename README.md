# construct-arneson

A creative persona engine. Hosts personas grounded in structured state, emits structured data from creative sessions. TTRPG design is the first vertical — not the identity.

Named for [Dave Arneson](https://en.wikipedia.org/wiki/Dave_Arneson) — co-creator of D&D, who brought improvisation, campaign structure, and collaborative fiction-within-rules to the hobby. The name evokes the fiction-generating, improvisational side of creative work.

**Pairs with [construct-gygax](https://github.com/0xHoneyJar/construct-gygax)** in the TTRPG domain. Gygax analyzes. Arneson plays. Together they form a complete design-and-play workbench. Apart, each works on its own.

---

## What Arneson Does

Arneson generates fiction that is grounded in your structured state and instrumented for analysis. Every session produces two outputs:

- A **prose transcript** — the session itself, readable as a standalone document
- A **structured sidecar** — every decision, signal, and friction point tagged with state references

The practitioner always directs. Arneson always performs. The canonical mode is **iterative workshop** — converging a persona's voice across multiple sessions until it locks.

## Core Skills (Domain-Agnostic)

| Command | What it does |
|---------|-------------|
| `/voice {persona}` | Workshop a persona's voice iteratively until it converges. The canonical Arneson flow. |
| `/distill {session}` | Compress a session into a downstream-consumable digest shaped by the domain's consumer spec. |
| `/arneson` | Status dashboard — active sessions, personas, domains. |

## TTRPG Skills (Reference Vertical)

| Command | What it does |
|---------|-------------|
| `/braunstein` | **Flagship.** Live playtest. You GM, Arneson plays an archetype. Dialogue, dice, structured sidecar. |
| `/scene {seed}` | Generate a scene from game-state + seed. Grounded in your world. |
| `/narrate {outcome}` | When a mechanic fires, generate the fiction that flows from it. |
| `/improvise` | Inverse of `/braunstein` — Arneson GMs, you play a PC. |
| `/fragment {scope}` | Generate setting material — locations, factions, histories, items. |

## Domain Extensibility

Arneson v2 is built around a **domain extension interface**. New creative domains (game writing, agent persona development, worldbuilding) can be added without touching core code:

```
domains/{your-domain}/
  schemas/       # Extend core schemas
  skills/        # Domain-specific skills
  resources/     # Domain resources
```

See `docs/EXTENSION-GUIDE.md` for the step-by-step guide. The TTRPG vertical (`domains/ttrpg/`) is the reference implementation.

## How to Use Arneson

There are two valid shapes. See `docs/CONSUMER-PATTERNS.md` for details.

1. **Workshop tool** (canonical) — invoke `/voice` iteratively across sessions until voice converges. This is what Arneson is designed for.
2. **Doctrine reference** (consumer) — serialize a locked voice-state into a static prompt. Valid only AFTER the workshop has converged.

## Architecture

```
schemas/core/           # Domain-agnostic schemas (voice-base, events-base, digest-base, safety)
protocols/              # Behavioral contracts all skills follow
skills/                 # Core skills (arneson, distill, voice)
domains/ttrpg/          # TTRPG reference vertical (schemas, skills, resources)
examples/test-domain/   # Extension story validation
grimoires/arneson/      # Runtime state (sessions, voices, scenes, digests)
```

## Quick Start

```
/braunstein --newcomer
```

Starts a live playtest session with the Newcomer archetype against your game-state.

## License

See LICENSE file.
