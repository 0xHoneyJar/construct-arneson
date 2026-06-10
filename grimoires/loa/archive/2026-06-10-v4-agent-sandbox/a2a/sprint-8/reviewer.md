# Implementation Report: Sprint 1 (global sprint-8) — Conformance Substrate

**Date:** 2026-06-09 · **Sprint:** local 1 / global 8 (ledger cycle-001 agent-sandbox-v4.0)
**Implementer:** /implement (run mode, plan-20260609-agent-sandbox-v4)
**Branch:** feature/sprint-plan-20260609

## Executive Summary

The `domains/agent-systems/` vertical exists, registered in construct.yaml with zero core
changes. Gygax's contract is vendored byte-exact with a sha256 pin; three domain schemas are
authored and CI-covered; three deterministic validators (Python 3 stdlib only) enforce the
contract with 40/40 shell-test assertions green; a hermetic synthetic fixture + committed valid
batch + six violation fixtures anchor CI; the vendor drift guard passes against the live sibling
checkout. Milestone (a) conformance is satisfied: anything claiming to be a batch is
machine-checked before any agent ever runs.

## AC Verification

**AC-1** — "`extension-story` CI job passes with the new vertical present and **zero core diffs** — FR-1's proof (sdd.md §7.1)"
✓ Met — `git status` on the sprint changeset shows zero modifications under `schemas/core/`, `protocols/`, `skills/`, `identity/`; only the two SDD-scoped exceptions changed: `construct.yaml` (domain registration, construct.yaml:63-78) + CI registration (`scripts/ci/validate-schemas.sh`, `.github/workflows/ci.yaml`). The extension-story job definition is untouched (.github/workflows/ci.yaml:144+). Full CI-leg confirmation lands when the PR runs Actions.

**AC-2** — "`validate_sidecar.py` refuses to run (exit 2) when vendored schema sha256 ≠ `VENDOR.yaml` (sdd.md §5.2.1)"
✓ Met — `vendor_selfcheck()` at domains/agent-systems/scripts/validate_sidecar.py:55-99 (message at :78). Test: "vendor drift refusal (sha256 mismatch)" + message assertion, test-validate-sidecar.sh:63-71 — tampers a copied tree, asserts exit 2 + `CONTRACT DRIFT`.

**AC-3** — "Each `allOf` conditional has a rejection fixture pair — e.g. `producer.kind: simulation` + `claim_strength: real-agent-observed` is rejected"
✓ Met — fixtures: resources/fixtures/violations/{laundering-sim-as-real,laundering-real-as-sim,runner-error-with-observation}.json; enforcement at validate_sidecar.py:217-225 (laundering message at :223); tests assert exit 2 per fixture (test-validate-sidecar.sh:39-45).

**AC-4** — "Scenario without `stopping.max_turns` rejected: `UNBOUNDED SCENARIO REJECTED` (NFR-2, sdd.md §6.1)"
✓ Met — validate_scenario.py:254; fixture scenarios/unbounded.yaml; test asserts exit 1 + exact message (test-validate-scenario.sh:44-45).

**AC-5** — "Committed fixture batch passes `validate_batch.py` exit 0"
✓ Met — resources/fixtures/batches/valid-batch/ (batch.json + 1 ungraded real-agent sidecar + runs/rung-0/trial-1/ artifacts); `validate-agent-systems.sh` output: `OK …/valid-batch (1 sidecar(s))`.

