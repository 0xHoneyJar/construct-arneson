# Implementation Report: sprint-bug-2 (bug 20260610-594345) — fake verdicts from wrapper timeouts

**Date:** 2026-06-10 · **Branch:** feature/bugfix/20260610-594345-fake-verdicts

## Executive Summary

Two coupled defects observed live during the four-model sweep are fixed test-first: the
wrapper's 240s fixed default timeout (which manufactured `failed` grades for runs where no
agent ever acted) and the absence of downstream triage (which let those non-runs pass as
verdicts). Three new assertions written and observed red, then green; the triage warning was
additionally verified against the sweep's REAL casualty batches (2/2 sidecars flagged).

## AC Verification

**AC-1** — "wrapper default timeout sized for local-model reality + pinned"
✓ Met — ollama-agent.py: `DEFAULT_TIMEOUT = 600` hoisted as a documented constant (comment
explains the size-under-engine-budget rule); main() uses it. Test: module-load assertion
`DEFAULT_TIMEOUT == 600` (observed red at 240/None, now green) + behavioral test: `--timeout 1`
vs a slow mock daemon → exit 1 with the named "timed out" error.

**AC-2** — "validate_batch.py warns 'non-run, not a verdict' on the wrapper's own error signature; warn-not-reject"
✓ Met — validate_batch.py: triage block alongside the existing honesty warning; matches the
literal `ERROR: [ollama-agent]` marker (stamping our own signature, not judging content —
G-4 posture); exit code unchanged. Tests: casualty fixture warns + exits 0 (observed red,
now green); clean batch asserts NO false triage. Real-data proof: both sidecars of the
sweep's qwen3-vl casualty batch flagged.

**AC-3** — "quickstart example shows explicit --timeout + sizing/pre-warm guidance"
✓ Met — quickstart.md Step 1: `--timeout 560` in the agent_cmd line, sizing note against
`stopping.timeout_seconds`, pre-warm tip (`ollama run <model> ""`). Banned-copy grep: clean.

## Confidence Signals
Reproduction: strong (two preserved evidence batches with duration_ms ≈ 240000) ·
Test type: unit/hermetic + real-data verification · Files changed: 4 · Risk: low

## Suite Status
83 → 91 assertions across 6 suites, all green. Evidence batches untouched (read-only).
