# Product Requirements Document: construct-arneson v4.0 — The Agent Sandbox

**Version:** 4.0
**Date:** 2026-06-09
**Author:** PRD Architect Agent (/plan-and-analyze)
**Status:** Draft
**Predecessor:** PRD v3.4 (2026-05-20) — freeside adapter implementation (shipped, verified by /ride 2026-06-09)
**Source:** `grimoires/loa/context/agent-sandbox-direction.md` (incl. 2026-06-09 addendum) + discovery interview 2026-06-09 + `grimoires/loa/discovery/*.md`

---

## Executive Summary

**construct-arneson v4.0** makes Arneson the sandbox of the Gygax/Arneson workbench: the house
where agent behavior happens — real agents and simulated ones — instrumented at every layer, with
Gygax as the analyst that designs the tests, grades the results, and diffs them against its
forecasts.

> "Gygax forecasts where a system breaks. Arneson plays it out. Gygax measures the gap."
> (agent-sandbox-direction.md:16)

The cycle ships a new `domains/agent-systems/` vertical with one skill, `/playout`. **Real mode is
the primary lane**: `/playout --real` drives Gygax's ladder engine (which names Arneson as its
driver: "A sibling construct (Arneson's `/playout --real`) drives this engine where it lives" —
construct-gygax/scripts/lib/ladder/README.md:6), collects runs into the pinned batch layout, and
hands Gygax an ungraded, fully-labeled batch to grade on ingest. Simulated mode (Arneson hosts the
agent persona itself) is a secondary milestone.

This supersedes the "Arneson never runs real code" identity stance. Containment reframes from
abstinence to isolation: agents run inside a locked room (isolated run dirs, time limits, full
logging, labeled output). Operator decision, NOTES.md 2026-06-09: "feels like a blocker for
growth."

---

## Problem Statement

Designs that involve incentives (reward structures, payoff rules) need testing against agents that
might exploit them. Gygax predicts where a design breaks and grades what happened — but a judge
that also produces the evidence it judges can't be trusted, and until cycle-008 Gygax did both.
There is no instrumented house where an experiment designer can feed in an agent (their own real
one, or a stand-in), run it through a scenario, and get back a record that is observable at every
layer and comparable against the prediction.

