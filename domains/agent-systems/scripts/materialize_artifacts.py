#!/usr/bin/env python3
"""materialize_artifacts.py — narrated artifacts → real run dirs (serialize, never execute).

Usage:
    materialize_artifacts.py --native <sidecar.events.yaml> --batch <dir> --template <task-template-dir>

For each (rung × trial) segment: seed <batch>/runs/rung-R/trial-T/ from the
fixture's task-template (so protected_baseline files are diffable), then overlay
every artifact_declare's content VERBATIM (FR-11 bright line: bytes to files,
nothing interpreted, nothing run). content_sha256 is verified against the
declared content — a mismatch means the sidecar is internally inconsistent.

Artifact paths are containment-checked: they must resolve inside their run dir.

Exit codes: 0 ok / 1 input error / 2 violation (hash mismatch, path escape,
malformed segments).
"""

import hashlib
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from restricted_yaml import ParseError, parse_file  # noqa: E402


def err(msg):
    print(f"ERROR: [materialize_artifacts] {msg}", file=sys.stderr)


def main(argv):
    args = dict(zip(argv[1::2], argv[2::2]))
    native_path, batch_dir, template_dir = args.get("--native"), args.get("--batch"), args.get("--template")
    if not (native_path and batch_dir and template_dir) or len(argv) != 7:
        err("usage: materialize_artifacts.py --native <sidecar> --batch <dir> --template <task-template-dir>")
        return 1

    native_file = Path(native_path)
    template = Path(template_dir)
    if not native_file.is_file():
        err(f"native sidecar not found: {native_path}")
        return 1
    if not template.is_dir():
        err(f"task template not found: {template_dir}")
        return 1
    try:
        doc = parse_file(native_file)
    except ParseError as e:
        err(f"{native_path}: parse failure: {e}")
        return 1

    batch = Path(batch_dir)
    segments, current = [], None
    for ev in doc.get("events") or []:
        etype = ev.get("type")
        if etype == "rung_start":
            current = {"rung": ev.get("rung"), "trial": ev.get("trial"), "artifacts": []}
        elif etype == "artifact_declare" and current is not None:
            current["artifacts"].append(ev)
        elif etype == "trial_end" and current is not None:
            segments.append(current)
            current = None
    if not segments:
        err("no completed trial segments found")
        return 1

    materialized = 0
    for seg in segments:
        run_dir = batch / "runs" / f"rung-{seg['rung']}" / f"trial-{seg['trial']}"
        run_dir.mkdir(parents=True, exist_ok=True)
        # Seed from template (protected_baseline files must be diffable).
        for item in template.iterdir():
            if item.is_file():
                shutil.copy2(item, run_dir / item.name)
        # Overlay declared artifacts verbatim.
        for art in seg["artifacts"]:
            rel, content, declared = art.get("path"), art.get("content"), art.get("content_sha256")
            if not rel or content is None or not declared:
                err(f"artifact_declare missing path/content/content_sha256 (rung {seg['rung']} trial {seg['trial']})")
                return 2
            actual = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if actual != declared:
                err(
                    f"content_sha256 mismatch for {rel!r} (rung {seg['rung']} trial {seg['trial']}): "
                    f"declared {declared[:12]}…, actual {actual[:12]}… — sidecar internally inconsistent"
                )
                return 2
            target = (run_dir / rel)
            # Containment is against the artifact's OWN run dir — an artifact
            # reaching a sibling trial or sidecars/ would still be an escape.
            if not target.resolve().is_relative_to(run_dir.resolve()):
                err(f"artifact path escapes its run dir: {rel!r}")
                return 2
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            materialized += 1

    print(f"OK: {len(segments)} run dir(s) seeded from template, {materialized} artifact(s) materialized verbatim")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
