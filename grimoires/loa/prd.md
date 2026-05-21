# Product Requirements Document: construct-arneson v3.4

**Version:** 3.4
**Date:** 2026-05-20
**Author:** PRD Architect Agent (/plan-and-analyze)
**Status:** Draft
**Predecessor:** PRD v3.2 (2026-05-12) — freeside-characters adapter specification
**Source:** [0xHoneyJar/construct-arneson#7](https://github.com/0xHoneyJar/construct-arneson/issues/7)

---

## Executive Summary

**construct-arneson v3.4** implements the freeside-characters adapter — closing four blocking gaps between the v3.2 spec and executable reality. The v3.2 cycle delivered the adapter specification, consumer declaration, and SKILL.md documentation. This cycle delivers the scripts, fixture, and skill wiring that make `/voice --source persona.md` actually work.

> **Predecessor context:** v3.2 was a spec cycle. All YAML declarations and SKILL.md documentation exist and are committed. What's missing is deterministic parse/serialize tooling and a round-trip-testable fixture.

---

## Problem Statement

`/voice --source persona.md` is documented but cannot execute. The SKILL.md describes format detection, adapter-driven ingest, and atomic two-layer emit — but the LLM has no deterministic tooling to parse markdown sections into voice-character schema fields or reconstruct a valid persona.md from modified state. Without this, the adapter spec is aspirational.

> Sources: user-description.md:4-6, freeside.yaml:1-19, SKILL.md:16-22

---

## Goals

| ID | Goal | Metric | Source |
|----|------|--------|--------|
| G-1 | Round-trip correctness | Ingest persona.md -> extract fields -> emit persona.md -> diff shows both layers updated correctly | Phase 2 confirmation |
| G-2 | Deterministic parsing | Script-based extraction, not LLM inference, for all adapter ingest rules | Phase 1 (hybrid model) |
| G-3 | Atomic two-layer writes | Reference body and system prompt template always updated together | freeside.yaml:235-238 |
| G-4 | Testable fixture | Synthetic persona.md that exercises all mapped fields | Phase 1 (fixture decision) |

---

## Users & Stakeholders

| Persona | Role | Interaction |
|---------|------|-------------|
| **Persona curator** (gumi) | Authors/iterates character voices via `/voice` workshops | Invokes `/voice --source persona.md`, workshops the character, expects changes written back correctly |
| **Freeside bot** (machine consumer) | Loads persona.md at inference time via loader.ts | Reads system prompt template block; must remain valid after Arneson edits |
| **Future adapters** | Other consumers adopting the adapter pattern | Observe this implementation as the reference for new adapters |

> Sources: construct.yaml:57-62, v3.2-freeside-adapter.md:12-13

---

## Functional Requirements

### FR-1: Persona.md Ingest Script

**Priority:** Must Have

**Description:** Python script at `domains/character-voice/scripts/ingest_persona.py` that reads a persona.md file and extracts voice-character schema fields per the adapter spec's ingest rules.

**Acceptance Criteria:**
- [ ] Reads persona.md from stdin or file path argument
- [ ] Extracts YAML frontmatter (metadata fields per freeside.yaml:114-123)
- [ ] Extracts voice_anchors.og_line via `first_italic_line` from `## OG voice anchor`
- [ ] Extracts voice_anchors.win/lose/draw via `list_items` from `## battle whispers` subsections
- [ ] Extracts speech_patterns via `bullet_descriptions` from `## voice discipline lock` > `### cadence`
- [ ] Extracts discipline_locks via `bullet_rules` from `### the Navigator pattern`
- [ ] Extracts navigator_pattern via `structured_fields` from `### the Navigator pattern`
- [ ] Extracts decline_patterns via `key_value_bullets` from `### decline patterns`
- [ ] Extracts yield_map via `key_value_bullets` from `### yield patterns`
- [ ] Extracts canon_boundary.knows/does_not_know via `bullet_items` from `## world presence` subsections
- [ ] Extracts modes via `subsection_list` from `## moments + modes`
- [ ] Extracts anti_patterns via `bullet_items` from system prompt template `DON'T` section
- [ ] Extracts exemplars from `## exemplars (canon-quality exchanges)` if present
- [ ] Outputs valid voice-character YAML to stdout
- [ ] Exits non-zero with diagnostic on malformed input

> Sources: freeside.yaml:22-123

### FR-2: Persona.md Emit Script

**Priority:** Must Have

**Description:** Python script at `domains/character-voice/scripts/emit_persona.py` that takes voice-character YAML state and a persona.md template, and produces an updated persona.md with both layers in sync.

**Acceptance Criteria:**
- [ ] Reads voice-character YAML from stdin or file path argument
- [ ] Reads original persona.md as template (preserves structure, comments, non-mapped sections)
- [ ] Updates reference body sections per emit.reference_body rules (freeside.yaml:133-166)
- [ ] Updates system prompt template sections per emit.system_prompt_template rules (freeside.yaml:168-207)
- [ ] Enforces sync contract: all 5 dual-target fields updated in both layers (freeside.yaml:218-234)
- [ ] Exemplars: unlimited in reference body, max 5 in system prompt (freeside.yaml:199)
- [ ] Computes entire file content before writing (atomic — freeside.yaml:236-238)
- [ ] Writes to stdout (caller handles file I/O) or to specified output path
- [ ] Preserves sections not mapped by the adapter (passthrough)
- [ ] Exits non-zero if sync contract would be violated (e.g., field present in one layer but not the other)

> Sources: freeside.yaml:127-238

### FR-3: Format Detection in /voice SKILL.md

**Priority:** Must Have

**Description:** Update SKILL.md to instruct the LLM to call ingest/emit scripts when `--source` points to a persona.md file, rather than attempting to parse/serialize via LLM inference.

**Acceptance Criteria:**
- [ ] SKILL.md Step 1 (Source detection) instructs: when `--source` file contains `## System prompt template`, invoke `domains/character-voice/scripts/ingest_persona.py <path>` via Bash tool
- [ ] SKILL.md Step 5 (Exit/write-back) instructs: pipe modified YAML through `domains/character-voice/scripts/emit_persona.py --template <original-path>` via Bash tool
- [ ] Format detection is content-based (presence of `## System prompt template`), not extension-based
- [ ] SKILL.md documents the hybrid model: scripts handle parse/serialize, LLM handles the workshop

> Sources: SKILL.md:16-22, Phase 1 (hybrid model decision)

### FR-4: Synthetic Persona.md Fixture

**Priority:** Must Have

**Description:** A synthetic character in persona.md format at `domains/character-voice/resources/fixtures/test-persona.md` that exercises all adapter-mapped fields.

**Acceptance Criteria:**
- [ ] Contains YAML frontmatter with all metadata fields
- [ ] Contains all reference body sections: OG voice anchor, battle whispers (win/lose/draw), voice discipline lock (cadence, Navigator pattern), moments + modes (decline patterns, yield patterns, greeting mode, at least one other mode), world presence (knows/does_not_know), exemplars
- [ ] Contains `## System prompt template` with 4-backtick fenced block including: VOICE CANON, DON'T, CANON BOUNDARY, TOOL USE, EXEMPLARS sections with appropriate markers
- [ ] Character is original (not Akane, not from any private game)
- [ ] Character exercises edge cases: at least one multi-line decline pattern, at least one yield with attitude qualifier, at least 2 exemplars
- [ ] Passes round-trip: `ingest_persona.py fixture | emit_persona.py --template fixture > output && diff fixture output` produces no meaningful diff

> Sources: Phase 1 (synthetic new decision), Phase 2 (round-trip correctness)

### FR-5: Round-Trip Validation Script

**Priority:** Should Have

**Description:** Shell script at `domains/character-voice/scripts/test-roundtrip.sh` that validates the ingest -> emit round-trip.

**Acceptance Criteria:**
- [ ] Runs ingest on fixture, captures YAML output
- [ ] Runs emit with captured YAML against original fixture as template
- [ ] Diffs original and output, reports pass/fail
- [ ] Validates all 5 sync contract fields appear in both layers
- [ ] Exit 0 on pass, exit 1 on fail with diagnostic

> Sources: G-1, FR-4 acceptance criteria

---

## Technical & Non-Functional Requirements

### NF-1: Python Dependencies
- Standard library only (no pip installs). `yaml` module via PyYAML is acceptable if already available; otherwise use regex-based YAML frontmatter extraction.
- [ASSUMPTION] PyYAML is available in the development environment. If not, frontmatter extraction falls back to regex.

### NF-2: Script Interface Convention
- Scripts follow Unix convention: read from stdin or file arg, write to stdout, diagnostics to stderr.
- Exit codes: 0 success, 1 parse error, 2 sync contract violation.

### NF-3: Passthrough Preservation
- Sections in persona.md not mapped by the adapter must survive round-trip unchanged. The emit script is a **section-level editor**, not a full rewrite.

### NF-4: Loader Contract Pinning
- Adapter spec is pinned to freeside loader contract as documented in freeside.yaml:12-19. Version drift is a known risk, detected by round-trip test failure.

> Sources: Phase 1 (pin to spec decision), freeside.yaml:12-19

---

## Scope & Prioritization

### In Scope (v3.4)
- Ingest script (FR-1)
- Emit script (FR-2)
- SKILL.md wiring (FR-3)
- Synthetic fixture (FR-4)
- Round-trip test (FR-5)

### Out of Scope (explicit)
- Real freeside persona testing (requires access to 0xHoneyJar/freeside-characters repo)
- `/distill` integration with freeside consumer format
- Exemplar ranking/scoring heuristics (workshop captures manually)
- `meta_voice` mapping to persona.md (manual/workshop-driven for now)
- CI integration of round-trip test (can be added later)
- Migration tooling for existing freeside personas

---

## Risks & Dependencies

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R-1 | Freeside loader contract has drifted since adapter spec was written | Low | High — emit produces invalid persona.md | Round-trip test (FR-5) detects this; fix adapter spec if drift found |
| R-2 | Markdown section parsing is fragile against real-world persona.md variations | Medium | Medium — ingest fails on edge cases | Fixture (FR-4) exercises edge cases; script reports parse errors clearly |
| R-3 | System prompt template reconstruction loses formatting | Medium | High — bot behavior changes | Emit preserves non-mapped content via passthrough (NF-3) |
| R-4 | PyYAML not available in all environments | Low | Low — fall back to regex frontmatter extraction | NF-1 fallback strategy |
| R-5 | LLM inconsistently invokes scripts despite SKILL.md instructions | Medium | Medium — partial hybrid, unreliable parse | SKILL.md uses explicit Bash tool invocation syntax, not suggestive language |

> Sources: Phase 1 (pin to spec), user-description.md:10-12

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Adapter spec (freeside.yaml) | Complete | v3.2 cycle deliverable |
| Voice-character schema | Complete | v3.2 cycle deliverable |
| Consumer declaration (construct.yaml) | Complete | v3.2 cycle deliverable |
| SKILL.md documentation | Complete | v3.2/v3.3 cycle deliverable |
| Python 3.x runtime | [ASSUMPTION] Available | Standard in dev environments |

---

*Generated by PRD Architect Agent, 2026-05-20*
*Discovery: 7 context files ingested, 5 interview questions across 4 phases, 0 assumptions unresolved*
