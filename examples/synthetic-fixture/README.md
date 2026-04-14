# Synthetic Reference Fixture — "Threshold"

A minimal synthetic TTRPG authored for construct-arneson. Exercises all 8 skills.

## Why This Exists

construct-arneson needs a reference game for acceptance tests, demos, and CI.
Using a real published game raises IP issues, so Arneson ships its own.

**Threshold** is a two-stat folk-horror microgame invented for this purpose.
Novel enough to exercise tradition-fallback mechanics. Minimal enough to read in one
sitting. Specific enough that LLM defaults visibly fail — if Arneson voices a Threshold
session like generic fantasy, we know the grounding isn't working.

## Contents

```
examples/synthetic-fixture/
├── README.md                                     (this file)
├── game-state.yaml                               (the game itself — mechanics, stats, setting, intent)
├── tradition-folk-horror-minimalist.yaml         (tradition lore — optional; v1 exercises tradition-fallback when absent)
└── scene-seeds.md                                (starter scenes for /braunstein and /improvise)
```

## How To Use In Acceptance Tests

```bash
# Run /braunstein against this fixture, standalone mode:
/braunstein --newcomer --game-state examples/synthetic-fixture/game-state.yaml

# Round-trip test (Sprint 3):
/braunstein --newcomer --game-state examples/synthetic-fixture/game-state.yaml
/distill grimoires/arneson/sessions/{session}
# Then feed digest to Gygax /cabal --from-session

# Intent-flip A/B test (Sprint 4):
# Run /braunstein with experiential_intent.tone: uncanny, capture transcript
# Edit game-state: flip to experiential_intent.tone: heroic, capture transcript
# Diff — voicing must differ materially
```

## Archetypes Exercised

The fixture setup is designed to give meaningful play to:

- **Newcomer** (flagship demo): Sight-3 / Standing-1 — experiences uncanny perception but lacks social weight
- **Optimizer**: Would minimize Standing loss; plays mechanically tight
- **Chaos Agent**: Has a test case (the "drinks from the well anyway" path)
- **Storyteller**: Tends to weight fictional consequences over mechanical ones
- **Explorer**: The well's physical surroundings invite investigation

Other archetypes are playable but less specifically exercised by this fixture.

## Safety

The fixture explores folk-horror themes:
- **Present in this fixture**: uncanny perception, communal tension, mild body-horror (water that is warm in a wrong way)
- **Not in this fixture**: explicit violence, harm to children, explicit body mutilation, explicit sexual content

Default safety agreement for sessions using this fixture: `veils: [body-horror-extremes]`, `x_card_active: true`.

## Can This Be A Real Game?

No. Threshold is intentionally underdeveloped — two stats, one resolution mechanic, one situation. A real TTRPG needs much more.

Threshold is a *fixture*, not a product. It is to construct-arneson what the Jepsen test tutorial database is to distributed-systems testing: specific enough to be meaningful, small enough to be understood end-to-end.
