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

WHY IT NOW REFUSES (Dan, 2026-08-28). It warned from 2026-08-20 because the
`/feature` mint path set a row's pointer with
`--body "→ [[doc|F001]] — F001 — Title"` and a refusal would have failed every
mint. Dan ruled that a tool must never half-succeed — "half of what you asked
for" is the semantics that confuses the agent — so `state set --doc NAME`
now writes the pointer alone (the mint path uses it), and a `--body` whose
prose would be discarded is refused outright with nothing written.

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
    print("== A: the discard is real, and a --body that would hit it is refused ==")
    # ============================================================
    build()
    run("set", "FIX", "Backlog", "T001", "--body", "CANARYPLAIN.")
    if "CANARYPLAIN." in BACKLOG.read_text():
        ok("a plain row takes --body — the control that makes the rest meaningful")
    else:
        no("--body did not land on a plain row; the fixture proves nothing")

    build()
    run("set", "FIX", "Backlog", "F001", "--status", "Ready")   # settle the F247 stamp
    before = BACKLOG.read_text()
    out = run("set", "FIX", "Backlog", "F001", "--body",
              "→ [[FIX001 - A doc-backed feature|F001]] — CANARYDOC.")
    text = BACKLOG.read_text()
    if "CANARYDOC." not in text:
        ok("a doc-backed row never carries the prose (the documented F332 behaviour)")
    else:
        no("the prose landed — F332's regeneration is not running")

    if "updated F001" not in out and "refus" in out.lower():
        ok("and the call REFUSES rather than reporting success")
    else:
        no(f"expected a refusal with no `updated F001`, got: {out[:200]}")

    if text == before:
        ok("a refused call changes nothing — no half-landed link")
    else:
        no("the backlog changed on a refused call")

    # ============================================================
    print("== B: the refusal fires only where a discard would have happened ==")
    # ============================================================
    build()
    if warned(run("set", "FIX", "Backlog", "F001", "--body",
                  "→ [[FIX001 - A doc-backed feature|F001]] — CANARYDOC.")):
        ok("pointer-led body with prose → refused")
    else:
        no("the discard is silent on a pointer-led body")

    # The carried case. A body with no pointer gains one from T174 and is then
    # discarded exactly like the case above — joined with `·`, not an em-dash,
    # which is what the first cut of this check missed.
    build()
    if warned(run("set", "FIX", "Backlog", "F001", "--body", "PLAINPROSE.")):
        ok("plain prose on a doc-backed row → refused (T174 carry, `·` separator)")
    else:
        no("a carried body is still silent — the separator assumption is back")

    build()
    out = run("set", "FIX", "Backlog", "F001", "--body",
              "→ [[FIX001 - A doc-backed feature|F001]]")
    if not warned(out) and "updated F001" in out:
        ok("pointer with no prose → accepted, because nothing is discarded")
    else:
        no("refused a body that asked for nothing after the pointer")

    build()
    if not warned(run("set", "FIX", "Backlog", "F001", "--status", "Active")):
        ok("a touch that passes no --body → quiet")
    else:
        no("refused a call that never supplied a body")

    build()
    out = run("set", "FIX", "Backlog", "F001", "--next", "a real next step")
    if not warned(out) and "a real next step" in BACKLOG.read_text():
        ok("--next → lands, and it is what the refusal tells the caller to use")
    else:
        no("--next failed, the flag the message recommends")

    build()
    if not warned(run("set", "FIX", "Backlog", "T001", "--body", "CANARYPLAIN.")):
        ok("a genuinely plain row → quiet")
    else:
        no("refused a row with no doc pointer at all")

    # ============================================================
    print("== C: the message names the flags that work ==")
    # ============================================================
    build()
    out = run("set", "FIX", "Backlog", "F001", "--body",
              "→ [[FIX001 - A doc-backed feature|F001]] — CANARYDOC.")
    if "--next" in out and "--doc" in out:
        ok("the refusal names `--next` and `--doc`, so the caller is not left guessing")
    else:
        no("the refusal does not say what to use instead")

    env = {**os.environ, "ANCHOR_VAULT_ROOT": str(ROOT)}
    build()
    r = subprocess.run(
        [sys.executable, str(STATE), "set", "FIX", "Backlog", "F001", "--body",
         "→ [[FIX001 - A doc-backed feature|F001]] — CANARYDOC."],
        capture_output=True, text=True, env=env)
    if "doc-backed row" in r.stderr and r.returncode != 0:
        ok("it goes to stderr and exits non-zero, so a sweeping script sees it")
    else:
        no(f"refusal not on stderr / exit 0 (rc={r.returncode})")

    # ============================================================
    print("== D: the /feature mint path runs on --doc ==")
    # ============================================================
    build()
    out = run("set", "FIX", "Backlog", "T001", "--doc", "FIX001 - A doc-backed feature")
    if "updated T001" in out and "refus" not in out.lower():
        ok("minting a pointer onto a plain row via --doc succeeds")
    else:
        no(f"the --doc mint path fails: {out[:200]}")

    text = BACKLOG.read_text()
    if "→ [[FIX001 - A doc-backed feature|T001]]" in text:
        ok("the pointer landed, aliased to the row id")
    else:
        no("the pointer did not land; the mint path is broken")

    if "the doc's own next field" in text:
        ok("and the trailing text regenerated from the doc (F332)")
    else:
        no("the row does not carry the derived line after --doc")

    build()
    out = run("set", "FIX", "Backlog", "T001", "--doc", "FIX001 - A doc-backed feature",
              "--body", "anything")
    if "exclusive" in out:
        ok("--doc with --body is refused as exclusive")
    else:
        no(f"--doc + --body was not refused: {out[:200]}")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