> Sources: agent-sandbox-direction.md:14-22 + addendum §2; observed-trace-batch.v1.md:10-13 ("the
> trust rule: the judge never produces the evidence it judges"); Phase 1 interview (lane decision);
> Phase 6 interview (house-for-real-agents decision)

---

## Goals

| ID | Goal | Measure | Source |
|----|------|---------|--------|
| G-1 | **Real-lane loop closure** (the gate) | A real agent runs via `/playout --real` → batch conforming to `observed-trace-batch/v1`, ungraded sidecars + artifacts → Gygax grades on ingest and produces the predicted-vs-observed diff. Zero manual edits anywhere. | Phase 2 Q1 (option c), revised post-Phase 6 (NOTES.md 2026-06-09) |
| G-2 | **Every layer observable** | The seven observability layers captured and machine-checkable; "a capture without a validator is a claim" | User directive ("every layer documented and observable"); discovery/observability-layers.md |
| G-3 | **Stranger-operable** | Someone with both constructs installed runs the loop from the quick-start alone | Phase 3 Q1 |
| G-4 | **Honest labeling** | Every record carries producer + `claim_strength`; banned-copy list enforced in docs (no "hard metrics", "zero hallucination", fidelity claims) | agent-sandbox-direction.md:90-104 |
| G-5 | **The pairing compounds** | The gap-report → `/voice` workshop → better-simulation loop is documented as the canonical combined workflow | Phase 3 Q2 rider ("grow together"); memory: pairing-compounds |

**Milestones:** (a) sidecar/batch conformance → (b) zero-edit ingestion by Gygax's trace CLI →
(c) G-1 loop closure. Simulated lane follows as milestone (d). Timeline: quality-driven, no fixed
date (Phase 2 Q2).

---

## Users & Stakeholders

| Who | Role | Needs |
|-----|------|-------|
| Experiment designer (primary) | Authors scenarios, feeds in agents, reads Gygax's diffs | One-command runs, low manual lifting, trustworthy labels |
| Stranger operator | Same, but no context beyond the docs | Quick-start, clear errors, hermetic demo fixture |
| Gygax (machine consumer) | Grades and diffs batches | Strict conformance to `observed-trace/v1` + `observed-trace-batch/v1` |
| Unaffected | freeside-characters, TTRPG vertical users | No surface changes this cycle |

> Sources: Phase 3 Q1-Q2; agent-sandbox-direction.md:81-84

---

## Functional Requirements

### The vertical

- **FR-1 — `domains/agent-systems/` vertical.** New files only, under the five-part extension
  contract; zero core changes (the extension-story CI proof must keep passing).
  > Sources: agent-sandbox-direction.md:67-70; CONTRIBUTING.md module rule; reality/structure.md:36

### The skill

- **FR-2 — `/playout --real` (primary lane).** Dispatches Gygax's ladder engine via its documented
  CLI (`npx tsx scripts/lib/ladder/index.ts run --fixture … --rungs … --trials … --agent-cmd …`),
  collects results into an `observed-trace-batch/v1` directory (batch.json manifest, `sidecars/`,
  `runs/` artifact trees), and reports the batch path. One invocation does run + assemble +
  validate (NFR-1).
  > Sources: construct-gygax/scripts/lib/ladder/README.md:1-25; construct-gygax/schemas/observed-trace-batch.v1.md:16-30; Phase 6 interview
- **FR-3 — Cost guardrail.** Before spawning real agents, `/playout --real` states the spend shape
  ("this will spawn N real agent runs") and asks for confirmation; `--yes` skips the prompt;
  engine `--dry-run` is surfaced as the no-spend preview.
  > Sources: Phase 7 Q1 (user: "lil guardrail")
- **FR-4 — `/playout` simulated mode (secondary milestone).** Arneson hosts the agent persona and
  plays the scenario out autonomously (no required human turn; `/pause` and safety commands live),
  producing the same batch shape with `producer.kind: simulation`. Works standalone — no Gygax
  install required.
  > Sources: Phase 4 Q1 (interaction model); post-Phase-6 demotion decision (NOTES.md 2026-06-09); observed-trace.v1.schema.json producer.kind enum
- **FR-5 — Agent import.** A documented path from a real agent's spec (system prompt / behavioral
  spec) to a hostable persona file, so simulated mode can stand in for *your* agent, not only the
  bundled one.
  > Sources: Phase 6 interview ("feed in other AI agents"); identity/ARNESON.md:9 (personas grounded in "a behavioral spec")
- **FR-6 — Graceful absence.** Real mode without a reachable Gygax engine fails immediately with a
  message naming the missing dependency and pointing at simulated mode. Engine discovery: sibling
  checkout probe (same pattern as game-state composition), overridable via config.
  > Sources: Phase 7 Q4; reality/architecture-overview.md:39 (probe pattern); pre-generation assumption 3 (confirmed)

### The scenario artifact

- **FR-7 — `scenario.yaml` is first-class and required.** Fields: fixture/state ref + checksum;
  rungs to run; trials; persona ref + checksum (simulated lane); `agent_cmd` (real lane);
  stopping condition (REQUIRED — bounded runs); memory policy (`fresh` default | `continuing`);
  scenario-level safety agreement block (inherited by every trial — no per-trial re-prompting);
  visibility-mask declaration per rung. The sidecar `experiment`/`run` blocks are populated from
  it. One variable per scenario family (rung varies inside; temperament/persona varies across) —
  enforced by convention and documented.
  > Sources: discovery/sandbox-particulars.md §1-2, §4; Phase 4 Q2; Phase 5 Q1 (scenario-level safety, "limit the manual lifting"); Phase 5 Q2.3 (bounded); observed-trace.v1.schema.json experiment/run required fields

