#!/usr/bin/env python3
"""validate_scenario.py — gate for agent-scenario files (scenario.schema.yaml).

Usage:
    validate_scenario.py [--lane real|simulated] <scenario.yaml>

Parses a RESTRICTED YAML subset (stdlib-only rule, NFR-5 — same approach as the
proven character-voice ingest parser): nested maps, lists of scalars, lists of
small blocks, inline [a, b] lists, scalar ints/strings. No anchors, no multiline
scalars, no flow maps. Scenario files are deliberately simple shapes.

Checks (sdd.md 5.3 + 6.1):
- required fields per scenario.schema.yaml; lane-conditional fields via --lane
- stopping.max_turns REQUIRED -> "UNBOUNDED SCENARIO REJECTED" (NFR-2, exit 1)
- fixture manifest sha256 verified (exit 2 on mismatch)
- simulated lane: persona file sha256 verified (exit 2 on mismatch)
- INFO note when sibling scenarios differ in >1 of {fixture, persona, agent_cmd}
  (one-variable-per-scenario-family is convention, not enforcement)

stdout: JSON summary of resolved + verified fields. Diagnostics on stderr.
Exit codes: 0 ok / 1 input error / 2 checksum-contract violation.
"""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from restricted_yaml import ParseError, parse as parse_restricted_yaml  # noqa: E402


def err(msg):
    print(f"ERROR: [validate_scenario] {msg}", file=sys.stderr)


def info(msg):
    print(f"INFO: [validate_scenario] {msg}", file=sys.stderr)


def warn(msg):
    print(f"WARNING: [validate_scenario] {msg}", file=sys.stderr)


KNOWN_TOP_KEYS = {
    "scenario_id", "fixture", "rungs", "trials", "stopping",
    "memory", "safety", "visibility", "agent_cmd", "persona",
}


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_scenario(path):
    p = Path(path)
    if not p.is_file():
        err(f"scenario file not found: {path}")
        sys.exit(1)
    try:
        doc = parse_restricted_yaml(p.read_text(encoding="utf-8"))
    except ParseError as e:
        err(f"{path}: restricted-YAML parse failure: {e}")
        sys.exit(1)
    if not isinstance(doc, dict):
        err(f"{path}: top level must be a map")
        sys.exit(1)
    return doc


def _require(doc, dotted, typ, problems):
    node = doc
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            problems.append(f"required field missing: {dotted}")
            return None
        node = node[part]
    if typ is int and (isinstance(node, bool) or not isinstance(node, int)):
        problems.append(f"{dotted}: must be an integer")
        return None
    if typ is str and not isinstance(node, str):
        problems.append(f"{dotted}: must be a string")
        return None
    if typ is dict and not isinstance(node, dict):
        problems.append(f"{dotted}: must be a block")
        return None
    if typ is list and not isinstance(node, list):
        problems.append(f"{dotted}: must be a list")
        return None
    return node


def one_variable_note(scenario_path, doc):
    """INFO when sibling scenarios differ in >1 of {fixture, persona, agent_cmd}."""
    me = Path(scenario_path).resolve()

    def dims(d):
        fixture = d.get("fixture", {}).get("path") if isinstance(d.get("fixture"), dict) else None
        persona = d.get("persona", {}).get("ref") if isinstance(d.get("persona"), dict) else None
        return {"fixture": fixture, "persona": persona, "agent_cmd": d.get("agent_cmd")}

    def lane_of(d):
        return "real" if d.get("agent_cmd") else ("simulated" if d.get("persona") else None)

    mine = dims(doc)
    for sibling in sorted(me.parent.glob("*.yaml")):
        if sibling.resolve() == me:
            continue
        try:
            other = parse_restricted_yaml(sibling.read_text(encoding="utf-8"))
        except (ParseError, OSError):
            continue
        if not isinstance(other, dict) or "scenario_id" not in other:
            continue
        if lane_of(other) != lane_of(doc):
            continue  # cross-lane scenarios naturally differ; the discipline is per-family
        diff = [k for k, val in dims(other).items() if val != mine[k]]
        if len(diff) > 1:
            info(
                f"one-variable note: sibling scenario {sibling.name} differs in more than one of "
                f"{{fixture, persona, agent_cmd}} ({', '.join(diff)}) — rung varies inside a "
                "scenario; one other variable varies across (domain.conventions.md)"
            )


