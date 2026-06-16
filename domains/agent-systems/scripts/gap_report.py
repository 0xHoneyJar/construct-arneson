#!/usr/bin/env python3
"""gap_report.py — simulated-vs-real divergence report (cycle-004).

Usage:
    gap_report.py --sim <playout-summary.json> --real <real-playout.yaml>
                  [--move-map <move-map.yaml>] [--out-dir <dir>]

Pairs a simulated playout summary (playout-summary/v1, ungraded behavioral
exploration) with its real graded batch (observed-trace/v1) and tabulates where
the two diverge. It shows where forecast and observation diverge — it does NOT
judge fidelity.

TRUST RULE (domain.conventions.md G-4, load-bearing):
  - Arithmetic only. D1 COUNTS the verdicts Gygax's scorer already wrote into each
    sidecar's `observation`; it never recomputes a grade, a severity, or a cliff.
  - Read-only. Never writes to / regrades the real batch (FR-8). No subprocess to
    the grader or ladder engine. No import from construct-gygax (NFR-2).
  - Honest labels. producer.kind / claim_strength are quoted verbatim, never
    paraphrased upward (G-4 §2).
  Interpretation — cliffs, severity, correctness — belongs to the analyst's report.

stdout: the path to the written report (success).
stderr: ERROR: [gap_report] ... on any failure.
exit:   0 success · 1 input/usage error · 2 pairing refusal (scenario_sha256 mismatch).
Deterministic: stable row/set ordering, no clock in the report body (the timestamp
lives in the filename only) — so the synthetic golden is byte-stable (NFR-6).
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from restricted_yaml import ParseError, parse as parse_yaml  # noqa: E402
from triage_lib import sidecar_paths, triage  # noqa: E402  (shared triage, OQ-2)

# Real-lane verdict classes — from observation.classification (closed enum) + triage.
VERDICT_CLASSES = ("fixed", "hacked", "failed", "infra", "ungraded")
# Sim-lane outcome signals — closed set for playout-summary/v1 (sdd 3.5).
OUTCOME_SIGNAL = ("task-declared-done", "max-turns", "gave-up", "safety-stop")


def err(msg):
    print(f"ERROR: [gap_report] {msg}", file=sys.stderr)


class InputError(Exception):
    pass


class PairingRefusal(Exception):
    pass


# ---- args -------------------------------------------------------------------

def parse_args(argv):
    sim = real = move_map = out_dir = None
    args = list(argv[1:])
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--sim":
            sim = _val(args, i)
        elif a == "--real":
            real = _val(args, i)
        elif a == "--move-map":
            move_map = _val(args, i)
        elif a == "--out-dir":
            out_dir = _val(args, i)
        else:
            raise InputError(
                f"usage: gap_report.py --sim <playout-summary.json> --real <real-playout.yaml> "
                f"[--move-map <m>] [--out-dir <d>] (got {a!r})"
            )
        i += 2
    if not sim or not real:
        raise InputError("usage: gap_report.py --sim <playout-summary.json> --real <real-playout.yaml>")
    return sim, real, move_map, out_dir


def _val(args, i):
    try:
        return args[i + 1]
    except IndexError:
        raise InputError(f"{args[i]} requires a value")


# ---- loaders ----------------------------------------------------------------

def load_sim(path):
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f"cannot read sim summary {path}: {e}")
    if not isinstance(obj, dict) or obj.get("schema") != "playout-summary/v1":
        raise InputError(f"sim summary {path} is not playout-summary/v1")
    if obj.get("lane") != "simulated":
        raise InputError(f"sim summary {path} lane is not 'simulated'")
    return obj


def load_real(path):
    try:
        rec = parse_yaml(Path(path).read_text(encoding="utf-8"))
    except (OSError, ParseError) as e:
        raise InputError(f"cannot read real record {path}: {e}")
    if not isinstance(rec, dict) or rec.get("lane") != "real":
        raise InputError(f"real record {path} lane is not 'real'")
    if rec.get("validation") == "non-conformant":
        raise InputError(f"real batch records validation: non-conformant ({path}); declining (read-only, no regrade)")
    batch_path = rec.get("batch_path")
    if not batch_path:
        raise InputError(f"real record {path} has no batch_path")
    batch_dir = (Path(path).resolve().parent / batch_path).resolve()
    if not batch_dir.is_dir():
        raise InputError(f"batch_path not found on disk: {batch_dir}")
    return rec, batch_dir


def assert_paired(sim, real_rec):
    a, b = sim.get("scenario_sha256"), real_rec.get("scenario_sha256")
    if a != b:
        raise PairingRefusal(f"scenario_sha256 mismatch: sim={a} real={b}")


def load_move_map(explicit, sim_path, real_path, scenario_id):
    """Explicit --move-map wins; else discover move-map.yaml beside --sim then --real,
    accepting it only if its scenario_id matches (one-variable convention, OQ-5).
    No map found -> empty map (every sim label stays raw; honest 'unconfirmed' fallback)."""
    if explicit:
        mm = _read_move_map(explicit)
        return mm
    for base in (sim_path, real_path):
        cand = Path(base).resolve().parent / "move-map.yaml"
        if cand.is_file():
            mm = _read_move_map(str(cand))
            if mm.get("scenario_id") == scenario_id:
                return mm
    return {"schema": "move-map/v1", "scenario_id": scenario_id, "entries": []}


def _read_move_map(path):
    try:
        mm = parse_yaml(Path(path).read_text(encoding="utf-8"))
    except (OSError, ParseError) as e:
        raise InputError(f"cannot read move-map {path}: {e}")
    if not isinstance(mm, dict) or mm.get("schema") != "move-map/v1":
        raise InputError(f"move-map {path} is not move-map/v1")
    return mm


def load_sidecars(batch_dir):
    out = []
    for p in sidecar_paths(batch_dir):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue  # tolerate a single bad sidecar; mirrors sweep_report
    return out


# ---- D1 / D2 ----------------------------------------------------------------

def outcome_divergence(sim, sidecars):
    """D1: real verdict-class counts (tallied, never recomputed) + sim outcome tags."""
    real = {k: 0 for k in VERDICT_CLASSES}
    for obj in sidecars:
        cls, classification = triage(obj)
        if cls == "verdict":
            real[classification] = real.get(classification, 0) + 1
        else:
            real[cls] += 1
    sim_tags = {}
    for t in sim.get("trials", []):
        sig = t.get("outcome_signal")
        sim_tags[sig] = sim_tags.get(sig, 0) + 1
    return real, sim_tags


def action_divergence(sim, sidecars, move_map):
    """D2: shared / sim-only / real-only action-label sets (sdd 3.3 algorithm)."""
    label_to_canon = {}
    for e in move_map.get("entries", []):
        for sl in e.get("sim_labels", []):
            label_to_canon[sl] = e.get("canonical")
    sim_set = set()
    for t in sim.get("trials", []):
        for lbl in t.get("action_labels", []):
            sim_set.add(label_to_canon.get(lbl, lbl))  # canonical if mapped, else raw
    real_set = set()
    for e in move_map.get("entries", []):
        if _evidence_matches(e.get("real_evidence") or {}, sidecars):
            real_set.add(e.get("canonical"))
    return sorted(sim_set & real_set), sorted(sim_set - real_set), sorted(real_set - sim_set)


def _evidence_matches(ev, sidecars):
    """Declarative recognizer over graded sidecars (read-only). Never grades."""
    for obj in sidecars:
        obs = obj.get("observation") if isinstance(obj, dict) else None
        if not isinstance(obs, dict):
            continue
        if ev.get("anomaly_note_present"):
            note = obs.get("anomaly_note")
            if isinstance(note, str) and note.strip():
                return True
        want_path = ev.get("artifact_path")
        if want_path:
            want_status = ev.get("artifact_status")
            for art in obs.get("artifacts") or []:
                if isinstance(art, dict) and art.get("path") == want_path:
                    if want_status is None or art.get("status") == want_status:
                        return True
    return False


def provenance(sim, real_rec, sidecars):
    prod = sim.get("producer") or {}
    return {
        "scenario_id": sim.get("scenario_id"),
        "scenario_sha256": sim.get("scenario_sha256"),
        "producer_kind": prod.get("kind"),
        "claim_strength": prod.get("claim_strength"),
        "batch_path": real_rec.get("batch_path"),
        "engine_git_sha": real_rec.get("engine_git_sha"),
        "validation": real_rec.get("validation") or "unknown",
        "sim_trials": len(sim.get("trials", [])),
        "real_runs": len(sidecars),
    }


# ---- render -----------------------------------------------------------------

def render(prov, d1, d2):
    real, sim_tags = d1
    shared, sim_only, real_only = d2
    L = [f"# Simulation Fidelity Gap Report — {prov['scenario_id']}", ""]
    L += ["## Provenance",
          f"- scenario_id: {prov['scenario_id']}",
          f"- scenario_sha256: {prov['scenario_sha256']}",
          f'- sim producer.kind: "{prov["producer_kind"]}"',
          f'- sim claim_strength: "{prov["claim_strength"]}"',
          f"- real batch: {prov['batch_path']}",
          f"- engine_git_sha: {prov['engine_git_sha']}",
          f"- real validation: {prov['validation']}",
          f"- runs: sim {prov['sim_trials']} trials, real {prov['real_runs']} runs",
          ""]
    L += ["## D1 — Outcome divergence",
          "| outcome class | real (count) | sim (count) |",
          "|---|---|---|"]
    for k in VERDICT_CLASSES:
        L.append(f"| {k} | {real[k]} | — |")
    for sig in OUTCOME_SIGNAL:
        if sim_tags.get(sig):
            L.append(f"| {sig} | — | {sim_tags[sig]} |")
    L += ["",
          "Counts only. Real verdict labels are Gygax's gradings, tallied — never recomputed.",
          ""]
    L += ["## D2 — Action-set divergence",
          f"- shared ({len(shared)}): [{', '.join(shared)}]",
          f"- sim-only ({len(sim_only)}): [{', '.join(sim_only)}]",
          f"- real-only ({len(real_only)}): [{', '.join(real_only)}]",
          ""]
    L += ["## Framing",
          "Simulated = behavioral exploration; real = proof. This report shows where forecast "
          "and observation diverge; it does not judge fidelity. Interpretation — cliffs, "
          "severity, correctness — belongs to the analyst's report."]
    return "\n".join(L) + "\n"


def write_report(scenario_id, md, out_dir):
    base = Path(out_dir) if out_dir else Path("grimoires/arneson/playouts/gap-reports")
    base.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = base / f"{scenario_id}-{ts}.md"
    path.write_text(md, encoding="utf-8")
    return path


def main(argv):
    try:
        sim_path, real_path, mm_path, out_dir = parse_args(argv)
        sim = load_sim(sim_path)
        real_rec, batch_dir = load_real(real_path)
        assert_paired(sim, real_rec)
        move_map = load_move_map(mm_path, sim_path, real_path, sim.get("scenario_id"))
        sidecars = load_sidecars(batch_dir)
        d1 = outcome_divergence(sim, sidecars)
        d2 = action_divergence(sim, sidecars, move_map)
        prov = provenance(sim, real_rec, sidecars)
        md = render(prov, d1, d2)
        path = write_report(sim.get("scenario_id"), md, out_dir)
    except PairingRefusal as e:
        err(str(e))
        return 2
    except InputError as e:
        err(str(e))
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
