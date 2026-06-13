#!/usr/bin/env python3
"""sweep_report.py — cross-config triaged comparison table (FR-1, Sprint 2).

Usage:
    sweep_report.py --config <label>=<batch-dir> [--config <label>=<batch-dir> ...]

Arranges N already-graded batches (one per config — a model, a scenario, a
difficulty) into ONE deterministic triaged table. It COUNTS what Gygax's scorer
already wrote into each sidecar's `observation`; it NEVER recomputes a grade, a
ratio, or a cliff (NFR-6, the producer-never-judges trust rule). Per-config cliff
/ within-noise INTERPRETATION stays in Gygax's own per-config report — this table
links to it, never reproduces it (the trace CLI is Markdown-only; see
discovery/gygax-trace-json-brief.md).

Each run is triaged into exactly one class, fully from the sidecar:
  - VERDICT      : has observation -> carry classification (fixed/hacked/failed)
  - INFRA NON-RUN: narration carries a wrapper infra marker, OR run.status is
                   runner-error/timeout -> excluded from verdict counts
  - UNGRADED     : completed, no observation, not infra (e.g. ungraded simulation)

stdout: the table. Exit 0 on success / 1 on input error. Deterministic: stable
config-then-rung ordering, no clock, no randomness.
"""

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

# Same convention as validate_batch.py's triage (domain.conventions.md "Wrapper authors").
INFRA_MARKER = re.compile(r"ERROR: \[[A-Za-z0-9_-]*(?:agent|wrapper)\]")
RUNG_NAMES = {0: "blind", 1: "reward-aware", 2: "adversarial"}


def err(msg):
    print(f"ERROR: [sweep_report] {msg}", file=sys.stderr)


def _sidecar_paths(batch_dir):
    sub = batch_dir / "sidecars"
    if sub.is_dir():
        return sorted(sub.glob("*.json"))
    return sorted(p for p in batch_dir.glob("*.json") if p.name != "batch.json")


def triage(obj):
    """Return ('verdict', classification) | ('infra', None) | ('ungraded', None)."""
    run = obj.get("run") if isinstance(obj, dict) else None
    status = run.get("status") if isinstance(run, dict) else None
    narration = obj.get("narration") if isinstance(obj, dict) else None

    if status in ("runner-error", "timeout", "infra-failure"):
        return ("infra", None)
    if isinstance(narration, str) and INFRA_MARKER.search(narration):
        return ("infra", None)
    obs = obj.get("observation") if isinstance(obj, dict) else None
    if isinstance(obs, dict) and obs.get("classification"):
        return ("verdict", obs["classification"])
    return ("ungraded", None)


def tally_config(batch_dir):
    """Per-rung tallies for one config. Counts only; carries nothing it didn't read."""
    rungs = OrderedDict()
    for path in _sidecar_paths(batch_dir):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        run = obj.get("run") if isinstance(obj, dict) else {}
        rung = run.get("rung") if isinstance(run, dict) else None
        key = rung if isinstance(rung, int) else -1
        cell = rungs.setdefault(key, {"fixed": 0, "hacked": 0, "failed": 0,
                                      "infra": 0, "ungraded": 0})
        cls, classification = triage(obj)
        if cls == "verdict":
            cell[classification] = cell.get(classification, 0) + 1
        else:
            cell[cls] += 1
    return rungs


def render(configs):
    lines = []
    lines.append("# Cross-config sweep — triaged comparison")
    lines.append("")
    lines.append("Counts are Gygax's gradings, tallied — never recomputed. Per-config cliff /")
    lines.append("within-noise interpretation lives in each config's own `trace --regrade` report.")
    lines.append("")
    lines.append("Legend: fixed/hacked/failed = graded verdicts · infra = non-run (excluded) · "
                 "ungraded = ran, not scored")
    lines.append("")
    header = f"| {'config':<24} | rung | fixed | hacked | failed | infra | ungraded |"
    sep = "|" + "-" * 26 + "|------|-------|--------|--------|-------|----------|"
    lines.append(header)
    lines.append(sep)
    for label in configs:  # insertion order = CLI order (deterministic)
        rungs = configs[label]
        for rung in sorted(k for k in rungs if k >= 0):
            c = rungs[rung]
            name = RUNG_NAMES.get(rung, f"rung-{rung}")
            lines.append(
                f"| {label:<24} | {rung} {name[:4]:<4} | {c['fixed']:^5} | {c['hacked']:^6} | "
                f"{c['failed']:^6} | {c['infra']:^5} | {c['ungraded']:^8} |"
            )
        if any(k < 0 for k in rungs):  # sidecars with no rung (shouldn't happen for valid batches)
            c = rungs[-1]
            lines.append(f"| {label:<24} | ?    | {c['fixed']:^5} | {c['hacked']:^6} | "
                         f"{c['failed']:^6} | {c['infra']:^5} | {c['ungraded']:^8} |")
    return "\n".join(lines)


def main(argv):
    pairs = []
    args = list(argv[1:])
    i = 0
    while i < len(args):
        if args[i] == "--config":
            try:
                spec = args[i + 1]
            except IndexError:
                err("--config requires <label>=<batch-dir>")
                return 1
            if "=" not in spec:
                err(f"--config must be <label>=<batch-dir>, got {spec!r}")
                return 1
            label, batch = spec.split("=", 1)
            pairs.append((label.strip(), Path(batch.strip())))
            i += 2
        else:
            err(f"unexpected argument: {args[i]!r}")
            return 1
    if not pairs:
        err("usage: sweep_report.py --config <label>=<batch-dir> [...]")
        return 1

    configs = OrderedDict()
    for label, batch in pairs:
        if not batch.is_dir():
            err(f"batch dir not found for config {label!r}: {batch}")
            return 1
        configs[label] = tally_config(batch)

    print(render(configs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
