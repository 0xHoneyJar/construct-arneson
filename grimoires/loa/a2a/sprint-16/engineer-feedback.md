# Senior Lead Review — Sprint 1 (global #16): observed-trace v1.1 Adoption + Seam Reply

**Reviewer verdict:** All good (with noted concerns)
**Date:** 2026-06-13 · **Reviewed commit:** `9b798cb` · **Branch:** `feature/seam-alignment-v1.1-20260611`

## Overall Assessment

Reviewed the actual code, not just the report. The implementation is surgical, additive, and
well-tested: 12/12 test suites green (11 pre-existing unchanged + 1 new), every v1.0 fixture
still validates, drift guard green against the gygax sibling. All 9 acceptance criteria are
walked verbatim in the AC Verification section with file:line evidence I spot-checked and
confirmed. The diff traces cleanly to the planned tasks — no drive-by changes (the large
`sprint.md` / `ledger.json` deltas are the expected cycle-003 plan regeneration, not scope creep).

Karpathy check: **Think** — assumptions surfaced in the plan + report; **Simplicity** — one
normalization module, not two code paths; **Surgical** — every changed line traces to a task;
**Goal-driven** — each AC has a concrete test. Pass on all four.

The bright-line handling in `SKILL.md` is the strongest part of this work: rather than quietly
adding a sidecar-rewrite step that contradicts the existing "byte-untouched" rule, the
implementation explicitly reconciles all three affected bright lines (State 5 gate-workaround,
the observation-authoring rule, and the claim-softening rule). That is exactly the right
instinct for a seam that another construct depends on.

## Adversarial Analysis

### Concerns Identified

1. **Partial-normalization on provenance conflict** (`normalize_sidecars.py:116-124`,
   `normalize_dir`). If sidecar A is rewritten and sidecar B then raises `NormalizeError`
   (conflicting pre-existing provenance), A is already written to disk while assembly aborts
   exit 1. Mitigating factors: (a) bad provenance *keys* are rejected by
   `_parse_provenance_args` before any filesystem mutation; (b) `batch.json` is written *after*
   normalize, so an aborted batch lacks its manifest and `validate_batch.py` rejects it cleanly
   rather than it being mistaken for ready; (c) the conflict path requires engine-written
   sidecars to already carry *differing* provenance, which neither lane produces today.
   **Non-blocking** — real but near-zero-probability, and it fails safe. Worth a follow-up note
   if the real lane ever starts writing provenance independently.

2. **`infra-failure` enumerated rather than expressed as "not completed"**
   (`validate_sidecar.py:241`). The upstream schema's allOf[2] is structurally "status !=
   completed → no observation"; the validator enumerates the three non-completed statuses. A
   future v1.2 status would need this list updated in lockstep with `STATUS_ENUM`.
   **Non-blocking** — it mirrors the existing enumerate-everything style of the validator, and
   the validator-structure contract already mandates a re-vendor revisit, but `!= "completed"`
   would be the lower-maintenance expression.

3. **Mixed sidecar formatting within an assembled batch** (`normalize_dir` writes
   `json.dumps(indent=2)`; untouched sidecars keep the engine's `shutil.copy2` bytes). A batch
   can therefore contain sidecars in two formats. **Non-blocking** — purely cosmetic; no
   consumer keys on formatting, and `validate_*` are format-agnostic.

### Assumption Challenged

- **Assumption:** the sim lane's `model_id` + `construct_sha` and the real lane's
  `engine_git_sha` + `agent_cmd_sha256` never collide, so the four-key merge across the two
  stamping sites (`project_trace.py` + `assemble_batch.py --provenance`) never hits the
  refuse-on-conflict path during normal operation.
- **Risk if wrong:** a legitimate batch would abort exit 1 at assembly.
- **Verdict:** assumption is sound — the two sites stamp *disjoint* key sets by design
  (documented at `project_trace.py:105-107`), so the merge is purely additive in practice. The
  E2E proof exercised both sites together and produced all four keys with no conflict. The
  refuse-on-conflict guard is correctly reserved for genuine disagreement (re-stamping a
  different value), which is what it should defend against. Make explicit: keep the disjoint-set
  invariant in mind if a future change has both sites write the same key.

### Alternative Not Considered

- **Alternative:** make `normalize_dir` atomic — normalize all sidecars in memory first, and
  only write once every sidecar passes (write-all-or-nothing), eliminating Concern 1's
  partial-write window.
- **Tradeoff:** marginally more memory + a second loop, for a failure mode that already fails
  safe (no `batch.json` written on abort). 
- **Verdict:** current approach is justified for this sprint — the partial-write state is
  unreachable in both production lanes and self-evidently broken (no manifest) if it ever
  occurs. Atomicity would be the right call only if/when the real lane writes provenance
  independently and conflicts become plausible. Noted for that future cycle, not required now.

## Documentation Verification: PASS

- Seam reply brief (`grimoires/loa/discovery/gygax-seam-reply-v1.1.md`) present, taxonomy
  verbatim, `bottleneck` drift flagged, no private/upstream-game references.
- `SKILL.md` updated for the new real-lane State 4.5 + bright-line reconciliation.
- `VENDOR.yaml` header contract honored (files remain Gygax's, pins + git_sha + date updated).
- Vendored contract files carry the v1.1 convention text (difficulty convention is doc-only).
- No new user-facing command added, so no CLAUDE.md change required.

## Complexity Analysis

- `normalize_obj` / `_apply_marker_triage` / `_apply_provenance`: all <25 lines, ≤3 params,
  nesting ≤2. OK.
- `assemble_batch.main` arg-parse loop: small, readable, handles interleaved flags + the
  no-value-at-end edge safely (falls to usage error). OK.
- No duplication, no dead code, no circular deps, stdlib-only rule held.

## Next Steps

Approved for the security audit gate. The three non-blocking concerns and the atomicity
alternative are documented here for the next engineer; none require an iteration. Recommend the
auditor confirm the `--provenance` CLI surface has no injection vector (values flow only into
JSON, never a shell or eval) and that the marker-triage observation-drop cannot be abused to
launder a real verdict (it only fires on the convention-anchored wrapper marker + non-triaged
status).
