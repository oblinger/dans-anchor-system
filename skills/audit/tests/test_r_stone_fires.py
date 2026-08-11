"""Regression tests for T164 — the four checked `R-stone` rules must be able to FAIL.

The live corpus is 8 stone groups across 2 kinds and every one of them conforms,
so a green sweep over it is not evidence that these rules work — it is exactly
the vacuous-zero shape the Stone facet was written in the middle of. This module
supplies the missing half: a deliberately malformed group carrying one defect per
rule, beside a well-formed twin, so each rule is observed to fire on the first and
stay quiet on the second.

Three separate things had to be true before a single stone rule ran, and each
failed silently on its own:

  1. the `check::` had to resolve to a name in `CHECKERS` (an unresolvable ref is
     not an error — `_needs_judgment` is a membership test, so it quietly
     promotes the rule to billed agent judgment);
  2. the ruleset had to exist as `rulesets/R-stone.md` — the plan builder resolves
     a slug to that path, and `R-stone` was embedded in `facets/DAS Stone.md`, the
     pre-2026-07-13 form, so `include:: [[R-stone]]` resolved to nothing;
  3. it had to be reachable from `R-anchor`, the umbrella `/audit anchor` actually
     resolves — `R-facet` names it but sits outside that closure.

With (1) and (2) fixed and (3) not, the sweep still produced zero stone verdicts
and no error anywhere. `test_rules_reach_a_real_plan` is the guard for (3): it
asserts a stone rule appears in a built plan, which is the only observation that
distinguishes "armed" from "reads as armed".

Run with:  python3 -m pytest ~/.claude/skills/audit/tests/test_r_stone_fires.py
"""

import importlib.util
import pathlib
import sys

import pytest

_AUDIT_PLAN_PATH = pathlib.Path(__file__).parent.parent / "scripts" / "audit-plan.py"
_spec = importlib.util.spec_from_file_location("audit_plan", _AUDIT_PLAN_PATH)
assert _spec is not None and _spec.loader is not None
ap = importlib.util.module_from_spec(_spec)
sys.modules["audit_plan"] = ap
_spec.loader.exec_module(ap)


RULES = {
    "R-stone-01": "stone_group_located",
    "R-stone-02": "stone_members_numbered",
    "R-stone-04": "stone_header_by_target",
    "R-stone-06": "stone_keys_above_prose",
}


