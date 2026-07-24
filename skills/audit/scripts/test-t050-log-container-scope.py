#!/usr/bin/env python3
"""test-t050-log-container-scope.py — T050: R-log-01 (`log_path_exists`) and
R-log-08 (`log_anchor_page_link`) must be suppressed when the audited anchor IS
itself a `{slug} Log` container (the standard name for the folder of reverse-
chronological dated entries, e.g. `SV Log`). Before the fix, editing `SV Log.md`
fired R-log-01 ("no SV Log Log/ under anchor") and R-log-08 ("no [[SV Log Log]]
link") — demanding a log INSIDE the log. Asserts:

  1. A `{slug} Log` anchor (slug or folder name ends in ` Log`) passes both.
  2. An ordinary anchor with NO log still FAILS both (no regression).
  3. An ordinary anchor WITH a proper log still passes both.

Self-contained: loads audit-plan in-process, builds tmp fixture anchors. No vault I/O."""
import importlib.util
import pathlib
import sys
import tempfile

S = (pathlib.Path(__file__).parent / "audit-plan.py").resolve()
_spec = importlib.util.spec_from_file_location("ap", S)
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"  (got {got!r}, want {want!r})"))


def _anchor(root, slug, files):
    d = root / slug
    d.mkdir()
    (d / ".anchor").write_text(f"slug: {slug}\n", encoding="utf-8")
    for name, body in files.items():
        (d / name).write_text(body, encoding="utf-8")
    return d


def run():
    root = pathlib.Path(tempfile.mkdtemp())

    print("A {slug} Log container is exempt from R-log-01 / R-log-08 (T050)")
    logc = _anchor(root, "SV Log", {"SV Log.md": "# SV Log\nReverse-chron entries.\n"})
    check("log-container passes R-log-01 (no nested log demanded)",
          ap.chk_log_path_exists(logc, logc, [])[0], "pass")
    check("log-container passes R-log-08 (no [[SV Log Log]] demanded)",
          ap.chk_log_anchor_page_link(logc, logc, [])[0], "pass")

    # folder name ends in ` Log` even if the .anchor slug were customized
    logc2 = root / "MED Heart Log"
    logc2.mkdir()
    (logc2 / ".anchor").write_text("slug: MEDLOG\n", encoding="utf-8")  # slug lacks " Log"
    (logc2 / "MED Heart Log.md").write_text("# MED Heart Log\nx\n", encoding="utf-8")
    check("folder-name-ends-in-Log is exempt even when slug does not",
          ap.chk_log_path_exists(logc2, logc2, [])[0], "pass")

    print("Ordinary anchors are unaffected (no regression)")
    nolog = _anchor(root, "Foo", {"Foo.md": "# Foo\nAn anchor.\n"})
    check("ordinary anchor with NO log still FAILS R-log-01",
          ap.chk_log_path_exists(nolog, nolog, [])[0], "fail")
    check("ordinary anchor with NO log still FAILS R-log-08",
          ap.chk_log_anchor_page_link(nolog, nolog, [])[0], "fail")

    withlog = _anchor(root, "Bar", {
        "Bar.md": "# Bar\nx\n\n[[Bar Log]]\n",
        "Bar Log.md": "# Bar Log\ny\n"})
    check("ordinary anchor WITH a proper log still passes R-log-01",
          ap.chk_log_path_exists(withlog, withlog, [])[0], "pass")
    check("ordinary anchor WITH a proper log still passes R-log-08",
          ap.chk_log_anchor_page_link(withlog, withlog, [])[0], "pass")


if __name__ == "__main__":
    run()
    print(f"\n{sum(results)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)
