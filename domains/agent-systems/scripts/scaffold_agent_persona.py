#!/usr/bin/env python3
"""scaffold_agent_persona.py — bootstrap a schema-valid agent-persona skeleton (cycle-005).

Usage:
    scaffold_agent_persona.py --from-voice <npc-id> [--out <path>]
    scaffold_agent_persona.py --blank --id <persona-id> [--out <path>]

Bridges a /voice output (voice-character YAML at
grimoires/arneson/voices/npcs/<id>.yaml) into a RUNNABLE agent-persona skeleton
(default: domains/agent-systems/resources/personas/<id>.yaml), so authoring starts
from a valid file instead of a blank schema.

It SCAFFOLDS, it does NOT auto-convert. The disposition is a DRAFT seeded from the
voice's personality prose; capabilities / knowledge / rung_overlays are guided TODO
stubs the human must author. Dialogue is not task-behavior — "you don't workshop an
agent's voice" (agent-persona.schema.yaml). It is NOT wired to the gap report (no
auto-optimization against divergence). The human stays the author. stdlib only.

Self-checks its own output (parse-back + required-field assert); never ships a broken
skeleton. Deterministic: stable field order, no clock.

stdout: the path written. stderr: ERROR: [scaffold_agent_persona] ...
exit:   0 ok · 1 input/usage error · 2 self-check failed.
"""

import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from restricted_yaml import ParseError, parse as parse_yaml  # noqa: E402

ID_RE = re.compile(r"^[a-z0-9-]+$")
VOICE_DIR = "grimoires/arneson/voices/npcs"
PERSONA_DIR = "domains/agent-systems/resources/personas"


def err(msg):
    print(f"ERROR: [scaffold_agent_persona] {msg}", file=sys.stderr)


class InputError(Exception):
    pass


class SelfCheckError(Exception):
    pass


# ---- args -------------------------------------------------------------------

def parse_args(argv):
    from_voice = persona_id = out = None
    blank = False
    args = list(argv[1:])
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--from-voice":
            from_voice = _val(args, i)
            i += 2
        elif a == "--blank":
            blank = True
            i += 1
        elif a == "--id":
            persona_id = _val(args, i)
            i += 2
        elif a == "--out":
            out = _val(args, i)
            i += 2
        else:
            raise InputError(f"unexpected argument: {a!r}")
    if from_voice and blank:
        raise InputError("--from-voice and --blank are mutually exclusive")
    if not from_voice and not blank:
        raise InputError(
            "usage: scaffold_agent_persona.py --from-voice <npc-id> | "
            "--blank --id <persona-id> [--out <path>]"
        )
    if blank and not persona_id:
        raise InputError("--blank requires --id <persona-id>")
    pid = persona_id or from_voice
    if not ID_RE.match(pid or "") or ".." in (pid or ""):
        raise InputError(f"id must match ^[a-z0-9-]+$ (got {pid!r})")
    return from_voice, pid, out


def _val(args, i):
    try:
        return args[i + 1]
    except IndexError:
        raise InputError(f"{args[i]} requires a value")


# ---- voice read + disposition seeding --------------------------------------

def load_voice(npc_id):
    path = os.path.join(VOICE_DIR, f"{npc_id}.yaml")
    try:
        raw = open(path, encoding="utf-8").read()
    except OSError:
        raise InputError(f"voice not found: {path}")
    try:
        doc = parse_yaml(raw)
    except ParseError as e:
        raise InputError(f"voice is not valid YAML ({path}): {e}")
    if not isinstance(doc, dict):
        raise InputError(f"voice {path} is not a mapping")
    sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return doc, path, sha


def seed_disposition(voice):
    """A DRAFT prose disposition seeded from the voice's personality signal.
    Descriptive, marked edit-me. Never instructions; never fabricated task behavior."""
    name = voice.get("display_name") or voice.get("voice_id") or "this character"
    er = voice.get("emotional_register")
    er = er if isinstance(er, dict) else {}
    sp = voice.get("speech_patterns")
    sp = sp if isinstance(sp, dict) else {}
    baseline = er.get("baseline") or "unspecified"
    length = sp.get("sentence_length") or "unspecified"
    register = sp.get("vocabulary_register") or "unspecified"
    return (
        f"DRAFT seeded from voice {name} (edit me before running). Voice signal: "
        f"{baseline} baseline; {length} / {register} register. This describes how the "
        f"character TALKS, not how an agent ACTS on a task. Re-author this as task "
        f"disposition: how does this temperament approach a coding task under "
        f"incentives (does it rush, cut corners, resist process, chase the risky "
        f"move)? Replace this draft."
    )


BLANK_DISPOSITION = (
    "DRAFT (edit me before running). Describe how this agent approaches tasks and "
    "incentives: does it diagnose before editing, make the minimal fix, seek "
    "loopholes, resist process? Descriptive grounding, never instructions to the host."
)

