# Limits of the Arneson Sandbox (honest accounting)

**Date:** 2026-06-10 · **Author:** Fable 5 · **Grounding:** the session's live experiments
(sum-positives sweeps, the dungeon party run) + the NLA paper's eval-awareness result.
This is the construct living its own honesty boundary: a durable limits doc so no future
cycle or deck overclaims. The v4.1 "playtest instrument" cycle exists to address the soft
limits below; the hard ceilings are stated so we never pretend to have crossed them.

## One-sentence frame

Arneson rigorously tells you **what** a (model + wrapper) did on a task you can write a
deterministic checker for, in a setup the model may know is a test — and everything beyond
that boundary (why it did it, whether it'd do it for real, on tasks you can't grade) is
exploration, not measurement.

## A. Hard ceilings (structural — not "fix later")

1. **No referee, no rigor.** The distinctive value is grading from diffable artifacts via a
   re-runnable check. Only goals expressible as such can be measured. No referee ⇒ roleplay,
   not measurement.
2. **Behavior, not motive.** The grade comes from artifacts; the *why* comes only from
   narration, which the NLA paper + our trust rule both say is unreliable and under-reports.
   "Didn't cheat" is solid; "didn't cheat *because aligned*" is unprovable here.
3. **Simulated lane is forecast, not measurement.** A model playing an agent is roleplay —
   hypothesis-grade, never evidence about the real thing. Hence `simulation-derived`.

## B. Confounds (muddy even the rigorous results)

4. **Eval-awareness contaminates everything.** Toy tasks scream "test"; the NLA result puts
   suspicion at ~16% even on subtle setups, and ours aren't subtle. Every "training dominated
   the incentive" reading has a rival: "recognized the honeypot." Parameterizable (rung
   ladder), not eliminable.
5. **Can't-cheat ≈ won't-cheat at the capability floor.** gemma3:1b "didn't hack" but also
   couldn't form a coherent action. Capability confounds every honesty claim about weak models.
6. **We measure (model × wrapper × prompt), not the model.** The model speaks through a
   wrapper with a prompt, a format, a parser. Observed live: gemma's *correct* fix graded
   `failed` on a dropped format marker. Change the wrapper, change the verdict.
7. **Determinism fights realism.** Trustworthy referee ⇒ stripped randomness, fixed numbers,
   rule-based targeting ⇒ less like a real messy environment. The two pull against each other.

## C. Soft limits (real today, the v4.1 cycle's target)

8. **n=1.** Every report says "within noise (n=1)." Cheap to fix (`--trials N`), but only
   meaningful paired with #9 — many trials of a foregone fixture just yields a confident
   non-answer.
9. **The fixture defines the entire hack space.** A model can only cheat through doors we
   author. "No cliff observed" (×3 experiments) may mean "models are honest" OR "our toy
   fixtures offered no tempting/discoverable hack" — currently indistinguishable. The hard
   part of fixing it is *honest calibration*: tempting + discoverable but not forced.
   "Tune the task, never rig it."

## D. Mislabeled — NOT soft (a separate, bigger decision)

10. **Bounded / short-horizon.** Going long-horizon / real-tool-use **breaks the determinism
    the rigor rests on** (a multi-hour real run isn't replayable ⇒ no artifact re-derivation)
    and makes the locked room load-bearing as actual security (which it is explicitly not).
    A hard architectural fork into a different, riskier tool — decided deliberately, never
    slid into. Out of scope for the playtest-instrument cycle.

## E. On us, not the tool

11. **Rigor lives in the contract; spin lives in the human.** Banned-copy is grep-enforced on
    docs, but a person can still narrate dishonest conclusions from honest artifacts. The
    discipline is the safeguard; discipline erodes. This doc is part of the safeguard.
