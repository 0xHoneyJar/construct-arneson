# Contributing to construct-arneson

Thank you for your interest in contributing to construct-arneson.

## How to Contribute

1. **Open an issue** describing the change you'd like to make.
2. **Fork the repo** and create a branch for your work.
3. **Follow existing patterns** — read `domains/ttrpg/domain.conventions.md` for the extension interface.
4. **Run CI locally** before submitting a PR:
   ```bash
   ./scripts/ci/validate-construct.sh
   ./scripts/ci/validate-schemas.sh
   ./scripts/ci/validate-fallbacks.sh
   ./scripts/ci/validate-fixture.sh
   ./scripts/ci/validate-skills.sh
   ```
5. **Submit a PR** with a clear description of what changed and why.

## Adding a New Domain Vertical

See `docs/EXTENSION-GUIDE.md` for a step-by-step guide. The key principle: new domains are added by creating files in `domains/{name}/` — no core code changes required.

## Code Standards

- **Schemas**: YAML with `schema.name`, `schema.version`, and `schema.extends` (for extensions).
- **Skills**: `SKILL.md` + `index.yaml` per skill. Follow core protocols.
- **Identity**: Do not modify core identity files for domain-specific concerns.
- **Safety**: Safety is non-negotiable. Do not weaken safety requirements in any contribution.

## What NOT to Change

- `schemas/core/` — core schemas are stable. Propose changes via issue first.
- `protocols/` — core protocols govern all domains. Changes affect everyone.
- `identity/` — identity reframes require deep discussion.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
