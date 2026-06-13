#!/usr/bin/env python3
"""normalize_sidecars.py — assembly-time v1.1 normalization for observed-trace sidecars.

Implements the two producer-side SHOULDs the v1.1 contract promotes from Arneson
conventions (observed-trace-batch.v1.md "Infrastructure failures + canonical triage
order" + "Producer provenance"):

  1. INFRA-MARKER → status mapping (canonical triage order, status FIRST):
     - run.status already runner-error / timeout / infra-failure  → untouched
     - else narration matches INFRA_MARKER                        → status=infra-failure,
                                                                      observation removed
       (the marker WINS over a producer-supplied observation — batch doc:126)
     This is stamping the producer's own triage convention into the record at the
     contract-sanctioned moment; it is NOT recomputing a grade (G-4 producer-never-judges).

  2. producer.provenance stamping: merge the 4 contract keys
     {agent_cmd_sha256, engine_git_sha, model_id, construct_sha} into producer.provenance.
     Existing identical value = no-op (idempotent); existing DIFFERENT value = exit 1
     loudly (a self-describing batch must never silently disagree with itself).

Usable as a module (assemble_batch.py imports normalize_obj) or a CLI over a batch's
sidecars/ directory. stdlib-only (NFR-5). Operates on the ASSEMBLED batch copy only —
never the source projected trace.

Exit codes: 0 ok / 1 input error or provenance conflict.
"""

import json
import re
import sys
from pathlib import Path

# Byte-equal to validate_batch.py:31 / sweep_report.py:32 / the vendored contract — the
# three sides MUST share one regex so they can never triage the same sidecar differently.
INFRA_MARKER = re.compile(r"ERROR: \[[A-Za-z0-9_-]*(?:agent|wrapper)\]")
PRESERVED_STATUSES = ("runner-error", "timeout", "infra-failure")
PROVENANCE_KEYS = ("agent_cmd_sha256", "engine_git_sha", "model_id", "construct_sha")


class NormalizeError(Exception):
    """A normalization invariant was violated (e.g. provenance conflict)."""


def err(msg):
    print(f"ERROR: [normalize_sidecars] {msg}", file=sys.stderr)


def _apply_marker_triage(obj):
    """Status-first INFRA_MARKER mapping. Returns True if the record was rewritten."""
    run = obj.get("run")
    if not isinstance(run, dict):
        return False
    if run.get("status") in PRESERVED_STATUSES:  # status is first in triage order
        return False
    narration = obj.get("narration")
    if isinstance(narration, str) and INFRA_MARKER.search(narration):
        run["status"] = "infra-failure"
        obj.pop("observation", None)  # marker wins over a producer-supplied observation
        return True
    return False


def _apply_provenance(obj, provenance):
    """Merge provenance keys into producer.provenance. Raises NormalizeError on conflict."""
    if not provenance:
        return False
    producer = obj.get("producer")
    if not isinstance(producer, dict):
        raise NormalizeError("cannot stamp provenance: sidecar has no producer object")
    existing = producer.get("provenance")
    if existing is None:
        existing = {}
    elif not isinstance(existing, dict):
        raise NormalizeError("producer.provenance present but not an object")
    changed = False
    for key, value in provenance.items():
        if key in existing:
            if existing[key] != value:
                raise NormalizeError(
                    f"producer.provenance.{key} already set to {existing[key]!r}, "
                    f"refusing to overwrite with {value!r} (self-describing batch must not disagree)"
                )
            continue
        existing[key] = value
        changed = True
    if changed:
        producer["provenance"] = existing
    return changed


def normalize_obj(obj, provenance=None):
    """Normalize one sidecar dict in place. Returns True if anything changed.

    provenance: optional dict of {contract_key: str_value} to stamp.
    Raises NormalizeError on a provenance conflict.
    """
    triaged = _apply_marker_triage(obj)
    stamped = _apply_provenance(obj, provenance or {})
    return triaged or stamped


def _parse_provenance_args(pairs):
    """`key=value` strings → dict, restricted to the 4 contract keys."""
    provenance = {}
    for pair in pairs:
        if "=" not in pair:
            raise NormalizeError(f"--provenance expects key=value, got {pair!r}")
        key, value = pair.split("=", 1)
        if key not in PROVENANCE_KEYS:
            raise NormalizeError(
                f"--provenance key {key!r} not a contract key {list(PROVENANCE_KEYS)}"
            )
        provenance[key] = value
    return provenance


def normalize_dir(sidecars_dir, provenance=None):
    """Normalize every *.json in a sidecars/ directory. Returns (changed, total)."""
    paths = sorted(p for p in sidecars_dir.glob("*.json"))
    changed = 0
    for path in paths:
        obj = json.loads(path.read_text(encoding="utf-8"))
        if normalize_obj(obj, provenance):
            path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
            changed += 1
    return changed, len(paths)


def main(argv):
    args = argv[1:]
    sidecars = None
    provenance_pairs = []
    i = 0
    while i < len(args):
        if args[i] == "--provenance" and i + 1 < len(args):
            provenance_pairs.append(args[i + 1])
            i += 2
        elif sidecars is None:
            sidecars = args[i]
            i += 1
        else:
            err(f"unexpected argument: {args[i]!r}")
            return 1
    if sidecars is None:
        err("usage: normalize_sidecars.py <sidecars-dir> [--provenance key=value ...]")
        return 1
    sidecars_dir = Path(sidecars)
    if not sidecars_dir.is_dir():
        err(f"sidecars dir not found: {sidecars}")
        return 1
    try:
        provenance = _parse_provenance_args(provenance_pairs)
        changed, total = normalize_dir(sidecars_dir, provenance)
    except NormalizeError as e:
        err(str(e))
        return 1
    except json.JSONDecodeError as e:
        err(f"sidecar is not valid JSON: {e}")
        return 1
    print(f"OK: normalized {sidecars_dir} ({changed}/{total} sidecar(s) rewritten)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
