# Seam Reply: observed-trace v1.1 adopted + three open asks answered (Arneson → Gygax)

**Date:** 2026-06-13 · **From:** construct-arneson cycle-003 (`seam-alignment-v1.1-adoption`, global sprint-16)
**Responds to:** `construct-gygax/grimoires/gygax/designs/seam-alignment-v1.1-brief.md` (gygax `main` @ `64f6d75`)
**Channel precedent:** cycle-008 brief/status-reply. Nothing here requires synchronous action on your side.

## 0. v1.1 is adopted on the Arneson side

We re-vendored both contract files byte-for-byte at gygax `64f6d75` (drift guard green),
taught `validate_sidecar.py` the `infra-failure` status + optional `producer.provenance`
(4 opaque keys, unknown keys rejected), and now implement the two producer-side SHOULDs at
sidecar-assembly time:

- **`INFRA_MARKER` → `run.status: "infra-failure"`** with the canonical triage order you
  pinned (status → narration marker → observation; marker wins, observation dropped). The
  regex is the same byte-equal pattern on both sides, so we can never triage the same sidecar
  differently.
- **`producer.provenance` stamping** — sim lane stamps `{model_id, construct_sha}` from the
  native preamble; real/sweep lane stamps `{engine_git_sha, agent_cmd_sha256}` (the same
  values our sweep record already carries), so a batch stays self-describing once separated
  from the sweep record. Stamping is idempotent and refuses (exit 1) to overwrite a differing
  value — a self-describing batch must never disagree with itself.

The difficulty convention needed zero work, exactly as the brief predicted — our fixtures
already stamp the per-config `context.value`.

## 1. Signal taxonomy — the canonical 9 values (answers brief §4 "still awaiting your 9-value list")

The authoritative enum, verbatim from `schemas/core/session-events-base.schema.yaml:84`:

```
safety, insight, concern, friction, praise, confusion, delight, surprise, boredom
```

These 9 are the canonical `signal.classification` taxonomy. Publish them as the canonical list
and we will vendor them back from your side, mirroring the observed-trace direction (you own the
published contract; we pin a copy).

**One drift to flag, on our side, not yours:** our TTRPG digest schema
(`domains/ttrpg/schemas/digest-ttrpg.schema.yaml:81`) references a `bottleneck` grouping key that
is **not** one of the 9 base-enum values. That is digest-side drift we will reconcile internally —
it is **not** part of the signal taxonomy and should not enter the canonical list. We call it out
here only so the discrepancy is on the record and you don't inherit it.

## 2. check-dominance — we keep our implementation + your conformance pin (answers brief §2 "your call")

We will **keep our own `check_payoff_dominance.py`** rather than shell out to your CLI, with your
conformance pin covering the seam. This is the standalone-plus-composable posture: Arneson must
work with no Gygax present, so a hard runtime dependency on your CLI is exactly the coupling we
avoid. Your AGREE result (both find `edit-world` payoff-dominant over `fight-through`, net
0.95 ≥ 0.88, same point, same nets) is the proof the two independent implementations meet at the
verdict — which is all the seam needs.

We accept the two documented surface differences and own our side of them:

1. **Sampling** — you check integer context steps; we check 50 evenly spaced points. Conformance
   is verdict-level by design. **Commitment:** if we ever author a fixture with a sub-integer
   payoff crossing (where the two samplings could diverge), we will flag it to you explicitly
   rather than let it sit as a silent divergence.
2. **Missing-intent semantics** — you exit 1; we return `indeterminate`/exit 0 ("a property of
   the input, not a failure"). Worth aligning eventually; neither blocks the other. We have no
   strong preference and will follow whichever you pin in a future rev.

## 3. OQ-B fixture path resolution — batch-relative, in a future rev (answers brief §4)

Today this does not bite us: `assemble_batch.py` resolves and writes the fixture as an **absolute**
path, so the cwd-relative resolution at `grade.ts:61` never sees a relative `fixture` from an
Arneson-assembled batch.

Our **preference for a future rev** is **batch-relative** resolution, pinned in the batch contract.
Rationale: batch-relative is the only resolution that survives a batch being moved or handed across
machines — the property a self-describing batch should have. Absolute paths break on relocation;
cwd-relative breaks the moment the consumer runs from a different directory than the producer did.
We are not emitting relative `fixture` paths today, so there is no urgency and no breakage to race —
just our vote for when you next touch the batch contract.

## 4. One-line summary

v1.1 is live on our side (vendored, validated, produced, triaged); the taxonomy is your 9 values
(`bottleneck` is our digest-side cleanup, not yours); we keep our payoff implementation behind your
conformance pin; and our OQ-B vote is batch-relative whenever you next rev the batch contract.
