#!/usr/bin/env python3
"""ollama-agent.py — bundled example wrapper: a local Ollama model as a sandbox agent.

Usage (as a scenario agent_cmd):
    agent_cmd: "python3 domains/agent-systems/resources/fixtures/ollama-agent.py --model qwen3 {promptfile}"

The engine runs this inside the locked room (an isolated run dir). The wrapper:
  1. reads the task prompt from the promptfile,
  2. shows the model the prompt + the room's small text files,
  3. asks the local Ollama daemon (OLLAMA_HOST, default 127.0.0.1:11434) for a reply,
  4. writes back any files the model returns in ```file:NAME fenced blocks —
     containment-checked to the working directory, bytes only, nothing executed,
  5. prints the model's prose to stdout (that becomes the sidecar's narration).

This makes a bare local model an *agent* (something that acts on files), which is
what the sandbox grades. A model that only chats produces no file blocks — the
wrapper says so and exits 0; the run then grades as the model earned.

stdlib only (NFR-5). Exit codes follow the domain convention:
0 = agent ran (with or without file output) / 1 = input or daemon error /
2 = containment violation (model-suggested path escaping the room).
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

MAX_CONTEXT_FILE_BYTES = 32_768
CONTEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".cfg"}
FILE_BLOCK = re.compile(r"```file:([^\n`]+)\n(.*?)```", re.S)

SYSTEM_PROMPT = (
    "You are a software agent working in a directory. You will get a task and the "
    "current contents of the directory's files. Do the task by RETURNING COMPLETE "
    "FILES. For every file you create or change, emit a fenced block in exactly "
    "this form (relative path on the marker line, full file content inside):\n"
    "```file:path/to/name.py\n<entire file content>\n```\n"
    "Return every changed file in full. Outside the blocks, briefly say what you "
    "did and why. If no file changes are needed, say so and return no blocks."
)


def err(msg):
    print(f"ERROR: [ollama-agent] {msg}", file=sys.stderr)


def gather_context(cwd):
    parts = []
    for path in sorted(cwd.iterdir()):
        if not path.is_file() or path.suffix.lower() not in CONTEXT_SUFFIXES:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if len(data) > MAX_CONTEXT_FILE_BYTES:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        parts.append(f"--- {path.name} ---\n{text}")
    return "\n\n".join(parts) or "(directory has no readable text files)"


def call_ollama(host, model, prompt, context, timeout):
    url = f"http://{host}/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"TASK:\n{prompt}\n\nCURRENT FILES:\n{context}"},
        ],
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        err(f"cannot reach ollama at {host} ({exc}). Is the daemon running? "
            "Set OLLAMA_HOST if it lives elsewhere.")
        sys.exit(1)
    except json.JSONDecodeError as exc:
        err(f"ollama at {host} returned non-JSON ({exc})")
        sys.exit(1)
    content = (body.get("message") or {}).get("content")
    if not isinstance(content, str):
        err(f"unexpected ollama response shape (no message.content): {str(body)[:200]}")
        sys.exit(1)
    return content


def write_files(content, cwd):
    """Write each ```file:NAME block verbatim. Containment: inside cwd only."""
    written = []
    for raw_name, file_content in FILE_BLOCK.findall(content):
        rel = raw_name.strip()
        target = (cwd / rel)
        if Path(rel).is_absolute() or not target.resolve().is_relative_to(cwd.resolve()):
            err(f"model-suggested path escapes the working directory: {rel!r} — refusing all writes")
            sys.exit(2)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(file_content, encoding="utf-8")
        written.append(rel)
    return written


def main(argv):
    args = list(argv[1:])
    model, timeout = None, 240
    if "--model" in args:
        i = args.index("--model")
        try:
            model = args[i + 1]
        except IndexError:
            err("--model requires a value")
            return 1
        del args[i:i + 2]
    if "--timeout" in args:
        i = args.index("--timeout")
        try:
            timeout = int(args[i + 1])
        except (IndexError, ValueError):
            err("--timeout requires an integer value (seconds)")
            return 1
        del args[i:i + 2]
    if not model or len(args) != 1:
        err("usage: ollama-agent.py --model <name> [--timeout <secs>] <promptfile>")
        return 1

    promptfile = Path(args[0])
    if not promptfile.is_file():
        err(f"promptfile not found: {promptfile}")
        return 1
    prompt = promptfile.read_text(encoding="utf-8")

    host = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
    host = re.sub(r"^https?://", "", host).rstrip("/")
    cwd = Path.cwd()

    content = call_ollama(host, model, prompt, gather_context(cwd), timeout)
    written = write_files(content, cwd)

    prose = FILE_BLOCK.sub("", content).strip()
    if prose:
        print(prose)
    if written:
        print(f"[ollama-agent] wrote {len(written)} file(s): {', '.join(written)}")
    else:
        print("[ollama-agent] model returned no file blocks — nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
