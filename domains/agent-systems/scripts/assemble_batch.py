#!/usr/bin/env python3
"""assemble_batch.py — projected sidecars + materialized runs → observed-trace-batch/v1.

Usage:
    assemble_batch.py --scenario <s.yaml> --traces <dir> --runs <dir> --out <batch-dir>

Writes batch.json (schema + fixture, per the vendored batch contract), copies
projected sidecars into <out>/sidecars/, and copies the materialized runs/ tree
into <out>/runs/. The result is exactly the layout validate_batch.py gates and
Gygax's grader reads.

Exit codes: 0 ok / 1 input error.
"""

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from restricted_yaml import ParseError, parse_file  # noqa: E402
from normalize_sidecars import NormalizeError, _parse_provenance_args, normalize_dir  # noqa: E402


def err(msg):
    print(f"ERROR: [assemble_batch] {msg}", file=sys.stderr)


def main(argv):
    # Required args are positional pairs; optional --provenance key=value flags may
    # repeat. Pull the provenance flags out first, then parse the rest as before.
    rest, provenance_pairs = [], []
    i = 1
    while i < len(argv):
        if argv[i] == "--provenance" and i + 1 < len(argv):
            provenance_pairs.append(argv[i + 1])
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    args = dict(zip(rest[0::2], rest[1::2]))
    needed = ("--scenario", "--traces", "--runs", "--out")
    if any(k not in args for k in needed) or len(rest) != 8:
        err("usage: assemble_batch.py --scenario <s.yaml> --traces <dir> --runs <dir> "
            "--out <batch-dir> [--provenance key=value ...]")
        return 1

    scenario_file = Path(args["--scenario"])
    traces = Path(args["--traces"])
    runs = Path(args["--runs"])
    out = Path(args["--out"])

    if not scenario_file.is_file():
        err(f"scenario not found: {scenario_file}")
        return 1
    if not traces.is_dir() or not sorted(traces.glob("*.json")):
        err(f"no projected sidecars in: {traces}")
        return 1
    if not runs.is_dir():
        err(f"runs dir not found: {runs}")
        return 1
    try:
        scenario = parse_file(scenario_file)
    except ParseError as e:
        err(f"{scenario_file}: parse failure: {e}")
        return 1
    fixture_rel = (scenario.get("fixture") or {}).get("path")
    if not fixture_rel:
        err("scenario missing fixture.path")
        return 1
    fixture_abs = str((scenario_file.resolve().parent / fixture_rel).resolve())

    try:
        provenance = _parse_provenance_args(provenance_pairs)
    except NormalizeError as e:
        err(str(e))
        return 1

    out.mkdir(parents=True, exist_ok=True)
    (out / "sidecars").mkdir(exist_ok=True)
    for sc in sorted(traces.glob("*.json")):
        shutil.copy2(sc, out / "sidecars" / sc.name)
    if (out / "runs").exists():
        shutil.rmtree(out / "runs")
    shutil.copytree(runs, out / "runs")

    # v1.1 assembly-time normalization on the ASSEMBLED copy only (never the source
    # projected trace): INFRA_MARKER → infra-failure (status-first triage) + provenance
    # stamping. See normalize_sidecars.py.
    try:
        normalize_dir(out / "sidecars", provenance)
    except NormalizeError as e:
        err(str(e))
        return 1

    manifest = {"schema": "observed-trace-batch/v1", "fixture": fixture_abs}
    (out / "batch.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    n = len(list((out / "sidecars").glob("*.json")))
    print(f"OK: batch assembled at {out} ({n} sidecar(s), fixture {fixture_abs})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