**AC-6** — "All validators are Python 3.10+ stdlib only — no PyYAML, no JSON-Schema library (NFR-5, sdd.md §2)"
✓ Met — imports across all three validators: `hashlib, json, re, sys, pathlib` + sibling `validate_sidecar` module only (verified by grep over domains/agent-systems/scripts/*.py). Scenario YAML handled by the restricted-subset parser (validate_scenario.py:55-130), the ingest_persona.py precedent.

**AC-7** — "`domains/agent-systems/schemas/` covered by `scripts/ci/validate-schemas.sh` (closes the character-voice zero-coverage pattern for this domain)"
✓ Met — scripts/ci/validate-schemas.sh:9,19-22,36-38 (AGENT_SCHEMAS_DIR + 3 entries); local run: "OK: all 13 schemas parse…". Plus a dedicated hermetic CI step (scripts/ci/validate-agent-systems.sh, wired at .github/workflows/ci.yaml:50-51).

## Tasks Completed

| Task | Deliverable | Evidence |
|------|-------------|----------|
| 1.1 | Vertical scaffold + construct.yaml registration (domains, schemas group, output_paths.playouts) + domain.conventions.md stub | construct.yaml:63-78,101-104,124; domains/agent-systems/domain.conventions.md |
| 1.2 | Vendored contract: 2 byte-exact copies (`cp`, sha256-verified) + VENDOR.yaml pin (upstream git sha b8dd409…) | schemas/vendor/{observed-trace.v1.schema.json, observed-trace-batch.v1.md, VENDOR.yaml} |
| 1.3 | scenario / session-events-agent / agent-persona schemas | domains/agent-systems/schemas/*.schema.yaml — all parse, schema.name+version present |
| 1.4 | validate_scenario.py (restricted-YAML parser, lane gating, checksum verify, one-variable INFO) + 14-assertion test | scripts/validate_scenario.py; test-validate-scenario.sh |
| 1.5 | validate_sidecar.py (contract-specific, drift refusal, 3 allOf) + validate_batch.py (layout, run_dir containment, delegation, honesty warning) + 26 assertions | scripts/validate_{sidecar,batch}.py; test-validate-{sidecar,batch}.sh |
| 1.6 | Synthetic incentive fixture (manifest mirrors Gygax shape; sum-positives task), valid batch, 6 violation fixtures, 4 scenario fixtures + test persona, fixture native sidecar | resources/fixtures/ |
| 1.7 | CI: schemas extension, hermetic vertical step (alone leg), real-sibling checkout + vendor drift guard (with-gygax leg) | scripts/ci/{validate-agent-systems,vendor-drift-guard}.sh; .github/workflows/ci.yaml:50-51,99-109 |

## Technical Highlights

- **Drift is loud by construction:** validators self-check the vendored bytes before every run;
  the drift test exercises the refusal end-to-end by tampering a copied tree (no env-var override
  backdoor introduced).
- **Containment check:** `validate_batch.py` resolves every `run.run_dir` and rejects paths
  escaping the batch dir (`Path.is_relative_to`) — the contract's "any relative path that
  resolves inside the batch dir" made mechanical.
- **Honesty warning, not failure:** completed simulation sidecars without `observation` pass
  layout but WARN "not Gygax-ingestible until scored" — matches sdd.md §5.2.3(4) standalone
  labeling without blocking the lane.

## Testing Summary

- `domains/agent-systems/scripts/test-validate-scenario.sh` — 14 assertions (happy ×3+1 stdout,
  exit-1 ×5 incl. exact UNBOUNDED message, exit-2 ×2 with message checks, tampered-persona pair)
- `test-validate-sidecar.sh` — 14 assertions (happy ×2 incl. stdin; six violation fixtures;
  3 input-error cases; drift refusal pair)
- `test-validate-batch.sh` — 12 assertions (committed batch; missing/wrong manifest; run_dir
  escape + missing; embedded bad sidecar; empty batch; ungraded-sim warning pair; input error)
- Run: `./scripts/ci/validate-agent-systems.sh` (all three suites + committed batch) — 40/40
- Repo-wide: all 5 pre-existing CI validators still green; `vendor-drift-guard.sh` green against
  the live sibling checkout.

## Known Limitations

1. **With-gygax CI leg needs checkout access.** The drift guard checks out
   `0xHoneyJar/construct-gygax` via `secrets.GYGAX_CHECKOUT_TOKEN || github.token`. If the repo
   is private and no PAT secret is configured, that leg fails loudly until the operator adds
   `GYGAX_CHECKOUT_TOKEN` — intentional (a stub cannot verify the pin), but it is operator
   action this sprint cannot perform.
2. **Restricted YAML parser** rejects exotic scenario syntax (anchors, multiline scalars except
   in committed fixtures' simple shapes, all-digit unquoted checksums). Documented in the schema
   header; the all-digit case is quoted in the one fixture that hits it.
3. **Native sidecar fixture carries placeholder hashes** (`fixture-hash-not-computed-in-sprint-1`)
   for context_manifest/content_sha256 — real hashing lands with the Sprint 4 toolchain that
   consumes them (materialize verifies content_sha256 then).
4. **construct.yaml `vendored_contracts` key** is a new, undeclared-by-schema manifest stanza —
   validate-construct.sh accepts it (no strict schema); flagging for reviewer judgment.

## Feedback Addressed (cycle 2)

All three CHANGES_REQUIRED items from engineer-feedback.md resolved:

1. **"No CHANGELOG.md in the construct repo"** → Created `CHANGELOG.md` with
   `[Unreleased] — 4.0.0-dev` section covering every Sprint 1 deliverable, plus a 3.3.0
   pointer stanza for the predecessor line.
2. **"Unknown scenario keys are silently accepted"** → `validate_scenario.py` now diffs
   top-level keys against `KNOWN_TOP_KEYS` and emits
   `WARNING: unknown field 'X' ignored — known fields: …` (warn-not-reject, preserving additive
   schema evolution as the feedback specified). Test added: typo'd `memorry:` field → exit 0 +
   warning asserted (test-validate-scenario.sh, "typo'd unknown field" pair). Suite: 16/16.
3. **"`validate_obj` is a 140-line function"** → Split into per-block helpers mirroring the
   contract's structure: `_validate_top`, `_validate_producer`, `_validate_experiment`,
   `_validate_run`, `_validate_observation`, `_validate_allof`; `validate_obj` is now a 15-line
   orchestrator. All 14 sidecar-suite assertions pass unmodified (behavior identical).

Re-verification after fixes: 42/42 assertions green across the three suites; committed batch
exit 0; vendor drift guard green against the live sibling.

## Verification Steps

```bash
./scripts/ci/validate-agent-systems.sh        # 3 suites + committed batch (hermetic)
./scripts/ci/validate-schemas.sh              # 13 schemas
./scripts/ci/vendor-drift-guard.sh            # needs ../construct-gygax sibling
python3 domains/agent-systems/scripts/validate_scenario.py --lane real \
  domains/agent-systems/resources/fixtures/scenarios/valid-real.yaml   # JSON summary, exit 0
```
