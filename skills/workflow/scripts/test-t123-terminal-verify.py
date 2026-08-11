#!/usr/bin/env python3
"""test-t123-terminal-verify.py — TINK T123: a terminal row's `- **Verify:**`
question must stay correctable.

The system has two question-shaped things and only one had a lifecycle. A `Q<n>`
is born with `define`, answered with `resolve --choice`, and migrates keeping its
block-ID. A `- **Verify:**` sub-bullet is born with `set --verify` and had no
answered state at all — `_subbullets_to_write` wrote one only when
`_verify_family(status)`, and `_verify_family("Done")` is False. So the moment a
row was answered and moved to [Done] its question froze at whatever it last
said, and every later `set --verify` was skipped and then correctly caught by
T050's post-write guard.

Found 2026-08-05 by the MUX Pilot closing two Verify rows whose questions the
agent had answered from the logs. MUX F237's question asserted "there is no log
anywhere that ever saw 13" — which the agent then proved FALSE. With no
supported way to correct or retire it, a closed row went on vouching for a false
claim, and both lines had to be rewritten by hand outside `state`.

Q1 → (A), 2026-08-08: widen the CARRIER set, not the family. The F240 ownership
gate governs `_verify_family` and exists to vet a question being ASKED; a
terminal row is recording that one was ANSWERED, which needs no ownership
justification and must not be refused for reading like a machine event.

  A. a [Done] row's Verify can be rewritten
  B. ...and F240 does not refuse the machine-event phrasing of an answer
  C. an ordinary re-touch of a Done row does NOT rewrite/reorder its Verify
  D. live-row behaviour is unchanged — the family still writes from eff_verify
  E. [Done] still does not INVENT a Verify nobody asked for

Self-contained: loads backlog-edit.py in-process against a tmpdir fixture."""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

BE = Path(__file__).parent / "backlog-edit.py"
_loader = importlib.machinery.SourceFileLoader("be_mod", str(BE))
_spec = importlib.util.spec_from_loader("be_mod", _loader)
be = importlib.util.module_from_spec(_spec)
sys.modules["be_mod"] = be
_loader.exec_module(be)
be._selffire = lambda *a, **k: None
be._post_conditions = lambda *a, **k: []

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


BACKLOG = """# ZZ Backlog
<!-- state:backlog 00 -->

## Now

- **T900 — a closed check** [Done] — body text. ^T900
  - **Verify:** there is no log anywhere that ever saw 13 — right?

- **T901 — a live check** [Verify] — body text. ^T901
  - **Verify:** does the gallery read right to you? *why-user: taste*

"""


def fresh(tmp):
    p = tmp / "ZZ Backlog.md"
    p.write_text(BACKLOG, encoding="utf-8")
    return p


def verify_of(p, row):
    lines = p.read_text(encoding="utf-8").splitlines()
    at = next(i for i, l in enumerate(lines) if l.startswith(f"- **{row} "))
    for l in lines[at + 1:]:
        if l.startswith("- **"):
            break
        if l.strip().startswith("- **Verify:**"):
            return l.split("**Verify:**", 1)[1].strip()
    return None


def subbullet_order(p, row):
    lines = p.read_text(encoding="utf-8").splitlines()
    at = next(i for i, l in enumerate(lines) if l.startswith(f"- **{row} "))
    out = []
    for l in lines[at + 1:]:
        if l.startswith("- **"):
            break
        s = l.strip()
        if s.startswith("- **") and ":**" in s:
            out.append(s.split("**", 2)[1].rstrip(":"))
    return out


TMP = Path(tempfile.mkdtemp())
try:
    print("A/B: a [Done] row's Verify can be rewritten")
    p = fresh(TMP)
    answer = ("ANSWERED 2026-08-05 — the claim was false; "
              "`grep 13 muxux.log` returns 4 hits.")
    try:
        be.perform_edit(p, "same", "T900", "same", "", "", False, False,
                        verify_text=answer, why_user=None)
        landed = verify_of(p, "T900")
        if landed == answer:
            ok("the frozen question was replaced by the answer")
        else:
            no(f"Verify did not change: {landed!r}")
        ok("F240 did not refuse a machine-event phrasing on a terminal row")
    except SystemExit as e:
        no(f"the edit was refused: {e}")

    print("C: an ordinary re-touch does not rewrite or reorder it")
    p = fresh(TMP)
    be.perform_edit(p, "same", "T900", "same", "", "", False, False,
                    next_text="a queued follow-up", why_user=None)
    if verify_of(p, "T900") == "there is no log anywhere that ever saw 13 — right?":
        ok("the existing Verify text is untouched")
    else:
        no("an unrelated edit rewrote the Verify text")
    order = subbullet_order(p, "T900")
    if "Verify" in order:
        ok(f"the Verify sub-bullet survives the unrelated edit ({order})")
    else:
        no(f"the Verify sub-bullet was dropped: {order}")
    # Ordering is `_ensure_subbullet`'s, not this feature's: it re-inserts
    # whichever label is WRITTEN directly under the row line, so writing Next
    # moves Verify down. Pre-existing and cosmetic — asserted here only so a
    # future reader does not mistake it for something T123 introduced.
    if order == ["Next", "Verify"]:
        ok("...below the newly-written Next, per _ensure_subbullet's insert rule")
    else:
        no(f"unexpected sub-bullet layout: {order}")

    print("D: live-row behaviour is unchanged")
    p = fresh(TMP)
    be.perform_edit(p, "same", "T901", "same", "", "", False, False,
                    verify_text="does the NEW gallery read right?",
                    why_user="taste", why_user_action=None)
    if verify_of(p, "T901").startswith("does the NEW gallery read right?"):
        ok("a [Verify] row still takes a rewritten question")
    else:
        no(f"live-row rewrite broke: {verify_of(p, 'T901')!r}")
    # The family branch writes from eff_verify, so a re-touch that names no
    # --verify still re-attaches the existing question. That is pre-existing
    # behaviour and must not have changed.
    p = fresh(TMP)
    be.perform_edit(p, "same", "T901", "same", "", "", False, False,
                    next_text="a queued step", why_user=None)
    if verify_of(p, "T901").startswith("does the gallery read right to you?"):
        ok("a live row's question survives an unrelated edit")
    else:
        no("a live row's question was lost on an unrelated edit")

    print("E: [Done] does not invent a Verify nobody asked for")
    p = TMP / "ZZ2 Backlog.md"
    p.write_text("# ZZ2 Backlog\n<!-- state:backlog 00 -->\n\n## Now\n\n"
                 "- **T902 — no question here** [Done] — body. ^T902\n\n",
                 encoding="utf-8")
    be.perform_edit(p, "same", "T902", "same", "", "", False, False,
                    next_text="a note", why_user=None)
    if verify_of(p, "T902") is None:
        ok("no Verify sub-bullet was fabricated")
    else:
        no("a Verify sub-bullet appeared on a row that never had one")

    print("F: the predicates stay separate")
    if not be._verify_family("Done") and be._terminal_bracket("Done"):
        ok("_verify_family excludes Done; _terminal_bracket includes it")
    else:
        no("the F240 gate's family was widened — a terminal row would now be "
           "asked to justify recording an answer")
    if be._terminal_bracket("Done 2026-08-08"):
        ok("the dated Done form is terminal too")
    else:
        no("`Done YYYY-MM-DD` is not recognised as terminal")
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
