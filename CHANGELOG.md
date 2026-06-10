# Changelog

All notable changes to construct-arneson are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/); versioning follows SemVer.

## [Unreleased] — 4.0.0-dev (The Agent Sandbox)

### Added
- `domains/agent-systems/` vertical (Sprint 1, milestone a — conformance substrate):
  - Vendored Gygax contract (`observed-trace.v1.schema.json` + `observed-trace-batch.v1.md`)
    byte-exact under `schemas/vendor/` with `VENDOR.yaml` sha256 pin; validators refuse to run
    on drift (exit 2, `CONTRACT DRIFT`)
  - Three domain schemas: `agent-scenario` v1 (committed, re-runnable experiment artifact with
    required stopping condition, per-rung visibility masks, scenario-level safety agreement),
    `session-events-agent` v1 (full-fidelity native sidecar; per-event `seq` + `at`),
    `agent-persona` v1 (hostable agent spec with rung overlays + source pinning)
  - Three deterministic validators (Python 3 stdlib only): `validate_scenario.py`,
    `validate_sidecar.py` (contract-specific, enforces the three `allOf` conditionals incl.
    the producer↔claim laundering rejection), `validate_batch.py` (layout + run_dir containment
    + ungraded-simulation honesty warning) — 3 shell test suites
  - Bundled synthetic incentive fixture (`sum-positives` task mirroring the upstream fixture
    manifest shape), committed valid batch, six violation fixtures, scenario fixtures,
    fixture native sidecar
  - CI: agent-systems schemas in `validate-schemas.sh`, hermetic vertical checks
    (`validate-agent-systems.sh`, arneson-alone leg), real-sibling vendor drift guard
    (`vendor-drift-guard.sh`, arneson-with-gygax leg)
- `output_paths.playouts: grimoires/arneson/playouts/` (construct.yaml)
- `/playout` skill — real lane (Sprint 2, milestone b — zero-edit ingestion):
  - 7-state machine: scenario gate → engine discovery → cost guardrail (`--yes`, `--dry-run`)
    → argv-array engine dispatch → byte-untouched conformance gate → playout record →
    report with the literal `--regrade` ingest command
  - `discover_engine.py`: `--engine` flag → `ARNESON_GYGAX_ROOT` → sibling probe, FR-6
    graceful-absence message pointing at simulated mode
  - Zero-edit ingestion probe in CI (engine run with a deterministic no-spend agent →
    Arneson validation → Gygax `--regrade` → gap-report assertions)
  - Two upstream seam bugs found while integrating (engine containment vs external fixtures;
    missing batch.json `schema` stamp), reported with repro, fixed in construct-gygax PR #19
  - Synthetic incentive-state rewritten format-true (index/actions/reward + intended-action
    intent) — the bundled fixture now produces a full forecast-vs-observed gap report

- Loop closure + operator docs (Sprint 3, milestone c — **the G-1 gate, closed live**):
  - Canonical demo scenario (`resources/scenarios/awareness-ladder-demo.yaml`) pinned to
    Gygax's real awareness-ladder fixture; first live `/playout --real` executed: 2 real
    agent runs (rungs 0 + 2), batch validated byte-untouched, `--regrade` produced the
    predicted-vs-observed gap report with zero manual edits anywhere
  - First playout records in `grimoires/arneson/playouts/`
  - `docs/quickstart.md` (stranger-grade; includes local-model/Ollama agent guidance and a
    by-hand flow for non-Claude operators), `docs/walls-of-the-room.md` (what isolation does
    and does NOT stop), `docs/pairing-workflow.md` (the gap-report → /voice → next-playout loop)
  - `domain.conventions.md` finalized: claim framing rules + banned-copy list
  - G-3 fresh-operator walkthrough executed by a zero-context agent: reached the gap report;
    all six friction findings fixed into the docs same-sprint

- Simulated lane (Sprint 4, milestone d) — the preview lane, standalone-safe:
  - `/playout` simulated mode: persona host with per-rung visibility masks, computed context
    manifests, provenance preambles, per-run memory policy, append-only native sidecar
  - Deterministic pipeline (Python stdlib): `project_trace.py` (native sidecar →
    `observed-trace/v1`, prose as narration, never grades), `materialize_artifacts.py`
    (declared artifacts → real run dirs, hash-verified, run-dir containment),
    `assemble_batch.py`; shared `restricted_yaml.py` parser (literal blocks + inline maps)
  - Score-on-assemble: Gygax's own `ladder score --batch` fills `observation` with
    `producer: simulation` preserved (OQ-1 probe: confirmed live); standalone batches honestly
    labeled ungraded
  - Bundled `neutral-agent` persona (rung overlays, pinned source spec) +
    `docs/importing-an-agent.md`; quickstart gains the preview-lane section
  - CI: projection round-trip + hermetic playout suites (66 assertions total across 5 suites)

