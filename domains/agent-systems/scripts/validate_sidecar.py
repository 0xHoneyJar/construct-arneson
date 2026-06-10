#!/usr/bin/env python3
"""validate_sidecar.py — contract-specific validator for observed-trace/v1 sidecars.

Usage:
    validate_sidecar.py <sidecar.json> [<sidecar.json> ...]
    cat sidecar.json | validate_sidecar.py -

NOT a general JSON Schema engine (stdlib-only rule, NFR-5). It hard-codes exactly
the observed-trace/v1 constraints — required keys, enums, additionalProperties
rejection, and the three allOf conditionals — and REFUSES TO RUN (exit 2) when the
vendored schema's sha256 differs from VENDOR.yaml: this validator was written
against that exact byte content (sdd.md 5.2.1). Drift is loud, never approximated.

Exit codes: 0 all conformant / 1 input error (missing file, bad JSON) /
2 contract violation or vendor drift.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

VENDOR_DIR = Path(__file__).resolve().parent.parent / "schemas" / "vendor"
VENDOR_PIN = VENDOR_DIR / "VENDOR.yaml"
VENDORED_SCHEMA = VENDOR_DIR / "observed-trace.v1.schema.json"

CLAIM_ENUM = {"real-agent-observed", "simulation-derived"}
PRODUCER_KIND_ENUM = {"real-agent", "simulation"}
RUNG_NAME_ENUM = {"blind", "reward-aware", "adversarial"}
STATUS_ENUM = {"completed", "runner-error", "timeout"}
CLASSIFICATION_ENUM = {"fixed", "hacked", "failed"}
ARTIFACT_STATUS_ENUM = {"intact", "modified", "added", "deleted"}

TOP_REQUIRED = ["schema", "claim_strength", "producer", "experiment", "run", "narration"]
TOP_ALLOWED = set(TOP_REQUIRED) | {"observation"}


def err(msg):
    print(f"ERROR: [validate_sidecar] {msg}", file=sys.stderr)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_str(v, min_length=0):
    return isinstance(v, str) and len(v) >= min_length


def vendor_selfcheck():
    """Refuse to run unless the vendored schema matches the VENDOR.yaml pin."""
    if not VENDOR_PIN.is_file() or not VENDORED_SCHEMA.is_file():
        err("vendored contract or VENDOR.yaml missing under schemas/vendor/")
        sys.exit(2)
    pin_text = VENDOR_PIN.read_text(encoding="utf-8")
    # Restricted parse: find the sha256 line in the entry whose `vendored:` names the schema file.
    pinned = None
    current_file = None
    for line in pin_text.splitlines():
        m = re.match(r"\s*-?\s*vendored:\s*(\S+)", line)
        if m:
            current_file = m.group(1)
            continue
        m = re.match(r"\s*sha256:\s*([0-9a-f]{64})", line)
        if m and current_file and current_file.endswith("observed-trace.v1.schema.json"):
            pinned = m.group(1)
    if pinned is None:
        err("VENDOR.yaml carries no sha256 pin for observed-trace.v1.schema.json")
        sys.exit(2)
    actual = hashlib.sha256(VENDORED_SCHEMA.read_bytes()).hexdigest()
    if actual != pinned:
        err(
            "CONTRACT DRIFT: vendored observed-trace.v1 differs from pin/upstream. "
            "Re-vendor + revisit validate_sidecar.py before producing batches. "
            f"(pinned {pinned[:12]}..., actual {actual[:12]}...)"
        )
        sys.exit(2)


def _check_extra_keys(obj, allowed, where, violations):
    extras = sorted(set(obj.keys()) - set(allowed))
    for k in extras:
        violations.append(f"{where}: additional property '{k}' not allowed")


def validate_obj(obj):
    """Return a list of violation strings (empty = conformant to observed-trace/v1)."""
    v = []
    if not isinstance(obj, dict):
        return ["top-level: not a JSON object"]

    for key in TOP_REQUIRED:
        if key not in obj:
            v.append(f"top-level: required property '{key}' missing")
    _check_extra_keys(obj, TOP_ALLOWED, "top-level", v)

    if "schema" in obj and obj["schema"] != "observed-trace/v1":
        v.append(f"schema: must be 'observed-trace/v1' (consumers hard-reject unknown versions), got {obj['schema']!r}")

    if "claim_strength" in obj and obj["claim_strength"] not in CLAIM_ENUM:
        v.append(f"claim_strength: {obj['claim_strength']!r} not in {sorted(CLAIM_ENUM)}")

    producer = obj.get("producer")
    if producer is not None:
        if not isinstance(producer, dict):
            v.append("producer: not an object")
        else:
            for key in ("kind", "id"):
                if key not in producer:
                    v.append(f"producer: required property '{key}' missing")
            _check_extra_keys(producer, {"kind", "id", "detail"}, "producer", v)
            if "kind" in producer and producer["kind"] not in PRODUCER_KIND_ENUM:
                v.append(f"producer.kind: {producer['kind']!r} not in {sorted(PRODUCER_KIND_ENUM)}")
            if "id" in producer and not _is_str(producer["id"], 1):
                v.append("producer.id: must be a non-empty string")
            if "detail" in producer and not isinstance(producer["detail"], str):
                v.append("producer.detail: must be a string")

    experiment = obj.get("experiment")
    if experiment is not None:
        if not isinstance(experiment, dict):
            v.append("experiment: not an object")
        else:
            for key in ("id", "fixture", "incentive_state", "context"):
                if key not in experiment:
                    v.append(f"experiment: required property '{key}' missing")
            _check_extra_keys(experiment, {"id", "fixture", "incentive_state", "context"}, "experiment", v)
            for key in ("id", "fixture", "incentive_state"):
                if key in experiment and not _is_str(experiment[key], 1):
                    v.append(f"experiment.{key}: must be a non-empty string")
            ctx = experiment.get("context")
            if ctx is not None:
                if not isinstance(ctx, dict):
                    v.append("experiment.context: not an object")
                else:
                    for key in ("name", "value"):
                        if key not in ctx:
                            v.append(f"experiment.context: required property '{key}' missing")
                    _check_extra_keys(ctx, {"name", "value"}, "experiment.context", v)
                    if "name" in ctx and not _is_str(ctx["name"], 1):
                        v.append("experiment.context.name: must be a non-empty string")
                    if "value" in ctx and not _is_number(ctx["value"]):
                        v.append("experiment.context.value: must be a number")

    run = obj.get("run")
    if run is not None:
        if not isinstance(run, dict):
            v.append("run: not an object")
        else:
            required = ("rung", "rung_name", "trial", "status", "run_dir", "started_at", "duration_ms")
            for key in required:
                if key not in run:
                    v.append(f"run: required property '{key}' missing")
            _check_extra_keys(run, set(required), "run", v)
            if "rung" in run and (not _is_int(run["rung"]) or not 0 <= run["rung"] <= 2):
                v.append("run.rung: must be an integer in [0, 2]")
            if "rung_name" in run and run["rung_name"] not in RUNG_NAME_ENUM:
                v.append(f"run.rung_name: {run['rung_name']!r} not in {sorted(RUNG_NAME_ENUM)}")
            if "trial" in run and (not _is_int(run["trial"]) or run["trial"] < 1):
                v.append("run.trial: must be an integer >= 1")
            if "status" in run and run["status"] not in STATUS_ENUM:
                v.append(f"run.status: {run['status']!r} not in {sorted(STATUS_ENUM)}")
            if "run_dir" in run and not _is_str(run["run_dir"], 1):
                v.append("run.run_dir: must be a non-empty string")
            if "started_at" in run and not _is_str(run["started_at"], 1):
                v.append("run.started_at: must be a non-empty string")
            if "duration_ms" in run and (not _is_number(run["duration_ms"]) or run["duration_ms"] < 0):
                v.append("run.duration_ms: must be a number >= 0")

    observation = obj.get("observation")
    if observation is not None:
        if not isinstance(observation, dict):
            v.append("observation: not an object")
        else:
            required = ("classification", "exit_code", "anomaly_note", "artifacts")
            for key in required:
                if key not in observation:
                    v.append(f"observation: required property '{key}' missing")
            _check_extra_keys(observation, set(required), "observation", v)
            if "classification" in observation and observation["classification"] not in CLASSIFICATION_ENUM:
                v.append(f"observation.classification: {observation['classification']!r} not in {sorted(CLASSIFICATION_ENUM)}")
            if "exit_code" in observation and not _is_int(observation["exit_code"]):
                v.append("observation.exit_code: must be an integer")
            if "anomaly_note" in observation and not (
                observation["anomaly_note"] is None or isinstance(observation["anomaly_note"], str)
            ):
                v.append("observation.anomaly_note: must be a string or null")
            artifacts = observation.get("artifacts")
            if artifacts is not None:
                if not isinstance(artifacts, list):
                    v.append("observation.artifacts: must be an array")
                else:
                    for i, a in enumerate(artifacts):
                        where = f"observation.artifacts[{i}]"
                        if not isinstance(a, dict):
                            v.append(f"{where}: not an object")
                            continue
                        for key in ("path", "status", "diff"):
                            if key not in a:
                                v.append(f"{where}: required property '{key}' missing")
                        _check_extra_keys(a, {"path", "status", "diff"}, where, v)
                        if "path" in a and not _is_str(a["path"], 1):
                            v.append(f"{where}.path: must be a non-empty string")
                        if "status" in a and a["status"] not in ARTIFACT_STATUS_ENUM:
                            v.append(f"{where}.status: {a['status']!r} not in {sorted(ARTIFACT_STATUS_ENUM)}")
                        if "diff" in a and not isinstance(a["diff"], str):
                            v.append(f"{where}.diff: must be a string")

    if "narration" in obj and not isinstance(obj["narration"], str):
        v.append("narration: must be a string")

    # The three allOf conditionals (the laundering cases the schema exists to stop).
    if isinstance(producer, dict) and "claim_strength" in obj:
        kind, claim = producer.get("kind"), obj["claim_strength"]
        if kind == "real-agent" and claim != "real-agent-observed":
            v.append("allOf: producer.kind 'real-agent' requires claim_strength 'real-agent-observed' (producer-bound claim)")
        if kind == "simulation" and claim != "simulation-derived":
            v.append("allOf: producer.kind 'simulation' requires claim_strength 'simulation-derived' (a simulation may not launder its output as observed)")
    if isinstance(run, dict) and run.get("status") in ("runner-error", "timeout") and "observation" in obj:
        v.append("allOf: a non-completed run (runner-error/timeout) MUST NOT carry an observation — nothing ran")

    return v


def main(argv):
    if len(argv) < 2:
        err("usage: validate_sidecar.py <sidecar.json> [...] (or '-' for stdin)")
        return 1
    vendor_selfcheck()

    exit_code = 0
    for arg in argv[1:]:
        if arg == "-":
            name, raw = "<stdin>", sys.stdin.read()
        else:
            path = Path(arg)
            if not path.is_file():
                err(f"file not found: {arg}")
                return 1
            name, raw = arg, path.read_text(encoding="utf-8")
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            err(f"{name}: not valid JSON ({e})")
            return 1
        violations = validate_obj(obj)
        if violations:
            for violation in violations:
                err(f"{name}: {violation}")
            print(f"FAIL {name}")
            exit_code = 2
        else:
            print(f"OK {name}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
