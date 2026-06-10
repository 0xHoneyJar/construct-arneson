# Review — sprint-bug-2 (bug 20260610-594345): APPROVED

All good (with noted concerns)

Verified: both fixes behind red-first tests; full suite 91/91; triage proven on the real
casualty batches; CHANGELOG shipped with the fix; quickstart guidance matches the constant's
own documentation.

## Adversarial Analysis

### Concerns (non-blocking)
1. **Signature false-positive surface:** an agent that legitimately *prints* the literal string
   `ERROR: [ollama-agent]` in its stdout would be flagged. Improbable, warn-only, and the
   clean-batch test guards the common case — acceptable. If other wrappers proliferate, a
   shared "infrastructure marker" convention would generalize this.
2. **DEFAULT_TIMEOUT (600) equals the common engine budget rather than sitting under it** —
   when both fire at once, the engine's SIGKILL records an honest `timeout` status, so no
   fake verdict either way; the quickstart teaches the explicit-under-budget form (560).
   Acceptable; the constant's comment carries the rule.
3. **Triage lives in validate_batch only** — the future `--sweep` table must consume it
   (findings file item 4) rather than re-deriving; noted for that cycle's spec.

### Assumption Challenged
- That the wrapper's error marker format is stable. It is now load-bearing for triage —
  marked by this review: changing the `ERROR: [ollama-agent]` prefix requires updating the
  validator + tests together (they are co-tested, so CI catches drift).

### Alternative Not Considered
- Rejecting (exit 2) casualty batches instead of warning. Rejected: the batch IS
  contract-valid and the grader handles it fine; the defect was silence, not acceptance.
  Warn-not-reject keeps standalone workflows alive while making the table-poisoning visible.
