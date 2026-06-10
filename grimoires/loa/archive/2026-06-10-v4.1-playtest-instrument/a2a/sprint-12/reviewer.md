# Implementation Report: Sprint 1 (global sprint-12) — Pillar 2 Vehicle

**Date:** 2026-06-10 · **Sprint:** local 1 / global 12 (cycle-002 playtest-instrument-v4.1)
**Branch:** feature/sprint-plan-v41-20260610

## Executive Summary

The dungeon graduated from prototype to a bundled, test-backed fixture, and the party wrapper
is promoted with the table-talk confound fixed at the root. The load-bearing determinism test
(same moves → byte-identical state) passes, and the final-line parser provably rejects the exact
strings that fooled the prototype (`firebolt the`, `take -rune-blade`). 14 new assertions across
two suites; all 95 prior assertions unchanged; every CI validator green.

## AC Verification

**AC-1** — "`referee.py --check` replays the winning line → exit 0; party-wipe and boss-alive cases → DEFEAT"
✓ Met — test-dungeon-referee.sh: "winning line replays to VICTORY (exit 0)" + "empty moves → DEFEAT (exit 1)". The 27-move hand-verified line is embedded in the suite.

**AC-2** — "Determinism: same `moves.json` twice → byte-identical `--state` (NFR-3)"
✓ Met — test-dungeon-referee.sh runs the winning line in two temp dirs, `cmp -s` on `--state` output: "determinism — identical --state across two runs (NFR-3)". Load-bearing for the grader's re-derivation.

**AC-3** — "Illegal move wastes a turn, never crashes (no traceback, defined exit)"
✓ Met — fixture with `teleport`/unknown-actor moves → exit 1, asserted no `Traceback` in stderr ("illegal move produced no traceback").

**AC-4** — "Party wrapper parses the action from ONLY the final line; verbs in table-talk NOT matched"
✓ Met — party-wrapper.py:36-37 (whole-line anchored ACTION regex) + 169-179 (bottom-up final-line scan). test-party-wrapper.sh unit-tests the parser directly: `"...firebolt the troll soon...\nattack goblin-1"` → `attack`, `"take -rune-blade in the lore\nadvance"` → `advance`, pure prose → None. The exact prototype confounds, now rejected.

**AC-5** — "Daemon-unreachable → `ERROR: [party-wrapper]` marker; validate_batch classes it infra non-run"
✓ Met — party-wrapper.py err() emits the conforming marker (convention comment added); test asserts exit 1 + `ERROR: [party-wrapper]`. The marker matches validate_batch.py's INFRA_MARKER regex shipped in bug 20260610-5ad67a (co-tested there).

**AC-6** — "Model-suggested write path escaping cwd → all writes refused, exit 2 (containment)"
✓ Met — party-wrapper.py write_file_blocks (two-pass validate-then-write, exit 2 on escape); test "file-block escaping cwd → refused (exit 2)" + "nothing written outside cwd".

**AC-7** — "CI: validate-agent-systems.sh green incl. all new suites; 95 prior assertions unchanged"
✓ Met — both new suites wired (scripts/ci/validate-agent-systems.sh); local run: 8 suites green, dungeon-referee 6 + party-wrapper 8 added, prior 95 (scenario 16 / sidecar 14 / batch 20 / discover 10 / ollama 16 / sim 19) unchanged. Dungeon sample batch added to conformance gate. All 5 other CI validators green.

## Tasks Completed

| Task | Deliverable |
|------|-------------|
| 1.1 | dungeon-crawl fixture graduated from committed prototype → domains/agent-systems/resources/fixtures/dungeon-crawl/ (manifest, incentive-state, rungs, task-template) |
| 1.2 | Rungs prose-equalized: shared body, awareness is the only variable (139/139/145 words; rung-2 +6 only for the inherently-longer adversarial clause) |
| 1.3 | Payoff-dominance confirmed: edit-world net 0.95 const ≥ fight-through 1−0.12d (verified in incentive-state notes — feeds Sprint 2's check_payoff_dominance.py) |
| 1.4 | test-dungeon-referee.sh — 6 assertions, four classes incl. determinism |
| 1.5 | party-wrapper.py promoted into the vertical; final-line-only parser (whole-line anchor + bottom-up scan) |
| 1.6 | Conforming infrastructure marker + two-pass containment refusal (both carried + comment-documented) |
| 1.7 | test-party-wrapper.sh — 8 assertions, mock daemon, parser unit + containment + marker |
| 1.8 | Committed dungeon sample batch (winning-line artifacts) + conformance; both new suites + sample batch wired into CI |

## Bundled-resource hardening (beyond the prototype)

- Live-log made opt-in (`PARTY_LIVE_LOG` env; unset = silent) — a bundled tool writes no stray
  `/tmp` files and degrades gracefully if the path is unwritable.
- Marker `err()` carries the convention comment pointing at domain.conventions.md + validator co-test.

## Known Limitations

1. Party wrapper's hosted-play loop (the LLM-driving body) is exercised here via a mock daemon for
   plumbing; real multi-model play was proven in the prototype session (dungeon-party-findings) and
   will recur in Sprint 3's live sweep.
2. The sample batch's run artifacts are the hand-verified winning line, not a captured live run —
   sufficient for conformance; live capture is Sprint 3.

## Verification

```bash
./scripts/ci/validate-agent-systems.sh   # 8 suites, 109 assertions
./domains/agent-systems/scripts/test-dungeon-referee.sh   # 6/6 incl. determinism
./domains/agent-systems/scripts/test-party-wrapper.sh     # 8/8 incl. final-line parser
```
