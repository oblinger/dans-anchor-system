#!/usr/bin/env python3
"""test-f329-backlog-folder.py — F329: the folder-form backlog.

The backlog may upgrade from `{slug} Track/{slug} Backlog.md` to the
folder-doc form `{slug} Track/{slug} Backlog/{slug} Backlog.md`, the folder
holding the anchor's T-docs. This pins the recognizers on both forms:

  1. `backlog_edit.anchor_track_dir` — Track dir from either form.
  2. `audit_q.backlog_track_dir` — the mirrored recognizer.
  3. `audit_q.classify_backlog` — the folder form opts in exactly like the
     flat form (verdict "render"); a folder-form backlog whose grandparent
     is NOT `{slug} Track` stays unclassified.
"""
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


be = _load("backlog_edit", HERE / "backlog-edit.py")
aq = _load("audit_q", HERE.parent.parent / "audit" / "scripts" / "audit-q.py")

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")

TMP = Path(tempfile.mkdtemp())
BACKLOG_TEXT = (
    "---\ndescription: t\n---\n\n# ZZF Backlog\n\n## Now\n\n"
    "- **F001 — seed** [Ready] — body ^F001\n\n## Done\n"
)

flat = TMP / "A" / "ZZF Track" / "ZZF Backlog.md"
flat.parent.mkdir(parents=True)
flat.write_text(BACKLOG_TEXT, encoding="utf-8")

folder = TMP / "B" / "ZZF Track" / "ZZF Backlog" / "ZZF Backlog.md"
folder.parent.mkdir(parents=True)
folder.write_text(BACKLOG_TEXT, encoding="utf-8")

stray = TMP / "C" / "SomewhereElse" / "ZZF Backlog" / "ZZF Backlog.md"
stray.parent.mkdir(parents=True)
stray.write_text(BACKLOG_TEXT, encoding="utf-8")

print("== 1. backlog_edit.anchor_track_dir ==")
ok("flat form → parent") if be.anchor_track_dir(flat) == flat.parent \
    else no(f"flat: {be.anchor_track_dir(flat)}")
ok("folder form → grandparent (the Track dir)") \
    if be.anchor_track_dir(folder) == folder.parent.parent \
    else no(f"folder: {be.anchor_track_dir(folder)}")

print("== 2. audit_q.backlog_track_dir mirrors it ==")
ok("flat form → parent") if aq.backlog_track_dir(flat) == flat.parent \
    else no(f"flat: {aq.backlog_track_dir(flat)}")
ok("folder form → grandparent") \
    if aq.backlog_track_dir(folder) == folder.parent.parent \
    else no(f"folder: {aq.backlog_track_dir(folder)}")

print("== 3. audit_q.classify_backlog on both forms ==")
v1, _ = aq.classify_backlog(flat)
ok("flat form renders") if v1 == "render" else no(f"flat verdict: {v1}")
v2, _ = aq.classify_backlog(folder)
ok("folder form renders (opt-in through the Backlog folder)") \
    if v2 == "render" else no(f"folder verdict: {v2}")
v3, _ = aq.classify_backlog(stray)
ok("folder form outside a Track dir stays unclassified") \
    if v3 == "unclassified" else no(f"stray verdict: {v3}")

shutil.rmtree(TMP, ignore_errors=True)
print("-" * 40)
print(f"test-f329-backlog-folder: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
