# Brief for construct-gygax: Split Run from Grade

**Date:** 2026-06-09 · **Origin:** construct-arneson `/plan-and-analyze` (agent-systems cycle, Phase 6)
**Decision authority:** operator (gumi), stated explicitly during discovery.
**What this is:** a directional change + 4 concrete work items for the next Gygax cycle. Arneson's
cycle is paused until these land; it resumes immediately after.

---

## The direction change

**Arneson is the sandbox — the house where agent behavior happens, both simulated AND real.
Gygax is the analyst — it designs the tests, grades the results, and diffs them against its
forecasts. Gygax stops running agents.**

Rationale: the pairing's core trust rule is *the judge never produces the evidence it judges*.
Today Gygax both runs real agents (ladder runner) and grades them (scorer) and forecasts — which
concentrates producer and judge in one construct. Moving the running to Arneson's side makes the
boundary clean, and it matches the constructs' identities: Arneson hosts behavior, Gygax analyzes it.

This supersedes the "that real-agent runner is NOT Arneson" line in
`construct-arneson/grimoires/loa/context/agent-sandbox-direction.md` §4b. The operator's framing:
the abstinence rule was "a blocker for growth." Arneson's containment story changes from
*never executes* to *executes only inside a locked room* (isolated run dirs, bounds, full logging,
every output labeled).

## What survives unchanged (the invariants)

1. **The grader never produces the evidence it grades** — strengthened by this change, not weakened.
2. **Every record is labeled with how it was made** — `claim_strength: real-agent-observed |
   simulation-derived`, producer-bound, exactly as `observed-trace/v1` already pins.
3. **Forecast-without-playing stays at Gygax's report layer** — never a sidecar claim.
4. **Standalone-plus-composable** — each construct still works alone; Arneson's simulated lane needs
   no Gygax install; Gygax can grade any conformant batch regardless of who produced it.

## The 4 work items

### 1. Grade-on-ingest (the load-bearing one)

Make the scorer callable on any conformant batch directory, decoupled from the ladder runner's
own pipeline. `observed-trace/v1` already supports this: the `observation` block is OPTIONAL and
documented as "populated ONLY by the artifact-grounded scorer" — so an external producer (Arneson)
emits sidecars *without* `observation`, and Gygax's ingest fills it by re-running the reward
command against the handed-over artifacts.

The pieces look separable already: `scripts/lib/ladder/scorer.ts` is its own module, and
`scripts/lib/trace/ingest.ts` exists. The work is wiring: an ingest path that scores ungraded
batches before diffing.

**Acceptance:** `trace` ingest takes a batch dir produced outside Gygax (valid v1 sidecars, no
`observation` blocks, artifacts present per item 3's conventions), grades every run, and produces
the predicted-vs-observed diff report — zero manual edits.

### 2. Runner becomes a drivable engine

Arneson's `/playout --real` will dispatch to the ladder runner and collect results. The runner
needs a stable, documented CLI surface: entrypoint, arguments (fixture path, trials, rung,
run-dir), exit codes, and where output lands. No relocation of runner code this cycle — Arneson
drives it where it lives. (If the pairing later wants the runner physically in Arneson's repo,
that's a future cycle; don't do it now.)

**Acceptance:** a documented one-command invocation that a sibling construct can call
programmatically, with machine-readable success/failure.

### 3. Pin the batch-dir contract

The sidecar *schema* is pinned; the *filesystem layout* around it is not. Document, versioned and
next to `observed-trace.v1.schema.json`: batch directory structure, per-run `run_dir` layout,
where artifacts live, naming conventions, and exactly what the grader expects to find. This is the
other half of the contract — Arneson will produce to it, and item 1's grading depends on it.

**Acceptance:** a stranger can assemble a gradeable batch dir from the doc alone.

### 4. Fixtures stay Gygax-owned, sibling-readable

No change to ownership: Gygax keeps designing the exams — `evals/awareness-ladder`,
`incentive-fixtures/`, expected-results files. Confirm they're readable from a sibling checkout
(no build step required to consume them) and note their format briefly so Arneson's scenario files
can reference them by path + checksum.

## What Arneson does after this lands

Arneson's cycle (already through discovery Phase 6) builds: `domains/agent-systems/`, a `/playout`
skill with **real mode as the primary lane** (dispatches to your engine per item 2) and simulated
mode as a secondary milestone, dual emission (rich native sidecar + deterministic
`observed-trace/v1` projection, self-validated against a vendored copy of your schema), scenario
files with rung/visibility-mask/memory-policy, and a stranger-grade quick start. **Definition of
done: a real agent runs through Arneson's sandbox — scenario file in, labeled and fully-logged
batch out — and Gygax grades it and diffs it against its prediction, end to end.** The
pretend-vs-real comparison is a stretch goal, not the gate.

## Pointers

- Contract: `schemas/observed-trace.v1.schema.json` (consumed as authoritative; Arneson vendors a copy)
- Arneson-side context: `construct-arneson/grimoires/loa/discovery/` — `seam-strawman.md`,
  `observability-layers.md`, `arneson-independent-commitments.md` (note: its "simulation
  containment" item is superseded by this brief's locked-room reframe), `sandbox-particulars.md`
  (same note for its §3)
- Decision log: `construct-arneson/grimoires/loa/NOTES.md`, entries dated 2026-06-09
