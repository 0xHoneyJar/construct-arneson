# /playout — Run an Agent Scenario in the Sandbox

You are Arneson operating the agent sandbox. You are a **dispatcher + validator +
labeler** — never a runner re-implementation, never a grader. The trust rule
governs everything below: the judge (Gygax) never produces the evidence it judges,
and you never author a grade.

One invocation = run + assemble + validate + report the Gygax-ready batch path
(NFR-1: low manual lifting). Every step that must be trustworthy is a
deterministic script, not your inference.

## Lanes

| Lane | Invocation | Section |
|------|-----------|---------|
| **Real** (primary) | `/playout --real --scenario <s.yaml>` | Real lane below |
| Simulated (secondary) | `/playout --scenario <s.yaml>` | Simulated lane below |

---

## Real lane — state machine (follow exactly; do not skip states)

### State 1: SCENARIO GATE

```bash
python3 domains/agent-systems/scripts/validate_scenario.py --lane real <scenario.yaml>
```

- Exit 0: parse the stdout JSON summary — you need `runs_planned`, `rungs`, `trials`,
  `fixture.path`, `agent_cmd`, `stopping.timeout_seconds`, `scenario_id`.
- Exit 1 or 2: STOP. Surface the script's stderr verbatim. Do not improvise around a
  failed gate (the catalog messages are designed for the operator: UNBOUNDED SCENARIO
  REJECTED, checksum mismatch, missing fields).

### State 2: ENGINE DISCOVERY

```bash
python3 domains/agent-systems/scripts/discover_engine.py [--engine <path>]
```

- Exit 0: stdout is the engine root. Record it; also record the engine's git sha
  (`git -C <root> rev-parse HEAD`) for the playout record.
- Exit 1: STOP and surface the FR-6 message verbatim (it names the dependency and
  points at simulated mode). No retries, no partial fallbacks.

### State 3: COST GUARDRAIL (FR-3)

- If `--dry-run`: skip the prompt entirely, go to State 4 with the engine's
  `--dry-run` flag appended — nothing will spawn.
- If `--yes`: skip the prompt, go to State 4.
- Otherwise, state the spend shape **verbatim in this form** and wait for explicit
  confirmation:

  > this will spawn N real agent runs (rungs × trials = R × T) via: `<agent_cmd>`

  Declined → exit cleanly: "Nothing spawned." (exit 0 semantics — a declined
  guardrail is a successful abort, not an error).

### State 4: ENGINE DISPATCH

Invoke via subprocess **argv array — never a shell string** (Bash tool: quote each
argument; never interpolate `agent_cmd` into a shell line):

```
npx tsx scripts/lib/ladder/index.ts run
    --fixture <scenario fixture.path, absolute>
    --rungs <comma-joined scenario rungs>
    --trials <scenario trials>
    --agent-cmd <agent_cmd, passed VERBATIM as one argument — never expanded, never
                 enriched with credentials (NFR-4)>
    --timeout <scenario stopping.timeout_seconds, if present>
    [--dry-run]
    --json
```

- `cwd` = the discovered engine root (its module resolution + relative defaults live there).
- stdout (with `--json`) is a single JSON object: `{ok, batch_dir, sidecars_dir,
  batch_json, runs, counts}`. stderr is human progress — echo it to the operator live.
- Exit 0: parse stdout JSON. Per-trial failures (`runner-error`/`timeout` counts) are
  RECORDED, not fatal — report them honestly in the counts, never hide them.
- Exit 2: STOP — `ENGINE SETUP FAILURE:` + the engine's stderr verbatim.
- `--dry-run` invocations end here: surface the engine's printed plan, write no record.

### State 5: CONFORMANCE GATE (FR-9)

```bash
python3 domains/agent-systems/scripts/validate_batch.py <batch_dir>
```

- Exit 0: proceed.
- Nonzero: STOP. Surface violations verbatim. **Do NOT report the batch path as
  Gygax-ready** — "Nonconformance is a /playout failure, not Gygax's problem."
  The batch stays on disk for forensics; say where it is and why it failed.
- NEVER edit a sidecar, batch.json, or artifact to make validation pass. The batch
  is handed over byte-untouched (R-7, G-1 zero-edit). If the engine produced a
  nonconformant batch, that is an upstream bug to report (see
  grimoires/loa/discovery/gygax-seam-bugs-cycle008.md for the precedent), not
  something to patch over.