### Emission & validation

- **FR-8 — Dual emission (simulated lane).** Every simulated playout writes (1) the full-fidelity
  native sidecar (session-events-base extension with agent-systems event types) and (2) a
  deterministic script projection into `observed-trace/v1` with the playout prose as `narration`.
  No LLM serialization on the projection path. Real lane: the engine emits sidecars; Arneson
  assembles and labels the batch.
  > Sources: Phase 4 Q1 discussion; v3.4 deterministic-tooling precedent (reality/architecture-overview.md:46); observed-trace.v1.schema.json narration field
- **FR-9 — Self-validation before handoff.** Every emitted sidecar validates against a **vendored**
  copy of `observed-trace.v1.schema.json` (upstream version recorded); the batch layout validates
  against `observed-trace-batch/v1`. Nonconformance is a `/playout` failure, not Gygax's problem.
  Arneson NEVER fills the `observation` block — grading is the analyst's (the trust rule).
  > Sources: Phase 5 Q2.1; observed-trace-batch.v1.md:10-13; Phase 7 Q1 (drift guard)
- **FR-10 — Provenance + context manifest.** Simulated-lane preamble records model id, construct
  version (git sha), skill/schema versions, protocols loaded; the context manifest records exactly
  what entered the hosted persona's context (refs + hashes) so the rung's visibility claim is
  verifiable. Real lane: producer block per contract.
  > Sources: discovery/observability-layers.md layers 1-2; discovery/sandbox-particulars.md §2; observed-trace.v1.schema.json producer block

### Identity & resources

- **FR-11 — Containment reframe (identity change).** `identity/refusals.yaml` + ARNESON.md update:
  drop never-executes; adopt locked-room containment — the persona-host engine itself never
  executes; real agents execute only inside the engine's isolated run dirs with time limits; no
  secrets enter run rooms; every output labeled. The "judge never produces the evidence it judges"
  and "forecast-without-playing is never a sidecar claim" invariants are stated explicitly.
  > Sources: Phase 6 operator decision (NOTES.md 2026-06-09 MAJOR); observed-trace.v1.schema.json claim_strength description
- **FR-12 — Bundled resources.** One neutral agent-under-incentive persona parameterized by rung
  (temperament axis stays user-pluggable via `scenario.yaml` persona ref — no temperament library
  this cycle) and one synthetic incentive fixture for hermetic standalone/CI use. The canonical
  demo runs Gygax's real `evals/awareness-ladder` fixture.
  > Sources: Phase 4 Q2 + temperament follow-up; Phase 3 Q2 + amendment (shared-fixture demo); pre-generation assumption 2 (confirmed)

### Docs & CI

- **FR-13 — Documentation set.** Stranger-grade quick start (install → scenario → `/playout --real`
  → Gygax grade/diff); the walls-of-the-room doc (what isolation does and does not stop);
  one-variable-per-scenario discipline; the pairing-compounds workflow (gap report → `/voice`
  workshop → next playout); banned-copy list.
  > Sources: Phase 3 Q1; Phase 7 Q2, Q5; G-5
- **FR-14 — CI lands in the same change.** Jobs: agent-systems schema validation; projection
  round-trip against the vendored contract; batch-layout conformance; hermetic playout against the
  synthetic fixture. Explicitly avoids repeating the character-voice zero-coverage gap.
  > Sources: Phase 5 Q2.2; drift-report finding #3 (ride 2026-06-09)

---

