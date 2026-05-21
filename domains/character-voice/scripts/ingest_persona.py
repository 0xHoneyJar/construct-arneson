#!/usr/bin/env python3
"""
ingest_persona.py — Parse a freeside-characters persona.md into voice-character YAML.

Reads persona.md from file arg or stdin. Extracts voice-character schema fields
per the adapter spec at domains/character-voice/adapters/freeside.yaml.
Outputs voice-character YAML to stdout.

Exit codes:
  0  success
  1  parse error (missing required section, malformed input)
  2  sync contract violation
"""

import re
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# Section navigation
# ---------------------------------------------------------------------------

def find_section(text: str, header: str, level: int = 2) -> Optional[str]:
    """Return text between a markdown header and the next header at same or higher level."""
    prefix = "#" * level
    # Match the exact header line
    pattern = re.compile(
        rf"^{prefix}\s+{re.escape(header)}\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    m = pattern.search(text)
    if not m:
        return None
    start = m.end()
    # Find next header at same or higher level
    next_header = re.compile(rf"^#{{{1},{level}}}\s+", re.MULTILINE)
    n = next_header.search(text, start)
    end = n.start() if n else len(text)
    return text[start:end].strip()


def find_subsection(section_text: str, sub_pattern: str) -> Optional[str]:
    """Return text under a ### header or **bold** subsection marker."""
    # Try ### header first
    h3 = re.compile(
        rf"^###\s+{re.escape(sub_pattern)}\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    m = h3.search(section_text)
    if m:
        start = m.end()
        # End at next ### or ** marker or end of section
        nxt = re.compile(r"^(###\s+|\*\*\w)", re.MULTILINE)
        n = nxt.search(section_text, start)
        end = n.start() if n else len(section_text)
        return section_text[start:end].strip()

    # Try **bold** marker
    bold = re.compile(
        rf"^\*\*{re.escape(sub_pattern)}\*\*\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    m = bold.search(section_text)
    if m:
        start = m.end()
        nxt = re.compile(r"^(\*\*\w|###\s+)", re.MULTILINE)
        n = nxt.search(section_text, start)
        end = n.start() if n else len(section_text)
        return section_text[start:end].strip()

    return None


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def extract_first_italic(text: str) -> Optional[str]:
    """Extract the first *italic* line."""
    m = re.search(r"^\*([^*]+)\*\s*$", text, re.MULTILINE)
    return m.group(1) if m else None


def extract_list_items(text: str) -> list[str]:
    """Extract bullet-point list items (- or *)."""
    return re.findall(r"^\s*[-*]\s+(.+)$", text, re.MULTILINE)


def extract_bullet_rules(text: str) -> list[dict]:
    """Extract bullet items as discipline lock rules."""
    items = extract_list_items(text)
    rules = []
    for item in items:
        # Check for severity hints
        severity = "strong"
        lower = item.lower()
        if "always" in lower or "never" in lower or "non-negotiable" in lower:
            severity = "non_negotiable"
        elif "prefer" in lower or "usually" in lower:
            severity = "soft"
        rules.append({"rule": item, "severity": severity})
    return rules


def extract_kv_bullets(text: str) -> dict[str, str]:
    """Extract key-value bullet items: '- key -> value' or '- key -> value'."""
    result = {}
    for m in re.finditer(r"^\s*[-*]\s+(\S+)\s*->\s*(.+)$", text, re.MULTILINE):
        key = m.group(1).strip()
        val = m.group(2).strip()
        # Strip surrounding quotes if present
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            val = val[1:-1]
        # Handle escaped newlines in values
        val = val.replace("\\n", "\n")
        result[key] = val
    return result


def extract_structured_navigator(text: str) -> dict:
    """Extract navigator pattern fields from bullet descriptions."""
    nav = {}
    items = extract_list_items(text)
    forbidden = []
    for item in items:
        lower = item.lower()
        if "player-side always" in lower or "player_side" in lower:
            nav["player_side"] = "always"
        elif "player-side contextual" in lower:
            nav["player_side"] = "contextual"
        elif "never narrate" in lower:
            nav["narrate_opponents"] = "never"
        elif "implied" in lower and "narrat" in lower:
            nav["narrate_opponents"] = "implied_only"
        elif lower.startswith("forbidden:"):
            # Parse comma-separated forbidden phrases
            phrases_str = item.split(":", 1)[1].strip()
            # Split on commas, strip quotes
            for phrase in phrases_str.split(","):
                phrase = phrase.strip().strip('"').strip("'")
                if phrase:
                    forbidden.append(phrase)

    if forbidden:
        nav["forbidden_phrases"] = forbidden
    return nav


def extract_subsections_as_modes(text: str) -> list[dict]:
    """Extract ### subsections as mode entries."""
    modes = []
    # Find all ### headers and their content
    parts = re.split(r"^(###\s+.+)$", text, flags=re.MULTILINE)
    i = 1  # Skip text before first ###
    while i < len(parts):
        header_line = parts[i].strip()
        name = re.sub(r"^###\s+", "", header_line).strip()
        # Skip known non-mode subsections
        if name.lower() in ("decline patterns", "yield patterns",
                            "the navigator pattern", "cadence"):
            i += 2
            continue
        desc = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if name and desc:
            modes.append({"name": name, "description": desc})
        i += 2
    return modes


# ---------------------------------------------------------------------------
# System prompt template parsing
# ---------------------------------------------------------------------------

def extract_system_prompt_block(text: str) -> Optional[str]:
    """Extract the content of the 4-backtick fenced block under ## System prompt template."""
    section = find_section(text, "System prompt template")
    if not section:
        return None
    # Find 4-backtick block
    m = re.search(r"````\n(.*?)````", section, re.DOTALL)
    return m.group(1) if m else None


def extract_anti_patterns(prompt_block: str) -> list[str]:
    """Extract DON'T section items from system prompt template."""
    m = re.search(r"===\s*DON'T\s*===\s*\n(.*?)(?:===|\Z)", prompt_block, re.DOTALL)
    if not m:
        return []
    return extract_list_items(m.group(1))


def extract_prompt_exemplars(prompt_block: str) -> list[dict]:
    """Extract exemplar exchange pairs from system prompt EXEMPLARS section."""
    m = re.search(r"===\s*EXEMPLARS\s*===\s*\n(.*?)(?:===|\Z)", prompt_block, re.DOTALL)
    if not m:
        return []
    content = m.group(1).strip()
    exemplars = []
    # Split on blank lines to get pairs
    pairs = re.split(r"\n\s*\n", content)
    for pair in pairs:
        pair = pair.strip()
        if not pair:
            continue
        player = re.search(r"\*\*Player:\*\*\s*(.+)", pair)
        persona = re.search(r"\*\*\w+:\*\*\s*(.+)", pair)
        # Get the second **Name:** match (persona response)
        matches = re.findall(r"\*\*(\w+):\*\*\s*(.+)", pair)
        if len(matches) >= 2:
            exemplars.append({
                "prompt": matches[0][1].strip(),
                "response": matches[1][1].strip(),
            })
    return exemplars


# ---------------------------------------------------------------------------
# Reference body exemplar parsing
# ---------------------------------------------------------------------------

def extract_body_exemplars(text: str) -> list[dict]:
    """Extract exemplars from ## exemplars (canon-quality exchanges) section."""
    section = find_section(text, "exemplars (canon-quality exchanges)")
    if not section:
        return []
    exemplars = []
    # Split by ### exemplar N headers
    parts = re.split(r"^###\s+exemplar\s+\d+\s*$", section, flags=re.MULTILINE | re.IGNORECASE)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        matches = re.findall(r"\*\*(\w+):\*\*\s*(.+)", part)
        context_m = re.search(r"^\*Context:\s*(.+)\*\s*$", part, re.MULTILINE)
        if len(matches) >= 2:
            ex = {
                "prompt": matches[0][1].strip(),
                "response": matches[1][1].strip(),
            }
            if context_m:
                ex["context"] = context_m.group(1).strip()
            exemplars.append(ex)
    return exemplars


# ---------------------------------------------------------------------------
# Frontmatter extraction
# ---------------------------------------------------------------------------

def extract_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter between --- delimiters."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        kv = line.split(":", 1)
        if len(kv) != 2:
            continue
        key = kv[0].strip()
        val = kv[1].strip()
        # Strip quotes
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            val = val[1:-1]
        # Handle arrays
        if val == "[]":
            val = []
        elif val.startswith("["):
            val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
        fm[key] = val
    return fm


# ---------------------------------------------------------------------------
# YAML serializer (no PyYAML — stdlib only)
# ---------------------------------------------------------------------------

def yaml_quote(s: str) -> str:
    """Double-quote a string value, escaping embedded quotes and newlines."""
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{s}"'


def to_yaml(data: dict, indent: int = 0) -> str:
    """Serialize a dict to YAML string. Handles str, list, dict, and list[dict]."""
    lines = []
    prefix = "  " * indent
    for key, val in data.items():
        if val is None or val == [] or val == {}:
            continue
        if isinstance(val, str):
            lines.append(f"{prefix}{key}: {yaml_quote(val)}")
        elif isinstance(val, list):
            if not val:
                continue
            if isinstance(val[0], dict):
                lines.append(f"{prefix}{key}:")
                for item in val:
                    # First key gets the dash
                    keys = list(item.keys())
                    first_key = keys[0]
                    lines.append(f"{prefix}  - {first_key}: {yaml_quote(str(item[first_key]))}")
                    for k in keys[1:]:
                        lines.append(f"{prefix}    {k}: {yaml_quote(str(item[k]))}")
            else:
                lines.append(f"{prefix}{key}:")
                for item in val:
                    lines.append(f"{prefix}  - {yaml_quote(str(item))}")
        elif isinstance(val, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(to_yaml(val, indent + 1))
        else:
            lines.append(f"{prefix}{key}: {yaml_quote(str(val))}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: [ingest] {msg}", file=sys.stderr)
    sys.exit(code)


def ingest(text: str) -> dict:
    """Parse persona.md text into voice-character dict."""
    result = {}

    # --- Frontmatter ---
    fm = extract_frontmatter(text)
    if fm:
        result["metadata"] = fm

    # --- OG voice anchor (REQUIRED) ---
    og_section = find_section(text, "OG voice anchor")
    if og_section is None:
        die("Missing required section: ## OG voice anchor")
    og_line = extract_first_italic(og_section)
    if og_line is None:
        die("No italic line found in ## OG voice anchor")

    # --- Battle whispers ---
    battle = find_section(text, "battle whispers")
    voice_anchors = {"og_line": og_line}
    if battle:
        win_sub = find_subsection(battle, "win")
        if win_sub:
            voice_anchors["win"] = extract_list_items(win_sub)
        lose_sub = find_subsection(battle, "lose")
        if lose_sub:
            voice_anchors["lose"] = extract_list_items(lose_sub)
        draw_sub = find_subsection(battle, "draw")
        if draw_sub:
            voice_anchors["draw"] = extract_list_items(draw_sub)
    result["voice_anchors"] = voice_anchors

    # --- Voice discipline lock ---
    discipline = find_section(text, "voice discipline lock")
    if discipline:
        # Speech patterns from cadence
        cadence = find_subsection(discipline, "cadence")
        if cadence:
            markers = extract_list_items(cadence)
            result["speech_patterns"] = {"distinctive_markers": markers}

        # Discipline locks from Navigator pattern
        nav_section = find_subsection(discipline, "the Navigator pattern")
        if nav_section:
            rules = extract_bullet_rules(nav_section)
            result["discipline_locks"] = rules
            nav = extract_structured_navigator(nav_section)
            if nav:
                result["navigator_pattern"] = nav

    # --- Moments + modes ---
    moments = find_section(text, "moments + modes")
    if moments:
        # Decline patterns
        decline_sub = find_subsection(moments, "decline patterns")
        if decline_sub:
            result["decline_patterns"] = extract_kv_bullets(decline_sub)

        # Yield patterns
        yield_sub = find_subsection(moments, "yield patterns")
        if yield_sub:
            result["yield_map"] = extract_kv_bullets(yield_sub)

        # Modes (non-special subsections)
        modes = extract_subsections_as_modes(moments)
        if modes:
            result["modes"] = modes

    # --- World presence ---
    world = find_section(text, "world presence")
    if world:
        canon = {}
        knows = find_subsection(world, "canon she carries")
        if knows:
            canon["knows"] = extract_list_items(knows)
        doesnt = find_subsection(world, "canon she does NOT carry")
        if doesnt:
            canon["does_not_know"] = extract_list_items(doesnt)
        if canon:
            result["canon_boundary"] = canon

    # --- Exemplars (from reference body) ---
    exemplars = extract_body_exemplars(text)
    if exemplars:
        result["exemplars"] = exemplars

    # --- Anti-patterns (from system prompt template DON'T section) ---
    prompt_block = extract_system_prompt_block(text)
    if prompt_block:
        anti = extract_anti_patterns(prompt_block)
        if anti:
            result["anti_patterns"] = anti

    return result


def main():
    # Read input
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        path = sys.argv[1]
        try:
            with open(path, "r") as f:
                text = f.read()
        except FileNotFoundError:
            die(f"File not found: {path}")
        except OSError as e:
            die(f"Cannot read file: {path}: {e}")
    else:
        text = sys.stdin.read()

    if not text.strip():
        die("Empty input")

    # Check format: must contain ## System prompt template
    if "## System prompt template" not in text:
        die("Not a freeside persona.md: missing '## System prompt template'")

    result = ingest(text)
    print(to_yaml(result))


if __name__ == "__main__":
    main()
