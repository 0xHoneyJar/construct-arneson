# Implementation Report — Sprint 1 (global #16): observed-trace v1.1 Adoption + Seam Reply

**Cycle:** cycle-003 (`seam-alignment-v1.1-adoption`) · **Date:** 2026-06-13 · **Branch:** `feature/seam-alignment-v1.1-20260611`
**Source:** Gygax cycle-009 seam brief (`construct-gygax/grimoires/gygax/designs/seam-alignment-v1.1-brief.md` @ gygax `64f6d75`)

## Executive Summary

Adopted Gygax's additive `observed-trace/v1.1` revision on the Arneson side and answered the
brief's three open asks. All changes are additive: 12/12 test suites green (11 pre-existing
unchanged + 1 new), every v1.0 fixture still validates, and the `vendor-drift-guard.sh` leg is
green against the gygax sibling. No application code was written outside the planned tasks.

Six tasks, all complete:
- **1.1** Re-vendored both contract files byte-for-byte at gygax `64f6d75`; VENDOR.yaml pins updated.
- **1.2** `validate_sidecar.py` accepts `infra-failure` + optional `producer.provenance` (4 keys, unknown rejected).
- **1.3** New `normalize_sidecars.py` (module + CLI): assembly-time marker→`infra-failure` triage + provenance stamping; wired into `assemble_batch.py`, `project_trace.py`, and the `/playout` real-lane SKILL.
- **1.4** `sweep_report.py` + `validate_batch.py` triage the new status; redundant marker-warn suppressed when status is already explicit.
- **1.5** Reply brief on disk (taxonomy, check-dominance position, OQ-B preference).
- **1.E2E** Full hermetic pipeline proof + additivity regression + drift guard.

## AC Verification

1. **"`shasum -a 256` of both vendored files matches VENDOR.yaml pins AND upstream gygax bytes (`df3f789b…` schema, `d04dabfa…` batch doc); `scripts/ci/vendor-drift-guard.sh` exits 0 against the sibling checkout"**
   - ✓ Met — pins at `VENDOR.yaml:22,25` (`df3f789b40fa…`, `d04dabfaca79…`); `git_sha: 64f6d75…` at `VENDOR.yaml:16`. Drift guard exits 0 against `/Users/mandy/construct-gygax` (E2E step, "byte-identical").

2. **"`validate_sidecar.py` exits 0 on: a v1.0 sidecar (regression), an `infra-failure` sidecar without observation, a sidecar with full 4-key `producer.provenance`"**
   - ✓ Met — `test-validate-sidecar.sh` cases "infra-failure without observation accepted", "full 4-key producer.provenance accepted" (both exit 0); v1.0 regression via 37 committed fixtures all `OK` (E2E additivity step).

3. **"`validate_sidecar.py` exits 2 on: unknown `producer.provenance` key, non-string provenance value, `infra-failure` + `observation` present"**
   - ✓ Met — `test-validate-sidecar.sh:` "unknown provenance key rejected", "non-string provenance value rejected", "infra-failure with observation rejected" (all exit 2). Logic at `validate_sidecar.py:122-130` (provenance block) + `validate_sidecar.py:231-232` (allOf extension).

4. **"A sidecar with `status: "completed"` + narration matching `ERROR: \[…(?:agent|wrapper)\]` is rewritten at assembly to `status: "infra-failure"` with observation removed (marker wins); a sidecar with non-conforming `ERROR: [x]` prose is NOT rewritten"**
   - ✓ Met — `normalize_sidecars.py:_apply_marker_triage` (`normalize_sidecars.py:54-67`); `test-normalize-sidecars.sh` "marker-wins: status → infra-failure" + "observation removed" + negative "non-conforming prose: status stays completed".

5. **"Sidecars with `status` already `runner-error`/`timeout`/`infra-failure` pass through assembly unchanged (status is first in triage order)"**
   - ✓ Met — `PRESERVED_STATUSES` guard at `normalize_sidecars.py:60`; `test-normalize-sidecars.sh` "status-first: {runner-error,timeout,infra-failure} passes through unchanged" (3 cases, marker present but status wins).

6. **"Provenance stamping writes only the 4 contract keys; refuses (exit 1) to overwrite an existing key with a *different* value; idempotent on re-run"**
   - ✓ Met — `_apply_provenance` (`normalize_sidecars.py:70-93`) + `_parse_provenance_args` key restriction (`normalize_sidecars.py:96-108`); tests "first stamp succeeds", "idempotent re-run unchanged", "conflicting value refused (exit 1)", "non-contract provenance key rejected".