def _w(p: pathlib.Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


@pytest.fixture
def good(tmp_path):
    """A conformant rock group — nothing here may draw a finding."""
    a = tmp_path / "OK"
    _w(a / ".anchor", "slug: OK\n")
    _w(a / "OK Track/OK Rocks/OK R0001.md",
       "line:: a well-formed rock\n\n# A well-formed rock\nBody prose.\n")
    _w(a / "OK Track/OK Rock.md",
       "# OK Rock\n\n[[OK Rock|-OK-]]\n\n[[OK R0001|OK:]] a well-formed rock\n")
    return a


@pytest.fixture
def bad(tmp_path):
    """One deliberate defect per checked rule, each in its own file."""
    a = tmp_path / "BAD"
    _w(a / ".anchor", "slug: BAD\n")
    # R-stone-01: filed under Design rather than Track, and no control file.
    _w(a / "BAD Design/BAD Pebbles/BAD P0001.md",
       "line:: filed in the wrong facet\n\n# Misfiled\nBody.\n")
    # R-stone-02: an abbreviation-named member — the superseded F309 shape.
    _w(a / "BAD Track/BAD Rocks/BAD LEX.md",
       "line:: named by abbreviation\n\n# Life expectancy\nBody.\n")
    # R-stone-06: a key below the prose.
    _w(a / "BAD Track/BAD Rocks/BAD R0002.md",
       "# Keys in the wrong place\nProse starts immediately.\n\n"
       "line:: this key is below the body\n")
    # R-stone-04: rendering disagreeing with the target, in both directions.
    _w(a / "BAD Track/BAD Rock.md",
       "# BAD Rock\n\n"
       "[[BAD R0002|-BAD-]] renders as a header, targets a stone\n"
       "[[DAS Stone|BAD:]] renders as a stone, targets a spec page\n"
       "[[BAD Rock]] targets the control file but renders bare\n"
       "UNCOMMITTED\n"
       "[[BAD R0002|BAD:]] this one is fine\n")
    return a


def _verdicts(anchor: pathlib.Path, rule: str):
    """Every verdict `rule` gives over one fixture anchor's stone files."""
    fn = ap.CHECKERS[RULES[rule]]
    out = []
    for group in sorted(p for p in anchor.rglob("*") if p.is_dir()
                        and any(p.name.endswith(s) for s in ap._stone_kind_suffixes())):
        for f in sorted(group.glob("*.md")):
            out.append(fn(f, ap._stone_owner(group), None))
    return out


@pytest.mark.parametrize("rule", sorted(RULES))
def test_rule_fires_on_a_malformed_group(bad, rule):
    """The point of the module: each rule must be observed to FAIL something."""
    fails = [m for v, m in _verdicts(bad, rule) if v == "fail"]
    assert fails, (f"{rule} never fired on a group built to violate it — a rule "
                   "that cannot fail is not coverage, it is a coverage claim")


@pytest.mark.parametrize("rule", sorted(RULES))
def test_rule_is_quiet_on_a_conformant_group(good, rule):
    """The other half — a rule that fails everything is equally useless."""
    fails = [m for v, m in _verdicts(good, rule) if v == "fail"]
    assert not fails, f"{rule} false-fired on a conformant group: {fails}"


def test_kind_config_is_readable():
    """Every per-kind fact is read from `DAS Stone Kinds.json`; nothing is
    hardcoded. If that file cannot be read the checkers must ERROR, never pass —
    an instrument that cannot see its subject has verified nothing."""
    kinds = ap._stone_kinds()
    assert kinds, f"no kinds readable from {ap._STONE_KINDS_PATH}"
    for cfg in kinds.values():
        assert {"folder", "control", "prefix"} <= set(cfg)


_STONE_SYMBOLS = [n for n in dir(ap)
                  if n.startswith(("_stone", "chk_stone")) and callable(getattr(ap, n))]


def test_checkers_name_no_kind():
    """The generalisation is the whole point: `_rocks_gate` hardcodes ' Rocks'
    and so passes silently on every pebble group. No stone symbol may *behave*
    differently for a named kind — a new kind should need config, not code.

    Docstrings and comments are stripped before the search, deliberately: this
    section's prose explains at length WHY it is kind-generic, and a test that
    forbade the words would forbid the explanation. Only executable code counts.
    """
    import ast
    import inspect

    for name in _STONE_SYMBOLS:
        src = inspect.getsource(getattr(ap, name))
        tree = ast.parse(inspect.cleandoc(src) if src.startswith(" ") else src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef, ast.Module)):
                body = node.body
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    node.body = body[1:] or [ast.Pass()]
        code = ast.unparse(tree)
        for kind in ("pebble", "rock", "Pebbles", "Rocks"):
            assert kind not in code, (
                f"{kind!r} is hardcoded in {name} — read it from "
                "DAS Stone Kinds.json instead")


def test_rules_reach_a_real_plan(tmp_path):
    """Guard for failure (3): the rules must be REACHABLE from `R-anchor`.

    Everything above would pass with `R-stone` absent from every umbrella — the
    checkers work in isolation and the audit still never calls them. This asserts
    the wiring itself, which is the part that failed silently three times."""
    anchor = tmp_path / "REACH"
    _w(anchor / ".anchor", "slug: REACH\n")
    _w(anchor / "REACH Track/REACH Rocks/REACH R0001.md", "line:: x\n\n# x\nBody.\n")
    _w(anchor / "REACH Track/REACH Rock.md",
       "# REACH Rock\n\n[[REACH Rock|-REACH-]]\n\n[[REACH R0001|REACH:]] x\n")
    plan = ap.plan_one(anchor, mode="anchor", cdir=None, warnings=[])
    named = {r["id"] for g in plan["groupings"] for r in g["rules"]}
    assert any(r.startswith("R-stone-") for r in named), (
        "no R-stone rule reached the plan — the ruleset is not armed, however "
        "many umbrellas name it and however green the sweep looks")
