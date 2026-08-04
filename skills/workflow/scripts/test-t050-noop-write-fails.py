#!/usr/bin/env python3
"""test-t050-noop-write-fails.py — T050: a write that didn't land exits non-zero.

`state set` could report `updated <row>` and exit 0 while changing nothing.
A mutation tool that can silently not-mutate makes every "I recorded it"
claim unfalsifiable, and the backlog is the project's memory. T046 fixed the
one control-flow path that dropped `--next` on a Verify-family row; this is
the general guarantee, so the NEXT such path is caught by the tool instead of
by someone noticing months later.

Design note — why this checks the post-condition rather than file bytes.
T050 proposed comparing whole-file bytes and warned the `state:backlog` stamp
would make that vacuous. **That premise is false, and this file pins the
measurement** (section 5): the stamp is a content hash, so a no-op leaves the
bytes identical. Bytes would have "worked" — and would still be the wrong
design, because an INTENTIONAL re-touch (setting a field to the value it
already holds) is legitimate and also produces zero byte change. Bytes cannot
separate "asked and failed" from "asked and it already matched"; the
post-condition separates them by construction.

Self-contained: imports backlog-edit.py in-process, writes only to a tempdir.
"""
import importlib.machinery
import importlib.util
import pathlib
import sys
import tempfile

BE = pathlib.Path(__file__).parent / "backlog-edit.py"
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


SRC = """# Scratch Backlog

## Now

- **T900 — A scratch row** [Ready] — original body. ^T900
  - **Next:** original next

- **T901 — A row under verification** [Verify] — body. ^T901
  - **Verify:** Did it recur? no = held

## Done

"""


def fresh():
    d = tempfile.mkdtemp()
    p = pathlib.Path(d) / "SCR Backlog.md"
    p.write_text(SRC)
    return p


def edit(p, **kw):
    args = dict(backlog_path=p, horizon="Now", row_id_arg="T900", status="Ready",
                title=None, body=None, title_provided=False, body_provided=False)
    args.update(kw)
    return be.perform_edit(**args)


def lines_of(p):
    return p.read_text().splitlines(keepends=True)


print("1. The guard is SILENT on writes that genuinely landed")

p = fresh()
edit(p, next_text="CANARY-NEXT")
if be._row_field(lines_of(p), "T900", "Next") == "CANARY-NEXT":
    ok("an ordinary --next lands and the guard does not object")
else:
    no("the --next did not land at all")

p = fresh()
edit(p, row_id_arg="T901", horizon="Now", status="Verify", next_text="CANARY-V")
if be._row_field(lines_of(p), "T901", "Next") == "CANARY-V":
    ok("the T046 case (a --next on a Verify-family row) still lands")
else:
    no("--next on a Verify row was dropped — T046 regressed")

print("2. THE requirement — an INTENTIONAL re-touch must NOT become an error")

# This is the case that rules out T050's proposed byte comparison: setting a
# field to the value it already holds changes zero bytes and is legitimate.
p = fresh()
edit(p, next_text="SAME-VALUE")
try:
    edit(p, next_text="SAME-VALUE")
    ok("re-setting a field to the value it already holds is accepted")
except SystemExit as e:
    no(f"a legitimate identical re-touch was rejected: {e}")

print("3. RED CHECK — the guard actually fires when a mutation is dropped")

# Simulate the T046 defect class: the dispatch decides to write no Next at
# all. Without the guard this is exactly the silent success T050 exists to
# kill. If this section does not raise, the guard proves nothing.
p = fresh()
real = be._subbullets_to_write
be._subbullets_to_write = lambda *a, **k: []      # drop every sub-bullet
try:
    edit(p, next_text="WILL-BE-DROPPED")
    no("a DROPPED --next was reported as success — the guard is inert")
except SystemExit as e:
    if "Next" in str(e) and "T900" in str(e):
        ok(f"dropped --next raises and names the row + field: {str(e)[:60]}…")
    else:
        no(f"raised, but the message identifies nothing useful: {e}")
finally:
    be._subbullets_to_write = real

# Same red check for the row line itself (status/title/body), driving the
# pure verifier so the failure text is pinned without corrupting a file.
got = be.verify_write_landed(
    ["- **T900 — A scratch row** [Ready] — original body. ^T900\n"],
    "T900", {"status": "Done"})
if got and "status" in got[0]:
    ok("a status that did not take is reported, naming the asked-for value")
else:
    no(f"a wrong status went unreported: {got!r}")

got = be.verify_write_landed(
    ["- **T900 — A scratch row** [Ready] — original body. ^T900\n"],
    "T900", {"status": "Ready", "body": "TEXT THAT IS NOT THERE"})
if got and "body" in got[0]:
    ok("a body that did not take is reported")
else:
    no(f"a missing body went unreported: {got!r}")

got = be.verify_write_landed([], "T900", {"status": "Ready"})
if got and "absent" in got[0]:
    ok("a row that vanished entirely is reported")
else:
    no(f"a vanished row went unreported: {got!r}")

got = be.verify_write_landed(
    ["- **T900 — A scratch row** [Ready] — body. ^T900\n"],
    "T900", {"status": "delete"})
if got and "still present" in got[0]:
    ok("a delete that left the row behind is reported")
else:
    no(f"a failed delete went unreported: {got!r}")

print("4. No false positives on the shapes the writer legitimately produces")

# `[Verify-by 2026-09-01]` / `[Blocked foo]` carry the family as a prefix;
# the caller asked for the family, so the annotated bracket must be accepted.
for stored, asked in (("Verify-by 2026-09-01", "Verify-by"),
                      ("Blocked foo.bar", "Blocked"),
                      ("Done — watch closed", "Done")):
    got = be.verify_write_landed(
        [f"- **T900 — A row** [{stored}] — body. ^T900\n"], "T900",
        {"status": asked})
    if got == []:
        ok(f"[{stored}] satisfies a request for [{asked}]")
    else:
        no(f"[{stored}] wrongly rejected for [{asked}]: {got!r}")

# A field the caller did NOT ask for must never be checked.
got = be.verify_write_landed(
    ["- **T900 — A row** [Ready] — body. ^T900\n"], "T900",
    {"status": "Ready", "next_text": None, "verify_text": None})
if got == []:
    ok("fields the caller never asked for are not checked")
else:
    no(f"an unrequested field was checked: {got!r}")

print("5. Pin the corrected premise — a no-op leaves bytes IDENTICAL")

# T050's Next asserted the state stamp is "rewritten on every call, so
# whole-file bytes are never actually identical." Measured here instead of
# inherited: `compute_backlog_stamp` sha1s the span with the stamp line
# excluded, so identical content yields an identical stamp. Kept as a test so
# a future agent doesn't reintroduce the byte compare on the strength of a
# claim that was never true.
p = fresh()
edit(p, next_text="STABLE")
a = p.read_bytes()
edit(p, next_text="STABLE")
b = p.read_bytes()
if a == b:
    ok("an identical re-touch is byte-identical (so bytes alone can't detect a no-op)")
else:
    no("bytes differed across an identical re-touch — re-derive the T050 premise")

edit(p, next_text="MOVED")
if p.read_bytes() != b:
    ok("a real change does change bytes (the comparison above is not blind)")
else:
    no("a real change left bytes identical — the byte check is broken")

print()
print(f"{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
