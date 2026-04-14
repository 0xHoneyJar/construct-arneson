# Agent Working Memory (NOTES.md)

> This file persists agent context across sessions and compaction cycles.
> Updated automatically by agents. Manual edits are preserved.

## Active Sub-Goals
<!-- Current objectives being pursued -->

**READ FIRST at cycle start (before `/plan`, `/ride`, or any analysis):**
1. `grimoires/loa/context/00-READ-FIRST-proposal-issue-3.md` — the construct-arneson proposal (GH issue 0xHoneyJar/construct-gygax#3)
2. `grimoires/loa/context/arneson-v1-concept.md` — full design document referenced by the proposal

Build target: **construct-arneson v1** — companion construct to Gygax for narrative generation, NPC voicing, live playtesting (flagship: `/braunstein`). Composes with Gygax v3 via grimoire artifacts.

## Discovered Technical Debt
<!-- Issues found during implementation that need future attention -->

## Blockers & Dependencies
<!-- External factors affecting progress -->

- Assumes Gygax v3 is installed in composing projects (for `skills/cabal/`, `grimoires/gygax/game-state/`, intent fields, probability scripts).

## Session Continuity
<!-- Key context to restore on next session -->
| Timestamp | Agent | Summary |
|-----------|-------|---------|
| 2026-04-13 | mount | Repo initialized, Loa mounted (submodule v1.71.1). Staged proposal issue #3 and arneson-v1-concept.md in `grimoires/loa/context/` as READ-FIRST cycle-start context. No code written yet — planning not yet run. |
| 2026-04-13 | plan-and-analyze | Discovery interview in progress. Phases 1-3 complete: qualitative success = "admissibility" (transcripts trustworthy as Gygax re-analysis evidence); timeline = quality-driven, no fixed ship; audience = Gygax community from day one (designer-only, no player UX); teammate feedback absorbed on structural tagging, intent interface, shared archetypes, safety-as-data, and `/distill` skill addition. |
| 2026-04-13 | plan-and-analyze | PRD generated: grimoires/loa/prd.md (853 lines, 17 FRs, 12 risks, 6 goals, 6 use cases). User approved; routed to architect. |
| 2026-04-13 | architect | SDD generated: grimoires/loa/sdd.md. Filesystem-first skill graph architecture, 7 YAML schemas specified, state machines for session flows, CI matrix design (arneson-alone + arneson-with-gygax). Resolved architect's open questions; 5 remain deferred to Phase 1 or v2. Ready for /sprint-plan. |
| 2026-04-13 | sprint-plan | Sprint plan generated: grimoires/loa/sprint.md. 7 sprints mapped to PRD milestones M0–M7 (M6+M7 merged). Sprint 2 (Vertical Slice) carries 8 FRs; Sprint 3 (Admissibility) is the MVP milestone. All 6 PRD goals mapped to contributing tasks + validation in Sprint 7 E2E. Ready for /implement sprint-1. |
| 2026-04-13 | sprint-0-prototype | Pre-sprint prototype executed: one /braunstein turn hand-authored against a minimal synthetic fixture (Threshold — folk-horror, HEKATE-free) as a hollow-fiction risk mitigation (R-2). Artifacts: `grimoires/loa/prototypes/sprint-0/` (threshold-game.md, newcomer-voice.md, turn-01.md). Self-critique passed on 5/5 axes (grounding, archetype-distinctness, intent fidelity, identity refusal, admissibility). One finding to carry into Sprint 1: "no narrator omniscience inside archetype voice" — encode in identity/ARNESON.md or /braunstein SKILL.md prompt. User confirmed: green-light Sprint 1. |
| 2026-04-13 | implement sprint-1 | Sprint 1 Foundation complete. 10 tasks delivered: construct.yaml, identity layer (4 files), 7 schemas (experiential_intent, voice-base + 3 extensions, session-events, digest), 9 fallback archetypes + README, synthetic fixture (Threshold game + folk-horror tradition + scene seeds), grimoire scaffold, CI workflow + 5 validation scripts. All 5 CI checks green locally. Implementation report: grimoires/loa/a2a/sprint-1/reviewer.md. Ready for /review-sprint sprint-1. |
| 2026-04-13 | review-sprint sprint-1 | **APPROVED with noted concerns.** Feedback: grimoires/loa/a2a/sprint-1/engineer-feedback.md. 7 concerns (all non-blocking for Sprint 1 scaffold): no beads tasks materialized (process); fallback archetype names are invented guesses (coordination risk with Gygax); schema validation is parse-only (no JSON Schema); CI never exercised on GitHub Actions; HEKATE audit filter is fragile; digest.schema has unenforceable inline prose; ARNESON.md first-person voice may cause role confusion in Sprint 2 prompt engineering. 2 assumptions challenged: (a) Gygax persona.yaml shape compatibility, (b) Threshold fixture exercises all 8 skills adequately. 1 alternative not considered: JSON Schema vs Loa-native YAML. Sprint 2 must: materialize tasks in beads, coordinate with Gygax on archetype names, and scope voice boundaries carefully in /braunstein prompt. |

## Decision Log
<!-- Major decisions with rationale -->

- **2026-04-13:** Created construct-arneson as a separate repo (not a branch/skill inside Gygax) because Gygax's refusal-to-generate-fiction is a load-bearing identity contract. Adding narrative-generation inside Gygax would dilute its trustworthiness as an analyst. See issue #3 "Why This Must Be a Separate Construct."
- **2026-04-13:** Qualitative success metric for v1 = **admissibility** — a `/braunstein` transcript is trustworthy enough for Gygax re-analysis to cite it as evidence. Mirrors Gygax's "trustworthy analysis" contract. Source: /plan-and-analyze Phase 2.
- **2026-04-13:** v1 audience scope = **Gygax community from day one** (not just MIBERA: HEKATE designer). Every skill must work across Gygax-supported traditions at v1. Raises the bar on tradition-generality. Source: /plan-and-analyze Phase 3.
- **2026-04-13:** v1 player scope = **designer-only**. No direct player UX; archetypes simulate players inside `/braunstein`. Player-facing mode is v2. Source: /plan-and-analyze Phase 3.
- **2026-04-13:** **Standalone-plus-composable** is a design principle. Arneson must work without Gygax installed; Gygax must work without Arneson installed. Composition is opt-in amplification, not dependency. Archetype SSOT in Gygax becomes "Gygax-overrides-Arneson-fallback" rather than "Arneson-requires-Gygax." `/distill` emits useful output even when no Gygax consumer exists. Source: /plan-and-analyze Phase 4.
- **2026-04-13:** Intent schema ownership = axis-split. Gygax owns `mechanical_intent`; Arneson owns `experiential_intent`. Each construct authors the axis matching its native work. Answers proposal open questions #1 and #5 (yes, Arneson needs a schemas directory). Gygax will need a minor-version bump to split its current single-axis `intent` into the two-axis schema. Source: /plan-and-analyze Phase 4.
- **2026-04-13:** `/distill` shape = **automatic sidecar + explicit skill**. `/braunstein` always writes prose transcript AND `{session}.events.yaml` sidecar (structured real-time capture). `/distill` is an explicit post-hoc skill that consumes both and emits a Gygax-ingestible digest. Sidecar is valuable alone (readable by any analyzer), satisfies standalone-plus-composable rule. Source: /plan-and-analyze Phase 4.
- **2026-04-13:** Technical decisions: archetype memory = 3-session sliding window; dice = user-configurable default 'user rolls'; tradition fallback = structural improvisation + user confirmation; voice schema = shared base + type-specific extensions; Chaos Agent = narrative-bounded + structurally-unbounded. Source: /plan-and-analyze Phase 5.
- **2026-04-13:** **NO MIBERA: HEKATE in construct-arneson development.** User correction. HEKATE is private/upstream. v1 ships HEKATE-free. Proposal's success criterion "/braunstein --newcomer runs against MIBERA: HEKATE game-state" (issue-3:193) is REFRAMED: v1 ships a **synthetic neutral reference fixture** in `examples/` (or `fixtures/`) — a minimal testbed game authored for Arneson that exercises the full skill set across traditions. This also aligns with community-from-day-one shippability. Source: /plan-and-analyze Phase 6.
- **2026-04-13:** Build ordering = **vertical slice first, then extract**. Ship `/braunstein` end-to-end against the synthetic fixture (with sidecar + safety + intent), then refactor out `/narrate`, `/voice`, `/scene`, `/distill` from real usage, then `/improvise`, `/fragment`, `/arneson`. Admissibility pressure-tests early; primitives extracted from real use. Source: /plan-and-analyze Phase 6.
- **2026-04-13:** Out-of-scope v1 (explicit): campaign arc modeling beyond 3-session archetype memory. Source: /plan-and-analyze Phase 6.

## Teammate Feedback — Gygax-Side Composition Requirements (2026-04-13)

Received during /plan-and-analyze Phase 4. Treating as authoritative composition requirement from the Gygax side. Resolves several proposal open questions (#2, #3, #4).

### 1. Structural Tagging Requirement (load-bearing)
`/braunstein` transcripts are not prose — they are *data*. Arneson must emit a structured sidecar (or inline tags) during playtests. When an archetype makes a move, Arneson logs WHY based on game-state Gygax provided. Must distinguish:
- **Fictional friction** (e.g., "NPC dialogue felt repetitive")
- **Mechanical bottleneck** (e.g., "only one viable social stat")

This is what makes the admissibility success metric mechanically precise, not just vibes.

### 2. Intent Interface — Two-Axis Schema
Formal schema for intent blocks in game-state YAML. Two axes:
- **Mechanical Intent** — what the math should do (e.g., "this roll is hard")
- **Experiential Intent** — what it should feel like (e.g., "this roll should feel desperate")

Requirement: when designer changes intent (Lethal → Heroic), Arneson's voicing shifts without manual prompt-tuning. Arneson reads both axes; never fudges fiction to overrule mechanical intent.

### 3. Shared Archetypes — Single Source of Truth
Gygax's `identity/persona.yaml` + `expertise.yaml` are SSOT for the 9 archetypes. Arneson consumes the SAME behavioral definitions Gygax uses for math-sim. No duplication; Arneson does not define archetypes.

**Edge case**: Chaos Agent archetype risks blowing context window. Open question: **Structural Chaos** vs **Narrative Chaos** distinction — can the narrative axis be bounded while the structural axis remains fully chaotic? (Or vice versa.)

### 4. Safety as a Data Point
Safety triggers (X-card, Line, Veil) are not only social events — they are **Dead Design Space** findings. Log as design constraints. Open question: do they belong in balance-report or playtest-report? (Probably both, with cross-reference.)

### 5. New Skill: `/distill`
Post-playtest skill. Converts a session into a Gygax-ingestible format. Identifies:
- Every moment a rule was invoked
- Every time a rule was ignored in favor of "rule of cool"
- Every clarifying question a player asked

This is the composition glue. `/distill` output is what `/cabal --from-session` and future Gygax analyzers actually consume. Binary admissibility check for v1: Gygax can round-trip a `/braunstein` session through `/distill` → `/cabal` without manual reformatting.
