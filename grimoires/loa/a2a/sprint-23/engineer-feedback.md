# Senior Tech Lead Review — cycle-007 Sprint 1 (global 23): FR-1 decision-trace emitter

**Verdict: All good (with noted concerns)**

Concerns documented below are **non-blocking**: all 8 acceptance criteria are met with file:line
evidence, the 14-check test passes, the full suite is 17/17 green, the closing proof against the live
Gygax lens succeeds (exit 0, `simulation-derived`), and there are no security issues. The concerns are
hardening/forward-compatibility recommendations, not defects in the shipped scope.

## What was verified (not from the report — from the code)

- `emit_decision_trace.py` builds all 10 required fields; `claim_strength`/`producer.kind` are literals
  (`:309`, `:311`), not derived — a sim log cannot produce `real-agent-observed` (NFR-5). ✓
- Self-check (`validate_record` `:138-253`) hand-encodes the vendored contract; `main` refuses to write
  on any violation (`:375-383`, exit 2). Re-ran broken-label fixture → exit 2. ✓
- Determinism: `sort_keys=True` (`:345`), no `datetime`/`random`. Golden + two-run byte-match. ✓
- Vendoring: byte-exact copy (sha `83d6a69f…`), wholesale bump byte-neutral, drift guard green for 4
  files. ✓
- Standalone: import-grep confirms zero `construct-gygax` coupling; no subprocess/shell-out. ✓
- AC Verification section present in `reviewer.md`, every AC walked verbatim with file:line. ✓

## Adversarial Analysis

### Concerns Identified
1. **Event order is document-order, not `seq`-sorted** (`emit_decision_trace.py:301-323`). SDD §3.1 says
   "iterate agent_turn in seq order"; the code iterates the `events` list as written. For append-only
   sidecars these coincide, so `t`-indexing is correct in practice — but a sidecar with out-of-order
   `seq` would index by document order. Matches `project_trace.py`'s behavior. Non-blocking; a defensive
   `sorted(..., key=seq)` would harden it.
2. **`events` is not type-guarded** (`emit_decision_trace.py:301`). A malformed sidecar with `events:` as
   a mapping (not a list) would make `ev.get(...)` raise `AttributeError` — an uncaught crash rather than
   a clean `exit 1`. Matches the sibling `project_trace.py`; an `isinstance(events, list)` guard would
   convert it to a clean input error.
3. **`actor_id` collapses multi-actor episodes** (`emit_decision_trace.py:278-280`). With no persona id
   in the preamble, every decision in an episode gets the same `sim:<corpus_id>` actor. Correct for the
   single-actor fixture; latent for a party/multi-agent sim (the lens would attribute all decisions to
   one actor). SDD RA-2 already flags this for "revisit when a multi-actor sim corpus exists."
4. **No CHANGELOG entry for cycle-007** (process). CHANGELOG uses per-cycle `[Unreleased]` blocks
   (precedent: cycle-002, cycle-003). Recommend adding the cycle-007 Unreleased entry by cycle end
   (Sprint 25 is the natural place, or at ship).

### Assumptions Challenged
- **Assumption**: the sim event log is append-only and `seq`-ordered, so document order == `seq` order.
  **Risk if wrong**: `t` would not reflect decision chronology, mis-ordering the corpus.
  **Recommendation**: sort by `seq` defensively, or assert monotonic `seq` (cheap; closes Concern 1).

### Alternatives Not Considered
- **Alternative**: add the forward-compatible `offered_labels` read-path now. SDD §1.2 (lines 119-123)
  describes it as "~3 defensive lines": if `agent_turn.offered_labels` is present, emit a real
  multi-option `offered` set (assert `chosen ⊆ offered`) and drop the chosen-only marker; else fall back
  to chosen-only.
  **Tradeoff**: ~6-8 lines of currently-dead read-path vs. zero-change forward-compatibility the day a
  serializer emits the field — which is the path from *contract* seam to *analytic* seam.
  **Verdict**: the current chosen-only approach is **justified** — simplicity-first (the field does not
  exist in `session-events-agent` yet, so reading it is speculative) and the SDD explicitly deferred
  adding the field this cycle. But this is the natural next step; recommend it head the offered-set
  capture cycle (the work RA-1 routes analytic value to).

## Documentation Verification
- CLAUDE.md: N/A (no new top-level command/skill; `emit_decision_trace.py` is a domain script).
- Code comments: adequate (docstring explains chosen-only honesty, guardrails, exit codes).
- Doc note added: `domains/agent-systems/docs/emitting-a-decision-trace-corpus.md`. ✓
- CHANGELOG: missing cycle-007 entry — non-blocking, see Concern 4.

## Next Steps
- Approved for the audit gate. Carry Concerns 1-2 (defensive guards) and the Alternative (offered_labels
  read-path) as candidates for the offered-set capture cycle; add the CHANGELOG entry by cycle end.
