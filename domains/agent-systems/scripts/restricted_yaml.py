#!/usr/bin/env python3
"""restricted_yaml.py — the domain's shared restricted-subset YAML parser (stdlib only).

One parser, three consumers: scenario gate, projection, materialization. Supports
exactly what the domain's committed shapes need and nothing more:

  - nested maps (2-space indent), lists of scalars, lists of small blocks
  - inline lists  [a, b]  and simple inline maps  { k: v, k2: v2 }
  - scalars: ints, quoted/unquoted strings, true/false/null
  - literal block scalars  key: |  (preserved verbatim incl. trailing newline)

NOT supported (by design — keep shapes flat): anchors, folded scalars (>) outside
top-level descriptions are tolerated nowhere here, tags, multi-document streams.
"""

import re

INDENT = 2


class ParseError(Exception):
    pass


def _scalar(tok):
    tok = tok.strip()
    if tok.startswith("[") and tok.endswith("]"):
        inner = tok[1:-1].strip()
        return [] if not inner else [_scalar(t) for t in inner.split(",")]
    if tok.startswith("{") and tok.endswith("}"):
        inner = tok[1:-1].strip()
        out = {}
        if inner:
            for part in inner.split(","):
                if ":" not in part:
                    raise ParseError(f"bad inline map entry: {part!r}")
                k, v = part.split(":", 1)
                out[k.strip()] = _scalar(v)
        return out
    if (tok.startswith('"') and tok.endswith('"')) or (tok.startswith("'") and tok.endswith("'")):
        return tok[1:-1]
    if re.fullmatch(r"-?\d+", tok):
        return int(tok)
    if tok in ("true", "false"):
        return tok == "true"
    if tok in ("null", "~", ""):
        return None
    return tok


def _strip_comment(line):
    """Remove comments outside quotes."""
    out, in_q = [], None
    for ch in line:
        if in_q:
            out.append(ch)
            if ch == in_q:
                in_q = None
        elif ch in "\"'":
            in_q = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def parse(text):
    """Parse restricted YAML text into dicts/lists/scalars."""
    raw_lines = text.splitlines()

    # Pre-pass: collapse literal blocks (key: |) into single logical entries.
    lines = []  # (depth, content) or (depth, key, LITERAL, value)
    i = 0
    while i < len(raw_lines):
        raw = raw_lines[i]
        stripped = _strip_comment(raw)
        if not stripped.strip():
            i += 1
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        if indent % INDENT:
            raise ParseError(f"indent not a multiple of {INDENT}: {raw!r}")
        depth = indent // INDENT
        content = stripped.strip()
        m = re.match(r"^(-\s+)?([A-Za-z0-9_-]+):\s*\|$", content)
        if m:
            # Literal block: consume following lines more-indented than this key.
            # Content indent = first content line's indent (relative strip).
            body_lines = []
            base_indent = None
            j = i + 1
            while j < len(raw_lines):
                cand = raw_lines[j]
                if not cand.strip():
                    body_lines.append("")
                    j += 1
                    continue
                cand_indent = len(cand) - len(cand.lstrip(" "))
                if cand_indent <= indent:
                    break
                if base_indent is None:
                    base_indent = cand_indent
                body_lines.append(cand[base_indent:] if len(cand) >= base_indent else cand.lstrip(" "))
                j += 1
            while body_lines and body_lines[-1] == "":
                body_lines.pop()
            value = "\n".join(body_lines) + "\n"
            lines.append((depth, ("__literal__", bool(m.group(1)), m.group(2), value)))
            i = j
            continue
        lines.append((depth, content))
        i += 1

    def parse_block(pos, depth):
        node = None
        while pos < len(lines):
            d, content = lines[pos]
            if d < depth:
                break
            if d > depth:
                raise ParseError(f"unexpected indent at: {content!r}")

            if isinstance(content, tuple):  # literal block entry
                _, is_list_item, key, value = content
                if is_list_item:
                    if node is None:
                        node = []
                    if not isinstance(node, list):
                        raise ParseError(f"mixed list/map at literal {key!r}")
                    item = {key: value}
                    pos += 1
                    while pos < len(lines) and lines[pos][0] == depth + 1 and not _is_list_entry(lines[pos][1]):
                        sub_map, pos = parse_block(pos, depth + 1)
                        if not isinstance(sub_map, dict):
                            raise ParseError("expected map continuation in list item")
                        item.update(sub_map)
                    node.append(item)
                else:
                    if node is None:
                        node = {}
                    if not isinstance(node, dict):
                        raise ParseError(f"mixed map/list at literal {key!r}")
                    node[key] = value
                    pos += 1
                continue

            if content.startswith("- "):
                if node is None:
                    node = []
                if not isinstance(node, list):
                    raise ParseError(f"mixed list/map at: {content!r}")
                item_text = content[2:].strip()
                m = re.match(r"^([A-Za-z0-9_-]+):(.*)$", item_text)
                if m:
                    item = {}
                    key, rest = m.group(1), m.group(2).strip()
                    if rest == "|":
                        raise ParseError("literal block inside list shorthand not pre-collapsed")
                    if rest:
                        item[key] = _scalar(rest)
                        pos += 1
                    else:
                        sub, pos = parse_block(pos + 1, depth + 2)
                        item[key] = sub
                    while pos < len(lines) and lines[pos][0] == depth + 1 and not _is_list_entry(lines[pos][1]):
                        sub_map, pos = parse_block(pos, depth + 1)
                        if not isinstance(sub_map, dict):
                            raise ParseError("expected map continuation in list item")
                        item.update(sub_map)
                    node.append(item)
                else:
                    node.append(_scalar(item_text))
                    pos += 1
                continue

            m = re.match(r"^([A-Za-z0-9_-]+):(.*)$", content)
            if not m:
                raise ParseError(f"unparseable line: {content!r}")
            if node is None:
                node = {}
            if not isinstance(node, dict):
                raise ParseError(f"mixed map/list at: {content!r}")
            key, rest = m.group(1), m.group(2).strip()
            if rest:
                node[key] = _scalar(rest)
                pos += 1
            else:
                child, pos = parse_block(pos + 1, depth + 1)
                node[key] = child if child is not None else {}
        return node, pos

    def _is_list_entry(content):
        if isinstance(content, tuple):
            return content[1]  # literal entry's is_list_item flag
        return content.startswith("- ")

    tree, pos = parse_block(0, 0)
    if pos != len(lines):
        leftover = lines[pos][1]
        raise ParseError(f"trailing content at: {leftover!r}")
    return tree if tree is not None else {}


def parse_file(path):
    with open(path, encoding="utf-8") as f:
        return parse(f.read())
