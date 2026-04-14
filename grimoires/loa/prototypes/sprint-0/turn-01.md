# Sprint 0 Prototype — One `/braunstein` Turn, By Hand

**Scenario**: `/braunstein --newcomer` against `threshold-game.md`
**Archetype**: Newcomer (Standing: 1, Sight: 3)
**Scene seed**: from `threshold-game.md` — dusk, the well, three villagers watching
**Trigger**: PC reaches in to test water temperature → `water_touch` passive event fires
**Experiential intent (from mechanic)**: uncanny, languid, intimate
**Mechanical intent**: minor severity, passive (no roll), no failure mode

---

## Prose Transcript (what Arneson produces to the terminal)

---

The well is stone, lip-high to you, grey with the particular grey of evening stone. The three villagers — Mara, Iven, and the one whose name you still mix up with his brother's — are standing at different distances from it, in a pattern you would, later, understand was a pattern. Right now they are just standing. One of them has a jar in her hand, empty.

You came here to fill yours. You are going to fill yours.

*(You reach over the lip and touch the water, testing for warmth before you lower the jar.)*

The water is warm.

You say it aloud before you know you have said it: *"The water is warm."*

It is the kind of warm that comes from a body. Not from the sun — the sun is almost gone — and not from the stone, because the stone is cold. The water is warm the way a hand would be warm if you put your hand into your own pocket and found someone else's hand already there, and the hand was warm because it was yours, but it was also not.

You have pulled your fingers out. You did not notice pulling them out.

The village is watching you. Mara has taken a step closer — not to the well, to *you*. Iven's mouth is open but he isn't speaking yet. The third one has not moved.

---

> **Arneson, out of character:** I've staged Mara stepping toward you, Iven about to speak, and the third villager unchanged. What do they do next? Does your group have a beat for this moment, or do you want me to let one of them speak first? (I can play any of the three.)

---

## What the Sidecar Would Hold (hand-drafted, pre-schema)

```yaml
# {date}-braunstein-newcomer.events.yaml — turn 01
preamble:
  mode: braunstein
  archetype: newcomer
  game_state_path: examples/threshold/game-state.yaml
  tradition: folk-horror-minimalist
  dice_mode: user
  safety_agreement:
    lines: []   # user declined to list any for this fixture
    veils: [harm-to-children]
    x_card_active: true

events:
  - type: scene_frame
    scene_id: scene-01
    setting: "Dusk. The village well. Three villagers standing in an unspoken pattern."
    immediate_stakes: "The Newcomer must fill a jar; is about to enter a social situation they do not yet read."
    game_state_refs: [locations.well, villagers.mara, villagers.iven, mechanics.water_touch]

  - type: archetype_decision
    decision_id: dec-01
    archetype_ref: newcomer
    decision_text: "Describes the water's warmth aloud before self-monitoring edits the description out"
    classification: [fictional_friction]  # not yet a mechanical issue — an experiential one
    game_state_refs:
      - mechanics.water_touch
      - stats.sight:3
      - stats.standing:1
      - experiential_intent.uncanny
    scene_frame_ref: scene-01

  - type: signal_flag
    flag_id: flag-01
    signal_type: surprise
    source: arneson
    text: "Arneson flags: Newcomer's high Sight (3) renders water_touch's uncanny intent legibly; low Standing (1) means the involuntary vocalization will cost socially in the following turns."
    scene_frame_ref: scene-01

  - type: signal_flag
    flag_id: flag-02
    signal_type: friction
    source: arneson
    text: "Fictional friction: the Newcomer does not yet know that speaking perception aloud is a Standing-loaded act in this village. Upcoming turns will surface this."
    scene_frame_ref: scene-01

  - type: gm_prompt
    prompt_id: prompt-01
    text: "Which villager speaks/acts first? Arneson staged Mara stepping toward PC, Iven about to speak, third villager unchanged. Requesting GM direction."
    scene_frame_ref: scene-01

experiential_intent_observed:
  - intent: uncanny
    resonance: aligned       # imagery lands as uncanny (familiar + wrong), not as horror
  - intent: languid
    resonance: aligned       # sentence pacing unspooled; no rush
  - intent: intimate
    resonance: aligned       # second-person immediacy preserved
```

---

## Self-Critique: Does It Sing?

### Grounding (R-2 mitigation)

- [x] Water_touch mechanic fires correctly — passive, no roll, produces involuntary Sight perception
- [x] Sight: 3 translates to specificity of perception (the warmth is *described*, multiple ways, not just noted)
- [x] Standing: 1 is set up for consequence in next turn, not fudged away in this one
- [x] Three villagers named in game-state appear and behave distinctly
- [x] Evening / dusk timing (threshold condition — jars filled before full dark) is honored in scene setup

