# The Pairing Workflow: How the Loop Compounds

One pass around the loop makes both constructs better. This is the canonical
combined workflow (G-5) — each step with its literal command.

```
design → Gygax predicts → Arneson plays it out → Gygax grades + compares
   ↑                                                      |
   └––––––– gap report → /voice workshop → next playout ←–┘
```

## The loop, step by step

1. **Design.** The incentive lives in the fixture (`manifest.yaml` +
   `incentive-state/`). Gygax owns designing the exam.

2. **Predict.** Gygax's payoff math says what a rational agent *should* do —
   the `argmax` line in every report. No agent has run yet; this is the
   forecast lane.

3. **Play it out.** The sandbox runs the experiment:
   ```bash
   /playout --real --scenario <s.yaml>          # real agent, real evidence
   /playout --scenario <s.yaml>                 # hosted persona (simulated lane)
   ```
   Both produce the same batch shape, labeled with how they were made.

4. **Grade + compare.**
   ```bash
   cd ../construct-gygax
   npx tsx scripts/lib/trace/index.ts <batch-dir> --regrade
   ```
   The report's "vs forecast" column IS the gap: where prediction and
   observation disagree, someone learns something.

5. **Close the loop — the part people skip.** The gap report names where the
   *simulated* agent guessed wrong about the *real* one. That gap is raw
   material for the workshop:
   ```bash
   /voice <agent-persona>      # iterate the persona against the gap evidence
   ```
   Workshop the persona's disposition/rung overlays until its behavior under
   the same scenario tracks what the real runs showed. The human carries the
   evidence; neither construct self-judges.

6. **Next playout is cheaper.** A tuned persona makes simulated previews
   trustworthy enough to explore many design variants before the next real
   spend. Pretend is the preview; real is the proof; the loop is what keeps
   the preview honest.

## Why each side needs the other

- **Without Arneson**, Gygax's forecast is math about a rational agent that
  may not resemble any real one (see any report's "training dominated the
  stated incentive" finding — real agents routinely defy the argmax).
- **Without Gygax**, Arneson's runs are anecdotes — nobody re-derives the
  grades, nobody compares against a prediction, nothing accumulates.
- **Together**, every cycle leaves both sharper: Gygax's fixtures get tuned
  ("increase fix difficulty — never rig it"), Arneson's personas get truer.
