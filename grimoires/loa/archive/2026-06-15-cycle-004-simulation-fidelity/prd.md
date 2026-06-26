# PRD — Simulation Fidelity Gap Report

> **Cycle theme:** Simulation fidelity measurement (Arneson)
> **Status:** Draft (discovery complete)
> **Author:** discovering-requirements / Practitioner
> **Date:** 2026-06-15
> **Grounding:** Brownfield. Cached reality (`grimoires/loa/reality/`, 2026-06-10, <7d). Context dir MEDIUM (12 files / 1018 lines). Design-shaping source: `domains/agent-systems/domain.conventions.md` (G-4 claim-framing rules).

---

## 1. Problem Statement

Arneson hosts a persona in a **simulated lane** (`/playout --scenario`, persona host, ungraded "behavioral exploration") and runs the same scenario in a **real lane** (`/playout --real`, Gygax's ladder engine, graded `observed-trace/v1` batches). The simulated lane is the cheaper, faster preview; the real lane is the proof.

Today nothing **diffs the two**. `sweep_report.py` cross-compares N *already-graded real batches* against each other, but never compares a simulated playout against its real counterpart. So the central question of a persona-simulation engine — *does the persona actually capture how real agents behave?* — has no instrument.

> Source: brief (Phase 1); `domains/agent-systems/scripts/sweep_report.py` (cross-compares graded batches only); `domains/agent-systems/skills/playout/SKILL.md` (dual-lane).

The domain conventions already **name** the instrument we're missing. The sanctioned replacement for the banned phrase "proves it's compelling" is:

> "shows where forecast and observation diverge"
> — `domains/agent-systems/domain.conventions.md` (banned-copy table)

This cycle builds exactly that: a report that shows where the forecast lane (simulated) and the observation lane (real) diverge.

## 2. Goals & Success Metrics

**Primary goal.** Ship a diagnostic that pairs a simulated playout with its real graded batch and tabulates their divergence — arithmetic and quoted labels only — so the Practitioner (and downstream, the analyst) can see where the persona's forecast departs from observed reality.

**Success metrics (verifiable):**

| # | Metric | Check |
|---|--------|-------|
| SM-1 | `gap_report.py` produces a byte-stable report for the synthetic fixture pair | golden-file test in `test-gap-report.sh` |
| SM-2 | End-to-end smoke: real pair from `awareness-ladder-demo` scenario produces a report with exit 0 | smoke test (informational, not a gate) |
| SM-3 | Generated reports contain **0 banned phrases** outside quoted ban lists | grep check in `test-gap-report.sh`, same list as `domain.conventions.md` |
| SM-4 | Pairing two playouts with mismatched `scenario_sha256` **refuses** (non-zero exit, clear message) | negative test |
| SM-5 | One command runs all domain `test-*.sh` + Python validator self-tests + the new tests, green | `scripts/test.sh` exit 0 |
| SM-6 | `ruff` + `mypy` clean on `domains/agent-systems/scripts/` | `scripts/test.sh` (or a lint target) |

**Non-goal (explicit).** The report does **not** score, rank, or judge fidelity. "Fidelity is exactly what's unproven" — calling the output "high-fidelity" is banned copy. The output shows divergence; it never concludes the persona is right or wrong.

> Source: brief (Phase 2); `domain.conventions.md` (banned-copy table, G-4 §1, §3).

## 3. Users & Stakeholders

- **Primary: the Practitioner** — runs `gap-report` after a sim + real pair exists, reads the markdown to see where the persona drifted from observed behavior.
- **Secondary: the analyst (Gygax-side, downstream)** — the divergence surfaced here is raw material the analyst *interprets* (cliffs, severity). The report hands them counts; it does not pre-empt their judgment.
- **Not a stakeholder in this cycle: `/voice`** — auto-feeding divergence into a persona-workshop loop is deferred to the Gygax cycle. This cycle is diagnostic-only.

> Source: brief (Phase 3, out-of-scope note); `domain.conventions.md` G-4 §3 ("judgments are Gygax's").

## 4. Functional Requirements

### Core: the gap report

- **FR-1 — Inputs.** `gap_report.py` takes one **simulated-lane** playout (persona-host serialization, `lane: simulated`, ungraded) and one **real-lane** playout (`lane: real`, pointing at an `observed-trace/v1` batch + the grader's report).
- **FR-2 — Pairing by `scenario_sha256`.** The two playouts must pin the same committed scenario (`scenario_sha256` equal). On mismatch, **refuse** with a non-zero exit and a message naming both shas. (Diffing across two scenarios produces a diff that can't be attributed — `domain.conventions.md` convention 3.)
- **FR-3 — D1 Outcome divergence.** Tabulate the real lane's **verdict-class distribution** (counts of `fixed`/`hacked`/`failed`/`infra`/`ungraded`, taken verbatim from the grader's report) beside the simulated lane's **outcome-signal tags**. Counts only; verdict labels **quoted**, never paraphrased upward.
- **FR-4 — D2 Action-set divergence.** Compute three sets over the move/action labels: **sim-only** (moves the persona took that never appear in the real batch), **real-only** (moves real agents made that the persona never explored), **shared**. Report the sets and their counts.
- **FR-5 — Provenance block.** Every report opens with: `scenario_id`, `scenario_sha256`, the sim playout's `producer.kind` + `claim_strength` (quoted), the real batch path + `engine_git_sha`, and run counts. (Honest labels — `domain.conventions.md` G-4 §2.)
- **FR-6 — Framing footer.** Each report ends with the standing frame: simulated = behavioral exploration, real = proof; divergence is shown, not judged; interpretation belongs to the analyst's report.
- **FR-7 — Output location.** Markdown written to `grimoires/arneson/playouts/gap-reports/<scenario_id>-<timestamp>.md`.
- **FR-8 — Read-only on the real batch.** The report **never** writes to, recomputes, or regrades the real batch. It consumes existing grades. (Producer-never-judges.)
- **FR-9 — Skill wrapper.** A `gap-report` domain skill (under `domains/agent-systems/skills/`) wraps `gap_report.py`, mirroring the `playout` skill + `sweep_report.py` pattern.

### Enablers (minimal, in scope)

- **FR-10 — Unified test runner.** A root-level `scripts/test.sh` (bash, stdlib tools only) that discovers and runs every `domains/*/scripts/test-*.sh` plus the Python validator self-tests, and exits non-zero on any failure. Single command for local + CI. **Not** npm/pytest.
- **FR-11 — Dev-only `pyproject.toml`.** Root `pyproject.toml` configuring `ruff` + `mypy` over `domains/agent-systems/scripts/`. Dev tooling only: **no `[project]` runtime dependencies**, nothing that makes the runtime import a third-party package. The runtime continues to vendor `restricted_yaml`.

## 5. Technical & Non-Functional Requirements

- **NFR-1 — stdlib-only runtime.** `gap_report.py` uses the Python stdlib + the vendored `restricted_yaml` parser. No new runtime dependencies. (Portability — brief Phase 5.)
- **NFR-2 — No Gygax coupling.** Reads Gygax-produced artifacts (`observed-trace/v1` batch, grader report) **as files** via the vendored contract under `schemas/vendor/`. Imports nothing from `construct-gygax`. (Standalone-plus-composable.)
- **NFR-3 — Banned-copy clean.** Generated reports and all new docs pass the banned-copy grep (0 hits outside quoted ban lists), reusing `domain.conventions.md`'s list.
- **NFR-4 — Arithmetic only.** The report emits counts, ratios, and set diffs computed from the grader's report; it authors no severity, "cliff," or correctness judgment. (`domain.conventions.md` G-4 §3.)
- **NFR-5 — Validator-respecting.** A real batch is only consumable as graded input if it is conformant; the report records the batch's validation status (and, where cheap, declines non-conformant input).
- **NFR-6 — Deterministic core.** Given fixed inputs, `gap_report.py` produces byte-identical output (stable ordering of sets/tables) so SM-1 golden-file testing holds.
- **NFR-7 — Vendored contract is read-only.** Never edit `schemas/vendor/`; if the contract must change, re-vendor + update `VENDOR.yaml`. (Convention 1.)

## 6. Scope & Prioritization

**MVP (this cycle):** FR-1…FR-11, NFR-1…NFR-7. Diff scope = **Standard**: D1 outcome divergence + D2 action-set divergence. Fixtures = **synthetic** (deterministic unit/golden test) **+ one real** pair generated from `awareness-ladder-demo` (informational smoke).

**Explicitly out of scope (deferred):**
- D3 improvisation-rate / per-rung / per-room breakdown (the "Rich" tier).
- Auto-feedback from divergence into `/voice` workshop goals (→ Gygax cycle).
- Domain contract validator, Vocs docs site, command-format migration.
- Any shared `@loa/*` package or shared identity base between Arneson and Gygax.

> Source: brief (out-of-scope block); Q1/Q2 answers (Standard + synthetic-plus-real).

## 7. Risks & Dependencies

| ID | Risk | Mitigation |
|----|------|------------|
| R1 | The simulated lane ("serialize-only" persona host) may not yet emit a structured action/outcome-signal list that D2/D1 can diff. | Verify the sim-playout output shape in architecture; if absent, a small, in-scope addition to the sim serializer is part of the cycle. First design question for `/architect`. |
| R2 | Real-lane move labels (`moves.json`) and sim-lane action labels may use different vocabularies, making the action-set diff noisy. | Architecture defines move-identity normalization (a documented mapping, not an inferred one); report raw labels when no mapping applies. |
| R3 | No simulated fixture exists; persona-host output is non-deterministic, so the real smoke (SM-2) can't be a hard gate. | Synthetic golden-file pair is the deterministic gate (SM-1); the real pair is an informational smoke only. |
| R4 | Replacing the orphaned `cycle-002` `prd.md`; ledger `cycle-003` is still `active` though its sprints are complete. | Open a new cycle (cycle-004) at the `/architect` / `/sprint-plan` step; archive cycle-003 via the ledger flow. |

**Dependencies:** Gygax `observed-trace/v1` + batch contracts (vendored, read-only); `validate_batch.py` / `validate_scenario.py`; the simulated-lane persona-host output format; `sweep_report.py` as the structural sibling pattern.

## 8. Traceability

| Requirement | Source |
|-------------|--------|
| Problem, dual-lane gap | brief Phase 1; `sweep_report.py`; `playout/SKILL.md` |
| "shows where forecast and observation diverge" framing | `domain.conventions.md` banned-copy table |
| Arithmetic-only / judgments-are-Gygax's | `domain.conventions.md` G-4 §3 |
| Honest labels / quote `claim_strength` | `domain.conventions.md` G-4 §2 |
| Pairing by scenario / one-variable convention | `domain.conventions.md` convention 3; playout artifact `scenario_sha256` field |
| Standard diff scope; synthetic+real fixtures | Discovery Q1 / Q2 (2026-06-15) |
| Enablers (runner, pyproject) | brief Phase 4–5 |
| Out-of-scope coupling guards | brief; memory: standalone-plus-composable |
