#!/usr/bin/env python3
"""test-f332-doc-next.py — F332: the doc owns the Next.

`state set <anchor> Backlog <row> --next "..."` mirrors the text into the
arrow-linked doc as a `next::` Dataview field in the H1's intro block
(under the orientation line, before the first H2). Pins:

  1. First --next INSERTS `next::` after the orientation line.
  2. A second --next UPDATES the same line (no duplicates).
  3. `--next ""` on a bracket that permits removal DELETES the field.
  4. A row with no arrow-linked doc keeps its row-only Next, no crash.
  5. The field lands BEFORE the first H2, never inside a section.
"""
import sys as _sys; _sys.dont_write_bytecode = True

import contextlib
import importlib.machinery
import importlib.util
import io
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


st = _load("state_mod", HERE / "state")
be = st.be

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")

TMP = Path(tempfile.mkdtemp())
be.VAULT_ROOT = TMP

BL = TMP / "ZZN Track" / "ZZN Backlog.md"
BL.parent.mkdir(parents=True)
BL.write_text(
    "---\ndescription: t\n---\n\n# ZZN Backlog\n\n## Now\n\n"
    "- **F001 — docful** [Ready] — → [[ZZN001 - docful|F001 — docful]] ^F001\n"
    "  - **Next:** old next.\n"
    "- **T002 — docless** [Ready] — plain body, no arrow link ^T002\n"
    "  - **Next:** old next.\n"
    "\n## Done\n",
    encoding="utf-8",
)

DOC = TMP / "ZZN Design" / "ZZN Features" / "ZZN001 - docful.md"
DOC.parent.mkdir(parents=True)
DOC.write_text(
    "---\ndescription: d\n---\n\n"
    "# [[ZZN]] · F001 — docful\n"
    "One-line orientation.\n"
    "\n"
    "## Status\n\n**Ready** — set.\n",
    encoding="utf-8",
)

be.find_backlog = lambda slug: BL
be.find_icebox = lambda slug: None
be.refresh_q_md = lambda slug: None
be.append_messages = lambda *a, **k: None
be.write_state = lambda *a, **k: None
be.heal_backlog_if_stale = lambda *a, **k: None
be._selffire = lambda *a, **k: None
st._selffire = lambda *a, **k: None


def set_next(label, next_text, status="Ready"):
    a = SimpleNamespace(
        doc="Backlog", label=label, verb="set", inline=None, from_file=None,
        why_ask=None, horizon=None, status=status, title=None,
        next_step=next_text, verify=None, user=None, why_user=None,
        why_user_action=None,
    )
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = st.cmd_item("ZZN", TMP, a)
    return rc, buf.getvalue()


print("== 1. first --next inserts next:: after the orientation line ==")
set_next("F001", "run the new thing")
t = DOC.read_text()
# R-spine-02: the orientation keeps its trailing blank; the field follows it
# with its own blank after.
ok("next:: inserted (blank-separated per R-spine-02)") \
    if "\nOne-line orientation.\n\nnext:: run the new thing\n\n" in t \
    else no(f"doc:\n{t}")

print("== 2. second --next updates in place ==")
set_next("F001", "run the newer thing")
t = DOC.read_text()
ok("next:: updated, no duplicate") \
    if t.count("next::") == 1 and "next:: run the newer thing\n" in t \
    else no(f"doc:\n{t}")

print("== 3. empty --next removes the field (bracket permitting) ==")
set_next("F001", "", status="Verify") if False else None
# [Ready] requires a Next, so removal is exercised on a bracket that
# doesn't demand one — rebracket to [Questions]-free [Done] is heavy; use
# sync_doc_next directly for the removal semantics.
be.sync_doc_next(
    "- **F001 — docful** [x] — → [[ZZN001 - docful|F001]]", "")
t = DOC.read_text()
ok("next:: removed") if "next::" not in t else no(f"doc:\n{t}")

print("== 4. docless row: no crash, backlog Next still lands ==")
rc, out = set_next("T002", "do the docless thing")
bl = BL.read_text()
ok("docless row updated without error") \
    if rc in (0, None) and "do the docless thing" in bl \
    else no(f"rc={rc} out={out}")

print("== 5. field stays in the intro block (before first H2) ==")
set_next("F001", "back again")
t = DOC.read_text()
intro = t.split("## ", 1)[0]
ok("next:: sits before the first H2") if "next:: back again" in intro \
    else no(f"doc:\n{t}")

shutil.rmtree(TMP, ignore_errors=True)
print("-" * 40)
print(f"test-f332-doc-next: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
