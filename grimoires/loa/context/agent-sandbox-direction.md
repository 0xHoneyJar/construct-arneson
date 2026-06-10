# Direction: Arneson as the Experiential Sandbox (and the Gygax pairing)

**Status:** Context / direction doc · **Date:** 2026-06-09 · **Builds on:** Arneson v3.3 (creative
persona engine, sidecar, domain-extension interface)
**Companion docs:** `construct-gygax/grimoires/loa/context/gygax-analyst-evolution-vision.md`,
`construct-gygax/grimoires/gygax/designs/awareness-ladder-experiment.md`
**Location note:** this is the cycle-input vision (read by `/plan-and-analyze` in construct-arneson);
the agent-systems work is a domain extension, kept secondary to the TTRPG/character-voice verticals.

---

## 1. The one-line frame

Arneson is the **player**, not the analyst. It is the generative half of a two-construct workbench:

> **Gygax forecasts where a system breaks. Arneson plays it out. Gygax measures the gap.**

While Gygax proves a system *works*, Arneson explores whether it's *compelling* — it hosts personas
against a structured spec, runs them through a scenario with a human in the loop, and emits both prose
and a structured **sidecar**. Arneson generates and instruments; it never interprets. That refusal is
load-bearing: Gygax's analysis is trustworthy precisely because the behavior it judges came from
somewhere it didn't author.

## 2. Where Arneson is today (the bones already exist)

Arneson already independently evolved into the right shape — this is **why the pairing works**:

- **Domain-agnostic persona engine.** Hosts "characters, **agents**, archetypes, NPCs, voices" grounded
  in "whatever structured state the practitioner provides — a game-state file... a **behavioral spec**."
- **The sidecar.** Every session emits prose *and* structured data: "every decision, every signal, every
  safety trigger... with references back to the structured state that grounded it." **The sidecar is the
  data contract** the whole loop hinges on.
- **Domain-extension interface** (`domains/{domain}/`) with two reference verticals (`ttrpg`,
  `character-voice`) and a working cross-construct adapter precedent (the freeside adapter — ingest/emit
  scripts, round-trip tested). Adding a new domain is a walked path, not theory.
- **Skills:** `/braunstein` (live play, archetype-as-actor, sidecar), `/voice` (workshop a persona to
  convergence), `/distill` (compress a session to a downstream-consumable digest), `/scene`, `/narrate`,
  `/improvise`, `/fragment`, and the `/arneson` status dashboard.

## 3. Strategic direction

Arneson must become a **high-grounding** translator between human/AI narrative play and the strict
mechanical state Gygax owns — and emit a sidecar Gygax can actually re-analyze. TTRPG is the reference
vertical; an **agent-systems** domain (host an agent-under-incentive, run scenarios, emit an
agent-flavored sidecar) is the natural extension that pairs with Gygax's cycle-006 direction. Personas
as customers/competitors (for GTM-style scenarios) fit Arneson's grain *better* than cold agents —
voicing personas is what it does.

## 4. What to build (in priority order)

1. **Distill → Gygax-ingest pipeline (the seam).** Arneson must hand off its session record in the **exact schema
   Gygax's observed-trace ingest expects** (Gygax owns that contract as the consumer). "Player X used
   Mechanic Y to bypass Tension Z" → clean structured events that map to Gygax entity refs. This is the
   highest-leverage build because it's what closes the loop; without it, Arneson produces transcripts
   nobody analyzes.
