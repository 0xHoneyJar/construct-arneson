# Sprint Plan: Simulation Fidelity Gap Report

**Version:** 1.0
**Date:** 2026-06-15
**Author:** Sprint Planner Agent
**PRD Reference:** grimoires/loa/prd.md
**SDD Reference:** grimoires/loa/sdd.md
**Cycle:** cycle-004 (`simulation-fidelity-gap-report`)
**Global sprint range:** 18–21

---

## Executive Summary

This cycle ships a diagnostic — `gap_report.py` — that pairs a simulated-lane playout with its real graded batch and tabulates their divergence using **arithmetic and quoted labels only**. The sprint backbone follows SDD §8 Development Phases (R1/R2 already resolved against the codebase). Four sprints: (1) sim-lane diffability + contracts, (2) the `gap_report.py` core, (3) the skill + enablers + the test gates, (4) cycle hygiene.

All five sprint-plan open questions (OQ-1…OQ-5) are **resolved** and baked into the task definitions below — they are not re-asked.

**Total Sprints:** 4 (global 18, 19, 20, 21)
**Sprint Duration:** 2.5 days each
**Execution path:** `/run sprint-plan` (implement → review → audit per sprint). No implementation happens in this plan.

---

## Resolved Open Questions (baked into tasks)

| OQ | Resolution | Lands in |
|----|------------|----------|
| OQ-1 | **Post-pass script.** A standalone `summarize_playout.py` reads the committed native `session-events-agent` sidecar and emits `playout-summary.v1.json`. It does **not** modify the live playout host serializer. Deterministic + testable on fixtures without running a persona. (Promotable to host-emit later; out of scope now.) | Sprint 18 (T18.2) |
| OQ-2 | **Shared `triage_lib.py`.** Extract triage / `INFRA_MARKER` logic out of `sweep_report.py` into a shared module; both `sweep_report.py` and `gap_report.py` import it. Existing `test-sweep-report.sh` must still pass byte-equal (guards the extraction). | Sprint 19 (T19.1) |
| OQ-3 | **Scoped lint.** ruff+mypy gate applies to `gap_report.py` + `summarize_playout.py` + `triage_lib.py` + their imports only. Pre-existing sibling findings get **scoped ignores**, not refactors. Refines PRD SM-6 from "whole dir" to "scoped". | Sprint 20 (T20.4) |
| OQ-4 | **Complement.** `scripts/test.sh` aggregates / co-exists with the existing `scripts/ci/*` legs; does **not** supersede them. | Sprint 20 (T20.3) |
| OQ-5 | **Scenario-scoped `move-map.yaml`.** One map per scenario; `scenario_id` field present. | Sprint 18 (T18.3) |

---

## Sprint Overview

| Sprint | Global | Theme | Scope | Key Deliverables | Dependencies |
|--------|--------|-------|-------|------------------|--------------|
| 1 | 18 | Sim-lane diffability + contracts | MEDIUM (5) | `playout-summary.v1.schema.json`, `summarize_playout.py`, `move-map.yaml` + schema, synthetic fixture pair + golden | None |
| 2 | 19 | `gap_report.py` core | LARGE (7) | `triage_lib.py` extraction, D1, D2, provenance+framing render, pairing refusal, output write, read-only/arithmetic audit | Sprint 18 |
| 3 | 20 | Skill + enablers + gates | MEDIUM (6) | `gap-report` SKILL.md, `test-gap-report.sh`, `scripts/test.sh`, `pyproject.toml`, real smoke, E2E goal validation | Sprint 19 |
| 4 | 21 | Cycle hygiene | SMALL (2) | Ledger/NOTES finalization, archive confirmation | Sprint 20 |

---

## Sprint 18 (cycle-004 sprint-1): Sim-lane Diffability + Contracts

**Duration:** 2.5 days
**Scope:** MEDIUM (5 tasks)

