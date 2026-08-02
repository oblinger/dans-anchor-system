#!/usr/bin/env python3
"""T100 — the vault-wide audit stops planning work against dot-directories.

`enumerate_scope` excluded exactly one name, `/.git/`, chosen because it was the
one that hurt first. The vault-wide batch (T098) showed the rest: of 376,208
planned rule-target pairs, **4,377 sat under a dot-directory** — 3,579 of them
under `.trash`. The audit was reporting findings against documents the user had
deleted, and fix-by-default would have repaired them.

    python3 test-t100-dot-dir-exclusion.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_S = (Path(__file__).parent / "audit-plan.py").resolve()
_spec = importlib.util.spec_from_file_location("ap", _S)
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  (got {got!r}, want {want!r})"))


td = tempfile.TemporaryDirectory()
ROOT = Path(td.name)
(ROOT / ".anchor").write_text("", encoding="utf-8")
(ROOT / "Real.md").write_text("# Real\nOrientation.\n", encoding="utf-8")
for d in (".trash", ".anchor.d", ".pytest_cache", ".git"):
    (ROOT / d).mkdir()
    (ROOT / d / "Junk.md").write_text("# Junk\nx\n", encoding="utf-8")
(ROOT / ".trash" / "nested").mkdir()
(ROOT / ".trash" / "nested" / "Deep.md").write_text("# Deep\nx\n", encoding="utf-8")
(ROOT / "Live").mkdir()
(ROOT / "Live" / "Also.md").write_text("# Also\nx\n", encoding="utf-8")

print("The predicate")

check("a file directly inside a dot-dir is excluded",
      ap._under_dot_dir(ROOT / ".trash" / "Junk.md", ROOT), True)
check("...and one nested deeper under it, too",
      ap._under_dot_dir(ROOT / ".trash" / "nested" / "Deep.md", ROOT), True)
check("a normal file is not",
      ap._under_dot_dir(ROOT / "Live" / "Also.md", ROOT), False)
check("a DOTFILE in a normal dir is not excluded — dirs are the subject",
      ap._under_dot_dir(ROOT / "Live" / ".hidden.md", ROOT), False)
# The reason the check is relative and not absolute: `~/.claude/skills/...` is a
# real audit target, and an absolute parts scan would empty its own scope.
check("a root that is ITSELF under a dot-dir still enumerates its files",
      ap._under_dot_dir(ROOT / ".trash" / "Junk.md", ROOT / ".trash"), False)

print("\nThe walk")

_, files = ap.enumerate_scope(ROOT, "anchor", set())
names = sorted(f.name for f in files)
check("scope holds the live docs and nothing from any dot-dir",
      names, ["Also.md", "Real.md"])
check("...and .git is still excluded, as it was before by name",
      any(".git" in str(f) for f in files), False)

print("\nAnchor discovery")

# A `.anchor` inside `.trash` would not merely contribute files to someone else's
# plan — it would get a whole plan of its own from the batch driver.
(ROOT / ".trash" / ".anchor").write_text("", encoding="utf-8")
(ROOT / "Live" / ".anchor").write_text("", encoding="utf-8")
subs = ap.sub_anchor_roots(ROOT)
check("a `.anchor` under a dot-dir is not a live sub-anchor",
      sorted(p.name for p in subs), ["Live"])

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
