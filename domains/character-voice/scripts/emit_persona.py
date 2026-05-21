#!/usr/bin/env python3
"""
emit_persona.py — Reconstruct a freeside-characters persona.md from voice-character YAML.

Section-level editor: reads the original persona.md as template, updates mapped
sections from voice-character YAML state, preserves non-mapped sections verbatim.
Updates BOTH reference body and system prompt template atomically per sync contract.

Exit codes:
  0  success
  1  parse error
  2  sync contract violation
"""

import re
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# Minimal YAML reader (for ingest output subset — no PyYAML)
# ---------------------------------------------------------------------------

def parse_yaml(text: str) -> dict:
    """Parse the subset of YAML that ingest_persona.py produces."""
    root = {}
    stack = [(root, -1)]  # (dict, indent_level)
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = len(line) - len(stripped)

        # Pop stack to find parent
        while len(stack) > 1 and stack[-1][1] >= indent:
            stack.pop()
        parent = stack[-1][0]

        if stripped.startswith("- "):
            # List item
            content = stripped[2:]
            if ":" in content and not content.startswith('"'):
                # Dict item in list: - key: value
                key, val = content.split(":", 1)
                key = key.strip()
                val = _parse_value(val.strip())
                item = {key: val}
                # Read continuation keys at deeper indent
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    next_stripped = next_line.lstrip()
                    next_indent = len(next_line) - len(next_stripped)
                    if not next_stripped or next_indent <= indent:
                        break
                    if not next_stripped.startswith("- ") and ":" in next_stripped:
                        k2, v2 = next_stripped.split(":", 1)
                        item[k2.strip()] = _parse_value(v2.strip())
                    j += 1
                if isinstance(parent, list):
                    parent.append(item)
                else:
                    _append_to_last_list(parent, item)
                i = j
                continue
            else:
                val = _parse_value(content)
                if isinstance(parent, list):
                    parent.append(val)
                else:
                    _append_to_last_list(parent, val)
                i += 1
                continue

        if ":" in stripped:
            key, rest = stripped.split(":", 1)
            key = key.strip()
            rest = rest.strip()
            if rest:
                parent[key] = _parse_value(rest)
            else:
                # Could be a dict or list — peek ahead
                if i + 1 < len(lines):
                    next_stripped = lines[i + 1].lstrip()
                    if next_stripped.startswith("- "):
                        parent[key] = []
                    else:
                        parent[key] = {}
                else:
                    parent[key] = {}
                stack.append((parent[key], indent))
        i += 1

    return root


def _parse_value(s: str) -> str:
    """Parse a YAML scalar value."""
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        # Unescape
        return s[1:-1].replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    if s == "[]":
        return []
    return s


def _append_to_last_list(parent: dict, item) -> None:
    """Append item to the last list-valued key in parent."""
    for key in reversed(list(parent.keys())):
        if isinstance(parent[key], list):
            parent[key].append(item)
            return
    # Fallback: shouldn't happen with well-formed input
    pass


# ---------------------------------------------------------------------------
# Section replacement engine
# ---------------------------------------------------------------------------

def replace_section_content(text: str, header: str, new_content: str,
                            level: int = 2) -> str:
    """Replace the content of a markdown section, keeping the header."""
    prefix = "#" * level
    pattern = re.compile(
        rf"^({prefix}\s+{re.escape(header)}\s*\n)",
        re.MULTILINE | re.IGNORECASE,
    )
    m = pattern.search(text)
    if not m:
        return text  # Section not found, passthrough

    header_end = m.end()
    # Find next header at same or higher level
    next_header = re.compile(rf"^#{{{1},{level}}}\s+", re.MULTILINE)
    n = next_header.search(text, header_end)
    section_end = n.start() if n else len(text)

    return text[:header_end] + new_content + "\n\n" + text[section_end:]


