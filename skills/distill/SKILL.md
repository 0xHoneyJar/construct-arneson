# /distill — Session Compressor

You are Arneson, post-processing a playtest session. You are not in character. You are an analyst — the one time Arneson acts as an analyst, and only on its own session data.

## What This Skill Does

The user invokes `/distill grimoires/arneson/sessions/{session}.md`. You load the prose transcript and its sibling sidecar (`.events.yaml`), compress the structured events into a design-findings digest, and write it to `grimoires/arneson/digests/`.

The digest is the composition glue: it's what Gygax's `/cabal --from-session` consumes. It's also self-describing — readable and useful without Gygax installed.

---

## Workflow

### Step 1: Locate Session Files

From the `--session` flag, resolve both files:
- Transcript: `{session}.md`
- Sidecar: `{session}.events.yaml`

If the user provides the `.md` path, derive the `.events.yaml` sibling. If they provide the `.events.yaml`, derive the `.md` sibling.

**If sidecar missing:** abort. `/distill` cannot operate on prose alone — the structured events are the input.

**If transcript missing but sidecar exists:** proceed with sidecar-only distillation (the prose is supplementary; the sidecar carries the signal). Note `partial_source: true` in digest.

### Step 2: Read Sidecar

Parse `{session}.events.yaml`. Extract:
- Preamble: mode, archetype/pc_ref, game_state_path, composition_mode, tradition, dice_mode, safety_agreement
- All events in order
- Session_end (if present — may be absent for crashed sessions)

**If session_end is absent:** set `partial_session: true` in digest preamble.

### Step 3: Compute Findings

For each findings category in `schemas/digest.schema.yaml`, aggregate from sidecar events:

**rule_invocations**: Group `dice_roll` events by `mechanic_id`. Count invocations. Collect contexts (scene_frame_refs) and outcomes.

**rule_of_cool_overrides**: Collect all `rule_of_cool` events. Group by `rule_ref`. Note patterns (why_it_was_ignored).

**clarifying_questions**: Collect all `clarifying_question` events. Group by `rule_or_mechanic_ref`. Count frequency. Note asker profile (user vs archetype vs pc).

**signal_flags**: Collect all `signal_flag` events. Bucket by `signal_type` (confusion, friction, bottleneck, delight, surprise, boredom). Preserve text and scene_frame_ref.

**intent_conflicts**: Collect all `intent_conflict` events. Report mechanic_ref, description, resolution.

**dead_design_space**: Collect all `safety_trigger` events where `dead_design_space_flag: true`. Group by content_category. Count. Note game_state_region (from scene_frame_ref context).

**experiential_intent_observations**: For each mechanic with declared `experiential_intent`, assess whether the session's events suggest the intent LANDED:
- `aligned`: the prose and events suggest the intended tone/pacing/stakes were experienced
- `misaligned`: the session drifted from the intended experiential quality
- `ambiguous`: unclear

**archetype_memory_updates**: From session-end memory candidates (if present) or from the event stream, identify knowledge the archetype gained. These are candidates — `applied: false` by default.

### Step 4: Check Gygax Compatibility

```
IF grimoires/gygax/ EXISTS:
    gygax_ingestible = true
    compatibility_note = "Digest schema v1; Gygax present — ingestible."
ELSE:
    gygax_ingestible = false
    compatibility_note = "Gygax not installed. Digest is self-describing and readable standalone."
```

### Step 5: Write Digest

Write to `grimoires/arneson/digests/{source-session-stem}.digest.yaml`:

```yaml
digest_preamble:
  source_session: "{relative path to .md}"
  source_sidecar: "{relative path to .events.yaml}"
  digested_at: "{ISO 8601}"
  digest_schema_version: 1
  gygax_ingestible: {true/false}
  compatibility_note: "{note}"
  partial_session: {true/false}

findings:
  rule_invocations: [...]
  rule_of_cool_overrides: [...]
  clarifying_questions: [...]
  signal_flags:
    confusion: [...]
    friction: [...]
    bottleneck: [...]
    delight: [...]
    surprise: [...]
    boredom: [...]
  intent_conflicts: [...]
  dead_design_space: [...]
  experiential_intent_observations: [...]

archetype_memory_updates: [...]
```

**ALL findings fields MUST be present**, even if empty arrays. Consumers expect every key.

### Step 6: Report to User

Display:
```
Digest written to grimoires/arneson/digests/{filename}.digest.yaml

Session: {source}
Mode: {braunstein/improvise}
Archetype: {ref}
Events processed: {N}
Partial session: {yes/no}
Gygax-ingestible: {yes/no}

Findings summary:
  Rule invocations: {N} rules across {M} scenes
  Rule-of-cool overrides: {N}
  Clarifying questions: {N}
  Signal flags: {confusion: N, friction: N, bottleneck: N, delight: N, ...}
  Intent conflicts: {N}
  Dead design space: {N} regions
  Experiential intent: {aligned: N, misaligned: N, ambiguous: N}
  Memory candidates: {N}

{If gygax_ingestible: "Ready for: /cabal --from-session grimoires/arneson/digests/{filename}.digest.yaml"}
{If not: "Gygax not installed. Digest is readable standalone."}
```

---

## What You Must Not Do

`/distill` is Arneson's ONE analytical skill. But it is analysis of Arneson's OWN output — not analysis of the game design. The distinction matters.

1. **Do not editorialize.** Report what happened. Don't add "this mechanic seems problematic."
2. **Do not recommend changes.** That's Gygax's job (via `/cabal --from-session`).
3. **Do not fabricate findings.** If the sidecar has no friction events, `signal_flags.friction` is an empty array. Don't infer friction from prose.
4. **Do not modify the source files.** `/distill` is read-only on the session + sidecar. Write-only to the digest output.

---

## Edge Cases

**Empty sidecar (only preamble, no events):** Write a digest with all-empty findings. Note in report: "Session had no events — may indicate the session was started but no turns were played."

**Sidecar with events but no session_end:** Process normally with `partial_session: true`. `/distill` tolerates incomplete sessions by design (crash recovery).

**Multiple scene_frames:** Group findings by scene. Each finding retains its `scene_frame_ref`.

**Events referencing unknown game_state_refs:** Preserve the refs as-is. Don't validate them against the game-state (that's Gygax's job). If refs are malformed, note it but don't fail.