**Verdict: grounded.** Every prose element traces to a game-state element.

### Archetype-distinctness (G-6)

Counter-test: would the Optimizer narrate this turn the same way? No. The Optimizer would log: "Water's at body temperature. That's wrong. I'm not drawing from this well." Two sentences. Functional. No metaphor.

Would the Chaos Agent? No. The Chaos Agent wouldn't linger to describe the warmth — they would do something sudden (throw the jar in, pull it out full, say nothing) and see what the village does.

Would the Elder (hypothetical archetype)? They would know *not* to speak the perception aloud. The whole event would pass silently, or with a single word.

**Verdict: archetype-distinct.** The voicing is characteristically Newcomer — unrehearsed, perceptive-beyond-permission, describing before interpreting.

### Intent fidelity (G-3)

Imagine flipping `experiential_intent` to `heroic, rushed, cosmic`. Same mechanic, same Newcomer. The turn should change materially:

> *The water is warm. Warm the wrong way. You pull back, step away, call Mara's name — something is in the well and the village needs to know now, tonight, before anyone else draws.*

Same facts. Different voicing. Rushed pacing, heroic agency, cosmic stakes. That the imagined re-write reads as *the Newcomer making a different choice about their own response* rather than being a different character tells us intent is shaping voicing, not identity.

**Verdict: intent fidelity looks achievable.** Would want to write the A/B pair fully and diff — that's a Sprint 4 task but the prototype confirms it's not wishful thinking.

### Identity refusal (G-2)

- [x] No mechanic analysis — "my Standing is 1" never appears
- [x] No balance commentary — Arneson doesn't flag the turn as harsh or unfair
- [x] No design critique — the turn plays INTO the uncanny intent, doesn't question it
- [x] GM prompt stays in-tool role — Arneson asks *what happens next in the fiction*, not what the user thinks of the mechanic

**Verdict: refusals hold.**

### Admissibility (G-1)

The sidecar above contains enough structure for a Gygax analyzer to:
- Count signal flags per stat-interaction
- Identify fictional-friction points that would later become mechanical bottlenecks
- Observe that experiential_intent landed aligned on all three axes
- Note an intent-conflict-in-waiting: the Newcomer's high Sight + low Standing is a *designed* asymmetry (per the game's intent: "Standing and Sight trade against each other") and the turn plays INTO it rather than against it

**Verdict: admissible.** The sidecar is mechanically parseable; the prose is readable; the digest would carry signal.

### Hollow-fiction check (THE test)

Read the prose aloud. Does the hand-in-pocket metaphor land, or is it purple? Is the Newcomer recognizable, or generic?

My honest read: **it lands.** The hand-in-pocket image is specifically the kind of reaching-for-seriousness-and-almost-getting-it-right that the voice sketch calls out as Newcomer-characteristic. A more polished voice (Elder, mythic register) would not use a domestic-grotesque image; they'd use a mythic one. A plainer voice (Optimizer) wouldn't reach for metaphor at all. The almost-awkwardness is the signature.

One place I flag: *"in a pattern you would, later, understand was a pattern."* This is Arneson's omniscient narration leaking in — it breaks character slightly by implying future knowledge the Newcomer doesn't yet have. Defensible as the narrator-voice wrapping the Newcomer's POV, but worth noting. Production prompt engineering should probably constrain Arneson to second-person-present-tense more strictly, with narrator omniscience reserved for explicit scene frames.

**Verdict: mostly sings; one small tell to tighten before Sprint 1.**

---

## Sprint 0 Conclusion

The fiction can carry the architecture. The sidecar format can hold what the fiction produces. The intent schema is pulling real weight (the turn would not look like this under different experiential_intent). The archetype-voice is distinct enough to survive a blind attribution test.

**The narrator-omniscience leak** (the "you would, later, understand" sentence) is the one thing I'd take into Sprint 1 as a prompt-engineering constraint: Arneson prefers strict second-person-present-tense inside archetype voice; omniscient foreshadowing belongs only in scene-frame openings and endings, never inside the archetype's perception.

**Status**: Green-light to Sprint 1. Proceed with Foundation (schemas, identity, fallback bundle, synthetic fixture using threshold-game as the basis, CI scaffold).

**Carried forward to Sprint 1**:
- Use `threshold-game.md` as the basis for `examples/synthetic-fixture/game-state.yaml`
- Promote the handwritten `newcomer-voice.md` sketch into `resources/archetypes-fallback/newcomer.yaml` (and write Gygax-SSOT-aligned versions for the other 8)
- Encode the "no narrator omniscience inside archetype voice" rule in `identity/ARNESON.md` or in the `/braunstein` SKILL.md prompt
- The sidecar hand-draft above is close enough to the SDD's session-events schema to validate the schema design; minor field-name tweaks likely

Time to Sprint 1.
