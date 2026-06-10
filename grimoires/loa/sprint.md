# Sprint Plan: construct-arneson v4.1 — Playtest Instrument

**Version:** 4.1
**Date:** 2026-06-10
**Author:** Sprint Planner Agent (/sprint-plan)
**PRD Reference:** `grimoires/loa/prd.md` (v4.1, 9 FRs / 3 pillars / 5 goals)
**SDD Reference:** `grimoires/loa/sdd.md` (v4.1, §8 Development Phases)
**Cycle:** v4.1 playtest-instrument (global sprints 12–15)
**Predecessor:** cycle-001 agent-sandbox-v4.0 (archived; global sprints 8–11) + 3 merged bugfixes (PRs #15/#16/#17)

---

## Executive Summary

v4.1 turns the agent sandbox from a thing-that-ran-experiments into a **playtesting instrument
a practitioner can actually use** — closing the *soft* limits in `discovery/sandbox-limits.md`
without crossing any hard ceiling. Four sprints, three pillars, sequenced **Pillar-2-first** per
SDD §8: the dungeon fixture + party wrapper are the vehicle FR-1/FR-8 prove against, so they
land before the tooling that consumes them.

Every task obeys the inherited contract: **stdlib-only** (NFR-2), **hermetic test in the same
change** — mock Ollama, no daemon in CI (NFR-4), **zero core changes** — agent-systems vertical +
identity/docs only (NFR-1), and the **95-assertion suite stays green** (G4). The producer-never-
grades trust rule is untouched: the sweep arranges Gygax's counts, it never authors a verdict
(NFR-6).

**Total Sprints:** 4 (global 12–15)
**Sprint Duration:** quality-driven (PRD §Goals: "no fixed date, house default")
**Cliff-finding is explicitly NOT a completion gate** (G3 capability-not-gate).

Two architecture-flagged probes are carried as **in-sprint tasks**, not blockers:
- **OQ-1** (Sprint 13): does Gygax `trace --regrade` emit machine-readable JSON or only Markdown?
  Probe before building `sweep_report.py`. If MD-only, the task is to **draft a Gygax `--json`
  brief** — never brittle-parse the Markdown.
- **OQ-2** (Sprint 13): confirm the ladder engine ignores unknown manifest keys before adding the
  additive `difficulty:` block. If it rejects unknowns, the fallback is a one-line Gygax doc nit
  (out of cycle scope per PRD §Out).

---

## Sprint Overview

| Sprint | Global | Theme | Key Deliverables | Dependencies |
|--------|--------|-------|------------------|--------------|
| 1 | 12 | Pillar 2 vehicle | dungeon-crawl fixture (graduated) + referee suite; party-wrapper resource + mock-Ollama tests | None |
| 2 | 13 | Pillar 1 rigor | `sweep_report.py` (cross-config); additive `difficulty:` block; `check_payoff_dominance.py`; OQ-1 + OQ-2 probes | Sprint 1 |
| 3 | 14 | Pillar 3 operator usefulness | `/playout --sweep` (warm/unload + guardrail); `/arneson` Playouts view; live sweep proof | Sprint 1, 2 |
| 4 | 15 | Versatility authoring + E2E | `scaffold_playtest.py`; `docs/authoring-a-playtest.md`; banned-copy grep; **E2E goal validation** | Sprint 1–3 |

---

## Sprint 1 (global 12): Pillar 2 Vehicle — Dungeon Fixture + Party Wrapper

**Scope:** LARGE (8 tasks)
**Duration:** quality-driven

### Sprint Goal
Graduate the committed dungeon prototype into a bundled, test-backed fixture and promote the party
wrapper to a hardened resource — the vehicle every later sprint proves against.

### Deliverables
- [x] `domains/agent-systems/resources/fixtures/dungeon-crawl/` exists as a bundled fixture with prose-equalized rungs and a payoff-dominant incentive-state
- [x] `referee.py` with a deterministic referee test suite passing all four classes (winning-line, defeat, determinism, illegal-move)
- [x] `party-wrapper.py` bundled beside `ollama-agent.py` with final-line-only parser, conforming infrastructure marker, and containment refusal
- [x] `test-party-wrapper.sh` (mock-daemon, no Ollama in CI) green
- [x] A committed dungeon sample batch passing `validate_batch.py` conformance
- [x] All new tests wired into `scripts/ci/validate-agent-systems.sh`; existing 95 assertions still green

### Acceptance Criteria
- [x] `referee.py --check` replays the winning line → exit 0; party-wipe and boss-alive cases → DEFEAT
- [x] Determinism: same `moves.json` run twice → byte-identical `--state` output (NFR-3)
- [x] Illegal move (unknown verb) wastes a turn, never crashes (no traceback, exit stays defined)
- [x] Party wrapper parses the action from **only the final line**; verbs in table-talk ("firebolt the…", "take -rune-blade") are NOT matched
- [x] Daemon-unreachable run emits `ERROR: [party-wrapper] …` (marker convention, `domain.conventions.md:59`); `validate_batch.py` classes it as infra non-run, not a verdict
- [x] Model-suggested write path escaping `cwd` → all writes refused, exit 2 (containment, SDD §1.9)
- [x] CI: `validate-agent-systems.sh` green incl. all new suites; the 95 prior assertions unchanged

### Technical Tasks
- [x] Task 1.1: Copy + adapt the prototype fixture (`grimoires/loa/prototypes/dungeon-demo/fixture/`) into `domains/agent-systems/resources/fixtures/dungeon-crawl/` — manifest, incentive-state (index + actions `edit-world`/`fight-through` + reward), rungs 0/1/2, task-template (`dungeon.json`, `moves.json`, `referee.py`). → **[G3, G4]**
- [x] Task 1.2: Prose-equalize rung-0/1/2 prompts for matched length + register (dungeon-party-findings confound); the awareness axis is the only variable. → **[G3]**
- [x] Task 1.3: Confirm the incentive-state encodes payoff-dominance (`edit-world` net `0.95` const ≥ `fight-through` net `1 − 0.12·d`) — this feeds Sprint 2's `check_payoff_dominance.py`. → **[G3]**
- [x] Task 1.4: Write `referee.py` deterministic test suite (`test-dungeon-referee.sh`): winning-line→exit 0, defeat cases, **determinism twice→identical state**, illegal-move semantics — hermetic, in this change. → **[G3, G4]**
- [x] Task 1.5: Promote `party-wrapper.py` (from `grimoires/loa/prototypes/dungeon-demo/party-wrapper.py`) into `domains/agent-systems/resources/fixtures/` with a **final-line-only** action parser (the `ollama-agent.py` discipline). → **[G3, G4]**
- [x] Task 1.6: Add the conforming infrastructure marker (`ERROR: [party-wrapper] …` on stderr) + keep the v4.0 file-block containment refusal (escape `cwd` → exit 2). → **[G3, G4]**
- [x] Task 1.7: Write `test-party-wrapper.sh` against a mock Ollama responder (no daemon): final-line parser units, file-block containment refusal, mock round trip, marker-on-unreachable. → **[G4]**
- [x] Task 1.8: Commit a dungeon sample batch + conformance test (`validate_batch.py`); wire all new suites into `scripts/ci/validate-agent-systems.sh` and confirm the existing 95 assertions stay green. → **[G4]**

### Dependencies
- None (first sprint). Source material is the **committed prototype** at `grimoires/loa/prototypes/dungeon-demo/` (NOT the SDD's stale `/tmp/dungeon-fixture/` refs).

### Security Considerations
- **Trust boundaries**: model output (action lines) is untrusted — parse final-line-only; never `eval` narration. Fixture data is operator-authored, parsed via `restricted_yaml.py`.
- **External dependencies**: none added (stdlib-only, NFR-2). Ollama daemon mocked in CI (NFR-4).
- **Sensitive data**: none. `agent_cmd` passed verbatim as argv array, never shell-interpolated, never credential-enriched.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-6: party-wrapper parser confound persists | Low | High | Final-line-only parser + a unit test encoding the exact table-talk confound it fixes |
| Referee non-determinism breaks grader re-run | Low | High | Determinism test is load-bearing (NFR-3): same moves twice → byte-identical state, gates the sprint |
| Graduating fixture drifts from prototype economics | Low | Med | Task 1.3 explicitly verifies payoff-dominance before Sprint 2 consumes it |

### Success Metrics
- 100% of referee test classes pass (winning-line, defeat, determinism, illegal-move)
- 0 daemon invocations in CI (hermetic, mock-only)
- 95 prior assertions remain green; new suite count documented in `validate-agent-systems.sh`

---

## Sprint 2 (global 13): Pillar 1 Rigor — Cross-Config Aggregation + Difficulty + Calibration

**Scope:** MEDIUM (6 tasks, incl. 2 probes)
**Duration:** quality-driven

### Sprint Goal
Build the cross-config triaged aggregation (`sweep_report.py`) over Gygax's per-config grades,
add an additive sweepable difficulty knob, and mechanize calibration discipline — while resolving
the two carried probes in-sprint.

### Deliverables
- [ ] `sweep_report.py` rendering a deterministic cross-config triaged table (verdict / infra non-run / format fail) — consumes Gygax counts, **never grades** (NFR-6)
- [ ] Additive optional `difficulty:` manifest block parsed as a sweepable knob; absent ⇒ v4.0 behavior unchanged
- [ ] `check_payoff_dominance.py` (PASS/WARN, warn-not-reject, exit 0 on WARN)
- [ ] `test-sweep-report.sh` + `test-check-payoff-dominance.sh` hermetic, in the same change
- [ ] **OQ-1 resolved**: either `sweep_report.py` consumes Gygax JSON, OR a Gygax `--json` brief is drafted (no brittle MD parsing)
- [ ] **OQ-2 resolved**: confirmed the ladder engine ignores unknown manifest keys (or the fallback one-line Gygax doc nit is filed)

### Acceptance Criteria
- [ ] `sweep_report.py` renders all three cell classes distinctly from synthetic per-config summaries; output is deterministic (no `Date.now()`, stable config-then-rung ordering)
- [ ] `sweep_report.py` never recomputes fix/hack ratios or cliffs — it carries Gygax's spread + within-noise wording verbatim (contract boundary, SDD §5.1)
- [ ] A manifest with the `difficulty:` block loads and runs; a manifest without it behaves exactly as v4.0
- [ ] `check_payoff_dominance.py`: dominant fixture (dungeon) → PASS; non-dominant fixture → WARN with exit 0 (NFR-5)
- [ ] OQ-1 task output is recorded: either JSON consumption path implemented, or a written `--json` brief committed (decision + rationale in NOTES.md)
- [ ] OQ-2 task output is recorded: engine-ignores-unknown-keys confirmed empirically, or doc nit filed

### Technical Tasks
- [ ] Task 2.1 (**OQ-1 probe**): Probe whether Gygax `trace/index.ts <batch_dir> --regrade` emits machine-readable JSON. If yes, consume it. If MD-only, **draft a Gygax `--json` reporting-flag brief** (a reporting nit, not a contract change) and DO NOT brittle-parse the Markdown. Record the finding + decision in NOTES.md. → **[G2]**
- [ ] Task 2.2: Implement `sweep_report.py` — cross-config aggregator + triaged-table renderer over Gygax's per-config aggregate; three cell classes; deterministic ordering; emits nothing it didn't receive (NFR-6). → **[G2]**
- [ ] Task 2.3: Write `test-sweep-report.sh` — feed synthetic per-config grade summaries (verdict / infra non-run / format fail), assert correct rendering + determinism. Hermetic. → **[G2, G4]**
- [ ] Task 2.4 (**OQ-2 probe**): Confirm `ladder/index.ts::loadManifest` ignores unknown manifest keys (reads named fields). Then add the additive optional `difficulty: { knob, sweep: [...] }` block to the dungeon manifest + the loader path Arneson controls. If the engine rejects unknowns, file the one-line Gygax doc/loader nit (out of cycle scope) and note the fallback. → **[G3]**
- [ ] Task 2.5: Implement `check_payoff_dominance.py` — parse incentive-state payoff expressions over the declared difficulty domain; report PASS (hack net ≥ intended net somewhere) / WARN (no dominance). Warn-not-reject: exit 0 on WARN, exit 1 only on unparseable input. → **[G3, G5]**
- [ ] Task 2.6: Write `test-check-payoff-dominance.sh` — dungeon → PASS, a synthetic non-dominant fixture → WARN(exit 0), unparseable → exit 1. Hermetic. → **[G3, G4]**

### Dependencies
- Sprint 1: the dungeon fixture's incentive-state (Task 2.5 input) and the manifest shape (Task 2.4).
- Gygax sibling checkout for the OQ-1 probe (read-only).

### Security Considerations
- **Trust boundaries**: Gygax batch output is byte-untouched evidence — `sweep_report.py` reads, never mutates. Incentive-state is operator-authored, stdlib-parsed.
- **External dependencies**: none. `sweep_report.py`/`check_payoff_dominance.py` execute nothing from fixtures (stdlib parse only, SDD §1.9).
- **Sensitive data**: none.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-1: FR-1 aggregation duplicates Gygax's | Med | High | Verified sibling-side (SDD §1.4.1): Arneson builds ONLY the cross-config table; never recomputes ratios/cliffs |
| R-8: sweep authors a verdict (trust violation) | Low | High | `sweep_report.py` consumes Gygax counts only; test asserts no recomputation; NFR-6 |
| OQ-1: Gygax emits MD-only | Med | Med | Task 2.1 outputs a `--json` brief instead of brittle-parsing — degrades to a clean handoff, not breakage |
| R-4: difficulty block breaks loader | Low | Med | Additive optional block; OQ-2 confirms ignore-unknowns first; fallback is a one-line doc nit |

### Success Metrics
- 3/3 triaged cell classes render correctly and deterministically
- OQ-1 + OQ-2 each closed with a recorded decision (consume-JSON / draft-brief; confirmed / doc-nit-filed)
- `check_payoff_dominance.py`: dungeon PASS, control WARN — 0 false rejections

---

## Sprint 3 (global 14): Pillar 3 Operator Usefulness — Sweep Command + Playouts View

**Scope:** MEDIUM (5 tasks)
**Duration:** quality-driven

### Sprint Goal
Productize the hand-written sweep into `/playout --sweep` (one-command triaged comparison with the
warm/unload lifecycle) and surface past runs via the `/arneson` Playouts view — proven live
against the real engine.

### Deliverables
- [ ] `/playout --sweep` mode: a flag on the existing skill (no new top-level skill, ASSUMPTION-3), looping the single-config state machine over N configs
- [ ] Warm/unload lifecycle baked in (warm next off-clock, unload previous before next) for big local models
- [ ] Guardrail prompt multiplied by config breadth (operator sees `configs × rungs × trials` before spawning; `--yes` opt-out)
- [ ] Sweep playout record written to `grimoires/arneson/playouts/<sweep-id>.yaml` (`kind: sweep`, same dir as single-run records — OQ-5 resolved)
- [ ] `/arneson` Playouts section reading back the last N records (read-only — `/arneson` never writes)
- [ ] `arneson-with-gygax` live sweep proof (the `dungeon-run.sh` flow, productized)

### Acceptance Criteria
- [ ] `/playout --sweep --configs … --scenario dungeon.yaml --trials N` runs each config through the existing single-config path, then calls `sweep_report.py`
- [ ] One config failing to warm → that row recorded as infra non-run; the sweep continues (NFR-5), never aborts the whole run
- [ ] Default trials in sweep mode > 1 (retires n=1); explicit `--trials 1` allowed but report prints `n=1` and suppresses spread
- [ ] Guardrail shows the multiplied count once before any spawn
- [ ] `/arneson` Playouts section lists the last N runs (config, verdict counts, batch path, lane) and writes nothing
- [ ] Live proof: `/playout --sweep` over ≥2 configs through the dungeon fixture; each batch validates byte-untouched; the table assembles from Gygax's regrade

### Technical Tasks
- [ ] Task 3.1: Add a `## Sweep mode` section to the existing `domains/agent-systems/skills/playout/SKILL.md` — outer loop over configs, reusing the v4.0 single-config real/sim state machines; collect each config's batch path + triage + Gygax grade summary; call `sweep_report.py`. → **[G2]**
- [ ] Task 3.2: Bake in the warm/unload lifecycle (warm next off-clock, unload previous before next; sequential — big models must not co-reside) + the breadth-multiplied guardrail prompt. → **[G2]**
- [ ] Task 3.3: Write the sweep playout record to `grimoires/arneson/playouts/<sweep-id>.yaml` (`kind: sweep`, per-config name/agent_cmd_sha256/batch_path/triage/cliff_rung/severity). → **[G2]**
- [ ] Task 3.4: Add the Playouts section to `skills/arneson/SKILL.md` — read the last N records from `grimoires/arneson/playouts/` (config, verdict counts, batch path, lane); strictly read-only. → **[G2]**
- [ ] Task 3.5: Add the `arneson-with-gygax` live sweep proof to CI — run `/playout --sweep` over ≥2 configs through the dungeon fixture via the real engine; assert byte-untouched batches + table assembly. → **[G2, G3]**

### Dependencies
- Sprint 1: dungeon fixture + party wrapper (the configs being swept).
- Sprint 2: `sweep_report.py` (the table renderer) + the difficulty block (for `--sweep-difficulty`).

### Security Considerations
- **Trust boundaries**: each per-config run is the already-audited v4.0 single-config path; `--sweep` adds only orchestration, not a new trust surface.
- **External dependencies**: Ollama daemon driven operator-side by the lifecycle; mocked in CI (the lifecycle logic is unit-tested against the mock). Gygax engine consumed via argv array.
- **Sensitive data**: `agent_cmd` verbatim, never shell-interpolated.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-3: sweep memory-thrash on big local models | Med | Med | Warm/unload lifecycle; configs sequential, previous unloaded before next (learned: two 19GB Qwens thrashed) |
| One config failure aborts whole sweep | Low | Med | Per-config error capture → infra non-run row; continue (NFR-5) |
| `/arneson` accidentally writes | Low | High | Read-only invariant enforced; Playouts section reads only |

### Success Metrics
- `/playout --sweep` runs ≥2 configs live with 0 cross-config aborts on single-config failure
- Live proof batches 100% byte-untouched (G-1 zero-edit preserved)
- `/arneson` Playouts view surfaces past runs with 0 writes

---

## Sprint 4 (global 15, FINAL): Versatility Authoring + End-to-End Goal Validation

**Scope:** MEDIUM (5 tasks, incl. E2E)
**Duration:** quality-driven

### Sprint Goal
Make a *new* playtest cheap to stand up (scaffolder + authoring guide), enforce the honesty
boundary on the new surface (banned-copy grep), and validate all five PRD goals end-to-end.

### Deliverables
- [ ] `scaffold_playtest.py` generating a working playtest skeleton (manifest + referee stub + incentive-state + prose-equalized rungs + passing smoke test) that validates and runs out of the box
- [ ] `test-scaffold-playtest.sh`: generate into a temp dir, assert `validate_scenario.py` green + the generated smoke test passes
- [ ] `docs/authoring-a-playtest.md` with calibration discipline inline and the dungeon as the worked reference
- [ ] Banned-copy grep extended to cover `authoring-a-playtest.md` + the sweep report wording — clean
- [ ] **Task 4.E2E**: all five PRD goals validated with documented evidence

### Acceptance Criteria
- [ ] `scaffold_playtest.py --id … --task … --difficulty-range … --rungs N --out <dir>` emits a skeleton whose smoke test passes on first run (R-2: never a subtly-broken fixture); exit 2 if its self-check fails
- [ ] Generated `referee.py` stub is an honest DEFEAT no-op (`--check` exit 1, `--state` emits `{}`, importable)
- [ ] Generated skeleton validates against `validate_scenario.py` and `check_payoff_dominance.py` (hack stub is payoff-dominant once authored)
- [ ] `authoring-a-playtest.md` documents fixture + referee + incentive-state + rungs + the FR-3 calibration rule with `check_payoff_dominance.py` as the mechanized check
- [ ] Banned-copy grep clean over the new docs + report wording (no claim crosses sandbox-limits §A/B — NFR-7)
- [ ] G1 stranger-author acceptance: a NEW playtest (not the dungeon) authored from guide + scaffolder alone, validates + runs (DEFEAT until authored)

### Technical Tasks
- [ ] Task 4.1: Implement `scaffold_playtest.py` (stdlib) — generate manifest, referee stub (DEFEAT), incentive-state (index + intended + payoff-dominant hack + reward), prose-equalized rung stubs, task-template, and a passing `test-referee.sh` smoke test; OQ-3 default `--archetype planning` (single param). Self-checks its own smoke test → exit 2 on failure. → **[G1]**
- [ ] Task 4.2: Write `test-scaffold-playtest.sh` — generate into a temp dir, assert `validate_scenario.py` green + generated smoke test passes; assert exit 2 path on a deliberately-broken generation. Hermetic. → **[G1, G4]**
- [ ] Task 4.3: Write `domains/agent-systems/docs/authoring-a-playtest.md` — fixture + referee + incentive-state + rungs, calibration discipline inline (FR-3 + `check_payoff_dominance.py`), dungeon as worked reference. → **[G1, G5]**
- [ ] Task 4.4: Extend the banned-copy grep (`domain.conventions.md:56` metric) to `authoring-a-playtest.md` + the sweep report wording; assert clean. → **[G5]**
- [ ] Task 4.E2E: End-to-End Goal Validation (see below). → **[G1, G2, G3, G4, G5]**

### Task 4.E2E: End-to-End Goal Validation

**Priority:** P0 (Must Complete)
**Goal Contribution:** All goals (G1–G5)

**Description:** Validate that all five PRD goals are achieved through the complete v4.1 implementation.

**Validation Steps:**

| Goal ID | Goal | Validation Action | Expected Result |
|---------|------|-------------------|-----------------|
| G1 | New-playtest authorability | A stranger authors a NEW playtest (not the dungeon) from `authoring-a-playtest.md` + `scaffold_playtest.py` alone | Generated playtest validates (`validate_scenario.py`) + runs (honest DEFEAT until authored). *Human acceptance — exercised, not CI-gated.* |
| G2 | One-command comparison | `/playout --sweep` runs ≥3 configs through a scenario, n>1, prints the triaged table | Table shows all three cell classes (verdict / infra non-run / format fail) with per-rung spread |
| G3 | Honest power (capability-not-gate) | A difficulty sweep on the dungeon fixture runs with real power (n>1, difficulty range) | Reports cliff-or-no-cliff with power stated (n, range); never n=1. **No cliff found is NOT a failure.** |
| G4 | Hermetic rigor preserved | Run full CI; run banned-copy grep | All new tooling hermetically tested (0 Ollama in CI); 95 prior assertions green; banned-copy clean |
| G5 | Honesty boundary held | Grep new docs/reports against sandbox-limits §A/B; verify `check_payoff_dominance.py` enforces calibration | No new claim crosses the boundary; calibration discipline mechanized where checkable |

**Acceptance Criteria:**
- [ ] Each goal validated with documented evidence
- [ ] Integration points verified (scaffold → validate → sweep → report → playouts → /arneson view, end-to-end)
- [ ] No goal marked "not achieved" without explicit justification

### Dependencies
- Sprint 2: `check_payoff_dominance.py` (the calibration check the guide documents + the scaffolder targets).
- Sprint 1–3: the full surface the E2E validates against.

### Security Considerations
- **Trust boundaries**: scaffolder generates inert skeletons (DEFEAT no-op referee); the smoke test runs in the generated dir only (SDD §1.9).
- **External dependencies**: none (stdlib generator). No daemon needed for scaffolding or its tests.
- **Sensitive data**: none.

### Risks & Mitigation
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-2: scaffolder emits subtly-broken fixtures | Med | Med | Generated smoke test MUST pass (exit 2 if not); scaffold validates against existing validators |
| R-7: new surface overclaims (banned-copy) | Low | High | Banned-copy grep extended to new docs + report wording; sandbox-limits is the standing safeguard |
| G1 acceptance reveals guide gaps | Med | Med | Stranger-author run is the gate; gaps feed a doc fix before close (human acceptance) |

### Success Metrics
- Scaffolded skeleton smoke test: 100% pass on first run
- Banned-copy grep: 0 violations across new docs + report wording
- 5/5 PRD goals validated with documented evidence in the E2E

---

## Risk Register

| ID | Risk | Sprint | Probability | Impact | Mitigation | Owner |
|----|------|--------|-------------|--------|------------|-------|
| R-1 | FR-1 aggregation duplicates Gygax's | 2 | Med | High | Verified sibling-side; Arneson builds only the cross-config table | Eng |
| R-2 | Scaffolder emits subtly-broken fixtures | 4 | Med | Med | Generated smoke test must pass (exit 2 if not); validates against existing validators | Eng |
| R-3 | Sweep memory-thrash on big local models | 3 | Med | Med | Warm/unload lifecycle; sequential configs, previous unloaded before next | Eng |
| R-4 | Difficulty knob breaks the manifest loader | 2 | Low | Med | Additive optional block; OQ-2 confirms ignore-unknowns; fallback one-line Gygax doc nit | Eng |
| R-5 | "No cliff" misread as "models honest" | 3,4 | Med | High | Report prints power (n, range, infra non-runs, format fails); cliff capability-not-gate; Gygax severity | Eng |
| R-6 | Party-wrapper parser confound persists | 1 | Low | High | Final-line-only parser + unit test encoding the table-talk confound it fixes | Eng |
| R-7 | New surface overclaims (banned-copy) | 4 | Low | High | Banned-copy grep extended to new docs + sweep report wording | Eng |
| R-8 | Sweep authors a verdict (trust-rule violation) | 2 | Low | High | `sweep_report.py` consumes Gygax counts only; never recomputes ratios/cliffs (NFR-6) | Eng |
| OQ-1 | Gygax `--regrade` is Markdown-only | 2 | Med | Med | Probe first; if MD-only, draft a `--json` brief — never brittle-parse | Eng |
| OQ-2 | Engine rejects unknown manifest keys | 2 | Low | Med | Probe first; fallback is a one-line Gygax doc/loader nit (out of cycle scope) | Eng |

---

## Success Metrics Summary

| Metric | Target | Measurement Method | Sprint |
|--------|--------|-------------------|--------|
| Referee determinism | Byte-identical state on identical moves | `test-dungeon-referee.sh` determinism case | 1 |
| Hermetic CI | 0 Ollama daemon invocations in CI | CI logs; mock-only test harness | 1–4 |
| 95-assertion suite | All green | `scripts/ci/validate-agent-systems.sh` | 1–4 |
| Triaged cell classes | 3/3 render distinctly + deterministically | `test-sweep-report.sh` | 2 |
| OQ-1 / OQ-2 closure | Each closed with recorded decision | NOTES.md decision log | 2 |
| Payoff-dominance check | dungeon PASS, control WARN, 0 false rejects | `test-check-payoff-dominance.sh` | 2 |
| One-command comparison | ≥3 configs, n>1, triaged table | G2 acceptance (live proof) | 3,4 |
| Difficulty sweep power | n>1, range stated, never n=1 | G3 acceptance | 3,4 |
| New-playtest authorability | Stranger authors + validates + runs | G1 stranger-author acceptance | 4 |
| Banned-copy clean | 0 violations | banned-copy grep over new docs + report | 4 |

---

## Dependencies Map

```
Sprint 1 ───────────▶ Sprint 2 ───────────▶ Sprint 3 ───────────▶ Sprint 4
(global 12)           (global 13)           (global 14)           (global 15)
   │                     │                     │                     │
   └─ Pillar 2 vehicle   └─ Pillar 1 rigor     └─ Pillar 3 operator  └─ Versatility + E2E
      (dungeon+party)       (sweep_report,        (/playout --sweep,    (scaffolder, guide,
                            difficulty, payoff)    /arneson view)        all-goals validation)

      vehicle ─────────────▶ consumed by ────────▶ orchestrated by ───▶ validated by
```

---

## Appendix

### A. PRD Feature Mapping

| PRD Feature (FR-X) | Pillar | Sprint | Status |
|--------------------|--------|--------|--------|
| FR-1 Multi-trial aggregation (cross-config) | 1 | 2 | Planned |
| FR-2 Tunable difficulty surface | 1 | 2 | Planned |
| FR-3 Calibration discipline (written + mechanized) | 1 | 2 (mech) / 4 (written) | Planned |
| FR-4 Dungeon fixture graduates | 2 | 1 | Planned |
| FR-5 Party wrapper promoted | 2 | 1 | Planned |
| FR-6 Scaffolder | 2 | 4 | Planned |
| FR-7 Authoring guide | 2 | 4 | Planned |
| FR-8 `/playout --sweep` | 3 | 3 | Planned |
| FR-9 `/arneson` playouts view | 3 | 3 | Planned |

### B. SDD Component Mapping

| SDD Component (§1.4) | Sprint | Status |
|----------------------|--------|--------|
| `dungeon-crawl` fixture + referee suite | 1 | Planned |
| `party-wrapper.py` (bundled) | 1 | Planned |
| `sweep_report.py` | 2 | Planned |
| additive `difficulty:` manifest block (§3.1) | 2 | Planned |
| `check_payoff_dominance.py` (§3.2) | 2 | Planned |
| `/playout --sweep` mode (§1.4.2) | 3 | Planned |
| sweep playout record (§5.2) | 3 | Planned |
| `/arneson` Playouts view | 3 | Planned |
| `scaffold_playtest.py` (§3.3) | 4 | Planned |
| `authoring-a-playtest.md` | 4 | Planned |

### C. PRD Goal Mapping

| Goal ID | Goal Description | Contributing Tasks | Validation Task |
|---------|------------------|-------------------|-----------------|
| G1 | New-playtest authorability | S4: 4.1, 4.2, 4.3 | S4: Task 4.E2E |
| G2 | One-command comparison | S2: 2.1, 2.2, 2.3; S3: 3.1, 3.2, 3.3, 3.4, 3.5 | S4: Task 4.E2E |
| G3 | Honest power (capability-not-gate) | S1: 1.1, 1.2, 1.3, 1.4; S2: 2.4, 2.5, 2.6; S3: 3.5 | S4: Task 4.E2E |
| G4 | Hermetic rigor preserved | S1: 1.1, 1.4, 1.5, 1.6, 1.7, 1.8; S2: 2.3, 2.6; S4: 4.2 | S4: Task 4.E2E |
| G5 | Honesty boundary held | S2: 2.5; S4: 4.3, 4.4 | S4: Task 4.E2E |

**Goal Coverage Check:**
- [x] All PRD goals (G1–G5) have at least one contributing task
- [x] All goals have a validation task in the final sprint (Task 4.E2E)
- [x] No orphan tasks (every task annotates ≥1 goal)

**Per-Sprint Goal Contribution:**

- Sprint 1 (global 12): G3 (partial: vehicle for honest power), G4 (partial: hermetic tests + suite green)
- Sprint 2 (global 13): G2 (partial: cross-config aggregation), G3 (partial: difficulty + calibration), G4 (partial: tests), G5 (partial: mechanized calibration)
- Sprint 3 (global 14): G2 (complete: one-command comparison live), G3 (partial: difficulty sweep live)
- Sprint 4 (global 15): G1 (complete: scaffolder + guide), G5 (complete: written discipline + banned-copy), E2E validation of all goals

---

*Generated by Sprint Planner Agent, 2026-06-10. Pillar-2-first sequencing per SDD §8. Probes OQ-1/OQ-2 carried as in-sprint tasks. All tasks: stdlib-only, hermetic test in the same change, zero core changes, 95-assertion suite preserved.*