7. **"`sweep_report.py` counts a `status: "infra-failure"` sidecar in the `infra` column (excluded from ratios)"**
   - ✓ Met — `sweep_report.py:53` (`triage()` status set += `infra-failure`); `test-sweep-report.sh` "v1.1 infra-failure status lands in infra column".

8. **"Reply brief quotes the 9-value taxonomy verbatim from `session-events-base.schema.yaml:84` and flags `bottleneck` (digest-ttrpg.schema.yaml:81) as digest-side drift"**
   - ✓ Met — `grimoires/loa/discovery/gygax-seam-reply-v1.1.md` §1 quotes the 9 values verbatim and flags `bottleneck` as digest-side drift "not part of the signal taxonomy". Verified by grep in E2E step.

9. **"All 10 existing `domains/agent-systems/scripts/test-*.sh` suites pass unchanged"**
   - ✓ Met (exceeded) — 11 pre-existing suites pass unchanged + 1 new (`test-normalize-sidecars.sh`); full run: check-payoff-dominance 7, discover-engine 10, dungeon-referee 6, normalize-sidecars 21, ollama-agent 16, party-wrapper 8, scaffold-playtest 14, sim-pipeline 19, sweep-report 11, validate-batch 22, validate-scenario 16, validate-sidecar 20.

## Tasks Completed

| Task | Files | Notes |
|------|-------|-------|
| 1.1 | `schemas/vendor/observed-trace.v1.schema.json`, `observed-trace-batch.v1.md`, `VENDOR.yaml` | Byte-exact copy from gygax `64f6d75`; pins + git_sha + vendored_at updated. Files remain GYGAX'S — never edited. |
| 1.2 | `scripts/validate_sidecar.py` (`+infra-failure`, `PROVENANCE_KEYS`, provenance block, allOf extension), `test-validate-sidecar.sh` (+6 cases) | One helper per block per the validator-structure contract. |
| 1.3 | `scripts/normalize_sidecars.py` (NEW), `assemble_batch.py`, `project_trace.py`, `skills/playout/SKILL.md`, `test-normalize-sidecars.sh` (NEW, 21 cases) | Marker-wins touches only the assembled copy; sim lane stamps `{model_id, construct_sha}` from preamble. |
| 1.4 | `scripts/sweep_report.py`, `validate_batch.py`, `test-sweep-report.sh` (+1), `test-validate-batch.sh` (+1) | Warn suppressed only when status already `infra-failure`; pre-v1.1 marker-only batches still warn. |
| 1.5 | `grimoires/loa/discovery/gygax-seam-reply-v1.1.md` (NEW) | Three positions; no private-game references. |

## Technical Highlights

- **Single normalization implementation**, called from `assemble_batch.py` (sim lane) AND documented as the real/sweep-lane State 4.5 step (`SKILL.md`) — not two parallel code paths.
- **Bright-line integrity preserved**: `SKILL.md` State 5 now distinguishes contract-sanctioned v1.1 normalization (stamps our own triage convention + provenance) from the still-forbidden "edit a sidecar to clear a conformance failure". The marker-wins observation-drop and the additive `producer.provenance` are each cross-referenced against the relevant "what you never do" bright line.
- **Refuse-on-conflict** for provenance: stamping is idempotent but aborts loudly (exit 1) on a differing pre-existing value — a self-describing batch must not disagree with itself.

## Testing Summary

Run all suites: `cd domains/agent-systems/scripts && for t in test-*.sh; do ./"$t"; done`
Hermetic E2E proof (project → inject marker+observation → materialize → assemble `--provenance` → assert infra-failure/no-observation/4-key provenance → validate → sweep): passed end-to-end against the re-vendored pin.

## Known Limitations

- Sub-integer payoff crossings (brief §2 sampling difference) remain out of scope; the reply brief records the commitment to flag any such fixture if authored.
- Real-lane State 4.5 is documented in `SKILL.md` (the real lane is engine-driven, exercised live), not covered by a hermetic shell test — the sim lane exercises the same `normalize_sidecars` module end-to-end in `test-sim-pipeline.sh`'s assembly path and the new E2E proof.

## Verification Steps for Reviewer

1. `cd domains/agent-systems/scripts && for t in test-*.sh; do ./"$t" | tail -1; done` → all `0 failed`.
2. `ARNESON_GYGAX_ROOT=/Users/mandy/construct-gygax ./scripts/ci/vendor-drift-guard.sh` → exit 0.
3. `shasum -a 256 domains/agent-systems/schemas/vendor/observed-trace.v1.schema.json` → `df3f789b40fa…`.
4. Read `grimoires/loa/discovery/gygax-seam-reply-v1.1.md` — confirm taxonomy verbatim + three positions + no private-game references.
