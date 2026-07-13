#!/usr/bin/env python3
"""F215 — the re-evaluation economy (significant-edit gate).

Pins the feature's Success Criteria fixture end-to-end through the real
compile→fire path: an expensive rule gated by `if:: file.diff.lines > 5`
(1) evaluates fully on first fire (whole-file diff), (2) spends NO body
execution on a typo-scale edit while its cached verdict persists, and
(3) re-judges on a section-scale edit. Plus the substrate units: DiffView
semantics, store persistence/accumulation, and the compiler's synthesised
residual-`if::` guards (which previously earned a `guard_py` name but no
emitted function). Runnable standalone — no test framework.
"""
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import warden_compile as wc  # noqa: E402
import warden_fire as wf  # noqa: E402
import warden_reval as wr  # noqa: E402

RULESET = """\
# RULESET R-reval-fx

where:: file:{ANCHOR}/**/*.md
description:: F215 fixture — an expensive body throttled by a file.diff gate

### RULE R-reval-fx-01 — expensive judgment, gated (when:: write:markdown)

if:: file.diff.lines > 5

```python
def body(ctx):
    import os
    with open(os.environ["REVAL_FX_LOG"], "a") as fh:
        fh.write("ran\\n")
    return ["finding: fixture issue"]
```
"""


def _runs(log: Path) -> int:
    return len(log.read_text().splitlines()) if log.is_file() else 0


