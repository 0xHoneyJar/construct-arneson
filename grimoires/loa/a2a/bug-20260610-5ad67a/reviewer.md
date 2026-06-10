# Implementation Report: sprint-bug-3 (bug 20260610-5ad67a) — infrastructure-marker convention

**Date:** 2026-06-10 · **Branch:** feature/bugfix/20260610-5ad67a-triage-convention

## Executive Summary
The triage false-negative is closed by replacing the literal-string match with the documented
convention. Test-first: the party-wrapper-marker case was written and observed red (sidecar
passed untriaged), then green after the anchored regex landed. False-positive guard proven:
agent-printed "ERROR: [compiler]" prose does not flag.

## AC Verification
**AC-1** — "convention-based regex in the triage block"
✓ Met — validate_batch.py: `INFRA_MARKER = re.compile(r"ERROR: \[[A-Za-z0-9_-]*(?:agent|wrapper)\]")`
(module-level, documented) replacing the literal `in` check; warn-not-reject and message
unchanged in posture (wording generalized: "a wrapper infrastructure error marker").
**AC-2** — "convention documented; load-bearing comments updated"
✓ Met — domain.conventions.md gains "Wrapper authors: the infrastructure-marker convention"
(MUST-emit prefix, suffix-anchor rationale, co-test pointer); ollama-agent.py err() comment
now references the convention instead of claiming sole ownership of the string.
**AC-3** — "three test cases: second-wrapper warns / regression / false-positive guard"
✓ Met — test-validate-batch.sh: party-wrapper marker → warning asserted (observed RED first);
existing ollama-agent casualty test still passing (regression, untouched); "ERROR: [compiler]"
in agent prose → asserted NOT flagged. Suite 20/20; all suites 95/95.

## Confidence Signals
Reproduction: strong (probe reproduced live in triage) · Test type: unit/hermetic ·
Files changed: 4 · Risk: low
