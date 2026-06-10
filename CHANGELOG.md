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
