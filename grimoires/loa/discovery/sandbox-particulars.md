# Sandbox Particulars: From Playtest to Re-runnable Experiment

**Status:** Discovery artifact · **Date:** 2026-06-09 · **Author:** Fable 5
**Feeds:** the parked agent-sandbox cycle. Companions: `observability-layers.md` (instrumentation),
`arneson-independent-commitments.md` (cross-repo brief), `seam-strawman.md` (the Gygax seam).
**Framing:** observability answered "can a stranger verify what happened." These five answer the
sandbox question proper: "can the same thing be made to happen again, and would two runs be
comparable?" All five are Gygax-independent and producer-side.

---

## 1. Scenario as a first-class, re-runnable artifact

Today a session is ad-hoc: someone invokes `/braunstein`, picks an archetype, plays. A *sandbox*
needs the run setup to be a committed artifact — `scenario.yaml`:

- state ref + checksum (what world)
- persona ref + checksum (who plays)
- visibility mask (what they're allowed to see — see §2)
- stopping condition (objective reached / N turns / signal threshold / open-ended)
- memory policy (fresh | continuing — see §4)
- optional GM script (see §5)

The sidecar preamble then cites `scenario_id` + `run_id`. This is the single highest-leverage
sandbox particular: it turns "we played it once" into "run 7 of scenario S against state v2," and
it's what makes the /scry fork workflow (play the forked state) reproducible rather than anecdotal.

## 2. Context manifest + visibility mask (evaluation-awareness hygiene)

The awareness ladder makes "what the persona knows" the experimental variable — so it must be
*recorded*, not implied. Two halves:

- **Visibility mask (declared, in scenario.yaml):** which parts of the spec/state the persona may
  see, and — critically — what it must NOT see. The test's own purpose ("we're checking whether
  you game this incentive") in the persona's context contaminates the forecast: that's the
  observer effect for hosted personas.
- **Context manifest (logged, in sidecar preamble):** what actually went into the persona's
  context — file refs + hashes. "Fully-aware adversary" is unverifiable unless the sidecar shows
  exactly what the adversary was shown.

This also formalizes an existing finding: sprint-0's "no narrator omniscience inside archetype
voice" is the same separation (host-context ≠ persona-context), now made mechanical. Gygax intent
fields, designer concerns, and experiment purpose live host-side unless the mask grants them.

## 3. Simulation containment as a declared invariant

The direction doc says the real-agent runner is not Arneson. The inverse guarantee needs declaring
too: **a hosted agent's "actions" are narrated events, never executed.** No tool calls, no file
writes, no network on the persona's behalf — the sandbox's walls. This belongs in
`identity/refusals.yaml` (or a containment protocol) *before* the agent-systems domain exists,
because the spec files an agent-under-incentive is grounded in are untrusted input; containment is
what makes hosting an adversarial persona safe by construction. Cheap to state now, expensive to
retrofit after a vertical ships without it.

## 4. Memory policy per run

The 3-session sliding window (ARNESON.md) is right for *play continuity* and wrong for
*forecasting*: independent forecast runs contaminated by memory of prior runs aren't independent.
Make it explicit per scenario: `memory: fresh` (default for forecast-type runs) vs
`memory: continuing` (campaign/TTRPG default). Stamp the policy in the preamble so a reader knows
which kind of run they're looking at. One field, large credibility payoff.

## 5. Comparability mechanics (honest variance, fair forks)

- **Scripted-GM mode:** an optional GM script in the scenario fixes the human side, so comparing
  state-fork A vs B (the scry+braunstein combined workflow) is apples-to-apples — the only
  variable is the state. Live mode stays the default for exploration; scripted mode exists for
  comparison runs.
- **N-run honesty:** one run is an anecdote; N runs of the same scenario show spread. Arneson's
  job is only to make runs cheap to repeat and tagged (`scenario_id`, `run_id`,
  `origin: simulation-derived`) — reading the spread is Gygax's. No statistics language from
  Arneson's side; the banned-copy rule (§5 of the direction doc) applies to variance claims too.

---

## Deliberately not proposed

- **Persona-drift self-detection** — "did the model stay in character" is a judgment; the
  mechanical share is already covered (persona checksum in the preamble, workshop convergence as
  the fidelity tool). Arneson flagging its own drift would be Arneson interpreting Arneson.
- **In-sandbox metrics/scoring** — same refusal. The sandbox counts and stamps; it never grades.

## Adoption note

If these land, items 1, 2, and 4 add fields to the scenario/preamble surface that the Gygax ingest
will eventually read — shapes worth showing to the Gygax design early (same caution as seq/origin
in the commitments brief). Item 3 is identity-zone. Item 5 is skill-logic only.
