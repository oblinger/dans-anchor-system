#!/usr/bin/env python3
"""T128 — a multi-line `--next` corrupted the row, and the guard reported it
without undoing it.

Two defects on one write, hit live 2026-08-05 while widening a Next.

**The corruption.** A sub-bullet is one line. `_ensure_subbullet` writes
`f"  - **{label}:** {text}\\n"` with no check that `text` is single-line. Pass a
value containing a newline — trivially easy, since `--next "$(cat file)"`
preserves internal newlines and any appended-to file has one — and the tail
lands as an **orphan line** that belongs to no sub-bullet, sits inside the row's
span, and is invisible to `_row_field`. audit-q reported 0 findings over the
corrupted row, so nothing downstream caught it either.

**The half-guard, which is the real defect.** `verify_write_landed` DID detect
it and raised — but `write_backlog_lines` ran *before* the check with no
rollback, so the CLI correctly reported failure over a file it had already
corrupted. The operator read that as "the write did not land" and committed the
damage. A guard that runs after an unconditional write can report, never
protect.

    python3 test-t128-multiline-subbullet.py
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.util
import sys
import tempfile
from pathlib import Path

_S = (Path(__file__).parent / "backlog-edit.py").resolve()
_spec = importlib.util.spec_from_file_location("be", _S)
be = importlib.util.module_from_spec(_spec)
sys.modules["be"] = be
_spec.loader.exec_module(be)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


ROW = ("# T Backlog\n\n## Later\n\n"
       "- **T900 — a row** [Ready] — a parked row. ^T900\n"
       "  - **Next:** the original single-line step.\n")


def fresh():
    td = tempfile.TemporaryDirectory()
    bl = Path(td.name) / "T Backlog.md"
    bl.write_text(ROW, encoding="utf-8")
    return td, bl


print("_refuse_multiline_subbullets — the argument boundary")

for flag, kwargs in (("--next", {"next_text": "line one\nline two"}),
                     ("--verify", {"verify_text": "did it?\nand also?"}),
                     ("--user", {"user_text": "log in\nthen click"})):
    try:
        be._refuse_multiline_subbullets(
            kwargs.get("verify_text"), kwargs.get("next_text"),
            kwargs.get("user_text"))
        check(f"{flag} with a newline is refused", "accepted", "refused")
    except be.BacklogEditError as exc:
        check(f"{flag} with a newline is refused", "refused", "refused")
        check(f"...and the message names {flag}", flag in str(exc), True)
        # No-silent-fallback: the caller passed two paragraphs and meant two
        # paragraphs. Telling them where the long form goes is the whole point
        # of refusing rather than joining.
        check("...and names the fix (collapse it, or use the body)",
              "Collapse" in str(exc) and "--body" in str(exc), True)

# A trailing newline is the shell's, not the caller's — but it is still a
# newline the writer would emit verbatim, so it is refused too rather than
# quietly stripped. Stripping here would re-introduce the guess this refusal
# exists to avoid.
try:
    be._refuse_multiline_subbullets(None, "one line\n", None)
    check("a trailing newline is refused too", "accepted", "refused")
except be.BacklogEditError:
    check("a trailing newline is refused too", "refused", "refused")

# Non-regression: everything legal still passes straight through.
check("single-line values pass",
      be._refuse_multiline_subbullets("a?", "b", "c"), None)
check("None values pass", be._refuse_multiline_subbullets(None, None, None),
      None)
check("the empty string (a REMOVAL, per T122) still passes",
      be._refuse_multiline_subbullets("", "", ""), None)


print("\nEnd-to-end — the write leaves the file byte-identical on refusal")

td, bl = fresh()
before = bl.read_text(encoding="utf-8")
try:
    be.perform_edit(bl, "Later", "T900", "same", None, None, False, False,
                    next_text="do the thing\nand then the other thing")
    check("a multi-line --next through perform_edit raises", "no", "yes")
except be.BacklogEditError:
    check("a multi-line --next through perform_edit raises", "yes", "yes")
check("...and the backlog is byte-identical afterwards",
      bl.read_text(encoding="utf-8"), before)
# The failure that actually happened: the tail became an orphan line inside the
# row span, belonging to no sub-bullet and invisible to `_row_field`.
check("...with no orphan line left behind",
      "and then the other thing" in bl.read_text(encoding="utf-8"), False)


print("\nRollback — a failed post-condition undoes its own write")

# Drive the guard to fail on a write that DID happen, by making the landing
# check disagree with what the writer produced. This is the shape T128 hit: the
# write succeeded in its own terms and the post-condition rejected the result.
td2, bl2 = fresh()
before2 = bl2.read_text(encoding="utf-8")
_real = be.verify_write_landed
be.verify_write_landed = lambda lines, row_id, requested: (
    [] if requested.get("status") == "delete" else ["synthetic post-condition failure"])
try:
    try:
        be.perform_edit(bl2, "Later", "T900", "same", None, None, False, False,
                        next_text="a perfectly legal single-line step")
        check("a failed post-condition raises", "no", "yes")
    except be.BacklogEditError as exc:
        check("a failed post-condition raises", "yes", "yes")
        check("...and says the file was restored",
              "restored" in str(exc), True)
    check("...and the file really is back to its pre-edit contents",
          bl2.read_text(encoding="utf-8"), before2)
finally:
    be.verify_write_landed = _real

# The delete path had the same shape — write, then verify, with no undo. A
# half-applied delete is the worst failure this file can hold.
td3, bl3 = fresh()
before3 = bl3.read_text(encoding="utf-8")
be.verify_write_landed = lambda lines, row_id, requested: ["synthetic failure"]
try:
    try:
        be.perform_edit(bl3, "Later", "T900", "delete", None, None, False, False)
        check("a failed delete post-condition raises", "no", "yes")
    except be.BacklogEditError:
        check("a failed delete post-condition raises", "yes", "yes")
    check("...and the deleted row is back", bl3.read_text(encoding="utf-8"),
          before3)
finally:
    be.verify_write_landed = _real


print("\nNon-regression — a legal write still lands")

td4, bl4 = fresh()
be.perform_edit(bl4, "Later", "T900", "same", None, None, False, False,
                next_text="a single-line replacement step.")
after4 = bl4.read_text(encoding="utf-8")
check("the new Next is on disk",
      "- **Next:** a single-line replacement step." in after4, True)
check("...and the old one is gone",
      "the original single-line step" in after4, False)
check("...and the row survived",
      "- **T900 — a row** [Ready]" in after4, True)


print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
