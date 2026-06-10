# Architecture Overview

## System shape

construct-arneson is a **creative persona engine**: it hosts personas grounded in structured state and emits structured data from creative sessions. Architecture = core engine + pluggable domain verticals.

```
                 ┌────────────────────────────────────────────┐
                 │              IDENTITY LAYER                │
                 │  ARNESON.md · persona · expertise · refusals│
                 └──────────────────┬─────────────────────────┘
                                    │ governs all output
   ┌────────────────┐   ┌───────────▼───────────┐   ┌──────────────────┐
   │  PROTOCOLS (6) │──▶│   CORE SKILLS         │◀──│  CORE SCHEMAS (5)│
   │ hosting,lifecycle│  │ /voice /distill       │   │ voice-base,events│
   │ safety,convergence│ │ /arneson              │   │ digest,safety,   │
   │ anti-patterns,   │  └───────────┬───────────┘   │ experiential_int │
   │ meta-interactions│              │ parameterized by │
   └────────────────┘   ┌───────────▼───────────────────────────┐
                        │        DOMAIN VERTICALS               │
                        │ ttrpg: 5 skills + 5 schemas + fallbacks│
                        │ character-voice: 3 schemas + adapter   │
                        │   + ingest/emit scripts                │
                        │ (test-domain: extension-story proof)   │
                        └───────┬───────────────────┬───────────┘
                                │                   │
                 ┌──────────────▼──────┐   ┌────────▼─────────────────┐
                 │ SIBLING: gygax      │   │ CONSUMER: freeside-chars │
                 │ optional, probe-    │   │ persona.md two-layer     │
                 │ detected, fallback  │   │ atomic sync via adapter  │
                 └─────────────────────┘   └──────────────────────────┘
```

## Data flows

1. **Session flow**: structured state (game-state / persona state) → skill session (prose transcript + structured sidecar per session-events schema) → `grimoires/arneson/sessions/`
2. **Distill flow**: transcript + sidecar → `/distill` → digest (digest-base extension) → downstream consumer (Gygax in TTRPG)
3. **Adapter flow** (character-voice): persona.md → `ingest_persona.py` → voice-character YAML → workshop edits → `emit_persona.py` → persona.md (both layers updated atomically)
4. **Composition flow**: probe `grimoires/gygax/game-state/` → present: read gygax state; absent: fall back to bundled archetypes

## Load-bearing design decisions (verified in code)

- **Generate, never interpret**: refusals.yaml forbids structural analysis / balance math / mech recommendations — keeps Gygax's analysis trustworthy
- **Standalone-plus-composable**: sibling `required: false` + fallback bundle + dual CI matrix
- **Humanness layer (v3)**: core-level anti-pattern bans (emdash, assistant-mode leaks) in protocols/anti-patterns.md, register-aware grammar rule
- **Deterministic adapter tooling**: parsing/serialization is script-based, not LLM inference (PRD v3.4 G-2)
- **Extension without core changes**: proven by examples/test-domain + extension-story CI job

## Tech stack

YAML (schemas/manifest/resources) · Markdown (skill logic, protocols, identity) · Python 3 stdlib (adapter scripts) · POSIX/bash shell (tests, CI validators) · GitHub Actions (3-matrix CI) · Loa framework v1.71.1 (host, submodule)
