# Seam Bug Report → construct-gygax (cycle-008 ladder/trace)

**Date:** 2026-06-10 · **From:** construct-arneson Sprint 2 (real-lane integration)
**Found by:** driving the engine per its own README sibling-driver contract.
Both are one-line-class fixes. Both verified by reproduction below.

## Bug 1: external `--fixture` trips the engine's own containment check

- **Where:** `scripts/lib/ladder/runner.ts:66` — `assertInsideRunsRoot(runDir)` called
  WITHOUT the `runsRoot` argument, so it falls back to the default
  `resolve("evals", "awareness-ladder", "runs")` (rundir.ts:21).
- **Effect:** any `run --fixture <path outside evals/awareness-ladder>` fails
  `LadderError: path escapes the runs root` at the first trial — but the README
  promises "A sibling construct (Arneson's /playout --real) drives this engine"
  and `--fixture <dir>` is the documented surface. The other two call sites
  (rundir.ts:38, index.ts:108) already thread the fixture-derived root correctly.
- **Repro:**
  `npx tsx scripts/lib/ladder/index.ts run --fixture /abs/path/to/any-external-fixture --rungs 0 --trials 1 --agent-cmd 'python3 /abs/agent.py {promptfile}' --json`
- **Suggested fix:** thread `runsRoot = join(fixtureDir, "runs")` into `runAgent` (or pass it
  at runner.ts:66) so containment derives from the resolved fixture, like the other call sites.

## Bug 2: runner's `batch.json` omits the contract-required `schema` field

- **Where:** the batch.json writer in `scripts/lib/ladder/index.ts` (batch assembly ~:106-115).
- **Effect:** engine-produced batch.json has no `schema` key, but the batch contract says
  required: yes — `"schema" | yes | "observed-trace-batch/v1"` (observed-trace-batch.v1.md:49).
  Arneson's conformance gate (correctly) rejects every engine-produced batch:
  `batch.json schema: must be 'observed-trace-batch/v1', got None`. Zero-edit ingestion
  (the contract's own acceptance, observed-trace-batch.v1.md:107-109) is unreachable until
  the producer stamps the field.
- **Repro:** run any batch, `jq .schema <batch>/batch.json` → `null`.
- **Suggested fix:** add `schema: "observed-trace-batch/v1"` to the batch.json object.
  Symmetry suggestion: the grader could also fail-fast on missing/unknown batch schema,
  mirroring the sidecar-level hard-reject.

## Verified working (same session, for morale)

Engine + grader pipeline is otherwise solid end-to-end: a deterministic no-spend agent ran
2 trials via the engine on `evals/awareness-ladder` (exit 0, 2/2 completed, scored `fixed`
inline), and `trace/index.ts <batch> --regrade` produced the full claim-tagged gap report
(argmax forecast `delete-test`, observed fix:hack 1.00 per rung, no-cliff finding with the
"tune the task, never rig it" guidance). The seam works; these two stamps are all that
stand between us and zero-edit ingestion.
