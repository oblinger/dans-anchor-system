#!/usr/bin/env python3
"""Warden moment dispatcher — the fire half of F211 (Rule compiler / installer).

Given a compiled anchor (`rules-ir.json` + `rules_<anchor>.py`, produced by
`warden_compile.py`) and a runtime moment, `fire()` runs **only** that moment's
rules and returns their steers. This is the hot path the ms budget rides on:

  fire(moment) = a dict lookup on `ir["moments"][moment]`  → candidate rule ids
               → filter by active-set membership (rule's trait ∈ anchor traits)
               → evaluate the declarative residual (`guards`; `where` is a place
                 filter applied by the caller when it has a target path)
               → run the rule's body (declarative `action`, or the emitted
                 `body_<id>` / `guard_<id>` from the module) → collect steers.

A rule keyed under a *different* moment is never in the bucket, so it never
executes — that indexed dispatch is the property the F211 Success Criteria
pins (two adopted rules on different moments; firing one runs only its module).

`build_ctx` assembles the interpretation environment a rule body reads. It is
moment-shaped: for the `audit-q` cooperative post-moment it carries
`queries_text` + `git_aspect` + `anchor` (what `R-query-14` reads). Callers may
inject/override any field (tests, or a moment that carries different context).

Install (registering these modules with the live Claude Code hook surface) is
the productionisation layer above this dispatcher; this module is the
engine-level fire that the differential harness (F214) and F212 test directly.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import types
from pathlib import Path

# Trait name (in `.anchor` `traits:`) → the git_aspect string a rule body reads.
_GIT_ASPECT = {"commit": "commit", "pr": "pr", "push": "push", "nogit": "nogit"}


# ── loading the compiled artifacts ──────────────────────────────────────────

def load_compiled(warden_dir: Path, anchor: str) -> tuple[dict, types.ModuleType | None]:
    """Load `rules-ir.json` + import `rules_<anchor>.py` from a compiled dir."""
    ir = json.loads((warden_dir / "rules-ir.json").read_text(encoding="utf-8"))
    mod_path = warden_dir / f"rules_{anchor}.py"
    module = None
    if mod_path.is_file():
        spec = importlib.util.spec_from_file_location(f"rules_{anchor}", mod_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
    return ir, module


# ── anchor sensing (active-set + ctx inputs) ────────────────────────────────

def read_anchor_traits(anchor_root: Path) -> list[str]:
    """The `.anchor` `traits:` list (YAML flow or block), plus the implicit base
    trait every anchor carries without declaring it ([[Warden Semantics]])."""
    traits: list[str] = []
    dot = anchor_root / ".anchor"
    if dot.is_file():
        text = dot.read_text(encoding="utf-8")
        m = re.search(r"^traits:\s*\[(.*?)\]", text, re.MULTILINE)
        if m:
            traits = [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]
        else:
            block = re.search(r"^traits:\s*\n((?:\s*-\s*.+\n?)+)", text, re.MULTILINE)
            if block:
                traits = [ln.split("-", 1)[1].strip()
                          for ln in block.group(1).splitlines() if ln.strip().startswith("-")]
    return traits + ["_base"]


def anchor_name(anchor_root: Path) -> str:
    dot = anchor_root / ".anchor"
    if dot.is_file():
        m = re.search(r"^\s*(?:slug|name)\s*:\s*(.+?)\s*$", dot.read_text(encoding="utf-8"),
                      re.MULTILINE)
        if m:
            return m.group(1).strip().strip("'\"")
    return anchor_root.name


def git_aspect_of(traits: list[str]) -> str:
    for t in traits:
        if t.lower() in _GIT_ASPECT:
            return _GIT_ASPECT[t.lower()]
    return ""


def build_ctx(anchor_root: Path, moment: str, **overrides) -> types.SimpleNamespace:
    """Assemble the interpretation environment for a moment. Moment-shaped;
    overrides win (tests inject, or a caller supplies moment-specific context)."""
    traits = read_anchor_traits(anchor_root)
    name = anchor_name(anchor_root)
    import warden_agent as wa
    fields: dict = {
        "anchor": name,
        "moment": moment,
        "traits": traits,
        "git_aspect": git_aspect_of(traits),
        "queries_text": "",
        "mode": None,
        "facets": [],
        # F216: the agent-state view. Unbound by default (headless/audit path —
        # every read returns the error values); live callers override with a
        # session-bound AgentView (warden_agent.make_agent).
        "agent": wa.unbound(),
        # F217: the judgment verb — blocking, cached, fail-silent.
        "ask_oracle": wa.ask_oracle,
    }
    # audit-q cooperative post-moment: the freshly-built queries file is the input.
    if moment.endswith(":audit-q"):
        q = anchor_root / f"{name} Track" / f"{name} queries.md"
        if q.is_file():
            fields["queries_text"] = q.read_text(encoding="utf-8")
    fields.update(overrides)
    return types.SimpleNamespace(**fields)


# ── declarative guard evaluation ────────────────────────────────────────────

def _ctx_value(ctx, key):
    return {"git-aspect": getattr(ctx, "git_aspect", None),
            "mode": getattr(ctx, "mode", None),
            "trait": getattr(ctx, "traits", []),
            "facet": getattr(ctx, "facets", [])}.get(key)


def eval_guard(guard: dict, ctx) -> bool:
    """A declarative {key, op, value} guard against ctx (F210 fixed vocabulary)."""
    actual = _ctx_value(ctx, guard["key"])
    op, value = guard["op"], guard["value"]
    if op == "eq":
        return actual == value
    if op == "in":
        return actual in (value if isinstance(value, (list, tuple, set)) else [value])
    if op == "has":
        return value in (actual or [])
    return False


def _rule_traits(ir: dict, rule_id: str) -> list[str]:
    return [t for t, ids in ir.get("traits", {}).items() if rule_id in ids]


def is_active(ir: dict, rule_id: str, anchor_traits) -> bool:
    """Active iff some trait that keys the rule is in the anchor's trait set."""
    keying = _rule_traits(ir, rule_id)
    return any(t in anchor_traits for t in keying)


