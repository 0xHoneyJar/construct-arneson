---
priority: READ-FIRST
scope: cycle-start
source: https://github.com/0xHoneyJar/construct-gygax/issues/3
issue_number: 3
issue_state: OPEN
issue_title: "Proposal: construct-arneson — companion construct for narrative generation and live playtesting"
companion_context: arneson-v1-concept.md
---

> # LOA: READ THIS FIRST AT CYCLE START
>
> This file is the **entry point** for any new cycle in the `construct-arneson` repo.
> Before `/plan-and-analyze`, before `/ride`, before any other context load, read:
>
> 1. **This file** (issue #3 — the proposal and scope)
> 2. **`arneson-v1-concept.md`** (in this same directory — the full design doc referenced by the issue)
>
> These two documents are the grounding for construct-arneson v1. Any planning,
> architecture, or sprint work that does not reference them is out of scope.
>
> Cross-repo origin: this issue lives in `0xHoneyJar/construct-gygax` because it
> proposes a *companion* to Gygax. The implementation happens *here*, in
> `construct-arneson`. When acting on this proposal, treat Gygax's grimoires as
> upstream read-only composition targets, not as part of this repo.

---

# GitHub Issue #3 — construct-gygax

**URL:** https://github.com/0xHoneyJar/construct-gygax/issues/3
**State:** OPEN
**Title:** Proposal: construct-arneson — companion construct for narrative generation and live playtesting

---

## Summary

Proposal to create **construct-arneson**, a companion construct to Gygax that handles everything Gygax deliberately refuses: fiction generation, NPC voicing, scene framing, live playtesting, and improvisational GMing.

Named after Dave Arneson — co-creator of D&D alongside Gary Gygax. Arneson brought the first dungeon crawl (Blackmoor, 1971), campaign structure, and improvisational GMing to the hobby Gygax then codified. The construct pair mirrors the historical complementarity: Gygax is the rules-architect, Arneson is the fiction-generator. Together they invented the hobby; as tools, together they form a complete design-and-play workbench.

## Why This Must Be a Separate Construct

Gygax's identity is load-bearing. Its persona explicitly refuses to generate narrative prose, voice characters, or make final creative decisions. These refusals are what make Gygax trustworthy as an analyst — users know the structural findings haven't drifted into storytelling.

Adding fiction-generation capabilities inside Gygax would weaken that contract. The cleanest architectural answer is a separate construct with an inverse identity — Arneson — that composes with Gygax via grimoire artifacts rather than running inside the same persona.

## Identity Inversion

| Gygax refuses | Arneson embraces |
|---------------|------------------|
| Writing fiction | Writing fiction as primary work |
| Final creative decisions | Making in-fiction decisions (as characters, as the world) |
| Voicing NPCs | Voicing NPCs as the core skill |
| Narrative prose output | Narrative prose as the output format |

| Gygax embraces | Arneson refuses |
|----------------|-----------------|
| Structural analysis | System analysis (that's Gygax's job) |
| Balance math, probability scripts | Probability analysis |
| Cross-system consistency checking | Consistency checking |
| Curated + learned design heuristics | Pattern matching against anti-patterns |
| Recommending mechanical changes | Making mechanical recommendations |

**Voice:** Where Gygax is opinionated and Socratic, Arneson is warm and generative. Where Gygax says 'I don't know enough about this tradition to have a strong opinion,' Arneson says 'here's what your NPC says next, and why.' Where Gygax surfaces gaps in knowledge, Arneson fills them with imaginative grounding.

## Proposed Skill Set

| Command | What it does |
|---------|--------------|
| `/arneson` | Status — active sessions, voiced NPCs, recent scenes, campaign continuity state |
| `/braunstein` | **Flagship.** Live playtest session. User GMs, Arneson plays an archetype (from Gygax's cabal definitions) as an actual character. Dialogue, in-character reactions, dice rolls, real-time experience signal capture. Named after Arneson's 1969 proto-RPG that led directly to D&D. |
| `/voice {npc-id}` | Embody a specific NPC for workshop-style dialogue. Designer iterates on a character's voice until it's right. Arneson stays in character until the session ends. |
| `/scene` | Generate a scene from a seed, oracle table output, or user prompt. Produces opening situation, sensory detail, immediate stakes. Grounded in game-state. |
| `/narrate` | When a mechanic fires, generate the 'new fiction' that flows from it. Implements the PbtA-derived fiction-mechanics-fiction loop at the tooling level. |
| `/improvise` | Inverse of braunstein — Arneson GMs, user plays a PC. For testing the GM-facing side of a design. Arneson runs the world, voices NPCs, interprets mechanics into fiction. |

## Composition with Gygax

The pair's value comes from the grimoire-level composition.

**Arneson reads Gygax outputs:**
- `grimoires/gygax/game-state/` — mechanics, stats, resources, tensions (for grounding)
- `skills/cabal/resources/archetypes.yaml` — for embodying playtesting archetypes authentically
- Entity `intent` fields — to play INTO deliberate asymmetries, not against them
- `skills/lore/resources/{tradition}.yaml` — to understand what makes this tradition's fiction feel right

**Gygax reads Arneson outputs:**
- `grimoires/arneson/sessions/*.md` — live session transcripts, consumable by `/cabal --from-session`
- `grimoires/arneson/voices/*.yaml` — NPC state that affects game-state

**Combined workflows:**

1. **Closed-loop design iteration:** Gygax analyzes → designer changes → Arneson plays the change in braunstein → Gygax re-analyzes the transcript → next iteration. Structural and experiential analysis couple.

2. **Scry + Arneson:** `/scry 'what if threshold was 4?'` forks game-state. `/braunstein --fork threshold-4 --newcomer` plays the forked version. Designer experiences the change fictionally, not just numerically. This is the killer combined feature.

3. **Intent validation:** Gygax's intent fields say 'the inversion IS the game.' Arneson plays INTO that inversion — the Newcomer experiencing the drama of succeeding against type, not just noting its statistical shape.

4. **Reverse workflow (design-by-play):** Arneson improvises sparse sessions. Gygax watches the transcripts and extracts what structural rules the fiction seems to want. Emergent design from narrative up, not top-down. No existing tooling does this.

## Proposed Grimoire Structure

```
grimoires/arneson/
  voices/
    archetypes/           # Archetype-as-character state (memory across sessions)
      newcomer.yaml
      optimizer.yaml
      gm.yaml
      ...
    npcs/                 # Workshop NPCs
      masked-mibera.yaml
    pcs/                  # PC voices when user needs Arneson to play a party member
  scenes/                 # Generated scenes (can be replayed or fed to cabal)
    {date}-{scope}.md
  sessions/               # Live playtest transcripts (braunstein + improvise modes)
    {date}-{mode}-{archetype-or-pc}.md
  improv/                 # Freeform Arneson-as-GM session logs
  fragments/              # Setting fragments, location descriptions, NPC sketches
  changelog/
```

## Architectural Principles

1. **Grounded fiction only.** Every NPC Arneson voices is grounded in game-state. Every oracle roll uses the designer's actual tables. Every archetype is grounded in Gygax's cabal behavioral profiles. This is what distinguishes Arneson from a generic LLM chat — the fiction is BOUNDED by the designer's design.

2. **Personas are first-class.** Arneson doesn't do voices. Arneson HOSTS personas — archetypes, NPCs, PCs — each with their own state, memory, and behavioral patterns. When you run `/braunstein --newcomer`, you are talking to the Newcomer, not to Arneson pretending to be the Newcomer.

3. **Intent respect.** Arneson reads Gygax's `intent` fields before playing. A mechanic marked `non_negotiable: true` is played INTO, not against. The Newcomer's confusion at a deliberate asymmetry is narrated as genuine confusion, not as a design-critique.

4. **Safety as load-bearing mechanic.** Arneson generates fiction involving potentially sensitive content. Must support safety-tool integration — X-card equivalent, Lines & Veils, session-level pause commands, pre-session agreement flow.

5. **Grimoire-as-deliverable** (shared with Gygax). Every session transcript, every voiced NPC, every generated scene is saved as presentable, exportable markdown. The grimoire IS the artifact.

## Key Design Decisions for Implementation

### 1. Archetype memory across sessions
If the Newcomer was confused by CROSSROADS last session, do they carry that memory into the next? State lives in `voices/archetypes/*.yaml`. Design question: how aggressive is the learning? Does the Newcomer stop being a Newcomer after 5 sessions? Recommendation: cap memory depth (most recent 3 sessions inform current behavior) but never fully extinguish archetype identity.

### 2. Experience signals in live vs post-hoc
Gygax's cabal captures signals post-hoc from analytical walkthroughs. Arneson must capture them IN REAL TIME — flagged by the archetype as they emerge. 'I hit confusion here because the trigger references DOSE and I don't know what DOSE means.' This requires structured signal embedding in session transcripts.

### 3. Dice resolution authority
Who rolls during braunstein? Options:
- Arneson rolls (faster, but user loses agency over randomness)
- User rolls and reports (maintains user control, slower, more authentic)
- Arneson rolls but user confirms (hybrid)
Recommendation: user-configurable per session. Default to 'user rolls' for authenticity.

### 4. Handoff format to Gygax
Live session transcripts need a structured format Gygax can analyze. Not just prose — structured events: scene frames, dice rolls with context, signal flags, intent conflicts encountered, GM prompts ('I don't know how this mechanic resolves'). Compatible with a new `/cabal --from-session {path}` consumption mode.

### 5. Construct identity files
- `identity/persona.yaml` — warm, improvisational, collaborative
- `identity/expertise.yaml` — voice work, scene framing, narrative causality, oracle interpretation, campaign continuity
- `identity/ARNESON.md` — prose identity narrative, distinct from Gygax's

### 6. Slug and manifest
- Slug: `arneson`
- schema_version: 3 (construct-base)
- type: skill-pack
- domain: design (same as Gygax, since they're design tools)
- composition_paths should declare that Arneson READS from Gygax's grimoire paths

### 7. Quick start
`quick_start.command: /braunstein` — the flagship capability, immediately demonstrates value.

## Full Design Context

A comprehensive design document has been staged in the Gygax repo at `grimoires/loa/context/arneson-v1-concept.md`. This document contains the complete architectural reasoning, grimoire structure specification, skill-by-skill detail, and open design questions.

> **NOTE for Loa in this repo:** that design document has been copied to this
> repo at `grimoires/loa/context/arneson-v1-concept.md`. Read it alongside this
> issue before planning.

## Relationship to Gygax v3

Gygax v3 just shipped (PR #2 merged 2026-04-13). v3 introduced:
- Probability scripts (foundation for Arneson's dice resolution)
- Intent tracking (Arneson must respect intent when playing)
- Cross-system comparison references (Arneson can voice NPCs from reference systems)
- `/delve` dungeon analysis (Arneson could voice dungeon inhabitants)
- 9-archetype cabal system (Arneson's braunstein uses these archetype definitions)
- Cepheus tradition support (Arneson must handle sci-fi-flavored fiction)

Arneson is designed as a clean v1 build that ASSUMES Gygax v3 is installed. The composition is explicit in Arneson's construct.yaml.

## Success Criteria for construct-arneson v1

- [ ] Construct validates at L0/L1/L2
- [ ] `/braunstein --newcomer` runs a live playtest session against a MIBERA: HEKATE game-state
- [ ] Session transcript is presentable standalone markdown with structured event format
- [ ] `/cabal --from-session {path}` (added to Gygax) can consume Arneson transcripts
- [ ] Safety mechanics work (user can pause, trigger X-card equivalent)
- [ ] Intent-aware — playing a mechanic with `non_negotiable: true` intent plays INTO the design
- [ ] At least 3 archetypes voiced distinctly (different speech patterns, reaction times, knowledge levels)
- [ ] Composition with Gygax verified: Arneson reads game-state, writes transcripts Gygax can analyze

## Open Questions for Implementer

1. Does Arneson need its own schemas directory, or can it reuse Gygax's construct.schema.json?
2. Should voice files (archetypes/npcs/pcs) use a shared schema or diverge?
3. How does Arneson handle games in traditions it wasn't specifically prepared for? Fall back to structural improvisation, or request user guidance?
4. Is `/improvise` (Arneson GMs, user plays PC) a core v1 feature or v2? Recommendation: v1 — it's the symmetric counterpart to `/braunstein` and lets designers test both sides of the table.
5. Should Arneson have a `/fragment` subcommand for generating setting material (locations, histories, factions), or is that out of scope? Recommendation: yes, v1 — setting fragments are low-effort, high-value for designers building worlds.
