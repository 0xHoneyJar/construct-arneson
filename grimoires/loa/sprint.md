# Sprint Plan: cycle-007 — Compounding-Seam Closure & In-Flight Consolidation

**Version:** 1.0
**Date:** 2026-06-25
**Author:** Sprint Planner Agent
**PRD Reference:** grimoires/loa/prd.md (cycle-007, 7 FRs, 7 NFRs, 6 risks)
**SDD Reference:** grimoires/loa/sdd.md (4 phases, OQ-1 + R-2 resolved empirically)

---

## Executive Summary

cycle-007 is a **consolidation cycle**, not a new subsystem (`sdd.md` §1.1). It closes the *producer
side* of the Arneson→Gygax compounding seam (Theme A) and restores truth to in-flight project state
(Theme C). The architecture is the construct's existing one — filesystem-first, stdlib-only projection
scripts + drift guards + additive schema deltas. No new runtime, no services, no dependencies.

The plan is **3 sprints** sequenced by the PRD priority matrix: the P0 spine first (FR-1, then
FR-2/FR-5/FR-7), the P1 Should-Haves last (FR-3/FR-4/FR-6) so they "trim first if pressed" (PRD R-6 /
SDD RA-7). This matches the PRD's "~3–4 sprints" estimate. Both design questions the PRD delegated to
`/architect` are already resolved in the SDD: **OQ-1 = chosen-only honest projection** (§1.2) and **R-2 =
wholesale pin bump `3fa6c91→95ccf21`** (§1.3). The two implementation-detail open questions (OQ-A, OQ-B)
carry SDD recommendations adopted as decisions below.

**Total Sprints:** 3 (global sprint IDs 23–25)
**Sprint Duration:** 2.5 days each
**Estimated Completion:** 2026-07-04