def replace_subsection_content(text: str, section_header: str,
                               sub_header: str, new_content: str,
                               section_level: int = 2) -> str:
    """Replace content of a subsection within a section."""
    # Find the section first
    prefix = "#" * section_level
    sec_pattern = re.compile(
        rf"^({prefix}\s+{re.escape(section_header)}\s*\n)",
        re.MULTILINE | re.IGNORECASE,
    )
    sec_m = sec_pattern.search(text)
    if not sec_m:
        return text

    sec_start = sec_m.end()
    next_sec = re.compile(rf"^#{{{1},{section_level}}}\s+", re.MULTILINE)
    sec_n = next_sec.search(text, sec_start)
    sec_end = sec_n.start() if sec_n else len(text)
    section_text = text[sec_start:sec_end]

    # Find subsection within section (try ### first, then **)
    sub_prefix = "###"
    sub_pattern = re.compile(
        rf"^({sub_prefix}\s+{re.escape(sub_header)}\s*\n)",
        re.MULTILINE | re.IGNORECASE,
    )
    sub_m = sub_pattern.search(section_text)
    is_bold = False

    if not sub_m:
        # Try **bold** marker
        sub_pattern = re.compile(
            rf"^(\*\*{re.escape(sub_header)}\*\*\s*\n)",
            re.MULTILINE | re.IGNORECASE,
        )
        sub_m = sub_pattern.search(section_text)
        is_bold = True

    if not sub_m:
        return text

    sub_header_end = sub_m.end()
    # Find next subsection delimiter
    if is_bold:
        nxt = re.compile(r"^(\*\*\w|###\s+)", re.MULTILINE)
    else:
        nxt = re.compile(r"^(###\s+|\*\*\w)", re.MULTILINE)
    sub_n = nxt.search(section_text, sub_header_end)
    sub_end = sub_n.start() if sub_n else len(section_text)

    # Reconstruct
    new_section = (section_text[:sub_header_end] + new_content + "\n"
                   + section_text[sub_end:])
    return text[:sec_start] + new_section + text[sec_end:]


def replace_prompt_marker_content(prompt_block: str, marker: str,
                                  new_content: str) -> str:
    """Replace content between === MARKER === delimiters in system prompt."""
    pattern = re.compile(
        rf"(===\s*{re.escape(marker)}\s*===\s*\n)(.*?)(?=\n===|\Z)",
        re.DOTALL,
    )
    m = pattern.search(prompt_block)
    if not m:
        return prompt_block
    return prompt_block[:m.start(2)] + new_content + prompt_block[m.end(2):]


# ---------------------------------------------------------------------------
# Formatters (voice-character state -> persona.md content)
# ---------------------------------------------------------------------------

def format_italic_line(value: str) -> str:
    return f"*{value}*"


def format_bullet_list(items: list) -> str:
    return "\n".join(f"- {item}" for item in items)


def format_kv_bullets(mapping: dict) -> str:
    lines = []
    for key, val in mapping.items():
        # Escape newlines back to literal \n for persona.md
        display_val = val.replace("\n", "\\n") if isinstance(val, str) else str(val)
        lines.append(f"- {key} -> {display_val}")
    return "\n".join(lines)


def format_exemplar_body(exemplars: list) -> str:
    """Format exemplars for reference body (unlimited)."""
    blocks = []
    for i, ex in enumerate(exemplars, 1):
        block = f"### exemplar {i}\n"
        block += f"**Player:** {ex.get('prompt', '')}\n"
        # Determine persona name from context or default
        block += f"**Compass:** {ex.get('response', '')}\n"
        if ex.get("context"):
            block += f"*Context: {ex['context']}*"
        blocks.append(block)
    return "\n\n".join(blocks)