### Sprint Goal
Give the simulated lane a deterministic, diffable structure and the contracts the report depends on — so `gap_report.py` has well-defined, fixture-producible inputs.

> From sdd.md §8 Phase 1: "Sim-lane diffability + contracts (R1/R2 foundation)" (sdd.md:L691)

### Deliverables
- [ ] `domains/agent-systems/schemas/playout-summary.v1.schema.json` — Arneson-owned, additive, NOT vendored (FR-1, R1)
- [ ] `domains/agent-systems/scripts/summarize_playout.py` — post-pass that reads the native `session-events-agent` sidecar and emits `playout-summary.v1.json` (OQ-1, R1)
- [ ] `domains/agent-systems/move-map.yaml` + a documented `move-map/v1` schema (R2, OQ-5)
- [ ] `domains/agent-systems/resources/fixtures/gap-report/` deterministic sim+real fixture pair + `gap-report.golden.md` target (SM-1 scaffolding)

### Acceptance Criteria
- [ ] `playout-summary.v1.schema.json` validates the §3.1 shape: `schema="playout-summary/v1"`, `lane="simulated"`, `producer.kind`/`claim_strength`, `trials[].action_labels` (slugs `^[a-z0-9-]+$`), `trials[].outcome_signal` ∈ closed `OUTCOME_SIGNAL` set, `trials[].stop_reason` (sdd.md §3.1, §3.5)
- [ ] `summarize_playout.py` is **deterministic**: same native sidecar → byte-identical `playout-summary.v1.json` (stable ordering); runs without invoking a persona host
- [ ] `summarize_playout.py` does NOT modify, write to, or re-run the live playout host serializer (OQ-1 boundary)
- [ ] `summarize_playout.py` is stdlib + vendored `restricted_yaml` only; imports nothing from `construct-gygax` (NFR-1, NFR-2)
- [ ] `move-map.yaml` carries `schema: move-map/v1` and a `scenario_id` field (scenario-scoped, OQ-5); entries follow §3.3 (`canonical`, `sim_labels`, `real_evidence`)
- [ ] Synthetic fixture pair pins the **same** `scenario_sha256` on both sim summary and real record; exercises all three D2 sets (a shared move, a sim-only raw label, a real-only move) and ≥2 verdict classes in D1 (sdd.md §7.2)

### Technical Tasks
- [ ] T18.1: Author `playout-summary.v1.schema.json` (Draft 2020-12, additive-only policy note in-file) per SDD §3.1 → **[SM-1, G-4]**
- [ ] T18.2: Implement `summarize_playout.py` — read committed native `session-events-agent` sidecar, project `agent_turn` action labels + `trial_end` → `outcome_signal`/`stop_reason`, emit `playout-summary.v1.json`; deterministic ordering; no host-serializer edit (OQ-1) → **[SM-1, G-4]**
- [ ] T18.3: Author `move-map.yaml` (scenario-scoped, OQ-5) + a documented `move-map/v1` schema; encode the `real_evidence` recognizer fields (`artifact_path`+`artifact_status`, `anomaly_note_present`) per SDD §3.3 → **[SM-1]**
- [ ] T18.4: Build the synthetic deterministic fixture pair under `resources/fixtures/gap-report/` (sim summary + minimal graded `observed-trace/v1` batch with `observation.classification` filled + the move-map), same `scenario_sha256`, covering all D2 sets + ≥2 D1 classes → **[SM-1]**
- [ ] T18.5: Establish the `gap-report.golden.md` expected-body target from the fixture (byte-stable goal; finalized against `gap_report.py` output in Sprint 19) → **[SM-1]**

### Dependencies
- None (first sprint of the cycle). Reads existing vendored contract + native-sidecar fixture as read-only references.

