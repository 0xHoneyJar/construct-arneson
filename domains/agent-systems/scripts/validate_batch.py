#!/usr/bin/env python3
"""validate_batch.py — layout validator for observed-trace-batch/v1 directories.

Usage:
    validate_batch.py <batch-dir>

Checks the on-disk batch contract (vendored observed-trace-batch.v1.md):
batch.json fields, sidecar presence, per-sidecar conformance (delegated to
validate_sidecar.validate_obj), and run_dir containment — every run.run_dir
must resolve INSIDE the batch directory.

Honesty note (not a failure): a completed simulation sidecar without an
observation is layout-valid but not Gygax-ingestible until scored — Gygax
rejects ungraded simulation records rather than fabricate a grade. We WARN.

Exit codes: 0 conformant / 1 input error / 2 contract violation or vendor drift.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_sidecar  # noqa: E402  (sibling module, same toolchain)

# Infrastructure-marker CONVENTION (bug 20260610-5ad67a): bundled/operator wrappers
# emit stderr errors prefixed "ERROR: [<tool>]" where <tool> ends in -agent or
# -wrapper (see domain.conventions.md "Wrapper authors"). Anchored to the convention
# so arbitrary agent-printed "ERROR: [x]" prose never false-positives.
INFRA_MARKER = re.compile(r"ERROR: \[[A-Za-z0-9_-]*(?:agent|wrapper)\]")


def err(msg):
    print(f"ERROR: [validate_batch] {msg}", file=sys.stderr)


def warn(msg):
    print(f"WARNING: [validate_batch] {msg}", file=sys.stderr)


def main(argv):
    if len(argv) != 2:
        err("usage: validate_batch.py <batch-dir>")
        return 1
    validate_sidecar.vendor_selfcheck()

    batch_dir = Path(argv[1])
    if not batch_dir.is_dir():
        err(f"batch dir not found: {argv[1]}")
        return 1
    batch_root = batch_dir.resolve()

    violations = []

    # batch.json — REQUIRED for grade-on-ingest.
    batch_json_path = batch_dir / "batch.json"
    if not batch_json_path.is_file():
        err("batch.json missing — REQUIRED for grade-on-ingest (observed-trace-batch.v1.md)")
        return 2
    try:
        manifest = json.loads(batch_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"batch.json: not valid JSON ({e})")
        return 1
    if not isinstance(manifest, dict):
        violations.append("batch.json: not a JSON object")
        manifest = {}
    if manifest.get("schema") != "observed-trace-batch/v1":
        violations.append(
            f"batch.json schema: must be 'observed-trace-batch/v1', got {manifest.get('schema')!r}"
        )
    if "reward_command" in manifest:
        rc = manifest["reward_command"]
        if not (isinstance(rc, list) and rc and all(isinstance(x, str) for x in rc)):
            violations.append("batch.json reward_command: must be a non-empty argv array of strings")

    # Sidecars: sidecars/*.json, or *.json in the batch dir directly (contract allows both).
    sidecars_dir = batch_dir / "sidecars"
    if sidecars_dir.is_dir():
        sidecar_paths = sorted(sidecars_dir.glob("*.json"))
    else:
        sidecar_paths = sorted(p for p in batch_dir.glob("*.json") if p.name != "batch.json")
    if not sidecar_paths:
        violations.append("no sidecar *.json files found (sidecars/ or batch dir)")

    fixture_in_manifest = isinstance(manifest.get("fixture"), str) and manifest.get("fixture")
    all_sidecars_carry_fixture = True

    for path in sidecar_paths:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err(f"{path}: not valid JSON ({e})")
            return 1
        for violation in validate_sidecar.validate_obj(obj):
            violations.append(f"{path.name}: {violation}")

        if not (isinstance(obj, dict) and isinstance(obj.get("experiment"), dict)
                and obj["experiment"].get("fixture")):
            all_sidecars_carry_fixture = False

        run = obj.get("run") if isinstance(obj, dict) else None
        if isinstance(run, dict) and isinstance(run.get("run_dir"), str) and run["run_dir"]:
            resolved = (batch_dir / run["run_dir"]).resolve()
            if not resolved.is_relative_to(batch_root):
                violations.append(
                    f"{path.name}: run.run_dir {run['run_dir']!r} escapes the batch directory "
                    "(must resolve inside <batch-dir>)"
                )
            elif not resolved.is_dir():
                violations.append(
                    f"{path.name}: run.run_dir {run['run_dir']!r} does not exist under the batch directory"
                )

        # Honesty warning, not a violation (sdd.md 5.2.3 item 4).
        if (isinstance(obj, dict)
                and isinstance(obj.get("producer"), dict)
                and obj["producer"].get("kind") == "simulation"
                and isinstance(run, dict) and run.get("status") == "completed"
                and "observation" not in obj):
            warn(
                f"{path.name}: completed simulation sidecar is ungraded — not Gygax-ingestible "
                "until scored (run: ladder score --batch <dir>)"
            )

        # Infrastructure triage (warn-not-reject; bugs 20260610-594345 + -5ad67a):
        # when the narration carries a CONVENTION-conforming wrapper error marker,
        # no agent ever acted — grading it would poison any comparison drawn from
        # this batch. Matching the marker convention is stamping, not judging
        # (G-4 posture). Emitters: ollama-agent.py err() and any wrapper following
        # domain.conventions.md "Wrapper authors"; co-tested in test-validate-batch.sh.
        if (isinstance(obj, dict)
                and isinstance(obj.get("narration"), str)
                and INFRA_MARKER.search(obj["narration"])):
            warn(
                f"{path.name}: narration carries a wrapper infrastructure error marker — "
                "this is a non-run, not a verdict; exclude it from comparisons and re-run "
                "(check timeouts/memory: see discovery/sweep-observability-findings.md)"
            )

    if not fixture_in_manifest and not all_sidecars_carry_fixture:
        violations.append(
            "batch.json fixture missing AND not every sidecar carries experiment.fixture — "
            "the grader cannot resolve the task template"
        )

    if violations:
        for violation in violations:
            err(violation)
        print(f"FAIL {batch_dir} ({len(violations)} violation(s))")
        return 2
    print(f"OK {batch_dir} ({len(sidecar_paths)} sidecar(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
