# Implementation Report — cycle-007 Sprint 1 (global sprint 23): FR-1 `decision-trace/v1` Emitter

**Sprint:** cycle-007 sprint-1 (global ID 23)
**Branch:** `feature/cycle-007-decision-trace-emitter`
**Date:** 2026-06-26
**Status:** Complete — all acceptance criteria met; 14/14 sprint tests + full suite (17/17) green; closing proof passes.

---

## Executive Summary

Closed the **producer side** of the Arneson→Gygax revealed-strategy seam (G-1). Arneson's simulated
lane now emits a `decision-trace/v1` corpus that Gygax's revealed-strategy lens consumes (exit 0,
`claim_strength: simulation-derived`) — the exact rejection that failed before
(`unknown schema "observed-trace/v1"`) is gone.

The implementation is a deterministic, stdlib-only projection (`emit_decision_trace.py`) modeled on the
existing `project_trace.py`, with a self-check mirroring `validate_sidecar.py` (refuses to write a
corpus that violates the vendored contract → exit 2). Per the SDD's empirically-resolved OQ-1, the sim
log is **chosen-only**, so each record's `offered` equals its `chosen` with an honest
`offered-set-unrecorded` marker — closing the *contract* seam while leaving the *analytic* seam
explicitly for future offered-set capture (RA-1, carried into this report and the doc note).

---

## AC Verification

Each acceptance criterion quoted verbatim from `grimoires/loa/sprint.md` (Sprint 1 block).

1. **AC1 (sprint.md:77-79):** "One sim episode in → N `decision-trace/v1` records out, each carrying
   `schema`, `claim_strength`, `producer.{kind,id,detail,provenance}`, `corpus.{id,game}`, `actor_id`,
   `episode_id`, `t`, `context.segment`, `offered`, `chosen` (PRD FR-1; `sdd.md` §3.1)."
   **✓ Met** — record assembly: `emit_decision_trace.py:307-323` (all 10 top-level fields).
   Concrete evidence: golden corpus
   `domains/agent-systems/resources/fixtures/decision-trace/golden/synthetic-simulated-smoke-dt-run-1-0.json`
   (and `-1.json`) carry every field; test "emitter exits 0 … self-validated"
   (`test-emit-decision-trace.sh:25-26`).

2. **AC2 (sprint.md:80-82):** "Chosen-only honesty: `offered == chosen` with `producer.detail` =
   "offered-set-unrecorded: chosen-only projection …"; `claim_strength: simulation-derived`,
   `producer.kind: simulation` are **hardcoded literals** (NFR-2, NFR-5; `sdd.md` §1.2)."
   **✓ Met** — `offered`/`chosen` both built from the same `action_label`
   (`emit_decision_trace.py:321-322`); `producer.detail` literal at `:57-60`; `claim_strength` and
   `producer.kind` are string literals at `:309` and `:311` (never derived from input).

3. **AC3 (sprint.md:83-84):** "Self-check on write: every record validates against the vendored schema
   (required fields, `additionalProperties:false`, enums); **exit 2** if any record fails (never ship a
   broken corpus)."
   **✓ Met** — `validate_record` (`emit_decision_trace.py:138-253`) hand-encodes the contract;
   `main` validates every record before writing and returns 2 on any violation
   (`emit_decision_trace.py:375-383`). Verified: broken-label fixture → exit 2
   (`test-emit-decision-trace.sh:44-46`).

4. **AC4 (sprint.md:85-86):** "Byte-identical corpus across runs (sorted keys, fixed separators,
   ordering stable by `t`/`seq`; no clock/random) — SM-1 determinism."
   **✓ Met** — `json.dumps(r, indent=2, sort_keys=True)` (`emit_decision_trace.py:345`); no `datetime`
   /`random` imported (`:42-46`). Verified: golden byte-match (`test-emit-decision-trace.sh:29-32`) +
   two-run determinism (`:35-36`).

5. **AC5 (sprint.md:87-88):** "`--blank`/degenerate input (no `agent_turn`/no `action_label`) → **exit
   1** with `ERROR: [emit_decision_trace] …`."
   **✓ Met** — degenerate guard at `emit_decision_trace.py:327-330` (returns None → `main` returns 1).
   Verified: degenerate fixture → exit 1 with the `ERROR: [emit_decision_trace]` prefix
   (`test-emit-decision-trace.sh:39-41`).

6. **AC6 (sprint.md:89):** "Import-grep test proves **zero** `construct-gygax` imports (NFR-1);
   banned-phrase gate green (NFR-7)."
   **✓ Met** — import-grep + no-subprocess + zero-gygax-ref assertions
   (`test-emit-decision-trace.sh:53-62`); banned-copy over the generated corpus (`:65`). All green.

7. **AC7 (sprint.md:90-92):** "**Closing proof (SM-2, informational gate):**
   `npx tsx ../construct-gygax/scripts/lib/trace/strategy.ts <corpus>/` exits 0 with
   `claim_strength: simulation-derived`; the today-failing rejection (`unknown schema
   "observed-trace/v1"`) is gone."
   **✓ Met** — ran `tsx scripts/lib/trace/strategy.ts <golden corpus>` from the gygax sibling: exit 0,
   "revealed 2 decisions", report header `Claim strength: **simulation-derived**`. The
   `observed-trace/v1` rejection no longer occurs. (Informational gate; not wired into CI.)

8. **AC8 (sprint.md:93):** "`vendor-drift-guard.sh` + source↔vendor convergence still green for all four
   files (SM-3)."
   **✓ Met** — drift guard extended to the 4th file (`scripts/ci/vendor-drift-guard.sh:20`); run output:
   all four byte-identical to upstream, all four pins match, source↔vendor convergence OK, exit 0.

