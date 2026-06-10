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

### Changed
- construct.yaml: registered the `agent-systems` domain (skills: `playout` — lands Sprint 2),
  its schema group, and vendored-contract pins. Zero core-surface changes (FR-1).

## [3.3.0] — 2026-06-09 (predecessor line)

Freeside adapter exemplar capture + v3.4 adapter implementation (ingest/emit scripts,
round-trip test). See git history (`v3.3/exemplar-capture`, PRs #10-12) for detail; this file
starts with the v4.0 cycle.
