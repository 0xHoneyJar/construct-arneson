"""triage_lib.py — shared sidecar triage (cycle-004, OQ-2).

The canonical triage order pinned by the observed-trace contract
(domain.conventions.md "Wrapper authors"), used byte-equal by BOTH
sweep_report.py (cross-config table) and gap_report.py (D1 outcome divergence).
Extracting it into one module is the only way to guarantee the two scripts can
never triage the same sidecar differently (sdd 4.1, R7). stdlib-only, no package.

Triage order (status-first):
  run.status (runner-error / timeout / infra-failure)
    -> narration INFRA_MARKER
      -> observation present (fixed | hacked | failed)
        -> ungraded (completed, no observation, no marker)

This module READS sidecars; it never grades, recomputes, or writes (NFR-4/FR-8).
"""

import re

# Same convention as validate_batch.py's triage (domain.conventions.md "Wrapper authors").
INFRA_MARKER = re.compile(r"ERROR: \[[A-Za-z0-9_-]*(?:agent|wrapper)\]")


def sidecar_paths(batch_dir):
    """Sidecar JSONs for a batch: the sidecars/ child if present, else flat (minus batch.json)."""
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
