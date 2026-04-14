# Archetype Fallback Bundle

> **FALLBACK**: These archetype definitions are used by Arneson only when Gygax is
> not installed. When `grimoires/gygax/identity/persona.yaml` (or equivalent Gygax
> SSOT) is detected, it overrides these fallbacks.

## Purpose

Standalone-plus-composable requires Arneson to work without Gygax. But archetype
definitions live in Gygax's SSOT. To bridge this, Arneson ships a minimal fallback
bundle that mirrors Gygax's 9-archetype cabal.

## Names

The 9 archetypes in this bundle are Arneson's best-effort mirror of Gygax's cabal.
Canonical names are owned by Gygax. If an archetype here diverges from Gygax's
canonical definition, Gygax wins when composed; the fallback is re-synced during
Arneson's hardening sprint (see sprint-7, CI fallback-sync-check).

Current fallback roster:

| voice_id | one-line shape |
|----------|----------------|
| newcomer | unrehearsed; high Sight, low Standing; describes before interpreting |
| optimizer | mechanics-first; terse; interrupts |
| chaos-agent | unpredictable; narratively bounded, structurally unbounded |
| storyteller | narrative-first; resists rule arbitration; flowing |
| rules-lawyer | procedural; consults rules continuously |
| explorer | spatial curiosity; "what's behind that door" |
| min-maxer | mechanical optimization; deep system knowledge |
| casual | light engagement; may miss complexity; good-natured |
| contrarian | plays against expected archetype choice |

## Authoring Notes

Each fallback file carries:

```yaml
fallback_source: true
```

This flag lets Arneson's sidecar mark the session as "authored against fallback"
rather than SSOT. Gygax or later tooling can down-weight findings that depended
on fallback-archetype behavior.

## Sync Discipline

- Fallback bundle pinned against a specific Gygax version (see top of each file).
- When Gygax releases a minor version, Sprint-7 CI step flags fallback divergence.
- Do not edit fallbacks without bumping the `pinned_against_gygax` field.

## How Arneson Loads

```
IF grimoires/gygax/identity/persona.yaml EXISTS:
    load Gygax SSOT
    archetype_source = "gygax-ssot"
ELSE:
    load resources/archetypes-fallback/{archetype_ref}.yaml
    archetype_source = "arneson-fallback"
    emit banner: "Running in standalone mode. Archetypes loaded from fallback bundle."
```
