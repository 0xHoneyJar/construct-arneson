#!/usr/bin/env python3
"""discover_engine.py — locate the Gygax ladder engine (FR-6; sdd.md 1.6).

Usage:
    discover_engine.py [--engine <path>]

Resolution order (first valid wins):
    1. --engine <path>           (explicit flag)
    2. $ARNESON_GYGAX_ROOT       (environment override)
    3. <repo-root>/../construct-gygax   (sibling checkout probe — same pattern
       as the grimoires/gygax/game-state composition probe)

A candidate is valid iff <root>/scripts/lib/ladder/index.ts exists. On success
the resolved engine root is printed to stdout (single line). On failure: exit 1
with the FR-6 message — immediate, named dependency, simulated-mode pointer.
No retries, no fallbacks to partial installs.
"""

import os
import sys
from pathlib import Path

ENGINE_MARKER = Path("scripts") / "lib" / "ladder" / "index.ts"
FR6_MESSAGE = (
    "MISSING DEPENDENCY: construct-gygax engine not found "
    "(probed {probed}). Real mode needs it. "
    "Simulated mode works standalone: /playout --scenario <s>"
)


def repo_root():
    # domains/agent-systems/scripts/ -> repo root is three levels up.
    return Path(__file__).resolve().parent.parent.parent.parent


def candidates(flag_value):
    if flag_value:
        yield "--engine flag", Path(flag_value)
        return  # explicit flag is authoritative: do not silently fall through
    env = os.environ.get("ARNESON_GYGAX_ROOT")
    if env:
        yield "$ARNESON_GYGAX_ROOT", Path(env)
        return  # explicit override is authoritative too
    yield "sibling ../construct-gygax", repo_root().parent / "construct-gygax"


def main(argv):
    flag_value = None
    args = list(argv[1:])
    if "--engine" in args:
        i = args.index("--engine")
        try:
            flag_value = args[i + 1]
        except IndexError:
            print("ERROR: [discover_engine] --engine requires a path", file=sys.stderr)
            return 1
        del args[i:i + 2]
    if args:
        print(f"ERROR: [discover_engine] unexpected arguments: {args}", file=sys.stderr)
        return 1

    probed = []
    for label, root in candidates(flag_value):
        root = root.expanduser()
        probed.append(f"{label}={root}")
        if (root / ENGINE_MARKER).is_file():
            print(root.resolve())
            return 0

    print("ERROR: [discover_engine] " + FR6_MESSAGE.format(probed=", ".join(probed)),
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
