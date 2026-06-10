# Entry Points

## User-facing

- **Quick start**: `/braunstein --newcomer` (construct.yaml:22-24, README.md:72)
- Skill commands: `/voice`, `/distill`, `/arneson`, `/braunstein`, `/scene`, `/narrate`, `/improvise`, `/fragment` (see api-surface.md)
- In-session: `/pause`, `/x-card`, `/resume`, `/break`

## Programmatic

- `python3 domains/character-voice/scripts/ingest_persona.py <persona.md|stdin>` → YAML stdout
- `python3 domains/character-voice/scripts/emit_persona.py --template <md> --state <yaml>` → md stdout
- `domains/character-voice/scripts/test-roundtrip.sh` → exit 0/1

## CI

- `.github/workflows/ci.yaml` on push/PR to main; 3 jobs (arneson-alone, arneson-with-gygax, extension-story); runs `scripts/ci/validate-*.sh`

## Runtime requirements

- No env vars consumed by app-zone code (grep: zero `os.environ`/`getenv` hits)
- Python 3 stdlib only (`re`, `sys`, `typing` — no PyYAML, no pip deps)
- `yq` v4.50.1 (pinned in CI) for validators
- POSIX sh for test-roundtrip.sh; bash for CI validators
