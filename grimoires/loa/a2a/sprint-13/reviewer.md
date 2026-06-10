# Implementation Report: Sprint 2 (global sprint-13) — Pillar 1 Rigor

**Date:** 2026-06-10 · **Sprint:** local 2 / global 13 (cycle-002 playtest-instrument-v4.1)
**Branch:** feature/sprint-plan-v41-20260610

## Executive Summary

Both carried probes resolved against ground truth, both cleanly. The cross-config aggregator
(`sweep_report.py`) counts Gygax's gradings into a triaged table and provably never recomputes
a verdict; the calibration checker (`check_payoff_dominance.py`) mechanizes "tune, never rig"
by checking declared economics only; the difficulty block is additive and engine-inert
(confirmed live). 17 new assertions; all 109 prior green.

## AC Verification

**AC-1** — "`sweep_report.py` renders all three cell classes distinctly from synthetic per-config summaries; deterministic (no clock, stable ordering)"
✓ Met — test-sweep-report.sh: verdict/infra/ungraded all rendered; "deterministic: identical output across two runs" (cmp -s); "config order follows CLI order". No `Date`/`random` in the script.

**AC-2** — "never recomputes ratios/cliffs — carries Gygax's output verbatim (contract boundary)"
✓ Met — sweep_report.py `triage()` reads `observation.classification` (Gygax's scorer wrote it) and counts; the cliff/within-noise interpretation is explicitly deferred to each config's own report. Test "never emits a computed cliff/forecast verdict" asserts no `argmax @`/`no cliff observed`/`vs forecast`/`fix:hack` strings. (NFR-6 held.)

**AC-3** — "manifest with `difficulty:` loads and runs; without it = v4.0 behavior"
✓ Met — additive `difficulty:` block on the dungeon manifest; engine dry-run planned the run with no rejection (OQ-2 live confirmation). Other fixtures unchanged ⇒ v4.0 behavior intact.

**AC-4** — "`check_payoff_dominance.py`: dominant fixture → PASS; non-dominant → WARN exit 0"
✓ Met — dungeon → PASS (edit-world 0.95 ≥ fight-through 0.88), synthetic → PASS too; test's synthetic non-dominant control → WARN exit 0; unparseable → exit 1; missing intent → exit 1. Warn-not-reject (NFR-5) held.

**AC-5 (OQ-1)** — "JSON consumption path OR a `--json` brief committed (decision in NOTES)"
✓ Met — probe found trace CLI is Markdown-only (index.ts:77-92). Decision recorded in NOTES.md: sweep_report consumes graded sidecars (structured JSON), NOT the Markdown report; `discovery/gygax-trace-json-brief.md` drafted for the richer interpretation layer (reporting nit, non-blocking). No brittle parsing.

**AC-6 (OQ-2)** — "engine-ignores-unknown-keys confirmed OR doc nit filed"
✓ Met — confirmed: `loadManifest` (index.ts:40-45) reads named fields off `Record<string,any>`, validates only reward_command+rungs. Recorded in NOTES.md; live dry-run confirmation against the difficulty-block manifest. No Gygax change needed.

## Tasks Completed

| Task | Deliverable |
|------|-------------|
| 2.1 (OQ-1) | Probe + decision (sidecars not Markdown) + gygax-trace-json-brief.md |
| 2.2 | sweep_report.py — cross-config triaged table, counts-only, deterministic |
| 2.3 | test-sweep-report.sh — 10 assertions (3 classes, determinism, ordering, trust boundary, errors) |
| 2.4 (OQ-2) | Confirmed ignore-unknown-keys; additive `difficulty:` block on dungeon manifest; live dry-run |
| 2.5 | check_payoff_dominance.py — stdlib safe-arithmetic evaluator (no eval), PASS/WARN/exit-1 |
| 2.6 | test-check-payoff-dominance.sh — 7 assertions incl. non-dominant control + unparseable |

## Beyond-spec (necessary)

- **restricted_yaml.py gained `>` folded-scalar support** (it had `|` literal only; incentive-state
  descriptions use `>`). General, backward-compatible — regression-checked: validate_scenario 16/16
  and sim-pipeline 19/19 still green. Benefits every consumer.

## Known Limitations

1. `check_payoff_dominance.py`'s evaluator is a deliberately tiny grammar (numbers, the context
   var, + - * / and parens). Exotic payoff expressions (sin, piecewise) are unparseable → exit 1
   by design — a fixture author gets a loud "express it in the supported grammar," not a wrong PASS.
2. sweep_report's "ungraded" class includes any completed-but-unscored sidecar; for the real lane
   (always graded on --regrade) this is empty; it exists for the simulated/standalone lane.

## Verification

```bash
./scripts/ci/validate-agent-systems.sh   # 10 suites, 126 assertions
python3 domains/agent-systems/scripts/check_payoff_dominance.py \
  domains/agent-systems/resources/fixtures/dungeon-crawl/incentive-state   # PASS
```
