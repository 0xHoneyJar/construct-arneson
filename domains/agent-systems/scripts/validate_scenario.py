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
import re
import sys
from pathlib import Path

INDENT = 2


def err(msg):
    print(f"ERROR: [validate_scenario] {msg}", file=sys.stderr)


def info(msg):
    print(f"INFO: [validate_scenario] {msg}", file=sys.stderr)


class ParseError(Exception):
    pass


def _scalar(tok):
    tok = tok.strip()
    if tok.startswith("[") and tok.endswith("]"):
        inner = tok[1:-1].strip()
        return [] if not inner else [_scalar(t) for t in inner.split(",")]
    if (tok.startswith('"') and tok.endswith('"')) or (tok.startswith("'") and tok.endswith("'")):
        return tok[1:-1]
    if re.fullmatch(r"-?\d+", tok):
        return int(tok)
    if tok in ("true", "false"):
        return tok == "true"
    if tok in ("null", "~", ""):
        return None
    return tok


def _strip(line):
    """Remove comments outside quotes (restricted: assumes no '#' inside quoted strings followed by quotes)."""
    out, in_q = [], None
    for ch in line:
        if in_q:
            out.append(ch)
            if ch == in_q:
                in_q = None
        elif ch in "\"'":
            in_q = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def parse_restricted_yaml(text):
    lines = []
    for raw in text.splitlines():
        stripped = _strip(raw)
        if stripped.strip():
            indent = len(stripped) - len(stripped.lstrip(" "))
            if indent % INDENT:
                raise ParseError(f"indent not a multiple of {INDENT}: {raw!r}")
            lines.append((indent // INDENT, stripped.strip()))

    def parse_block(pos, depth):
        node = None
        while pos < len(lines):
            d, content = lines[pos]
            if d < depth:
                break
            if d > depth:
                raise ParseError(f"unexpected indent at: {content!r}")
            if content.startswith("- "):
                if node is None:
                    node = []
                if not isinstance(node, list):
                    raise ParseError(f"mixed list/map at: {content!r}")
                item_text = content[2:].strip()
                m = re.match(r"^([A-Za-z0-9_-]+):(.*)$", item_text)
                if m:
                    item = {}
                    key, rest = m.group(1), m.group(2).strip()
                    if rest:
                        item[key] = _scalar(rest)
                        pos += 1
                    else:
                        sub, pos = parse_block(pos + 1, depth + 2)
                        item[key] = sub
                    while pos < len(lines) and lines[pos][0] == depth + 1 and not lines[pos][1].startswith("- "):
                        sub_map, pos = parse_block(pos, depth + 1)
                        if not isinstance(sub_map, dict):
                            raise ParseError("expected map continuation in list item")
                        item.update(sub_map)
                    node.append(item)
                else:
                    node.append(_scalar(item_text))
                    pos += 1
                continue
            m = re.match(r"^([A-Za-z0-9_-]+):(.*)$", content)
            if not m:
                raise ParseError(f"unparseable line: {content!r}")
            if node is None:
                node = {}
            if not isinstance(node, dict):
                raise ParseError(f"mixed map/list at: {content!r}")
            key, rest = m.group(1), m.group(2).strip()
            if rest:
                node[key] = _scalar(rest)
                pos += 1
            else:
                child, pos = parse_block(pos + 1, depth + 1)
                node[key] = child if child is not None else {}
        return node, pos

    tree, pos = parse_block(0, 0)
    if pos != len(lines):
        raise ParseError(f"trailing content at: {lines[pos][1]!r}")
    return tree if tree is not None else {}


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
