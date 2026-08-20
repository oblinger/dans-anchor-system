#!/usr/bin/env python3
"""T363 — a folder-form backlog's member doc that nothing links is found.

F329 hoisted each live row's record into `{slug} Track/{slug} Backlog/` as its
own doc. The backlog's horizon sections list every LIVE row, so for those the
folder is fully reachable from its index — which is the argument that the form
needs no dispatch table (T363 Q1 option A).

**That argument is true for live rows and false for retired ones.** When a row
is removed its doc stays in the folder with nothing pointing at it. [[SONAR]]
found the consequence 2026-08-19: `SONAR017` was a live question addressed to
Dan carrying `Recommendation: None`, lost its row in the F329 hoist, and had no
reference anywhere in the vault for three days — not retired, not parked, just
gone. Three more claimed an unsent note was owed, months after their rows went.

So the reachability R-spine-03 protects is real, and this is what protects it.
A dispatch table would also list the orphans, but at the cost of a
machine-maintained masthead on the file `state` parses and rewrites — the one
edit T363 calls least safe to guess at.

The narrowness matters as much as the catch:
  - a doc whose row is live is linked BY that row, so it must not fire;
  - `{slug} Chores.md` is written by `audit-q --fix` and linked from nowhere by
    design, so it must not fire;
  - an ALIASED or block-anchored link (`[[X|Y]]`, `[[X#^id]]`) is a reference;
  - a STRUCK link (`~~[[X]]~~`) is a reference too — a struck pointer is a
    different defect (T550) and reading it as an orphan would send the reader
    to restore a row that already exists;
  - a flat (non-folder-form) backlog fronts no folder and is out of scope.

Run: python3 test-t363-orphan-row-docs.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "aq", Path(__file__).resolve().parent / "audit-q.py")
aq = importlib.util.module_from_spec(_spec)
sys.modules["aq"] = aq
_spec.loader.exec_module(aq)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


BACKLOG = """---
description: "fixture"
---

# ZZ Backlog
Fixture for the T363 / C58 assertions.

## Now

- **T001 — a live row** [Ready] — → [[ZZ001 - A live row|T001]] — body ^T001
  - **Next:** do it.
- **T002 — a row whose pointer got struck** [Ready] — → ~~[[ZZ002 - A struck pointer|T002]]~~ — body ^T002
  - **Next:** do it.
- **T003 — a row that links its doc with a block anchor** [Ready] — → [[ZZ003 - Anchored#^ZZ003-Q1|T003]] — body ^T003
  - **Next:** do it.
"""


def build(tmp, folder_form=True):
    root = Path(tmp)
    (root / ".anchor").write_text("slug: ZZ\n")
    folder = root / "ZZ Backlog" if folder_form else root
    folder.mkdir(parents=True, exist_ok=True)
    backlog = folder / "ZZ Backlog.md"
    backlog.write_text(BACKLOG)
    for stem in ("ZZ001 - A live row", "ZZ002 - A struck pointer",
                 "ZZ003 - Anchored", "ZZ017 - An orphaned question to Dan",
                 "ZZ Chores"):
        (folder / f"{stem}.md").write_text(f"# {stem}\nbody\n")
    return backlog, root


def orphans(backlog, root):
    linked = aq._vault_wikilink_targets(root)
    return sorted(f.surface_file.stem
                  for f in aq.check_c58_orphan_row_docs(backlog, linked))


print("1. Exactly the doc whose row is gone")
with tempfile.TemporaryDirectory() as td:
    backlog, root = build(td)
    got = orphans(backlog, root)
    check("only the orphan fires", got, ["ZZ017 - An orphaned question to Dan"])
    check("...a live row's doc does not",
          "ZZ001 - A live row" in got, False)
    check("...a STRUCK pointer still counts as a reference (T550)",
          "ZZ002 - A struck pointer" in got, False)
    check("...a block-anchored link counts as a reference",
          "ZZ003 - Anchored" in got, False)
    check("...and Chores is exempt by design",
          "ZZ Chores" in got, False)
    check("the finding is a warning, not a stop-gate",
          sorted({f.severity for f in aq.check_c58_orphan_row_docs(
              backlog, aq._vault_wikilink_targets(root))}), ["warning"])
    check("and is not claimed mechanically fixable",
          sorted({f.mechanically_fixable for f in aq.check_c58_orphan_row_docs(
              backlog, aq._vault_wikilink_targets(root))}), [False])

print("2. Restoring a reference clears it")
with tempfile.TemporaryDirectory() as td:
    backlog, root = build(td)
    (root / "somewhere-else.md").write_text(
        "A mention from anywhere counts: [[ZZ017 - An orphaned question to Dan]]\n")
    check("a link from ANY file in the vault is enough",
          orphans(backlog, root), [])

print("3. A flat backlog fronts no folder and is out of scope")
with tempfile.TemporaryDirectory() as td:
    backlog, root = build(td, folder_form=False)
    # Here `ZZ Backlog.md` sits beside the docs but its folder is the anchor
    # root, not a folder named after it — the F329 form is what C58 addresses.
    check("no findings on the flat form", orphans(backlog, root), [])

print("4. The vault scan is what makes an absence decidable")
with tempfile.TemporaryDirectory() as td:
    backlog, root = build(td)
    targets = aq._vault_wikilink_targets(root)
    check("an aliased link resolves to its basename",
          "ZZ001 - A live row" in targets, True)
    check("a struck link is still collected",
          "ZZ002 - A struck pointer" in targets, True)
    check("a block-anchored link drops its anchor",
          "ZZ003 - Anchored" in targets, True)
    check("the orphan is genuinely absent",
          "ZZ017 - An orphaned question to Dan" in targets, False)

print()
if FAILURES:
    print(f"test-t363-orphan-row-docs: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t363-orphan-row-docs: all checks pass")
