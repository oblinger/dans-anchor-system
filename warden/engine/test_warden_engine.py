#!/usr/bin/env python3
"""Regression test for warden_engine.py (F212 reference loop).

Exercises the whole scan→compile→fire loop through the single `WardenEngine`
entry against a fixture anchor that has adopted the `query` trait — the real
`R-query-14` fires end-to-end, and the lazy warm-start memoises the corpus
compile. Runnable standalone.
"""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
from warden_root import corpus_root
REPO = corpus_root()
sys.path.insert(0, str(HERE))

import warden_engine as we  # noqa: E402


def _fixture_anchor(tmp: Path, traits: str, question: str) -> Path:
    anchor = tmp / "FX"
    (anchor / "FX Track").mkdir(parents=True)
    (anchor / ".anchor").write_text(f"slug: FX\ntraits: [{traits}]\n", encoding="utf-8")
    (anchor / "FX Track" / "FX queries.md").write_text(
        f"## Immediate Questions\n\n- **Q1** {question}\n", encoding="utf-8")
    return anchor


def test_engine_fires_r_query_14():
    with tempfile.TemporaryDirectory() as td:
        anchor = _fixture_anchor(Path(td), "query, Commit", "Should I commit and push this now?")
        engine = we.WardenEngine(REPO)
        steers = engine.fire(anchor, "skill:pre:audit-q")
        assert steers and "Do NOT ask" in steers[0], steers
        assert "commit now" in steers[0], steers[0]
        # the corpus compiled once and is memoised (same object on re-access)
        assert engine.ir is engine._ir
        assert "R-query-14" in engine.ir["rules"]
    print("PASS  engine_fires_r_query_14")


def test_engine_gating_and_stream():
    with tempfile.TemporaryDirectory() as td:
        # an anchor that did NOT adopt the query trait fires nothing
        anchor = _fixture_anchor(Path(td), "Commit", "Should I commit and push this now?")
        engine = we.WardenEngine(REPO)
        assert engine.fire(anchor, "skill:pre:audit-q") == [], "fired without the query trait"

        # a moment with no rules yields no steers; run_moments returns per-moment
        adopted = _fixture_anchor(Path(td) / "b", "query, Commit", "Should I push?")
        stream = engine.run_moments(adopted, ["skill:pre:audit-q", "tool:post:Write"])
        assert stream["skill:pre:audit-q"], stream
        assert stream["tool:post:Write"] == [], stream
    print("PASS  engine_gating_and_stream")


def test_engine_fire_audit_surface():
    # the reference engine also owns the doc-audit fire path (the tier doc-rules);
    # firing a queries doc with no frontmatter yields the R-query-02 fail verdict.
    with tempfile.TemporaryDirectory() as td:
        doc = Path(td) / "FX queries.md"
        doc.write_text("# FX queries\n\nno frontmatter here\n", encoding="utf-8")
        engine = we.WardenEngine(REPO)
        verdicts = engine.fire_audit(doc, "doc")
        rules = {v["rule"]: v["status"] for v in verdicts}
        assert "R-query-02" in rules, rules
        assert rules["R-query-02"] == "fail", rules
    print("PASS  engine_fire_audit_surface")


def main():
    test_engine_fires_r_query_14()
    test_engine_gating_and_stream()
    test_engine_fire_audit_surface()
    print("\nall warden_engine tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
