#!/usr/bin/env python3
"""emit_decision_trace.py — deterministic projection: native sim sidecar → decision-trace/v1 corpus.

Usage:
    emit_decision_trace.py --in <events.yaml> --out <corpus_dir>

One `decision-trace/v1` JSON record per `agent_turn` that carries an
`action_label`, projected from an Arneson SIMULATED-lane session-events-agent
sidecar. Sibling to `project_trace.py` (which projects the same native sidecar
into the reward-hack-shaped `observed-trace/v1`); this projects the
decision-shaped `decision-trace/v1` the revealed-strategy lens (Gygax cycle-012)
reasons over.

CHOSEN-ONLY (SDD §1.2 / brief OQ-1): the sim log records the move TAKEN
(`action_label`), not the legal option set. There is no `offered` field. So each
record's `offered` equals its `chosen` (`[{"type": <action_label>}]`) and
`producer.detail` carries an honest offered-set-unrecorded marker. Inventing a
plausible offered set the host never presented would violate producer-never-judges
(NFR-2); equal offered/chosen is the only honest projection of a chosen-only log.
A chosen-only corpus is contract-valid (`offered` minItems 1, `chosen ⊆ offered`
holds trivially) but analytically empty (no alternatives ⇒ no revealed preference)
— that is the documented MVP boundary; analytic value needs offered-set capture
(future work).

`producer.kind` is `simulation` and `claim_strength` `simulation-derived` —
hardcoded literals, never derived from input: a sim log can never produce a
`real-agent-observed` record (NFR-5). No LLM, no `datetime.now()`, no `random`
(NFR-3). Imports only stdlib + the sibling `restricted_yaml` (NFR-1).

Self-checks every emitted record against the vendored `decision-trace.v1.schema.json`
(required fields, `additionalProperties: false`, enums, the producer-bound claim
rule) and REFUSES (exit 2) on vendor-pin drift or any contract violation — never
ship a broken corpus (mirrors `validate_sidecar.py`).

Exit codes: 0 ok / 1 input error (missing/empty/degenerate input) /
2 contract violation or vendor drift.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from restricted_yaml import ParseError, parse_file  # noqa: E402

VENDOR_DIR = Path(__file__).resolve().parent.parent / "schemas" / "vendor"
VENDOR_PIN = VENDOR_DIR / "VENDOR.yaml"
VENDORED_SCHEMA = VENDOR_DIR / "decision-trace.v1.schema.json"

CLAIM_ENUM = {"real-agent-observed", "simulation-derived"}
PRODUCER_KIND_ENUM = {"real-agent", "simulation"}
PROVENANCE_KEYS = {"agent_cmd_sha256", "engine_git_sha", "model_id", "construct_sha"}

# §1.2 honesty flag, stamped on every chosen-only record.
OFFERED_UNRECORDED_DETAIL = (
    "offered-set-unrecorded: chosen-only projection "
    "(the sim log captures the move taken, not the legal option set)"
)

TOP_REQUIRED = [
    "schema", "claim_strength", "producer", "corpus",
    "actor_id", "episode_id", "t", "context", "offered", "chosen",
]
TOP_ALLOWED = set(TOP_REQUIRED) | {"outcome"}


def err(msg):
    print(f"ERROR: [emit_decision_trace] {msg}", file=sys.stderr)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_str(v, min_length=0):
    return isinstance(v, str) and len(v) >= min_length


def vendor_selfcheck():
    """Refuse to run unless the vendored schema matches the VENDOR.yaml pin.

    The hand-written contract checks below were written against exactly these
    bytes (the stdlib has no JSON-Schema engine). Drift is loud (exit 2), never
    approximated — mirrors validate_sidecar.py.
    """
    if not VENDOR_PIN.is_file() or not VENDORED_SCHEMA.is_file():
        err("vendored contract or VENDOR.yaml missing under schemas/vendor/")
        sys.exit(2)
    pin_text = VENDOR_PIN.read_text(encoding="utf-8")
    pinned, current_file = None, None
    for line in pin_text.splitlines():
        m = re.match(r"\s*-?\s*vendored:\s*(\S+)", line)
        if m:
            current_file = m.group(1)
            continue
        m = re.match(r"\s*sha256:\s*([0-9a-f]{64})", line)
        if m and current_file and current_file.endswith("decision-trace.v1.schema.json"):
            pinned = m.group(1)
    if pinned is None:
        err("VENDOR.yaml carries no sha256 pin for decision-trace.v1.schema.json")
        sys.exit(2)
    actual = hashlib.sha256(VENDORED_SCHEMA.read_bytes()).hexdigest()
    if actual != pinned:
        err(
            "CONTRACT DRIFT: vendored decision-trace.v1 differs from pin/upstream. "
            "Re-vendor + revisit emit_decision_trace.py before producing a corpus. "
            f"(pinned {pinned[:12]}..., actual {actual[:12]}...)"
        )
        sys.exit(2)


def _check_extra_keys(obj, allowed, where, v):
    for k in sorted(set(obj.keys()) - set(allowed)):
        v.append(f"{where}: additional property '{k}' not allowed")


def _validate_option(opt, where, v):
    if not isinstance(opt, dict):
        v.append(f"{where}: not an object")
        return
    if "type" not in opt:
        v.append(f"{where}: required property 'type' missing")
    _check_extra_keys(opt, {"type", "id", "label"}, where, v)
    if "type" in opt and not _is_str(opt["type"], 1):
        v.append(f"{where}.type: must be a non-empty string")
    if "id" in opt and not _is_str(opt["id"], 1):
        v.append(f"{where}.id: must be a non-empty string")
    if "label" in opt and not isinstance(opt["label"], str):
        v.append(f"{where}.label: must be a string")


def validate_record(r):
    """Return a list of violation strings (empty = conformant to decision-trace/v1).

    Hand-encodes the vendored contract's structural constraints (required keys,
    additionalProperties:false, enums, option shape) plus the producer-bound
    claim rule (a simulation may not tag its output as observed).
    """
    if not isinstance(r, dict):
        return ["top-level: not a JSON object"]
    v = []
    for key in TOP_REQUIRED:
        if key not in r:
            v.append(f"top-level: required property '{key}' missing")
    _check_extra_keys(r, TOP_ALLOWED, "top-level", v)

    if "schema" in r and r["schema"] != "decision-trace/v1":
        v.append(f"schema: must be 'decision-trace/v1', got {r['schema']!r}")
    if "claim_strength" in r and r["claim_strength"] not in CLAIM_ENUM:
        v.append(f"claim_strength: {r['claim_strength']!r} not in {sorted(CLAIM_ENUM)}")

    producer = r.get("producer")
    if isinstance(producer, dict):
        for key in ("kind", "id"):
            if key not in producer:
                v.append(f"producer: required property '{key}' missing")
        _check_extra_keys(producer, {"kind", "id", "detail", "provenance"}, "producer", v)
        if "kind" in producer and producer["kind"] not in PRODUCER_KIND_ENUM:
            v.append(f"producer.kind: {producer['kind']!r} not in {sorted(PRODUCER_KIND_ENUM)}")
        if "id" in producer and not _is_str(producer["id"], 1):
            v.append("producer.id: must be a non-empty string")
        if "detail" in producer and not isinstance(producer["detail"], str):
            v.append("producer.detail: must be a string")
        if "provenance" in producer:
            prov = producer["provenance"]
            if not isinstance(prov, dict):
                v.append("producer.provenance: not an object")
            else:
                _check_extra_keys(prov, PROVENANCE_KEYS, "producer.provenance", v)
                for key in sorted(PROVENANCE_KEYS & set(prov.keys())):
                    if not _is_str(prov[key], 1):
                        v.append(f"producer.provenance.{key}: must be a non-empty string")
    elif producer is not None:
        v.append("producer: not an object")

    corpus = r.get("corpus")
    if isinstance(corpus, dict):
        for key in ("id", "game"):
            if key not in corpus:
                v.append(f"corpus: required property '{key}' missing")
        _check_extra_keys(corpus, {"id", "game"}, "corpus", v)
        for key in ("id", "game"):
            if key in corpus and not _is_str(corpus[key], 1):
                v.append(f"corpus.{key}: must be a non-empty string")
    elif corpus is not None:
        v.append("corpus: not an object")

    if "actor_id" in r and not _is_str(r["actor_id"], 1):
        v.append("actor_id: must be a non-empty string")
    if "episode_id" in r and not _is_str(r["episode_id"], 1):
        v.append("episode_id: must be a non-empty string")
    if "t" in r and (not _is_int(r["t"]) or r["t"] < 0):
        v.append("t: must be an integer >= 0")

    context = r.get("context")
    if isinstance(context, dict):
        if "segment" not in context:
            v.append("context: required property 'segment' missing")
        _check_extra_keys(context, {"segment", "phase", "digest"}, "context", v)
        if "segment" in context and not _is_str(context["segment"], 1):
            v.append("context.segment: must be a non-empty string")
        if "phase" in context and not isinstance(context["phase"], str):
            v.append("context.phase: must be a string")
        if "digest" in context:
            digest = context["digest"]
            if not isinstance(digest, dict):
                v.append("context.digest: not an object")
            else:
                for k, val in digest.items():
                    if not (_is_str(val) or _is_number(val)):
                        v.append(f"context.digest.{k}: must be a string or number")
    elif context is not None:
        v.append("context: not an object")

    for field in ("offered", "chosen"):
        arr = r.get(field)
        if field in r:
            if not isinstance(arr, list):
                v.append(f"{field}: must be an array")
            elif len(arr) < 1:
                v.append(f"{field}: must have at least one item (minItems: 1)")
            else:
                for i, opt in enumerate(arr):
                    _validate_option(opt, f"{field}[{i}]", v)

    # Producer-bound claim rule (the laundering case the schema exists to stop).
    if isinstance(producer, dict) and "claim_strength" in r:
        kind, claim = producer.get("kind"), r["claim_strength"]
        if kind == "real-agent" and claim != "real-agent-observed":
            v.append("claim: producer.kind 'real-agent' requires claim_strength 'real-agent-observed'")
        if kind == "simulation" and claim != "simulation-derived":
            v.append("claim: producer.kind 'simulation' requires claim_strength 'simulation-derived' "
                     "(a simulation may not launder its output as observed)")

    # chosen ⊆ offered, matched by type (and id when present on the chosen item).
    if isinstance(r.get("offered"), list) and isinstance(r.get("chosen"), list):
        offered_types = {o.get("type") for o in r["offered"] if isinstance(o, dict)}
        offered_pairs = {(o.get("type"), o.get("id")) for o in r["offered"] if isinstance(o, dict)}
        for i, c in enumerate(r["chosen"]):
            if not isinstance(c, dict):
                continue
            ok = (c.get("type"), c.get("id")) in offered_pairs if c.get("id") is not None \
                else c.get("type") in offered_types
            if not ok:
                v.append(f"chosen[{i}]: {c.get('type')!r} not present in offered (chosen ⊆ offered)")
    return v


def build_records(doc):
    """Project the native sim sidecar into decision-trace/v1 records.

    Iterates events in document (= seq) order. Each `agent_turn` carrying an
    `action_label` key becomes one record; `context.segment` tracks the nearest
    preceding `rung_start.rung_name` (falling back to `preamble.visibility_rung`).
    Turns with NO `action_label` key are skipped (chosen-only: nothing recorded);
    a present-but-malformed label is projected as-is and caught by the self-check
    (exit 2 — never ship a broken corpus).
    """
    preamble = doc.get("preamble") or {}
    events = doc.get("events") or []
    for field in ("scenario_id", "run_id", "domain"):
        if field not in preamble:
            err(f"preamble missing required field: {field}")
            return None

    corpus_id = f"{preamble['scenario_id']}:{preamble['run_id']}"
    corpus_game = str(preamble["domain"])
    episode_id = str(preamble["run_id"])

    # actor_id: explicit persona/actor id in the preamble, else a stable
    # corpus.id-derived token (documented; never a clock/uuid — RA-2).
    actor_id = preamble.get("actor_id") or preamble.get("persona")
    if not _is_str(actor_id, 1):
        actor_id = f"sim:{corpus_id}"

    # producer.provenance: map the native preamble's provenance onto the contract
    # keys, stamping only present strings (the sim lane knows model_id +
    # construct_sha; engine/cmd shas belong to the real lane). Mirrors project_trace.
    provenance = preamble.get("provenance") or {}
    producer_provenance = {}
    if _is_str(provenance.get("model_id"), 1):
        producer_provenance["model_id"] = provenance["model_id"]
    if _is_str(provenance.get("construct_git_sha"), 1):
        producer_provenance["construct_sha"] = provenance["construct_git_sha"]

    # Default segment from the preamble's visibility rung; refined as rung_start
    # events are seen.
    segment = None
    if "visibility_rung" in preamble:
        segment = f"rung:{preamble['visibility_rung']}"

    records, t = [], 0
    for ev in events:
        etype = ev.get("type")
        if etype == "rung_start":
            if "rung_name" in ev:
                segment = f"rung:{ev['rung_name']}"
            elif "rung" in ev:
                segment = f"rung:{ev['rung']}"
        elif etype == "agent_turn" and "action_label" in ev:
            record = {
                "schema": "decision-trace/v1",
                "claim_strength": "simulation-derived",
                "producer": {
                    "kind": "simulation",
                    "id": "arneson-host",
                    "detail": OFFERED_UNRECORDED_DETAIL,
                    **({"provenance": dict(producer_provenance)} if producer_provenance else {}),
                },
                "corpus": {"id": corpus_id, "game": corpus_game},
                "actor_id": actor_id,
                "episode_id": episode_id,
                "t": t,
                "context": {"segment": segment if segment is not None else "rung:unknown"},
                "offered": [{"type": ev["action_label"]}],
                "chosen": [{"type": ev["action_label"]}],
            }
            records.append(record)
            t += 1

    if not records:
        err("no agent_turn with an action_label to project — a chosen-only sim "
            "log must record at least one move (degenerate input)")
        return None
    return records


def _sanitize(name):
    return re.sub(r"[^A-Za-z0-9._-]", "-", str(name))


def write_corpus(records, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for r in records:
        fname = f"{_sanitize(r['corpus']['id'])}-{r['t']}.json"
        path = out / fname
        path.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(str(path))
    return written


def main(argv):
    vendor_selfcheck()

    args = dict(zip(argv[1::2], argv[2::2]))
    in_path = args.get("--in")
    out_dir = args.get("--out")
    if not in_path or not out_dir or len(argv) != 5:
        err("usage: emit_decision_trace.py --in <events.yaml> --out <corpus_dir>")
        return 1

    in_file = Path(in_path)
    if not in_file.is_file():
        err(f"sim sidecar not found: {in_path}")
        return 1
    try:
        doc = parse_file(in_file)
    except ParseError as e:
        err(f"{in_path}: restricted-YAML parse failure: {e}")
        return 1
    if not isinstance(doc, dict) or not doc:
        err(f"{in_path}: empty or non-mapping sidecar")
        return 1

    records = build_records(doc)
    if records is None:
        return 1

    for i, r in enumerate(records):
        violations = validate_record(r)
        if violations:
            for violation in violations:
                err(f"record {i} (t={r.get('t')}): {violation}")
            err("refusing to write a corpus that violates the vendored contract")
            return 2

    written = write_corpus(records, out_dir)
    print(json.dumps({"corpus": str(out_dir), "records": written, "decisions": len(written)},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
