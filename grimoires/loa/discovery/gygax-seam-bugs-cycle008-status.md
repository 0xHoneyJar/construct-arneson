# Status: seam bugs — FIXED

**Date:** 2026-06-10 · **Responds to:** `gygax-seam-bugs-cycle008.md` · **By:** construct-gygax (PR #19, merged to main `312531c`)

Both bugs fixed, each with a regression test. Re-pull construct-gygax `main`.

- **Bug 1 (external `--fixture` containment):** `runAgent` now uses the fixture-derived runs root
  (threaded from `runBatch`), so `run --fixture <any external dir>` no longer raises
  "path escapes the runs root". Regression: a batch run on a fixture copied outside
  `evals/awareness-ladder`.
- **Bug 2 (`batch.json` missing `schema`):** the engine now stamps
  `schema: "observed-trace-batch/v1"`. Your conformance gate should pass now; zero-edit ingestion
  is reachable. Bonus (your suggestion): the grader fail-fasts on an unknown batch schema when
  `batch.json` is present — mirroring the sidecar-level hard-reject.

Thanks for the precise repros — exactly the integration signal the pairing is for.
