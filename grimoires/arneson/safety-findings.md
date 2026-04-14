# Safety Findings — construct-arneson

> Project-level append-only log of safety events surfaced during sessions.
> Each entry is a "dead design space" finding — a region of game-state that triggered
> a safety tool for a specific table.
>
> This file is READ-ONLY to Arneson skills beyond append. Designers may summarize
> or export findings elsewhere; never rewrite this file's history.

## Entry Format

```
## {YYYY-MM-DD} — {session-filename}

- **Trigger type**: {x_card | line | veil | script_change_pause}
- **Content category**: {short label}
- **Game-state region**: {location, mechanic, or scene reference}
- **Action taken**: {immediate_halt | off_stage | tone_shift}
- **Table context**: {public / private / unknown, per session preamble}
- **Notes**: {brief description; not a transcript — the transcript is the source of truth}
```

## Entries

*(none yet — populated automatically by session-length skills when safety triggers fire)*
