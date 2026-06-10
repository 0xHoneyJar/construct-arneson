# Bug Triage: Local-model agent path in agent-systems quickstart is unrunnable as documented

## Metadata
- **schema_version**: 1
- **bug_id**: 20260610-c7bc67
- **classification**: documentation_operability_defect (G-3 stranger-operability failure, local-model case)
- **severity**: medium
- **eligibility_score**: 3
- **eligibility_reasoning**: Reproducible steps that can be followed verbatim (+2: follow quickstart.md Step 1 local-model path; `which aider` returns not-found; repo grep confirms no bundled wrapper exists). Observed operator failure with dated environment evidence (+1: 2026-06-10, ollama installed, gemma:latest pulled, run still impossible without third-party install). No disqualifiers: this is a defect in documented existing behavior — domain.conventions.md ("Local-model agents" section) promises "working examples" in quickstart Step 1 and describes a wrapper-script fallback ("a small script that reads the prompt, asks the model, and writes the files"), but quickstart Step 1 offers only `aider` (not installed, not bundled) and the described script exists nowhere in the repo. PRD G-3 (prd.md:57) requires the loop be runnable "from the quick-start alone." Bundling the example wrapper is the minimal fix for the broken documented promise, not new feature surface — precedent: `deterministic-agent.py` already ships as operator-side fixture tooling.
- **test_type**: integration
- **risk_level**: low
- **created**: 2026-06-10T16:32:14Z

## Reproduction
### Steps
1. Be a stranger-operator with both constructs installed per `docs/quickstart.md` "What you need" (Node, Python 3.10+, Ollama running with a model pulled — verified: `gemma:latest`).
2. Follow quickstart Step 1 to pick a local-model agent. The only local-model `agent_cmd` example given is `aider --model ollama/qwen3 --yes --message-file {promptfile}` (quickstart.md:34).
3. Run `which aider` → not found (aider is third-party tooling, not bundled, not listed in "What you need").
4. Look for the documented fallback: domain.conventions.md:62-66 says to wrap the model in "a small script that reads the prompt, asks the model, and writes the files it answers with" and points to "docs/quickstart.md Step 1 for working examples."
5. Search the repo for any such wrapper: `grep -rn "aider\|ollama" domains/agent-systems/` → only the quickstart mention; no wrapper script exists anywhere in the repo.
6. Net effect: `/playout --real` with a local model cannot be run without first installing or authoring third-party tooling.

### Expected Behavior
An operator with Ollama running can take a works-out-of-the-box example from quickstart Step 1 and run a local model through `/playout --real` with zero API spend, using only what ships in the repo (G-3: "Someone with both constructs installed runs the loop from the quick-start alone").

### Actual Behavior
The single documented local-model `agent_cmd` example depends on `aider` (not installed, not bundled, not declared as a prerequisite). The wrapper-script fallback described in domain.conventions.md does not exist in the repo, and its pointer back to "working examples" in quickstart Step 1 is circular. The G-3 stranger-operability bar fails for the local-model case.

### Environment
Operator machine, 2026-06-10. Ollama installed and serving on localhost:11434; `gemma:latest` pulled. `aider` not installed. Both constructs installed side by side.

## Analysis
### Suspected Files
| File | Line(s) | Confidence | Reason |
|------|---------|------------|--------|
| domains/agent-systems/docs/quickstart.md | 26-35 | high | Step 1 agent examples: the only local-model `agent_cmd` references absent third-party tooling (`aider`); no bundled alternative offered |
| domains/agent-systems/domain.conventions.md | 60-67 | high | "Local-model agents" section describes a wrapper script that does not exist and claims "working examples" live in quickstart Step 1 |
| domains/agent-systems/resources/fixtures/deterministic-agent.py | 1-13 | medium | Pattern precedent (not itself defective): existing stdlib-only operator-side fixture agent; the new wrapper should mirror its posture and docstring honesty |
| domains/agent-systems/resources/fixtures/ | n/a | high | Where the bundled wrapper is missing from (proposed: `ollama-agent.py`) |

