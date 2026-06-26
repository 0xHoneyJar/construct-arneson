# PRD — cycle-007: Compounding-Seam Closure & In-Flight Consolidation

> **Cycle theme:** Close the Arneson→Gygax compounding seam (producer side) + restore truth to in-flight project state.
> **Status:** Draft (discovery complete)
> **Author:** discovering-requirements / Practitioner
> **Date:** 2026-06-25
> **Grounding:** Brownfield. Direct cross-repo code analysis of `construct-arneson` and `construct-gygax` (2026-06-25), in lieu of the 15-day-stale cached reality (`grimoires/loa/reality/`, 2026-06-10). Scope set by Practitioner: Themes A (seam) + C (in-flight cleanup); demo and release-hardening explicitly cut.
> **Supersedes:** cycle-004 "Simulation Fidelity Gap Report" PRD (preserved at `grimoires/loa/archive/2026-06-15-cycle-004-simulation-fidelity/prd.md`).

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Goals & Success Metrics](#goals--success-metrics)
4. [Personas & Use Cases](#personas--use-cases)
5. [Functional Requirements](#functional-requirements)
6. [Non-Functional Requirements](#non-functional-requirements)
7. [Scope & Prioritization](#scope--prioritization)
8. [Risks & Mitigation](#risks--mitigation)
9. [Appendix](#appendix)

---

## Executive Summary

construct-arneson is a creative persona engine; its reason for existing alongside its sibling
construct-gygax is that the two are meant to **compound** — Arneson produces evidence (transcripts,
sidecars, digests, forecasts), Gygax re-analyzes it, and each construct's output improves the other's
next iteration. A cross-construct audit found that the compounding loop is **half-built in several
places**: Gygax shipped consumers that Arneson does not feed, schemas were agreed in prose but never
realized, and an extension mechanism was documented but never wired. Separately, project bookkeeping
has drifted — code has shipped for cycles and bug-fixes that the ledger still reports as unfinished.

This cycle does two things. **Theme A** closes the *producer side* of the seam: it makes Arneson emit
the record shapes Gygax's consumers actually require, keeps Arneson sessions interpretable without a
Gygax install, and wires the dead extension/SSOT seams — while pushing the two genuinely Gygax-side
changes into a clean handoff brief rather than committing another repo's work. **Theme C** restores
truth to project state: it reconciles the ledger to reality and clears a short list of seam-adjacent
loose ends.

Out of scope by Practitioner decision: a runnable reference demo, release-hardening (CI/tags/LICENSE),
and any Gygax-side code.

> **Sources:** cross-repo audit (2026-06-25); `grimoires/loa/context/decision-trace-emitter-brief.md`; `grimoires/loa/discovery/seam-strawman.md`; scope confirmed in discovery (demo cut; Theme B deferred).

---

## Problem Statement

### The Problem
The Arneson↔Gygax composition is specified in many places but realized in only some of them. Three
seam defects and a class of bookkeeping drift currently undercut the "pairing compounds" premise.

### Seam defects (Theme A)

1. **Gygax's revealed-strategy lens cannot consume Arneson sim output.** Gygax cycle-012 shipped
   `/cabal --observed --strategy`, whose design asserts it consumes "an Arneson sim (forecast)."
   That assertion is **not contractually real**: the lens's `loadCorpus` requires `decision-trace/v1`
   records; Arneson's simulated lane emits `observed-trace/v1` sidecars. Verified empirically: the
   lens rejects a real Arneson sidecar with `unknown schema "observed-trace/v1" (expected
   "decision-trace/v1")`. Arneson has **zero** `decision-trace` references anywhere.
   > Source: `decision-trace-emitter-brief.md:7-16`; `grimoires/loa/discovery/gygax-revealed-strategy-seam-verified.md` (empirical, 2026-06-20).

2. **Arneson sessions are not standalone-interpretable.** Session events that touch a mechanic /
   tension / resource carry `entity_ref`s. The unresolved design question is *whose IDs* — Gygax's
   game-state IDs verbatim (couples sessions to a Gygax install) vs Arneson-local refs + a preamble
   binding table (standalone-safe). No binding table exists, so refs that resolve only in Gygax's
   namespace silently break the standalone-plus-composable contract.
   > Source: `seam-strawman.md:53-57` (producer preference: binding table); `construct.yaml:85-89` (Arneson reads Gygax game-state paths).

3. **Documented seams that were never wired.** (a) `experiential_intent.schema.yaml:77-86` documents
   an extension mechanism (traditions extend the tone/register vocabulary via lore YAML
   `experiential_intent_extensions`); no Arneson code path reads it and no lore file carries it.
   (b) Arneson falls back to its own 9 archetypes when Gygax is absent and reads Gygax's
   `archetypes.yaml` when present, but with **no version pin or drift detection** — divergence
   between the two sets is undetectable.
   > Source: `experiential_intent.schema.yaml:77-86`; seam audit (archetype SSOT); `construct.yaml:49,85-89`.

### Bookkeeping drift (Theme C)

4. **The ledger lies about what shipped.** cycle-005 (`voice-persona-bridge`, sprint-22) and three
   bug cycles (`cycle-bug-20260610-*`) have **shipped code on disk** but read `active`/`planned`
   with unchecked deliverables; cycle-006 (`decision-trace-emitter` brief, PR #23) is not a ledger
   cycle at all. Plus a short tail of seam-adjacent inconsistencies: a `bottleneck` digest field
   unreconciled with the canonical 9-value signal taxonomy; the freeside adapter's load-bearing
   two-layer atomic-write invariant has no enforcing test; a stray `NOTES.md.tmp`; one snake_case
   schema-name outlier.
   > Source: `ledger.json:9-24,170-208`; engineering audit (2026-06-25); `seam-strawman.md:38-43` (taxonomy); `freeside.yaml:212-239` (atomic-write invariant).

### Desired State
Arneson emits exactly the record shapes Gygax's consumers require; its sessions remain interpretable
with no Gygax install; the extension and SSOT seams are live and drift-guarded; the two Gygax-side
changes are captured in a self-contained handoff brief; and the project's recorded state matches the
code on disk.

---

## Goals & Success Metrics

| ID | Goal | Measurement | Validation |
|----|------|-------------|------------|
| G-1 | Close the **producer side** of the revealed-strategy seam | Gygax's lens consumes an Arneson sim corpus with exit 0 | The exact rejection that fails today is gone (FR-1 acceptance) |
| G-2 | Make Arneson sessions **standalone-interpretable** | A session's `entity_ref`s resolve via its own preamble binding table, no Gygax checkout | Round-trip resolution test, Gygax absent (FR-2) |
| G-3 | Make the **documented-but-dead seams live** | Extension vocab applied when present; archetype drift detectable | Extension test + drift-guard exit codes (FR-3, FR-4) |
| G-4 | Restore **truth to project state** | Ledger entries match shipped code; loose ends closed | Ledger-vs-disk consistency check green (FR-5, FR-6) |
| G-5 | Hand off Gygax-side seam requests **cleanly** | A self-contained brief Gygax can consume without re-deriving context | Brief reviewed; Arneson side works regardless of Gygax action (FR-7) |

### Success Metrics (verifiable)

| # | Metric | Check |
|---|--------|-------|
| SM-1 | `emit_decision_trace.py` turns a synthetic sim-lane episode into a `decision-trace/v1` corpus; every record self-validates against the vendored schema | golden-file test in `test-emit-decision-trace.sh` |
| SM-2 | The produced corpus is consumable by Gygax's lens: `npx tsx ../construct-gygax/scripts/lib/trace/strategy.ts <corpus>/` exits 0 with `claim_strength: simulation-derived` | closing-proof smoke (informational gate per NFR posture) |
| SM-3 | `vendor-drift-guard.sh` stays green for all vendored files including the new `decision-trace.v1.schema.json` (byte-diff + sha-pin) | drift-guard exit 0 |
| SM-4 | A session with Arneson-local `entity_ref`s resolves every ref through its preamble binding table with **no** Gygax checkout present | binding-table resolution test |
| SM-5 | A tradition lore file carrying `experiential_intent_extensions` extends the tone/register vocabulary; absence degrades gracefully to the base vocabulary | extension test (present + absent paths) |
| SM-6 | Archetype drift between the Arneson fallback set and a pinned Gygax `archetypes.yaml` is **detected** (non-zero exit / explicit report) | archetype drift check |
| SM-7 | `ledger.json` reports no cycle as `active`/`planned` whose deliverables exist on disk; cycle-006 exists as a cycle | ledger-vs-disk consistency review |
| SM-8 | The full domain suite (`scripts/test.sh`) stays green with the new tests added | `scripts/test.sh` exit 0 |

### Constraints
- New tooling is **stdlib-only** and **deterministic** (byte-stable output for golden-file testing).
- Vendored contracts are **read-only**; the only cross-construct coupling is a pinned vendored schema.
- No schema change beyond **additive** fields; no breaking renames.

> **Sources:** `decision-trace-emitter-brief.md:17-19,60-68`; `seam-strawman.md:53-57`; G-1–G-5 derived from Problem Statement defects 1–4.

---

## Personas & Use Cases

### Primary Persona: the Practitioner
The human operating both constructs — runs Arneson to produce evidence, runs Gygax to analyze it, and
sits **at the hinge** between the two repos (the only actor authorized to commit cross-construct
coordination). Wants the loop to actually close and the project's records to be trustworthy.

### Secondary Persona: the Analyst (Gygax-side consumer)
Consumes Arneson's forecast corpus through Gygax's revealed-strategy lens. Needs Arneson output that
is honestly claim-tagged (`simulation-derived`, never laundered as real-observed).

#### UC-1: Forecast a strategy, then analyze it
**Actor:** Practitioner → Analyst.
**Flow:** run an Arneson simulated playout → `emit_decision_trace.py` projects it into a
`decision-trace/v1` corpus → Gygax's lens reads the corpus and reports revealed strategy.
**Postcondition:** the producer side of the seam is closed; the corpus is consumable, byte-stable,
and claim-honest.

#### UC-2: Re-analyze a session without a Gygax install
**Actor:** Practitioner.
**Flow:** open an Arneson session sidecar with no Gygax checkout present → every `entity_ref` resolves
via the preamble binding table.
**Postcondition:** standalone-plus-composable holds; composition is amplification, not dependency.

> **Sources:** `decision-trace-emitter-brief.md:19,62-63`; `seam-strawman.md:55-57`; cycle-004 prd persona ("Practitioner").

---

## Functional Requirements

### FR-1: `decision-trace/v1` emitter (Theme A1) — **Must Have**
A stdlib-only projection pass (`emit_decision_trace.py`, sibling to `summarize_playout.py`) that reads
one Arneson **simulated-lane** episode and emits a corpus of `decision-trace/v1` records — one per
observed choice — tagged `producer.kind: simulation`, `claim_strength: simulation-derived`. Adopts the
cycle-006 brief as its specification rather than re-specifying it.

**Acceptance Criteria:**
- [ ] One sim episode in → N `decision-trace/v1` records out, each carrying `schema`, `claim_strength`,
      `producer.{kind,provenance}`, `corpus.{id,game}`, `actor_id`, `episode_id`, `t`,
      `context.segment`, `offered`, `chosen`.
- [ ] Self-check on write: every record validates against the vendored `decision-trace.v1.schema.json`
      (`additionalProperties: false`, required fields); exit 2 if any record fails its own contract.
- [ ] Deterministic, byte-identical corpus across runs (stable ordering by `t`; no clock/random).
- [ ] Vendor `decision-trace.v1.schema.json` from `construct-gygax/schemas/` into
      `domains/agent-systems/schemas/vendor/`, pinned in `VENDOR.yaml`
      (`sha256: 83d6a69f…dab02`, upstream `git_sha: 95ccf21`); never edited here.
- [ ] `vendor-drift-guard.sh` extended to cover the new file; the per-file vs wholesale upstream-pin
      question (existing pin `3fa6c91` vs `95ccf21`) is reconciled so the guard stays green for all
      four vendored files.
- [ ] **Closing proof:** Gygax's lens consumes the produced corpus (exit 0, report present).
- [ ] `--blank`/degenerate input → exit 1 with `ERROR: [emit_decision_trace] …`.
- [ ] `test-emit-decision-trace.sh` added, auto-discovered by `scripts/test.sh`; short doc note added.

**Dependencies:** OQ-1 (offered-set availability — see R-1) is for `/architect` to resolve; it is a
design question, not a blocker.
> **Sources:** `decision-trace-emitter-brief.md:21-68` (verbatim spec); guardrails `:52-58`.

### FR-2: Entity-ref binding table (Theme A3) — **Must Have**
Arneson session sidecars carry **Arneson-local** `entity_ref`s plus a **preamble binding table** that
maps each local ref to its meaning (and, when composing, to a Gygax game-state ID), so a session is
fully interpretable with no Gygax install.

**Acceptance Criteria:**
- [ ] Session preamble gains an (additive) binding-table structure mapping Arneson-local ref → label
      (+ optional Gygax-namespace ID when composed).
- [ ] Session skills emit Arneson-local `entity_ref`s that resolve **only** through the binding table.
- [ ] Resolution works with no Gygax checkout present (SM-4); composition fills the optional Gygax IDs.
- [ ] Producer preference recorded for the consumer's ingest design: **quarantine-and-tag** on
      ref-resolution failure (so partial admissibility survives schema drift) — captured in FR-7's brief.
- [ ] No breaking change to `session-events-base`; additive only.

**Dependencies:** final ingest semantics are Gygax-owned (FR-7); Arneson ships the producer offer.
> **Sources:** `seam-strawman.md:36-37,55-57,61-63`.

### FR-3: Wire the experiential-intent extension mechanism (Theme A5) — **Should Have**
Implement the Arneson code path that reads `experiential_intent_extensions` (tone/register vocabulary)
from tradition lore YAML when present, and ship one worked example.

**Acceptance Criteria:**
- [ ] When a lore file carries `experiential_intent_extensions`, the extended tone/register values are
      accepted/applied; when absent, behavior degrades gracefully to the base controlled vocabulary.
- [ ] One worked example carries the extension (in the TTRPG vertical or `examples/test-domain/`,
      not in the Gygax repo).
- [ ] Test covers both the present and absent paths (SM-5).
> **Sources:** `experiential_intent.schema.yaml:77-86`; seam audit (extension never wired).

### FR-4: Archetype SSOT version-pin + drift detection (Theme A6) — **Should Have**
Add version-pinning and drift detection between the Arneson fallback archetype set and the Gygax
canonical `archetypes.yaml`, so divergence is observable rather than silent.

**Acceptance Criteria:**
- [ ] A pin (version or checksum) records the Gygax `archetypes.yaml` the fallback set was reconciled
      against.
- [ ] A check reports drift (non-zero exit / explicit report) when the canonical set diverges from the
      pin (SM-6).
- [ ] Standalone behavior unchanged: with no Gygax present, the fallback set is authoritative and the
      check is a no-op/skip, not a failure.
> **Sources:** seam audit (archetype SSOT, no pin/checksum); `construct.yaml:49,85-89`; NFR-1.

### FR-5: Ledger reconciliation (Theme C1) — **Must Have**
Reconcile `ledger.json` to reality: every cycle/sprint with shipped code on disk reads its true status;
cycle-006 exists as a cycle; cycle-005 archived post-PR#22.

**Acceptance Criteria:**
- [ ] For cycle-005 (sprint-22) and the three `cycle-bug-20260610-*` cycles: verify code presence, then
      mark `completed` (with timestamps) or document precisely what remains.
- [ ] cycle-006 (`decision-trace-emitter`) is represented as a ledger cycle consistent with PR #23.
- [ ] Ledger-vs-disk consistency check passes: no `active`/`planned` entry whose deliverables exist (SM-7).
- [ ] Reconciliation is verification-gated — a cycle is marked done only after its deliverables are
      confirmed present (see R-5).
> **Sources:** `ledger.json:9-24,170-208`; engineering audit (code present, status stale).

### FR-6: Seam-adjacent loose ends (Theme C3) — **Should Have**
Close the short tail of inconsistencies bundled with this cycle.

**Acceptance Criteria:**
- [ ] `bottleneck` digest field reconciled with the canonical 9-value signal taxonomy (removed or
      mapped, with the decision recorded).
- [ ] A test enforces the freeside adapter's two-layer atomic-write invariant (reference body + system
      prompt template updated in one write; partial write is detectable).
- [ ] Stray `grimoires/loa/NOTES.md.tmp` removed.
- [ ] The snake_case `experiential_intent.schema.yaml` naming outlier is **documented as an intentional
      exception** (renaming is a breaking change per `consistency-report.md:C1`); no rename this cycle.
> **Sources:** `seam-strawman.md:38-43`; `freeside.yaml:212-239`; engineering audit (hygiene); `consistency-report.md:C1`.

### FR-7: Gygax-side handoff brief (Theme A2/A4) — **Must Have**
Write a self-contained brief capturing the two genuinely Gygax-side seam changes as cross-construct
requests, so the Practitioner can hand them to Gygax without re-deriving context. **This is an
Arneson-side deliverable (the brief); it commits no Gygax code.**

**Acceptance Criteria:**
- [ ] Brief documents request A2: a `/cabal --from-session` (or `--from-digest`) ingest mode that
      consumes Arneson's digest/session output (currently emitted but unconsumed).
- [ ] Brief documents request A4: a Gygax `mechanical_intent` schema + reconciliation of the two-axis
      intent shape across `attune` docs (single-axis), `homebrew/SKILL.md` (two-axis), and sample
      game-state files.
- [ ] Brief carries the producer-side context Gygax needs: the binding-table offer, the
      quarantine-and-tag rejection preference, and the signal-taxonomy vendoring direction.
- [ ] Brief lives in an Arneson-owned location and references the seam-strawman + this PRD.
> **Sources:** seam audit (A2 ingest dead-end, A4 intent drift); `seam-strawman.md:28-43,53-63`.

---

## Non-Functional Requirements

| ID | Requirement | Rationale / Source |
|----|-------------|--------------------|
| NFR-1 | **Standalone-plus-composable**: every deliverable works with no Gygax checkout at runtime; the only cross-construct coupling is a pinned vendored schema. | `decision-trace-emitter-brief.md:55`; memory: standalone-plus-composable |
| NFR-2 | **Producer-never-judges**: emitters project/reshape observations; they never score, rank, or interpret (no severity, no "cliff," no correctness verdict). | `decision-trace-emitter-brief.md:54`; `domain.conventions.md` G-4 |
| NFR-3 | **stdlib-only + deterministic**: new scripts use only the standard library and produce byte-stable output. | `decision-trace-emitter-brief.md:23,35` |
| NFR-4 | **Read-only vendored contracts**: never edit `schemas/vendor/`; re-vendor + update `VENDOR.yaml` on contract change. | `decision-trace-emitter-brief.md:58` |
| NFR-5 | **Claim-strength honesty**: simulation output is always `simulation-derived` / `producer.kind: simulation`; it may never tag as real-observed. | `decision-trace-emitter-brief.md:57` |
| NFR-6 | **Additive schema changes only**: no breaking changes to `session-events-base` or `observed-trace/v1`. | `decision-trace-emitter-brief.md:73`; FR-2/FR-3 |
| NFR-7 | **No private/upstream game references** in any artifact; the construct stands alone. | memory: construct stands on its own |

---

## Scope & Prioritization

### In Scope — MVP spine (Must Have)
- FR-1 decision-trace/v1 emitter (closing proof: Gygax lens consumes the corpus)
- FR-2 entity-ref binding table (standalone-interpretable sessions)
- FR-5 ledger reconciliation (state matches disk)
- FR-7 Gygax-side handoff brief

### In Scope — secondary (Should Have)
- FR-3 experiential-intent extension wiring
- FR-4 archetype SSOT version-pin + drift detection
- FR-6 seam-adjacent loose ends

### Explicitly Out of Scope
- ❌ **Runnable reference demo** — cut by Practitioner ("too much"); the dungeon demo stays shelved.
- ❌ **Release-hardening (Theme B)** — CI rigor (`test.sh`/character-voice/ruff/mypy in CI, real schema
  enforcement), git tags, LICENSE, `construct.yaml` refresh — deferred to a future cleanup cycle.
- ❌ **Any Gygax-side code** — A2 `/cabal` ingest and A4 `mechanical_intent` schema are *requests* in
  FR-7's brief, never Arneson commitments.
- ❌ **Closing half of the `/voice` feedback loop** (auto-feeding the corpus into workshop goals) —
  later cycle / Gygax-side.
- ❌ **Reviving the dormant TTRPG narrative skills** (`/narrate`, `/scene`, `/improvise`, `/fragment`).
- ❌ A shared `@loa/*` package or shared identity base between the constructs.

### Priority Matrix
| FR | Priority | Effort | Impact |
|----|----------|--------|--------|
| FR-1 decision-trace emitter | P0 | L | High |
| FR-2 binding table | P0 | L | High |
| FR-5 ledger reconciliation | P0 | S | Med |
| FR-7 handoff brief | P0 | S | Med |
| FR-3 extension wiring | P1 | M | Med |
| FR-4 archetype drift | P1 | S | Med |
| FR-6 loose ends | P1 | S | Low |

> **Sources:** scope confirmed in discovery (Generate-as-scoped; demo cut; Theme B deferred).

---

## Risks & Mitigation

| ID | Risk | Prob | Impact | Mitigation |
|----|------|------|--------|------------|
| R-1 | **OQ-1**: the sim event log may not carry the `offered` option set, only `chosen` — if so FR-1 needs an additive serializer extension (or honest `offered:[chosen]` flag) | Med | Med | Probe the dungeon-crawl `moves.json` early; `/architect` decides pure-projection vs additive extension before build (`decision-trace-emitter-brief.md:43-50,77-79`) |
| R-2 | Vendor pin reconciliation: observed-trace/taxonomy pinned at `3fa6c91`, decision-trace at `95ccf21` — drift guard must stay green for all four files | Med | Low | Decide per-file vs wholesale pin in FR-1; guard test covers all four (`decision-trace-emitter-brief.md:41`) |
| R-3 | Gygax-side items (A2/A4) stall outside Arneson's control | Med | Low | FR-7 brief is self-contained; Arneson's producer side works regardless of Gygax action (NFR-1) |
| R-4 | Binding-table / ingest semantics are ultimately Gygax-owned; the consumer may want different semantics | Med | Med | Arneson ships the *producer offer* with documented preferences; final ingest contract is Gygax's (FR-2, FR-7) |
| R-5 | Ledger reconciliation may reveal "shipped" code that is actually incomplete | Med | Med | Verification-gated: confirm deliverables on disk before marking done; document residue rather than rubber-stamp (FR-5) |
| R-6 | A+C is ~3–4 sprints; partial completion risk | Med | Low | MVP spine (FR-1/2/5/7) is P0; Should-Haves (FR-3/4/6) trim first if pressed |

### Assumptions
- [ASSUMPTION] The cycle-006 decision-trace brief is still the intended spec for FR-1 — if stale, FR-1 grows.
- [ASSUMPTION] "Improving Arneson" = seam + hygiene above, **not** reviving the dormant TTRPG narrative skills.
- [ASSUMPTION] C3's loose ends belong bundled here rather than in a separate `/bug`.

---

## Appendix

### A. Source audit
Three parallel read-only audits (product/feature, engineering/quality, cross-construct seam) over
`construct-arneson` + `construct-gygax`, 2026-06-25. ~30 raw findings deduplicated into Themes A/B/C;
two claimed gaps corrected on verification (`/braunstein` is built, not a stub — 435-line SKILL.md;
`playout-summary` emitter exists — the gap is inline emission, demoted to minor).

### B. Glossary
| Term | Definition |
|------|------------|
| compounding seam | The Arneson→Gygax loop where each construct's output improves the other's next iteration |
| `decision-trace/v1` | Decision-shaped record (`offered`/`chosen`/`t`/`context.segment`) Gygax's revealed-strategy lens consumes |
| `observed-trace/v1` | Reward-hack-shaped sidecar Arneson's sim lane emits today (sibling schema, not consumable by the lens) |
| binding table | Preamble map from Arneson-local `entity_ref`s to labels (+ optional Gygax IDs), enabling standalone interpretation |
| standalone-plus-composable | Each construct works without the other; composition is opt-in amplification, never a hard dependency |
| producer-never-judges | Arneson produces evidence; it never scores/interprets — the judge (Gygax) never produces the evidence it judges |

### C. Bibliography (internal)
- `grimoires/loa/context/decision-trace-emitter-brief.md` — FR-1 spec (cycle-006)
- `grimoires/loa/discovery/seam-strawman.md` — FR-2/FR-7 producer offer
- `grimoires/loa/discovery/gygax-revealed-strategy-seam-verified.md` — empirical seam finding
- `grimoires/loa/archive/2026-06-15-cycle-004-simulation-fidelity/prd.md` — superseded PRD
- `construct.yaml`, `ledger.json`, `experiential_intent.schema.yaml`, `domains/character-voice/adapters/freeside.yaml`

---

*Generated by discovering-requirements (cycle-007). Every requirement traces to a cited source or a confirmed discovery decision.*
