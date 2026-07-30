#!/usr/bin/env python3
"""test-f284-frontier-totality.py — F284: the queue-file render is TOTAL over
the frontier. Every `## Now` / `## Next` row reaches the rendered body no matter
what its bracket says — including brackets the render has never heard of, and
rows carrying no bracket at all.

Before F284 the render selected the brackets it knew (`Verify*`/`Watching*`,
`*Questions*`, `Ready`/`Agreed`/`Active`) and let everything else fall off the
end of `build_queries_body` — silently, with no error and no count. That hid 47
of 99 frontier rows vault-wide (2026-07-29), and hid them from the one surface
the user reads to find work. The largest hidden class was rows with no bracket
at all, which no whitelist would ever have caught.

So this test does NOT enumerate the brackets that should render. It asserts the
property: give the renderer a frontier row with an arbitrary bracket and the row
comes out the other side. `purple monkey dishwasher` is in the fixture on
purpose — it stands in for whatever bracket someone invents next.

Self-contained: writes a fixture backlog to a temp dir, parses it with
queries-render's own parser, and reads the rendered body."""
import importlib.machinery
import importlib.util
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
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")


# One row per class of bracket the render has to survive. The last three are the
# ones that were silently dropped before F284.
FIXTURE = """# FX Backlog

## Now

- **F001 — a ready row** [Ready] — body ^F001
  - **Next:** do the thing
- **F002 — an implementing row** [Implementing] — body ^F002
  - **Next:** finish the thing
- **F003 — a questions row** [Questions] — body ^F003
- **F004 — a verify row** [Verify] — body ^F004
  - **Verify:** did it work?
- **F005 — a designing row** [Designing] — body ^F005
- **F006 — a user-gated row** [User] — body ^F006
- **F007 — a bracket nobody has ever defined** [purple monkey dishwasher] — body ^F007
- **F008 — no bracket at all** — body ^F008

## Next

- **F009 — a blocked row** [Blocked F001] — body ^F009
- **F010 — a waiting row** [Waiting on the bridge] — body ^F010

## Later

- **F011 — parked, not frontier** [Designing] — body ^F011

## Done

- **F012 — finished** [Done] — body ^F012
"""


def main():
    d = Path(tempfile.mkdtemp())
    backlog = d / "FX Backlog.md"
    backlog.write_text(FIXTURE, encoding="utf-8")

    rows = qr.parse_backlog(backlog)
    body = qr.build_queries_body(
        "FX", "# [A]  FX  -  Runnable 2", rows, {},
        qr.extract_next_actions(backlog), qr.extract_verify_questions(backlog),
        backlog)
    text = "\n".join(body or [])

    frontier = [r for r in rows if r.horizon in ("Now", "Next")]
    if len(frontier) != 10:
        no(f"fixture parsed {len(frontier)} frontier rows, expected 10 "
           f"(the fixture or the parser changed)")
    else:
        ok("fixture parses to 10 frontier rows")

    hidden = [r.identifier for r in frontier if r.identifier not in text]
    if hidden:
        no(f"frontier rows missing from the render: {', '.join(hidden)}")
    else:
        ok("all 10 frontier rows render, whatever their bracket")

    # The catch-all must show the bracket VERBATIM — a row that renders under a
    # laundered label is only half-visible; the user needs to see what state the
    # row actually claims so they know what to fix.
    if "**[purple monkey dishwasher]**" in text:
        ok("unknown bracket is shown verbatim, not laundered")
    else:
        no("unknown bracket text absent — the catch-all is hiding the bracket")

    if "**[no state]**" in text:
        ok("bracketless row is labeled `[no state]` rather than blank")
    else:
        no("bracketless row has no visible state marker")

    # The assertion is the structural gate — it must be silent when coverage
    # holds, or it is noise nobody will read when it does fire.
    if "Coverage failure" in text:
        no("coverage assertion fired on a fully-covered render")
    else:
        ok("coverage assertion silent when the partition holds")

    # Totality is scoped to the frontier ON PURPOSE (F284 § Scope note): `Later`
    # is deferred-by-choice and rendering all of it would bury the frontier.
    if "F011" in text:
        no("a `## Later` row leaked into the render — scope creep past the frontier")
    else:
        ok("`## Later` stays out of scope")

    if "F012" in text:
        no("a `[Done]` row rendered")
    else:
        ok("`[Done]` rows stay out")

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
