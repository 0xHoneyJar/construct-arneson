# Implementation Report — Sprint 2 (global #17): Signal Taxonomy Vendor + Source↔Vendor Convergence Guard

**Cycle:** cycle-003 (`seam-alignment-v1.1-adoption`) · **Local:** sprint-2 · **Global:** #17
**Date:** 2026-06-14 · **Branch:** `feature/seam-taxonomy-vendor-20260614`
**Source:** Gygax cycle-010 published `signal-taxonomy.v1.schema.json` @ `3fa6c91` — the reciprocal closeout of sprint-1's seam reply.

## Executive Summary

Sprint-1 sent Gygax the canonical 9-value `signal.classification` taxonomy; Gygax published it verbatim as `schemas/signal-taxonomy.v1.schema.json` (gygax `3fa6c91`) and stated "Arneson vendors a pinned copy." This sprint vendors that pin and — critically — adds the **source↔vendor convergence guard** that makes vendoring-a-list-we-authored load-bearing rather than decorative: a CI invariant that fails loudly if our source enum (`session-events-base.schema.yaml`) and the published taxonomy ever drift in value set or canonical order.

No validator or producer code was touched. The change is purely additive: one vendored file, one VENDOR.yaml entry, three lines + one Python block in the drift guard, one new test, one CI step.

## AC Verification

Each acceptance criterion from `grimoires/loa/sprint.md` (Sprint 2 section), quoted verbatim:

1. > "`shasum -a 256 domains/agent-systems/schemas/vendor/signal-taxonomy.v1.schema.json` == `f6ba7182d8d41e53595a142316451377456a1899217a085fdbc9c4a22e542ce6` == upstream gygax bytes; matches the new `VENDOR.yaml` pin"
   - **✓ Met.** Vendored file sha256 = `f6ba7182…` (verified against upstream `/Users/mandy/construct-gygax/schemas/signal-taxonomy.v1.schema.json`). Pin at `domains/agent-systems/schemas/vendor/VENDOR.yaml:26-28`.

2. > "`ARNESON_GYGAX_ROOT=../construct-gygax ./scripts/ci/vendor-drift-guard.sh` exits 0 and reports the taxonomy as byte-identical (3 files checked, not 2)"
   - **✓ Met.** Guard exits 0; output: "OK: signal-taxonomy.v1.schema.json byte-identical to upstream". Loop at `scripts/ci/vendor-drift-guard.sh:20` now lists all three files.

3. > "The convergence guard exits 0 today (source and vendored enums agree: `safety, insight, concern, friction, praise, confusion, delight, surprise, boredom`, same order)"
   - **✓ Met.** Guard prints "OK: source signal.classification enum == vendored signal-taxonomy (9 values, canonical order)". Logic at `scripts/ci/vendor-drift-guard.sh:68-105`.

4. > "The convergence guard exits non-zero (proven via a temporary mutation in-test, reverted) if the source enum is reordered or a value added/removed without re-vendoring"
   - **✓ Met.** `scripts/ci/test-vendor-drift-guard.sh` reorders the source enum, asserts non-zero exit ("guard fails on reordered source enum"), restores via EXIT trap. Ran 3/3 PASS; `git diff` on the source is clean after.

5. > "`bottleneck` (digest-ttrpg.schema.yaml:81) is NOT pulled into scope — it is digest-side grouping, not a signal class (per seam reply §1); convergence guard compares only the taxonomy source, so it stays cleanly green"
   - **✓ Met.** No edit to `domains/ttrpg/schemas/digest-ttrpg.schema.yaml`. The convergence guard scopes to the top-level `signal:` block of `session-events-base.schema.yaml` (`vendor-drift-guard.sh:80-85`), which never contained `bottleneck`. Logged as a tracked follow-up in the sprint plan, not this sprint.

6. > "Every pre-existing `domains/agent-systems/scripts/test-*.sh` suite passes unchanged"
   - **✓ Met.** 12/12 suites PASS (`test-check-payoff-dominance`, `-discover-engine`, `-dungeon-referee`, `-normalize-sidecars`, `-ollama-agent`, `-party-wrapper`, `-scaffold-playtest`, `-sim-pipeline`, `-sweep-report`, `-validate-batch`, `-validate-scenario`, `-validate-sidecar`). Zero modifications to any test expectation.

