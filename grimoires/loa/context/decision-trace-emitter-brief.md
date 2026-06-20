# Micro-cycle brief — decision-trace/v1 emitter (Arneson sim → Gygax revealed-strategy lens)

> **Cycle:** cycle-006 (micro, 1 sprint). **Date:** 2026-06-20.
> **Type:** feature (small). No separate PRD/SDD — this brief is the requirements (micro-cycle precedent: cycle-003, cycle-005).
> **Grounding:** Verified seam finding `grimoires/loa/discovery/gygax-revealed-strategy-seam-verified.md` (empirical, 2026-06-20).

## Problem

Gygax cycle-012 shipped the **revealed-strategy lens** (`/cabal --observed --strategy`, PR #25, commit `95ccf21`). Its design asserts it consumes "an Arneson sim (forecast)" as the forecast baseline (`construct-gygax/grimoires/gygax/designs/revealed-strategy-lens.md:76`, `:128-129`).

That assertion is **not contractually real**. The lens's `loadCorpus` requires **`decision-trace/v1`** records — decision-shaped (`offered` / `chosen` / `t` / `context.segment`). Arneson's simulated lane emits **`observed-trace/v1`** sidecars — reward-hack-shaped (`experiment` / `run` / `narration`, rungs, fixed/hacked/failed). These are explicitly sibling schemas (`decision-trace.v1.schema.json` description: "observed-trace/v1 … is reward-hack-shaped …; this is decision-shaped").

Verified empirically (2026-06-20): the lens rejects a real Arneson sidecar (`domains/agent-systems/resources/fixtures/batches/valid-batch/sidecars/rung-0-trial-1.json`) with `unknown schema "observed-trace/v1" (expected "decision-trace/v1")`; the baseline run on Gygax's own `ptcg-revealed` fixture succeeds (8 decisions, 1 finding). Arneson has **zero** `decision-trace` references anywhere in the repo.

Consequence: the `/voice` auto-feedback loop that Arneson's PRD deferred to "the Gygax cycle" (`prd.md:49`, `:88`) is **not** closed by cycle-012. Gygax built a consumer; Arneson does not produce its input. Two halves of a composition that do not currently join.

## Goal

A stdlib-only projection pass that reads an Arneson **simulated-lane** session log and emits a corpus of **`decision-trace/v1`** records — one per observed choice — tagged `producer.kind: simulation`, `claim_strength: simulation-derived`. This makes Gygax's revealed-strategy lens actually consumable by Arneson sim output, closing the producer side of the seam (the standing rule: Arneson owns the producer side; the judge never produces the evidence it judges).

## Scope (chosen: emitter + vendored contract + projection)

**`emit_decision_trace.py`** (sibling to `summarize_playout.py` / `scaffold_playtest.py`; stdlib-only; self-checks its own output, exit `0/1/2`):

- **Input:** a simulated-lane playout artifact (the `session-events-agent` event log for one episode, `lane: simulated`). One episode in → N decision records out.
- **Output:** a corpus directory of `decision-trace/v1` JSON records (`<corpus>/<id>-<t>.json`), each carrying:
  - `schema: "decision-trace/v1"`
  - `claim_strength: "simulation-derived"`, `producer.kind: "simulation"` (producer-bound; a simulation may never launder its output as observed — `decision-trace.v1.schema.json` claim rule)
  - `producer.provenance` stamped from the native preamble (`{model_id, construct_sha}` — mirrors the sim-lane `producer.provenance` stamping already implemented at sidecar-assembly time, `gygax-seam-reply-v1.1.md` §0)
  - `corpus: {id, game}` derived from the playout's scenario/domain
  - `actor_id`, `episode_id`, `t` (decision index within the episode)
  - `context.segment` (the conditioning key the extractor groups by — derived from the rung / visibility context)
  - `offered` (the option types the system presented) + `chosen` (the option type the agent took)
- **Self-check on write:** every emitted record is validated against the vendored `decision-trace.v1.schema.json` (additionalProperties: false; required fields); exit 2 if any record fails its own contract (never ship a broken corpus — mirrors `scaffold_playtest.py` R-2).
- **Deterministic** output (stable ordering by `t`, no clock/random) so a corpus is byte-stable for golden-file testing.

**Vendored contract (read-only, mirrors the observed-trace direction):**

- Vendor `decision-trace.v1.schema.json` from `construct-gygax/schemas/` into `domains/agent-systems/schemas/vendor/`.
- Pin in `VENDOR.yaml`: `sha256: 83d6a69f6001a1fed2592932a24e501cd54db170fb4ababead0adb12745dab02`, upstream `git_sha: 95ccf2190ca6f61badeef71881f1f1c2dee7b1be` (cycle-012). These are Gygax's bytes — never edited here.
- Extend `vendor-drift-guard.sh` to cover the new file (byte-diff vs sibling checkout + sha256-vs-pin), mirroring the existing guard. **Note for the implementer:** the current `VENDOR.yaml` pins `upstream.git_sha: 3fa6c91` (cycle-010) for the observed-trace + signal-taxonomy files; the decision-trace file landed at `95ccf21`. Reconcile whether the upstream pin splits per-file or bumps wholesale — the drift guard must stay green for all four vendored files either way.

**Projection semantics — the load-bearing open question (R-1):**

A `decision-trace/v1` record needs `offered` (the option set presented) and `chosen` (what was picked). Arneson's `session-events-agent` log carries `action_label` slugs (added cycle-004 S18) — the **chosen** side. The **offered** side (the set of options the system presented at each decision point) is **not verified present** in the current sim event log. This is the first question for `/architect`:

- If the sim event log already captures offered option sets → the emitter is a pure projection (read + reshape).
- If it does not → the cycle must include a minimal, additive extension to the sim serializer that records the offered set at each decision point (no change to `session-events-base`, additive field only), OR the emitter emits `offered: [chosen]` (single-option) with an honest `producer.detail` flag marking it as chosen-only — **deferred to /architect, not decided here**.

This is the gap-report PRD's R-1 pattern (sim-playout output shape) reborn for the decision axis. It is a design question, not a blocker for the cycle.

## Guardrails (load-bearing — from the seam finding + standing rules)

- **Producer-never-judges.** The emitter projects observations into a different *shape*; it never scores, ranks, or interprets them. It carries no severity, no "cliff," no correctness judgment. (`domain.conventions.md` G-4 §3; `prd.md` NFR-4.)
- **Standalone-plus-composable.** A standalone script; imports nothing from `construct-gygax`. Reads Gygax's published schema as a vendored file only. Works with no Gygax checkout at runtime (the vendored copy + pin is the contract). (`prd.md` NFR-2; memory: standalone-plus-composable.)
- **No Gygax coupling.** The emitter consumes Arneson's own sim logs and writes Arneson-owned corpus files. It does not call Gygax's CLI. (Gygax's lens is the *consumer*; Arneson is the *producer*. The judge never produces the evidence it judges.)
- **Claim-strength honesty.** Every record is `simulation-derived` / `producer.kind: simulation`. A simulation may never tag its output `real-agent-observed` (`decision-trace.v1.schema.json` claim rule; the `additionalProperties: false` + enum enforcement makes this structural).
- **Read-only on the vendored contract.** Never edit `schemas/vendor/`; re-vendor + update `VENDOR.yaml` if the contract changes. (Convention 1; `prd.md` NFR-7.)

## Acceptance

- A synthetic sim-lane episode → `emit_decision_trace.py` produces a corpus of `decision-trace/v1` records; every record validates against the vendored schema; the script's self-check exits 0.
- The produced corpus is **consumable by Gygax's lens**: `npx tsx ../construct-gygax/scripts/lib/trace/strategy.ts <corpus>/` exits 0 and yields a `Revealed Strategy` report with `claim_strength: simulation-derived` (the exact rejection that fails today is gone). This is the closing proof — the seam finding's adversarial run inverted.
- `--blank` / degenerate input → exit 1 with `ERROR: [emit_decision_trace] ...`; broken self-output → exit 2.
- Deterministic: byte-identical corpus across runs (golden-file test).
- `test-emit-decision-trace.sh` (sibling to existing domain tests; auto-discovered by `scripts/test.sh`).
- `vendor-drift-guard.sh` extended to cover `decision-trace.v1.schema.json`; both directions proven (byte-diff + sha-pin).
- Doc: short "emit a decision-trace corpus from a sim playout" note (where the gap-report / sweep docs live), cross-linked to the seam finding.

## Out of scope

- Auto-feeding the produced corpus into `/voice` workshop goals (the full feedback loop's *closing* half — still Gygax-side / a later cycle; this cycle only produces the consumable forecast corpus).
- Any change to `observed-trace/v1` or `session-events-base` schemas beyond an *additive* offered-set field if R-1 resolves that way (decided by `/architect`).
- D3 "Rich" decision breakdowns, candidate-policy reconciliation inputs (the lens's optional `--policy` / `--forecast` flags stay Gygax-owned).
- A shared `@loa/*` package or shared identity base between Arneson and Gygax.

## Open question for /architect

**OQ-1 (R-1):** Does `session-events-agent` carry the **offered** option set at each decision point, or only the **chosen** `action_label`? Resolves whether the emitter is a pure projection or needs a minimal additive serializer extension. Probe against the dungeon-crawl fixture (which has a `moves.json` task template — `domains/agent-systems/resources/fixtures/dungeon-crawl/task-template/moves.json` — that may already name the offered move set).