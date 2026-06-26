# Emitting a decision-trace corpus from a sim playout

`emit_decision_trace.py` projects an Arneson **simulated-lane** session
(`session-events-agent` sidecar) into a corpus of `decision-trace/v1` records —
the decision-shaped contract that Gygax's revealed-strategy lens
(`/cabal --observed --strategy`, cycle-012) consumes. This is the **producer
side** of that seam: Arneson produces the forecast corpus; Gygax (the judge) is
the consumer. The judge never produces the evidence it judges.

## Run it

```bash
python3 domains/agent-systems/scripts/emit_decision_trace.py \
  --in <sim-episode.events.yaml> \
  --out <corpus-dir>
```

One `agent_turn` carrying an `action_label` → one `decision-trace/v1` record
(`t` is the decision index within the episode; `context.segment` tracks the
nearest preceding `rung_start.rung_name`). The corpus is deterministic
(sorted-key JSON, no clock/random) and self-validates against the vendored
`schemas/vendor/decision-trace.v1.schema.json`; the script exits `2` rather than
write a corpus that violates the contract.

## Hand it to the lens (the closing proof)

```bash
# from the gygax sibling checkout (its local tsx):
npx tsx scripts/lib/trace/strategy.ts <corpus-dir>
```

The lens reports `Claim strength: simulation-derived`.

## Chosen-only honesty (read this before reading the report)

The sim event log records the move **taken** (`action_label`), not the legal
option set the host presented. So every record's `offered` **equals** its
`chosen`, and `producer.detail` carries an `offered-set-unrecorded` marker
(`emit_decision_trace.py`, SDD §1.2). This means:

- The **contract** seam is closed — Arneson sim output is now *consumable* by the
  lens (it was rejected before: `unknown schema "observed-trace/v1"`).
- The **analysis** is empty — a chosen-only corpus has no alternatives, so there
  is no revealed *preference* (the lens reports 100% pick-rate, "within noise").

Making the join analytically valuable requires capturing the offered option set
at each decision point (a future, additive `offered_labels` field on
`agent_turn`). Until then, do not read "seam closed" as "revealed-strategy now
produces findings."

> Seam finding (empirical): `grimoires/loa/discovery/gygax-revealed-strategy-seam-verified.md`
> Micro-brief: `grimoires/loa/context/decision-trace-emitter-brief.md`
