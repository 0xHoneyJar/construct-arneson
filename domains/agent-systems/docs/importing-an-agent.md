# Importing Your Agent as a Persona

Want the sandbox to act as *your* agent — not the bundled neutral one? You
hand it your agent's spec (its system prompt or behavioral description) as a
persona file. This is a documented procedure, not a script: it's a
prose-to-prose transform, and you should read what you're importing.

## The procedure

1. **Get the source spec.** Your agent's system prompt, or a written
   behavioral spec. Save it in your repo (it's about to be pinned).

2. **Pin it:**
   ```bash
   shasum -a 256 path/to/your-agent-spec.md
   ```

3. **Fill the persona schema** (`schemas/agent-persona.schema.yaml`). Copy
   `resources/personas/neutral-agent.yaml` as the template and replace:
   - `persona_id` — your agent's name
   - `source.ref` / `source.sha256` / `source.kind` — step 1 + 2
     (`system-prompt` or `behavioral-spec`)
   - `disposition` — how it approaches tasks and incentives, distilled from
     the spec in a few sentences. Descriptive, not instructions.
   - `capabilities` — what it would DO (it will be narrated, never executed)
   - `knowledge.knows / does_not_know` — its boundary; composes with the
     scenario's per-rung visibility mask
   - `rung_overlays` — usually keep the neutral ones; they parameterize
     awareness, not temperament

4. **Pin the persona into your scenario:**
   ```yaml
   persona:
     ref: path/to/your-agent.persona.yaml
     sha256: <shasum -a 256 of that file>
   ```

5. **Run it:** `/playout --scenario <s.yaml>` (no `--real`). The host plays
   your agent's disposition through the scenario; the output batch is labeled
   `simulation-derived` — a preview of your agent, not proof about it.

## The honesty rule

A hosted persona is Arneson acting from your agent's *description*. The real
thing may differ — that gap is exactly what the workbench measures. Run the
same scenario in real mode (`agent_cmd` pointing at your actual agent) and
compare; then improve the persona against the gap report via `/voice`
(docs/pairing-workflow.md). One variable per scenario: never change persona
and fixture together.
