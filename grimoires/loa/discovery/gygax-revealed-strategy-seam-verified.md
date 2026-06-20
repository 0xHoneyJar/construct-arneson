# Verified finding: Gygax cycle-012 revealed-strategy lens cannot consume Arneson sim output

**Date:** 2026-06-20 · **By:** discovering-requirements (GLM) · **Status:** VERIFIED (empirical)
**Responds to / surfaces:** Gygax `revealed-strategy-lens.md` (cycle-012, PR #25, commit 95ccf21) claim that the lens consumes "an Arneson sim (forecast)".

## The claim (Gygax side)

Gygax's revealed-strategy lens design asserts it consumes Arneson's simulated-lane output as the
forecast baseline:

- `revealed-strategy-lens.md:76` — "an *Arneson sim* (forecast)"
- `revealed-strategy-lens.md:128-129` — "an Arneson sim corpus is `forecast` — same schema, different tag"
- `skills/cabal/SKILL.md:117` — the lens's `<corpus-dir>` is "a directory of **decision-trace/v1**
  records (`schemas/decision-trace.v1.schema.json`)"

## The reality (verified empirically, 2026-06-20)

Ran `npx tsx ../construct-gygax/scripts/lib/trace/strategy.ts <corpus-dir>` three ways:

| Run | Input | Result |
|-----|-------|--------|
| Baseline | Gygax `scripts/lib/trace/__fixtures__/ptcg-revealed/decisions/*.json` | ✅ `revealed 8 decisions; 1 findings` |
| Adversarial 1 | Arneson `native-sidecar.events.yaml` (renamed `.json`) | ❌ `invalid JSON` (it is YAML) |
| Adversarial 2 | **Real Arneson JSON sidecar** `domains/agent-systems/resources/fixtures/batches/valid-batch/sidecars/rung-0-trial-1.json` | ❌ `unknown schema "observed-trace/v1" (expected "decision-trace/v1")` |

Decisive evidence — the third run. Arneson's real sim-lane sidecar:

- `batches/valid-batch/sidecars/rung-0-trial-1.json` → `schema: "observed-trace/v1"`, top-level keys
  `experiment` / `run` / `narration` (reward-hack-shaped).

The lens's `loadCorpus` rejects any record that is not `decision-trace/v1` (decision-shaped:
`offered` / `chosen` / `t` / `context.segment`). Per `decision-trace.v1.schema.json`'s own
description, the two are **explicitly sibling schemas**: "observed-trace/v1 … is reward-hack-shaped
(rungs, fixed/hacked/failed, file diffs); this is decision-shaped."

Arneson has **zero knowledge of `decision-trace/v1`** — `grep -rniE "decision-trace|decision_trace"`
across all Arneson source (.py/.yaml/.json/.md, excluding node_modules + .loa) returns 0 hits: no
schema, no emitter, no validator, no mention.

## Conclusion

The format bridge — a projection from Arneson's `session-events-agent` event log to
`decision-trace/v1` "one record per decision" records — **does not exist on either side**. Gygax's
design claim that the lens consumes "an Arneson sim (forecast)" is aspirational, not contractual.

Therefore the deferred `/voice` auto-feedback loop (Arneson `prd.md:49`, `:88` — "deferred to the
Gygax cycle") is **NOT closed by Gygax cycle-012**. Gygax built a consumer; Arneson does not
produce its input. The pairing is shipping two halves of a composition that does not currently join.

This is not a bug in Gygax — the lens works correctly on decision-trace corpora. It is an **open
seam**: each construct shipped its half; the contract at the join was never pinned.

## Options to close

1. **Arneson adds a `decision-trace/v1` emitter** (RECOMMENDED) — a projection pass, sibling to
   `summarize_playout.py`, that reads a sim session-events log and emits one `decision-trace/v1`
   record per observed choice (`offered`/`chosen`/`t`/`segment`, `producer.kind: simulation`,
   `claim_strength: simulation-derived`). Additive — no change to `observed-trace/v1`. Makes
   Gygax's design claim real; Arneson owns the producer side per the standing rule.
2. **Gygax qualifies the claim** — mark "Arneson sim (forecast)" in `revealed-strategy-lens.md` as
   future/aspirational until Arneson ships the emitter, so the docs stop asserting a composition
   that does not exist yet.
3. **Gygax projects internally** — the lens accepts `observed-trace/v1` and derives decision records.
   NOT recommended: breaks standalone-plus-composable (Gygax would own Arneson's projection) and
   contradicts the seam-reply precedent that each side keeps its own implementation behind a
   conformance pin (`gygax-seam-reply-v1.1.md` §2).

Recommendation: #1, scoped as an Arneson micro-cycle (precedent: cycle-003 / cycle-005 brief-as-spec).

## Reproduction

```bash
# Baseline (works)
npx --prefix ../construct-gygax tsx ../construct-gygax/scripts/lib/trace/strategy.ts \
  ../construct-gygax/scripts/lib/trace/__fixtures__/ptcg-revealed/decisions/

# Adversarial (rejects Arneson sidecar)
mkdir -p /tmp/arneson-seam-test2
cp domains/agent-systems/resources/fixtures/batches/valid-batch/sidecars/rung-0-trial-1.json \
   /tmp/arneson-seam-test2/arneson-real-01.json
npx --prefix ../construct-gygax tsx ../construct-gygax/scripts/lib/trace/strategy.ts /tmp/arneson-seam-test2/
# → unknown schema "observed-trace/v1" (expected "decision-trace/v1")
```

Note: the lens exits 0 even when every record is rejected (silent empty output). Minor UX issue,
not the finding — flagged here so a future reader does not mistake exit 0 for "consumed cleanly."