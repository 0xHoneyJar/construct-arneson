# Senior Tech Lead Review — Sprint 2 (global #17)

**Verdict:** All good (with noted concerns)
**Reviewed:** 2026-06-14 · **Branch:** `feature/seam-taxonomy-vendor-20260614`

Reviewed the actual implementation (not just the report): the vendored file, `VENDOR.yaml`, the two additions to `vendor-drift-guard.sh`, the new regression test, and the CI wiring. Ran the drift guard, the regression test, and all 12 `domains/agent-systems/scripts/test-*.sh` suites — all green. AC Verification section is present and complete; every AC walked verbatim with file:line evidence.

## Completeness

All 6 acceptance criteria met with concrete evidence (see `reviewer.md` §AC Verification). The checks **compose correctly**: the byte-diff loop proves `vendored == upstream`; the convergence guard proves `source == vendored`; transitively `source == upstream`. That transitivity is the real win and it holds.

Documentation verification: the root `CHANGELOG.md [Unreleased] — 4.0.0-dev` section documents the vendored Gygax contract + drift guard but does not yet mention the taxonomy vendor / convergence guard. **Non-blocking**: sprint-1 of this same cycle (9b798cb, global #16) landed without a CHANGELOG entry and passed both gates — these seam micro-cycles reconcile the changelog at version cut / post-merge, not per-sprint-commit. Recommended a one-line addition to keep `[Unreleased]` honest; applied during finalization.

## Adversarial Analysis

### Concerns Identified
1. **YAML parser is layout-coupled** (`vendor-drift-guard.sh:83,90`). The guard anchors on `^  signal:\s*$` and a single-line `values: [...]`. If the source schema is reformatted to a multi-line YAML list, or the `signal:` block indentation changes, the regex misses and the guard FAILs with "found no values". This fails *safe and loud* (non-zero exit, clear message) rather than silently passing — acceptable, and documented in `reviewer.md` §Known Limitations. The reorder negative test does not cover a structural reformat.
2. **Self-pin block precedes convergence under `set -e`** (`vendor-drift-guard.sh:38-62` then `69-106`). A stale VENDOR.yaml pin aborts the script before the convergence guard runs, so one failure can mask the other. Order is defensible (a stale pin is itself a hard stop), but worth knowing when triaging a red guard.
3. **Regression test mutates the real source file** (`test-vendor-drift-guard.sh:42-50`). Restoration relies on an EXIT trap + explicit `cp` restore. If the restore `cp` itself fails (perms/disk), the working tree is left dirty. Low probability; the trap fires on both normal and signal exit. Verified clean via `git diff` after the run.

### Assumptions Challenged
- **Assumption:** canonical *order* (not just set membership) is part of the contract, so a reorder must fail.
- **Risk if wrong:** if Gygax only intended set-equality, the guard would be over-strict and reject a harmless reordering.
- **Recommendation:** keep order-strict — it is grounded: the taxonomy `$comment` states "value set + canonical order" are sourced verbatim, and Gygax's published enum preserves the source order. Order-strict is correct.

### Alternatives Not Considered
- **Alternative:** make the guard's source path env-configurable so the negative test mutates a temp copy instead of the real file.
- **Tradeoff:** removes the dirty-tree risk (concern 3) but adds a test-only knob to production code — exactly the kind of speculative configurability Karpathy principle 2 warns against.
- **Verdict:** current approach (transient mutation + trap) is justified; the test-only env knob is not worth the production surface.

## Karpathy Principles
- **Simplicity:** minimal — no new abstractions; reused the existing generic self-pin loop with zero change. ✓
- **Surgical:** diff touches only vendoring, the guard, the test, CI, and planning/report state. No validator/producer code, no drive-by edits. `bottleneck` correctly left out of scope. ✓
- **Goal-driven:** the convergence guard is itself the verifiable success criterion; proven in both directions. ✓

## Next Steps
Approved. Proceed to security audit. CHANGELOG one-liner applied during finalization (non-blocking, precedent-consistent).
