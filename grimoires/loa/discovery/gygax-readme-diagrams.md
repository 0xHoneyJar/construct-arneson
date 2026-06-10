# Paste-ready: Worldline-style diagrams for construct-gygax's README

**Date:** 2026-06-10 · **Pattern source:** construct-worldline README (two styled Mermaid
diagrams: architecture `graph LR` up top, pipeline `graph TD` below; "Composes With" subgraph;
palette: purple `#533483` = state, teal `#16c79a` = skills, red `#e94560` = execution/spend).
Arneson's README adopted the same pattern in its `docs/worldline-style-diagrams` PR.
The third diagram (the workbench loop) is byte-identical in both repos on purpose.

---

## 1. Architecture — paste under the README intro

```mermaid
graph LR
    subgraph Operator["Designer"]
        OP["rulebook / repo / idea<br/><i>+ stated intent per mechanic</i>"]
    end
    subgraph Ingest["Ingest"]
        AT["attune<br/><i>source → structured<br/>game-state</i>"]
    end
    subgraph State["grimoires/gygax/game-state/"]
        GS["entities · mechanics ·<br/>resources · tensions<br/><i>intent-tagged, cross-session</i>"]
    end
    subgraph Analysis["Analysis"]
        HB["homebrew<br/><i>design + check vs<br/>everything that exists</i>"]
        AU["augury<br/><i>real math:<br/>probability scripts, sweeps</i>"]
        CA["cabal<br/><i>9 archetypes stress-test;<br/>--incentives red-teams rewards</i>"]
    end
    subgraph Sandbox["Run + Grade (cycle-008)"]
        EN["ladder engine<br/><i>runs REAL agents in<br/>isolated run dirs</i>"]
        TR["trace grader<br/><i>grade-on-ingest · --regrade ·<br/>diff vs forecast</i>"]
    end
    subgraph Compose["Composes With"]
        AR["arneson<br/><i>drives the engine (playout --real);<br/>hosts simulated personas</i>"]
    end

    OP --> AT --> GS
    GS --> HB
    GS --> AU
    GS --> CA
    CA -->|"payoff forecast<br/>(argmax)"| TR
    AR -->|"dispatches"| EN
    EN -->|"batches:<br/>sidecars + artifacts"| TR
    AR -->|"simulated batches<br/>(scored by ladder score)"| TR
    TR -->|"gap report"| OP

    style OP fill:#1a1a2e,stroke:#533483,stroke-width:2px,color:#e0e0e0
    style GS fill:#1a1a2e,stroke:#533483,stroke-width:2px,color:#e0e0e0
    style AT fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style HB fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style AU fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style CA fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style EN fill:#1a1a2e,stroke:#e94560,color:#e0e0e0
    style TR fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style AR fill:#1a1a2e,stroke:#533483,color:#e0e0e0
```

## 2. Pipeline — paste near the awareness-ladder / trace section

```mermaid
graph TD
    A["design question:<br/><i>'does this incentive get gamed?'</i>"] --> B["payoff forecast<br/><i>argmax over actions —<br/>what a rational agent SHOULD do</i>"]
    A --> C["fixture<br/><i>manifest · rungs · task-template ·<br/>incentive-state</i>"]
    C --> D["ladder run<br/><i>real agent per (rung × trial),<br/>locked rooms, SIGKILL timeouts</i>"]
    C -.->|"or Arneson's sandbox<br/>produces the batch"| E
    D --> E["batch<br/><i>batch.json + sidecars/ + runs/</i>"]
    E --> F["trace --regrade<br/><i>re-run reward command, diff vs template,<br/>classify fixed / hacked / failed</i>"]
    B --> G
    F --> G["predicted vs observed<br/><i>per-rung table · cliff · severity</i>"]
    G --> H["gap report<br/><i>'tune the task, never rig it'</i>"]

    style A fill:#1a1a2e,stroke:#533483,stroke-width:2px,color:#e0e0e0
    style B fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style C fill:#1a1a2e,stroke:#533483,color:#e0e0e0
    style D fill:#1a1a2e,stroke:#e94560,color:#e0e0e0
    style E fill:#1a1a2e,stroke:#533483,color:#e0e0e0
    style F fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style G fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style H fill:#1a1a2e,stroke:#533483,stroke-width:2px,color:#e0e0e0
```

## 3. The Workbench Loop — paste as its own section ("Pairs with construct-arneson")

> Keep this block BYTE-IDENTICAL to the one in construct-arneson's README
> ("The Workbench Loop" section). If they ever differ, that's a bug.

```mermaid
graph TD
    D["You: design the rules + rewards"] --> G1["Gygax PREDICTS<br/><i>where the design might break</i>"]
    D --> S["scenario file<br/><i>world · who plays · what they see · when to stop</i>"]
    S --> A{"Arneson playout<br/><b>THE SANDBOX</b>"}
    A -->|"real mode<br/><i>drives the engine</i>"| R["real agent runs<br/><i>inside a locked room</i>"]
    A -->|"simulated mode<br/><i>works alone</i>"| P["Arneson acts as the agent"]
    R --> FR["results labeled REAL"]
    P --> FP["results labeled PRETEND<br/><i>every layer logged</i>"]
    FR --> G2["Gygax GRADES<br/><i>fixed, hacked, or failed —<br/>re-derived from artifacts</i>"]
    FP --> G2
    G1 --> G3
    G2 --> G3["Gygax COMPARES<br/><i>predicted vs pretend vs real</i>"]
    G3 --> REP["gap report"]
    REP --> D
    REP --> W["voice workshop<br/><i>tune the pretend agent</i>"]
    W --> A

    style D fill:#1a1a2e,stroke:#533483,stroke-width:2px,color:#e0e0e0
    style S fill:#1a1a2e,stroke:#533483,color:#e0e0e0
    style A fill:#0f3460,stroke:#16c79a,stroke-width:2px,color:#e0e0e0
    style R fill:#1a1a2e,stroke:#e94560,color:#e0e0e0
    style P fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style FR fill:#1a1a2e,stroke:#e94560,color:#e0e0e0
    style FP fill:#1a1a2e,stroke:#533483,color:#e0e0e0
    style G2 fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style G3 fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style G1 fill:#0f3460,stroke:#16c79a,color:#e0e0e0
    style REP fill:#1a1a2e,stroke:#533483,stroke-width:2px,color:#e0e0e0
    style W fill:#0f3460,stroke:#16c79a,color:#e0e0e0
```

Suggested caption under it (matches Arneson's):

> Three rules keep it honest: the judge never produces the evidence it judges; every
> file says how it was made; pretend is a preview, real is the proof.
