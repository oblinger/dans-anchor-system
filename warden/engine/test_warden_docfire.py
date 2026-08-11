#!/usr/bin/env python3
"""Differential test — Warden doc-fire ≡ audit-plan verdicts (F212 / F214).

For every golden-corpus fixture, fire the doc-rules two ways — through the Warden
reference engine (`warden_docfire.fire_audit`, IR-driven, in-process) and through
the shipped `audit-plan --run` engine (subprocess) — and assert the canonical
verdict sets `(rule, target, status)` are identical. This is the differential
layer F214 specifies: the two engines cannot drift silently because a divergence
fails here regardless of what `expected.json` is blessed against. Runnable
standalone (no pytest).
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
from warden_root import corpus_root
REPO = corpus_root()
CASES = REPO / "warden" / "Warden Corpus" / "cases"
AUDIT_PLAN = REPO / "skills" / "audit" / "scripts" / "audit-plan.py"
sys.path.insert(0, str(HERE))

import warden_docfire as wd  # noqa: E402


def _read_case_yaml(path: Path) -> dict:
    meta: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def _materialize(fixture: Path) -> Path:
    sandbox = Path(tempfile.mkdtemp(prefix="warden-docfire-test-"))
    dst = sandbox / "fixture"
    shutil.copytree(fixture, dst)
    marker = dst / "_anchor.yaml"
    if marker.is_file():
        marker.rename(dst / ".anchor")
    return dst


def _canonical(verdicts: list[dict]) -> list[tuple]:
    return sorted((v["rule"], v["target"], v["status"]) for v in verdicts)


def _audit_plan_verdicts(target: Path, mode: str) -> list[dict]:
    out = subprocess.run(
        [sys.executable, str(AUDIT_PLAN), str(target),
         "--mode", mode, "--run", "--json", "--no-cache"],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)["results"]


def test_docfire_matches_audit_plan_on_every_case():
    case_dirs = sorted(d for d in CASES.iterdir()
                       if d.is_dir() and (d / "case.yaml").is_file())
    assert case_dirs, "no corpus cases found"
    for case_dir in case_dirs:
        meta = _read_case_yaml(case_dir / "case.yaml")
        mode = meta["mode"]
        if mode not in ("doc", "anchor"):
            continue  # moment cases are the live-fire path, not the doc-audit surface
        sandbox = _materialize(case_dir / "fixture")
        try:
            target = sandbox if meta["target"] == "." else sandbox / meta["target"]
            warden = _canonical(wd.fire_audit(target, mode))
            audit = _canonical(_audit_plan_verdicts(target, mode))
        finally:
            shutil.rmtree(sandbox.parent, ignore_errors=True)
        assert warden == audit, (
            f"{meta['id']}: verdict divergence\n"
            f"  warden-only:    {[v for v in warden if v not in audit]}\n"
            f"  audit-plan-only: {[v for v in audit if v not in warden]}")
        print(f"PASS  {meta['id']}  ({len(warden)} verdicts, warden ≡ audit-plan)")


def test_signature_matches_audit_plan():
    # the warden doc-fire pins to the same content signature audit-plan does
    out = subprocess.run(
        [sys.executable, str(REPO / "warden" / "Warden Corpus" / "harness" / "run-corpus.py"),
         "--engine", "audit-plan", "--json"],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    audit_sig = json.loads(out.stdout)["rule_corpus_sigs"]["audit-plan"]
    assert wd.corpus_signature() == audit_sig, (wd.corpus_signature(), audit_sig)
    print(f"PASS  signature ≡ audit-plan  ({audit_sig})")


ONWRITE_FIXTURE = """\
# RULESET R-onwrite-fx

where:: `file:{anchor}/**/*.md`
description:: M4a on-write fixture — one fixable rule, one message-only rule

### RULE R-onwrite-fx-01 — no trailing whitespace (checked)

check:: md_trailing_ws
fix:: md_trailing_ws

### RULE R-onwrite-fx-02 — frontmatter has description (checked)

check:: frontmatter_has description

