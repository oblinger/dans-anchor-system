#!/usr/bin/env python3
"""test-t159-blocker-elevation.py — a row that BLOCKS visible work is elevated to
`## Blockers` at the top of the page.

Dan, 2026-08-08, after failing to find ATT F041 while eight rows announced they
were blocked on it: *"if an item is blocking other items, create a category at
the very top, even above Ready… that way my eyes are drawn right to it."* The
section already existed (F283) and already sat first. It fired on nothing, for
two independent reasons, and both had to go:

  (1) SCOPE — the gate was `horizon in ACTIVE_HORIZONS_BANNER`, so only a blocked
      row on the Now/Next frontier could promote its blocker. A `[Blocked …]` row
      under `## Later` renders (F283 admits it to the visibility ledger) and is
      just as stuck, so the honest test is "does the waiting row appear on this
      page", not "is it on the frontier".
  (2) THE HANDLE NEVER MATCHED — `gated_by` was keyed by handle text and looked
      up against `identifier`, so `[Blocked ATT-F041]` stored `ATT-F041` while the
      row it names is `F041`. Every anchor-qualified handle in the vault was
      inert, and that is most of them.

Either bug alone keeps the section empty, which is why F283 shipped believing it
worked: its own comment records "the section renders empty everywhere", read at
the time as "nothing is blocked" rather than as a defect.

  A. an anchor-qualified handle matches the row it names
  B. a blocker of a `## Later` [Blocked] row is elevated
  C. the blocker is elevated even when its OWN bracket renders nowhere
  D. a handle naming a different anchor promotes nothing here
  E. a blocker of a row that renders NOWHERE is not elevated
  F. a [Done] blocker is never elevated

Self-contained: fixture backlog in a tmpdir, parsed by queries-render's own
parser. Never touches the vault."""
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


qr = _load("queries_render_mod", HERE / "queries-render.py")

PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  ok    {m}")


def no(m):
    global FAIL
    FAIL += 1
    print(f"  FAIL  {m}")


FIXTURE = """# ATT Backlog

## Now

- **F001 — a frontier row blocked by a bare handle** [Blocked F050] — body ^F001
- **F050 — the bare-handle blocker** [Ready] — body ^F050
  - **Next:** do it
- **F060 — blocks only a hidden row** [Ready] — body ^F060
  - **Next:** do it

## Later

- **F041 — disk-ops master pointer** [User] — body ^F041
  - **User:** attach BEAST / COPPER and start a disk-work session
- **F040 — a merge that needs the disks** [Blocked ATT-F041] — body ^F040
- **F039 — another one** [Blocked ATT-F041] — body ^F039
- **F050 — the bare-handle blocker** [Ready] — body ^F050
  - **Next:** do it
- **F060 — blocks only a hidden row** [Ready] — body ^F060
  - **Next:** do it
- **F061 — waits on F060, and renders nowhere** [Waiting] — body ^F061
- **F070 — names another anchor's row** [Blocked MUX-F999] — body ^F070
- **F090 — gated on Dan, but also runnable** [Ready, User] — body ^F090
  - **Next:** run the agent phase
  - **User:** then decide
- **F092 — waits on the half-gated one** [Blocked F090] — body ^F092
- **F091 — a stuck blocker** [Blocked upstream] — body ^F091
- **F093 — waits on the stuck one** [Blocked F091] — body ^F093

## Done

- **F080 — a finished blocker** [Done] — body ^F080
- **F081 — waits on the finished one** [Blocked ATT-F080] — body ^F081
"""


def section(text, title):
    lines = text.splitlines()
    try:
        at = next(i for i, l in enumerate(lines) if l.strip() == f"## {title}")
    except StopIteration:
        return ""
    end = next((i for i in range(at + 1, len(lines))
                if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[at + 1:end])


d = Path(tempfile.mkdtemp())
try:
    backlog = d / "ATT Backlog.md"
    backlog.write_text(FIXTURE, encoding="utf-8")
    rows = qr.parse_backlog(backlog)
    body = qr.build_queries_body(
        "ATT", "# [A]  ATT  -  Runnable 2", rows, {},
        qr.extract_next_actions(backlog), qr.extract_verify_questions(backlog),
        backlog)
    text = "\n".join(body or [])
    blockers = section(text, "Blockers")

    print("A/B/C: the ATT F041 case Dan could not find")
    if "F041" in blockers:
        ok("F041 is elevated to ## Blockers")
    else:
        no("F041 is absent from ## Blockers — the anchor-qualified handle "
           "`ATT-F041` still does not match the row `F041`")
    if "F040" in blockers and "F039" in blockers:
        ok("...naming the rows it gates")
    else:
        no("the blocker bullet does not name what it gates")
    # Its own bracket is [User] under Later, which renders nowhere. Elevation
    # must not depend on the blocker itself being visible — that is the whole
    # point, since an invisible blocker is the one you cannot go find.
    if "## Blockers" in text and text.index("## Blockers") < text.index("## Ready"):
        ok("## Blockers sits above ## Ready")
    else:
        no("## Blockers is not first")

    print("D/E/F: what must NOT be elevated")
    if "F999" not in blockers and "F070" not in blockers:
        ok("a handle naming another anchor promotes nothing here")
    else:
        no("a foreign-anchor handle was resolved locally")
    if "F060" not in blockers:
        ok("a blocker whose only waiter renders nowhere stays put")
    else:
        no("F060 was elevated by a [Waiting] row that renders in no section")
    if "F080" not in blockers:
        ok("a [Done] blocker is never elevated")
    else:
        no("a finished blocker was elevated")

    print("G: a self-clearing blocker is NOT elevated (Dan, 2026-08-08)")
    # A [Ready] row that gates something is not stuck — working the Ready queue
    # clears it. Elevating it displaces rows nothing an agent does will move.
    if "F050" not in blockers:
        ok("a [Ready] blocker stays in ## Ready and out of ## Blockers")
    else:
        no("a self-clearing [Ready] blocker occupied the top of the page")
    if "F050" in section(text, "Ready"):
        ok("...and is still shown as Ready, where it will be worked")
    else:
        no("the un-elevated blocker vanished instead of rendering in Ready")
    # `[Ready, User]` is the case that makes the test `all` and not `any`:
    # the agent phase runs, and the row is STILL gated on Dan afterwards.
    if "F090" in blockers:
        ok("[Ready, User] stays elevated — the Ready queue does not clear it")
    else:
        no("a row gated on Dan was suppressed because it also had a Ready member")

    print("H: the bare-handle form still works (F283's original case)")
    if "F091" in blockers:
        ok("a bare `[Blocked F091]` handle still resolves and promotes")
    else:
        no("the un-prefixed handle regressed")
finally:
    shutil.rmtree(d, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