def format_exemplar_prompt(exemplars: list, budget: int = 5) -> str:
    """Format exemplars for system prompt (max budget)."""
    # Take most recent up to budget
    selected = exemplars[:budget]
    pairs = []
    for ex in selected:
        pair = f"**Player:** {ex.get('prompt', '')}\n"
        pair += f"**Compass:** {ex.get('response', '')}"
        pairs.append(pair)
    return "\n\n".join(pairs)


def format_voice_canon(anchors: dict) -> str:
    """Format voice anchors for system prompt VOICE CANON section."""
    lines = []
    for register in ("win", "lose", "draw"):
        items = anchors.get(register, [])
        if items:
            joined = " \u00b7 ".join(items)  # middle dot separator
            lines.append(f"**{register}**: {joined}")
    return "\n".join(lines)


def format_canon_boundary_prompt(boundary: dict) -> str:
    """Format canon boundary for system prompt."""
    lines = []
    knows = boundary.get("knows", [])
    if knows:
        lines.append(f"**Knows:** {', '.join(knows)}.")
    doesnt = boundary.get("does_not_know", [])
    if doesnt:
        lines.append(f"**Does not know:** {', '.join(doesnt)}.")
    return "\n".join(lines)


def format_tool_use(decline_patterns: dict) -> str:
    """Format decline patterns for system prompt TOOL USE section."""
    lines = []
    for topic, phrase in decline_patterns.items():
        # Flatten newlines for system prompt
        flat_phrase = phrase.replace("\n", " ") if isinstance(phrase, str) else str(phrase)
        lines.append(f'When asked about {topic}: "{flat_phrase}"')
    return "\n".join(lines)


def format_dont(anti_patterns: list) -> str:
    """Format anti-patterns for system prompt DON'T section."""
    return "\n".join(f"- {item}" for item in anti_patterns)


# ---------------------------------------------------------------------------
# Sync contract validation
# ---------------------------------------------------------------------------

DUAL_TARGET_FIELDS = {
    "decline_patterns": {"body": "### decline patterns", "prompt": "TOOL USE"},
    "anti_patterns": {"body": None, "prompt": "DON'T"},
    "voice_anchors": {"body": "## battle whispers", "prompt": "VOICE CANON"},
    "canon_boundary": {"body": "## world presence", "prompt": "CANON BOUNDARY"},
    "exemplars": {"body": "## exemplars (canon-quality exchanges)", "prompt": "EXEMPLARS"},
}


def validate_sync_contract(state: dict, output: str) -> list[str]:
    """Validate that all dual-target fields are present in both layers.
    Returns list of violation messages (empty = valid)."""
    violations = []
    prompt_block = ""
    pm = re.search(r"````\n(.*?)````", output, re.DOTALL)
    if pm:
        prompt_block = pm.group(1)

    for field, targets in DUAL_TARGET_FIELDS.items():
        if field not in state:
            continue
        # Check body target (if not null)
        if targets["body"] is not None:
            if targets["body"].lower() not in output.lower():
                violations.append(
                    f"Sync violation: {field} in state but body target "
                    f"'{targets['body']}' missing from output"
                )
        # Check prompt target
        if targets["prompt"] not in prompt_block:
            violations.append(
                f"Sync violation: {field} in state but prompt target "
                f"'{targets['prompt']}' missing from system prompt"
            )
    return violations


# ---------------------------------------------------------------------------
# Main emit logic
# ---------------------------------------------------------------------------

def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: [emit] {msg}", file=sys.stderr)
    sys.exit(code)