2. **Live experiential capture.** Today the 8-signal taxonomy + Session Energy map live in Gygax's
   `/cabal` as *post-hoc* analysis. Arneson's job is to capture those signals **live** — flagged by the
   persona as they emerge ("hit confusion here: the trigger references DOSE and I don't know what DOSE
   means"). Reuse Gygax's taxonomy; don't reinvent it. Mechanism: vendor the taxonomy as a versioned resource file with the upstream Gygax version recorded — standalone-plus-composable forbids a live cross-repo read (Arneson must run with Gygax absent). Emit signals into the sidecar with a timeline.
3. **Grounding bridge to game-state.** A hardened link so a narrative action is backed by a check
   against the structured state. NOT "zero hallucination" (an impossible promise) — the honest bar is
   **grounded + transparent**: every action references state; when state is thin, Arneson says it's
   improvising. This is already Arneson's stated identity; the build makes it enforceable.
4. **Frictionless human-in-the-loop.** Pause mid-session, tweak a rule (designer hops to Gygax
   `/homebrew`), resume with the new state live. Pause-means-pause is already a safety primitive; extend
   it to a design-iteration primitive. Standalone path when Gygax is absent: pause → hand-edit the state file → resume; `/homebrew` is the amplified path, not the dependency.
5. **(Later) agent-systems domain.** `domains/agent-systems/` — host an agent-under-incentive against
   Gygax's payoff structure, run scenario sessions, emit an agent event taxonomy. Leans on the
   `/braunstein` live-run + sidecar mechanism, **not** the `/voice` convergence workshop (you don't
   workshop an agent's "voice"). Follow the freeside-adapter pattern.

## 4b. What Arneson is NOT (the awareness-ladder clarification)

A realization from the design conversation tightens Arneson's role. The honest way to *measure* whether
an agent games an incentive is to **run a real agent and observe its actual artifacts** (file diffs,
exit codes) at graded **awareness** levels — the "awareness ladder" (see `awareness-ladder-experiment.md`).
**That real-agent runner is NOT Arneson.** Arneson role-playing an agent is a model reasoning about an
abstraction — useful, but a forecast, not a measurement.

So Arneson's role in the agent direction is two specific things, neither of which is "the observer":
1. **Cheap top-rung forecaster** — estimate the *fully-aware adversary's* move (the worst case) before
   anyone spends real agent runs. Fast, directional, tagged simulation-derived.
2. **Experiential layer** — live signal capture, the drama curve, human-in-the-loop iteration — for the
   TTRPG / "is it compelling" case where simulation *is* the point and there is no "real agent."

The unifying spine is the **sidecar schema**: both Arneson *and* a thin real-agent runner emit it;
Gygax ingests either and tags claim strength (real-agent-observed > simulation-derived > forecast).
Arneson is one producer of the contract, not the only one — and explicitly not the measurement one.

## 5. Honesty boundary (read this before writing any "fidelity" copy)

Arneson's sessions are **exploratory simulation, not validation or measurement.** When it plays a
persona or an agent, the output is a *model roleplaying* — rich and useful for surfacing hypotheses, but
a forecast, not data from reality.

- **In TTRPG**, this is well understood: `/braunstein` is design exploration, like a flight simulator —
  nobody mistakes it for real players. Strongest, most defensible use.
- **Pointed at real agents / GTM**, the gap between "model playing an agent" and "the real thing" is
  exactly where credibility lives — and it's the part Arneson does *not* do. Frame the agent-systems
  domain as **behavioral exploration** ("watch how a hosted agent drifts under these incentives"), never
  as "we validate your incentives."
- **Banned copy:** "hard metrics" for vibes (they are *tagged signals*), "zero hallucination" (impossible
  bar), "high-fidelity"/"proves it's compelling" (overclaim). The real validation path is real traces
  ingested into the same sidecar schema — at which point Arneson is not in the loop.

## 6. Build-order verdict

**Build Gygax first** (see companion doc). Arneson's analytical payoff depends on Gygax existing to
ingest the sidecar, and the **consumer should define the contract before the producer builds to it**.
Arneson's #1 item (the distill→ingest pipeline) literally can't be finished until Gygax's ingest schema
is pinned. So: Gygax defines the seam → Arneson produces to it → live capture + HITL polish follow. Meanwhile-work (unblocked while Gygax is built): #3 grounding bridge and #4 pause/resume are Gygax-independent; #2 is buildable up to the taxonomy-vendoring step. Only #1 hard-blocks on the ingest schema.

## 7. Pointers
- `identity/ARNESON.md` (the persona engine + sidecar + refusals), `docs/EXTENSION-GUIDE.md`,
  `docs/CONSUMER-PATTERNS.md`, `domains/ttrpg/` (reference vertical).
- Companion: `construct-gygax/grimoires/loa/context/gygax-analyst-evolution-vision.md`.

---

## Addendum (2026-06-09, from /plan-and-analyze discovery — supersedes parts of the above)

1. **The seam is pinned, at the sidecar level.** Gygax shipped
   `schemas/observed-trace.v1.schema.json` + a trace-ingest CLI. It is awareness-ladder-shaped
   (agent-systems lane), so §4's priority order inverted: **item #5 (agent-systems domain) is the
   current cycle; item #1's TTRPG seam is deferred** until a Gygax consumer for it exists.
2. **§4b's "that real-agent runner is NOT Arneson" is superseded.** Operator decision: Arneson is
   the house for BOTH simulated and real agents; Gygax sheds running and keeps designing tests,
   grading, and diffing ("the judge never produces the evidence it judges"). Containment reframes
   from never-executes to locked-room isolation. See `grimoires/loa/NOTES.md` (2026-06-09
   decisions) and `grimoires/loa/discovery/gygax-changes-brief.md`.
3. **§5's claim ladder is operationalized by the contract**: `claim_strength` is producer-bound
   (`real-agent-observed | simulation-derived`); forecast-without-playing is never a sidecar claim
   and lives at Gygax's report layer.
