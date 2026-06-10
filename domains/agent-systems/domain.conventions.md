# agent-systems — Domain Conventions

**Status:** Finalized (Sprint 3). The five-part contract, validator gate, and
honesty rules below are load-bearing; the banned-copy list polices every doc
and report in this domain.

## The five-part extension contract (how this domain plugs in)

| Part | This domain's answer |
|------|----------------------|
| State | A committed `scenario.yaml` (agent-scenario v1) + the fixture it pins |
| Personas | `agent-persona` v1 specs (NOT voice-base — you don't workshop an agent's voice) |
| Events | `session-events-agent` v1 (extends session-events-base v2; per-event seq + at) |
| Resolution | Real lane: Gygax's ladder engine. Simulated lane: persona host, serialize-only |
| Consumer | Gygax's trace CLI, via the vendored `observed-trace/v1` + batch contracts |

## Conventions (Sprint 1 set)

1. **The vendored contract is Gygax's file.** Never edit anything under
   `schemas/vendor/`; re-vendor + update `VENDOR.yaml` + revisit the validators.
2. **Validators are the gate.** No batch path is reported as Gygax-ready unless
   `validate_batch.py` exits 0. A capture without a validator is a claim.
3. **One variable per scenario family** (documented convention): rung varies
   *inside* a scenario; temperament/persona/agent_cmd varies *across* scenarios.
   Varying both at once produces a diff Gygax can't attribute.
4. **Honest labels always:** producer ↔ claim_strength binding is checked before
   handoff; forecast-without-playing is never a sidecar claim.

## Claim framing rules (G-4 — what every doc and report must honor)

1. **Pretend is a preview; real is the proof.** Simulated results inform; only
   real runs evidence. Frame the simulated lane as *behavioral exploration*
   ("watch how a hosted agent drifts under these incentives"), never as
   validation of anything.
2. **Labels are facts, not flair.** `producer.kind` and `claim_strength` say
   how a record was made. Quote them; never paraphrase a simulation upward.
3. **Signals are tagged, counts are counted, judgments are Gygax's.** Arneson
   may report arithmetic (runs, counts, ratios from the grader's report).
   Interpretations — cliffs, severity, "the incentive is broken" — come from
   the analyst's report and are cited, not authored here.
4. **A forecast made without playing is never an observation.** It lives at
   Gygax's report layer, clearly marked as the forecast lane.

## Banned copy (quoted ban list — these phrases may appear ONLY inside ban lists like this one)

| Banned phrase | Why | Say instead |
|---------------|-----|-------------|
| "hard metrics" (for experiential/behavioral signals) | overclaims tagged signals into measurements | "tagged signals", "counts from the grader's report" |
| "zero hallucination" | impossible bar; erodes trust in every other claim | "grounded + transparent: every action references state; improvisation is declared" |
| "high-fidelity" (about simulated agents) | fidelity is exactly what's unproven | "behavioral exploration", "preview" |
| "proves it's compelling" / "validates your incentives" | the sandbox explores; the analyst grades; nothing here *proves* | "surfaces hypotheses", "shows where forecast and observation diverge" |
| "effectively real" / "as good as observed" | claim laundering in prose form | quote the actual `claim_strength` |

Enforcement: `identity/refusals.yaml` (`claim_laundering.vocabulary_to_avoid`)
is grepped by the identity-refusal audit; this table is the doc-side mirror.
The Sprint 3 success metric is `0` banned phrases outside quoted ban lists in
`domains/agent-systems/docs/` + this file (grep check).

## Wrapper authors: the infrastructure-marker convention

A wrapper (the operator-side tool that turns a model into a file-acting agent) MUST emit
its own failures to stderr prefixed `ERROR: [<tool-name>]` where `<tool-name>` ends in
`-agent` or `-wrapper` (e.g. `ERROR: [ollama-agent] cannot reach …`). `validate_batch.py`'s
infrastructure triage matches exactly this convention in sidecar narrations to flag
non-runs ("a non-run, not a verdict") — so a conforming marker is what keeps your wrapper's
plumbing failures from masquerading as graded results. The suffix anchor exists so an
AGENT's own printed errors (`ERROR: [compiler] …`) are never mistaken for infrastructure.
Warn-not-reject; co-tested in `scripts/test-validate-batch.sh`.

## Local-model agents

Any agentic CLI works as `agent_cmd` — including local models. The rule of
thumb: the command must *act on files*, not just talk. Bare `ollama run <model>`
prints text and grades as `failed`. The repo BUNDLES a stdlib-only wrapper that
closes this gap out of the box: `resources/fixtures/ollama-agent.py` (prompt +
room files → local Ollama daemon → returned file blocks written back,
containment-checked to the room, bytes only). Third-party agentic CLIs (aider,
opencode) work the same way. See docs/quickstart.md Step 1 for the literal
`agent_cmd` lines.
