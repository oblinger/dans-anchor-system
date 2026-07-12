#!/usr/bin/env python3
"""Regression test for warden_compile.py (F211 pilot — R-query-14).

Pins both halves of the dual output against the F211 § IR schema worked
example: (1) the IR row R-query-14 compiles to, and (2) the emitted module's
`body_R_query_14` reproducing today's `audit-q` autofire steer. Runnable
standalone (`python3 test_warden_compile.py`) — no test framework.
"""
import importlib.util
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]  # dans-anchor-system repo root
sys.path.insert(0, str(HERE))

import warden_compile as wc  # noqa: E402

FCT_QUERY = REPO / "facets" / "DAS Query.md"


def _compile_pilot(tmp: Path):
    text = FCT_QUERY.read_text(encoding="utf-8")
    rs = wc.parse_ruleset(text, "R-query", FCT_QUERY.name)
    assert rs is not None, "R-query ruleset not found in FCT Query.md"
    ir, module_src, stats = wc.compile_ruleset(rs, "query")
    mod_path = tmp / "rules_query.py"
    mod_path.write_text(module_src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("rules_query", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return ir, module_src, stats, mod


def test_ir_row_matches_worked_example(ir):
    """The R-query-14 IR row is exactly the F211 § IR schema worked example."""
    row = ir["rules"]["R-query-14"]
    # authored `when:: skill:post:audit-q` normalizes to skill:pre — v1 ships
    # skill:pre only, an authored post is treated as pre (F209 Q3); keying it
    # verbatim would orphan the rule (the dispatcher never fires skill:post).
    assert row["moment"] == "skill:pre:audit-q", row["moment"]
    assert row["phase"] == "pre", row["phase"]
    assert row["where"] is None, row["where"]
    assert row["guards"] == [], row["guards"]
    assert row["guard_py"] is None
    assert row["action"] is None
    assert row["body_py"] == "body_R_query_14", row["body_py"]
    # dispatch + activation indices
    assert ir["moments"]["skill:pre:audit-q"] == ["R-query-14"]
    assert ir["traits"]["query"] == ["R-query-14"] or "R-query-14" in ir["traits"]["query"]
    # the tier doc-rules are where-major (no runtime moment), fired on /audit doc
    assert "R-query-14" not in ir["doc_rules"]
    assert "R-query-13" in ir["doc_rules"]
    print("PASS  ir_row_matches_worked_example")


def test_tier_doc_rules_emitted(ir):
    """All 16 R-query rules compile; tier rows carry the right declarative action.
    (16th = R-query-16 banner-form rule, landed after R-query-15.)"""
    assert len(ir["rules"]) == 16, len(ir["rules"])
    assert len(ir["doc_rules"]) == 15, ir["doc_rules"]
    # a `check::`-ref rule → a check action delegating to the named primitive
    r02 = ir["rules"]["R-query-02"]
    assert r02["moment"] is None and r02["phase"] == "post"
    assert r02["action"] == {"kind": "check", "ref": "frontmatter_has", "args": ["description"]}, r02["action"]
    # a check with a regex arg keeps the whole tail as args
    r05 = ir["rules"]["R-query-05"]
    assert r05["action"]["kind"] == "check" and r05["action"]["ref"] == "regex_absent", r05["action"]
    # a `stated` rule with no checker → agent-judged
    assert ir["rules"]["R-query-06"]["action"] == {"kind": "judge"}, ir["rules"]["R-query-06"]
    # every doc-rule inherits the ruleset where-selector
    assert ir["rules"]["R-query-01"]["where"] == "file:{anchor}/**/* queries.md", ir["rules"]["R-query-01"]["where"]
    print("PASS  tier_doc_rules_emitted")


def test_emitted_body_fires_like_autofire(mod):
    """body_R_query_14 returns a mode-appropriate steer for a push/commit Q,
    and is silent when the queries file carries no such question — matching
    the behaviour of today's R-query-14 trigger(ctx) (the F212 oracle)."""
    fire = types.SimpleNamespace(
        queries_text="- **Q1** Should I commit and push this branch now?\n",
        git_aspect="Commit", anchor="Warden")
    out = mod.body_R_query_14(fire)
    assert out and "Do NOT ask" in out[0], out
    assert "commit now" in out[0], out[0]

    quiet = types.SimpleNamespace(
        queries_text="- **Q1** Which layout should the dispatch table use?\n",
        git_aspect="Commit", anchor="Warden")
    assert mod.body_R_query_14(quiet) == [], "fired on a non-commit question"

    # PR aspect steers to the PR policy, not a commit.
    pr = types.SimpleNamespace(
        queries_text="- **Q2** Should I push this?\n", git_aspect="PR", anchor="X")
    out_pr = mod.body_R_query_14(pr)
    assert out_pr and "PR" in out_pr[0], out_pr
    print("PASS  emitted_body_fires_like_autofire")


def test_corpus_compile():
    """Whole-vault corpus compile: every ruleset the scan index lists compiles
    into one combined IR + a module that imports cleanly (the corpus-scale
    collision-hardening check)."""
    import importlib.util
    import warden_scan  # noqa
    files, seen, _ = warden_scan.build_index(str(REPO), {}, {}, rescan=True)
    index = {"root": str(REPO), "files": files, "seen": seen}
    ir, module_src, stats = wc.compile_corpus(REPO, index, "all")
    assert stats["rules"] > 100, stats               # the vault has hundreds of rules
    assert "R-query-14" in ir["rules"], "pilot rule missing from corpus IR"
    assert ir["rules"]["R-query-14"]["moment"] == "skill:pre:audit-q"
    assert "R-query-14" in ir["moments"]["skill:pre:audit-q"]
    # no orphaned moments (F209): every moment key the corpus compiles to must
    # be reachable from some hook event the live dispatcher emits
    # (warden_hook.event_to_moments) — an unreachable key is a rule that can
    # never fire. This is what caught skill:post:audit-q pre-normalization.
    reachable = ("tool:pre", "tool:post", "skill:pre", "session:start",
                 "session:stop", "session:compact", "prompt:submit",
                 "prompt:stop", "write:", "read:", "git:", "timer:")
    orphans = [m for m in ir["moments"] if not m.startswith(reachable)]
    assert not orphans, f"moment keys unreachable from the live dispatcher: {orphans}"
    # F232 A1: the fenced example ruleset (R-sample in FCT Ruleset) must NOT
    # compile into the corpus — it is shown grammar, not live rules. (R-wp,
    # first suspected a phantom, turned out to be a REAL ruleset swallowed by
    # an unclosed fence in FCT WP.md — fence repaired, so it must be present.)
    phantoms = [r for r in ir["rules"] if r.startswith("R-sample-")]
    assert not phantoms, f"fenced example rules leaked into the IR: {phantoms}"
    assert "sample" not in ir["traits"], "phantom trait 'sample' keyed in the IR"
    assert "R-wp-01" in ir["rules"], "real R-wp lost — FCT WP.md fence broken again?"
    # F219: the wiring snapshot is stamped — declared anchor traits + implicit base
    assert "anchor-base" in ir.get("declared_traits", []), ir.get("declared_traits")
    # the emitted corpus module must import — proves no cross-ruleset name collision
    with tempfile.TemporaryDirectory() as td:
        mp = Path(td) / "rules_all.py"
        mp.write_text(module_src, encoding="utf-8")
        spec = importlib.util.spec_from_file_location("rules_all", mp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert callable(getattr(mod, "body_R_query_14")), "pilot body not in corpus module"
        _check_trait_reachability_rule(mod, Path(td))
    print(f"PASS  corpus_compile ({stats['rules']} rules, {stats['moments']} moment(s))")


def _check_trait_reachability_rule(mod, tmp: Path):
    """F219 fixture: R-warden-dev-02 fires on a moment-rule trait no anchor
    declares (dead wiring), stays silent on a correctly-wired catalog, and
    exempts the hermetic warden-selftest fixture trait."""
    import json
    import os
    import types
    body = getattr(mod, "body_R_warden_dev_02")
    home = tmp / "f219-home"
    home.mkdir()
    os.environ["WARDEN_HOME"] = str(home)
    try:
        base = {"moments": {"session:start": ["R-x-01"]},
                "rules": {"R-x-01": {}},
                "traits": {"x": ["R-x-01"], "docsonly": ["R-d-01"]}}
        # dead wiring: trait `x` keys a moment rule, no anchor declares it
        (home / "rules-ir.json").write_text(
            json.dumps({**base, "declared_traits": ["anchor-base"]}), encoding="utf-8")
        out = body(types.SimpleNamespace())
        assert out and "dead wiring" in out[0] and "x" in out[0], out
        assert "docsonly" not in out[0], "doc-only trait wrongly flagged"
        # correctly wired → silent
        (home / "rules-ir.json").write_text(
            json.dumps({**base, "declared_traits": ["anchor-base", "x"]}), encoding="utf-8")
        assert body(types.SimpleNamespace()) == [], "fired on a wired catalog"
        # the hermetic test-fixture trait is exempt
        (home / "rules-ir.json").write_text(
            json.dumps({"moments": {"m": ["R-warden-selftest-01"]},
                        "rules": {}, "traits": {"warden-selftest": ["R-warden-selftest-01"]},
                        "declared_traits": ["anchor-base"]}), encoding="utf-8")
        assert body(types.SimpleNamespace()) == [], "selftest trait not exempt"
    finally:
        os.environ.pop("WARDEN_HOME", None)
    print("PASS  trait_reachability_rule (F219)")


BACKTICK_FIXTURE = """\
# RULESET R-tick-fx

where:: `file:{ANCHOR}/**/*.md`
description:: F172 backtick-form fixture

### RULE R-tick-fx-01 — backticked rule-level where (checked)

where:: `file:{ANCHOR}/**/* PRD.md`
check:: frontmatter_has description

### RULE R-tick-fx-02 — bare legacy where (checked)

where:: file:{ANCHOR}/**/* Backlog.md
check:: frontmatter_has description

### RULE R-tick-fx-03 — prose where with inline code spans (stated)

where:: every authored doc — any `.md` we own, with a `# ` H1
"""


def test_backticked_where():
    """F172: `` where:: `<expr>` `` (whole-expression backtick wrap) parses to
    the same selector as the bare form; prose values with INTERIOR code spans
    are never mis-stripped."""
    assert wc.strip_ticks("`file:{ANCHOR}/**/*.md`") == "file:{ANCHOR}/**/*.md"
    assert wc.strip_ticks("file:{ANCHOR}/**/*.md") == "file:{ANCHOR}/**/*.md"
    assert wc.strip_ticks("`always`") == "always"
    prose = "any `.md` we own, with a `# ` H1"
    assert wc.strip_ticks(prose) == prose, "interior code spans mis-stripped"
    rs = wc.parse_ruleset(BACKTICK_FIXTURE, "R-tick-fx", "fixture")
    assert rs is not None
    assert rs["where"] == "file:{ANCHOR}/**/*.md", rs["where"]
    by_id = {r["id"]: r for r in rs["rules"]}
    assert by_id["R-tick-fx-01"]["where"] == "file:{ANCHOR}/**/* PRD.md"
    assert by_id["R-tick-fx-02"]["where"] == "file:{ANCHOR}/**/* Backlog.md"
    assert by_id["R-tick-fx-03"]["where"].startswith("every authored doc"), \
        by_id["R-tick-fx-03"]["where"]
    print("PASS  backticked_where (F172)")


FIELD_STYLE_FIXTURE = """\
# RULESET R-field-fx
where:: `**/CLAUDE.md`
description:: Audit 2026-07-12 W1 fixture — a paren-less RULE heading in the documented field style.

### RULE R-field-fx-01 — File sits at the anchor root
description:: A CLAUDE.md file must live at the anchor folder root.
when:: write:markdown
if:: `file.path != anchor.root.rstrip('/') + '/CLAUDE.md'`
This CLAUDE.md is not at the anchor root.
"""


def test_paren_less_rule_heading():
    """Audit 2026-07-12 W1: a `### RULE R-... — <title>` heading with NO trailing `(...)`
    (the documented field-style form used by e.g. R-fct-claude-01) used to be
    silently dropped from `rule_idxs` — it now parses, and its `when::`/`if::`
    body fields wire a real when-rule with an intact moment + guard."""
    rs = wc.parse_ruleset(FIELD_STYLE_FIXTURE, "R-field-fx", "fixture")
    assert rs is not None
    ids = [r["id"] for r in rs["rules"]]
    assert ids == ["R-field-fx-01"], ids
    rule = rs["rules"][0]
    assert rule["paren"] == "", rule["paren"]
    assert rule["tier"] is None, rule["tier"]
    assert rule["when"] == "write:markdown", rule["when"]
    assert rule["ifs"] == ["file.path != anchor.root.rstrip('/') + '/CLAUDE.md'"], rule["ifs"]
    ir, _src, _stats = wc.compile_ruleset(rs, "field-fx")
    row = ir["rules"]["R-field-fx-01"]
    assert row["moment"] == "write:markdown", row["moment"]
    assert row["phase"] == "post", row["phase"]
    assert row["guard_py"] == "guard_R_field_fx_01", row["guard_py"]
    assert ir["moments"]["write:markdown"] == ["R-field-fx-01"]
    assert "R-field-fx-01" not in ir["doc_rules"]
    print("PASS  paren_less_rule_heading (Audit 2026-07-12 W1)")


def test_malformed_rule_heading_warns():
    """Audit 2026-07-12 W1: a heading that starts a RULE but fails the strict grammar
    (no `— name` separator) warns on stderr instead of silently vanishing
    from the compiled ruleset."""
    import contextlib
    import io
    bad = (
        "# RULESET R-bad\n\n"
        "### RULE R-bad-01 no dash separator at all\n\nx.\n\n"
        "### RULE R-bad-02 — a real one\n\nwhen:: write:markdown\n"
    )
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rs = wc.parse_ruleset(bad, "R-bad", "bad.md")
    assert rs is not None
    ids = [r["id"] for r in rs["rules"]]
    assert ids == ["R-bad-02"], ids
    assert "malformed RULE heading" in err.getvalue(), err.getvalue()
    print("PASS  malformed_rule_heading_warns (Audit 2026-07-12 W1)")


def test_include_flatten():
    """F218 follow-through: `include::` composition flattens into the trait
    index — an umbrella's trait keys its own rules plus every included
    ruleset's rules, transitively, with no cross-umbrella leak. (Before this,
    every umbrella trait keyed zero rules — a documented no-op.)"""
    import warden_scan  # noqa
    files, seen, _ = warden_scan.build_index(str(REPO), {}, {}, rescan=True)
    ir, _, _ = wc.compile_corpus(
        REPO, {"root": str(REPO), "files": files, "seen": seen}, "all")
    t = ir["traits"]
    assert "R-single-source-of-truth-01" in t["arch"], t.get("arch")
    assert "R-ownership-03" in t["arch"]
    assert len(t["arch"]) == 15, len(t["arch"])
    assert "R-design-gate-01" in t["process"] and len(t["process"]) == 14
    assert "R-design-gate-01" not in t["arch"], "cross-umbrella leak"
    assert "R-diagram-geometry-01" in t["diagram"], "pre-existing umbrella not flattened"
    # include-target parsing: embedded form + bare form
    assert wc._include_target("FCT Brief#RULESET R-brief") == "R-brief"
    assert wc._include_target("R-arch") == "R-arch"
    print("PASS  include_flatten (F218)")


FENCED_DOC = '''# Spec

The grammar, shown as an example (must never compile):

```
# RULESET R-phantom
### RULE R-phantom-01 — never live (checked)
```

# RULESET R-live

where:: `*.md`

### RULE R-live-01 — real rule (checked)

An example shown inside the rule body:

```
### RULE R-live-99 — fenced example (checked)
when:: tool:pre:Bash
```

Body prose after the example.
'''


def test_fenced_sentinels_ignored():
    """F232 A1: RULESET/RULE sentinels and `field::` lines inside ``` fences are
    shown examples — the scan must not index them, the parser must not compile
    them, and a fenced `when::` must not re-key the enclosing live rule."""
    import warden_scan  # noqa
    assert warden_scan.extract_ruleset_names(FENCED_DOC) == ["R-live"]
    assert wc.parse_ruleset(FENCED_DOC, "R-phantom", "t.md") is None
    rs = wc.parse_ruleset(FENCED_DOC, "R-live", "t.md")
    assert rs is not None
    ids = [r["id"] for r in rs["rules"]]
    assert ids == ["R-live-01"], ids
    r = rs["rules"][0]
    assert r["when"] is None, f"fenced when:: re-keyed the live rule: {r['when']}"
    assert r["tier"] == "checked", r["tier"]
    print("PASS  fenced_sentinels_ignored (F232 A1)")


def test_duplicate_rule_id_first_wins():
    """F232 A2: a redefined rule id keeps the FIRST definition in both compile
    paths (single-ruleset mode used to silently last-win) and warns on stderr."""
    import contextlib
    import io
    dup = (
        "# RULESET R-dup\n\n"
        "### RULE R-dup-01 — the first (checked)\n\nfirst body.\n\n"
        "### RULE R-dup-01 — the second (stated)\n\nsecond body.\n"
    )
    rs = wc.parse_ruleset(dup, "R-dup", "dup.md")
    assert rs is not None and len(rs["rules"]) == 2
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        ir, _src, _stats = wc.compile_ruleset(rs, "dup")
    assert list(ir["rules"]) == ["R-dup-01"]
    assert ir["rules"]["R-dup-01"]["tier"] == "checked", "first definition must win"
    assert "duplicate rule id R-dup-01" in err.getvalue(), err.getvalue()

    # corpus mode: same id in two files — first (scan-order) wins, with a
    # warning naming both sources; a duplicate ruleset name also warns.
    import warden_scan  # noqa
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "a.md").write_text(
            "# RULESET R-one\n\n### RULE R-one-01 — from a (checked)\n",
            encoding="utf-8")
        (root / "b.md").write_text(
            "# RULESET R-two\n\n### RULE R-one-01 — from b (stated)\n",
            encoding="utf-8")
        files, seen, _ = warden_scan.build_index(str(root), {}, {}, rescan=True)
        index = {"root": str(root), "files": files, "seen": seen}
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            ir, _src, _stats = wc.compile_corpus(root, index, "all")
        assert ir["rules"]["R-one-01"]["tier"] == "checked", "first file must win"
        assert "duplicate rule id R-one-01" in err.getvalue(), err.getvalue()
    print("PASS  duplicate_rule_id_first_wins (F232 A2)")


def test_compile_robustness_batch():
    """F232 A3–A8 + D2: moment validation, empty-when warning, dual entry
    defs wired, fence discipline, bare include::, unknown-include warning,
    installed-surface deliverability helpers."""
    import contextlib
    import importlib.machinery
    import importlib.util
    import io
    import types

    # A3 — trailing comment stripped from the moment key; typo'd class warns.
    assert wc.canonical_moment("tool:pre:Bash  # a note")[0] == "tool:pre:Bash"
    doc = (
        "# RULESET R-rb\n\n"
        "### RULE R-rb-01 — typo class (when:: toool:pre:Bash)\n\nx.\n\n"
        "### RULE R-rb-02 — empty when (when::)\n\nx.\n"
    )
    rs = wc.parse_ruleset(doc, "R-rb", "rb.md")
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        wc.compile_ruleset(rs, "rb")
    assert "unknown moment class 'toool'" in err.getvalue(), err.getvalue()
    # A8 — empty when:: warns instead of silently reclassifying.
    assert "R-rb-02: empty when::" in err.getvalue(), err.getvalue()

    # A4 — dual `def guard` + `def body`: BOTH wired, both emitted, preamble
    # shared into each, no def leaking to module scope unrenamed.
    dual = (
        "# RULESET R-du\n\n"
        "### RULE R-du-01 — dual defs (when:: tool:pre:Bash)\n\n"
        "```python\n"
        "N = 3\n"
        "def guard(ctx):\n"
        "    return N > 2\n"
        "def body(ctx):\n"
        "    return ['x' * N]\n"
        "```\n"
    )
    rs = wc.parse_ruleset(dual, "R-du", "du.md")
    rule = rs["rules"][0]
    assert rule["py_kinds"] == ["guard", "body"], rule["py_kinds"]
    ir, src, _stats = wc.compile_ruleset(rs, "du")
    row = ir["rules"]["R-du-01"]
    assert row["guard_py"] == "guard_R_du_01" and row["body_py"] == "body_R_du_01", row
    ns_mod = types.ModuleType("rules_du")
    exec(compile(src, "rules_du.py", "exec"), ns_mod.__dict__)
    assert ns_mod.guard_R_du_01(None) is True
    assert ns_mod.body_R_du_01(None) == ["xxx"]
    assert not hasattr(ns_mod, "guard") and not hasattr(ns_mod, "body"), \
        "an entry def leaked unrenamed to module scope"

    # A5 — multiple ```python fences: the entry-def-bearing block wins, warned.
    multi = (
        "# RULESET R-mf\n\n"
        "### RULE R-mf-01 — illustration first (when:: tool:pre:Bash)\n\n"
        "```python\n"
        "print('just an illustration')\n"
        "```\n\n"
        "```python\n"
        "def body(ctx):\n"
        "    return ['real']\n"
        "```\n"
    )
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rs = wc.parse_ruleset(multi, "R-mf", "mf.md")
    assert "2 ```python fences" in err.getvalue(), err.getvalue()
    assert "def body" in rs["rules"][0]["py_src"], "real block was displaced"

    # A6 — bare-name include:: is honoured.
    bare = "# RULESET R-um\n\ninclude:: R-a, R-b\n"
    rs = wc.parse_ruleset(bare, "R-um", "um.md")
    assert rs["includes"] == ["R-a", "R-b"], rs["includes"]

    # A7 — an include target resolving to no scanned ruleset warns.
    import warden_scan  # noqa
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "u.md").write_text(
            "# RULESET R-umb\n\ninclude:: [[R-nonexistent]]\n\n"
            "### RULE R-umb-01 — own rule (checked)\n", encoding="utf-8")
        files, seen, _ = warden_scan.build_index(str(root), {}, {}, rescan=True)
        index = {"root": str(root), "files": files, "seen": seen}
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            wc.compile_corpus(root, index, "all")
        assert "unknown ruleset 'R-nonexistent'" in err.getvalue(), err.getvalue()

    # D2 — installed-surface deliverability helpers (CLI module).
    loader = importlib.machinery.SourceFileLoader(
        "warden_cli", str(HERE / "warden"))
    spec = importlib.util.spec_from_loader("warden_cli", loader)
    cli = importlib.util.module_from_spec(spec)
    loader.exec_module(cli)
    settings = {"hooks": {
        "SessionStart": [{"hooks": [{"command": "warden-rs hook"}]}],
        "UserPromptSubmit": [{"hooks": [{"command": "warden-rs hook"}]}],
        "PreToolUse": [
            {"matcher": "Skill", "hooks": [{"command": "warden-rs hook"}]},
            {"matcher": "Bash|Edit|Write", "hooks": [{"command": "warden-rs hook"}]}],
        "PostToolUse": [
            {"matcher": "Write|Edit", "hooks": [{"command": "warden-rs hook"}]}],
        "Stop": [{"hooks": [{"command": "other-tool"}]}],   # NOT a warden entry
    }}
    ev = cli._installed_warden_events(settings)
    assert "Stop" not in ev, ev
    for m, want in [("tool:pre:Bash", True), ("skill:pre:audit-q", True),
                    ("write:markdown", True), ("session:start", True),
                    ("prompt:submit", True), ("tool:pre:WebFetch", False),
                    ("session:stop", False), ("git:commit", False)]:
        assert cli._moment_deliverable(m, ev) is want, (m, want)
    print("PASS  compile_robustness_batch (F232 A3–A8, D2)")


def test_recompile_cache():
    """The compiled IR records the scan-index hash as its cache key;
    `cached_source_hash` round-trips it, and the key changes when a ruleset
    changes — so an unchanged corpus is a cache hit (recompile skipped)."""
    import warden_scan  # noqa
    files, seen, _ = warden_scan.build_index(str(REPO), {}, {}, rescan=True)
    h1 = warden_scan.index_hash(files)
    index = {"root": str(REPO), "files": files, "seen": seen}
    ir, module_src, _ = wc.compile_corpus(REPO, index, "all", h1)
    assert ir["source_hash"] == h1, "IR did not record the cache key"

    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        wc._write_artifacts(out, "all", ir, module_src)
        assert wc.cached_source_hash(out) == h1, "cache key not round-tripped"
        # F232 B5: atomic writes leave no temp files; module lands before IR.
        assert not list(out.glob("*.tmp")), "temp artifact left behind"
        assert (out / "rules_all.py").stat().st_mtime_ns \
            <= (out / "rules-ir.json").stat().st_mtime_ns, "IR written before module"
        # a hash over a mutated ruleset set differs → cache would miss
        mutated = [dict(f) for f in files]
        mutated[0] = dict(mutated[0], hash="deadbeef")
        assert warden_scan.index_hash(mutated) != h1, "cache key insensitive to change"
    print("PASS  recompile_cache")


def test_stats(stats):
    assert stats["when_rules"] == 1, stats
    assert stats["py_rules"] == 1, stats
    assert stats["doc_rules"] == 15, stats
    print("PASS  stats")


def main():
    with tempfile.TemporaryDirectory() as td:
        ir, _module_src, stats, mod = _compile_pilot(Path(td))
        test_ir_row_matches_worked_example(ir)
        test_tier_doc_rules_emitted(ir)
        test_emitted_body_fires_like_autofire(mod)
        test_stats(stats)
    test_corpus_compile()
    test_backticked_where()
    test_paren_less_rule_heading()
    test_malformed_rule_heading_warns()
    test_include_flatten()
    test_fenced_sentinels_ignored()
    test_duplicate_rule_id_first_wins()
    test_compile_robustness_batch()
    test_recompile_cache()
    print("\nall warden_compile tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