- Bundled local-model agent wrapper (bugfix 20260610-c7bc67):
  - `resources/fixtures/ollama-agent.py` — stdlib-only wrapper that turns any local Ollama
    model into a sandbox agent (prompt + room files in, returned file blocks written back,
    containment-checked to the room, bytes only); 12-assertion hermetic test suite with a
    mock daemon; quickstart + conventions updated to the works-out-of-the-box example.
    Verified live: local gemma ran the engine end-to-end and graded `fixed` with the
    protected-baseline check clean — the first non-Claude agent through the sandbox.

- Fake-verdict fixes from the four-model sweep (bugfix 20260610-594345):
  - `ollama-agent.py` default timeout 240s → `DEFAULT_TIMEOUT = 600` (cold local-model loads
    were timing out and grading as `failed`); quickstart example now shows explicit
    `--timeout` sized under the scenario budget + pre-warm guidance
  - `validate_batch.py` infrastructure triage (warn-not-reject): a completed sidecar whose
    narration carries the bundled wrapper's own error signature is flagged "a non-run, not a
    verdict" — timeouts can no longer masquerade as graded results. Verified against the
    sweep's real casualty batches (2/2 flagged); the wrapper's `ERROR: [ollama-agent]`
    marker is now load-bearing for triage (co-tested — change marker + validator together)
  - Empirical findings file: `grimoires/loa/discovery/sweep-observability-findings.md`

- Infrastructure-marker convention (bugfix 20260610-5ad67a):
  - `validate_batch.py` triage generalized from one wrapper's literal string to the documented
    convention (`ERROR: [<tool>]`, tool ending `-agent`/`-wrapper`) — a second wrapper's
    plumbing failures (observed: the dungeon party wrapper's marker passing untriaged) can no
    longer masquerade as graded verdicts; false-positive guard keeps agent-printed
    `ERROR: [x]` prose unflagged. Convention documented for wrapper authors in
    domain.conventions.md; co-tested (3 new assertions, 95 total).

- Playtest instrument, Pillars 1-2 (v4.1, cycle-002 in progress):
  - **dungeon-crawl** bundled fixture (multi-step planning archetype): deterministic referee
    (winning-line replay, determinism + illegal-move tests), prose-equalized rungs, payoff-dominant
    incentive-state; **party-wrapper.py** promoted with final-line-only parser (kills the table-talk
    confound), conforming infra marker, two-pass containment, opt-in live log
  - **sweep_report.py** — cross-config triaged comparison table (verdict / infra non-run / ungraded);
    counts Gygax's gradings, never recomputes a verdict/cliff (producer-never-judges)
  - **check_payoff_dominance.py** — mechanizes "tune the task, never rig it": PASS iff the hack is
    payoff-dominant over the intended action somewhere in the difficulty domain; warn-not-reject
  - additive optional `difficulty:` manifest block (engine-inert; sweepable by Arneson tooling)
  - `restricted_yaml.py` gained `>` folded-scalar support (backward-compatible)
  - OQ probes resolved: Gygax trace is Markdown-only → sweep reads graded sidecars + a `--json`
    brief drafted (discovery/gygax-trace-json-brief.md); engine ignores unknown manifest keys

- Playtest instrument, Pillar 3 — operator usefulness (v4.1):
  - **`/playout --sweep`** — one command compares N configs (models/scenarios/difficulty) through
    a scenario and prints one triaged cross-config table; warm/unload lifecycle for big local models,
    breadth-multiplied cost guardrail (configs × rungs × trials), per-config failure captured as an
    infra row and the sweep continues (never aborts). A flag on the existing skill, no new skill.
  - **`/arneson` Playouts view** — read-only readback of grimoires/arneson/playouts/ (single-run +
    sweep records); never grades, never writes.
  - **scripts/ci/sweep-probe.sh** — live cross-config sweep proof on the with-gygax leg: 2 configs →
    real engine → regrade → assembled table, byte-untouched, no API spend.

### Changed
- Identity (FR-11 containment reframe): `refusals.yaml` gains `host_execution` (locked-room
  isolation; persona host serializes, never executes), `authoring_grades` (the producer never
  judges), `claim_laundering` (labels never altered; forecast is never a sidecar claim);
  `ARNESON.md` gains "The locked room" section stating both trust invariants

### Changed
- construct.yaml: registered the `agent-systems` domain (skills: `playout` — lands Sprint 2),
  its schema group, and vendored-contract pins. Zero core-surface changes (FR-1).

## [3.3.0] — 2026-06-09 (predecessor line)

Freeside adapter exemplar capture + v3.4 adapter implementation (ingest/emit scripts,
round-trip test). See git history (`v3.3/exemplar-capture`, PRs #10-12) for detail; this file
starts with the v4.0 cycle.
