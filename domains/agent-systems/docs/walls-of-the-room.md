# The Walls of the Room

Real agents run inside a locked room. This page says exactly what the walls
stop, and — just as load-bearing — what they don't. Trusting walls that aren't
there is worse than having no walls.

## What the walls stop

| Wall | Mechanism | Owner |
|------|-----------|-------|
| Escaping the run folder via batch metadata | every `run_dir` is containment-checked (engine-side at creation; Arneson-side again at validation) | engine + Arneson |
| Running forever | hard per-trial timeout → SIGKILL; scenarios must declare a stopping condition or they are rejected | engine + scenario gate |
| One run contaminating another | one isolated directory per (rung × trial), created no-clobber | engine |
| Grades being made up | grades re-derived by Gygax from the artifacts (`--regrade`); a producer's claimed grade is never trusted | Gygax |
| Pretend dressed up as real | `producer` ↔ `claim_strength` binding is schema-enforced and validated again before handoff | contract + Arneson |
| Arneson's own hands | the persona host serializes, never executes; Arneson-side tooling writes bytes to files and runs nothing an agent says | Arneson identity (refusals) |

## What the walls do NOT stop

- **Whatever your `agent_cmd` can do.** The agent is YOUR command, run with
  YOUR user's permissions. The room scopes its *working directory*, not its
  process rights: an agent with network access can phone home; one with broad
  file permissions can read outside the room. The template is passed verbatim
  and recorded in `batch.json` — **never put secrets in it**, and prefer
  agents with the narrowest permissions that can still do the task
  (e.g. `--permission-mode acceptEdits`, not a blanket bypass).
- **A malicious agent's output content.** Files an agent writes are kept as
  evidence, verbatim. They are diffed and re-run BY THE GRADER in the same
  room. Nothing imports them elsewhere — keep it that way: never execute
  batch artifacts outside the grading flow.
- **Resource use inside the time limit.** Within its timeout an agent can burn
  CPU, disk, and API budget. The cost guardrail tells you N before anything
  spawns; the timeout bounds duration, not intensity.
- **Your own prompt content.** Rung prompts and fixture text reach the agent
  as instructions. If you put something in the prompt you didn't want followed,
  the room will faithfully record the agent following it.

## The honest summary

The room is a *fence for routine containment*, not a hardened security
boundary against a hostile superuser agent. It makes ordinary runs isolated,
bounded, evidenced, and labeled. If you need to run an agent you actively
distrust with system-level capabilities, add real sandboxing (container, VM,
network policy) UNDER the room — the engine composes fine with it, and the
walls above still apply.