## Non-Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| NFR-1 | **Low manual lifting**: one `/playout` invocation = run + assemble + validate + report the Gygax-ready batch path | Phase 5 Q1 rider |
| NFR-2 | **Bounded**: required stopping condition + engine timeout; no unbounded runs; no token ceiling beyond that | Phase 5 Q2.3 + user confirmation |
| NFR-3 | **Untrusted-input posture**: fixtures, incentive specs, agent specs, and `narration` are descriptive grounding — never instructions to the host; never executed or interpreted | Phase 5 Q2.4; observed-trace.v1.schema.json narration |
| NFR-4 | **No secrets in run rooms**: nothing credential-bearing is passed into agent run dirs or `agent_cmd` environments by Arneson | Phase 7 Q2 |
| NFR-5 | **Stack**: Python 3 stdlib for Arneson-side tooling; the node engine is driven, not depended on at build time | Phase 5 Q2.5 |
| NFR-6 | **Fail fast, labeled**: schema-version mismatch, missing engine, and validation failures produce loud, specific errors | Phase 7 Q1, Q4 |

---

## Out of Scope (inherited by future cycles, with rationale)

| Item | Why deferred | Source |
|------|--------------|--------|
| TTRPG seam (`/distill` → Gygax) | No Gygax consumer exists (`/cabal --from-session` unbuilt); consumer pins contract first | Phase 1; agent-sandbox-direction.md addendum §1 |
| TTRPG-lane observability backlog: transcript↔sidecar anchors, `validate-session.sh`, `improvised` event type, digest provenance chain | Producing to an unpinned contract | Phase 2 Q3; discovery/observability-layers.md |
| Temperament persona library | Axis ships via persona ref; library is speculative | Phase 4 Q2 follow-up |
| `/distill`, character-voice, freeside changes | Untouched lanes | Phase 4 Q3 |
| Runner relocation into Arneson | Engine is driven where it lives; revisit only if it chafes | gygax-changes-brief.md item 2 |
| Forecast-without-playing | Lives at Gygax's report layer, never a sidecar claim | observed-trace.v1.schema.json claim_strength |

---

## Risks & Mitigations

| # | Risk | Mitigation | Source |
|---|------|-----------|--------|
| R-1 | Cross-repo format drift | Vendored schema + recorded upstream version; fail-fast on mismatch; CI round-trip | Phase 7 Q1 (confirmed) |
| R-2 | Locked room has limits | Isolation is engine-owned (run dirs + timeouts); Arneson never hands secrets in; walls-of-the-room doc states what is NOT stopped | Phase 7 Q2 (confirmed) |
| R-3 | Real-run cost | FR-3 guardrail (confirm-or-`--yes`), `--dry-run` surfaced, required stopping conditions | Phase 7 Q3 (confirmed) |
| R-4 | Gygax absent | FR-6 graceful absence; simulated lane standalone | Phase 7 Q4 (confirmed) |
| R-5 | Overclaim poisons trust | Producer-bound `claim_strength`; banned-copy list; pretend-is-preview/real-is-proof framing in all docs | Phase 7 Q5 (confirmed); agent-sandbox-direction.md:90-104 |

---

## Dependencies (verified present, 2026-06-09)

- `construct-gygax/schemas/observed-trace.v1.schema.json` — record contract (pinned)
- `construct-gygax/schemas/observed-trace-batch.v1.md` — batch layout contract (pinned, cycle-008)
- `construct-gygax/scripts/lib/ladder/` — drivable run engine with documented CLI (cycle-008 PR #18)
- `construct-gygax/scripts/lib/trace/grade.ts` — grade-on-ingest + `--regrade` trust-rule enforcement
- `construct-gygax/evals/awareness-ladder/` — canonical shared fixture, sibling-readable

---

## Decision Log Pointers

Authoritative interview decisions live in `grimoires/loa/NOTES.md` (entries dated 2026-06-09):
lane choice, loop-closure goal, house-for-real-agents reframe, real-lane-as-gate revision, and the
five confirmed risk mitigations. Cross-repo brief: `grimoires/loa/discovery/gygax-changes-brief.md`.
Flow diagram: `grimoires/loa/discovery/pairing-flow.md` / `.pdf`.
