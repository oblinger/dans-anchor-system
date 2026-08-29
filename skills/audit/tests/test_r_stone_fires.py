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


def _header_line(slug: str, target: str, kind: str = "rock") -> str:
    """Render a control-file header the way the DAS kind table declares it.

    **Built from config, never spelled out.** These fixtures used to hardcode
    `[[OK Rock|-OK-]]` — the dashes-INSIDE form, which was tried, reverted on
    2026-08-17 when HookAnchor f180d008c retired the bare-dash electric
    grammar, and replaced by dashes-outside. The declaration moved; the
    fixture did not, so the group labelled *conformant* stopped conforming and
    `R-stone-04`'s no-false-fire half was asserting against a shape the system
    no longer uses. Found 2026-08-28 while moving the declarations out of JSON
    — the third copy of the same facts to drift, and the reason this one is
    derived instead of written."""
    cfg = ap._stone_kinds()[kind]
    alias = cfg["header_alias"].replace("{slug}", slug)
    return cfg["header_line"].replace("{link}", f"[[{target}|{alias}]]")


@pytest.fixture
def good(tmp_path):
    """A conformant rock group — nothing here may draw a finding."""
    a = tmp_path / "OK"
    _w(a / ".anchor", "slug: OK\n")
    _w(a / "OK Track/OK Rocks/OK R0001.md",
       "line:: a well-formed rock\n\n# A well-formed rock\nBody prose.\n")
    _w(a / "OK Track/OK Rock.md",
       f"# OK Rock\n\n{_header_line('OK', 'OK Rock')}\n\n"
       "[[OK R0001|OK:]] a well-formed rock\n")
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
       f"{_header_line('BAD', 'BAD R0002')} renders as a header, "
       "targets a stone\n"
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
    """Every per-kind fact is read from the DAS kind table (markdown, located
    by `stone_kinds_doc` in F080 config); nothing is hardcoded. If that table
    cannot be read the checkers must ERROR, never pass — an instrument that
    cannot see its subject has verified nothing."""
    kinds = ap._stone_kinds()
    assert kinds, f"no kinds readable from {ap._stone_kinds_path()}"
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
                "the DAS kind table instead")


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