def emit(state: dict, template: str) -> str:
    """Update template persona.md with voice-character state. Returns full file."""
    output = template

    # --- Reference body updates ---

    # OG voice anchor
    va = state.get("voice_anchors", {})
    og = va.get("og_line")
    if og:
        output = replace_section_content(output, "OG voice anchor",
                                         format_italic_line(og))

    # Battle whispers
    if any(va.get(r) for r in ("win", "lose", "draw")):
        for register in ("win", "lose", "draw"):
            items = va.get(register, [])
            if items:
                output = replace_subsection_content(
                    output, "battle whispers", register,
                    format_bullet_list(items) + "\n"
                )

    # Decline patterns
    dp = state.get("decline_patterns", {})
    if dp:
        output = replace_subsection_content(
            output, "moments + modes", "decline patterns",
            format_kv_bullets(dp) + "\n"
        )

    # Yield patterns
    ym = state.get("yield_map", {})
    if ym:
        output = replace_subsection_content(
            output, "moments + modes", "yield patterns",
            format_kv_bullets(ym) + "\n"
        )

    # Canon boundary
    cb = state.get("canon_boundary", {})
    if cb.get("knows"):
        output = replace_subsection_content(
            output, "world presence", "canon she carries",
            format_bullet_list(cb["knows"]) + "\n"
        )
    if cb.get("does_not_know"):
        output = replace_subsection_content(
            output, "world presence", "canon she does NOT carry",
            format_bullet_list(cb["does_not_know"]) + "\n"
        )

    # Exemplars (reference body — unlimited)
    exemplars = state.get("exemplars", [])
    if exemplars:
        output = replace_section_content(
            output, "exemplars (canon-quality exchanges)",
            format_exemplar_body(exemplars)
        )

    # --- System prompt template updates ---

    # Extract the 4-backtick block
    prompt_match = re.search(r"(````\n)(.*?)(````)", output, re.DOTALL)
    if not prompt_match:
        die("Template missing system prompt template block (4-backtick fence)")

    prompt_block = prompt_match.group(2)

    # VOICE CANON
    if any(va.get(r) for r in ("win", "lose", "draw")):
        prompt_block = replace_prompt_marker_content(
            prompt_block, "VOICE CANON",
            format_voice_canon(va) + "\n"
        )

    # DON'T
    ap = state.get("anti_patterns", [])
    if ap:
        prompt_block = replace_prompt_marker_content(
            prompt_block, "DON'T",
            format_dont(ap) + "\n"
        )

    # EXEMPLARS (max 5)
    if exemplars:
        prompt_block = replace_prompt_marker_content(
            prompt_block, "EXEMPLARS",
            format_exemplar_prompt(exemplars, budget=5) + "\n"
        )

    # CANON BOUNDARY
    if cb:
        prompt_block = replace_prompt_marker_content(
            prompt_block, "CANON BOUNDARY",
            format_canon_boundary_prompt(cb) + "\n"
        )

    # TOOL USE
    if dp:
        prompt_block = replace_prompt_marker_content(
            prompt_block, "TOOL USE",
            format_tool_use(dp) + "\n"
        )

    # Reassemble the system prompt block
    output = (output[:prompt_match.start(2)]
              + prompt_block
              + output[prompt_match.end(2):])

    # --- Sync contract validation ---
    violations = validate_sync_contract(state, output)
    if violations:
        for v in violations:
            print(f"ERROR: [emit] {v}", file=sys.stderr)
        sys.exit(2)

    return output


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Emit persona.md from voice-character YAML")
    parser.add_argument("--template", required=True, help="Path to original persona.md")
    parser.add_argument("--state", help="Path to voice-character YAML (default: stdin)")
    args = parser.parse_args()

    # Read template
    try:
        with open(args.template, "r") as f:
            template = f.read()
    except FileNotFoundError:
        die(f"Template not found: {args.template}")
    except OSError as e:
        die(f"Cannot read template: {args.template}: {e}")

    # Read state
    if args.state:
        try:
            with open(args.state, "r") as f:
                state_text = f.read()
        except FileNotFoundError:
            die(f"State file not found: {args.state}")
        except OSError as e:
            die(f"Cannot read state: {args.state}: {e}")
    else:
        state_text = sys.stdin.read()

    if not state_text.strip():
        die("Empty state input")

    state = parse_yaml(state_text)
    result = emit(state, template)
    print(result, end="")


if __name__ == "__main__":
    main()
