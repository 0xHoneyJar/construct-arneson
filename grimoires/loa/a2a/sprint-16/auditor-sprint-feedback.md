# Security Audit — Sprint 1 (global #16): observed-trace v1.1 Adoption + Seam Reply

**Verdict:** APPROVED - LETS FUCKING GO
**Auditor:** Paranoid Cypherpunk Auditor · **Date:** 2026-06-13 · **Commit:** `9b798cb`

## Scope

Audited the full diff of commit `9b798cb` (12 source/test files + vendored contract + docs).
Focus per the senior lead's hand-off: (1) the new `--provenance` CLI injection surface, (2)
whether the marker-triage observation-drop can launder a real verdict. Plus a standard paranoid
pass: input validation, path traversal, secrets, data integrity, and abuse of the new mutation
path.

## Reviewer-Flagged Surfaces — Both Clear

### 1. `--provenance` injection vector — NONE

`grep` for `subprocess|os.system|eval|exec|shell|Popen|popen` across `normalize_sidecars.py`
and `assemble_batch.py` returns nothing. Provenance values flow exactly one way:
`_parse_provenance_args` → dict → `_apply_provenance` merge → `json.dumps`. No value ever
reaches a shell, an `eval`, a subprocess argv, or a path component. Downstream,
`validate_sidecar.py:122-130` enforces the 4-key allowlist (`additionalProperties`-equivalent
rejection of unknown keys) and string-typing of every value. A malicious producer cannot stuff
executable content, extra keys, or non-string payloads through this surface. **Cleared.**

### 2. Marker-triage cannot launder a real verdict — CONFIRMED SAFE

`_apply_marker_triage` (`normalize_sidecars.py:48-67`) fires only when BOTH hold: status is NOT
already a triaged status (`runner-error`/`timeout`/`infra-failure`), AND narration matches the
convention-anchored `INFRA_MARKER = ERROR: \[[A-Za-z0-9_-]*(?:agent|wrapper)\]`. Three reasons
this is not a laundering surface:

- **Direction is conservative.** The triage *excludes* a run from ratios/margins (it becomes a
  non-run), never promotes it to a pass. An attacker forging a marker downgrades their own run
  to "didn't count" — they cannot turn a `hacked` into a `fixed`.
- **No new surface.** The byte-identical regex already drives the pre-v1.1 marker fallback in
  `sweep_report.py:55` and the `validate_batch.py` honesty-warn. v1.1 promotes the same triage
  to status level at assembly; the *outcome* (excluded, surfaced in its own column) is unchanged
  and is the bilaterally-agreed contract behavior (vendored batch doc, "marker wins").
- **Anchor holds.** The `-agent`/`-wrapper` suffix anchor means arbitrary agent prose like
  `ERROR: [compiler] segfault` does NOT trigger triage — verified by the existing negative test
  (`test-validate-batch.sh` "non-conforming ERROR string ... does NOT triage") and the new
  `test-normalize-sidecars.sh` "non-conforming prose: status stays completed".
- **Observation-drop is contract-mandated.** Dropping `observation` on `infra-failure` is
  required (an `infra-failure` record MUST NOT carry a grade); it is not editing a grade, and it
  only fires on the marker path. In the sim lane the host never writes an observation anyway.

**Residual (accepted, pre-existing):** an agent that can write its own wrapper-conforming stderr
marker can get its run excluded-not-graded. This is the documented, bilateral marker convention —
not introduced by this sprint — and it fails safe (exclusion, never a false pass). No action.

## Standard Paranoid Pass

| Check | Result |
|-------|--------|
| **Secrets in diff** | None. `grep` for password/secret/key/token/PRIVATE/AKIA/ghp_/sk- on `+` lines is empty. |
| **Input validation** | `_apply_marker_triage` guards `run` is a dict + `narration` is a str before use. `_apply_provenance` guards `producer` is a dict and `existing` provenance is dict-or-None (raises, never crashes). `_parse_provenance_args` rejects non-contract keys (exit 1). |
| **Path traversal (CWE-22)** | `normalize_dir` globs `*.json` in an operator-supplied/assembly-controlled dir; no user-data-driven path construction. (Contrast `project_trace.py`, which handles untrusted `state_path` and retains its existing containment guards — unchanged here.) |
| **Source-data integrity** | Marker-wins observation-drop mutates only the **assembled copy** (`assemble_batch.py` copies at :82, normalizes at :91); the source projected trace in `traces/` is never touched. Confirmed by data flow. |
| **Provenance integrity** | Refuse-on-conflict (exit 1) prevents silent overwrite of a differing value; stamping is idempotent. A self-describing batch cannot be made to disagree with itself. |
| **Vendored contract tamper** | Both vendored files byte-identical to gygax upstream (drift guard exit 0); `validate_sidecar.py` vendor self-check (sha256-vs-pin, refuse-on-drift) is intact and unchanged. |
| **allOf integrity** | The non-completed-no-observation rule was correctly extended to include `infra-failure`; the marker-wins drop keeps records on the right side of it (tested both directions). |
| **OWASP A03/A08** | No injection (A03) and no integrity-tampering (A08) surface introduced. |

## Test Integrity

12/12 suites green; the 3 new accept + 3 new reject validator cases, the 21-case normalizer
suite, and the consumer-triage cases all assert behavior (not just exit codes). No pre-existing
test expectation was weakened — the warn-suppression is gated strictly on
`status == "infra-failure"`, so pre-v1.1 marker-only batches still warn (regression-protected by
the unchanged existing cases).

## Decision

No CRITICAL, HIGH, MEDIUM, or LOW findings. The change is additive, well-guarded, and the two
flagged surfaces are confirmed safe. The senior lead's three non-blocking concerns
(partial-normalize-on-conflict, enumerate-vs-not-completed, mixed formatting) are accurate, fail
safe, and do not rise to security findings.

**APPROVED - LETS FUCKING GO**