### Related Tests
| Test File | Coverage |
|-----------|----------|
| domains/agent-systems/scripts/test-validate-scenario.sh | Scenario gate only; does not cover agent_cmd runnability |
| domains/agent-systems/scripts/test-sim-pipeline.sh | Sim lane only; no real-lane local-model coverage |
| (missing) domains/agent-systems/scripts/test-ollama-agent.sh | Does not exist — the gap this bug's test fills |

### Test Target
New `domains/agent-systems/scripts/test-ollama-agent.sh` following the domain's existing `test-*.sh` convention. Offline, zero-spend: stand up a stdlib-only stub HTTP server impersonating Ollama's API on a local port, point the wrapper at it via its base-URL/port handling, and assert (a) the wrapper reads `{promptfile}`, (b) it writes the files the stubbed model answers with into cwd, (c) it exits nonzero on connection failure / non-200 / malformed response, (d) `python3 -c "import ast; ast.parse(...)"`-level stdlib-only import check (no third-party imports). Additionally assert quickstart Step 1 references the bundled wrapper (doc grep). Live verification (engine run against the bundled synthetic-incentive fixture with `ollama/gemma`, zero API spend) is a manual acceptance step recorded in the sprint, since CI has no Ollama daemon.

### Constraints
- **NFR-5** (prd.md:180): Python 3 stdlib only — wrapper uses `urllib.request`/`json`/`argparse`/`pathlib`, no pip installs.
- **NFR-3/FR-11 posture** (prd.md:178,146): the wrapper is operator-side agent tooling like `deterministic-agent.py` — it runs engine-side inside the locked room; its inputs (promptfile, model output) are untrusted content, never interpreted by the host.
- **Banned-copy rules** (domain.conventions.md "Banned copy" table): any new or edited doc text must contain 0 banned phrases outside quoted ban lists.
- Wrapper must exit nonzero on failure so the engine grades the trial `failed` rather than silently passing an empty room.
- Keep `aider` as a documented alternative — the fix adds a works-out-of-the-box path, it does not remove the existing example.

## Fix Strategy
Bundle the minimal wrapper the docs already describe, then make the docs point at the real thing. Create `domains/agent-systems/resources/fixtures/ollama-agent.py`: stdlib-only CLI that takes `--model` plus a promptfile path argument (engine substitutes `{promptfile}`), reads the prompt, POSTs to Ollama on `localhost:11434` (`/api/chat`, fall back or pin per implementation choice), parses the response for file contents to write into cwd (define a simple, documented response convention, e.g. fenced filename blocks — keep it boring and deterministic to parse), writes those files, narrates briefly to stdout, and exits nonzero on any failure (connection refused, HTTP error, unparseable reply, zero files written). Mirror `deterministic-agent.py`'s docstring honesty about what it is and is not. Update quickstart.md Step 1 to present the bundled wrapper as the works-out-of-the-box local-model example (`agent_cmd: "python3 <abs-or-resolved path>/ollama-agent.py --model gemma {promptfile}"`) with aider retained as the third-party alternative; update domain.conventions.md "Local-model agents" to reference the now-real script. Add `test-ollama-agent.sh` per Test Target. Verify live once with `ollama/gemma` against the bundled synthetic-incentive fixture (zero API spend) and record the batch result in the sprint evidence.

### Fix Hints
Structured hints for multi-model handoff (each hint targets one file change):

| File | Action | Target | Constraint |
|------|--------|--------|------------|
| domains/agent-systems/resources/fixtures/ollama-agent.py | add | stdlib-only Ollama wrapper agent: --model flag + promptfile arg, POST localhost:11434, write returned files to cwd, exit nonzero on failure | NFR-5 stdlib only; operator-side fixture posture like deterministic-agent.py |
| domains/agent-systems/scripts/test-ollama-agent.sh | add | offline test: stdlib stub HTTP server, assert file-writing, nonzero-exit on failure, stdlib-only imports | zero network spend; follow existing test-*.sh convention |
| domains/agent-systems/docs/quickstart.md | fix | Step 1 local-model example: lead with bundled ollama-agent.py, keep aider as alternative | banned-copy table compliance; no removal of existing examples |
| domains/agent-systems/domain.conventions.md | fix | "Local-model agents" section: replace hypothetical "small script" description with reference to the bundled wrapper | banned-copy table compliance |
