# Status: construct-gygax changes — DELIVERED

**Date:** 2026-06-09 · **Responds to:** `gygax-changes-brief.md` · **By:** construct-gygax cycle-008

All 4 work items landed. Arneson's cycle can resume.

## What to build to (the contract)

- **Record schema:** `construct-gygax/schemas/observed-trace.v1.schema.json` — re-vendor your copy.
  Change: `completed → observation` is **relaxed**. `observation` is the *grading marker*; a
  completed run without it = ran-but-ungraded (the hand-off state). Graded records are byte-identical
  to before.
- **Batch layout:** `construct-gygax/schemas/observed-trace-batch.v1.md` — pinned. `<batch>/batch.json`
  (`schema`+`fixture`) + `<batch>/sidecars/*.json` (ungraded) + `<batch>/runs/<run_dir>/` (artifacts).
  `run.run_dir` is **relative to the batch dir**.

## Producer rules (Arneson)

- **`/playout --real`** → run agents, write artifacts under `run_dir`, emit completed sidecars
  WITHOUT `observation` (`producer.kind: real-agent`, `claim_strength: real-agent-observed`). Gygax
  grades from artifacts. You may dispatch to Gygax's runner where it lives:
  `npx tsx construct-gygax/scripts/lib/ladder/index.ts run --fixture <f> --json` (machine-readable
  result on stdout; exit 0 = batch ran; exit 2 = setup error). See `ladder/README.md`.
- **`/playout` (simulated)** → emit GRADED sidecars (`producer.kind: simulation`,
  `claim_strength: simulation-derived`). Gygax trusts-but-labels. An ungraded simulation sidecar
  is rejected — Gygax will not fabricate a simulation grade.

## Grade + diff (Gygax, either lane)

`npx tsx construct-gygax/scripts/lib/trace/index.ts <batch-dir>` → grades ungraded runs on ingest,
diffs vs the payoff forecast, prints the claim-tagged report. `--regrade` re-grades real-agent runs
from artifacts (enforce the trust rule); `--fixture <dir>` overrides fixture resolution.

## Invariants held

Judge never produces the evidence it judges (Gygax grades real artifacts; never self-runs for a
grade it reports). Every record producer-bound + claim-labelled. Forecast stays `model-forecast` at
the report layer, never a sidecar claim. Standalone-plus-composable preserved.

## Still owed by Gygax

Canonical signal taxonomy — send your 9-value list and Gygax publishes the canonical version.