**Why:** every doc self-describes.
"""


def test_fire_on_write_fixer_parity():
    """M4a: the on-write path repairs a fixable fail in place (audit-plan's
    fixer + never-delete floor, by delegation) and messages the unfixable one
    — the behavior contract of the bespoke `audit-on-write.sh` (F177)."""
    import warden_compile as wc
    rs = wc.parse_ruleset(ONWRITE_FIXTURE, "R-onwrite-fx", "fixture")
    assert rs is not None
    # shape [(row, rs)] like compile_audit_ir; rs needs source + rules w/ why
    ap_rs = {"source": "does/not/exist.md",
             "where": rs["where"],
             "rules": [{"id": "R-onwrite-fx-02", "why": "every doc self-describes."}]}
    rows = [(wc.compile_rule(r, rs), ap_rs) for r in rs["rules"]]
    assert rows[0][0].get("fix") == "md_trailing_ws", rows[0][0]

    with tempfile.TemporaryDirectory() as td:
        anchor = Path(td) / "FX"
        anchor.mkdir()
        (anchor / ".anchor").write_text("slug: FX\n", encoding="utf-8")
        doc = anchor / "note.md"
        doc.write_text("# Note   \n\nbody line  \n", encoding="utf-8")  # trailing ws, no frontmatter
        report = wd.fire_on_write(doc, rows=rows)
        # fixable fail → repaired in place + reported fixed
        assert [f["rule"] for f in report["fixed"]] == ["R-onwrite-fx-01"], report
        assert doc.read_text(encoding="utf-8") == "# Note\n\nbody line\n", doc.read_text()
        # unfixable fail → message with the why carried through
        msgs = {m["rule"]: m for m in report["messages"]}
        assert "R-onwrite-fx-02" in msgs, report
        assert msgs["R-onwrite-fx-02"]["why"] == "every doc self-describes."
        # steady state: re-fire → 01 clean, only the message remains
        report2 = wd.fire_on_write(doc, rows=rows)
        assert report2["fixed"] == [] and len(report2["messages"]) == 1, report2
    print("PASS  fire_on_write fixer parity (M4a)")


TOPIC_FIXTURE = """---
description: Topic fixture — Subtopics masthead + duplicate member rows + staging marks.
---

