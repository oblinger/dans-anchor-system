#!/usr/bin/env python3
"""T122 — `state` could never REMOVE a companion sub-bullet.

`perform_edit` deliberately distinguishes *not provided* from *provided empty*:

    eff_verify = verify_text if verify_text is not None else existing_verify
    # "The provided flag wins; else preserve the existing sub-bullet."

The plumbing to carry a removal was therefore already built. The write path
ignored it — every arm of `_subbullets_to_write` gates on `and eff_x`, so an
empty string fell through, the line on disk stayed, and the CLI printed
`updated`. That is T056's defect class (an accepted argument reported as applied
and discarded) in the one direction T056 did not cover.

`verify_write_landed` could not catch it either: it skipped anything falsy, so
it only ever asserted that requested text IS present. A guard that cannot see a
negative cannot catch a discarded one.

The case that needs this is a Verify on a bracket that does NOT require one — a
WITHDRAWN check rather than a deferred one. Measured before filing: of 494
companion sub-bullets sitting on a non-requiring bracket across 41 backlogs, 421
are `[Done]` rows whose Next/Verify is the archived record of what happened, and
12 of the remaining 13 are `[Waiting]` rows holding a genuinely deferred check
awaiting natural exercise. Exactly one is a withdrawal: F275, whose user-facing
question Dan cancelled while the row sat `[Waiting]`.

    python3 test-t122-subbullet-removal.py
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


print("_subbullets_to_write — an empty flag emits a REMOVAL, text is None")

# The live shape: a [Waiting] row carrying a Verify the bracket never required.
# No status arm reaches it (`_verify_family('Waiting')` is False), which is why
# the removal has to be unconditional rather than another arm of the chain.
check("Waiting + eff_verify='' → remove Verify",
      be._subbullets_to_write("Waiting", "", None, None, None),
      [("Verify", None)])
check("...and _verify_family('Waiting') really is False — no arm would reach it",
      be._verify_family("Waiting"), False)

check("Waiting + eff_next='' → remove Next",
      be._subbullets_to_write("Waiting", None, "", None, ""),
      [("Next", None)])
check("Waiting + eff_user='' → remove User",
      be._subbullets_to_write("Waiting", None, None, "", None),
      [("User", None)])
check("two removals in one edit",
      sorted(be._subbullets_to_write("Waiting", "", None, "", None)),
      [("User", None), ("Verify", None)])

# Narrowing guards — the change must not disturb the three existing behaviours.
check("None (not provided) is still a no-op, not a removal",
      be._subbullets_to_write("Waiting", None, None, None, None), [])
check("a real Verify on a Verify row still writes",
      be._subbullets_to_write("Verify", "is it good?", None, None, None),
      [("Verify", "is it good?")])
check("T056: an explicit Next on a parked row still writes",
      be._subbullets_to_write("Waiting", None, "do the thing", None,
                              "do the thing"),
      [("Next", "do the thing")])
check("T046: an explicit Next on a Verify row still rides alongside",
      be._subbullets_to_write("Verify", "q?", None, None, "step"),
      [("Verify", "q?"), ("Next", "step")])
# The one arm that writes two labels from two values: [User] writes User AND a
# queued Next (F259). Removing one while setting the other must work, and is why
# the removal pass is a separate loop rather than an `else` on the chain.
check("[User]: set the User action, remove the queued Next",
      be._subbullets_to_write("User", None, "", "log in first", ""),
      [("User", "log in first"), ("Next", None)])

print("\n_ensure_subbullet — text=None drops the line and inserts nothing")

lines = ["- **T900 — a row** [Waiting] — body ^T900\n",
         "  - **Next:** keep me\n",
         "  - **Verify:** withdraw me\n"]
be._ensure_subbullet(lines, "T900", "Verify", None)
check("the Verify line is gone", any("**Verify:**" in l for l in lines), False)
check("...and the Next line survived", any("**Next:**" in l for l in lines), True)
check("...and the row line survived", lines[0].startswith("- **T900"), True)
be._ensure_subbullet(lines, "T900", "Verify", None)
check("removing an absent sub-bullet is a no-op, not an error", len(lines), 2)

print("\nverify_write_landed — it must be able to assert an ABSENCE")

# THE guard that let this bug hide. Before T122 the falsy `want` was skipped, so
# a removal the write path declined to perform still passed the landing check.
stayed = ["- **T900 — a row** [Waiting] — body ^T900\n",
          "  - **Verify:** still here\n"]
fails = be.verify_write_landed(stayed, "T900", {"verify_text": ""})
check("a removal that did NOT land is now reported", len(fails), 1)
check("...and the message says REMOVE",
      "REMOVE" in (fails[0] if fails else ""), True)
gone = ["- **T900 — a row** [Waiting] — body ^T900\n"]
check("a removal that DID land reports nothing",
      be.verify_write_landed(gone, "T900", {"verify_text": ""}), [])
# Non-regression: the positive direction is unchanged.
check("a set that did not land is still reported",
      len(be.verify_write_landed(gone, "T900", {"verify_text": "q?"})), 1)
check("a set that did land still reports nothing",
      be.verify_write_landed(stayed, "T900", {"verify_text": "still here"}), [])

print("\nEnd-to-end through perform_edit — the path the CLI actually takes")

_td = tempfile.TemporaryDirectory()
bl = Path(_td.name) / "T Backlog.md"
bl.write_text(
    "# T Backlog\n\n## Later\n\n"
    "- **T900 — a row** [Waiting] — a parked row. ^T900\n"
    "  - **Next:** waiting on the budget to spend.\n"
    "  - **Verify:** a question that was withdrawn, not deferred.\n",
    encoding="utf-8")

be.perform_edit(bl, "Later", "T900", "same", None, None, False, False,
                verify_text="")
after = bl.read_text(encoding="utf-8")
check("the withdrawn Verify is gone from disk",
      "**Verify:**" in after, False)
check("...the Next survived the same write",
      "waiting on the budget to spend" in after, True)
check("...and the row itself survived",
      "- **T900 — a row** [Waiting]" in after, True)

print("\n`define` PRESERVES an omitted companion — deliberately, and it is not this fix")

# The row filing T122 claimed both `set` and `define --from-file` fail "the same
# way". They do not. `define`'s create-or-REPLACE is keyed on `pending_subs`,
# which `state define` fills with the LEFTOVER subs only — it lifts the
# companion trio into their own arguments first. A row whose sub-bullets are all
# companions arrives with `pending_subs == []` and takes the preserve branch.
#
# Left as-is on purpose: making omission mean deletion would silently drop a Next
# every time an agent re-defines a row to reword its body. Pinned so the reading
# is a decision on the record rather than an accident nobody measured.
bl2 = Path(_td.name) / "T2 Backlog.md"
# The bracket carries a DATE because F305's `watch_grammar_gate` refuses a bare
# `[Waiting]` on any write that sets one, and this is a define-shaped write. The
# date is incidental to what is being pinned here (companion preservation); it
# is dated rather than removed so the fixture keeps exercising a parked row.
bl2.write_text(
    "# T Backlog\n\n## Later\n\n"
    "- **T900 — a row** [Waiting 2026-09-01] — body. ^T900\n"
    "  - **Next:** keep me.\n"
    "  - **Verify:** and keep me too.\n",
    encoding="utf-8")
be.perform_edit(bl2, "Later", "T900", "Waiting 2026-09-01", "a row",
                "reworded body.",
                True, True, verify_text=None, next_text=None, pending_subs=[])
after2 = bl2.read_text(encoding="utf-8")
check("a define-shaped write with no pending_subs keeps the Verify",
      "and keep me too" in after2, True)
check("...and keeps the Next", "keep me." in after2, True)
check("...while the body did change", "reworded body." in after2, True)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
