# Review — sprint-bug-3 (bug 20260610-5ad67a): APPROVED

All good (with noted concerns)

Verified: red-first test observed (party-wrapper marker untriaged before fix); anchored regex
behavior matches the triage's 5/5 pre-validated cases; regression (ollama-agent marker) and
false-positive guard (agent-printed "ERROR: [compiler]") both asserted; convention documented
on all three surfaces (validator constant, wrapper comment, conventions doc); 95/95.

## Adversarial Analysis

### Concerns (non-blocking)
1. **A conforming forged marker still triggers the warn** — an agent that deliberately prints
   "ERROR: [evil-agent] …" gets its run flagged as a non-run candidate. Same forge vector
   analyzed and accepted in the -594345 audit: warn-only, grader re-derives from artifacts,
   operator sees both. The convention doc's suffix-anchor section now makes the boundary
   explicit. Acceptable.
2. **Empty tool name matches** (`ERROR: [agent]`) — degenerate but conforming; harmless
   (still a warn). Tightening to require ≥1 char before the suffix would be cosmetic.
3. The prototype party-wrapper (grimoires/loa/prototypes/) emits the conforming marker but is
   session tooling, not shipped — if it ever graduates (cliff-instrument cycle), its tests
   must co-test the marker like ollama-agent's do. Noted for that future cycle.

### Assumption Challenged
- That uppercase "ERROR:" is stable across wrappers — it is the documented convention now,
  not an accident; the conventions doc says MUST.

### Alternative Not Considered
- A structured sidecar field (e.g. infrastructure_error: true) instead of narration matching.
  Better in principle, but it would require an upstream contract change (observed-trace/v1 is
  additive-only and Gygax owns it) — out of proportion for a warn-level triage. Revisit only
  if the convention ever proves insufficient; note it as a candidate optional field for a
  future v1 minor revision conversation with Gygax.
