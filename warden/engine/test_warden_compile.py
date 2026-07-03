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
    assert ir["traits"]["query"] == ["R-query-14"]
    # the tier doc-rules are honestly deferred, not silently dropped
    assert "R-query-13" in ir["deferred"]
    assert "R-query-14" not in ir["deferred"]
    print("PASS  ir_row_matches_worked_example")


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


def test_stats(stats):
    assert stats["when_rules"] == 1, stats
    assert stats["py_rules"] == 1, stats
    assert stats["deferred"] == 13, stats
    print("PASS  stats")


def main():
    with tempfile.TemporaryDirectory() as td:
        ir, _module_src, stats, mod = _compile_pilot(Path(td))
        test_ir_row_matches_worked_example(ir)
        test_emitted_body_fires_like_autofire(mod)
        test_stats(stats)
    print("\nall warden_compile tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
