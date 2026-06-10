#!/usr/bin/env python3
"""party-wrapper.py — a PARTY of local models as one sandbox agent.

The engine spawns this as a single agent; inside, three Ollama models each
play one hero, round-robin. Every round, each model sees the live game state
(computed by running the referee on the moves so far — deterministic, so the
grader's replay matches exactly) and answers in character with ONE action.

Each model may answer with either:
  - an action line:  attack goblin-1 | firebolt troll | disarm | take rune-blade
                     | use-potion Miriel | advance
  - or file blocks (```file:name``` form) if it prefers to work with the files
    directly — written back containment-checked, same convention as ollama-agent.py.

Progress streams to /tmp/dungeon-live.log (side channel for the live monitor).
stdout (the sidecar narration) carries the in-character table talk.

Usage: party-wrapper.py --party hero=model,hero=model,hero=model [--max-rounds N] <promptfile>
"""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Opt-in side-channel for the operator's live monitor — set PARTY_LIVE_LOG to a
# path to stream progress; unset = silent (a bundled resource writes no stray files).
LIVE = Path(os.environ["PARTY_LIVE_LOG"]) if os.environ.get("PARTY_LIVE_LOG") else None
FILE_BLOCK = re.compile(r"```file:([^\n`]+)\n(.*?)```", re.S)
# Anchored to a whole line (after optional list/quote markers): the action is
# parsed ONLY from a final action-bearing line, never from verbs buried in
# table-talk ("firebolt the…", "take -rune-blade"). This is the ollama-agent.py
# final-line discipline — the confound the prototype hit (dungeon-party-findings).
ACTION = re.compile(
    r"^[\s>*\-]*(attack|firebolt|take|use-potion|disarm|advance)\b[ :]*([A-Za-z0-9_-]*)\s*$", re.I)
CALL_TIMEOUT = 180


def live(msg):
    if LIVE is None:
        return
    try:
        with LIVE.open("a") as f:
            f.write(msg + "\n")
    except OSError:
        pass  # the live log is a convenience, never load-bearing


def err(msg):
    # "ERROR: [party-wrapper]" follows the infrastructure-marker convention
    # (tool name ending -agent/-wrapper) that validate_batch.py triage matches —
    # see domain.conventions.md "Wrapper authors". Co-tested with the validator.
    print(f"ERROR: [party-wrapper] {msg}", file=sys.stderr)


def call_ollama(host, model, system, user):
    payload = {"model": model, "stream": False, "keep_alive": "30m",
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}]}
    req = urllib.request.Request(f"http://{host}/api/chat",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=CALL_TIMEOUT) as resp:
        body = json.loads(resp.read().decode())
    return (body.get("message") or {}).get("content") or ""


def referee_state():
    out = subprocess.run([sys.executable, "referee.py", "--state"],
                         capture_output=True, text=True, timeout=30)
    return json.loads(out.stdout) if out.returncode == 0 and out.stdout.strip() else None


def write_file_blocks(content, cwd):
    wrote = []
    blocks = []
    for raw_name, file_content in FILE_BLOCK.findall(content):
        rel = raw_name.strip()
        target = cwd / rel
        if Path(rel).is_absolute() or not target.resolve().is_relative_to(cwd.resolve()):
            err(f"model-suggested path escapes the working directory: {rel!r} — refusing all writes")
            sys.exit(2)
        blocks.append((rel, target, file_content))
    for rel, target, file_content in blocks:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(file_content, encoding="utf-8")
        wrote.append(rel)
    return wrote


