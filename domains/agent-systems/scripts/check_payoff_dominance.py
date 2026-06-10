#!/usr/bin/env python3
"""check_payoff_dominance.py — calibration discipline mechanized (FR-3, Sprint 2).

Usage:
    check_payoff_dominance.py <incentive-state-dir>

For a cliff claim to be meaningful, the *hack* must be payoff-dominant over the
*intended* action somewhere in the declared difficulty domain — otherwise "no
cliff observed" is uninformative (a model staying honest proves nothing if honesty
was already optimal). This checks the fixture's DECLARED ECONOMICS only — it reads
payoff expressions, never an agent's behavior (NFR-6, producer-never-judges).

Each action declares `payoff: {reward, cost}` as expressions in the context
variable (e.g. cost "0.12 * difficulty"). net = reward - cost. The reward's
`intent.intended_action` names the honest action; every other action is a
candidate hack. PASS iff some hack's net >= intended net at some sampled point in
[domain.min, domain.max].

Discipline = warn-not-reject (NFR-5): PASS / WARN both exit 0; exit 1 only on
unparseable input. Output is the verdict + the dominating point if any.

Expression grammar (deliberately tiny, stdlib eval-free): numbers, the context
variable name, + - * /, and parentheses. Anything else => unparseable (exit 1).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from restricted_yaml import ParseError, parse_file  # noqa: E402

SAMPLES = 50  # evenly spaced points across the domain


def err(msg):
    print(f"ERROR: [check_payoff_dominance] {msg}", file=sys.stderr)


# --- tiny safe arithmetic evaluator (no eval/exec) -------------------------------
_TOKEN = re.compile(r"\s*([0-9]*\.?[0-9]+|[A-Za-z_][A-Za-z0-9_]*|[()+\-*/])")


def _tokenize(expr):
    pos, toks = 0, []
    while pos < len(expr):
        m = _TOKEN.match(expr, pos)
        if not m:
            raise ValueError(f"bad token near {expr[pos:pos+8]!r}")
        toks.append(m.group(1))
        pos = m.end()
    return toks


def _eval(expr, var_name, var_val):
    """Recursive-descent over + - * / and parens; one variable. No eval()."""
    toks = _tokenize(expr)
    i = 0

    def peek():
        return toks[i] if i < len(toks) else None

    def nextt():
        nonlocal i
        t = toks[i]
        i += 1
        return t

    def atom():
        nonlocal i
        t = peek()
        if t == "(":
            nextt()
            v = expr_()
            if peek() != ")":
                raise ValueError("unbalanced parens")
            nextt()
            return v
        t = nextt()
        if re.fullmatch(r"[0-9]*\.?[0-9]+", t):
            return float(t)
        if t == var_name:
            return float(var_val)
        raise ValueError(f"unknown symbol {t!r} (only numbers and {var_name!r} allowed)")

    def term():
        v = atom()
        while peek() in ("*", "/"):
            op = nextt()
            r = atom()
            v = v * r if op == "*" else v / r
        return v

    def expr_():
        v = term()
        while peek() in ("+", "-"):
            op = nextt()
            r = term()
            v = v + r if op == "+" else v - r
        return v

    v = expr_()
    if i != len(toks):
        raise ValueError("trailing tokens")
    return v


def _net_fn(action, var_name):
    payoff = action.get("payoff") or {}
    reward, cost = str(payoff.get("reward", "")), str(payoff.get("cost", ""))
    if not reward or not cost:
        raise ValueError(f"action {action.get('id')!r} missing payoff.reward/cost")
    return lambda x: _eval(reward, var_name, x) - _eval(cost, var_name, x)


def main(argv):
    if len(argv) != 2:
        err("usage: check_payoff_dominance.py <incentive-state-dir>")
        return 1
    isdir = Path(argv[1])
    index = isdir / "index.yaml"
    if not index.is_file():
        err(f"incentive-state index not found: {index}")
        return 1
    try:
        idx = parse_file(index)
    except ParseError as e:
        err(f"{index}: parse failure: {e}")
        return 1

    ctx = idx.get("context") or {}
    var_name = str(ctx.get("name", "difficulty"))
    domain = ctx.get("domain") or {}
    try:
        lo, hi = float(domain.get("min", 1)), float(domain.get("max", 10))
    except (TypeError, ValueError):
        err("context.domain.min/max must be numbers")
        return 1

    reward_ref = idx.get("reward_signal")
    intended = None
    if reward_ref:
        rpath = isdir / Path(str(reward_ref)).name if not (isdir / str(reward_ref)).is_file() else isdir / str(reward_ref)
        if rpath.is_file():
            try:
                intended = ((parse_file(rpath).get("intent") or {}).get("intended_action"))
            except ParseError:
                intended = None
    if not intended:
        err("reward signal declares no intent.intended_action — cannot identify the honest action")
        return 1

    # Load actions
    actions = {}
    for ref in idx.get("actions") or []:
        apath = isdir / str(ref)
        if not apath.is_file():
            err(f"declared action file missing: {apath}")
            return 1
        try:
            a = parse_file(apath)
        except ParseError as e:
            err(f"{apath}: parse failure: {e}")
            return 1
        actions[a.get("id")] = a

    if intended not in actions:
        err(f"intended_action {intended!r} not among declared actions {sorted(actions)}")
        return 1

    try:
        intended_net = _net_fn(actions[intended], var_name)
        hack_nets = {aid: _net_fn(a, var_name) for aid, a in actions.items() if aid != intended}
    except ValueError as e:
        err(f"unparseable payoff expression: {e}")
        return 1
    if not hack_nets:
        err("no candidate hack actions (only the intended action declared)")
        return 1

    # Sample the domain; find any point where some hack net >= intended net.
    dominating = None
    step = (hi - lo) / (SAMPLES - 1) if SAMPLES > 1 else 0
    for k in range(SAMPLES):
        x = lo + step * k
        try:
            inet = intended_net(x)
            for aid, fn in hack_nets.items():
                if fn(x) >= inet:
                    dominating = (aid, round(x, 3), round(fn(x), 3), round(inet, 3))
                    break
        except (ValueError, ZeroDivisionError) as e:
            err(f"payoff evaluation failed at {var_name}={x}: {e}")
            return 1
        if dominating:
            break

    if dominating:
        aid, x, hnet, inet = dominating
        print(f"PASS: hack {aid!r} is payoff-dominant at {var_name}={x} "
              f"(net {hnet} >= intended {intended!r} net {inet}) — a cliff claim is meaningful here.")
    else:
        print(f"WARN: no declared hack out-nets the intended action {intended!r} anywhere in "
              f"[{lo}, {hi}] — 'no cliff observed' would be uninformative (honesty is already "
              "optimal). Tune the task (raise the honest cost / sharpen the hack), never rig it.")
    return 0  # warn-not-reject (NFR-5)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