# Honest provenance marker for voice-sourced personas. A fictional character voice
# has no real-agent counterpart, so a persona scaffolded from it is exploration-only
# and must never be laundered into a fidelity / gap-report claim (source.kind ==
# character-voice carries the same fact machine-readably).
EXPLORATION_HEADER = (
    "# EXPLORATION persona — scaffolded from character voice {voice!r}.\n"
    "# Behavioral exploration ONLY: not grounded in a real agent, no real-lane\n"
    "# counterpart, NOT eligible for fidelity / gap-report claims. source.kind:\n"
    "# character-voice marks this. For a fidelity-grade persona, ground source in a\n"
    "# real agent's spec (docs/importing-an-agent.md) and use behavioral-spec."
)


# ---- YAML emission (hand-built for deterministic field order) ---------------

def _fold(text, indent="  "):
    """Emit `text` as a YAML folded (>) block body: wrapped, indented lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > 86:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "\n".join(f"{indent}{ln}" for ln in lines)


def render(persona_id, source_ref, source_sha, source_kind, disposition, header=""):
    cap_stub = "TODO: what this agent would DO on a task (narrated, never executed)"
    knows_stub = "TODO: what this agent knows (prompt + working dir, general practice)"
    nknows_stub = "TODO: what it does NOT know (grader internals, that it is observed)"
    overlay = {
        "blind": "TODO: what the agent knows at the blind rung (task + working dir only).",
        "reward-aware": "TODO: add what changes when it knows the reward command.",
        "adversarial": "TODO: add the adversarial framing (only the reward outcome is measured).",
    }
    lines = []
    if header:
        lines.append(header.rstrip("\n"))
    lines += [
        f"persona_id: {persona_id}",
        "source:",
        f"  ref: {source_ref}",
        f"  sha256: {source_sha}",
        f"  kind: {source_kind}",
        "disposition: >",
        _fold(disposition),
        "capabilities:",
        f'  - "{cap_stub}"',
        "knowledge:",
        "  knows:",
        f'    - "{knows_stub}"',
        "  does_not_know:",
        f'    - "{nknows_stub}"',
        "rung_overlays:",
        "  blind: >",
        _fold(overlay["blind"], "    "),
        "  reward-aware: >",
        _fold(overlay["reward-aware"], "    "),
        "  adversarial: >",
        _fold(overlay["adversarial"], "    "),
    ]
    return "\n".join(lines) + "\n"


# ---- self-check -------------------------------------------------------------

REQUIRED = ("persona_id", "source", "disposition", "capabilities", "knowledge", "rung_overlays")


def self_check(text):
    """Parse the emitted YAML back and assert the agent-persona contract holds."""
    try:
        doc = parse_yaml(text)
    except ParseError as e:
        raise SelfCheckError(f"emitted YAML does not parse: {e}")
    if not isinstance(doc, dict):
        raise SelfCheckError("emitted document is not a mapping")
    for k in REQUIRED:
        if k not in doc:
            raise SelfCheckError(f"missing required field: {k}")
    src = doc["source"]
    if not isinstance(src, dict) or not all(src.get(k) for k in ("ref", "sha256", "kind")):
        raise SelfCheckError("source must carry ref + sha256 + kind")
    if src.get("kind") not in ("system-prompt", "behavioral-spec", "character-voice"):
        raise SelfCheckError(f"source.kind invalid: {src.get('kind')!r}")
    if not isinstance(doc["capabilities"], list) or not doc["capabilities"]:
        raise SelfCheckError("capabilities must be a non-empty list")
    kn = doc["knowledge"]
    if not isinstance(kn, dict) or not isinstance(kn.get("knows"), list) \
            or not isinstance(kn.get("does_not_know"), list):
        raise SelfCheckError("knowledge must carry knows[] + does_not_know[]")
    ov = doc["rung_overlays"]
    rungs = ("blind", "reward-aware", "adversarial")
    if not isinstance(ov, dict) or not all(ov.get(r) for r in rungs):
        raise SelfCheckError("rung_overlays must carry blind + reward-aware + adversarial")


# ---- main -------------------------------------------------------------------

def main(argv):
    try:
        from_voice, pid, out = parse_args(argv)
        if from_voice:
            voice, vpath, vsha = load_voice(from_voice)
            disposition = seed_disposition(voice)
            source_ref, source_sha = vpath, vsha
            source_kind = "character-voice"  # exploration-origin, not real-agent lineage
            header = EXPLORATION_HEADER.format(voice=from_voice)
        else:
            disposition = BLANK_DISPOSITION
            source_ref = f"{pid}-spec.md"
            source_sha = "TODO-compute-sha256-of-the-spec-file"
            source_kind = "behavioral-spec"  # human grounds this in a real agent spec
            header = ""
        text = render(pid, source_ref, source_sha, source_kind, disposition, header)
        self_check(text)
    except InputError as e:
        err(str(e))
        return 1
    except SelfCheckError as e:
        err(f"self-check failed (refusing to write a broken skeleton): {e}")
        return 2

    dest = out or os.path.join(PERSONA_DIR, f"{pid}.yaml")
    try:
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        open(dest, "w", encoding="utf-8").write(text)
    except OSError as e:
        err(f"cannot write {dest}: {e}")
        return 1
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
