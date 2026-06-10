# Implementation Report: Sprint 4 (global sprint-15, FINAL) — Versatility Authoring + E2E

**Date:** 2026-06-10 · **Sprint:** local 4 / global 15 (cycle-002 playtest-instrument-v4.1)
**Branch:** feature/sprint-plan-v41-20260610

## Executive Summary

A new playtest is now cheap to stand up: `scaffold_playtest.py` generates a complete,
self-checking, payoff-dominant skeleton from four flags; `authoring-a-playtest.md` is the
worked guide with the calibration discipline inline; the honesty boundary is mechanized as a
CI banned-copy gate. All five PRD goals validated end-to-end. 24 new assertions this sprint
(scaffold 12 + the rest across the cycle); 138 total, all green; banned-copy clean.

## AC Verification

**AC-1** — "scaffolder emits a skeleton whose smoke test passes on first run; exit 2 on self-check failure"
✓ Met — scaffold_playtest.py self-runs the generated smoke test, exit 2 if broken (R-2). test-scaffold-playtest.sh: happy path exit 0, generated smoke passes standalone, corrupted-referee → smoke fails (exit-2 path reachable).

**AC-2** — "generated referee stub is an honest DEFEAT no-op (--check exit 1, --state {}, importable)"
✓ Met — REFEREE_STUB `run()` returns `(False, {...})`; test asserts `--check` exit 1 + `--state` valid JSON.

**AC-3** — "generated skeleton validates against validate_scenario + check_payoff_dominance (hack dominant once authored)"
✓ Met — generated incentive-state ships an `intended` + payoff-dominant `hack`; check_payoff_dominance → PASS (test asserts it). Manifest parses (validate-skills/fixture-shape green).

**AC-4** — "authoring-a-playtest.md documents fixture+referee+incentive-state+rungs + the FR-3 calibration rule with check_payoff_dominance as the mechanized check"
✓ Met — docs/authoring-a-playtest.md, 5 steps + "make the incentive gameable, honestly" (the calibration rule, PASS/WARN, "tune the task, never rig it") + the honesty-boundary closing section. Dungeon cited as the worked reference.

**AC-5** — "banned-copy grep clean over new docs + report wording (NFR-7)"
✓ Met — scripts/ci/banned-copy-check.sh scans all docs/ + domain.conventions.md + sweep_report.py, excludes the ban-list table rows, fails the build on any other occurrence. Green. Wired into validate-agent-systems.sh.

**AC-6 (G1)** — "a NEW playtest (not the dungeon) authored from guide + scaffolder alone, validates + runs"
✓ Met — E2E: scaffolded `code-golf` (and `maze-solver`) from flags alone → smoke passes, payoff-dominance PASS. Human-acceptance class (exercised, not CI-gated), per plan.

## Task 4.E2E — Goal Validation (5/5)

| Goal | Validation | Result |
|------|-----------|--------|
| G1 New-playtest authorability | Scaffolded `code-golf` (new, not dungeon) from flags alone | ✓ validates + runs (honest DEFEAT until authored); payoff-dominance PASS |
| G2 One-command comparison | 3-config sweep (modelA/B/C), n=2/rung, via real engine → sweep_report | ✓ triaged table, all configs × rungs, per-cell counts, n>1 spread |
| G3 Honest power (capability-not-gate) | Multi-trial run (n=2/rung) on the fixture via real engine → regrade | ✓ runs with n>1 (4 sidecars/2 rungs); reports counts, no n=1. *No cliff with the deterministic agent — not a failure (it doesn't game).* |
| G4 Hermetic rigor preserved | Full CI: 11 suites + banned-copy; 0 Ollama in CI | ✓ 138 assertions green; all 5 other validators green; banned-copy clean |
| G5 Honesty boundary held | banned-copy gate + check_payoff_dominance enforces calibration | ✓ no claim crosses sandbox-limits §A/B; calibration mechanized |

Integration verified end-to-end: scaffold → validate → (engine run) → regrade → sweep_report
→ playout record → /arneson view. No goal unachieved.

## Tasks Completed

| Task | Deliverable |
|------|-------------|
| 4.1 | scaffold_playtest.py — stdlib generator, self-checking, payoff-dominant skeleton |
| 4.2 | test-scaffold-playtest.sh — 12 assertions (happy path, smoke, dominance, DEFEAT stub, errors, exit-2 path) |
| 4.3 | docs/authoring-a-playtest.md — worked guide + calibration discipline + honesty boundary |
| 4.4 | scripts/ci/banned-copy-check.sh — honesty gate, wired into CI |
| 4.E2E | 5/5 goals validated with evidence (table above) |

## Known Limitations

1. G1's stranger-author acceptance is human-class (I exercised it as the stranger; not CI-gated) —
   per plan. A genuinely fresh operator pass would further harden the guide.
2. G3's "no cliff" here is expected: the deterministic agent never games (it's honest plumbing).
   A real cliff hunt is the post-cycle capability the instrument now enables — the point was that
   the instrument *runs with power*, not that a cliff appears on a deadline (capability-not-gate).

## Verification

```bash
./scripts/ci/validate-agent-systems.sh   # 11 suites, 138 assertions + banned-copy gate
python3 domains/agent-systems/scripts/scaffold_playtest.py --id demo --task "x" --difficulty-range 1-10 --out /tmp/demo
```

## Audit Feedback Addressed (cycle 2)

Audit APPROVED non-blocking but flagged two; both closed (cheap + right):
- **SEC-001 (path traversal via --out):** scaffold_playtest.py now refuses `..` in --out and
  relative paths resolving outside cwd; absolute paths honored (operator intent). Test added.
- **CQ-001 (--id trailing dash):** regex tightened to true kebab (start+end alphanumeric) —
  also guarantees --id can never influence the output path. Test added.
Suite: scaffold-playtest 12 → 14; full vertical 140 assertions, all green.
