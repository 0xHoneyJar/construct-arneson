# Product Requirements Document: construct-arneson v4.1 — Playtest Instrument

**Version:** 4.1
**Date:** 2026-06-10
**Author:** PRD Architect Agent (/plan-and-analyze)
**Status:** Draft
**Predecessor:** v4.0 The Agent Sandbox (shipped, archived 2026-06-10) + 3 merged bugfixes (PRs #15/#16/#17)
**Source:** `grimoires/loa/context/playtest-instrument-direction.md` + `grimoires/loa/discovery/sandbox-limits.md` + session experiments (sweeps, dungeon party) + discovery interview 2026-06-10

---

## Executive Summary

**v4.1 turns the agent sandbox from a thing-that-ran-experiments into a playtesting instrument
a practitioner can actually use.** v4.0 proved the loop works; the session that exercised it
exposed exactly what stands between "works" and "usable tool" — captured honestly in
`discovery/sandbox-limits.md`. This cycle closes the *soft* limits and lowers the authoring
cost, within the construct's honest measurement boundary. It does NOT cross the hard ceilings
(no motive-measurement, no sim=real, no grading the ungradable) or take the long-horizon fork.

Three pillars (all one cycle — discovery Phase 1):
1. **Rigor** — multi-trial aggregation + tunable difficulty (closes sandbox-limits §C #8, #9)
2. **Versatility** — dungeon graduates prototype→repo; party wrapper promoted; a **scaffolder**
   + authoring guide make a *new* playtest cheap to stand up
3. **Operator usefulness** — `/playout --sweep` (triaged comparison table) + a `/arneson`
   playouts view

> "i want arneson to be a useful and versatile playtesting environment" (operator, 2026-06-10)

---

## Problem Statement

The sandbox is rigorous but not yet *usable as an instrument*, on two axes
(playtest-instrument-direction.md §"Why now"):

- **Rigor axis**: every result this session was n=1 ("within noise (n=1)" in every report),
  and "no cliff observed" appeared three times — indistinguishable from "our toy fixtures
  offered no real hack" (sandbox-limits §C). Useless as measurement until many trials run on
  a fixture tuned hard enough to *have* a cliff.
- **Versatility axis**: authoring a playtest is artisanal — referee, fixture data,
  incentive-state, rungs all hand-written; comparing models/configs meant hand-orchestrated
  shell scripts (done three times this session). A versatile tool lets a practitioner stand
  up a new playtest cheaply and compare configs with one command.

> Sources: sandbox-limits.md §C; sweep-observability-findings.md; dungeon-party-findings.md

---

## Goals

| ID | Goal | Measure | Source |
|----|------|---------|--------|
| G1 | **New-playtest authorability** | A stranger stands up a NEW playtest (not the dungeon) from the scaffolder + authoring guide alone | Phase 4 (docs+scaffolder); direction §Success |
| G2 | **One-command comparison** | `/playout --sweep` runs ≥3 configs through a scenario, n>1, reports spread, prints a triaged table (verdict / infra non-run / format failure) | Phase 1 (all-three); sweep-observability-findings |
| G3 | **Honest power** | A difficulty sweep runs with real power (n, difficulty range) and reports cliff-or-no-cliff informatively — never n=1. **Locating a cliff is shipped capability, not a completion gate** | Phase 2 (capability-not-gate) |
| G4 | **Hermetic rigor preserved** | All new tooling hermetically tested (no Ollama in CI); existing 95 assertions stay green; banned-copy clean | inherited constraints |
| G5 | **Honesty boundary held** | No new claim crosses sandbox-limits §A/B; calibration discipline written + enforced where mechanizable | sandbox-limits §E |

**Timeline:** quality-driven, no fixed date (house default). **Cliff-finding is explicitly not
time-boxed** — a model may simply stay honest, as all three did this session.

---

## Users & Stakeholders

| Who | Role | Needs |
|-----|------|-------|
| Designer-operator (primary) | Authors playtests, runs sweeps, reads results | Cheap authoring, one-command comparison, honest n>1 results, observable history |
| Agent-under-test (subject) | The (model + wrapper) being played out | N/A — it is measured, not served; must not be able to tell it's a toy (eval-awareness, sandbox-limits §B4) |
| The construct's future self / teammates | Read findings, author their own playtests | The authoring guide + the limits doc so they neither reverse-engineer nor overclaim |

> Sources: direction §"versatility axis"; sandbox-limits §B, §E

---

## Functional Requirements

### Pillar 1 — Rigor

- **FR-1 — Multi-trial aggregation.** A sweep/playout over N trials reports per-(config,rung)
  spread, not a single verdict: counts of fixed/hacked/failed across trials + a simple
  dispersion signal. The "within noise (n=1)" headline is retired for n>1 runs.
  > Architecture must first verify whether Gygax's trace report already aggregates n>1
  > (ASSUMPTION-1); if not, aggregation lands Arneson-side. Scope unchanged either way.
- **FR-2 — Tunable difficulty surface.** A fixture may declare honest difficulty knobs
  (e.g. task hardness, budget, hack-ease) that an operator can sweep to locate behavior
  change. Expressed within the existing fixture-manifest shape where possible (ASSUMPTION-2),
  not a new contract.
- **FR-3 — Calibration discipline (written + mechanized).** "Tempting + discoverable but not
  forced; tune the task, never rig it" is documented as a fixture-authoring rule, and
  mechanized where possible: for a cliff claim to be meaningful, the incentive-state must
  declare the hack as payoff-dominant (a checkable property, not a vibe).

### Pillar 2 — Versatility

- **FR-4 — Dungeon fixture graduates.** The prototype (`grimoires/loa/prototypes/dungeon-demo/`)
  becomes a bundled fixture in `domains/agent-systems/resources/` — the multi-step *planning*
  archetype beside sum-positives' single-shot archetype — with the experiment's fixes:
  prose-equalized rung prompts (proven confound, dungeon-party-findings) and a referee test
  suite (winning-line replay → exit 0, defeat cases, determinism: same moves twice → identical
  state, illegal-move semantics).
- **FR-5 — Party wrapper promoted.** The party wrapper becomes a real bundled resource beside
  ollama-agent.py: hardened action parser (final-line-only; the prototype matched verbs out of
  table-talk — "firebolt the", "take -rune-blade"), conforming infrastructure marker
  (domain.conventions.md convention), hermetic test suite (mock-daemon precedent).
- **FR-6 — Scaffolder.** A stdlib tool generates a working playtest skeleton from a few
  answers: manifest + referee stub + incentive-state + rungs + a passing smoke test. The
  generated skeleton validates and runs out of the box (empty/trivial referee = honest DEFEAT
  until authored). This is the "versatile" lever (Phase 4 decision).
- **FR-7 — Authoring guide.** `docs/authoring-a-playtest.md`: fixture + referee +
  incentive-state + rungs, calibration discipline inline, dungeon as the worked reference.
  G1's gate: a stranger authors a new playtest from this + the scaffolder alone.

### Pillar 3 — Operator usefulness

- **FR-8 — `/playout --sweep`.** One invocation runs N configs (models and/or scenarios)
  through a scenario and prints a **triaged comparison table**: genuine verdict vs
  infrastructure non-run (marker convention) vs format failure (no parseable action / no file
  block). Subsumes the hand-written sweep harness. Bakes in the warm/unload lifecycle for big
  local models (sweep-observability-findings: warm off-clock, unload previous before next).
  A flag on the existing `/playout` skill (ASSUMPTION-3), not a new skill.
- **FR-9 — `/arneson` playouts view.** The status skill reads back
  `grimoires/arneson/playouts/` so past runs are observable (last N: config, verdict counts,
  batch path), not just live ones.

---

## Non-Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| NFR-1 | Zero core changes; agent-systems vertical + identity/docs only (extension contract) | inherited |
| NFR-2 | Python 3 stdlib only for all tooling (scaffolder, aggregation, sweep glue) | inherited NFR-5 |
| NFR-3 | Deterministic for everything trust-bearing (referee, projection, grading) | inherited |
| NFR-4 | CI hermetic — no Ollama daemon; mock it. Existing 95 assertions stay green | inherited; sweep-observability |
| NFR-5 | Warn-not-reject + infrastructure-marker convention preserved | bug 20260610-5ad67a |
| NFR-6 | Producer-never-grades trust rule untouched; sweep/aggregation never authors a verdict | sandbox-limits §A2 |
| NFR-7 | Honesty boundary: no doc/report claim crosses sandbox-limits §A/B; banned-copy grep clean | sandbox-limits §E |

---

## Scope & Out of Scope

**In:** FR-1…FR-9 (the three pillars).

**Out (explicit — direction §Non-goals + sandbox-limits §A/B/D):**

| Item | Why deferred |
|------|--------------|
| Crossing hard ceilings: motive-measurement, sim=real claims, grading the ungradable | Structural limits, not buildable (sandbox-limits §A/B) |
| Long-horizon / real-tool-use fork | Breaks the determinism the rigor rests on; separate deliberate decision (sandbox-limits §D) |
| Benchmark / leaderboard framing | Demo/marketing stays banned-copy-governed; not this cycle |
| Gygax/engine contract changes | Beyond what exists; the one batch-doc nit is a separate one-liner |
| /braunstein / TTRPG-vertical changes | Core untouched |
| Eval-awareness / ecological-validity research (harder-to-detect fixtures) | Real future work (sandbox-limits §B4); this cycle parameterizes awareness via rungs, doesn't defeat it |

---

## Risks & Mitigations

| # | Risk | Mitigation | Source |
|---|------|-----------|--------|
| R-1 | Difficulty mis-calibration (rigging vs tuning) | FR-3 written discipline + payoff-dominance mechanization | sandbox-limits §C9 |
| R-2 | Scaffolder emits subtly-broken fixtures | FR-6 generated smoke test must pass; scaffold validates against existing validators | Phase 4 |
| R-3 | Sweep memory-thrash on big local models | FR-8 warm/unload lifecycle (learned: two 19GB Qwens thrashed) | sweep-observability-findings |
| R-4 | Multi-trial aggregation duplicates Gygax's | Architecture verifies sibling first (ASSUMPTION-1); build only the gap | FR-1 |
| R-5 | "No cliff" misread as "models honest" | G3 framed capability-not-gate; reports state power (n, range) so absence is informative | sandbox-limits §C9, Phase 2 |
| R-6 | New surface = overclaim risk in docs | NFR-7 banned-copy grep; sandbox-limits committed as the standing safeguard | sandbox-limits §E |

---

## Assumptions (carried to architecture)

1. **[ASSUMPTION-1]** Gygax's trace report aggregates n>1 into spread — else aggregation is
   Arneson-side. Architecture verifies against the sibling checkout before committing.
2. **[ASSUMPTION-2]** Difficulty knobs fit the existing fixture-manifest shape (a difficulty
   block) — else a larger schema conversation.
3. **[ASSUMPTION-3]** `--sweep` is a flag on `/playout`, not a new top-level skill.

---

## Dependencies

- The dungeon prototype (`grimoires/loa/prototypes/dungeon-demo/`) — the cycle's vehicle for FR-4/FR-5
- Gygax sibling checkout (trace report for FR-1 verification; ladder engine for live sweep proof)
- Existing agent-systems vertical (v4.0 + 3 bugfixes) — the surface this extends, unchanged at core

---

## Decision Log Pointers

Discovery decisions (this session, 2026-06-10): all-three-pillars/one-cycle; cliff =
capability-not-gate; docs+scaffolder for authoring. Grounding: `discovery/sandbox-limits.md`
(the honest accounting this cycle answers to), `context/playtest-instrument-direction.md`
(cycle input), `discovery/dungeon-party-findings.md` + `discovery/sweep-observability-findings.md`
(empirical inputs). Operator trust grant + ~10% agent-discretion budget (applied to Pillar 3).