> **Honest seam tradeoff (must survive into the PR — SDD §1.2 / RA-1):** FR-1 closes the **contract**
> seam (Arneson sim output becomes *consumable* by Gygax's lens), but a chosen-only corpus is
> **analytically empty** (no alternatives ⇒ no revealed preference). The halves now join structurally and
> honestly; making the join analytically valuable requires offered-set capture, which is explicit future
> work. Do not let the seam read as "fully closed."

---

## Sprint Overview

| Sprint | Global ID | Theme | Scope | Key Deliverables | Dependencies |
|--------|-----------|-------|-------|------------------|--------------|
| 1 | 23 | FR-1 decision-trace/v1 emitter (P0 centerpiece) | MEDIUM (6) | Vendored schema + `VENDOR.yaml` bump + 4-file drift guard; `emit_decision_trace.py`; fixture+golden; test; closing proof | None |
| 2 | 24 | FR-2 + FR-5 + FR-7 (rest of P0 spine) | MEDIUM (5) | Binding-table preamble + `resolve_entity_refs.py`; ledger reconciliation + consistency check; Gygax-side handoff brief | Sprint 1 (vendor/guard pattern reused) |
| 3 | 25 | FR-3 + FR-4 + FR-6 (P1) + E2E validation | MEDIUM (6) | Experiential-vocab loader; archetype pin + drift guard; loose-end tail; full-suite E2E goal validation | Sprints 1–2 (all FRs present for E2E) |

**Decisions baked into the plan (from SDD open questions):**
- **OQ-A → remove-only** (Sprint 3 / FR-6): remove `bottleneck` from `signal_flags`; do *not* add the
  missing canonical signal values this cycle (surgical; adding values is a separate digest-completeness
  decision — `sdd.md` §10 OQ-A).
- **OQ-B → ship the script** (Sprint 2 / FR-5): ship `ledger-consistency-check.sh` as a durable SM-7
  gate rather than a one-time review (cheap, durable — `sdd.md` §10 OQ-B).

---

## Sprint 1: FR-1 — `decision-trace/v1` Emitter (the centerpiece)

**Global Sprint ID:** 23 · **Local:** cycle-007 sprint-1
**Scope:** MEDIUM (6 tasks)
**Duration:** 2.5 days
**Dates:** 2026-06-26 – 2026-06-28

### Sprint Goal
Make Arneson's simulated lane emit a `decision-trace/v1` corpus that Gygax's revealed-strategy lens
consumes with exit 0 — closing the *producer side* of the seam (G-1).

### Deliverables
- [ ] `domains/agent-systems/schemas/vendor/decision-trace.v1.schema.json` vendored read-only (Gygax HEAD
      `95ccf21`, `sha256: 83d6a69f…dab02`).
- [ ] `VENDOR.yaml` bumped wholesale `git_sha: 3fa6c91 → 95ccf21` + decision-trace entry added, with the
      byte-identity comment for the three unchanged files (`sdd.md` §3.2).
- [ ] `vendor-drift-guard.sh` extended to cover all **four** vendored files; guard exits 0.
- [ ] `emit_decision_trace.py` — stdlib-only, deterministic, self-checking projection script.
- [ ] Committed sim-lane fixture + **golden** corpus under `resources/fixtures/decision-trace/`.
- [ ] `test-emit-decision-trace.sh` auto-discovered by `scripts/test.sh`; short doc note in
      `domains/agent-systems/docs/`.

### Acceptance Criteria
- [ ] One sim episode in → N `decision-trace/v1` records out, each carrying `schema`, `claim_strength`,
      `producer.{kind,id,detail,provenance}`, `corpus.{id,game}`, `actor_id`, `episode_id`, `t`,
      `context.segment`, `offered`, `chosen` (PRD FR-1; `sdd.md` §3.1).
- [ ] Chosen-only honesty: `offered == chosen` with `producer.detail` = "offered-set-unrecorded: chosen-only
      projection …"; `claim_strength: simulation-derived`, `producer.kind: simulation` are **hardcoded
      literals** (NFR-2, NFR-5; `sdd.md` §1.2).
- [ ] Self-check on write: every record validates against the vendored schema (required fields,
      `additionalProperties:false`, enums); **exit 2** if any record fails (never ship a broken corpus).
- [ ] Byte-identical corpus across runs (sorted keys, fixed separators, ordering stable by `t`/`seq`; no
      clock/random) — SM-1 determinism.
- [ ] `--blank`/degenerate input (no `agent_turn`/no `action_label`) → **exit 1** with
      `ERROR: [emit_decision_trace] …` (`sdd.md` §6).
- [ ] Import-grep test proves **zero** `construct-gygax` imports (NFR-1); banned-phrase gate green (NFR-7).
- [ ] **Closing proof (SM-2, informational gate):** `npx tsx ../construct-gygax/scripts/lib/trace/strategy.ts
      <corpus>/` exits 0 with `claim_strength: simulation-derived`; the today-failing rejection (`unknown
      schema "observed-trace/v1"`) is gone.
- [ ] `vendor-drift-guard.sh` + source↔vendor convergence still green for all four files (SM-3).

### Technical Tasks
- [ ] Task 1.1: Vendor `decision-trace.v1.schema.json` (95ccf21) into `schemas/vendor/`; bump `VENDOR.yaml`
      wholesale + add entry + byte-identity comment. → **[G-1]**
- [ ] Task 1.2: Extend the `vendor-drift-guard.sh` byte-diff array (`:20`) to the 4th file; verify pin-loop
      auto-discovers the new entry; prove guard exit 0 (R-2 closed). → **[G-1]**
- [ ] Task 1.3: Write `emit_decision_trace.py` (sibling to `project_trace.py`): `load → build_records →
      validate_record → write_corpus`; chosen-only projection per §3.1; self-check exit 2; deterministic
      sorted-key JSON; stdlib + `restricted_yaml` only. → **[G-1]**
- [ ] Task 1.4: Build the synthetic sim-lane `session-events-agent` fixture (extend the
      `native-sidecar.events.yaml` shape) + its byte-stable golden `decision-trace/v1` corpus. → **[G-1]**
- [ ] Task 1.5: Write `test-emit-decision-trace.sh` — records+self-validate (SM-1a), golden byte-match
      (SM-1b determinism), exit 1 (degenerate), exit 2 (broken self-output), import-grep (NFR-1),
      banned-phrase (NFR-7). → **[G-1]**
- [ ] Task 1.6: Run the closing proof (SM-2); add the short "emit a decision-trace corpus" doc note
      cross-linked to the seam finding; add `decision-trace.v1` to `construct.yaml::agent-systems.vendored_contracts`
      (signal-taxonomy omission = optional hygiene, mention in PR — `sdd.md` §3.2). → **[G-1]**

### Dependencies
- None (first sprint). Intra-sprint ordering only: **vendor the schema (1.1) before the emitter self-checks
  against it (1.3)** — the single ordering constraint noted in `sdd.md` §1.4.

### Security Considerations
- **Trust boundaries:** the vendored Gygax schema is the **only** cross-construct coupling — pinned
  read-only by `sha256` (NFR-4). The sim-lane event log is Arneson-produced (trusted). The Gygax lens used
  for the closing proof is an external Node toolchain — proof is informational, not a hard CI leg.
- **External dependencies:** no new pip/runtime deps (stdlib + `restricted_yaml` only, NFR-3). New vendored
  file integrity = byte-diff + sha-pin via `vendor-drift-guard.sh`.
- **Sensitive data:** none (no credentials/PII; fixtures are HEKATE-free, NFR-7).

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RA-1 Chosen-only corpus is analytically empty | High (by design) | Med | Flag explicitly in PR + docs; MVP closes *contract* seam per UC-1; analytic value deferred to offered-set capture |
| RA-2 `actor_id` derivation under-specified (single vs multi-actor) | Med | Low | §3.1 rule: persona id else stable `corpus.id`-derived token; never clock/uuid; golden fixture pins the rule |
| RA-3 Future re-vendor finds the 3 files diverged at target SHA | Low | Low | Wholesale choice justified only by today's verified byte-identity; `VENDOR.yaml` comment records it; switch to per-file then |

### Success Metrics
- SM-1: emitter turns a synthetic sim episode into a self-validating, byte-stable `decision-trace/v1` corpus.
- SM-2: Gygax lens consumes the corpus, exit 0, `claim_strength: simulation-derived`.
- SM-3: `vendor-drift-guard.sh` green for all four vendored files.

---

## Sprint 2: FR-2 + FR-5 + FR-7 — Standalone Sessions, Honest Ledger, Clean Handoff

**Global Sprint ID:** 24 · **Local:** cycle-007 sprint-2
**Scope:** MEDIUM (5 tasks)
**Duration:** 2.5 days
**Dates:** 2026-06-29 – 2026-07-01

### Sprint Goal
Make Arneson sessions standalone-interpretable (G-2), restore truth to project state (G-4), and hand the
two Gygax-side seam changes off cleanly (G-5) — completing the P0 spine.

### Deliverables
- [ ] Additive `binding_table` block + entity_ref discipline rule on `schemas/core/session-events-base.schema.yaml`.
- [ ] `scripts/resolve_entity_refs.py` (core) + `test-resolve-entity-refs.sh`.
- [ ] `ledger.json` reconciled (verify-gated) + internal counter inconsistency fixed.
- [ ] `scripts/ci/ledger-consistency-check.sh` (durable SM-7 gate — OQ-B decision).
- [ ] `grimoires/loa/discovery/gygax-seam-requests-cycle007.md` handoff brief.

### Acceptance Criteria
- [ ] Session preamble gains an **additive** `binding_table` (`ref` `^arn:[a-z0-9-]+$`, `label` required,
      optional `gygax_id`); validation rule: every event `entity_ref` MUST appear as a `binding_table[].ref`,
      resolving only through the table (never a bare Gygax id). No breaking change to `session-events-base`
      (NFR-6; `sdd.md` §3.3).
- [ ] A session with `arn:` refs resolves **every** ref through its binding table **with no Gygax checkout
      present** (SM-4); an unbound ref → `resolve_entity_refs.py` exit 1; a pre-existing sidecar with no
      table and no refs still passes (additive-safe).
- [ ] Producer preference recorded for the consumer: **quarantine-and-tag** on ref-resolution failure
      (captured in the FR-7 brief, not enforced Arneson-side).
- [ ] FR-5 verify-gate: for cycle-005 (sprint-22) + the three `cycle-bug-20260610-*` cycles, confirm
      deliverable paths on disk **and** the PR merged (git log) **before** marking `completed`/`archived` with
      timestamps; cycle-006 added as a brief-only micro-cycle (precedent cycle-003/005); document residue
      rather than rubber-stamp if anything fails to verify (R-5; `sdd.md` §3.7).
- [ ] Counter inconsistency fixed: keep `next_sprint_number` canonical, correct/remove stale
      `global_sprint_counter: 3`; decision recorded in PR (`sdd.md` §3.7).
- [ ] `ledger-consistency-check.sh` exits 0: no `active`/`planned` cycle has declared deliverables on disk;
      cycle-006 present (SM-7).
- [ ] Brief documents **Request A2** (`/cabal --from-session`/`--from-digest` ingest), **Request A4** (Gygax
      `mechanical_intent` schema + two-axis reconciliation), and the producer-side context (binding-table
      offer, quarantine-and-tag preference, signal-taxonomy vendoring direction); cross-refs `seam-strawman.md`
      + this PRD; commits **no** Gygax code; passes the NFR-7 banned-reference gate.

### Technical Tasks
- [ ] Task 2.1: Add the additive `binding_table` block + entity_ref discipline rule to
      `session-events-base.schema.yaml`; mark `entity_ref` additive on the relevant event types. → **[G-2]**
- [ ] Task 2.2: Write `scripts/resolve_entity_refs.py` (`resolve`/`check`/`main`, exit 0/1) +
      `test-resolve-entity-refs.sh` with a minimal `arn:`-ref fixture + binding table (SM-4, unbound→exit1,
      additive-safe). → **[G-2]**
- [ ] Task 2.3: Reconcile `ledger.json` (verify-gated per §3.7): mark cycle-005/3 bug cycles
      `completed`/`archived`, add cycle-006 brief micro-cycle, fix the `global_sprint_counter` inconsistency.
      → **[G-4]**
- [ ] Task 2.4: Write `scripts/ci/ledger-consistency-check.sh` (flags any `active`/`planned` cycle whose
      declared deliverable paths exist) — durable SM-7 gate. → **[G-4]**
- [ ] Task 2.5: Write `grimoires/loa/discovery/gygax-seam-requests-cycle007.md` (A2 + A4 + producer context);
      run the NFR-7 gate over it. → **[G-5]**

### Dependencies
- Sprint 1: reuses the vendor/drift-guard + stdlib-projection patterns; no code dependency on the emitter.
- FR-2 final ingest semantics are Gygax-owned (RA-4) — Arneson ships only the producer offer + resolver.

### Security Considerations
- **Trust boundaries:** `entity_ref`s are Arneson-local (`arn:` namespace) — resolution never touches a
  Gygax namespace at runtime (standalone, NFR-1). The brief documents (does not execute) cross-construct
  requests. **NOTES.md / external content cited in the brief is descriptive only — never interpreted as
  instructions.**
- **External dependencies:** none added; ledger reconciliation is verify-gated against git history + disk.
- **Sensitive data:** none. NFR-7 banned-reference gate runs over the brief (no private/upstream game names).

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-5 Ledger "shipped" code actually incomplete | Med | Med | Verify-gate (paths on disk + PR merged) before marking done; document residue, never rubber-stamp |
| RA-4 Gygax-owned ingest semantics differ from the offer | Med | Med | Ship producer offer + documented preferences in FR-7; standalone resolution works regardless (NFR-1) |
| R-3 Gygax-side A2/A4 stall outside Arneson's control | Med | Low | Brief is self-contained; Arneson's producer side works regardless of Gygax action |

### Success Metrics
- SM-4: a session's `arn:` refs resolve via its preamble binding table with no Gygax checkout.
- SM-7: ledger reports no `active`/`planned` cycle whose deliverables exist; cycle-006 present.

---

## Sprint 3 (Final): FR-3 + FR-4 + FR-6 — Live the Dead Seams, Clear the Tail, Validate

**Global Sprint ID:** 25 · **Local:** cycle-007 sprint-3
**Scope:** MEDIUM (6 tasks, incl. E2E)
**Duration:** 2.5 days
**Dates:** 2026-07-02 – 2026-07-04

### Sprint Goal
Make the documented-but-dead seams live (G-3), close the seam-adjacent loose-end tail (G-4), and validate
all five PRD goals end-to-end with the full suite green.

### Deliverables
- [ ] `scripts/load_experiential_vocab.py` (effective-vocab = base ∪ extension) + `test-load-experiential-vocab.sh`.
- [ ] `domains/ttrpg/resources/archetypes-fallback/ARCHETYPE-PIN.yaml` + `scripts/ci/archetype-drift-guard.sh`
      + test.
- [ ] `digest-ttrpg.schema.yaml` `bottleneck` reconciliation (remove-only, decision recorded).
- [ ] `domains/character-voice/scripts/test-freeside-atomic-write.sh`.
- [ ] `NOTES.md.tmp` deleted; snake_case naming exception documented (no rename).
- [ ] Full `scripts/test.sh` green with all new tests (SM-8).

### Acceptance Criteria
- [ ] FR-3: when a tradition lore file carries `experiential_intent_extensions`, the extended tone/register
      values are accepted; when absent, validation falls back to the base controlled vocabulary (graceful
      degradation). Test covers **both** paths (SM-5; reuse `tradition-folk-horror-minimalist.yaml` + a
      base-only tradition; `sdd.md` §4.3).
- [ ] FR-4: `ARCHETYPE-PIN.yaml` records the Gygax `archetypes.yaml` sha + git_sha + the 9 `archetype_names`;
      `archetype-drift-guard.sh` reports drift (sha **or** name-set diff) → exit 1, and **SKIPs/exit 0 when
      Gygax is absent** (standalone unaffected — SM-6; `sdd.md` §4.4).
- [ ] FR-6 bottleneck (OQ-A remove-only): `bottleneck` removed from `signal_flags`; `signal_flags` keys now
      draw only from the canonical 9-value signal taxonomy; decision recorded in the schema comment + PR.
- [ ] FR-6 freeside: `test-freeside-atomic-write.sh` asserts (1) two-layer co-update (body + prompt-marker)
      and (2) a sync-contract violation → `emit_persona.py` exits non-zero **and emits no partial document to
      stdout** (`validate_sync_contract` fires before output; `sdd.md` §4.6). No production-code change.
- [ ] FR-6 hygiene: `grimoires/loa/NOTES.md.tmp` deleted; snake_case `experiential_intent.schema.yaml`
      documented as an **intentional exception** (renaming is breaking per `consistency-report.md:C1`) — no
      rename this cycle.
- [ ] **E2E (Task 3.E2E):** every SM (SM-1…SM-8) re-verified; `scripts/test.sh` exits 0; all drift guards
      green; closing proof re-run.

### Technical Tasks
- [ ] Task 3.1: Write `scripts/load_experiential_vocab.py` (`effective_vocab`/`validate_intent`/`main`) +
      `test-load-experiential-vocab.sh` (present + absent paths, SM-5). → **[G-3]**
- [ ] Task 3.2: Create `ARCHETYPE-PIN.yaml` + `scripts/ci/archetype-drift-guard.sh` (skip-clean on Gygax
      absence) + `test-archetype-drift-guard.sh` (drift→exit1, absent→SKIP, SM-6). → **[G-3]**
- [ ] Task 3.3: Reconcile `bottleneck` in `digest-ttrpg.schema.yaml` (remove from `signal_flags`; record
      decision in comment + PR). → **[G-4]**
- [ ] Task 3.4: Write `domains/character-voice/scripts/test-freeside-atomic-write.sh` (positive co-update +
      negative no-partial-emit lock). → **[G-4]**
- [ ] Task 3.5: Delete `grimoires/loa/NOTES.md.tmp`; document the snake_case naming exception in
      `domain.conventions.md`/`SCHEMA-NAMING.md` (no rename). → **[G-4]**
- [ ] Task 3.E2E: **End-to-End Goal Validation** (P0, see below). → **[G-1, G-2, G-3, G-4, G-5]**

### Task 3.E2E: End-to-End Goal Validation

**Priority:** P0 (Must Complete)
**Goal Contribution:** All goals (G-1, G-2, G-3, G-4, G-5)

**Description:** Validate that all five PRD goals are achieved through the complete cycle-007 implementation.

| Goal ID | Goal | Validation Action | Expected Result |
|---------|------|-------------------|-----------------|
| G-1 | Close producer side of revealed-strategy seam | Run `emit_decision_trace.py` on the fixture, then the Gygax lens on the corpus | Lens exits 0, `claim_strength: simulation-derived` (SM-1, SM-2); the today-failing `observed-trace/v1` rejection is gone |
| G-2 | Standalone-interpretable sessions | `resolve_entity_refs.py` on the `arn:`-ref fixture with **no** Gygax checkout | Every ref resolves; exit 0 (SM-4) |
| G-3 | Documented-but-dead seams live | `load_experiential_vocab.py` (present + absent) + `archetype-drift-guard.sh` | Extension applied/degraded correctly (SM-5); drift detected / SKIP-clean when Gygax absent (SM-6) |
| G-4 | Restore truth to project state | `ledger-consistency-check.sh` + spot-check ledger vs disk | Exit 0; no `active`/`planned` cycle whose deliverables exist; cycle-006 present (SM-7) |
| G-5 | Clean Gygax-side handoff | Review `gygax-seam-requests-cycle007.md`; NFR-7 gate | A2 + A4 + producer context present; no Gygax code committed; banned-reference gate green |
| All | Full suite green | `scripts/test.sh` | Exit 0 (SM-8) |

**Acceptance Criteria:**
- [ ] Each goal validated with documented evidence (command + output).
- [ ] Integration point verified end-to-end: sim episode → `decision-trace/v1` corpus → Gygax lens exit 0.
- [ ] No goal marked "not achieved" without explicit justification.

### Dependencies
- Sprints 1–2: all seven FRs must be present for E2E validation; FR-4 guard reuses the FR-1 drift-guard pattern.

### Security Considerations
- **Trust boundaries:** Gygax `archetypes.yaml` is **untrusted external content** — FR-4 only sha-pins +
  diffs names; absence is SKIP (standalone never fails on Gygax absence, NFR-1). `experiential_intent_extensions`
  lore is Arneson-authored vocabulary data.
- **External dependencies:** none added; FR-4 reads the Gygax checkout only when present (read-only sha).
- **Sensitive data:** none. NFR-7 gate covers all new artifacts; fixtures HEKATE-free.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RA-5 FR-3 "applied" side is prompt-driven, not mechanically testable | Med | Low | Scope FR-3's verifiable contract to the effective-vocab loader + validation; the test locks that |
| RA-6 FR-4 name-set diff surfaces a genuine fallback↔Gygax divergence | Med | Low | That is the guard working; report (exit 1) for the Practitioner to reconcile/re-pin; standalone path skips |
| RA-7 A+C partial-completion risk (~3–4 sprints) | Med | Low | P0 spine (Sprints 1–2) lands first; P1 (this sprint) trims first if pressed |

### Success Metrics
- SM-5: extension present → extended values accepted; absent → base vocab only.
- SM-6: archetype drift (sha or name-set) detected; Gygax absent → SKIP.
- SM-8: full `scripts/test.sh` green with all new tests added.

---

## Risk Register

| ID | Risk | Sprint | Probability | Impact | Mitigation | Owner |
|----|------|--------|-------------|--------|------------|-------|
| RA-1 | Chosen-only corpus analytically empty (contract seam ≠ analytic seam) | 1 | High (by design) | Med | Flag in PR + docs; analytic value deferred to offered-set capture | Practitioner |
| RA-2 | `actor_id` derivation under-specified (single vs multi-actor) | 1 | Med | Low | §3.1 rule + golden fixture pins it; never clock/uuid | — |
| RA-3 | Future re-vendor finds 3 files diverged at target SHA | 1 | Low | Low | Wholesale justified by today's byte-identity; `VENDOR.yaml` comment; switch per-file then | — |
| R-5 | Ledger "shipped" code actually incomplete | 2 | Med | Med | Verify-gate (disk + PR merged) before mark; document residue | Practitioner |
| RA-4 | Gygax-owned ingest semantics differ from the offer | 2 | Med | Med | Ship producer offer + preferences in brief; standalone works regardless | Gygax (consumer) |
| R-3 | Gygax-side A2/A4 stall outside Arneson's control | 2 | Med | Low | Self-contained brief; Arneson side works regardless | Practitioner |
| RA-5 | FR-3 applied side not mechanically testable | 3 | Med | Low | Lock the effective-vocab loader + validation; prompt-application is doc convention | — |
| RA-6 | FR-4 name-set diff = real coordination gap | 3 | Med | Low | Guard working as intended; report for reconcile/re-pin | Practitioner |
| RA-7 | A+C partial completion (~3–4 sprints) | 1–3 | Med | Low | P0 spine first; P1 trims first if pressed (PRD R-6) | Practitioner |

---

## Success Metrics Summary

| Metric | Target | Measurement Method | Sprint |
|--------|--------|-------------------|--------|
| SM-1 | sim episode → self-validating, byte-stable `decision-trace/v1` corpus | `test-emit-decision-trace.sh` golden-file test | 1 |
| SM-2 | Gygax lens consumes the corpus, exit 0, `simulation-derived` | closing-proof smoke (informational) | 1 |
| SM-3 | drift guard green for all 4 vendored files | `vendor-drift-guard.sh` exit 0 | 1 |
| SM-4 | `arn:` refs resolve via binding table, no Gygax checkout | `test-resolve-entity-refs.sh` | 2 |
| SM-7 | no `active`/`planned` cycle has deliverables on disk; cycle-006 present | `ledger-consistency-check.sh` exit 0 | 2 |
| SM-5 | extension present→extended; absent→base vocab | `test-load-experiential-vocab.sh` | 3 |
| SM-6 | archetype drift detected; Gygax absent → SKIP | `test-archetype-drift-guard.sh` | 3 |
| SM-8 | full domain suite green with new tests | `scripts/test.sh` exit 0 | 3 |

---

## Dependencies Map

```
Sprint 1 (23) ──────────▶ Sprint 2 (24) ──────────▶ Sprint 3 (25, FINAL)
   │                         │                          │
   └─ FR-1 emitter           ├─ FR-2 binding table      ├─ FR-3 vocab loader
      (vendor + guard +      ├─ FR-5 ledger reconcile   ├─ FR-4 archetype pin/guard
       golden + closing      └─ FR-7 Gygax brief        ├─ FR-6 loose-end tail
       proof) [P0 spine]        [P0 spine]              └─ Task 3.E2E (all goals) [P1]

Pattern reuse only (no hard code dep): FR-4 guard reuses the FR-1 drift-guard pattern.
Intra-Sprint-1 ordering: vendor schema (1.1) BEFORE emitter self-check (1.3).
```

---

## Appendix

### A. PRD Feature Mapping

| PRD Feature | Priority | Sprint | Status |
|-------------|----------|--------|--------|
| FR-1 decision-trace/v1 emitter | P0 | 1 | Planned |
| FR-2 entity-ref binding table | P0 | 2 | Planned |
| FR-5 ledger reconciliation | P0 | 2 | Planned |
| FR-7 Gygax-side handoff brief | P0 | 2 | Planned |
| FR-3 experiential-intent extension wiring | P1 | 3 | Planned |
| FR-4 archetype SSOT pin + drift detection | P1 | 3 | Planned |
| FR-6 seam-adjacent loose ends | P1 | 3 | Planned |

### B. SDD Component Mapping

| SDD Component | Sprint | Status |
|---------------|--------|--------|
| `emit_decision_trace.py` + vendored schema + `VENDOR.yaml` bump + 4-file drift guard (§4.1, §3.2) | 1 | Planned |
| `binding_table` preamble + `resolve_entity_refs.py` (§3.3, §4.2) | 2 | Planned |
| `ledger.json` reconciliation + `ledger-consistency-check.sh` (§3.7, §4.5) | 2 | Planned |
| `gygax-seam-requests-cycle007.md` brief (§4.8) | 2 | Planned |
| `load_experiential_vocab.py` (§3.4, §4.3) | 3 | Planned |
| `ARCHETYPE-PIN.yaml` + `archetype-drift-guard.sh` (§3.5, §4.4) | 3 | Planned |
| `bottleneck` reconciliation + `test-freeside-atomic-write.sh` + hygiene (§3.6, §4.6, §4.7) | 3 | Planned |

### C. PRD Goal Mapping

| Goal ID | Goal Description | Contributing Tasks | Validation Task |
|---------|------------------|--------------------|-----------------|
| G-1 | Close the producer side of the revealed-strategy seam | Sprint 1: Tasks 1.1–1.6 | Sprint 3: Task 3.E2E |
| G-2 | Make Arneson sessions standalone-interpretable | Sprint 2: Tasks 2.1, 2.2 | Sprint 3: Task 3.E2E |
| G-3 | Make the documented-but-dead seams live | Sprint 3: Tasks 3.1 (FR-3), 3.2 (FR-4) | Sprint 3: Task 3.E2E |
| G-4 | Restore truth to project state | Sprint 2: Tasks 2.3, 2.4 (FR-5); Sprint 3: Tasks 3.3, 3.4, 3.5 (FR-6) | Sprint 3: Task 3.E2E |
| G-5 | Hand off Gygax-side seam requests cleanly | Sprint 2: Task 2.5 (FR-7) | Sprint 3: Task 3.E2E |

**Goal Coverage Check:**
- [x] All 5 PRD goals have at least one contributing task.
- [x] All goals have a validation task in the final sprint (Task 3.E2E).
- [x] No orphan tasks (every task annotated with a contributing goal).

**Per-Sprint Goal Contribution:**
- Sprint 1: G-1 (complete: producer-side seam closed at the contract level).
- Sprint 2: G-2 (complete), G-4 (partial: ledger/FR-5), G-5 (complete).
- Sprint 3: G-3 (complete), G-4 (complete: FR-6 tail), + E2E validation of all goals.

### D. Notes on Ledger & Beads
- This plan registers **cycle-007** in `grimoires/loa/ledger.json` (global sprints 23–25; `active_cycle`
  → cycle-007; `next_sprint_number` → 26) **additively** — it does **not** touch the pre-existing drifted
  entries (cycle-005, the bug cycles, cycle-006). Reconciling those is FR-5's verify-gated job during
  `/implement` (`sdd.md` §3.7 scope note: "cycle-007 itself is registered by `/sprint-plan`, not by FR-5").
- Beads (`br` 0.1.12) is installed but **DEGRADED** (JSONL stale ~223h). Run `br sync` and create the
  cycle-007 epic + tasks at `/build` time (before implementation), per the Beads-First default.

---

*Generated by Sprint Planner Agent (cycle-007). Every task traces to a cited PRD FR / SDD section / SM.*
