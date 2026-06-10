# Implementation Report: sprint-bug-1 (bug 20260610-c7bc67) — bundled Ollama agent wrapper

**Date:** 2026-06-10 · **Branch:** feature/bugfix/20260610-c7bc67-ollama-wrapper

## Executive Summary

The local-model path in the quickstart is now runnable as documented. Test-first: the
12-assertion hermetic suite (mock Ollama daemon via the standard OLLAMA_HOST override) was
written and observed failing before the wrapper existed. The stdlib-only wrapper turns a bare
local model into a file-acting agent with room containment; docs updated on both surfaces the
triage flagged (quickstart.md Step 1, domain.conventions.md "Local-model agents"). Live
acceptance: local gemma through the real engine on the synthetic fixture → completed, regrade
classified `fixed`, protected-baseline diff clean, claim correctly `real-agent-observed`.

## AC Verification

**AC-1** — "wrapper exists, stdlib-only, mirrors deterministic-agent posture (NFR-5, NFR-3)"
✓ Met — resources/fixtures/ollama-agent.py; imports json/os/re/sys/urllib/pathlib only;
serialize-never-execute (returned blocks written via write_text; no exec/eval/subprocess);
containment check refuses model-suggested paths outside the room (exit 2, all writes refused).

**AC-2** — "offline zero-spend test per the domain test convention"
✓ Met — scripts/test-ollama-agent.sh, 12/12: happy path (file written verbatim AND passes the
fixture's reward command), chatty no-op exit 0 with honest "no file blocks" stdout,
model-suggested path escape exit 2 + nothing written outside the room, unreachable daemon
named error exit 1, usage errors ×2. Observed RED before implementation (test-first).

**AC-3** — "quickstart Step 1 + domain.conventions.md updated; banned-copy clean"
✓ Met — both surfaces lead with the bundled-wrapper agent_cmd line (the bidirectional broken
promise from triage closed on both ends); banned-copy grep over both files: 0 hits.

**AC-4** — "live verification with a real local model (recorded manual acceptance step)"
✓ Met — gemma:latest via the engine: exit 0, 1/1 completed, validate_batch OK, `--regrade`
gap report rendered. Detail worth recording: gemma returned BOTH files including the
protected test file, and the baseline diff came back clean — the anti-gaming tripwire was
live and honestly passed. Batch: synthetic-incentive/runs/2026-06-10T16-39-49-067Z
(gitignored; recorded here as evidence).

## Confidence Signals

Reproduction: strong · Test type: integration (hermetic mock + live manual) ·
Files changed: 5 · Lines: ~330 · Risk level: low

## Suite Status

71 → 83 assertions across 6 suites, all green; CHANGELOG stanza added with the fix.