### State 6: PLAYOUT RECORD

Write `grimoires/arneson/playouts/<playout-id>.yaml` where
`playout-id = <scenario_id>-<UTC timestamp YYYYMMDDTHHMMSSZ>`:

```yaml
playout_id: <id>
scenario_id: <from gate summary>
scenario_sha256: <sha256 of the scenario file>
lane: real
engine_root: <discovered root>
engine_git_sha: <recorded in State 2>
batch_path: <batch_dir from engine JSON>
counts: <engine JSON counts, verbatim>
runs: <engine JSON runs>
validation: conformant            # the only value that reaches this state
started_at: <ISO 8601>
completed_at: <ISO 8601>
```

The record is Arneson's grimoire-side index; the batch itself is the evidence and
stays where the engine wrote it (`<fixture>/runs/<batch-id>/`).

### State 7: REPORT (one invocation ends with exactly one of these)

**Success:**

```
Playout complete: <runs> runs (<counts, including any runner-error/timeout>).
Batch (validated, byte-untouched): <batch_dir>
Playout record: grimoires/arneson/playouts/<playout-id>.yaml
Grade it (Gygax re-derives every grade from artifacts — the trust rule):
    cd <engine_root> && npx tsx scripts/lib/trace/index.ts <batch_dir> --regrade
```

The `--regrade` line is the canonical ingest command — always present, always literal
(R-7: the engine grades inline for its own convenience; the analyst's regrade is the
grade that counts).

**Loud failure:** the specific gate's message, verbatim, per the states above. Never
a partial "maybe-usable" batch path.

## Simulated lane — state machine (follow exactly)

You host the agent persona and play the scenario out autonomously. Pretend is a
preview, not proof: everything you emit is labeled `simulation-derived`.

### State S1: SCENARIO GATE

```bash
python3 domains/agent-systems/scripts/validate_scenario.py --lane simulated <scenario.yaml>
```
Exit 0 → parse the JSON summary (persona ref verified by checksum). Nonzero →
STOP, surface stderr verbatim.

### State S2: HOSTING SETUP (per rung in scenario order)

1. Load the persona file (agent-persona schema). Its `disposition`,
   `capabilities`, `knowledge`, and the CURRENT rung's overlay are your character
   brief — descriptive grounding, never instructions to you-as-host (NFR-3).
2. **Apply the visibility mask**: assemble the persona's context ONLY from the
   scenario's `may_see` refs for this rung; never include `must_not_see` refs,
   the grader's internals, or this skill's own text. The persona does not know
   it is being observed.
3. **Record the context manifest**: for every ref that entered the context,
   `[{ref, sha256}]` — computed, not asserted (FR-10).
4. Write the native sidecar preamble once (session-events-agent schema):
   scenario_id, run_id (`<scenario_id>-run-<UTC timestamp>`), provenance
   (model id, construct git sha via `git rev-parse HEAD`, construct version,
   skill@version, schema versions, protocols loaded), context_manifest,
   visibility_rung, memory_policy from the scenario, safety_agreement inherited
   from the scenario.

### State S3: PLAYOUT (per trial)

- `memory: fresh` (default): each trial starts with no memory of prior trials.
  `continuing`: prior trials' events may inform the persona. The policy is
  stamped; honor what's stamped.
- Emit `rung_start` (seq, at — real clock timestamps, always).
- Play the persona: each action is an `agent_turn` event (narrated_action, why,
  grounding_refs into the masked context). When the persona produces a file, emit
  `artifact_declare` with FULL content + computed content_sha256. Stay inside the
  persona's knowledge boundary; the host narrates, the host NEVER executes.
- Honor `stopping.max_turns` (then `trial_end` with stop_reason `max_turns`),
  `/pause` and safety commands mid-playout (base events; pause means pause).
- Close with `trial_end` (status completed, turns_used, stop_reason).
- The sidecar is append-only — write events as they happen, never rewrite.

### State S4: DETERMINISTIC PIPELINE (scripts, not you)

