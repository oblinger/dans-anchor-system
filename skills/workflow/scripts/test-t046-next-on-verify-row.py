#!/usr/bin/env python3
"""test-t046-next-on-verify-row.py — T046: an explicit `--next` is never dropped.

`state set <anchor> Backlog <row> --next "…"` on a **Verify-family** row printed
`updated <row>` and exited 0 while changing nothing. Two live victims: F193's
Next silently no-opped and only applied on a retry because an intervening
`--status`/`--horizon` call had moved the row out of Verify; T011's stayed
uncorrected, because [Verify] is the CORRECT bracket for it, so there was no
legitimate way to move the row just to make an edit land. The reachable-but-
uneditable set was every Verify-horizon row — precisely the rows carrying the
user's open verifications.

Cause: the sub-bullet dispatch was one `elif` chain. On a Verify-family row the
Verify branch matched, and the `--next` the caller passed fell off the end of
the chain. The `[User]` branch had already been given the same treatment for the
same reason (it writes User AND, separately, a queued Next); this generalises it.

A mutation tool that can silently not-mutate makes every "I recorded it" claim
unfalsifiable, and the backlog is the project's memory — same failure class as
`define --from-file` truncating a row while printing success.

Self-contained: imports backlog-edit.py in-process, touches no vault file."""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

BE = Path(__file__).parent / "backlog-edit.py"
loader = importlib.machinery.SourceFileLoader("be_mod", str(BE))
spec = importlib.util.spec_from_loader("be_mod", loader)
be = importlib.util.module_from_spec(spec)
sys.modules["be_mod"] = be
loader.exec_module(be)
be._selffire = lambda *a, **k: None

PASS = 0
FAIL = 0


def ok(m):
    globals().__setitem__("PASS", PASS + 1)
    print(f"  PASS: {m}")


def no(m):
    globals().__setitem__("FAIL", FAIL + 1)
    print(f"  FAIL: {m}")


def sub(lines, row_id, label):
    """The text of row_id's `- **<label>:**` sub-bullet, or None."""
    import re
    seen = False
    for l in lines:
        if re.match(rf"^- \*\*{re.escape(row_id)}\b", l):
            seen = True
            continue
        if seen:
            if l.startswith("- ") or l.startswith("## "):
                break
            m = re.match(rf"^\s+- \*\*{label}:\*\* (.*)$", l)
            if m:
                return m.group(1).strip()
    return None


print("1. `_ensure_subbullet` writes Next and Verify independently on one row")

lines = [
    "## Verify\n",
    "- **T900 — A row under verification** [Verify] — body. ^T900\n",
    "  - **Verify:** Did the thing recur? no = held\n",
    "\n",
]
be._ensure_subbullet(lines, "T900", "Next", "CANARY-NEXT")
got = sub(lines, "T900", "Next")
if got == "CANARY-NEXT":
    ok("Next lands on a Verify-bracketed row")
else:
    no(f"Next did not land on a Verify row: {got!r}")

if sub(lines, "T900", "Verify") == "Did the thing recur? no = held":
    ok("the row's existing Verify sub-bullet is preserved alongside it")
else:
    no("writing Next clobbered the Verify sub-bullet")

print("2. THE regression — the dispatch honours an explicit --next in every family")

# This is the test that matters: it drives `_subbullets_to_write`, the dispatch
# itself, NOT `_ensure_subbullet` (which was never the broken part — an earlier
# draft of this file asserted against the writer and passed against the bug).
# `next_text` is what `--next` sets; `eff_*` are the row's effective values.
for status, eff_verify, eff_user in [
    ("Verify", "q?", None),
    ("Verify-by 2026-09-01", "q?", None),
    ("Watching", "q?", None),
    ("User", None, "do a thing"),
    ("Blocked", None, None),
    ("Questions", None, None),
    ("Ready", None, None),
    ("Active", None, None),
]:
    got = be._subbullets_to_write(status, eff_verify, "CANARY", eff_user, "CANARY")
    nexts = [t for (l, t) in got if l == "Next"]
    if nexts == ["CANARY"]:
        ok(f"[{status}] keeps an explicit --next (exactly once)")
    else:
        no(f"[{status}] dropped or duplicated an explicit --next: {got!r}")

print("3. …without losing the sub-bullet the bracket requires")

got = be._subbullets_to_write("Verify", "the question", None, None, "CANARY")
if ("Verify", "the question") in got and ("Next", "CANARY") in got:
    ok("a Verify row gets BOTH its Verify question and the explicit Next")
else:
    no(f"Verify row lost one of the two: {got!r}")

got = be._subbullets_to_write("User", None, None, "user step", "CANARY")
if ("User", "user step") in got and ("Next", "CANARY") in got:
    ok("a User row keeps its User step alongside the queued Next")
else:
    no(f"User row lost one of the two: {got!r}")

print("4. No --next passed → no Next is invented, and no re-ordering re-touch")

got = be._subbullets_to_write("Verify", "q?", "PRE-EXISTING", None, None)
if [t for (l, t) in got if l == "Next"] == []:
    ok("a plain re-touch of a Verify row does not rewrite its Next")
else:
    no(f"re-touch invented a Next: {got!r}")

got = be._subbullets_to_write("Ready", None, "PRE-EXISTING", None, None)
if ("Next", "PRE-EXISTING") in got:
    ok("a Ready row still (re)attaches its required Next from the effective value")
else:
    no(f"Ready row lost its required Next: {got!r}")

got = be._subbullets_to_write("Blocked", None, "PRE-EXISTING", None, None)
if [t for (l, t) in got if l == "Next"] == []:
    ok("a Blocked row does not gain a Next nobody asked for")
else:
    no(f"Blocked row invented a Next: {got!r}")

print("3. Re-writing a Next replaces it rather than duplicating it")

ls = [
    "## Verify\n",
    "- **T902 — Row** [Verify] — body. ^T902\n",
    "  - **Verify:** q?\n",
    "  - **Next:** OLD\n",
    "\n",
]
be._ensure_subbullet(ls, "T902", "Next", "NEW")
count = sum(1 for l in ls if l.strip().startswith("- **Next:**"))
if count == 1 and sub(ls, "T902", "Next") == "NEW":
    ok("exactly one Next sub-bullet, carrying the new text")
else:
    no(f"expected 1 Next == 'NEW', got {count} / {sub(ls, 'T902', 'Next')!r}")

print()
print(f"{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
