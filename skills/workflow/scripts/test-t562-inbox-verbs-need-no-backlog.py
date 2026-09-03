#!/usr/bin/env python3
"""T562 — the Inbox verbs resolve a slug without demanding a backlog.

Found 2026-08-20 routing T554's tempo census to fourteen pebble owners: five of
them refused. `state drop SVH …` said *"declares `slug: SVH` but holds NO
backlog under any name"*; `state drop SYS|NJ|BUY|FIN …` said *"no '{SLUG}
Backlog.md' found"*. An Inbox has nothing to do with a backlog, and `cmd_drop`
already knew it — its last lines read `if backlog_path is not None:`. The
precondition lived one layer up, in `resolve_anchor`, which resolved **every**
slug through `find_backlog`.

**The reach this opens, measured:** 1,466 vault anchors answer to a unique slug
and **1,430 of them hold no backlog**. Before this, `state drop <SLUG>` reached
about 36 anchors — 2.5% of them.

**Two failure modes are deliberately preserved**, and §3 and §4 exist because
either would be easy to lose:

  - **Ambiguity still fails.** A drop is fire-and-forget: nobody comes back to
    check. Delivering to the wrong anchor because a slug matched two is a
    message that is never found, so "exactly one" is the rule and "the first of
    several" is not.
  - **Backlog verbs are untouched.** `set` / `show` / `define` still raise the
    errors they raise today, which were written against real incidents (ATT's
    PROS/BOONE rename mid-migration, the SV drop) and are better diagnostics
    than a resolution.

Run: python3 test-t562-inbox-verbs-need-no-backlog.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

STATE = Path(__file__).resolve().parent / "state"

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def live(*args):
    r = subprocess.run([sys.executable, str(STATE), *args],
                       capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


print("1. The five anchors that refused T554's drop now resolve")
# SVH declares a slug and has no backlog; BUY/FIN/NJ/SYS declare NO slug and
# are reached by folder basename — one case in five vs four, which is why the
# basename fallback is in the fix and not left for later.
for slug in ("SVH", "BUY", "FIN", "NJ", "SYS"):
    rc, out, err = live("inbox-list", slug)
    check(f"`state inbox-list {slug}` succeeds", rc, 0)
    check(f"...and names {slug}'s own Inbox",
          f"{slug} Inbox.md" in err, True)

print("2. Anchors that always worked still work")
for slug in ("TINK", "LUMEN"):
    rc, out, err = live("inbox-list", slug)
    check(f"`state inbox-list {slug}` succeeds", rc, 0)
    # T360: slugs are case-insensitive; the path is spelled as the files are (`Tink Inbox.md`).
    check(f"...and names {slug}'s own Inbox", f"{slug} Inbox.md".lower() in err.lower(), True)

print("3. Backlog verbs are untouched — the precondition moved, it did not go")
rc, out, err = live("show", "SVH", "Backlog", "T1")
check("`show` on a backlog-less anchor still fails", rc != 0, True)
check("...with the message that names the real situation",
      "holds NO backlog under any name" in err, True)
rc, out, err = live("show", "NOSUCHSLUGAT_ALL", "Backlog", "T1")
check("an unknown slug still fails", rc != 0, True)
check("...naming the file it looked for",
      "NOSUCHSLUGAT_ALL Backlog.md" in err, True)

print("4. `or_named` returns declarations first, so one of each is still two")
sys.path.insert(0, str(STATE.parent))
import importlib.util  # noqa: E402
from importlib.machinery import SourceFileLoader  # noqa: E402
_spec = importlib.util.spec_from_loader("st", SourceFileLoader("st", str(STATE)))
st = importlib.util.module_from_spec(_spec)
sys.modules["st"] = st
_spec.loader.exec_module(st)
check("the backlog-free verb list is exactly the Inbox verbs",
      set(st._BACKLOG_FREE_VERBS), {"drop", "inbox-list", "inbox-tag"})
# The ordering property is what makes "exactly one" safe: a declared hit and a
# folder-name hit are two entries, so resolution refuses rather than guessing.
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / "Declared").mkdir()
    (root / "Declared" / ".anchor").write_text("slug: DUP\n")
    (root / "DUP").mkdir()
    (root / "DUP" / ".anchor").write_text("")
    real_root = st.be.VAULT_ROOT
    try:
        st.be.VAULT_ROOT = root
        both = st._anchors_declaring_slug("DUP", or_named=True)
        check("a declared hit and a named hit are two", len(both), 2)
        check("...and the DECLARED one is first", both[0].name, "Declared")
        only = st._anchors_declaring_slug("DUP")
        check("without or_named only the declaration is seen", len(only), 1)
    finally:
        st.be.VAULT_ROOT = real_root

print("5. `cmd_drop` was already written for this — the fix removed a blocker")
import inspect  # noqa: E402
src = inspect.getsource(st.cmd_drop)
check("cmd_drop guards its backlog use rather than requiring one",
      "if backlog_path is not None" in src, True)

print()
if FAILURES:
    print(f"test-t562-inbox-verbs-need-no-backlog: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t562-inbox-verbs-need-no-backlog: all checks pass")
