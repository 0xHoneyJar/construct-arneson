# Sprint Plan: construct-arneson v3.4

**Version:** 3.4
**Date:** 2026-05-20
**Author:** Sprint Planner Agent (/sprint-plan)
**PRD Reference:** `grimoires/loa/prd.md` (v3.4)
**SDD Reference:** `grimoires/loa/sdd.md` (v3.4)
**Predecessor:** Sprint Plan v3.2 (complete — adapter spec cycle delivered)

**Total Sprints:** 2
**Starting Point:** v3.3 complete (exemplar capture). Adapter spec, consumer declaration, SKILL.md docs all committed. No scripts or fixtures exist yet.

---

## Sprint Overview

| Sprint | Theme | Scope | Key Deliverables |
|--------|-------|-------|------------------|
| 1 | Fixture + Ingest Parser | MEDIUM (5 tasks) | Synthetic persona.md, ingest script, directory scaffolding |
| 2 | Emit + Wiring + Validation | MEDIUM (5 tasks) | Emit script, round-trip test, SKILL.md wiring, docs |

---

## Sprint 1: Fixture + Ingest Parser

**Scope:** MEDIUM (5 tasks)

### Tasks

- [ ] **1.1** Create directory scaffolding: `domains/character-voice/scripts/` and `domains/character-voice/resources/fixtures/`. [G-4]
- [ ] **1.2** Author `domains/character-voice/resources/fixtures/test-persona.md` — Compass (Guild Cartographer). Terse cartographer NPC with directional metaphors. Must include: complete YAML frontmatter (7 fields), `## OG voice anchor` (`*North is earned.*`), `## battle whispers` (win: 2, lose: 2, draw: 1), `## voice discipline lock` with `### cadence` and `### the Navigator pattern`, `## moments + modes` with `### decline patterns` (3 entries, one multi-line), `### yield patterns` (2 entries, one with attitude qualifier), `### greeting mode`, `### expedition mode`, `## world presence` (knows: 3, does_not_know: 3), `## exemplars` (2 exchange pairs), `## System prompt template` with 4-backtick block containing all 5 marker sections. [FR-4, G-4]
- [ ] **1.3** Implement `domains/character-voice/scripts/ingest_persona.py` — core infrastructure. Section navigator (`find_section`, `find_subsection`), frontmatter regex extraction, YAML serializer (string formatting, double-quoted values per SDD 1.5), error handling (exit 0/1/2, stderr diagnostics), stdin/file-arg interface. Python 3.10+, stdlib only. [FR-1, G-2]
- [ ] **1.4** Implement extract functions in `ingest_persona.py`: `extract_first_italic` (og_line), `extract_list_items` (win/lose/draw/canon/modes), `extract_bullet_rules` (discipline_locks), `extract_kv_bullets` (decline_patterns, yield_map), `extract_structured` (navigator_pattern), `extract_subsections` (modes). System prompt template parser for DON'T → anti_patterns. [FR-1, G-2]
- [ ] **1.5** Integration validation: run `python3 ingest_persona.py test-persona.md`, verify exit 0, all 12 field groups present, correct values. Fix parsing issues. [FR-1, G-2, G-4]

### Acceptance Criteria

- [ ] Fixture contains all sections from FR-4 with edge cases exercised
- [ ] Character is original (Compass, not Akane or private game)
- [ ] `ingest_persona.py` extracts 12 field groups from fixture
- [ ] `python3 ingest_persona.py test-persona.md` exits 0 with valid YAML on stdout
- [ ] Python stdlib only, no pip installs

---

## Sprint 2: Emit + Wiring + Round-Trip Validation

**Scope:** MEDIUM (5 tasks)

### Tasks

- [ ] **2.1** Implement `domains/character-voice/scripts/emit_persona.py` — section-level editor. Read original persona.md as template, read voice-character YAML (regex-based parser). Update reference body: `## OG voice anchor` (italic line), `## battle whispers` (win/lose/draw lists), `### decline patterns` (kv bullets), `### yield patterns` (kv bullets), `## world presence` subsections (bullet lists), `## exemplars` (exchange blocks, unlimited). Update system prompt template: VOICE CANON (dot-separated), DON'T (bullet list), CANON BOUNDARY (knows/doesn't-know), TOOL USE (decline phrases), EXEMPLARS (max 5, most recent by captured_at). Atomic output to stdout. `--template` and `--state` flags. Exit 0/1/2. [FR-2, G-1, G-3]
- [ ] **2.2** Implement sync contract validation in `emit_persona.py`. Before output, verify 5 dual-target fields (decline_patterns, anti_patterns, voice_anchors, canon_boundary, exemplars) present in both layers per `freeside.yaml:218-234`. Exit 2 if dual-target field in YAML but target section missing from output. [FR-2, G-3]
- [ ] **2.3** Implement `domains/character-voice/scripts/test-roundtrip.sh` — POSIX shell. Ingest fixture → pipe to emit → diff against original (ignore trailing whitespace). Validate all 5 sync contract markers in output. Exit 0 pass, exit 1 fail with diagnostic. `chmod +x`. [FR-5, G-1, G-4]
- [ ] **2.4** Update `skills/voice/SKILL.md` — Step 1: when `--source` contains `## System prompt template`, invoke `python3 domains/character-voice/scripts/ingest_persona.py <path>` via Bash tool. Step 5: pipe modified YAML through `python3 domains/character-voice/scripts/emit_persona.py --template <original-path>`. Add hybrid model note. Content-based detection, not extension-based. [FR-3, G-2]
- [ ] **2.5** E2E validation + docs. Run `test-roundtrip.sh` (G-1). Verify ingest is deterministic (G-2). Verify emit updates both layers (G-3). Verify fixture exercises all fields (G-4). Update `domains/character-voice/domain.conventions.md` with Scripts section. CHANGELOG entry for v3.4. [G-1, G-2, G-3, G-4]

### Acceptance Criteria

- [ ] `emit_persona.py` produces valid persona.md with both layers updated
- [ ] Sync contract validation exits 2 on deliberately broken input
- [ ] `test-roundtrip.sh` exits 0 — round-trip produces no meaningful diff
- [ ] Non-mapped sections survive round-trip unchanged (NF-3 passthrough)
- [ ] Exemplar budget: max 5 in system prompt, unlimited in reference body
- [ ] SKILL.md contains exact script invocation commands
- [ ] domain.conventions.md documents adapter scripts

---

## PRD Feature Mapping

| PRD Feature | Sprint | Task(s) |
|-------------|--------|---------|
| FR-1: Ingest Script | 1 | 1.3, 1.4, 1.5 |
| FR-2: Emit Script | 2 | 2.1, 2.2 |
| FR-3: SKILL.md Wiring | 2 | 2.4 |
| FR-4: Synthetic Fixture | 1 | 1.1, 1.2 |
| FR-5: Round-Trip Test | 2 | 2.3 |

## Goal Mapping

| Goal | Contributing Tasks | Validation |
|------|-------------------|------------|
| G-1: Round-trip correctness | 2.1, 2.3, 2.5 | `test-roundtrip.sh` passes |
| G-2: Deterministic parsing | 1.3, 1.4, 2.4 | Ingest produces YAML without LLM |
| G-3: Atomic two-layer writes | 2.1, 2.2 | Emit updates both layers, sync validated |
| G-4: Testable fixture | 1.2, 1.5, 2.3 | Fixture passes round-trip |

---

*Generated by Sprint Planner Agent, 2026-05-20*