def test_stone_dispatch_linked_fires_beside_a_linked_twin(tmp_path):
    """T603 / R-stone-07 — an unlinked group fires, a linked twin stays quiet.

    The standing R-stone evidence rule: a green sweep over the live corpus is
    not evidence, because a rule that selects nothing is also green. So the
    fixture builds BOTH groups in one anchor and asserts the pair — the linked
    one silent, the unlinked one failing — which is the only shape that
    distinguishes "the rule works" from "the rule never ran".

    The pair is not decoration. The live victim was exactly this asymmetry:
    `SV Sleepers` was unreachable by navigation and nothing said so, while the
    ROCKS half of the identical defect fired in the same sweep on the same
    anchor. R-stone had generalised six of R-rocks' thirteen rules and stopped.
    """
    anchor = tmp_path / "DUO"
    _w(anchor / ".anchor", "slug: DUO\n")

    # A linked rock group.
    _w(anchor / "DUO Track/DUO Rocks/DUO R0001.md", "line:: x\n\n# x\nBody.\n")
    _w(anchor / "DUO Track/DUO Rock.md",
       "# DUO Rock\n\n[[DUO Rock|-DUO-]]\n\n[[DUO R0001|DUO:]] x\n")
    # An UNLINKED pebble group, same anchor, same shape.
    _w(anchor / "DUO Track/DUO Pebbles/DUO P0001.md", "line:: y\n\n# y\nBody.\n")
    _w(anchor / "DUO Track/DUO Pebble.md",
       "# DUO Pebble\n\n[[DUO Pebble|-DUO-]]\n\n[[DUO P0001|DUO:]] y\n")

    # The Track page links only the rock group.
    track = anchor / "DUO Track/DUO Track.md"
    _w(track, "# DUO Track\n\n| -[[DUO Track]]- | |\n| --- | --- |\n"
              "| [[DUO Rocks]] | rocks |\n| ... | |\n")

    # A folder-scope rule is judged ONCE per group, on the group's spokesfile --
    # its first member -- not on the control file, which for most kinds sits
    # beside the folder rather than in it. `_stone_gate` passes anything else
    # with "judged once, on '<spokes>'", so aiming at the control file would
    # make this whole fixture green for the wrong reason.
    rock_ctl = anchor / "DUO Track/DUO Rocks/DUO R0001.md"
    peb_ctl = anchor / "DUO Track/DUO Pebbles/DUO P0001.md"

    v_rock, _ = ap.chk_stone_dispatch_linked(rock_ctl, anchor, None)
    v_peb, msg = ap.chk_stone_dispatch_linked(peb_ctl, anchor, None)

    assert v_rock == "pass", f"the LINKED group must stay quiet, got {v_rock}"
    assert v_peb == "fail", (
        "the UNLINKED group must fire — this is the exact silence that let "
        f"SV Sleepers go unreachable, got {v_peb}")
    assert "DUO Pebbles" in msg, f"the message must name the missing link: {msg}"

    # Now link it, and the finding must clear -- a rule that cannot be satisfied
    # is not a rule, it is a permanent complaint.
    _w(track, "# DUO Track\n\n| -[[DUO Track]]- | |\n| --- | --- |\n"
              "| [[DUO Rocks]] | rocks |\n| [[DUO Pebbles]] | pebbles |\n| ... | |\n")
    v_peb2, _ = ap.chk_stone_dispatch_linked(peb_ctl, anchor, None)
    assert v_peb2 == "pass", f"linking the group must clear the finding, got {v_peb2}"

    # A dispatch cell escapes its pipe; the alias form must satisfy it too.
    _w(track, "# DUO Track\n\n| -[[DUO Track]]- | |\n| --- | --- |\n"
              "| [[DUO Rocks]] | rocks |\n| [[DUO Pebbles\\|the pebbles]] | |\n| ... | |\n")
    v_peb3, _ = ap.chk_stone_dispatch_linked(peb_ctl, anchor, None)
    assert v_peb3 == "pass", f"a pipe-escaped alias link must satisfy it, got {v_peb3}"

    # The CONTROL FILE satisfies reachability too, and in this vault it is what
    # actually does: measured 2026-08-28, every non-rock Track page links
    # `[[{slug} Pebble]]` (singular) rather than the folder. Porting R-rocks-08's
    # folder-only predicate fired on 21 of 32 live groups -- a rule measuring a
    # convention rather than a defect. The control file is the better target
    # anyway: it is what a reader opens, and the folder is storage.
    _w(track, "# DUO Track\n\n| -[[DUO Track]]- | |\n| --- | --- |\n"
              "| [[DUO Rocks]] | rocks |\n| [[DUO Pebble]] | control file |\n| ... | |\n")
    v_peb4, _ = ap.chk_stone_dispatch_linked(peb_ctl, anchor, None)
    assert v_peb4 == "pass", f"a link to the control file must satisfy it, got {v_peb4}"

    # And neither present is still a finding -- the two accepted targets must
    # not add up to "anything mentioning the slug".
    _w(track, "# DUO Track\n\n| -[[DUO Track]]- | |\n| --- | --- |\n"
              "| [[DUO Rocks]] | rocks |\n| ... | |\n")
    v_peb5, _ = ap.chk_stone_dispatch_linked(peb_ctl, anchor, None)
    assert v_peb5 == "fail", f"neither target linked must still fire, got {v_peb5}"


def test_stone_ranking_rules_fire_beside_a_clean_twin(tmp_path):
    """T603 leg 2 / R-stone-08 + R-stone-09 — an unranked member warns, a dead
    line fails, and a fully-ranked twin in the same anchor stays quiet on both.

    Measured 2026-08-28 across all 32 live groups: zero findings from either
    predicate. That is the vacuous-green shape the R-stone evidence rule exists
    for, so this fixture is the rule's only evidence. It builds a BOOK group on
    purpose -- dated members, which the number regex cannot parse -- to pin that
    both rules see a member by its stem and never through the regex.
    """
    anchor = tmp_path / "PAIR"
    _w(anchor / ".anchor", "slug: PAIR\n")

    # The clean twin: a pebble group, every member ranked, every line live.
    _w(anchor / "PAIR Track/PAIR Pebbles/PAIR P0001.md", "line:: a\n\n# a\nBody.\n")
    _w(anchor / "PAIR Track/PAIR Pebbles/PAIR P0002.md", "line:: b\n\n# b\nBody.\n")
    _w(anchor / "PAIR Track/PAIR Pebble.md",
       "# PAIR Pebble\n\n-[[PAIR Pebble|PAIR]]-\n\n"
       "[[PAIR P0001|PAIR:]] a\n[[PAIR P0002|PAIR:]] b\n"
       "[[OTHER P0007|OTHER:]] a line propagated in from another anchor\n")
    # The defective group: a BOOK, dated members. One member the control file
    # never names; one control line naming a member that does not exist.
    _w(anchor / "PAIR Track/PAIR Book/PAIR 2026-08-01 first.md",
       "line:: first\n\n# first\nBody.\n")
    _w(anchor / "PAIR Track/PAIR Book/PAIR 2026-08-02 orphan.md",
       "line:: never ranked\n\n# orphan\nBody.\n")
    _w(anchor / "PAIR Track/PAIR Book/PAIR Book.md",
       "# PAIR Book\n\n-[[PAIR Book|PAIR]]-\n\n"
       "[[PAIR 2026-08-01 first|PAIR:]] first\n"
       "[[PAIR 2026-08-03 ghost|PAIR:]] a line whose file was never written\n")

    peb = anchor / "PAIR Track/PAIR Pebbles/PAIR P0001.md"
    # A container-named kind's spokesfile is its own folder page.
    book = anchor / "PAIR Track/PAIR Book/PAIR Book.md"

    for fn in (ap.chk_stone_member_ranked, ap.chk_stone_control_links_resolve):
        v, msg = fn(peb, anchor, None)
        assert v == "pass", f"{fn.__name__} must stay quiet on the clean twin: {v} {msg}"

    v, msg = ap.chk_stone_member_ranked(book, anchor, None)
    assert v == "warn", f"an unranked dated member must WARN, got {v}: {msg}"
    assert "PAIR 2026-08-02 orphan" in msg and "first" not in msg.split(":")[1], msg

    v, msg = ap.chk_stone_control_links_resolve(book, anchor, None)
    assert v == "fail", f"a dead control line must FAIL, got {v}: {msg}"
    assert "PAIR 2026-08-03 ghost" in msg, msg
    assert "2026-08-01" not in msg, f"the live line must not be reported: {msg}"

    # Fix both, and both must clear.
    _w(anchor / "PAIR Track/PAIR Book/PAIR Book.md",
       "# PAIR Book\n\n-[[PAIR Book|PAIR]]-\n\n"
       "[[PAIR 2026-08-01 first|PAIR:]] first\n"
       "[[PAIR 2026-08-02 orphan|PAIR:]] now ranked\n")
    for fn in (ap.chk_stone_member_ranked, ap.chk_stone_control_links_resolve):
        v, msg = fn(book, anchor, None)
        assert v == "pass", f"{fn.__name__} must clear once fixed: {v} {msg}"


