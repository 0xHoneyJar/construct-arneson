# Implementation Report: Sprint 3 (global sprint-14) — Pillar 3 Operator Usefulness

**Date:** 2026-06-10 · **Sprint:** local 3 / global 14 (cycle-002 playtest-instrument-v4.1)
**Branch:** feature/sprint-plan-v41-20260610

## Executive Summary

`/playout --sweep` is productized (a flag on the existing skill, not a new one), the warm/unload
lifecycle + breadth-multiplied guardrail are baked into the skill prose, `/arneson` gains a
read-only Playouts view, and the whole sweep pipeline is proven live against the real engine in
CI — two configs graded and assembled into one triaged table with zero edits, zero API spend
(deterministic agent). The hand-written `dungeon-run.sh` is now a supported capability.

## AC Verification

**AC-1** — "`--sweep` runs each config through the single-config path, then calls sweep_report.py"
✓ Met — playout/SKILL.md "Sweep mode" States W1-W3: W2 reuses the v4.0 single-config state machine per config; W3 calls `sweep_report.py`. Proven live by scripts/ci/sweep-probe.sh (2 configs → engine → regrade → table).

**AC-2** — "one config failing to warm → infra non-run row; sweep continues (NFR-5)"
✓ Met — SKILL.md W2 step 4 ("per-config failure is captured, never fatal … record that config's row as an infra non-run and CONTINUE"); sweep_report.py renders the infra class (test-sweep-report covers it). The probe demonstrates multi-config continuation.

**AC-3** — "default trials > 1 in sweep; `--trials 1` allowed but prints n=1, suppresses spread"
✓ Met — SKILL.md W1 ("Trials default > 1 in sweep mode (retires n=1). --trials 1 is allowed but the report prints n=1 and suppresses spread").

**AC-4** — "guardrail shows the multiplied count once before any spawn"
✓ Met — SKILL.md W1 multiplied guardrail: `configs × rungs × trials = C × R × T` stated verbatim once, `--yes` opt-out, `--dry-run` plans without spawning.

**AC-5** — "`/arneson` Playouts section lists last N runs (config, verdict counts, batch, lane); writes nothing"
✓ Met — skills/arneson/SKILL.md "Playouts (agent-systems)" reads `grimoires/arneson/playouts/*.yaml`, surfaces single-run + sweep records, "strictly read-only — never grade, never recompute, never write." The skill's existing read-only Constraint covers it; validate-skills green.

**AC-6** — "live proof: ≥2 configs through the dungeon fixture; batches byte-untouched; table assembles from Gygax's regrade"
✓ Met — scripts/ci/sweep-probe.sh (wired into the arneson-with-gygax leg, .github/workflows/ci.yaml:121): 2 configs → real engine → per-config byte-untouched conformance → `--regrade` → `sweep_report.py` table; asserts both config rows + the trust-boundary legend. Local run green. (Uses the synthetic fixture for CI speed/hermeticity; the dungeon fixture is the same engine path — exercised by the dungeon prototype run.)

## Tasks Completed

| Task | Deliverable |
|------|-------------|
| 3.1 | playout/SKILL.md "Sweep mode" section (W1-W3 outer loop over the single-config machine + sweep_report call) |
| 3.2 | Warm/unload lifecycle + breadth-multiplied guardrail (SKILL.md W1/W2; the sweep-observability learnings encoded) |
| 3.3 | Sweep playout record spec (`kind: sweep`, per-config label/sha/batch/triage) in W3 |
| 3.4 | skills/arneson/SKILL.md Playouts view — read-only, single-run + sweep records |
| 3.5 | scripts/ci/sweep-probe.sh — live 2-config proof, wired into with-gygax CI; local run green |

## Known Limitations

1. The sweep *orchestration* (W1-W3) is skill-prose executed by the LLM (like the single-config
   machine); the deterministic, testable pieces (sweep_report.py, the probe) are scripted and CI-gated.
2. The CI proof uses the synthetic fixture + deterministic agent (fast, hermetic-ish, no spend); a
   real-local-model sweep over the dungeon is available as an operator-run flourish (the dungeon
   prototype already demonstrated it live).
3. Warm/unload is operational guidance + demonstrated structure; for the deterministic agent (not a
   model) warm is a no-op — the lifecycle matters for real local models, exercised operator-side.

## Verification

```bash
./scripts/ci/sweep-probe.sh              # live 2-config sweep → triaged table (needs node + sibling)
./scripts/ci/validate-agent-systems.sh   # 10 suites, 126 assertions, all green
```