def _compile_fixture(tmp: Path):
    rs = wc.parse_ruleset(RULESET, "R-reval-fx", "fixture.md")
    assert rs is not None
    ir, module_src, _ = wc.compile_ruleset(rs, "revalfx")
    mod_path = tmp / "rules_revalfx.py"
    mod_path.write_text(module_src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("rules_revalfx", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return ir, module_src, mod


def test_compile_marks_and_emits(ir, module_src):
    """The gated rule is file_bearing, keeps guard_py, and the synthesised
    guard function is actually EMITTED (the pre-F215 gap: name, no function)."""
    row = ir["rules"]["R-reval-fx-01"]
    assert row.get("file_bearing") is True, row
    assert row["guard_py"] == "guard_R_reval_fx_01", row
    assert row["body_py"] == "body_R_reval_fx_01", row
    assert "def guard_R_reval_fx_01(" in module_src, "synth guard not emitted"
    assert "def body_R_reval_fx_01(" in module_src
    print("PASS  compile_marks_and_emits")


def test_gate_lifecycle(ir, mod, tmp: Path):
    """The F215 Success Criteria: first fire full → typo edit throttled with
    verdict persistence → section edit re-judges. Sub-threshold edits
    accumulate (the record only advances on evaluation)."""
    doc = tmp / "target.md"
    log = tmp / "runs.log"
    os.environ["REVAL_FX_LOG"] = str(log)
    traits = ["reval-fx", "anchor-base"]

    def fire():
        ctx = wf.build_ctx(tmp, "write:markdown", file_path=str(doc))
        return wf.fire(ir, mod, "write:markdown", ctx, traits)

    # 1. first fire: no prior record → diff is the whole file → full evaluation
    doc.write_text("# Doc\n\none\ntwo\nthree\nfour\nfive\nsix\n")
    out = fire()
    assert _runs(log) == 1, "body did not run on first fire"
    assert out == ["finding: fixture issue"], out

    # 2. typo-scale edit: gate false → no body run; the verdict persists
    doc.write_text("# Doc\n\none\ntwo\nthree\nfour\nfive\nsix!\n")
    out = fire()
    assert _runs(log) == 1, "body ran on a typo-scale edit (gate failed to throttle)"
    assert out == [], "a throttled live fire must emit nothing"
    persisted = wr.store().verdict("R-reval-fx-01", doc)
    assert persisted == ["finding: fixture issue"], \
        f"cached verdict lost under throttle: {persisted}"

    # 3. section-scale edit: gate true → re-judged, record advances
    doc.write_text("# Doc\n\n" + "\n".join(f"line {i}" for i in range(12)) + "\n")
    out = fire()
    assert _runs(log) == 2, "body did not re-run on a section-scale edit"
    assert out == ["finding: fixture issue"], out

    # 4. accumulation: two sub-threshold edits whose JOINT diff crosses the
    # gate → the second fire evaluates (diff is measured since last EVALUATED,
    # not since last write)
    text = doc.read_text()
    doc.write_text(text + "tail a\ntail b\ntail c\n")
    fire()
    assert _runs(log) == 2, "3-line edit should stay under a >5 gate"
    doc.write_text(doc.read_text() + "tail d\ntail e\ntail f\n")
    fire()
    assert _runs(log) == 3, "accumulated 6-line diff failed to cross the gate"
    print("PASS  gate_lifecycle")


def test_diffview_semantics():
    """DiffView: first-pass = whole file; added/removed/lines/text agree."""
    first = wr.DiffView(None, "a\nb\nc")
    assert first.lines == 3 and first.added == ["a", "b", "c"] and first.removed == []
    dv = wr.DiffView("a\nb\nc", "a\nX\nc\nd")
    assert dv.added == ["X", "d"] and dv.removed == ["b"]
    assert dv.lines == 3
    assert "+X" in dv.text and "-b" in dv.text
    print("PASS  diffview_semantics")


def test_store_roundtrip(tmp: Path):
    """The store round-trips records atomically and isolates (rule, file) keys."""
    home = tmp / "store-home"
    st = wr.RevalStore(home)
    f = tmp / "f.md"
    assert st.record("R-a-01", f) is None
    st.mark_evaluated("R-a-01", f, "text v1", verdict=["v1"])
    assert st.verdict("R-a-01", f) == ["v1"]
    assert st.record("R-b-01", f) is None, "records leaked across rules"
    # a fresh instance reads the same state back off disk
    assert wr.RevalStore(home).record("R-a-01", f)["text"] == "text v1"
    print("PASS  store_roundtrip")


def test_store_thread_safety(tmp: Path):
    """Audit 2026-07-12 W6: the daemon is thread-per-connection, and RevalStore's
    load-mutate-replace had no lock — concurrent `mark_evaluated` calls on
    different files last-writer-won, dropping records. All marks from all
    threads must survive."""
    import threading
    home = tmp / "threaded-home"
    st = wr.RevalStore(home)
    n_threads, n_files = 8, 12

    def _worker(t: int):
        for i in range(n_files):
            st.mark_evaluated(f"R-thr-{t:02d}", tmp / f"f{i}.md",
                              f"text {t}/{i}", verdict=[f"v{t}/{i}"])

    threads = [threading.Thread(target=_worker, args=(t,)) for t in range(n_threads)]
    for th in threads:
        th.start()
    for th in threads:
        th.join(timeout=30)
    fresh = wr.RevalStore(home)
    missing = [(t, i) for t in range(n_threads) for i in range(n_files)
               if fresh.record(f"R-thr-{t:02d}", tmp / f"f{i}.md") is None]
    assert not missing, f"{len(missing)} records lost to the write race: {missing[:5]}"
    assert fresh.verdict("R-thr-03", tmp / "f7.md") == ["v3/7"]
    print("PASS  store_thread_safety (Audit 2026-07-12 W6)")


def test_authored_guard_still_wired():
    """A rule with an authored python guard (no residual if::) now earns
    guard_py + an emitted function (previously parsed but never wired)."""
    rs = wc.parse_ruleset(
        "# RULESET R-ag-fx\n\nwhere:: file:{ANCHOR}/**/*.md\n\n"
        "### RULE R-ag-fx-01 — authored guard (when:: session:start)\n\n"
        "```python\ndef guard(ctx):\n    return ctx.anchor == 'X'\n```\n",
        "R-ag-fx", "fixture.md")
    ir, module_src, _ = wc.compile_ruleset(rs, "agfx")
    row = ir["rules"]["R-ag-fx-01"]
    assert row["guard_py"] == "guard_R_ag_fx_01", row
    assert "def guard_R_ag_fx_01(" in module_src
    print("PASS  authored_guard_still_wired")


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        os.environ["WARDEN_HOME"] = str(tmp / "warden-home")
        wr._STORE = None  # rebind the singleton to the test home
        try:
            ir, module_src, mod = _compile_fixture(tmp)
            test_compile_marks_and_emits(ir, module_src)
            test_gate_lifecycle(ir, mod, tmp)
            test_diffview_semantics()
            test_store_roundtrip(tmp)
            test_store_thread_safety(tmp)
            test_authored_guard_still_wired()
        finally:
            os.environ.pop("WARDEN_HOME", None)
            os.environ.pop("REVAL_FX_LOG", None)
            wr._STORE = None
    print("\nall warden_reval tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