### Security Considerations
- **Trust boundaries:** native `session-events-agent` sidecar is Arneson-produced; the real graded batch is Gygax-produced and consumed read-only. `summarize_playout.py` reads the native sidecar only — it never reads or writes the real batch.
- **External dependencies:** NONE added. Runtime stays stdlib + vendored `restricted_yaml` (NFR-1).
- **Sensitive data:** none. Fixtures are synthetic.
- **Vendored contract:** `schemas/vendor/*` is NOT touched; `playout-summary.v1.schema.json` is a separate Arneson-owned schema (NFR-7).

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Native sidecar field shape drifts from `summarize_playout.py` assumptions | Med | Med | Pin the projection against the committed `native-sidecar.events.yaml` fixture; the deterministic fixture is the gate |
| Outcome-signal vocabulary too narrow for real native data | Low | Low | `OUTCOME_SIGNAL` is closed (SDD §3.5); unmapped stop_reasons fail loud rather than silently mis-tag |

### Success Metrics
- `summarize_playout.py` produces byte-identical `playout-summary.v1.json` across two runs on the same fixture (determinism)
- Synthetic fixture pair validates against both schemas and pins one shared `scenario_sha256`

---

## Sprint 19 (cycle-004 sprint-2): gap_report.py Core

**Duration:** 2.5 days
**Scope:** LARGE (7 tasks)

### Sprint Goal
Implement the core `gap_report.py` — pairing refusal, D1 outcome divergence, D2 action-set divergence, provenance+framing render — arithmetic and quoted labels only, read-only on the real batch.

> From sdd.md §8 Phase 2: "gap_report.py (core)" (sdd.md:L698)

### Deliverables
- [ ] `domains/agent-systems/scripts/triage_lib.py` — shared triage / `INFRA_MARKER` module extracted from `sweep_report.py` (OQ-2)
- [ ] `sweep_report.py` refactored to import `triage_lib.py`; `test-sweep-report.sh` still passes **byte-equal** (guards the extraction)
- [ ] `gap_report.py` with D1, D2, provenance, framing, pairing refusal (exit 2), output write to `gap-reports/`
- [ ] Read-only + arithmetic-only audit pass documented (no classifier, no writes to batch)