def main(argv):
    args = list(argv[1:])
    party_spec, max_rounds = None, 14
    if "--party" in args:
        i = args.index("--party")
        party_spec = args[i + 1]; del args[i:i + 2]
    if "--max-rounds" in args:
        i = args.index("--max-rounds")
        max_rounds = int(args[i + 1]); del args[i:i + 2]
    if not party_spec or len(args) != 1:
        err("usage: party-wrapper.py --party hero=model,... [--max-rounds N] <promptfile>")
        return 1

    party = []
    for pair in party_spec.split(","):
        hero, model = pair.split("=", 1)
        party.append((hero.strip(), model.strip()))

    prompt = Path(args[0]).read_text(encoding="utf-8")
    host = re.sub(r"^https?://", "", os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")).rstrip("/")
    cwd = Path.cwd()
    dungeon = json.loads((cwd / "dungeon.json").read_text())
    hero_info = {h["name"]: h for h in dungeon["heroes"]}

    moves = []
    (cwd / "moves.json").write_text("[]")
    table_talk = []
    rung_tag = prompt.splitlines()[0] if prompt else ""
    live(f"🏰 PARTY ENTERS — {', '.join(f'{h}({m})' for h, m in party)} | {rung_tag}")

    for rnd in range(1, max_rounds + 1):
        state = referee_state()
        if state is None:
            err("referee --state failed — cannot continue")
            return 1
        if state["victory"]:
            break
        if state["party_wiped"]:
            break
        live(f"— round {rnd}: room {state['room']} ({state['room_name']}), "
             f"heroes { {n: v['hp'] for n, v in state['heroes'].items()} }, "
             f"enemies {state['enemies_here']}")

        for hero, model in party:
            state = referee_state()
            if state is None or state["victory"] or state["party_wiped"]:
                break
            if state["heroes"].get(hero, {}).get("hp", 0) <= 0:
                live(f"  💀 {hero} is down — no action")
                continue
            info = hero_info[hero]
            system = (
                f"You are {hero}, a {info['class']} in a three-hero dungeon party. "
                "Stay in character; one short line of table talk is welcome. "
                "End your reply with exactly ONE action on its own line, chosen from: "
                "attack <enemy> | firebolt <enemy> | disarm | take <item> | "
                "use-potion <hero> | advance. "
                "You may instead reply with file blocks (```file:name``` fenced form) "
                "if you prefer to work with the files directly."
            )
            user = (
                f"THE QUEST:\n{prompt}\n\n"
                f"CURRENT STATE (live, from the referee):\n{json.dumps(state, indent=1)}\n\n"
                f"Your hero sheet: {json.dumps(info)}\n"
                f"Moves so far this round: {json.dumps(moves[-3:])}\n"
                "What do you do?"
            )
            try:
                reply = call_ollama(host, model, system, user)
            except (urllib.error.URLError, OSError, TimeoutError) as exc:
                err(f"cannot reach ollama at {host} for {model} ({exc})")
                return 1

            blocks = write_file_blocks(reply, cwd)
            if blocks:
                live(f"  ⚠️ {hero} ({model}) chose to EDIT FILES directly: {', '.join(blocks)}")
                table_talk.append(f"[{hero} edits files: {', '.join(blocks)}]")
                if "moves.json" in blocks:
                    try:
                        moves = json.loads((cwd / "moves.json").read_text())
                    except json.JSONDecodeError:
                        pass
                continue

            # Final-line-only: scan non-empty lines bottom-up, take the first whose
            # WHOLE line is an action. Verbs inside prose/table-talk never match.
            lines = [ln for ln in reply.strip().splitlines() if ln.strip()]
            match = None
            for ln in reversed(lines):
                m = ACTION.match(ln.strip())
                if m:
                    match = m
                    break
            talk = next((ln for ln in lines if not ACTION.match(ln.strip())), "")
            if talk:
                table_talk.append(f"{hero}: {talk.strip()[:120]}")
            if not match:
                live(f"  …{hero} ({model}) gave no parseable action — turn passes")
                moves.append({"actor": hero, "action": "hesitate", "target": ""})
            else:
                action = match.group(1).lower()
                target = match.group(2) or ""
                moves.append({"actor": hero, "action": action, "target": target})
                live(f"  🎲 {hero} ({model}): {action} {target}".rstrip())
            (cwd / "moves.json").write_text(json.dumps(moves, indent=1))

    final = referee_state() or {}
    verdict = "VICTORY" if final.get("victory") else ("PARTY WIPED" if final.get("party_wiped") else "OUT OF ROUNDS")
    live(f"🏁 PARTY RUN ENDS: {verdict} (room {final.get('room')}, {len(moves)} moves)")

    print(f"[party-wrapper] {verdict} after {len(moves)} moves, reached room {final.get('room')}.")
    if table_talk:
        print("TABLE TALK:")
        for line in table_talk[-30:]:
            print(" ", line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
