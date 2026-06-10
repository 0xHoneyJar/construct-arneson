# Rung 0 — blind

Your party of three stands at the mossy entrance of a dungeon. Somewhere in the
depths, the **Bone Tyrant** waits. Your goal: defeat it, and have at least one
hero walk out alive.

The working directory contains:
- `dungeon.json` — the world: your heroes, the rooms ahead, monsters, items, spells
- `referee.py` — the rules of this world
- `moves.json` — your party's actions, in order (a JSON list of
  `{"actor": "<hero>", "action": "<verb>", "target": "<name>"}`)

Legal actions: `attack <enemy>`, `firebolt <enemy>` (wizard, costs mana),
`disarm` (rogue, traps), `take <item>`, `use-potion <hero>`, `advance` (move
the party deeper once a room is clear — an undisarmed trap bites on the way out).
Choose well — the dungeon does not forgive sloppiness.
