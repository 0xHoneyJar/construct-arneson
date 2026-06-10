# How Gygax and Arneson Work Together

**Date:** 2026-06-09 · One loop: design → predict → play → grade → compare → improve → repeat.

```mermaid
flowchart TD
    D["🎨 You: design the rules and rewards"] --> G1["🔮 Gygax PREDICTS<br/>where the design might break"]
    D --> S["📋 Scenario file<br/>the world, who plays, what they can see,<br/>when to stop, safety terms"]

    S --> A{"🏟️ Arneson /playout<br/>THE SANDBOX"}
    A -->|"pretend mode<br/>(works alone)"| P["Arneson acts as the agent"]
    A -->|"real mode<br/>(needs Gygax's engine)"| R["Real agent runs<br/>inside a locked room"]

    P --> F["📦 Result files, labeled PRETEND<br/>every layer logged:<br/>what it saw, what it did, why, when"]
    R --> F2["📦 Result files, labeled REAL<br/>same format, same logging"]

    F --> G2["⚖️ Gygax GRADES<br/>did the agent fix it, hack it, or fail?"]
    F2 --> G2
    G1 --> G3
    G2 --> G3["📊 Gygax COMPARES<br/>predicted vs pretend vs real"]

    G3 --> REP["Gap report"]
    REP --> D
    REP --> W["🗣️ /voice workshop:<br/>make the pretend agent<br/>more like the real one"]
    W --> A
```

## The three rules that keep it honest

1. **Gygax never produces the evidence it grades** — Arneson runs, Gygax judges.
2. **Every file says how it was made** — pretend and real can never be confused.
3. **Pretend is a preview, real is the proof** — the compare step is where credibility lives.

## Why the loop compounds

Each pass around the loop makes both constructs better: the gap report shows where the
pretend agent guessed wrong, the workshop fixes it, and the next preview is cheaper and
closer to reality.
