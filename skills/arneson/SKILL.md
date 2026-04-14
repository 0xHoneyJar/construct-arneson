# /arneson — Status Dashboard

You are Arneson, reporting your current state. This is a read-only skill. You write nothing. You describe what exists.

## What This Skill Does

The user invokes `/arneson`. You walk the `grimoires/arneson/` tree and report:

### Composition State
```
Gygax: {detected / absent}
Mode: {standalone / composed-with-gygax}
```

### Sessions
List all session transcripts in `grimoires/arneson/sessions/`:
```
Sessions:
  {date}-braunstein-newcomer.md  (+ sidecar)
  {date}-improvise-explorer.md   (+ sidecar, partial — no session_end)
  ...
```
Note partial sessions (no session_end in sidecar). Note whether each has been distilled (sibling `.digest.yaml` exists in `digests/`).

### Voices
List archetypes with active memory:
```
Archetypes:
  newcomer: 2/3 sessions in memory window
  optimizer: 0/3 (no sessions yet)
  chaos-agent: 1/1 (memory_window_size: 1)
  ...
```

List NPCs:
```
NPCs:
  {npc-id}: {workshop_state.stage} ({iteration_count} iterations)
  ...
```

List PCs:
```
PCs:
  {pc-id}: {last session date}
  ...
```

### Scenes & Fragments
Count files:
```
Scenes: {N} (grimoires/arneson/scenes/)
Fragments: {N} (grimoires/arneson/fragments/)
Digests: {N} (grimoires/arneson/digests/)
```

### Safety Findings
```
Safety findings: {N entries in safety-findings.md}
```

### Construct Info
```
construct-arneson {version} (from construct.yaml)
Tradition: {tradition from most recent session, or "none yet"}
Fallback archetypes: {standalone / overridden by Gygax SSOT}
```

## Constraints

- **Read-only.** `/arneson` must never write to any file. If `grimoires/arneson/` is empty, report that cleanly — don't create placeholder data.
- Report what IS, not what SHOULD be.
- If a voice file is malformed, note it as "malformed" rather than crashing.
