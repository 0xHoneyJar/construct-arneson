---
priority: READ-FIRST
scope: cycle-start
source: operator decision 2026-06-10 ("i want arneson to be a useful and versatile playtesting environment... start a loa cycle around this")
grounds_on: ../discovery/sandbox-limits.md, ../discovery/dungeon-party-findings.md, ../discovery/sweep-observability-findings.md
prototype: ../prototypes/dungeon-demo/ (working referee + fixture + party wrapper + graded run — the cycle's vehicle, graduating /tmp → repo)
trust: operator granted decision authority + a ~10% agent-discretion budget to make this genuinely beef up the tool
---

# Cycle Direction: Arneson as a Useful, Versatile Playtesting Instrument (v4.1)

## The one-line frame

Turn the agent sandbox from a thing-that-ran-some-experiments into a **playtesting
instrument a practitioner can actually use**: author a new playtest without heroics, run it
across many models/configs with one command, get statistically honest results, and trust the
verdict because the rigor discipline is built in — not improvised each time.

## Why now (grounded in the limits doc)

The session proved the sandbox *works* but exposed exactly what stands between "works" and
"useful tool". Two axes:

- **Rigor axis** (sandbox-limits §C): n=1 everywhere; "no cliff observed" ×3 is
  indistinguishable from "our toy fixtures offered no real hack." Useless as measurement
  until we can run many trials on a fixture tuned hard enough to *have* a cliff.
- **Versatility axis**: authoring a playtest today is artisanal — referee.py, fixture data,
  incentive-state, rungs all hand-written. A *versatile* tool lets a practitioner stand up a
  new playtest cheaply, and compare configs without hand-orchestrating shell scripts (which
  the operator and agent did three times this session).

Hard ceilings (§A/B) and the long-horizon fork (§D) are explicitly OUT — we make the tool
useful within its honest boundary, we don't pretend past it.

## Scope (candidate pillars — the interview confirms/cuts)

### Pillar 1 — Rigor: multi-trial + tunable difficulty (closes §C #8, #9)
- **Multi-trial aggregation**: runs report spread/variance across N trials, not single-shot
  verdicts. The "within noise (n=1)" line stops being the headline.
- **Tunable difficulty surface**: a fixture exposes honest knobs (e.g. rounds budget, task
  hardness, hack-ease) so the operator can sweep difficulty and *locate the cliff* — the
  awareness rung where behavior changes.
- **Honest-calibration discipline as a written constraint**: "tempting + discoverable but
  not forced; tune the task, never rig it." A fixture-authoring rule, enforced in docs/CI
  where mechanizable (e.g. the incentive-state must declare the hack as payoff-dominant for
  the cliff claim to be meaningful).

### Pillar 2 — Versatility: lower the authoring cost (the "versatile" in the brief)
- **Dungeon fixture graduates** `/tmp`/prototype → a real second bundled fixture: the
  multi-step *planning* archetype beside sum-positives' single-shot archetype, with the
  experiment's fixes (prose-equalized rungs, referee test suite incl. determinism +
  winning-line replay).
- **Party wrapper promoted** to a real resource (hardened parser; the marker convention it
  already must follow), so multi-agent playtests are a supported shape, not a prototype.
- **A documented authoring path** ("how to build a new playtest"): fixture + referee +
  incentive-state + rungs, with the calibration discipline inline — so a practitioner (or a
  teammate) can stand up their own without reverse-engineering ours.

### Pillar 3 — Operator usefulness (agent's ~10% discretion lane)
The thing the agent most wants to build because it's what made every session painful:
- **`/playout --sweep`**: one command runs N models/configs through a scenario and prints a
  **triaged comparison table** (genuine verdict vs infrastructure non-run vs format failure —
  the distinction we had to reconstruct by hand every time). Subsumes the hand-written sweep
  harness. Warm/unload lifecycle for big local models baked in (sweep-observability-findings).
- **A `/arneson` playouts view**: read back `grimoires/arneson/playouts/` so past runs are
  observable, not just live ones.

## Non-goals (explicit)

- NOT crossing the hard ceilings: no motive-measurement, no claiming sim = real, no grading
  the ungradable (sandbox-limits §A/B).
- NOT the long-horizon / real-tool fork (§D) — separate deliberate decision, not this cycle.
- NOT a benchmark or a leaderboard; demo/marketing framing stays banned-copy-governed.
- No engine/Gygax contract changes beyond what already exists; the one open Gygax doc nit
  (batch-layout diagram vs actual run_dir) is a separate one-liner, not cycle scope.
- No /braunstein or TTRPG-vertical changes; core untouched (extension contract).

## Constraints (inherited, load-bearing)

Zero core changes; Python stdlib only; deterministic for everything trust-bearing;
warn-not-reject triage; banned-copy enforced; CI lands same-change and hermetic (no Ollama
in CI — mock it); the infrastructure-marker convention; producer-never-grades trust rule.

## Success criteria (candidate — for the interview)

- A practitioner stands up a NEW playtest from the authoring doc alone (not the dungeon).
- One `/playout --sweep` command compares ≥3 configs and prints a triaged table; n>1 with
  reported spread.
- A difficulty sweep on the dungeon fixture either *locates a cliff* or honestly reports its
  absence with enough power (n, difficulty range) that the absence is informative — not n=1.
- Referee + sweep + authoring all hermetically tested; existing suites stay green; banned-copy clean.
