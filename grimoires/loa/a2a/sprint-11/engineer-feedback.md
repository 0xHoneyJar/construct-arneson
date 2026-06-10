# Senior Lead Review — Sprint 4 (global sprint-11): APPROVED

**Date:** 2026-06-10 · **Reviewer:** /review-sprint (run mode, cycle 1)

All good (with noted concerns)

## Verification performed

- All 8 ACs walked against artifacts: the hermetic pipeline re-ran green (66/66 across 5
  suites); the projected record's labels and absent-observation asserted in-suite; OQ-1's
  live evidence checked (scored sidecar carries observation:fixed with producer simulation
  intact, batch re-validated, ingested). The E2E table's claims spot-checked: playout records
  on disk, label coverage 3/3, banned-grep 0, pairing doc commands literal.
- **Carried items discharged:** fixture placeholder hashes → computed (verified by the
  pipeline's own hash checks passing on the fixture); real-timestamp concern → projection
  derives duration from event timestamps; record timestamps mandated "real clock" in S6.
- The containment hardening (run-dir, not batch-root) was FOUND BY the new test — exactly
  what the test-first gate is for. The fix closes a real hole (artifact overwriting a
  sibling trial or sidecars/).
- CHANGELOG shipped with the implementation (pattern held).

## Adversarial Analysis

### Concerns Identified (non-blocking)
1. **`_iso_ms_delta` assumes `Z`/offset timestamps** (project_trace.py): a naive timestamp
   raises an uncaught ValueError (traceback, exit 1). Input-error class either way, but a
   caught, named message would match the error-catalog discipline. Post-cycle polish.
2. **The no-trial_end tamper uses `grep -v`** (test-sim-pipeline.sh) — line-pattern surgery
   on the fixture is brittle if the fixture gains lines containing "trial_end" in prose.
   Works today; prefer a python mutation if the fixture grows.
3. **The simulated host loop (S2-S3) has no live exercise yet** — same class as Sprint 2's
   skill-prose concern, honestly declared in Known Limitations. The deterministic pipeline
   downstream is fully tested; first live hosted playout is post-cycle work and its transcript
   should be checked against S1-S6 like Sprint 3's was against the real lane.

### Assumption Challenged
- **Assumption:** Gygax's `ladder score` semantics stay stable for simulation batches (OQ-1
  verified against today's checkout).
- **Risk if wrong:** simulated batches silently stop being scorable.
- **Mitigation in place:** the with-gygax CI leg is the tripwire; standalone labeling is the
  honest fallback either way. Acceptable.

### Alternative Not Considered
- **Alternative:** PyYAML for the native sidecar (it's Arneson-authored, not adversarial).
- **Tradeoff:** full YAML support vs the stdlib-only rule (NFR-5) and one parser for all
  domain shapes. The shared restricted_yaml module is the right call — one dialect,
  documented limits, three consumers.
- **Verdict:** justified; revisit only if committed shapes outgrow the dialect.

Sprint 4 (global sprint-11) approved. Milestone (d) complete; all 5 PRD goals validated.
Documentation verification: PASS (CHANGELOG current; quickstart + import doc cover the new
user-facing surface).
