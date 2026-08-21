#!/usr/bin/env python3
"""test-t578-derived-body-warning.py — TINK T578.

`state set --body` on a doc-backed row reported `updated <row>` and wrote
nothing. Reported by MUX 2026-08-20 across a 2x2 (Done/Verify x doc-backed/
plain) and reproduced here in a fixture before anything was changed.

WHAT THE DEFECT IS, PRECISELY — because the obvious reading is wrong. The
discard itself is CORRECT and documented: `regenerate_derived_row` says
"hand text after the pointer is overwritten here", so on a pointer-led row
only the LINK is the caller's and the trailing text belongs to the doc. The
defect is that nothing said so. `verify_write_landed`'s F332 branch compares
only the wiki-link target for two derived bodies and returns clean, which is
right given that contract and is also why it could not be the thing that
announced it.

WHY A WARNING RATHER THAN THE REFUSAL THE ROW PROPOSED. Measured: the
`/feature` mint path sets a row's pointer with
`--body "→ [[doc|F001]] — F001 — Title"`, and its trailing text is discarded
by this same rule. A refusal would turn every feature mint into an error. The
link half genuinely lands, so the honest report is "half of what you asked
for" — not a failure, and not silence.

THE CASE THAT ALMOST GOT MISSED, kept as a case of its own: a body with NO
pointer does not stay pointerless. T174's carry puts the row's existing
`→ [[doc]]` back on, which makes it derived, which sends it through the same
discard. So a caller passing plain prose to a doc-backed row loses it too —
and the first cut of the warning missed exactly that, because the carry joins
with `·` while the canonical form joins with an em-dash. Splitting on one
separator character silently skipped every carried body.
"""
import sys as _sys; _sys.dont_write_bytecode = True

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "state"
TMP = Path(tempfile.mkdtemp())

PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  PASS: {m}")


def no(m):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {m}")


ROOT = TMP / "vault"
ANCHOR = ROOT / "FIX"
BACKLOG = ANCHOR / "FIX Track" / "FIX Backlog" / "FIX Backlog.md"
DOC = ANCHOR / "FIX Design" / "FIX Features" / "FIX001 - A doc-backed feature.md"

ROWS = """---
description: fixture backlog
---

# FIX Backlog

## Now

- **T001 — A plain row with no feature doc** [Ready] — original plain body. ^T001
  - **Next:** do the plain thing.
- **F001 — A doc-backed feature** [Ready] — → [[FIX001 - A doc-backed feature|F001]] — original doc-backed body. ^F001
  - **Next:** do the doc-backed thing.

## Next

## Later

## Done
"""

FEATURE = """---
description: fixture feature
---

# [[FIX]] · F001 — A doc-backed feature
One line.

next:: the doc's own next field

## Summary

Fixture.

## Status

Ready — fixture.
"""


def build():
    """A fresh vault per case — these calls mutate the backlog they read."""
    shutil.rmtree(ROOT, ignore_errors=True)
    BACKLOG.parent.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(parents=True, exist_ok=True)
    (ANCHOR / ".anchor").write_text("slug: FIX\nfeeds:\n", encoding="utf-8")
    BACKLOG.write_text(ROWS, encoding="utf-8")
    DOC.write_text(FEATURE, encoding="utf-8")


def run(*args):
    env = {**os.environ, "ANCHOR_VAULT_ROOT": str(ROOT)}
    r = subprocess.run([sys.executable, str(STATE), *args],
                       capture_output=True, text=True, env=env)
    return r.stdout + r.stderr


def warned(out):
    return "doc-backed row" in out


