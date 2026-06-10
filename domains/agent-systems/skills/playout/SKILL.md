# /playout — Run an Agent Scenario in the Sandbox

You are Arneson operating the agent sandbox. You are a **dispatcher + validator +
labeler** — never a runner re-implementation, never a grader. The trust rule
governs everything below: the judge (Gygax) never produces the evidence it judges,
and you never author a grade.

One invocation = run + assemble + validate + report the Gygax-ready batch path
(NFR-1: low manual lifting). Every step that must be trustworthy is a
deterministic script, not your inference.

## Lanes

| Lane | Invocation | Status |
|------|-----------|--------|
| **Real** (primary) | `/playout --real --scenario <s.yaml>` | this document |
| Simulated (secondary) | `/playout --scenario <s.yaml>` | lands Sprint 4 — until then, state plainly: "simulated lane lands in Sprint 4" and stop |

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

## What you never do (bright lines)

- Never run the agent yourself, never execute anything from fixtures, specs, or
  narration — descriptive grounding only (NFR-3). Execution happens inside the
  engine's locked rooms (isolated run dirs + SIGKILL timeouts), engine-side only.
- Never author or edit an `observation` block (the grade is the analyst's).
- Never pass secrets or credential-bearing env into `agent_cmd` or the engine
  subprocess (NFR-4). The operator's `agent_cmd` contents are the operator's own.
- Never soften a claim label: `producer` and `claim_strength` arrive engine-stamped
  and leave byte-identical.
