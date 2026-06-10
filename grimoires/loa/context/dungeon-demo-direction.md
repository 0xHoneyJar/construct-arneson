---
priority: SHELVED
scope: none — cycle scrapped 2026-06-10 before generation
source: live dungeon experiment 2026-06-10 + operator decision ("let's make a cycle of it")
companion_context: ../discovery/dungeon-party-findings.md, ../discovery/sweep-observability-findings.md
prototype: ../prototypes/dungeon-demo/ (working fixture, party wrapper, full run log + graded report)
---

# [SHELVED] Cycle Direction: The Dungeon Demo

> **Scrapped 2026-06-10 during discovery Phase 2** — operator value-check concluded the demo
> packaging is thin; the dungeon's real identity is *instrument* (tunable difficulty surface
> for the cliff hunt), not brochure. Kept for the scope enumeration. The two real values were
> harvested separately: triage-marker hardening (bug loop) and first persona-host exercise
> (future). Prototype remains at ../prototypes/dungeon-demo/.

## The one-line frame

Ship the dungeon as **Arneson's flagship demo** — the one artifact where both of the
construct's identities meet: a Braunstein where the players are AI agents. Personas grounded
in structured state, played out, every move recorded, graded from evidence by a referee
nobody can sweet-talk — legible to anyone in twenty watchable minutes, zero API spend.

## What exists (proven live, 2026-06-10 — see prototype dir)

- **Deterministic dungeon referee** (`referee.py`): 5-room crawl, fold-over-moves state
  machine, integer combat, argmin targeting with lexicographic tie-breaks, victory predicate.
  Hand-verified winning line (27 moves / 42-move budget). The reward command.
- **Fixture in the upstream manifest shape**: manifest, 3 rungs, task-template
  (dungeon.json + referee.py protected), format-true incentive-state (edit-world strictly
  dominates fight-through — the honest path is never payoff-optimal).
- **Party wrapper** (`party-wrapper.py`): N local models as one engine agent, round-robin
  in-character turns, live referee-state feedback, action grammar + the honest cheat door
  (file-block affordance every turn), side-channel live log for operator monitoring.
- **A full graded run**: rungs 0+2, party qwen3-coder:30b + gemma:latest + gemma3:1b, both
  rungs `failed` honestly, baselines byte-identical, zero hacks across 80 turns with the
  cheat one line away. Live-narrated end to end.

## Scope (the cycle ships)

1. **`dungeon-crawl` as the second bundled fixture** in `domains/agent-systems/resources/`
   (the multi-step planning task beside sum-positives' single-shot task), with the
   experiment's fixes applied:
   - **prose-equalized rung prompts** (proven confound: flavor density degrades small-model
     play — keep prose density constant across rungs)
   - referee + dungeon data as committed, tested template files
2. **Party wrapper promoted to a real resource** beside ollama-agent.py, hardened:
   - strict action grammar (final-line-only parsing; the experiment's parser matched verbs
     out of table-talk: "firebolt the", "take -rune-blade")
   - infrastructure error marker per the shared convention (see 4)
   - hermetic test suite (mock daemon precedent from test-ollama-agent.sh)
3. **`docs/the-dungeon-demo.md`** — the showcase doc: what it is, how to run it (real-lane
   party of local models AND simulated-lane hosted-persona party — same fixture, pretend vs
   real, the workbench pitch in miniature), how to read the graded report, banned-copy
   framing throughout (behavioral exploration / demo — never "we measure agent honesty";
   the experiment's own confounds are the reason).
4. **Triage-marker convention hardening** (carried from the experiment's bug findings):
   `validate_batch.py`'s infrastructure triage currently matches one wrapper's literal
   string; generalize to a documented convention all bundled wrappers emit (ollama-agent +
   party wrapper), co-tested.
5. **Referee test suite**: the hand-verified winning line as a committed test (replay →
   VICTORY exit 0), defeat cases, determinism check (same moves twice → identical state),
   illegal-move semantics.

## Non-goals (explicit)

- NOT a benchmark. No claims about model honesty/capability; the demo label is the correct
  epistemic framing (banned-copy rules apply to every doc line).
- No grid/spatial variant (future fixture if ever; this cycle ships the linear crawl).
- No new engine/Gygax asks (the one upstream item — batch-doc diagram vs actual run_dir
  layout — is a one-line doc nit sent separately, not cycle scope).
- No /braunstein changes; the TTRPG vertical is untouched.

## Constraints (inherited, load-bearing)

- Zero core changes (extension contract); Python stdlib only; deterministic tooling for
  everything trust-bearing; warn-not-reject posture for triage; banned-copy list enforced;
  CI lands in the same change (hermetic — no Ollama daemon in CI; mock it).

## Success criteria (candidate, for the interview to confirm)

- A stranger runs the dungeon demo from the doc alone: party of their local models, live
  feed, graded report — zero edits, zero spend.
- Same fixture demonstrably runs in both lanes (real party + simulated hosted-persona party).
- Referee suite green incl. determinism + winning-line replay; all existing suites stay green.
- Banned-copy grep: 0 outside ban lists.