| -[[FX]]- | → [[kmr]] → [[SYS]] → [FX](hook://p/FX)<br>: Topic fixture. |
| --- | --- |
| Related | [[FX Notes\\|Notes]],   |
| Subtopics | [[FX DU\\|DU]],  [[FX Log\\|Log]],   |
| --- | |
| [[FX DU\\|DU]] | Per-drive du reports. |
| [[FX Log\\|Log]] | Dated entries documenting per-session plans. |
| ~~[[FX Ops\\|Ops]]~~ | Retired ops doc, staged for removal. |

Body content below the masthead.

~~[[FX BIG]] retired to APFS wipe~~
"""


def test_fire_on_write_preserves_dispatch_body():
    """F233 (F189 pilot fallout): the on-write path must NEVER delete body
    dispatch member rows that duplicate a masthead Subtopics row, and must
    NEVER strip `~~strikethrough~~` staging marks — fired against the LIVE
    R-doc umbrella so any future fixer that regresses this trips here.
    (Reproduction 2026-07-13 exonerated warden for the pilot's data loss —
    no registered fixer ever touched dispatch rows or tildes; the residual
    actor is HookAnchor's electric dispatch rebuild, tracked on HA.)"""
    with tempfile.TemporaryDirectory() as td:
        anchor = Path(td) / "FX"
        anchor.mkdir()
        (anchor / ".anchor").write_text("slug: FX\n", encoding="utf-8")
        doc = anchor / "FX.md"
        doc.write_text(TOPIC_FIXTURE, encoding="utf-8")
        wd.fire_on_write(doc)  # live R-doc rows — fixers apply in place
        after = doc.read_text(encoding="utf-8")
        assert "| [[FX DU\\|DU]] | Per-drive du reports. |" in after, after
        assert "| [[FX Log\\|Log]] |" in after, after
        assert "~~[[FX Ops\\|Ops]]~~" in after, after
        assert "~~[[FX BIG]] retired to APFS wipe~~" in after, after
        assert after.count("~~") == TOPIC_FIXTURE.count("~~"), after
    print("PASS  fire_on_write preserves dispatch body rows + staging marks (F233)")


def test_audit_ir_cache():
    """F232 B3: the umbrella flatten is mtime-cached — repeat calls return the
    cached rows without re-reading ~50 ruleset files; touching any source
    invalidates."""
    import os
    import time as _t
    wd._AUDIT_IR_CACHE.clear()
    t0 = _t.perf_counter()
    rows1 = wd.compile_audit_ir("R-doc")
    cold_ms = (_t.perf_counter() - t0) * 1000
    t0 = _t.perf_counter()
    rows2 = wd.compile_audit_ir("R-doc")
    warm_ms = (_t.perf_counter() - t0) * 1000
    assert rows2 is rows1, "cache miss on unchanged sources"
    assert warm_ms < cold_ms / 5 or warm_ms < 5.0, (cold_ms, warm_ms)
    src = wd._AUDIT_IR_CACHE["R-doc"]["sources"][0]
    os.utime(wd.ap.REPO_ROOT / src)
    rows3 = wd.compile_audit_ir("R-doc")
    assert rows3 is not rows1, "touching a source did not invalidate"
    print(f"PASS  audit_ir_cache (F232 B3 — cold {cold_ms:.0f} ms, warm {warm_ms:.2f} ms)")


SVG_FIXTURE = """<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200">
  <rect x="40" y="40" width="160" height="60" fill="none" stroke="#333"/>
  <rect x="240" y="40" width="120" height="60" fill="none" stroke="#333"/>
  <path d="M200 70 L240 70" stroke="#333" fill="none"/>
  <text x="150" y="75" font-size="12">spilled label text</text>
</svg>
"""


def _svg_anchor(traits: str) -> Path:
    """A throwaway anchor declaring `traits`, holding one deliberately-bad svg."""
    d = Path(tempfile.mkdtemp(prefix="warden-f297-"))
    (d / ".anchor").write_text(f"slug: F297T\ntitle: f297 probe\ntraits: [{traits}]\n",
                               encoding="utf-8")
    (d / "probe.svg").write_text(SVG_FIXTURE, encoding="utf-8")
    return d


def test_non_markdown_rules_reachable():
    """F297: a `.svg` write in an anchor declaring `svg-jiggle` puts that
    ruleset — and ONLY that ruleset — in play, and the same file in an anchor
    that declares nothing puts nothing in play.

    This is the T106 regression: every part of R-svg-jiggle was correct
    (written, compiled, registered, declared) and the fire path still could not
    reach it, because rule selection was hardcoded to one markdown umbrella."""
    declared = _svg_anchor("svg-jiggle")
    try:
        rows = wd.rows_for(declared / "probe.svg")
        ids = sorted(r["id"] for r, _ in rows)
        assert ids, "declared svg-jiggle selected no rules — T106 regression"
        assert all(i.startswith("R-svg-jiggle-") for i in ids), ids
        # the checkers actually run and report through the normal message shape
        report = wd.fire_on_write(declared / "probe.svg")
        assert report["messages"], report
        assert all(m["rule"].startswith("R-svg-jiggle-") for m in report["messages"])
    finally:
        shutil.rmtree(declared, ignore_errors=True)

    bare = _svg_anchor("topic")
    try:
        assert wd.rows_for(bare / "probe.svg") == [], "undeclared anchor selected rules"
        assert wd.fire_on_write(bare / "probe.svg") == {"fixed": [], "messages": []}
    finally:
        shutil.rmtree(bare, ignore_errors=True)
    print(f"PASS  non_markdown_rules_reachable (F297 — {len(ids)} svg rules in play)")


def test_markdown_selection_unchanged():
    """The markdown path still flattens the `R-doc` umbrella — F297 widened what
    a non-markdown write reaches without touching what a markdown write does."""
    d = Path(tempfile.mkdtemp(prefix="warden-f297-md-"))
    try:
        (d / ".anchor").write_text("slug: F297T\ntitle: f297 probe\n", encoding="utf-8")
        assert wd.rows_for(d / "x.md") == wd.compile_audit_ir("R-doc")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("PASS  markdown_selection_unchanged (F297)")


def test_governed_sweep_sees_a_script_write():
    """F297 leg 2: the post-Bash mtime sweep reports a governed file whose bytes
    changed with no tool call to attribute it to — and reports nothing on a
    baseline pass, an unchanged pass, or a recompile."""
    import os
    home = Path(tempfile.mkdtemp(prefix="warden-f297-home-"))
    anchor = _svg_anchor("svg-jiggle")
    svg = anchor / "probe.svg"
    prev_home = os.environ.get("WARDEN_HOME")
    os.environ["WARDEN_HOME"] = str(home)
    try:
        import warden_hook as wh
        ir = {"source_hash": "h1", "governed_paths": [str(svg)]}
        assert wh._governed_moved(ir) == [], "baseline pass fired"
        assert wh._governed_moved(ir) == [], "unchanged pass fired"
        os.utime(svg, (0, 0))                      # a generator rewrote it
        assert wh._governed_moved(ir) == [svg], "script write not seen"
        assert wh._governed_moved(ir) == [], "same write reported twice"
        os.utime(svg, (1, 1))
        assert wh._governed_moved({**ir, "source_hash": "h2"}) == [], \
            "a recompile re-reported the list instead of re-baselining"
    finally:
        if prev_home is None:
            os.environ.pop("WARDEN_HOME", None)
        else:
            os.environ["WARDEN_HOME"] = prev_home
        shutil.rmtree(home, ignore_errors=True)
        shutil.rmtree(anchor, ignore_errors=True)
    print("PASS  governed_sweep_sees_a_script_write (F297 leg 2)")


def main():
    test_docfire_matches_audit_plan_on_every_case()
    test_signature_matches_audit_plan()
    test_fire_on_write_fixer_parity()
    test_fire_on_write_preserves_dispatch_body()
    test_audit_ir_cache()
    test_non_markdown_rules_reachable()
    test_markdown_selection_unchanged()
    test_governed_sweep_sees_a_script_write()
    print("\nall warden_docfire tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
