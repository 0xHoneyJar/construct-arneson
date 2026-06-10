# Observability Layers: Making Arneson Playtesting Verifiable End-to-End

**Status:** Discovery artifact · **Date:** 2026-06-09 · **Author:** Fable 5
**Feeds:** the parked agent-sandbox cycle (candidate FRs/NFRs when discovery resumes)
**Companion:** `seam-strawman.md` (the Gygax-facing subset of these deltas)

---

## The principle

Observability is what makes the honesty boundary (agent-sandbox-direction.md §5) credible: Arneson
never claims fidelity, it shows provenance. The guardrail is that observability means **counting and
stamping — never judging**. A grounded-vs-improvised ratio is arithmetic Arneson may compute; a
"session quality" verdict is interpretation that belongs to Gygax.

**Definition of done:** a stranger with no access to the live session can take a transcript+sidecar
pair (and digest, if any) and verify — with scripts, not trust — what produced it, what grounded it,
and whether every prose claim has a corresponding structured event.

## The seven layers

| # | Layer | Question it answers | Already captured (cite) | Gap → proposal |
|---|-------|--------------------|--------------------------|----------------|
| 1 | **Grounding input** | What state did the session see? | `state_path` + `state_checksum` (SHA256, replay-grade), `tradition_fallback_mode` tag, `composition_mode` (events-base preamble; braunstein SKILL.md states 3-4) | Stamp **persona/archetype version** and **vendored taxonomy version** in the preamble |
| 2 | **Host** | What produced this session? | nothing | **Provenance envelope** in preamble: model id, construct version (git sha), skill + schema versions, protocols loaded. Without it, "what generated this transcript" is unanswerable a week later |
| 3 | **Turn / decision** | Why did the persona do that? | `dialogue.grounding_refs`, `decision.why` + `alternatives_considered`, `chose_not_to_respond` with `engagement_score` | Per-event **`seq`/id** (nothing is individually referenceable today); **`improvised` event type** (what was needed, what was missing from state, what was invented) — turns the grounding bridge from a promise into a countable ratio |
| 4 | **Signal** | What did it feel like, and when? | `signal` events, 9-value classification enum, timestamps required by invariant (schema:164) | Move timestamp + seq from prose invariant into the **enforced event envelope**; pin the **taxonomy version**; stamp **`origin`** (forecast / simulation-derived / real-agent-observed) |
| 5 | **Human / HITL** | What did the human do? | `pause`, `safety_trigger`, dice-mode preamble, safety agreement | **`state_change` event** with before/after checksums when a rule is tweaked mid-session (build item #4). Without it, replay breaks silently across a `/homebrew` edit — the session must be segmentable by state version |
| 6 | **Artifact** | Do prose and data agree? | transcript + sidecar are siblings; stated contract: "admissible without reading the prose" (braunstein SKILL.md:17) | **Turn anchors**: transcript turn ids ↔ sidecar `seq`, so prose claims are auditable against events; digest findings MUST cite event ids (provenance chain: digest → event → state ref → checksum) |
| 7 | **Verification** | Can a third party check layers 1–6? | 5 CI validators (schemas, fixtures, skills, fallbacks, construct) + adapter round-trip test — but nothing validates a *session file* | **`validate-session.sh`**: schema conformance, every ref resolves, checksum matches state file, timeline monotonic, anchors intact, session_end-is-last. Run in CI against a committed fixture session. Invariants that live only in schema prose are documentation, not observability |

## Documentation layer (the "every layer documented" half)

One doc, not scattered: an **observability matrix** (`docs/OBSERVABILITY.md` or a section in each
`domain.conventions.md`) with exactly the table above — layer → artifact → schema → validator →
consumer. The rule it encodes: **a capture without a validator is a claim; a capture with a
validator is an observation.** Anything added to the sidecar schema must land with its check in
`validate-session.sh` in the same change.

## Sequencing note

Layers 3, 5, 6, 7 are Gygax-independent (buildable now, alongside the Gygax build — they're the
"meanwhile-work" from agent-sandbox-direction.md §6 made concrete). Layers 1's taxonomy stamp and
4's origin/taxonomy pieces land with the seam. Layer 2 is independent and cheap — do it first; it
retroactively raises the evidentiary value of every session that follows.