def main(argv):
    args = list(argv[1:])
    lane = None
    if "--lane" in args:
        i = args.index("--lane")
        try:
            lane = args[i + 1]
        except IndexError:
            err("--lane requires a value: real|simulated")
            return 1
        del args[i:i + 2]
        if lane not in ("real", "simulated"):
            err(f"--lane must be real|simulated, got {lane!r}")
            return 1
    if len(args) != 1:
        err("usage: validate_scenario.py [--lane real|simulated] <scenario.yaml>")
        return 1

    scenario_path = args[0]
    doc = load_scenario(scenario_path)
    base = Path(scenario_path).resolve().parent
    problems = []

    # WARN (not reject) on unknown fields: a typo'd optional key would otherwise be
    # silently dropped and the run would proceed against the operator's intent.
    # Warn-not-reject keeps additive schema evolution possible.
    for key in sorted(set(doc.keys()) - KNOWN_TOP_KEYS):
        warn(f"unknown field '{key}' ignored — known fields: {', '.join(sorted(KNOWN_TOP_KEYS))}")

    scenario_id = _require(doc, "scenario_id", str, problems)
    fixture_path = _require(doc, "fixture.path", str, problems)
    fixture_pin = _require(doc, "fixture.manifest_sha256", str, problems)
    rungs = _require(doc, "rungs", list, problems)
    trials = _require(doc, "trials", int, problems)
    _require(doc, "safety.agreement", dict, problems)

    # NFR-2: bounded runs. Distinct message per the error catalog.
    stopping = doc.get("stopping")
    max_turns = None
    if not isinstance(stopping, dict) or "max_turns" not in stopping:
        err("UNBOUNDED SCENARIO REJECTED: stopping.max_turns required")
        return 1
    max_turns = stopping["max_turns"]
    if isinstance(max_turns, bool) or not isinstance(max_turns, int) or max_turns < 1:
        problems.append("stopping.max_turns: must be an integer >= 1")
    timeout_seconds = stopping.get("timeout_seconds")
    if timeout_seconds is not None and (isinstance(timeout_seconds, bool)
                                        or not isinstance(timeout_seconds, int) or timeout_seconds < 1):
        problems.append("stopping.timeout_seconds: must be an integer >= 1 when present")

    if rungs is not None:
        if not rungs:
            problems.append("rungs: must be non-empty")
        for r in rungs:
            if isinstance(r, bool) or not isinstance(r, int) or not 0 <= r <= 2:
                problems.append(f"rungs: {r!r} not an integer in [0, 2]")
    if trials is not None and trials < 1:
        problems.append("trials: must be >= 1")

    memory = doc.get("memory", "fresh")
    if memory not in ("fresh", "continuing"):
        problems.append(f"memory: {memory!r} not in [fresh, continuing]")

    visibility = doc.get("visibility")
    if visibility is not None:
        if not isinstance(visibility, list):
            problems.append("visibility: must be a list of per-rung blocks")
        else:
            for entry in visibility:
                if not isinstance(entry, dict) or "rung" not in entry:
                    problems.append("visibility: each entry must be a block with a rung field")

    if lane == "real":
        agent_cmd = _require(doc, "agent_cmd", str, problems)
        if agent_cmd and "{prompt}" not in agent_cmd and "{promptfile}" not in agent_cmd:
            problems.append("agent_cmd: template must contain {prompt} or {promptfile}")
    if lane == "simulated":
        _require(doc, "persona.ref", str, problems)
        _require(doc, "persona.sha256", str, problems)

    if problems:
        for p in problems:
            err(f"{scenario_path}: {p}")
        return 1

    # Checksum verification (exit 2 on mismatch — the pin is the contract).
    fixture_dir = (base / fixture_path).resolve() if not Path(fixture_path).is_absolute() else Path(fixture_path)
    manifest = fixture_dir / "manifest.yaml"
    if not manifest.is_file():
        err(f"fixture manifest not found: {manifest}")
        return 1
    actual = sha256_file(manifest)
    if actual != fixture_pin:
        err(
            f"checksum mismatch: fixture.manifest_sha256 — ref {manifest}, "
            f"expected {fixture_pin}, actual {actual}"
        )
        return 2

    persona_summary = None
    if lane == "simulated":
        persona_ref = doc["persona"]["ref"]
        persona_file = (base / persona_ref).resolve() if not Path(persona_ref).is_absolute() else Path(persona_ref)
        if not persona_file.is_file():
            err(f"persona file not found: {persona_file}")
            return 1
        actual = sha256_file(persona_file)
        if actual != doc["persona"]["sha256"]:
            err(
                f"checksum mismatch: persona.sha256 — ref {persona_file}, "
                f"expected {doc['persona']['sha256']}, actual {actual}"
            )
            return 2
        persona_summary = {"ref": persona_ref, "sha256": actual}

    one_variable_note(scenario_path, doc)

    summary = {
        "scenario_id": scenario_id,
        "lane": lane,
        "fixture": {"path": str(fixture_dir), "manifest_sha256": fixture_pin, "verified": True},
        "rungs": rungs,
        "trials": trials,
        "runs_planned": len(rungs) * trials,
        "stopping": {"max_turns": max_turns, "timeout_seconds": timeout_seconds},
        "memory": memory,
        "persona": persona_summary,
        "agent_cmd": doc.get("agent_cmd"),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