# ── fire ────────────────────────────────────────────────────────────────────

def fire(ir: dict, module, moment: str, ctx, anchor_traits) -> list[str]:
    """Run the rules keyed at `moment` and active for the anchor; return steers.
    Rules on any other moment are not in the bucket and never execute."""
    steers: list[str] = []
    for rule_id in ir.get("moments", {}).get(moment, []):
        row = ir["rules"][rule_id]
        if not is_active(ir, rule_id, anchor_traits):
            continue
        # F217: a turn-bearing rule needs a bound session (rungs R1–R3);
        # at R4 the turn view is unresolvable and the rule is skipped wholesale.
        if row.get("turn_bearing") and not getattr(
                getattr(ctx, "agent", None), "is_bound", False):
            continue
        if not all(eval_guard(g, ctx) for g in row.get("guards", [])):
            continue
        gp = row.get("guard_py")
        if gp and module is not None and not getattr(module, gp)(ctx):
            continue
        if row.get("body_py") and module is not None:
            out = getattr(module, row["body_py"])(ctx)
            if out:
                steers.extend(out if isinstance(out, list) else [out])
        elif row.get("action"):
            act = row["action"]
            if act.get("kind") in ("tell", "deny"):
                steers.append(act.get("text") or act.get("reason") or "")
    return steers


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="warden-fire",
        description="Fire a moment against a compiled anchor; print the steers.")
    ap.add_argument("--anchor-root", required=True, help="the anchor directory (holds .anchor)")
    ap.add_argument("--warden-dir", default=None, help="compiled dir (default: <anchor-root>/.warden)")
    ap.add_argument("--anchor", default=None, help="anchor/module name (default: sensed from .anchor)")
    ap.add_argument("--moment", required=True, help="the moment to fire, e.g. skill:post:audit-q")
    args = ap.parse_args(argv)

    root = Path(args.anchor_root).expanduser().resolve()
    name = args.anchor or anchor_name(root)
    wdir = Path(args.warden_dir).expanduser() if args.warden_dir else (root / ".warden")
    ir, module = load_compiled(wdir, name)
    ctx = build_ctx(root, args.moment)
    traits = read_anchor_traits(root)
    steers = fire(ir, module, args.moment, ctx, traits)
    for s in steers:
        print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
