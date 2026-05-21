# Software Design Document: construct-arneson v3.4

**Version:** 3.4
**Date:** 2026-05-20
**Author:** Architecture Designer Agent (/architect)
**Status:** Draft
**PRD Reference:** `grimoires/loa/prd.md` (v3.4, 2026-05-20)
**Predecessor:** SDD v3 (2026-05-12) — core/vertical split + character-voice domain

> v3.4 is a **delta document**. Only sections that change from v3 are specified here.
> For unchanged sections (directory structure, core schemas, protocols, TTRPG vertical,
> CI matrix, etc.), the v3 SDD remains canonical.

---

## What Changes in v3.4

| Area | Change Type | SDD Section |
|------|-------------|-------------|
| character-voice domain scripts | NEW (3 files) | [1](#1-scripts-layer) |
| character-voice fixture | NEW (1 file) | [2](#2-synthetic-fixture) |
| /voice SKILL.md | UPDATED (script wiring) | [3](#3-skill-wiring) |
| domain.conventions.md | UPDATED (scripts reference) | [3](#3-skill-wiring) |

---

## 1. Scripts Layer

### 1.1 New Directory: `domains/character-voice/scripts/`

```
domains/character-voice/
  scripts/
    ingest_persona.py     # persona.md -> voice-character YAML
    emit_persona.py       # voice-character YAML -> persona.md (both layers)
    test-roundtrip.sh     # round-trip validation
  resources/
    fixtures/
      test-persona.md     # synthetic fixture (Compass character)
```

### 1.2 Technology

| Component | Tech | Justification |
|-----------|------|---------------|
| Ingest/emit | Python 3.10+ | Standard library only (no PyYAML). Regex-based parsing. |
| YAML serialization | String formatting | Values are strings/lists/dicts — hand-rolled serializer is safe. |
| Round-trip test | POSIX shell | Consistent with `scripts/ci/*.sh`. |

### 1.3 Ingest Script (`ingest_persona.py`)

**Interface:**
```bash
python3 ingest_persona.py <path>        # file arg
cat persona.md | python3 ingest_persona.py  # stdin
# stdout: voice-character YAML
# stderr: diagnostics
# exit: 0 success, 1 parse error, 2 sync violation
```

**Three parsing layers:**

1. **Frontmatter**: Regex between `---` delimiters. Extracts metadata per `freeside.yaml:114-123`.

2. **Reference body**: Section-level parser. Each adapter extract type maps to a function:

| Extract Type | Function | Pattern |
|-------------|----------|---------|
| `first_italic_line` | `extract_first_italic(text)` | `\*(.+?)\*` first match |
| `list_items` | `extract_list_items(text)` | `^\s*[-*]\s+(.+)$` multiline |
| `bullet_rules` | `extract_bullet_rules(text)` | list_items → `{rule, severity}` objects |
| `key_value_bullets` | `extract_kv_bullets(text)` | `^\s*[-*]\s+(.+?)\s*->?\s*(.+)$` |
| `structured_fields` | `extract_structured(text)` | Key-value from prose patterns |
| `subsection_list` | `extract_subsections(text)` | `###` headers within `##` section |
| `bullet_descriptions` | alias for `list_items` | Same pattern |
| `bullet_items` | alias for `list_items` | Same pattern |

3. **System prompt template**: Locate 4-backtick block under `## System prompt template`. Extract DON'T section bullets as `anti_patterns`.

**Section navigation:**
- `find_section(text, header_level, header_text)` → text between header and next same-level header (or EOF)
- `find_subsection(section_text, sub_pattern)` → text between `### sub` / `**sub**` and next similar delimiter

**Manual fields** (`tensions`, `engagement`, `meta_voice`) are omitted from output — populated by LLM during workshop.

### 1.4 Emit Script (`emit_persona.py`)

**Interface:**
```bash
python3 emit_persona.py --template original.md < state.yaml
python3 emit_persona.py --state state.yaml --template original.md
# stdout: complete updated persona.md
# exit: 0 success, 1 parse error, 2 sync violation
```

**Section-level editor** (not full rewrite — PRD NF-3):

1. Read original persona.md as template
2. Read voice-character YAML (regex-based parser for ingest-compatible subset)
3. Update **reference body** sections per `freeside.yaml:133-166`:
   - `## OG voice anchor` → italic line
   - `## battle whispers` → win/lose/draw bullet lists
   - `### decline patterns` → key-value bullets
   - `### yield patterns` → key-value bullets
   - `## world presence` subsections → bullet lists
   - `## exemplars` → exchange blocks (unlimited)
4. Update **system prompt template** per `freeside.yaml:168-207`:
   - `VOICE CANON` → win/lose/draw dot-separated
   - `DON'T` → bullet list
   - `CANON BOUNDARY` → knows/doesn't-know
   - `TOOL USE` → decline phrases
   - `EXEMPLARS` → max 5 exchange pairs (most recent by `captured_at`)
5. Validate sync contract (`freeside.yaml:218-234`): all 5 dual-target fields present in both layers
6. Output complete file to stdout

**Section replacement**: Find section boundaries → keep header → replace content → preserve non-mapped sections verbatim.

### 1.5 YAML String Quoting

Always double-quote string values. Escape embedded `"` as `\"`. Handles colons, `#`, special chars in voice anchors (e.g., "NOW.", "...recalculating.").

### 1.6 Error Handling

| Exit Code | Meaning | Trigger |
|-----------|---------|---------|
| 0 | Success | Clean parse/emit |
| 1 | Parse error | Missing required section, malformed frontmatter |
| 2 | Sync violation | Dual-target field in YAML but target section missing |

Diagnostic format:
```
ERROR: [ingest|emit] {description}
  file: {path}
  section: {section header}
```

Optional fields missing from persona.md → omitted from YAML (not an error).
Only `voice_anchors.og_line` is required per schema validation rules.

---

## 2. Synthetic Fixture

### 2.1 Character: Compass (Guild Cartographer)

**Path:** `domains/character-voice/resources/fixtures/test-persona.md`

A terse cartographer NPC who speaks in directional metaphors. Exercises:

| Feature | How Exercised |
|---------|--------------|
| Frontmatter (7 fields) | Complete YAML header |
| OG voice anchor | `*North is earned.*` |
| Battle whispers (3 registers) | win (2), lose (2), draw (1) |
| Speech patterns / cadence | Terse, directional, clipped |
| Navigator pattern | player_side: always, forbidden phrases |
| Decline patterns | 3 entries, one multi-line |
| Yield patterns | 2 entries, one with attitude qualifier |
| Canon boundary | knows (3), does_not_know (3) |
| Modes | greeting, expedition (2 modes) |
| Exemplars | 2 exchange pairs |
| System prompt template | All 5 marker sections |

### 2.2 Round-Trip Invariant

The fixture must satisfy: `ingest(fixture) | emit(--template fixture) == fixture` (modulo trailing whitespace).

---

## 3. Skill Wiring

### 3.1 SKILL.md Updates

**Step 1 (Source detection)** gains concrete invocation:
```
When --source file contains "## System prompt template":
  python3 domains/character-voice/scripts/ingest_persona.py <path>
```

**Step 5 (Exit/write-back)** gains concrete invocation:
```
When writing back to persona.md source:
  python3 domains/character-voice/scripts/emit_persona.py --template <original-path>
```

Content-based detection (presence of `## System prompt template`), not extension-based.

### 3.2 domain.conventions.md

Add "Scripts" section documenting the ingest/emit tooling and the hybrid model.

---

## 4. Open Questions

| ID | Question | Recommendation |
|----|----------|----------------|
| OQ-1 | Add round-trip test to CI? | Recommend yes — trivial to wire into `arneson-alone` job |
| OQ-2 | YAML quoting: always double-quote? | Yes — covers all voice anchor edge cases |
| OQ-3 | Update domain.conventions.md? | Yes — add Scripts section |

---

*Generated by Architecture Designer Agent, 2026-05-20*
*Delta from SDD v3. Predecessor sections remain canonical.*
