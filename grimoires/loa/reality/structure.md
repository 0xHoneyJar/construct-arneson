# Structure (annotated, app zone)

```
construct.yaml              # Manifest: skills, domains, schemas, protocols, composition, output_paths
identity/                   # Who Arneson is
  ARNESON.md                #   identity prose
  persona.yaml              #   meta-role voice (banners, prompts, safety interjections)
  expertise.yaml            #   what it does well
  refusals.yaml             #   load-bearing refusals (no analysis, no balance math, no mech recs)
schemas/core/               # 5 domain-agnostic schemas (voice-base v2, events-base v2, digest-base v2, safety v1, experiential_intent v1)
protocols/                  # 6 behavioral contracts (4 declared in manifest + anti-patterns, meta-interactions — DRIFT-2)
skills/                     # 3 core skills: arneson (dashboard), distill (compressor), voice (workshop)
  {skill}/index.yaml        #   metadata + protocol declarations
  {skill}/SKILL.md          #   skill logic (executable source)
domains/
  ttrpg/                    # Reference vertical
    schemas/                #   5 schemas extending core
    skills/                 #   braunstein, scene, narrate, improvise, fragment
    resources/archetypes-fallback/  # 9 standalone archetypes
    domain.conventions.md   #   extension contract
  character-voice/          # v3.2-3.4 vertical (no domain skills until v4)
    schemas/                #   3 schemas extending core (NOT in CI — DRIFT-3)
    adapters/freeside.yaml  #   persona.md adapter spec + sync contract
    scripts/                #   ingest_persona.py, emit_persona.py, test-roundtrip.sh (stdlib Python)
    resources/              #   akane.yaml, akane-canon.yaml, fixtures/test-persona.md
docs/                       # CONSUMER-PATTERNS.md, EXTENSION-GUIDE.md
examples/
  synthetic-fixture/        # game-state + tradition + scene seeds (CI-validated)
  test-domain/              # extension-story proof: domain added with zero core changes
scripts/ci/                 # 5 validators (construct, schemas, fallbacks, fixture, skills)
.github/workflows/ci.yaml   # 3-matrix CI: arneson-alone / arneson-with-gygax(stub) / extension-story
grimoires/arneson/          # Runtime state: sessions, voices, scenes, fragments, digests, changelog, safety-findings
grimoires/loa/              # Loa planning state (prd v3.4, sdd v3.4, sprint plan, context, reality)
```

Module responsibility rule: new domains = new files under `domains/{name}/` only; `schemas/core/` and `protocols/` are stable surfaces (CONTRIBUTING.md:33-34).
