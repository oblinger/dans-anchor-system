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
REPO = HERE.parents[1]  # ob-skills repo root
sys.path.insert(0, str(HERE))

import warden_compile as wc  # noqa: E402

FCT_QUERY = REPO / "facets" / "FCT Track" / "FCT Query.md"


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
    assert row["moment"] == "skill:post:audit-q", row["moment"]
    assert row["phase"] == "post", row["phase"]
    assert row["where"] is None, row["where"]
    assert row["guards"] == [], row["guards"]
    assert row["guard_py"] is None
    assert row["action"] is None
    assert row["body_py"] == "body_R_query_14", row["body_py"]
    # dispatch + activation indices
    assert ir["moments"]["skill:post:audit-q"] == ["R-query-14"]
    assert ir["traits"]["query"] == ["R-query-14"] or "R-query-14" in ir["traits"]["query"]
    # the tier doc-rules are where-major (no runtime moment), fired on /audit doc
    assert "R-query-14" not in ir["doc_rules"]
    assert "R-query-13" in ir["doc_rules"]
    print("PASS  ir_row_matches_worked_example")


def test_tier_doc_rules_emitted(ir):
    """All 14 R-query rules compile; tier rows carry the right declarative action."""
    assert len(ir["rules"]) == 14, len(ir["rules"])
    assert len(ir["doc_rules"]) == 13, ir["doc_rules"]
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
    assert ir["rules"]["R-query-01"]["where"] == "file:{ANCHOR}/**/* queries.md", ir["rules"]["R-query-01"]["where"]
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
    assert ir["rules"]["R-query-14"]["moment"] == "skill:post:audit-q"
    assert "R-query-14" in ir["moments"]["skill:post:audit-q"]
    # the emitted corpus module must import — proves no cross-ruleset name collision
    with tempfile.TemporaryDirectory() as td:
        mp = Path(td) / "rules_all.py"
        mp.write_text(module_src, encoding="utf-8")
        spec = importlib.util.spec_from_file_location("rules_all", mp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert callable(getattr(mod, "body_R_query_14")), "pilot body not in corpus module"
    print(f"PASS  corpus_compile ({stats['rules']} rules, {stats['moments']} moment(s))")


def test_stats(stats):
    assert stats["when_rules"] == 1, stats
    assert stats["py_rules"] == 1, stats
    assert stats["doc_rules"] == 13, stats
    print("PASS  stats")


def main():
    with tempfile.TemporaryDirectory() as td:
        ir, _module_src, stats, mod = _compile_pilot(Path(td))
        test_ir_row_matches_worked_example(ir)
        test_tier_doc_rules_emitted(ir)
        test_emitted_body_fires_like_autofire(mod)
        test_stats(stats)
    test_corpus_compile()
    print("\nall warden_compile tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