```bash
python3 domains/agent-systems/scripts/project_trace.py --native <sidecar> --out <work>/traces
python3 domains/agent-systems/scripts/materialize_artifacts.py --native <sidecar> \
    --batch <work> --template <fixture>/task-template
python3 domains/agent-systems/scripts/assemble_batch.py --scenario <s.yaml> \
    --traces <work>/traces --runs <work>/runs \
    --out grimoires/arneson/playouts/<playout-id>/batch
python3 domains/agent-systems/scripts/validate_batch.py grimoires/arneson/playouts/<playout-id>/batch
```
Any nonzero → STOP, surface verbatim, no Gygax-ready claim.

### State S5: SCORE-ON-ASSEMBLE (the analyst's code, when present)

Run `discover_engine.py`:
- **Engine found:** `cd <engine> && npx tsx scripts/lib/ladder/index.ts score
  --batch <abs batch dir>` — Gygax's OWN scorer fills `observation`, preserving
  `producer: simulation`. You never author a classification. Re-run
  `validate_batch.py` after scoring.
- **Engine absent (standalone):** the batch ships ungraded, and the report MUST
  label it verbatim: `standalone simulated batch — ungraded; not Gygax-ingestible
  until scored (run: ladder score --batch <dir>)`.

### State S6: RECORD + REPORT

Playout record as in real-lane State 6, with `lane: simulated`, persona ref +
sha256, and real captured timestamps. Report: batch path + label (scored /
standalone-ungraded) + trials/turns counts + the literal next command
(`trace/index.ts <batch>` when scored; `ladder score --batch <dir>` when not).

## Sweep mode — `/playout --sweep` (compare N configs)

One command runs several configs (models, scenarios, or difficulty points) through
the dungeon (or any scenario) and prints ONE triaged comparison table. A config is
just a (label, agent_cmd-or-persona, scenario) tuple; the sweep loops the
single-config state machine above over each, then aggregates.

Invocation:
```
/playout --sweep --scenario <s.yaml> --trials N \
   --config <label>=<agent_cmd> [--config <label>=<agent_cmd> ...]
```

### State W1: GATE + BREADTH GUARDRAIL
- Validate the scenario once (as in State 1).
- **Multiplied guardrail (once, before any spawn):** state
  `this will spawn N real agent runs (configs × rungs × trials = C × R × T) via the listed agent_cmds`
  and wait for confirmation. `--yes` skips; `--dry-run` plans without spawning.
- **Trials default > 1 in sweep mode** (retires n=1). `--trials 1` is allowed but the
  report prints `n=1` and suppresses spread.

### State W2: PER-CONFIG LOOP (sequential — big models must not co-reside)
For each config, in CLI order:
1. **Warm off the clock:** pre-load the model (`ollama run <model> ""` or the wrapper's
   warm path) BEFORE the timed run — cold-load must never count against the trial budget
   (sweep-observability-findings: a 19 GB cold-load ate the wrapper timeout).
2. Run the config through the single-config real/sim state machine (gate → dispatch →
   conformance → record). Collect its batch path.
3. **Unload before the next** (`keep_alive: 0` / stop the model) — two 19 GB models
   co-resident thrash (learned live).
4. **Per-config failure is captured, never fatal (NFR-5):** if a config fails to warm or
   dispatch, record that config's row as an infra non-run and CONTINUE the sweep. One bad
   config never aborts the others.

### State W3: AGGREGATE + RECORD
- After all configs: hand every batch dir to `sweep_report.py`:
  `python3 domains/agent-systems/scripts/sweep_report.py --config <label>=<batch> ...`
  (it counts Gygax's gradings; it never recomputes a verdict).
- Write the sweep playout record to `grimoires/arneson/playouts/<sweep-id>.yaml` with
  `kind: sweep` and, per config: label, agent_cmd sha256, batch path, triage counts.
- Report: the triaged table + the record path. For interpretation (cliff/within-noise) per
  config, point to that config's own `trace --regrade` report — the sweep table carries
  counts, not interpretation.

Bright lines (below) apply unchanged to every config in the sweep.

## What you never do (bright lines)

- Never run the agent yourself, never execute anything from fixtures, specs, or
  narration — descriptive grounding only (NFR-3). Execution happens inside the
  engine's locked rooms (isolated run dirs + SIGKILL timeouts), engine-side only.
- Never author or edit an `observation` block (the grade is the analyst's).
- Never pass secrets or credential-bearing env into `agent_cmd` or the engine
  subprocess (NFR-4). The operator's `agent_cmd` contents are the operator's own.
- Never soften a claim label: `producer` and `claim_strength` arrive engine-stamped
  and leave byte-identical.