---

## Tasks Completed

| Task | Deliverable | Files |
|------|-------------|-------|
| 1.1 | Vendor schema (byte-exact) + wholesale pin bump `3fa6c91→95ccf21` + byte-identity note | `domains/agent-systems/schemas/vendor/decision-trace.v1.schema.json` (new); `VENDOR.yaml:14-38` |
| 1.2 | Extend drift guard to the 4th file (self-pin auto-discovers) | `scripts/ci/vendor-drift-guard.sh:20` |
| 1.3 | `emit_decision_trace.py` — stdlib, deterministic, self-checking projection | `domains/agent-systems/scripts/emit_decision_trace.py` (new, 391 lines) |
| 1.4 | Sim-lane fixture + byte-stable golden corpus (+ 2 negative fixtures) | `resources/fixtures/decision-trace/{sim-episode,degenerate,broken-label}.events.yaml`, `golden/*.json` (new) |
| 1.5 | Test, auto-discovered by `scripts/test.sh` | `domains/agent-systems/scripts/test-emit-decision-trace.sh` (new, 14 checks) |
| 1.6 | Closing proof (run); doc note; `construct.yaml` vendored-contract entry | `domains/agent-systems/docs/emitting-a-decision-trace-corpus.md` (new); `construct.yaml:76-77` |

**Approach:** `emit_decision_trace.py` is a structural twin of `project_trace.py` (same native-sidecar →
vendored-schema projection, exit 0/1/2) with the self-check pattern lifted from `validate_sidecar.py`
(`vendor_selfcheck` + per-block `validate_record`). Chosen-only projection per SDD §1.2: `offered` ==
`chosen` == `[{"type": <action_label>}]`, `producer.detail` honesty flag, `claim_strength`/`producer.kind`
hardcoded.

---

## Technical Highlights

- **Producer-never-judges (NFR-2):** the emitter reshapes; it scores nothing. Inventing an offered set
  the host never presented would be a judgment, so chosen-only stays `offered == chosen`.
- **Claim honesty is structural (NFR-5):** `claim_strength`/`producer.kind` are literals; the
  `validate_record` claim-binding check (`emit_decision_trace.py:241-249`) rejects any sim record tagged
  `real-agent-observed`.
- **Contract pinned read-only (NFR-4):** the vendored schema is a byte-exact copy
  (sha `83d6a69f…dab02`); `vendor_selfcheck` refuses (exit 2) on pin drift.
- **Wholesale pin bump is byte-neutral:** the 3 pre-existing vendored files are byte-identical at
  `3fa6c91` and `95ccf21` (drift guard confirms), so the bump changed no bytes and needed no validator
  revisit — recorded in `VENDOR.yaml:14-20`.

---

## Testing Summary

- **New test:** `test-emit-decision-trace.sh` — 14 checks, all pass (golden byte-match ×2, determinism,
  exit 1, exit 2 ×2, claim honesty ×2, import/shell-out/gygax ×3, banned-copy).
- **Full suite:** `bash scripts/test.sh` → **17/17 test scripts pass** (was 16; the new test is
  auto-discovered with zero wiring).
- **Drift guard:** `bash scripts/ci/vendor-drift-guard.sh` → exit 0 (4 files byte-identical + 4 pins +
  source convergence).
- **Closing proof:** Gygax lens on the golden corpus → exit 0, `simulation-derived`.
- **Floor:** `python3 -m py_compile emit_decision_trace.py` clean.

**Reproduce:**
```bash
bash domains/agent-systems/scripts/test-emit-decision-trace.sh
bash scripts/ci/vendor-drift-guard.sh
bash scripts/test.sh
# closing proof (from the gygax sibling checkout):
npx tsx scripts/lib/trace/strategy.ts /Users/mandy/construct-arneson/domains/agent-systems/resources/fixtures/decision-trace/golden
```

---

## Known Limitations

- **Chosen-only corpus is analytically empty (RA-1, by design).** The contract seam is closed (the lens
  *consumes* the corpus), but with `offered == chosen` there is no revealed *preference* — the lens
  reports 100% pick-rate, "within noise, no direction asserted." Analytic value requires offered-set
  capture (a future additive `agent_turn.offered_labels` field), explicitly deferred. Flagged in the doc
  note and must carry into the PR.
- **`ruff`/`mypy` not run** — not installed in this environment; CI does not run them either (Theme B,
  deferred). `py_compile` is the floor that ran.
- **Closing proof is informational** — depends on the gygax sibling's Node toolchain; not a hard CI leg
  (matches SDD §1.2 / sprint AC7).
- **Pre-existing hygiene, not fixed (out of scope, surgical):** `construct.yaml` still omits
  `signal-taxonomy.v1.schema.json` from `vendored_contracts` (the drift guard already covers it). Noted
  per SDD §3.2 ("optional hygiene, mention in PR"); not touched this sprint.

---

## Verification Steps (for reviewer)

1. `bash scripts/test.sh` → expect `OK: all 17 test script(s) passed`.
2. `bash scripts/ci/vendor-drift-guard.sh` → expect exit 0, decision-trace listed among the 4 files.
3. Inspect a golden record (`…/golden/synthetic-simulated-smoke-dt-run-1-0.json`) — confirm
   `claim_strength: simulation-derived`, `offered == chosen`, honest `producer.detail`.
4. (Optional) run the closing proof against the gygax sibling — expect exit 0, `simulation-derived`.
5. Confirm zero `construct-gygax` imports in `emit_decision_trace.py`.
