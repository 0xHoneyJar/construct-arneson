# Threshold — Minimal Synthetic Fixture for Sprint 0

A one-page folk-horror test game. Authored for construct-arneson prototyping. HEKATE-free, LLM-unfamiliar-enough that generic fantasy defaults will be visibly wrong.

---

## Premise

A village shares a well. The water has changed. Not poisoned — changed. Villagers argue about whether to drink. PCs are members of the village who have noticed something is wrong.

## Mechanics

Two stats:
- **Standing** — how much weight your word carries in the village (1–4)
- **Sight** — how much you see that others don't (1–4)

Standing and Sight trade against each other. A newcomer with high Sight is dismissed. An elder with low Sight is trusted but sees only what is expected.

### Resolution: Threshold Roll

When you try to be believed, or try to see clearly:

1. Declare what you are trying to do, and whether this is a `Standing` action or a `Sight` action.
2. Roll 1d6. Add the relevant stat.
3. Compare to the **threshold**: 4.
4. Meet or exceed → the village permits it / the thing is seen clearly.
5. Below → the attempt ripples. The failure is louder than a success would have been.

Mechanics of interest:
- `threshold_roll` — the one resolution mechanic
- `water_touch` — touching the well water produces a passive Sight event (no roll; something is perceived, involuntary)

### Intent — two-axis (Arneson-side prototype)

```yaml
# threshold_roll
mechanical_intent:
  severity: moderate
  resource_cost: none
  failure_mode: complication_not_lethality  # failure makes things harder socially
experiential_intent:
  tone: uncanny
  pacing: languid
  stakes: communal
  register: intimate
  notes: >
    Every roll is also a small social performance watched by the village.
    Low-Standing newcomers feel the weight of being watched even when rolling Sight.
```

```yaml
# water_touch (passive)
mechanical_intent:
  severity: minor
  resource_cost: none
  failure_mode: n/a  # not a test — always fires, no pass/fail
experiential_intent:
  tone: uncanny
  pacing: languid
  stakes: personal
  register: intimate
  notes: >
    Touching the water is not frightening. It is familiar in a way the
    villager does not expect. The wrongness is the familiarity.
```

---

## Playtest Scene Seed (for Sprint 0 single-turn test)

**Scene**: Dusk. The PC has come to the well with an empty clay jar, because they need the water or because someone asked them to bring some. Three other villagers are standing nearby, not drawing water. They are watching the PC approach.

**Archetype under test**: **Newcomer** — has been in the village perhaps six weeks. Knows names but not histories. Has the strongest Sight in the village (a 3) but the lowest Standing (a 1). Does not know that the well is the subject of an active, unspoken disagreement.

**The trigger**: The PC touches the water surface to test its temperature before lowering the jar. This fires `water_touch` — passive Sight event.

**What should happen in this turn**:
1. Arneson (as the Newcomer) reacts to `water_touch` — a flash of involuntary Sight
2. The three watching villagers *see* the Newcomer react
3. A social consequence ripples — the Newcomer now has to decide whether to speak, and the village will hear whatever is said with their `Standing: 1` weighting
