# Sprint 1 Review — Engineer Feedback

**Sprint**: sprint-1 (Foundation / M0)
**Reviewer**: /review-sprint skill
**Date**: 2026-04-13
**Verdict**: **All good (with noted concerns)**

---

## Overall Assessment

Sprint 1 delivers the structural bedrock per acceptance criteria. All ten tasks completed,
all five CI validation scripts pass locally, the HEKATE audit is working (caught
real-but-legitimate meta-references and filtering was correctly added rather than silenced).

The implementation is shippable as scaffolding. Several concerns identified — none blocking
for Sprint 1's purpose (no executable skills yet; voice quality deferred to Sprint 2), but
some are material risks for Sprint 2 start.

---

## Adversarial Analysis

### Concerns Identified

1. **Process: no beads tasks for Sprint 1** — `construct.yaml` is tracked via Claude
   TaskCreate, not `br`. CLAUDE.md rule: "ALWAYS create beads tasks from sprint plan
   before implementation (if beads available)." `br init` ran during preflight (beads
   was available), but no tasks were materialized. Sprint 1 itself is now invisible to
   `br list`, `/run-resume`, and cross-session recovery.
   - **File**: `grimoires/loa/a2a/sprint-1/reviewer.md:252-255` (Known Limitation #6)
   - **Severity**: Non-blocking for Sprint 1 (work is complete). Blocking for Sprint 2
     if pattern repeats — by Sprint 2 start, tasks MUST live in beads.

2. **Fallback archetype names are hand-authored guesses** — The 9 archetype names
   (newcomer, optimizer, chaos-agent, storyteller, rules-lawyer, explorer, min-maxer,
   casual, contrarian) were invented. Gygax's canonical cabal names may differ.
   - **Files**: `resources/archetypes-fallback/*.yaml` (all 9)
   - **Risk blast radius**: If names diverge, every `archetype_ref` in every test, every
     session file, every fallback YAML, and every reference in code needs renaming. Not
     a trivial find-replace (references live in sidecar `archetype_ref` fields, scene
     seeds, scripts, CI). Flagged in reviewer.md Known Limitation #1; Sprint 7 has a
     sync check. But the risk is Sprint 2 building on the wrong names for 5 sprints
     before it's discovered.
   - **Recommendation**: Before Sprint 2 starts voicing work, obtain access to a Gygax
     v3 install (or its archetype.yaml samples) and sync the fallback names.

3. **Schema validation only checks parsing + a few required fields** — The 7 `.schema.yaml`
   files are declarative YAML, not formal JSON Schema. `validate-schemas.sh` checks they
   parse and have `schema.name` + `schema.version`. `validate-fallbacks.sh` checks a
   handful of required fields by hand. Fields in the middle (e.g., does
   `voice-archetype::chaos_axis_config.per_turn_sidecar_event_cap` match its declared type?)
   are unchecked.
   - **Files**: `scripts/ci/validate-*.sh`, `schemas/*.schema.yaml`
   - **Consequence**: A Sprint 2 archetype YAML could be structurally wrong in ways that
     only surface at skill execution time — harder to debug than schema-time failure.
   - **Mitigation considered**: JSON Schema would catch this. Deferred to future sprint.

4. **CI workflow has never actually executed** — `.github/workflows/ci.yaml` has not been
   triggered. Validation was local-script runs only. YAML syntax is parsed-correct (yq
   loaded it), but GitHub Actions has its own runner semantics, env handling, permissions,
   and shell behavior that can surface issues not caught locally.
   - **File**: `.github/workflows/ci.yaml` (entire file)
   - **Verdict**: Unavoidable at Sprint 1 (no push yet). Should be first concern on
     first PR/push.

5. **HEKATE audit filter is fragile** — Multiple-pipe `grep -v` chain in
   `scripts/ci/hekate-audit.sh:41-49`. Adding a new meta-phrase requires editing the
   regex pipeline. If the exclusions are wrong, the audit either false-negatives (real
   reference missed) or false-positives (legitimate meta-reference flagged). The
   validator works today but is hard to reason about.
   - **File**: `scripts/ci/hekate-audit.sh:41-49`
   - **Alternative**: Dedicated allowlist of phrases + strict match on actual content.
     Defer to v1.1.

6. **`digest.schema.yaml` has unenforceable inline documentation** — Lines like
   `items_shape: "same as confusion"` appear in the signal_flags object. This is prose,
   not a structural declaration. No validator catches it; the next engineer can write
   a digest where `friction` and `bottleneck` have materially different shapes without
   any warning.
   - **File**: `schemas/digest.schema.yaml:98,99,100,101,102` (items_shape stringly-typed)
   - **Fix**: Replace with actual repeated structure. Trivial — 10 lines of diff. Could
     be a non-blocking fix in Sprint 2.

7. **`identity/ARNESON.md` first-person voice may cause role confusion** — The file is
   written as Arneson-speaking-about-itself ("I am construct-arneson. I voice, I narrate,
   I stage."). When loaded into a skill prompt, this reads as system-role speech. If the
   skill prompt's structure isn't careful, the LLM could start speaking AS Arneson-the-
   construct during turn content (instead of as an archetype), confusing the meta/voice
   boundary `identity/persona.yaml::meta_role_boundaries` was supposed to enforce.
   - **File**: `identity/ARNESON.md:1-2,8-9,etc.`
   - **Check in Sprint 2**: When `/braunstein`'s prompt engineering happens, verify
     the prompt explicitly scopes when Arneson-voice is active vs. when archetype-voice
     is active. The voice-switching discipline from ARNESON.md:"How I speak" section
     is the rule; the prompt must encode it.

### Assumptions Challenged

- **Assumption**: Gygax v3's `identity/persona.yaml` and `skills/cabal/resources/archetypes.yaml`
  will have shape compatible with Arneson's `voice-archetype` schema.
- **Risk if wrong**: Arneson's composition-detection probe will succeed (directories exist),
  but archetype loading will produce shape mismatches at skill execution time. Neither
  standalone nor composed mode will work cleanly until the contract is verified.
- **Recommendation**: Before Sprint 2 Task 2.4 (archetype loading with Gygax-or-fallback),
  explicitly validate the contract — either with a real Gygax install or with
  documented-shape samples from the Gygax maintainer. If shapes differ, an adapter layer
  is required, which is not in the current SDD.

- **Assumption 2**: Threshold fixture (one location, one situation, two mechanics) will
  adequately exercise all 8 skills at acceptance time.
- **Risk if wrong**: `/fragment` (setting material generation) has essentially no setting
  to fragment against; `/scene` has only the dusk-at-the-well scene to riff from; `/voice`
  has three named NPCs but no NPC development arc.
- **Recommendation**: Acknowledged in PRD A-2. Sprint 6 should explicitly grow the
  fixture if /fragment or /scene can't exercise meaningfully. Not a Sprint 1 gap.

### Alternatives Not Considered

- **Alternative**: Use formal JSON Schema instead of Loa-native YAML schemas.
- **Tradeoff**: JSON Schema enables: IDE auto-completion, widely-supported validators
  (ajv, jsonschema), auto-generated documentation. Costs: additional syntax, less
  readable than hand-authored YAML, another dependency.
- **Verdict**: Current approach is defensible for v1 — the fallback and schemas are
  all hand-authored and small enough that prose-YAML is sufficient. Should revisit in
  v1.1 or v2 when the schema count and complexity grows. Document as a deferred
  improvement in NOTES.md for future consideration.

---

## Checklist — Acceptance Criteria Verification

From `grimoires/loa/sprint.md` Sprint 1 acceptance criteria:

- [x] `construct.yaml` validates — confirmed via `validate-construct.sh`
- [x] All 7 Arneson schemas validate as valid YAML — confirmed via `validate-schemas.sh`
- [x] Synthetic fixture's `game-state.yaml` validates against declared schemas — confirmed via `validate-fixture.sh`
- [x] Synthetic fixture exercises: both intent axes, ≥3 archetypes (Newcomer, Optimizer, Chaos Agent playable), dice modes (documented), safety triggers (documented), tradition fallback — confirmed via manual inspection of `game-state.yaml` and `scene-seeds.md`
- [x] HEKATE audit passes (zero hits) — confirmed via `hekate-audit.sh`
- [x] CI runs green in both modes against smoke tests — local run green; GitHub Actions unverified (Concern #4)
- [-] `/arneson` skill dashboard can list zero sessions cleanly — DEFERRED to Sprint 6, per sprint.md's conditional ("if needed to keep smoke tests green"). Smoke tests are green without it.

7 of 7 required criteria met. Deferred item is explicitly permitted by sprint.md wording.

---

## Complexity Analysis

- **Function/script length**: All CI scripts under 100 lines. Clean.
- **Duplication**: HEKATE meta-filter logic duplicated in `hekate-audit.sh` and
  `validate-fixture.sh` — could be extracted to a shared function. Non-blocking;
  flagged as Sprint 2 refactor opportunity.
- **Dependency issues**: `yq` downloaded without version pin in CI. Flagged as a
  supply-chain concern; pin to specific yq version in Sprint 2.
- **Naming**: All YAML and script filenames follow consistent conventions.
- **Dead code**: None detected.

---

## Documentation Verification

- [x] CHANGELOG entry for Sprint 1 present at `grimoires/arneson/changelog/CHANGELOG.md`
- [x] CLAUDE.md not modified (not required — no new user-facing commands in Sprint 1)
- [x] `identity/ARNESON.md` + `persona.yaml` + `expertise.yaml` + `refusals.yaml` fully populated
- [x] Inline comments explain all schema choices and degradation paths
- [x] `resources/archetypes-fallback/README.md` documents the fallback discipline + sync requirements
- [x] `examples/synthetic-fixture/README.md` documents the fixture's purpose and safety posture

Documentation: **PASS**.

---

## Subagent Reports

No `grimoires/loa/a2a/subagent-reports/` directory present — `/validate` was not run.
Sprint 1 is scaffolding; formal subagent validation is reasonably deferred to Sprint 2
when executable skills exist. Recommend `/validate` run in Sprint 2 before that sprint's
review.

---

## Previous Feedback Status

No prior `engineer-feedback.md` — first review pass for Sprint 1.

---

## Non-Critical Improvements (Sprint 2 or later)

Tracked for follow-up, not blocking Sprint 1 approval:

1. **Fallback archetype names sync**: coordinate with Gygax v3 to verify/rename (Concern #2)
2. **Materialize Sprint 2 tasks in beads BEFORE starting implementation** (Concern #1)
3. **Pin yq version in CI** (supply-chain)
4. **Extract shared HEKATE meta-filter** from `hekate-audit.sh` and `validate-fixture.sh` (Concern #5)
5. **Replace inline prose in `digest.schema.yaml`** (`items_shape: "same as confusion"`) with actual repeated structure (Concern #6)
6. **Verify `/braunstein` prompt engineering scopes voice boundaries correctly** (Concern #7)
7. **Make `pinned_against_gygax: v3.0.0` a structured field** in each fallback YAML; validate it (documentation-only today)
8. **Consider JSON Schema for future schema revisions** (Alternative #1)

---

## Approval

**All good (with noted concerns)**

Sprint 1 Foundation is approved. Seven concerns and two assumptions documented above
for tracking into Sprint 2. None are blocking for Sprint 1's purpose (structural
scaffolding before skills exist). Engineer acknowledged several of these in their
own reviewer.md (beads, fallback names, CI unverified on GitHub) — this review
confirms those acknowledgments and adds five more observations.

Engineer is green-lit to start Sprint 2 (Vertical Slice `/braunstein`) **after**:
- Creating Sprint 2 tasks in beads (Concern #1 mitigation)
- Reviewing Concerns #2 and #7 with the user / project lead for input

Sprint 2 is the real risk-carrying sprint; the groundwork Sprint 1 delivered is
clean enough to build on.

---

*Reviewed by /review-sprint, 2026-04-13*