def test_stone_single_per_kind_fires_beside_a_clean_twin(tmp_path):
    """T603 leg 3 / R-stone-10 — two groups of ONE kind fire; several kinds do
    not; a nested anchor's group of the same kind does not count.

    The last case is the one that would have bitten: `SV` encloses four pebble
    groups, three of them owned by nested anchors. A port that counted them
    would have failed the vault's heaviest Stone user for using the facet as
    designed.
    """
    # Clean: one anchor, three KINDS, one group each — the SV shape.
    ok = tmp_path / "OK"
    _w(ok / ".anchor", "slug: OK\n")
    for kind, ctl, m in (("Pebbles", "Pebble", "P0001"), ("Rocks", "Rock", "R0001"),
                         ("Sleepers", "Sleeper", "S0001")):
        _w(ok / f"OK Track/OK {kind}/OK {m}.md", "line:: x\n\n# x\nBody.\n")
        _w(ok / f"OK Track/OK {ctl}.md", f"# OK {ctl}\n\n-[[OK {ctl}|OK]]-\n\n[[OK {m}|OK:]] x\n")
    # And a NESTED project anchor with its own pebble group, which is its own.
    _w(ok / "sub/.anchor", "slug: SUB\n")
    _w(ok / "sub/SUB Track/SUB Pebbles/SUB P0001.md", "line:: y\n\n# y\nBody.\n")
    _w(ok / "sub/SUB Track/SUB Pebble.md", "# SUB Pebble\n\n-[[SUB Pebble|SUB]]-\n\n[[SUB P0001|SUB:]] y\n")

    for kind, m in (("Pebbles", "P0001"), ("Rocks", "R0001"), ("Sleepers", "S0001")):
        v, msg = ap.chk_stone_single_per_kind(ok / f"OK Track/OK {kind}/OK {m}.md", ok, None)
        assert v == "pass", f"one group per kind must pass ({kind}): {v} {msg}"
    v, msg = ap.chk_stone_single_per_kind(ok / "sub/SUB Track/SUB Pebbles/SUB P0001.md", ok / "sub", None)
    assert v == "pass", f"the nested anchor's own group must pass: {v} {msg}"

    # Defective: a second pebble group under the same anchor, filed elsewhere.
    bad = tmp_path / "BAD"
    _w(bad / ".anchor", "slug: BAD\n")
    _w(bad / "BAD Track/BAD Pebbles/BAD P0001.md", "line:: x\n\n# x\nBody.\n")
    _w(bad / "BAD Track/BAD Pebble.md", "# BAD Pebble\n\n-[[BAD Pebble|BAD]]-\n\n[[BAD P0001|BAD:]] x\n")
    _w(bad / "BAD Design/BAD Old Pebbles/BAD P0009.md", "line:: z\n\n# z\nBody.\n")
    v, msg = ap.chk_stone_single_per_kind(bad / "BAD Track/BAD Pebbles/BAD P0001.md", bad, None)
    assert v == "fail", f"two pebble groups under one anchor must FAIL, got {v}: {msg}"
    assert "BAD Old Pebbles" in msg and "BAD Pebbles" in msg, msg
