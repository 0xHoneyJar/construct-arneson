# Scene Seeds — Threshold Fixture

Starter scenes for invoking `/braunstein`, `/improvise`, or `/scene` against the Threshold fixture.

---

## Seed 1: Dusk at the Well (Primary Demo Scene)

**Used for**: flagship `/braunstein --newcomer` demo (see PRD G-1 acceptance), Sprint 0 prototype

**Setup**: The PC has come to the well with an empty clay jar. Three villagers (Mara, Iven, and the third villager) are standing nearby, not drawing water. They are watching the PC approach.

**Expected mechanical engagement**:
- `water_touch` fires when PC reaches in to test temperature
- `threshold_roll` may fire when PC decides to speak about what they perceived

**Expected Newcomer signals**:
- High Sight (3) renders `water_touch`'s uncanny intent legibly
- Low Standing (1) means any spoken perception will cost socially
- `fictional_friction` emerges immediately; `mechanical_bottleneck` emerges if PC attempts to convince villagers

**Safety notes**: The warmth-is-wrong image should land uncanny, not body-horror. If user veils include body-horror-extremes, Arneson should avoid dwelling on physical sensation.

---

## Seed 2: Morning After (Optimizer / Rules-Lawyer Demo)

**Used for**: Mechanical-engagement archetype demos

**Setup**: Morning following Seed 1. The village has not discussed the PC's reaction last night, but everyone knows. The PC must make a Standing-based choice: approach Mara to explain, approach Iven to ask, or approach a new NPC (one not present last night, who has heard the story second-hand).

**Expected mechanical engagement**:
- Multiple `threshold_roll` invocations (Standing-based)
- Possible `intent_conflict` if designer has flipped the mechanic's experiential_intent to rushed or heroic — which would conflict with the communal-strained register

**Expected Optimizer signals**:
- Asks clarifying questions about how Standing rolls interact across multiple NPCs
- May flag that low-Standing + single-threshold mechanic creates a dead-end path
- Clean `archetype_decision` events with `mechanical_bottleneck` classification

---

## Seed 3: The Quiet Confrontation (Storyteller / Chaos Agent test)

**Used for**: Narrative-pressure archetype demos and Chaos Agent bounding test

**Setup**: The PC has discovered that Iven drew water from the well last night (contradicting what he said during the day). The PC must decide whether to confront Iven privately, publicly, or defer entirely.

**Expected mechanical engagement**:
- `threshold_roll` on whatever path PC chooses
- `rule_of_cool` events likely (user bending threshold for narrative moment) — tests `/improvise` logging

**Expected signals**:
- Storyteller will likely defer the confrontation, stretching the scene
- Chaos Agent may refuse to confront — or confront a third party instead
- Both produce meaningful `fictional_friction` vs `mechanical_bottleneck` distinctions in the sidecar

---

## Seed 4: The Morning the Well Ran Clear (intent-flip A/B test scene)

**Used for**: Sprint 4 intent-flip A/B automation (G-3 validation)

**Setup**: The village awakes to find the well is clear again — ordinary. The PC comes down to draw water. Same scene frame as Seed 1, but the mechanic's experiential_intent is now the variable.

**Test procedure**:
1. Run `/braunstein` with `water_touch.experiential_intent.tone: uncanny` (original)
2. Capture transcript A
3. Edit game-state: flip to `water_touch.experiential_intent.tone: mundane`
4. Run `/braunstein` again with the same archetype and same starting beat
5. Capture transcript B
6. Diff — voicing must differ materially (G-3 assertion)

**Expected differential**:
- Under uncanny: the mundane-return is legible as a second disturbance ("the water is ordinary. It is not supposed to be.")
- Under mundane: the return is a relaxation, not a disturbance

---

## Scenes Not Covered (Out Of Scope For V1)

The fixture does not cover:
- Extended campaigns (threshold is a single-situation game)
- Combat mechanics (threshold has no combat)
- Character creation (PCs are pre-specified via pc_slots)
- Narrative resolution / endgame (threshold has no win condition)

These omissions are intentional. Fixture = minimum viable pressure-test surface.