try:
    # ============================================================
    print("== A: the discard is real, and it is silent without this fix ==")
    # ============================================================
    build()
    run("set", "FIX", "Backlog", "T001", "--body", "CANARYPLAIN.")
    if "CANARYPLAIN." in BACKLOG.read_text():
        ok("a plain row takes --body — the control that makes the rest meaningful")
    else:
        no("--body did not land on a plain row; the fixture proves nothing")

    build()
    out = run("set", "FIX", "Backlog", "F001", "--body",
              "→ [[FIX001 - A doc-backed feature|F001]] — CANARYDOC.")
    text = BACKLOG.read_text()
    if "CANARYDOC." not in text:
        ok("a doc-backed row discards the prose (the documented F332 behaviour)")
    else:
        no("the prose landed — F332's regeneration is not running")

    if "updated F001" in out:
        ok("and the call still reports success, which is why silence was the bug")
    else:
        no(f"expected an `updated F001` report, got: {out[:200]}")

    if "the doc's own next field" in text:
        ok("the row carries the doc's `next::`, not the caller's text")
    else:
        no("the row does not carry the derived line")

    # ============================================================
    print("== B: the discard is announced, and only where it happened ==")
    # ============================================================
    build()
    if warned(run("set", "FIX", "Backlog", "F001", "--body",
                  "→ [[FIX001 - A doc-backed feature|F001]] — CANARYDOC.")):
        ok("pointer-led body with prose → warned")
    else:
        no("the discard is still silent on a pointer-led body")

    # The carried case. A body with no pointer gains one from T174 and is then
    # discarded exactly like the case above — joined with `·`, not an em-dash,
    # which is what the first cut of this warning missed.
    build()
    if warned(run("set", "FIX", "Backlog", "F001", "--body", "PLAINPROSE.")):
        ok("plain prose on a doc-backed row → warned (T174 carry, `·` separator)")
    else:
        no("a carried body is still silent — the separator assumption is back")

    build()
    if not warned(run("set", "FIX", "Backlog", "F001", "--body",
                      "→ [[FIX001 - A doc-backed feature|F001]]")):
        ok("pointer with no prose → quiet, because nothing was discarded")
    else:
        no("warned about a body that asked for nothing after the pointer")

    build()
    if not warned(run("set", "FIX", "Backlog", "F001", "--status", "Active")):
        ok("a touch that passes no --body → quiet")
    else:
        no("warned on a call that never supplied a body")

    build()
    if not warned(run("set", "FIX", "Backlog", "F001", "--next", "a real next step")):
        ok("--next → quiet, and it is what the warning tells the caller to use")
    else:
        no("warned on --next, the flag the message recommends")

    build()
    if not warned(run("set", "FIX", "Backlog", "T001", "--body", "CANARYPLAIN.")):
        ok("a genuinely plain row → quiet")
    else:
        no("warned on a row with no doc pointer at all")

    # ============================================================
    print("== C: the message names the flag that works ==")
    # ============================================================
    build()
    out = run("set", "FIX", "Backlog", "F001", "--body",
              "→ [[FIX001 - A doc-backed feature|F001]] — CANARYDOC.")
    if "--next" in out:
        ok("the warning names `--next`, so the caller is not left guessing")
    else:
        no("the warning does not say what to use instead")

    # A warning that does not survive being piped is no warning at all: the
    # caller here is usually a script, and MUX's case was a batch sweep.
    env = {**os.environ, "ANCHOR_VAULT_ROOT": str(ROOT)}
    build()
    r = subprocess.run(
        [sys.executable, str(STATE), "set", "FIX", "Backlog", "F001", "--body",
         "→ [[FIX001 - A doc-backed feature|F001]] — CANARYDOC."],
        capture_output=True, text=True, env=env)
    if "doc-backed row" in r.stderr:
        ok("it goes to stderr, so a script capturing stdout still sees it")
    else:
        no("the warning is on stdout — a sweep piping stdout would swallow it")

    # ============================================================
    print("== D: the /feature mint path is not broken by this ==")
    #
    # The reason this is a warning rather than the refusal T578 proposed. The
    # mint gives a plain row its pointer via --body and has its trailing text
    # discarded by the same rule; a refusal would fail every feature mint.
    # ============================================================
    build()
    out = run("set", "FIX", "Backlog", "T001", "--body",
              "→ [[FIX001 - A doc-backed feature|T001]] — T001 — A plain row")
    if "updated T001" in out and "refus" not in out.lower():
        ok("minting a pointer onto a row still succeeds")
    else:
        no(f"the mint path now fails: {out[:200]}")

    if "→ [[FIX001 - A doc-backed feature|T001]]" in BACKLOG.read_text():
        ok("and the link — the half that is the caller's — landed")
    else:
        no("the pointer did not land; the mint path is broken")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
