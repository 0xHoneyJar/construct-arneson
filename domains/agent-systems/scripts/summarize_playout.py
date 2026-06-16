#!/usr/bin/env python3
"""summarize_playout.py — project a simulated-lane native sidecar into playout-summary/v1 (R1, cycle-004).

Usage:
    summarize_playout.py --sidecar <native-sidecar.yaml> --scenario-sha256 <64hex> [-o <out.json>]

The simulated lane records a native `session-events-agent` sidecar (prose
`narrated_action` + an optional `action_label` slug per turn). This post-pass
tool PROJECTS that stream into the structured `playout-summary/v1` shape that
`gap_report.py` can diff (sdd 3.1). It is a projection, never a grade and never
an inference:

  - action_labels come from the host-named `agent_turn.action_label` SLUG only.
    The prose `narrated_action` is NEVER parsed to recover a move (sdd 1.2) — a
    turn with no slug simply contributes no label.
  - outcome_signal is a deterministic map of the closed `trial_end.stop_reason`
    enum onto the closed OUTCOME_SIGNAL set (sdd 3.5). No judgement is made.

It does NOT touch the host serializer (OQ-1: a standalone post-pass over the
committed sidecar, runnable on fixtures without a live persona).

stdout: the playout-summary/v1 JSON (or the written path if -o given).
stderr: ERROR: [summarize_playout] ... on any failure.
exit:   0 success · 1 input/usage error. Deterministic: stable field + trial order, no clock.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from restricted_yaml import ParseError, parse as parse_restricted_yaml  # noqa: E402

# Closed map: trial_end.stop_reason enum -> OUTCOME_SIGNAL (sdd 3.5). The host's
# stop_reason is a label, not a verdict; this is a 1:1 label projection.
#   gave-up is a reserved OUTCOME_SIGNAL value not produced by the current
#   completed-trial stop_reason enum (early abandonment is a base event that does
#   not project) — so it never appears here, by design.
STOP_TO_SIGNAL = {
    "task_declared_done": "task-declared-done",
    "max_turns": "max-turns",
    "operator_pause": "safety-stop",
}


def err(msg):
    print(f"ERROR: [summarize_playout] {msg}", file=sys.stderr)


def parse_args(argv):
    sidecar = sha = out = None
    args = list(argv[1:])
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--sidecar":
            sidecar = _value(args, i)
            i += 2
        elif a == "--scenario-sha256":
            sha = _value(args, i)
            i += 2
        elif a in ("-o", "--out"):
            out = _value(args, i)
            i += 2
        else:
            raise _Usage(f"unexpected argument: {a!r}")
    if not sidecar or not sha:
        raise _Usage("usage: summarize_playout.py --sidecar <file> --scenario-sha256 <64hex> [-o <out>]")
    return sidecar, sha, out


class _Usage(Exception):
    pass


def _value(args, i):
    try:
        return args[i + 1]
    except IndexError:
        raise _Usage(f"{args[i]} requires a value")


def project(doc, scenario_sha256):
    """native session-events-agent doc -> playout-summary/v1 dict. Deterministic."""
    if not isinstance(doc, dict):
        raise ValueError("sidecar is not a mapping")
    preamble = doc.get("preamble")
    if not isinstance(preamble, dict) or not preamble.get("scenario_id"):
        raise ValueError("preamble.scenario_id missing")
    scenario_id = preamble["scenario_id"]
    events = doc.get("events")
    if not isinstance(events, list):
        raise ValueError("events list missing")

    trials = []
    cur = None  # the open (rung, trial) accumulator
    for ev in events:
        if not isinstance(ev, dict):
            continue
        etype = ev.get("type")
        if etype == "rung_start":
            cur = {"rung": ev.get("rung"), "trial": ev.get("trial"), "action_labels": []}
        elif etype == "agent_turn" and cur is not None:
            label = ev.get("action_label")
            if isinstance(label, str) and label:
                cur["action_labels"].append(label)
        elif etype == "trial_end" and cur is not None:
            stop_reason = ev.get("stop_reason")
            if stop_reason not in STOP_TO_SIGNAL:
                raise ValueError(f"unknown stop_reason {stop_reason!r} (rung {cur['rung']} trial {cur['trial']})")
            trials.append({
                "rung": cur["rung"],
                "trial": cur["trial"],
                "action_labels": cur["action_labels"],
                "outcome_signal": STOP_TO_SIGNAL[stop_reason],
                "stop_reason": stop_reason,
            })
            cur = None

    return {
        "schema": "playout-summary/v1",
        "lane": "simulated",
        "scenario_id": scenario_id,
        "scenario_sha256": scenario_sha256,
        "producer": {"kind": "simulation", "claim_strength": "simulation-derived"},
        "trials": trials,
    }


def main(argv):
    try:
        sidecar, sha, out = parse_args(argv)
    except _Usage as e:
        err(str(e))
        return 1
    try:
        text = open(sidecar, encoding="utf-8").read()
    except OSError as e:
        err(f"cannot read sidecar {sidecar}: {e}")
        return 1
    try:
        doc = parse_restricted_yaml(text)
    except ParseError as e:
        err(f"sidecar is not valid YAML ({sidecar}): {e}")
        return 1
    try:
        summary = project(doc, sha)
    except ValueError as e:
        err(f"cannot project {sidecar}: {e}")
        return 1

    rendered = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    if out:
        try:
            open(out, "w", encoding="utf-8").write(rendered)
        except OSError as e:
            err(f"cannot write {out}: {e}")
            return 1
        print(out)
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
