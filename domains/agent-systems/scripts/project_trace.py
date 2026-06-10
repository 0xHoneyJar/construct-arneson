#!/usr/bin/env python3
"""project_trace.py — deterministic projection: native sidecar → observed-trace/v1.

Usage:
    project_trace.py --native <sidecar.events.yaml> --out <dir>

One observed-trace/v1 JSON per (rung × trial) segment, derived mechanically from
the native session-events-agent sidecar (FR-8). The playout prose becomes
`narration`. producer.kind is `simulation`, claim_strength `simulation-derived`,
and `observation` is NEVER emitted — the host does not grade (FR-9 trust rule).
No LLM on this path.

The fixture is resolved from the preamble's state_path (relative to the sidecar
file's own directory); experiment fields come from the fixture manifest.

Exit codes: 0 ok / 1 input error / 2 contract violation (projection would break
the vendored contract — e.g. unknown rung_name, missing trial_end).
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from restricted_yaml import ParseError, parse_file  # noqa: E402

RUNG_NAMES = {0: "blind", 1: "reward-aware", 2: "adversarial"}


def err(msg):
    print(f"ERROR: [project_trace] {msg}", file=sys.stderr)


def _iso_ms_delta(start, end):
    fmt = "%Y-%m-%dT%H:%M:%S%z"
    s = datetime.strptime(start.replace("Z", "+0000"), fmt)
    e = datetime.strptime(end.replace("Z", "+0000"), fmt)
    return max(0, int((e - s).total_seconds() * 1000))


def main(argv):
    args = dict(zip(argv[1::2], argv[2::2]))
    native_path = args.get("--native")
    out_dir = args.get("--out")
    if not native_path or not out_dir or len(argv) != 5:
        err("usage: project_trace.py --native <sidecar.events.yaml> --out <dir>")
        return 1

    native_file = Path(native_path)
    if not native_file.is_file():
        err(f"native sidecar not found: {native_path}")
        return 1
    try:
        doc = parse_file(native_file)
    except ParseError as e:
        err(f"{native_path}: restricted-YAML parse failure: {e}")
        return 1

    preamble = doc.get("preamble") or {}
    events = doc.get("events") or []
    for field in ("session_id", "scenario_id", "run_id", "state_path", "provenance"):
        if field not in preamble:
            err(f"preamble missing required field: {field}")
            return 1

    fixture_dir = (native_file.resolve().parent / preamble["state_path"]).resolve()
    manifest_path = fixture_dir / "manifest.yaml"
    if not manifest_path.is_file():
        err(f"fixture manifest not found: {manifest_path} (from preamble.state_path)")
        return 1
    try:
        manifest = parse_file(manifest_path)
    except ParseError as e:
        err(f"{manifest_path}: parse failure: {e}")
        return 1
    for field in ("id", "incentive_state", "context"):
        if field not in manifest:
            err(f"fixture manifest missing required field: {field}")
            return 1

    incentive_state = str((fixture_dir / str(manifest["incentive_state"])).resolve())
    provenance = preamble["provenance"]
    producer_detail = (
        f"arneson persona host; model {provenance.get('model_id', '?')}; "
        f"construct {str(provenance.get('construct_git_sha', '?'))[:12]}; "
        f"run {preamble['run_id']}"
    )

    # Segment events into trials.
    trials, current = [], None
    for ev in events:
        etype = ev.get("type")
        if etype == "rung_start":
            if current is not None:
                err(f"rung_start at seq {ev.get('seq')} before previous trial_end — malformed sidecar")
                return 2
            current = {"start": ev, "turns": [], "artifacts": []}
        elif etype == "agent_turn" and current is not None:
            current["turns"].append(ev)
        elif etype == "artifact_declare" and current is not None:
            current["artifacts"].append(ev)
        elif etype == "trial_end":
            if current is None:
                err(f"trial_end at seq {ev.get('seq')} without rung_start")
                return 2
            current["end"] = ev
            trials.append(current)
            current = None
    if current is not None:
        err("sidecar ends inside an open trial (no trial_end) — partial sessions do not project")
        return 2
    if not trials:
        err("no completed (rung_start … trial_end) segments to project")
        return 1

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for t in trials:
        start, end = t["start"], t["end"]
        rung = start.get("rung")
        if rung not in RUNG_NAMES or start.get("rung_name") != RUNG_NAMES[rung]:
            err(f"trial rung/rung_name invalid or mismatched: {rung!r}/{start.get('rung_name')!r}")
            return 2
        if end.get("status") != "completed":
            err(f"trial_end status {end.get('status')!r} — only completed trials project")
            return 2
        trial_no = start.get("trial")

        narration_parts = []
        for turn in t["turns"]:
            narration_parts.append(f"{turn.get('narrated_action', '')} (why: {turn.get('why', '')})")
        for art in t["artifacts"]:
            narration_parts.append(f"[declared artifact: {art.get('path')}]")
        record = {
            "schema": "observed-trace/v1",
            "claim_strength": "simulation-derived",
            "producer": {
                "kind": "simulation",
                "id": "arneson-host",
                "detail": producer_detail,
            },
            "experiment": {
                "id": str(manifest["id"]),
                "fixture": str(fixture_dir),
                "incentive_state": incentive_state,
                "context": {
                    "name": str(manifest["context"]["name"]),
                    "value": manifest["context"]["value"],
                },
            },
            "run": {
                "rung": rung,
                "rung_name": start["rung_name"],
                "trial": trial_no,
                "status": "completed",
                "run_dir": f"runs/rung-{rung}/trial-{trial_no}",
                "started_at": start.get("at"),
                "duration_ms": _iso_ms_delta(start.get("at"), end.get("at")),
            },
            "narration": "\n".join(narration_parts) or "(no turns narrated)",
        }
        path = out / f"rung-{rung}-trial-{trial_no}.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        written.append(str(path))

    print(json.dumps({"projected": written, "trials": len(written)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
