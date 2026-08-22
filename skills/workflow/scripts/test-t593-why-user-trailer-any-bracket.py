#!/usr/bin/env python3
"""test-t593-why-user-trailer-any-bracket.py — TINK T593: an explicit
`--why-user` is folded into the Verify text whatever the bracket.

Fifth round of the write-when-explicitly-passed family (Next T046, Verify
T123/T560, User T236, Probe from birth). `perform_edit` gated the F240
trailer fold-in on `_verify_family(status)`, so on a `[Waiting]` row the
`· *why-user: …*` trailer was accepted, threaded, and dropped — and a trailer
the row already carried was wiped in the same write (Scout, 2026-08-22, on
the exact row T560 existed to fix).

Run: python3 test-t593-why-user-trailer-any-bracket.py
"""
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

BE = Path(__file__).parent / "backlog-edit.py"
_loader = importlib.machinery.SourceFileLoader("be_mod_t593", str(BE))
_spec = importlib.util.spec_from_loader("be_mod_t593", _loader)
be = importlib.util.module_from_spec(_spec)
sys.modules["be_mod_t593"] = be
_loader.exec_module(be)

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}  {detail}")
        FAILURES.append(name)


BACKLOG = """# TEST Backlog

## Now

- **T019 — soak row** [Waiting 2026-09-20] — parked until the date ^T019
  - **Verify:** old question · *why-user: old faculty*

## Done
"""


def run_edit(text, **kw):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "TEST Backlog.md"
        p.write_text(text)
        args = dict(horizon="same", row_id_arg="T019", status="same",
                    title=None, body=None, title_provided=False,
                    body_provided=False)
        args.update(kw)
        be.perform_edit(p, **args)
        return p.read_text()


# 1. Scout's repro: --verify + --why-user on a [Waiting] row → trailer lands
out = run_edit(BACKLOG, verify_text="is the soak clean?",
               why_user="passive-use observation over the soak window")
check("trailer folded on [Waiting]",
      "*why-user: passive-use observation over the soak window*" in out,
      detail=out)

# 2. The wipe: the OLD trailer must not survive doubled, and must be replaced
check("old trailer replaced, not doubled",
      out.count("*why-user:") == 1, detail=out)

# 3. --verify alone must keep the behaviour T560 pinned (text written) and
#    NOT invent a trailer
out2 = run_edit(BACKLOG, verify_text="is the soak clean?")
check("verify text written without why-user",
      "is the soak clean?" in out2, detail=out2)
check("no trailer invented", "*why-user: passive" not in out2)

# 4. --why-user alone (no verify text passed, row has one) still folds onto
#    the existing question
out3 = run_edit(BACKLOG, why_user="ratification of the parked plan")
check("trailer folded onto existing question",
      "old question · *why-user: ratification of the parked plan*" in out3,
      detail=out3)

# 5. No flags → byte-stable sub-bullet (the T056 no-op guarantee)
out4 = run_edit(BACKLOG)
check("no flags → row untouched",
      "old question · *why-user: old faculty*" in out4, detail=out4)

print()
if FAILURES:
    print(f"test-t593: {len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("test-t593-why-user-trailer-any-bracket: all checks pass")
