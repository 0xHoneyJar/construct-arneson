# Arneson Producer-Side Commitments (Gygax-Independent)

**Status:** Cross-repo brief · **Date:** 2026-06-09 · **Origin:** construct-arneson discovery
**Audience:** construct-gygax planning. These are the things Arneson will build with **zero
dependency on Gygax's ingest schema** — the Gygax-side design can rely on them as given.
A short list of the decisions Gygax *does* own follows at the end, for contrast.

**Minimal shared context:** every Arneson session emits a prose transcript (`.md`) plus a
structured sidecar (`{session}.events.yaml`, schema `session-events-base` v2) — timestamped
events with grounding references back to the structured state the session ran against, including
a SHA256 `state_checksum` of that state.

---

## The nine commitments

1. **Host provenance envelope.** The sidecar preamble gains: model id, construct version (git
   sha), skill + schema versions, protocols loaded. Answers "what produced this session" forever
   after. Sequenced first — it retroactively raises the evidentiary value of every later session.

2. **Per-event `seq` + enforced `at`.** Timestamps are currently required only by a prose
   invariant; they move into the enforced event envelope, and every event gets a stable sequence
   id. This is what makes individual events *citable* — by digests, by transcripts, and by any
   future Gygax ingest.

3. **`improvised` as a first-class event type.** When state is too thin to ground an action,
   Arneson logs what was needed, what was missing, and what it invented. Turns the grounding
   promise ("when state is thin, Arneson says it's improvising") into a countable
   grounded-vs-improvised ratio per session.

4. **`state_change` event for mid-session edits.** When the human pauses and tweaks a rule, the
   sidecar records the transition with before/after state checksums. Sessions become segmentable
   by state version; replay never silently spans a rule change.

5. **Standalone human-in-the-loop path.** Pause → hand-edit the state file → resume works with no
   sibling installed. Gygax `/homebrew` is the amplified path, not a dependency.

6. **Transcript↔sidecar turn anchors.** Prose turns carry ids matching sidecar `seq`, so every
   prose claim is auditable against a structured event.

7. **Digest provenance chain.** Whatever role the digest ends up playing in the seam, its findings
   will cite event ids — giving a full chain: digest → event → state ref → state checksum.

8. **Mechanical session validator in CI.** `validate-session.sh`: schema conformance, every ref
   resolves, checksum matches the state file, timeline monotonic, anchors intact, session_end is
   last. Run against a committed fixture session. House rule: **a capture without a validator is a
   claim; a capture with a validator is an observation** — schema additions land with their check
   in the same change.

9. **`origin` stamp emitted per session** with the vocabulary `forecast | simulation-derived |
   real-agent-observed`. Arneson stamps origin (a fact it knows at emit time); mapping origin to
   claim strength is a judgment reserved for the consumer. The enum values are an offer — if Gygax
   wants different vocabulary, say so before this ships.

## For contrast: the decisions Gygax owns (NOT covered above)

- **Ingest contract level** — sidecar (event stream) vs digest (aggregated findings). Arneson-side
  recommendation: pin at the sidecar level (a thin real-agent runner can emit events but not
  findings, and findings-aggregation edges on interpretation Arneson shouldn't do).
- **Canonical signal taxonomy** — Arneson's `signal.classification` enum has 9 values today; the
  direction doc says "8-signal." Gygax publishes the canonical versioned list; Arneson vendors it.
- **Entity-ref namespace** — Gygax IDs verbatim vs Arneson-local refs + binding table
  (producer prefers binding table, for standalone safety).
- **Ingest granularity** — raw event stream vs pre-grouped (grouping should be the consumer's
  pass; it's the first step of interpretation).
- **Rejection semantics** — drop / fail / quarantine-and-tag on unresolvable refs (producer
  prefers quarantine-and-tag, so partial admissibility survives schema drift).