## Tasks Completed

| Task | Deliverable | Files (changed lines) |
|------|-------------|------------------------|
| 2.1 | Vendor taxonomy + pin | `domains/agent-systems/schemas/vendor/signal-taxonomy.v1.schema.json` (new, byte-exact); `VENDOR.yaml:14-28` (git_sha→`3fa6c91`, vendored_at→`2026-06-14`, +3rd entry) |
| 2.2 | Extend byte-diff loop | `scripts/ci/vendor-drift-guard.sh:20` (added taxonomy to `for name in …`) |
| 2.3 | Convergence guard | `scripts/ci/vendor-drift-guard.sh:68-105` (new Python block); final msg `:108` |
| 2.E2E | Regression test + CI wiring | `scripts/ci/test-vendor-drift-guard.sh` (new); `.github/workflows/ci.yaml:110-111` (new step) |

**Approach notes:**
- The VENDOR.yaml self-pin Python block (`vendor-drift-guard.sh:38-62`) iterates `files` entries generically — it covered the new taxonomy entry with **zero code change**.
- Convergence parser is stdlib-only (`json` + targeted `re`), matching the guard's existing embedded-Python convention. It anchors on the top-level `signal:` block because 6 other `values:` lines exist in the source schema; a whole-file grep would be ambiguous.
- Both observed-trace pins were re-verified byte-identical at `3fa6c91` before bumping `upstream.git_sha` (cycle-010 only *added* the taxonomy file).

## Technical Highlights

- **Load-bearing, not decorative.** Arneson authors the 9 values; Gygax republishes them. Vendoring back creates a cycle that only earns its keep if drift fails loudly — Task 2.3 is that mechanism. Without it the sprint would be a no-op file copy.
- **Inverted publish/vendor direction, same drift discipline.** observed-trace: Gygax authors → Arneson vendors. Taxonomy: Arneson authors → Gygax publishes → Arneson vendors. The convergence guard is the extra check this inversion requires.
- **Surgical.** No validator/producer code touched; `bottleneck` correctly left out of scope per seam reply §1.

## Testing Summary

- **New:** `scripts/ci/test-vendor-drift-guard.sh` — 3/3 PASS (green clean / fails on reorder / green after restore). Self-restoring via EXIT trap; SKIPs cleanly without the gygax sibling.
- **Drift guard:** `ARNESON_GYGAX_ROOT=../construct-gygax ./scripts/ci/vendor-drift-guard.sh` → exit 0, 3 files + 3 pins + convergence all OK.
- **Regression:** all 12 `domains/agent-systems/scripts/test-*.sh` → 12/12 PASS unchanged.
- **Run:** `cd domains/agent-systems/scripts && for t in test-*.sh; do bash "$t"; done`

## Known Limitations

- The convergence guard parses the source YAML with a targeted regex (no stdlib YAML). It is scoped to the `signal:` block and covered by the reorder negative test; if the source schema's block layout changes radically the parser anchors would need revisiting (mitigation noted in sprint plan Risks).
- The regression test mutates the real source file transiently (EXIT-trap restored). Chosen over making the guard's source path env-configurable, which would add a test-only knob to production code.

## Verification Steps (for reviewer)

```bash
# 1. Vendored bytes match upstream
shasum -a 256 domains/agent-systems/schemas/vendor/signal-taxonomy.v1.schema.json
#   → f6ba7182d8d41e53595a142316451377456a1899217a085fdbc9c4a22e542ce6

# 2. Drift guard green (3 files, pin, convergence)
ARNESON_GYGAX_ROOT=../construct-gygax ./scripts/ci/vendor-drift-guard.sh

# 3. Convergence guard regression (both directions)
ARNESON_GYGAX_ROOT=../construct-gygax ./scripts/ci/test-vendor-drift-guard.sh

# 4. Zero regression
cd domains/agent-systems/scripts && for t in test-*.sh; do bash "$t" >/dev/null && echo "PASS $t"; done
```

## Out of Scope (tracked follow-up)

Reconcile the `bottleneck` grouping key in `domains/ttrpg/schemas/digest-ttrpg.schema.yaml:81`. Sprint-1's seam reply committed this as internal digest-side cleanup, explicitly separate from the signal taxonomy. Not this sprint.
