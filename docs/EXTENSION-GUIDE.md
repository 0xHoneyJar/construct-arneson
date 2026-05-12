# Extension Guide — Adding a New Domain to Arneson

> Step-by-step guide for adding a domain vertical to construct-arneson.

---

## Prerequisites

- construct-arneson v2 installed
- Familiarity with YAML and the Loa skill-pack pattern
- Your domain's structured state, persona definitions, and event types planned

## The Five-Part Contract

Every domain vertical provides five things:

| # | Part | What You Create |
|---|------|----------------|
| 1 | Structured state | YAML/MD files your domain grounds fiction against |
| 2 | Persona definitions | Voice schema extending `voice-base` |
| 3 | Event taxonomy | Session-events schema extending `session-events-base` |
| 4 | Resolution mechanics | Skills that implement your domain's creative flow |
| 5 | Consumer specification | Digest schema extending `digest-base` |

## Step-by-Step

### 1. Create your domain directory

```
domains/{your-domain}/
  domain.conventions.md           # Document your vertical
  schemas/
    voice-{type}.schema.yaml      # Extend schemas/core/voice-base
    session-events-{name}.schema.yaml  # Extend schemas/core/session-events-base
    digest-{name}.schema.yaml     # Extend schemas/core/digest-base
  skills/
    {skill-name}/
      SKILL.md                    # Follow core protocols
      index.yaml                  # Declare domain, type, protocols
  resources/
    {your domain's resources}
```

### 2. Create your voice schema

Extend `voice-base` with domain-specific fields:

```yaml
schema:
  name: voice-{your-type}
  version: 1
  extends: voice-base
  description: "Your domain's persona type."

additional_fields:
  your_field:
    type: string
    required: true
    description: "What this field captures."
```

All `voice-base` fields (voice_id, speech_patterns, reaction_tempo, emotional_register, memory_slots, known_facts, workshop_state) are inherited automatically.

### 3. Create your event schema

Extend `session-events-base` with domain-specific events:

```yaml
schema:
  name: session-events-{your-domain}
  version: 1
  extends: session-events-base

additional_event_types:
  your_event:
    description: "What this event captures."
    fields:
      field_name: {type: string, required: true}
```

All base events (dialogue, signal, decision, pause, scene_transition, state_reference, safety_trigger) are inherited.

### 4. Create your skills

Each skill MUST:
- Have a `SKILL.md` and `index.yaml`
- Declare compliance with core protocols in `index.yaml`:
  ```yaml
  protocols:
    - persona-hosting
    - session-lifecycle
    - safety-protocol
    - workshop-convergence  # if workshop-type skill
  ```
- Follow the session lifecycle (Invoked → Safety → DomainLoad → PersonaLoad → Active → Closing → Persisted)
- Emit base + domain events to the sidecar

### 5. Create your digest schema

Extend `digest-base` with domain-specific findings:

```yaml
schema:
  name: digest-{your-domain}
  version: 1
  extends: digest-base

{your_domain}_findings:
  your_finding_type:
    type: array
    items: {type: object, fields: {...}}
```

### 6. Register in construct.yaml

Add your domain to the `domains:` section:

```yaml
domains:
  {your-domain}:
    description: "What your domain does"
    skills:
      - {skill-1}
      - {skill-2}
```

### 7. Validate

Run the CI validation scripts to ensure everything parses:
```bash
./scripts/ci/validate-schemas.sh
./scripts/ci/validate-construct.sh
```

## Reference Implementations

- **TTRPG vertical**: `domains/ttrpg/` — the full reference implementation
- **Test domain**: `examples/test-domain/` — minimal working example

## What You Get for Free

By following the five-part contract, your domain automatically gets:
- Safety infrastructure (pre-session agreement, /pause, /x-card, /resume)
- Persona hosting (loading, memory, grounding, consistency)
- Workshop convergence (iterative voice development)
- Session lifecycle management
- Transcript + sidecar output
- `/distill` compression (using your consumer spec)
- `/arneson` status dashboard awareness
