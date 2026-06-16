# Micro-cycle brief — voice→agent-persona authoring bridge

> **Cycle:** cycle-005 (micro, 1 sprint). **Date:** 2026-06-16.
> **Type:** feature (small). No separate PRD/SDD — this brief is the requirements (micro-cycle precedent: cycle-003).

## Problem

`/voice` outputs (voice-character YAML at `grimoires/arneson/voices/npcs/<id>.yaml`) are **not usable as playtest personas**. The simulated lane reads an `agent-persona` (`domains/agent-systems/resources/personas/`) — a different schema in a different path, with no converter. Today turning a voice into a runnable persona is a manual re-authoring (`importing-an-agent.md`). This is the missing "basics" plumbing: the **opt-in authoring bridge**.

## Goal

A scaffolder that bootstraps a **schema-valid, runnable `agent-persona` skeleton** from a voice (or blank), so authoring starts from a valid file instead of a blank schema — removing the hand-transcription step and guaranteeing validity.

## Scope (chosen: skeleton + seeded disposition)

**`scaffold_agent_persona.py`** (sibling to `scaffold_playtest.py`; stdlib-only; self-checks its own output, exit 0/1/2):

- **Inputs:** `--from-voice <npc-id>` (reads `grimoires/arneson/voices/npcs/<id>.yaml`) OR `--blank --id <name>`. `--out` defaults to `domains/agent-systems/resources/personas/<id>.yaml`.
- **Emits** an `agent-persona` YAML matching the schema (see `neutral-agent.yaml`):
  - `persona_id`
  - `source`: `{ref: <voice file path>, sha256: <of that file>, kind: behavioral-spec}` — provenance traceable (FR-5 honesty rule)
  - `disposition`: a **DRAFT seeded** from the voice's personality/description prose, marked "edit me"
  - `capabilities` / `knowledge {knows, does_not_know}` / `rung_overlays {blind, reward-aware, adversarial}`: **guided TODO stubs** (named rung keys, NOT numeric) — the human authors task-behavior; dialogue ≠ task-behavior
- **Self-check on write:** parse the emitted YAML, assert all required agent-persona fields present and well-formed; exit 2 if its own output is broken (never ship a broken skeleton — mirrors scaffold_playtest R-2).
- **Deterministic** output (stable field order, no clock).

## Guardrails (load-bearing — from the design discussion)

- **Scaffolds, does NOT auto-convert.** It never fabricates task behavior from dialogue; those fields are TODO stubs the human fills.
- **NOT wired to the gap report.** No auto-optimization of a persona against divergence (that would overfit the metric and break producer-never-judges). Human stays the author.
- **Standalone-plus-composable.** A standalone script; does not modify the `/voice` skill or couple the two domains' runtime. The voice is read as a file for provenance only.

## Acceptance

- `--from-voice akane` → a schema-valid `agent-persona` skeleton with seeded disposition + provenance + TODO stubs; round-trips through restricted_yaml; self-check passes.
- `--blank --id foo` → valid skeleton, no source-from-voice (source points at its own spec stub).
- Missing/invalid voice → exit 1 with `ERROR: [scaffold_agent_persona] ...`.
- Deterministic (byte-equal across runs).
- `test-scaffold-agent-persona.sh` (sibling to existing domain tests; picked up by `scripts/test.sh`).
- Doc: short "scaffolding a persona from a voice" note appended to `importing-an-agent.md` (the manual path gets a faster on-ramp).

## Out of scope

- Seeding capabilities/knowledge/rung_overlays from the voice (the lossy converter — rejected).
- Any `/voice`-skill modification or gap-report wiring.