### Acceptance Criteria
- [ ] `triage_lib.py` exposes `triage`, `_sidecar_paths`, `INFRA_MARKER`; `sweep_report.py` imports them; `test-sweep-report.sh` output is byte-identical to pre-extraction (OQ-2 guard)
- [ ] D1 tabulates real verdict-class counts (`fixed`/`hacked`/`failed`/`infra`/`ungraded`) from `observation.classification` via `triage_lib`, **verbatim/quoted**, beside sim `outcome_signal` tags as separate rows (FR-3, sdd.md §3.4)
- [ ] D2 computes `shared`/`sim_only`/`real_only` over move labels via `move-map.yaml`; unmapped sim labels surface raw in `sim_only`; sets sorted lexicographically (FR-4, sdd.md §3.3)
- [ ] Provenance block renders `scenario_id`, `scenario_sha256`, sim `producer.kind`+`claim_strength` **quoted**, real `batch_path`, `engine_git_sha`, validation status, run counts (FR-5, NFR-5)
- [ ] Framing footer renders the standing frame verbatim (simulated = exploration, real = proof; divergence shown not judged; interpretation is the analyst's) (FR-6)
- [ ] `scenario_sha256` mismatch → `ERROR: [gap_report] scenario_sha256 mismatch: sim=<a> real=<b>` on stderr, **exit 2** (distinct from input-error exit 1) (FR-2, SM-4)
- [ ] Report written to `grimoires/arneson/playouts/gap-reports/<scenario_id>-<timestamp>.md`; timestamp in filename only, body clock-free (FR-7, NFR-6)
- [ ] Real batch opened `"r"` only — no writes, no grader subprocess, no `--regrade`; **arithmetic only**, no classification/severity/cliff function present (FR-8, NFR-4, sdd.md §4.3)
- [ ] Output is **deterministic** — generated body byte-matches the Sprint 18 golden (timestamped filename excluded) (NFR-6, SM-1)

### Technical Tasks
- [ ] T19.1: Extract `triage`, `_sidecar_paths`, `INFRA_MARKER` into `triage_lib.py`; refactor `sweep_report.py` to import; verify `test-sweep-report.sh` byte-equal (OQ-2, R7) → **[SM-5, G-4]**
- [ ] T19.2: Implement `main(argv)` + `parse_args` (`--sim`/`--real` only) + `load_sim` + `load_real` (reads `lane`, `scenario_sha256`, `batch_path`, validation status) per SDD §4.2 → **[SM-1]**
- [ ] T19.3: Implement `assert_paired` refusal — exit 2 + both-sha message (FR-2) → **[SM-4, G-4]**
- [ ] T19.4: Implement `outcome_divergence` (D1) — `tally_real` via `triage_lib` + sim `outcome_signal` tags, iterate fixed `VERDICT_CLASSES`/`OUTCOME_SIGNAL` tuples (FR-3, NFR-6) → **[SM-1, G-4]**
- [ ] T19.5: Implement `action_divergence` (D2) — normalize via `move-map.yaml`, three sorted sets, raw-when-unmapped (FR-4, sdd.md §3.3) → **[SM-1, G-4]**
- [ ] T19.6: Implement `provenance` (quoted labels, validation status) + `render` + `write_report` to `gap-reports/`, deterministic body (FR-5, FR-6, FR-7, NFR-6) → **[SM-1, G-4]**
- [ ] T19.7: Negative-design audit — confirm no classifier/severity/cliff, no batch writes, no grader subprocess, no `construct-gygax` import, no third-party import (sdd.md §4.3; FR-8, NFR-1, NFR-2, NFR-4) → **[G-4]**

### Dependencies
- Sprint 18: `playout-summary.v1.schema.json`, `move-map.yaml`, synthetic fixture pair, golden file.

### Security Considerations
- **Trust boundaries:** real graded batch + grader sidecars are Gygax-produced, untrusted-for-mutation. `gap_report.py` opens them read-only. Producer-never-judges (G-4 §3) is enforced structurally — no classifier in the script.
- **External dependencies:** NONE added. stdlib + vendored `restricted_yaml`.
- **Sensitive data:** none.
- **Injection surface:** sidecar JSON parse errors are caught per-file and skipped (mirrors `sweep_report` tolerance), never crashing the run (sdd.md §6).

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `triage_lib.py` extraction changes `sweep_report.py` byte output | Med | Med | `test-sweep-report.sh` byte-equal gate is the acceptance criterion (R7) |
| Hash-order nondeterminism leaks into rendered sets/tables | Med | High | Iterate over fixed tuples + `sorted()` everywhere; golden-file diff catches it (NFR-6) |
| Pairing refusal collides with generic input-error exit | Low | Med | Exit 2 is reserved exclusively for the FR-2 refusal; SM-4 negative test asserts the path |

### Success Metrics
- Generated report body byte-matches the Sprint 18 golden (SM-1)
- Mismatch fixture → exit 2 with both shas named (SM-4)
- `test-sweep-report.sh` passes byte-equal post-extraction

---

## Sprint 20 (cycle-004 sprint-3): Skill + Enablers + Gates

**Duration:** 2.5 days
**Scope:** MEDIUM (6 tasks)

### Sprint Goal
Wrap the script in an operator skill, stand up the test gates and dev enablers, run the informational real smoke, and validate all PRD success metrics end-to-end.

> From sdd.md §8 Phase 3: "Skill + enablers + tests (the gates)" (sdd.md:L707)

### Deliverables
- [ ] `domains/agent-systems/skills/gap-report/SKILL.md` — thin wrapper (G1 pair gate → G2 generate → G3 report) (FR-9)
- [ ] `domains/agent-systems/scripts/test-gap-report.sh` — golden + banned-copy grep + negative + import-grep + read-only checks (the gate)
- [ ] `scripts/test.sh` — unified runner, globs `domains/*/scripts/test-*.sh` + Python validator self-tests (FR-10, OQ-4 complement)
- [ ] `pyproject.toml` — ruff + mypy, scoped, NO `[project]`/runtime deps (FR-11, OQ-3)
- [ ] Real informational smoke from `awareness-ladder-demo` (exit 0, not a gate)
- [ ] Task 20.E2E: End-to-End Goal Validation (all PRD success metrics)

### Acceptance Criteria
- [ ] `gap-report/SKILL.md` mirrors `playout/SKILL.md` pattern; G1 surfaces the script's refusal verbatim on sha mismatch; G3 states the standing frame and never summarizes divergence as a verdict (FR-9, sdd.md §5.2)
- [ ] `test-gap-report.sh`: (a) golden body diff passes, (b) banned-copy grep reuses the `scripts/ci/banned-copy-check.sh` BANNED regex and finds **0 hits** outside quoted ban lists, (c) mismatch negative asserts exit 2, (d) source grep finds no third-party / `construct-gygax` import, (e) batch bytes snapshot identical before/after a run (SM-1, SM-3, SM-4, FR-8, NFR-1)
- [ ] `scripts/test.sh` exit 0 runs every `domains/*/scripts/test-*.sh` (incl. the new one by glob) + validator self-tests; **complements** `scripts/ci/*`, does not supersede (SM-5, FR-10, OQ-4)
- [ ] `pyproject.toml` has NO `[project]` table and NO runtime dependency; `ruff` + `mypy` clean on `gap_report.py` + `summarize_playout.py` + `triage_lib.py` + their imports; pre-existing sibling findings handled via narrowly-scoped `per-file-ignores`/module overrides with a one-line comment each — not refactored (SM-6 refined to scoped, FR-11, OQ-3)
- [ ] Real smoke: `awareness-ladder-demo` sim+real pair → `gap_report.py` exits 0 and writes a report; treated as informational (NOT a gate) per R3 (SM-2)
- [ ] G-4 hard constraints verified end-to-end: arithmetic-only output, read-only on the real batch, quoted `producer.kind`/`claim_strength` labels, banned-copy grep clean, deterministic golden, stdlib-only + no Gygax imports

### Technical Tasks
- [ ] T20.1: Author `skills/gap-report/SKILL.md` (G1 pair gate, G2 generate, G3 report + framing; bright lines from `playout/SKILL.md`) (FR-9) → **[SM-2, G-4]**
- [ ] T20.2: Implement `test-gap-report.sh` — golden diff, banned grep (reuse CI regex, single source of truth), mismatch negative, import-grep, read-only byte snapshot (sdd.md §7.3) → **[SM-1, SM-3, SM-4, G-4]**
- [ ] T20.3: Implement `scripts/test.sh` — glob domain `test-*.sh` + validator self-tests, nonzero on any failure; complement `scripts/ci/*` (FR-10, OQ-4) → **[SM-5]**
- [ ] T20.4: Author `pyproject.toml` (ruff+mypy, scoped, no runtime deps) + make the cycle's surface clean + scoped ignores for pre-existing sibling findings (FR-11, OQ-3) → **[SM-6]**
- [ ] T20.5: Run the real informational smoke from `awareness-ladder-demo`; record exit 0; document it is not a gate (R3) → **[SM-2]**
- [ ] T20.E2E: End-to-End Goal Validation (see below) → **[All SM, G-4]**

### Task 20.E2E: End-to-End Goal Validation

**Priority:** P0 (Must Complete)
**Goal Contribution:** All PRD success metrics (SM-1…SM-6) + the G-4 hard-constraint bundle.

**Validation Steps:**

| Goal ID | Goal | Validation Action | Expected Result |
|---------|------|-------------------|-----------------|
| SM-1 | Byte-stable report for synthetic fixture pair | Run golden-file diff in `test-gap-report.sh` | Generated body byte-matches golden (timestamp excluded) |
| SM-2 | Real-pair smoke produces a report, exit 0 | Run `gap_report.py` on `awareness-ladder-demo` sim+real pair | Exit 0; report written (informational, not a gate) |
| SM-3 | 0 banned phrases outside quoted ban lists | Banned-copy grep over a freshly generated report | 0 hits |
| SM-4 | Mismatched `scenario_sha256` refuses | Run mismatch negative fixture | Exit 2 + both shas named |
| SM-5 | One command runs all tests green | `scripts/test.sh` | Exit 0 |
| SM-6 (scoped, OQ-3) | ruff+mypy clean on cycle surface + imports | `ruff` + `mypy` via `pyproject.toml` | Clean on gap_report/summarize_playout/triage_lib + imports; siblings scoped-ignored |
| G-4 | Hard constraints | Inspect output + script source | Arithmetic-only, read-only on batch, quoted labels, banned-clean, deterministic, stdlib-only + no Gygax imports |

**Acceptance Criteria:**
- [ ] Each metric validated with documented evidence (test output captured)
- [ ] Integration verified: sim summary → `gap_report.py` → report, end-to-end on both synthetic and real pairs
- [ ] No metric marked "not achieved" without explicit justification

### Dependencies
- Sprint 19: working `gap_report.py` + golden output.
- Sprint 18: fixtures, schemas, move-map.

### Security Considerations
- **Trust boundaries:** the skill is operator-facing; it never authors a grade, edits the batch, softens a claim label, or paraphrases a simulation upward (sdd.md §5.2 bright lines).
- **External dependencies:** `pyproject.toml` adds ruff/mypy as **dev-only** tooling — explicitly NO runtime dep, NO `[project]` table (FR-11, NFR-1). This is the one place a dependency could leak in; the acceptance criterion forbids it.
- **Sensitive data:** none.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Whole-dir lint surfaces unrelated sibling findings | Med | Low | OQ-3 scoped ignores (`per-file-ignores`/module overrides) with one-line comments; do not refactor siblings |
| `pyproject.toml` accidentally introduces a runtime dep | Low | High | Acceptance criterion: no `[project]` table, no dependency list; grep asserts it |
| Real smoke flakes (persona-host nondeterminism) | High | Low | Smoke is informational only — exit 0 is the only assertion (R3, SM-2) |

### Success Metrics
- `scripts/test.sh` exit 0 (SM-5)
- All SM-1…SM-6 validated in Task 20.E2E
- Banned-copy grep clean (SM-3)

---

## Sprint 21 (cycle-004 sprint-4): Cycle Hygiene

**Duration:** 0.5 day
**Scope:** SMALL (2 tasks)

### Sprint Goal
Finalize ledger and NOTES state for the cycle; confirm cycle-003 archival and cycle-004 sprint completion records.

> From sdd.md §8 Phase 4: "Open cycle-004, archive cycle-003 via the ledger flow — R4" (sdd.md:L715)

### Deliverables
- [ ] Ledger reflects cycle-003 archived + cycle-004 active with sprints 18–21 (applied at plan time — this sprint confirms + records sprint completions)
- [ ] `grimoires/loa/NOTES.md` updated with cycle-004 decision log + session continuity

### Acceptance Criteria
- [ ] `grimoires/loa/ledger.json`: `cycle-003.status == "archived"`, `active_cycle == "cycle-004"`, `next_sprint_number == 22`, sprints 18–21 registered (verified)
- [ ] Sprint completion timestamps recorded for 18–20 as `/run` closes each
- [ ] NOTES.md carries the cycle-004 decision log (OQ-1…OQ-5 resolutions, key tradeoffs)

### Technical Tasks
- [ ] T21.1: Confirm ledger state (cycle-003 archived, cycle-004 active, next_sprint_number=22); record sprint 18–20 completion timestamps → **[hygiene]**
- [ ] T21.2: Update `grimoires/loa/NOTES.md` — cycle-004 decision log + session continuity + deferred items (host-emit promotion of OQ-1, D3 Rich tier, `/voice` feedback loop) → **[hygiene]**

### Dependencies
- Sprints 18–20 completed (their completion timestamps are recorded here).

### Security Considerations
- **Trust boundaries:** ledger + NOTES are State Zone (read/write). No app code touched.
- **External dependencies:** none.
- **Sensitive data:** none.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Ledger drift if a sprint reopens | Low | Low | Confirm-only sprint; re-validate JSON before close |

### Success Metrics
- Ledger JSON valid + cycle states correct
- NOTES.md decision log present

---

## Risk Register

| ID | Risk | Sprint | Probability | Impact | Mitigation | Owner |
|----|------|--------|-------------|--------|------------|-------|
| R1 | Sim lane emits no diffable structure | 18 | Confirmed | High | Additive `playout-summary.v1.json` via post-pass `summarize_playout.py` (OQ-1) | Implementer |
| R2 | Sim/real action vocabularies diverge | 18–19 | High | Med | Documented `move-map.yaml`; raw labels when unmapped (R2, OQ-5) | Implementer |
| R3 | Persona-host nondeterminism → real smoke can't gate | 20 | High | Low | Synthetic golden is the gate (SM-1); real pair is exit-0 smoke (SM-2) | Implementer |
| R4 | Orphaned cycle-002 prd; cycle-003 still active | 21 | Resolved | Low | cycle-004 opened + cycle-003 archived at plan time (this plan) | Planner |
| R5 | "grader's report" Markdown-only, not parseable | 19 | Confirmed | Med | D1 reads `observation.classification` from graded sidecars via `triage_lib` (sdd.md §3.2) | Implementer |
| R6 | Whole-dir lint surfaces pre-existing findings | 20 | Med | Low | Scoped lint (OQ-3): cycle surface clean, siblings scoped-ignored | Implementer |
| R7 | Triage drifts between `sweep_report.py` and `gap_report.py` | 19 | Low | Med | Shared `triage_lib.py` (OQ-2); `test-sweep-report.sh` byte-equal guard | Implementer |

---

## Success Metrics Summary

| Metric | Target | Measurement Method | Sprint |
|--------|--------|-------------------|--------|
| SM-1 | Byte-stable golden report | golden-file diff in `test-gap-report.sh` | 19 (impl), 20 (gate) |
| SM-2 | Real pair → exit 0 | informational smoke | 20 |
| SM-3 | 0 banned phrases | grep (reused CI regex) | 20 |
| SM-4 | sha mismatch refuses | negative test, exit 2 | 19 (impl), 20 (gate) |
| SM-5 | one command, all green | `scripts/test.sh` exit 0 | 20 |
| SM-6 (scoped) | ruff+mypy clean on cycle surface | `pyproject.toml` gate | 20 |

---

## Dependencies Map

```
Sprint 18 ──────────▶ Sprint 19 ──────────▶ Sprint 20 ──────────▶ Sprint 21
   │                     │                     │                     │
   └─ Contracts +        └─ gap_report.py      └─ Skill + gates +    └─ Cycle
      fixtures +            core (D1/D2/         E2E validation +       hygiene
      summarize_playout     refusal/render)      real smoke
```

---

## Appendix

### A. PRD Feature Mapping

| PRD Requirement | Sprint | Status |
|-----------------|--------|--------|
| FR-1 Inputs | 18 (schema), 19 (load) | Planned |
| FR-2 Pairing refusal | 19 | Planned |
| FR-3 D1 outcome divergence | 19 | Planned |
| FR-4 D2 action-set divergence | 19 | Planned |
| FR-5 Provenance block | 19 | Planned |
| FR-6 Framing footer | 19 | Planned |
| FR-7 Output location | 19 | Planned |
| FR-8 Read-only on real batch | 19 | Planned |
| FR-9 Skill wrapper | 20 | Planned |
| FR-10 Unified test runner | 20 | Planned |
| FR-11 Dev-only pyproject.toml | 20 | Planned |
| NFR-1 stdlib-only runtime | 18, 19, 20 | Planned |
| NFR-2 No Gygax coupling | 18, 19, 20 | Planned |
| NFR-3 Banned-copy clean | 20 | Planned |
| NFR-4 Arithmetic only | 19 | Planned |
| NFR-5 Validator-respecting | 19 | Planned |
| NFR-6 Deterministic core | 18, 19 | Planned |
| NFR-7 Vendored contract read-only | 18 | Planned |

### B. SDD Component Mapping

| SDD Component | Sprint | Status |
|---------------|--------|--------|
| `playout-summary.v1.schema.json` (§3.1) | 18 | Planned |
| `summarize_playout.py` (OQ-1) | 18 | Planned |
| `move-map.yaml` + schema (§3.3) | 18 | Planned |
| Synthetic fixture pair + golden (§7.2) | 18 | Planned |
| `triage_lib.py` (§4.1, OQ-2) | 19 | Planned |
| `gap_report.py` (§4) | 19 | Planned |
| `skills/gap-report/SKILL.md` (§5.2) | 20 | Planned |
| `test-gap-report.sh` (§7.3) | 20 | Planned |
| `scripts/test.sh` (§7.4, OQ-4) | 20 | Planned |
| `pyproject.toml` (§2.2, OQ-3) | 20 | Planned |
| Cycle hygiene (§8 Phase 4) | 21 | Planned |

### C. PRD Goal Mapping

The PRD expresses goals as success metrics (SM-1…SM-6) plus the G-4 hard-constraint bundle (arithmetic-only, read-only, quoted labels, banned-clean, deterministic, stdlib-only/no-Gygax). These are the traceability anchors.

| Goal ID | Goal Description | Contributing Tasks | Validation Task |
|---------|------------------|-------------------|-----------------|
| SM-1 | Byte-stable golden report | T18.1, T18.2, T18.4, T18.5, T19.2, T19.4, T19.5, T19.6, T20.2 | T20.E2E |
| SM-2 | Real-pair smoke, exit 0 | T20.1, T20.5 | T20.E2E |
| SM-3 | 0 banned phrases | T20.2 | T20.E2E |
| SM-4 | sha mismatch refuses (exit 2) | T19.3, T20.2 | T20.E2E |
| SM-5 | one command, all green | T19.1, T20.3 | T20.E2E |
| SM-6 (scoped) | ruff+mypy clean on cycle surface | T20.4 | T20.E2E |
| G-4 | Hard-constraint bundle | T18.1, T18.2, T19.1, T19.3, T19.4, T19.5, T19.6, T19.7, T20.1, T20.2 | T20.E2E |

**Goal Coverage Check:**
- [x] All PRD goals (SM-1…SM-6 + G-4) have at least one contributing task
- [x] All goals have a validation task in the final implementation sprint (T20.E2E)
- [x] No orphan tasks (every task traces to ≥1 SM or G-4 or cycle hygiene)

**Per-Sprint Goal Contribution:**

- Sprint 18: SM-1 (foundation: contracts + fixtures + summarize), G-4 (partial: schema, stdlib-only)
- Sprint 19: SM-1 (core impl), SM-4 (refusal), SM-5 (triage extraction), G-4 (arithmetic/read-only/quoted/deterministic)
- Sprint 20: SM-2, SM-3, SM-5 (runner), SM-6 (lint), G-4 (full E2E verification) — E2E validation of all goals
- Sprint 21: cycle hygiene (no SM/G-4 contribution)

---

*Generated by Sprint Planner Agent. Arithmetic only; the report shows where forecast and observation diverge — it never judges fidelity.*
