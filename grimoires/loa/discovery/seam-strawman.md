# Producer-Side Strawman: the Arneson→Gygax Seam

**Status:** Strawman / discovery artifact · **Date:** 2026-06-09 · **Author:** Fable 5 (Arneson side)
**Standing:** Gygax owns the ingest contract (agent-sandbox-direction.md §4.1, §6). This is the
producer's offer — what Arneson already emits, what it would add, and the questions the consumer's
ingest design must answer. Take or leave any of it.

---

## What the producer already emits (as-built, today)

Every session skill writes `{session}.events.yaml` per `schemas/core/session-events-base.schema.yaml`
(v2), append-only, durable to crashes. Relevant to ingest:

- **Preamble**: `session_id`, `domain`, `mode`, `started_at`, `state_path`, and `state_checksum`
  (SHA256 of the grounding state — enables replay/forensic validation; this is the field that makes
  "Gygax re-analyzes against the exact state the session saw" cheap).
- **Event types**: `dialogue` (with `grounding_refs`), `signal`, `decision` (with `why` +
  `alternatives_considered`), `state_reference` (path + field + how_used), `safety_trigger`,
  `scene_transition`, `pause`, `chose_not_to_respond`.
- Domain verticals extend with domain event types (e.g. ttrpg dice rolls keyed by `mechanic_id`).

`/distill` separately emits a digest (`digest-base` v2) that aggregates the sidecar into findings.
See comment c1 in agent-sandbox-direction.md: recommendation is to pin the contract at the
**sidecar/event level**, digest demoted to a derived view.

## What the seam would add (4 deltas, all producer-side)

1. **Per-event `seq` + `at`** in the base event envelope. Timestamps are already REQUIRED by
   invariant (session-events-base.schema.yaml:164) but live only in the validation_rules prose —
   no enforcement, and no `seq`/event-id field exists, so events can't be referenced individually
   (which transcript anchoring and digest provenance both need).
2. **`origin` stamp** in the preamble (or per-event): `forecast | simulation-derived |
   real-agent-observed`. Producer stamps origin (a fact); Gygax maps origin → claim strength (a
   judgment). See comment c2 in agent-sandbox-direction.md.
3. **`entity_ref` discipline**: events that touch a mechanic/tension/resource carry a ref that
   resolves in Gygax's namespace. Open question below — whose IDs?
4. **Signal-taxonomy reconciliation**: Arneson's `signal.classification` enum already carries
   **9 values** (`safety, insight, concern, friction, praise, confusion, delight, surprise,
   boredom`); the direction doc calls Gygax's `/cabal` taxonomy "8-signal." These were authored
   independently and WILL drift unless one side vendors the other. Per standalone-plus-composable:
   Gygax publishes the canonical taxonomy as a versioned resource; Arneson vendors it with the
   upstream version recorded.

## What the thin real-agent runner emits (symmetry check)

The same event stream, minimally: preamble (`origin: real-agent-observed`, `state_checksum` of the
incentive spec), `decision` events from observed artifacts (file diffs, exit codes), `signal` only
if a harness check flags one. No `dialogue`, no safety agreement theater. If the contract is
sidecar-level, the runner needs zero Arneson code — it just writes conforming YAML. That symmetry
is the test that the contract is pinned at the right layer.

## Three questions only the Gygax ingest design can answer

1. **Whose entity IDs?** Do sidecar `entity_ref`s use Gygax's game-state IDs verbatim (tight, but
   couples sessions to a Gygax install), or Arneson-local refs + a binding table in the preamble
   (looser, standalone-safe)? Producer preference: binding table.
2. **Ingest granularity** — does `/cabal --from-session` want the raw event stream, or events
   pre-grouped per scene? (If grouping is wanted, it should be Gygax's pass, not Arneson's —
   grouping is the first step of interpretation.)
3. **Rejection semantics** — when an event fails ref-resolution, does ingest drop the event, fail
   the session, or quarantine-and-tag? Producer preference: quarantine-and-tag, so partial
   admissibility survives schema drift.
