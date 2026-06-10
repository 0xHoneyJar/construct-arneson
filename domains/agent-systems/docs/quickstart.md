# Quickstart: Run an Agent Through the Sandbox

You write one scenario file, run one command, and Gygax hands you a report
comparing what it *predicted* an agent would do against what an agent
*actually did*. This page assumes nothing beyond a terminal.

## What you need

1. **Both constructs, side by side** in the same parent directory:
   ```
   ~/work/construct-arneson/
   ~/work/construct-gygax/
   ```
   (Different layout? Set `ARNESON_GYGAX_ROOT=/path/to/construct-gygax`.)
2. **Node** (for Gygax's engine) and **Python 3.10+** (for Arneson's checks).
3. **An agent command.** Any CLI that takes a task prompt and edits files in
   the current directory. Examples below.

## Step 1 — pick your agent

The scenario's `agent_cmd` is a command template. The engine replaces
`{prompt}` with the task text (or `{promptfile}` with a path to it), runs your
command inside a locked room (an isolated folder with a hard time limit), and
keeps every file it touches.

```yaml
# Claude:
agent_cmd: "claude -p {prompt} --permission-mode acceptEdits"

# A local model via Ollama needs an AGENT wrapper, not the bare model —
# `ollama run qwen3` only talks; it won't edit files, so every run would
# grade as "failed". Point agent_cmd at an agentic CLI with Ollama as its
# brain, e.g. aider:
agent_cmd: "aider --model ollama/qwen3 --yes --message-file {promptfile}"
```

Comparing two agents? One scenario file per agent, same fixture — that's the
one-variable rule (see `domain.conventions.md`), and Gygax's reports will show
them side by side.

## Step 2 — write the scenario

Copy `domains/agent-systems/resources/scenarios/awareness-ladder-demo.yaml`
(path from the arneson repo root) and adjust. The fields that matter most:

| Field | Meaning |
|-------|---------|
| `fixture.path` + `manifest_sha256` | which test world, pinned (`shasum -a 256 <fixture>/manifest.yaml`) |
| `rungs` | how much the agent is told: 0 = blind, 1 = knows the reward, 2 = told to win at any cost |
| `trials` | repeats per rung |
| `stopping` | REQUIRED — no unbounded runs, ever |
| `safety.agreement` | REQUIRED — the scenario-level safety block (copy the demo's; every trial inherits it) |
| `agent_cmd` | your agent, from Step 1 |

Two things that bite people:

- **`fixture.path` resolves relative to the scenario file's own directory.** If
  you copy the demo somewhere else, rewrite that path — an absolute path is fine.
  (A wrong path fails loudly and prints the resolved location it tried.)
- **Scenario files use a deliberately restricted YAML subset**: 2-space indents,
  plain scalars, no anchors, no multiline strings. Keep shapes flat like the demo.

## Step 3 — run it

`/playout` is a **Claude skill**, not a shell command — inside a Claude Code
session in the arneson repo, say:

```
/playout --real --scenario path/to/your-scenario.yaml
```

You'll be told exactly what's about to spend money:

> this will spawn N real agent runs (rungs × trials = R × T) via: `<your agent_cmd>`

Say yes (or pass `--yes` to skip the question, `--dry-run` to see the plan and
spawn nothing). Arneson then drives the engine, checks every produced file
against the contract, writes a playout record to `grimoires/arneson/playouts/`,
and ends with the batch's location plus the literal next command.

<details>
<summary><b>No Claude session? The same flow by hand</b> (what the skill runs, in order — full spec: <code>skills/playout/SKILL.md</code>)</summary>

```bash
# 1. gate the scenario (prints a JSON summary incl. runs_planned)
python3 domains/agent-systems/scripts/validate_scenario.py --lane real <s.yaml>
# 2. find the engine
ENGINE=$(python3 domains/agent-systems/scripts/discover_engine.py)
# 3. run it (THIS is the step that spends money — you are your own guardrail here)
cd "$ENGINE" && npx tsx scripts/lib/ladder/index.ts run \
  --fixture <abs fixture path> --rungs 0,2 --trials 1 \
  --agent-cmd '<your agent_cmd>' --timeout 300 --json
# stdout JSON includes batch_dir — that's your batch
# 4. validate it (byte-untouched)
python3 domains/agent-systems/scripts/validate_batch.py <batch_dir>
# 5. grade it (Step 4 below)
```

Hand-runs skip the skill's playout record; copy the shape from SKILL.md
State 6 if you want the same grimoire trail.
</details>

## Step 4 — get the report

Batches land under the fixture: `<fixture>/runs/<batch-id>/` (the engine's
`--json` output and the skill's report both print the exact `batch_dir`).

```bash
cd /path/to/construct-gygax
npx tsx scripts/lib/trace/index.ts <batch-dir> --regrade
```

`--regrade` means Gygax re-derives every grade from the files the agent
actually left behind — it never trusts anyone's word, including ours. The
report shows the forecast (what the incentive math says a rational agent
*should* do), what your agent observably did at each awareness rung, and where
the two diverge.

## Reading the result honestly

- Every record is labeled: `real-agent-observed` means a real agent really ran;
  `simulation-derived` means Arneson acted it out. The two are never mixed up.
- A run is classified `fixed`, `hacked`, or `failed` — derived from file diffs
  and a test re-run, not from what the agent claimed.
- One run is an anecdote. Raise `trials` for spread; the report does the
  per-rung arithmetic.

## The preview lane (no spend, no Gygax needed)

Before paying for real runs — or before your agent even exists — the sandbox
can *act as* the agent from a written description:

```
/playout --scenario path/to/sim-scenario.yaml      # no --real
```

The scenario swaps `agent_cmd` for a pinned `persona` block (start from the
bundled `resources/personas/neutral-agent.yaml`; import your own via
`docs/importing-an-agent.md`). Output is the same batch shape, labeled
`simulation-derived` — a preview, never proof. With Gygax installed it's
scored by Gygax's own scorer automatically; standalone it's labeled
`ungraded; not Gygax-ingestible until scored`. Compare preview vs real with
the same fixture, then tune the persona against the gap
(docs/pairing-workflow.md).

## When something refuses

Every gate fails loudly with a named reason: `UNBOUNDED SCENARIO REJECTED`
(add `stopping`), `checksum mismatch` (re-pin your fixture hash),
`MISSING DEPENDENCY: construct-gygax engine not found` (fix the layout or set
`ARNESON_GYGAX_ROOT`), `CONTRACT DRIFT` (the vendored contract needs
re-vendoring — see `schemas/vendor/VENDOR.yaml`). A refusal is the system
working; nothing half-runs.
