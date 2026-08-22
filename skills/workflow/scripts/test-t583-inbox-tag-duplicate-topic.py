#!/usr/bin/env python3
"""test-t583-inbox-tag-duplicate-topic.py — TINK T583.

`state inbox-tag` counted ALREADY-TAGGED entries among its candidates, so the
second of two same-day entries sharing a topic could never be tagged.

Reported by Atticus 2026-08-21 from a live `ATT Inbox`: two entries both titled
"2026-08-21 — browser lease expired and was stolen", the second written by
ctrl's new lease-steal path — so the duplicate topic is STRUCTURAL, produced by
a machine that writes the same sentence every time, not a typo somebody could
have avoided.

WHY IT IS A TRAP RATHER THAN AN ANNOYANCE. `--date` and `--topic` are the only
selectors. Once the first entry is tagged, tagging the second reports "2 entries
dated 2026-08-21 — disambiguate with --topic" and lists the already-DONE entry
as one of the choices; with byte-identical topics there is nothing left to
disambiguate WITH. The entry is permanently untaggable and inflates that
anchor's `Inbox N` forever — a counter that can only go up, on the banner whose
entire job is to say whether there is anything to drain.

WHY PARTITION RATHER THAN FILTER. The report proposed dropping tagged entries
from the candidate list, which fixes the bug and costs a good error message:
explicitly re-tagging one processed entry would then report "no entry dated …",
which is both wrong and less useful than the "already carries a status tag"
message that already existed. So untagged entries are the candidates, and if
the date matched but everything matching is tagged, the old message still
answers. Both halves are asserted below.

WHAT THIS DOES NOT FIX, asserted in section C so it is not rediscovered as a
surprise: if BOTH duplicates are still untagged, neither can be selected —
`--date` and `--topic` both match both, and closing that needs a new selector
(an ordinal / `--nth`), which is a CLI surface rather than an implementation
detail. It is narrow because `drop` writes entries one at a time and anchors
drain regularly, so the sequential shape in section A is the one that actually
occurs; this one needs two identical drops to land before anyone touches either.
"""
import sys as _sys; _sys.dont_write_bytecode = True

import contextlib
import importlib.machinery
import importlib.util
import io
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
loader = importlib.machinery.SourceFileLoader("state_mod", str(HERE / "state"))
spec = importlib.util.spec_from_loader("state_mod", loader)
st = importlib.util.module_from_spec(spec)
sys.modules["state_mod"] = st
loader.exec_module(st)

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


DUP = "browser lease expired and was stolen"

INBOX = """---
description: FIX inbox
---

# FIX Inbox
Raw input dropped for later processing.

## 2026-08-21 — {dup}    `DONE`

*from: ctrl · tag: fact*

> first one, tagged when it was the only one on this date

## 2026-08-21 — {dup}

*from: ctrl · tag: fact*

> second one, written by the lease-steal path

## 2026-08-20 — something else entirely

*from: someone · tag: fact*

> unrelated
""".format(dup=DUP)


def build(both_pending=False):
    root = TMP / "vault"
    shutil.rmtree(root, ignore_errors=True)
    anchor = root / "FIX"
    (anchor / "FIX Track").mkdir(parents=True, exist_ok=True)
    (anchor / ".anchor").write_text("slug: FIX\nfeeds:\n", encoding="utf-8")
    body = INBOX.replace("    `DONE`", "") if both_pending else INBOX
    (anchor / "FIX Track" / "FIX Inbox.md").write_text(body, encoding="utf-8")
    return anchor, anchor / "FIX Track" / "FIX Inbox.md"


def tag(anchor, date, topic, value):
    argv = ["state", "inbox-tag", str(anchor), "--date", date, "--tag", value]
    if topic:
        argv += ["--topic", topic]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf), contextlib.redirect_stdout(io.StringIO()):
            rc = st.main(argv)
    except SystemExit as e:
        rc = int(e.code or 0)
    except Exception as e:                       # BacklogEditError and kin
        return 1, str(e)
    return rc, buf.getvalue()


try:
    # ============================================================
    print("== A: the live shape — the duplicate lands AFTER the first is tagged ==")
    #
    # This is the real sequence, and it is why nobody notices until it is
    # already stuck: entries arrive one at a time, so the first is tagged while
    # it is the only one on that date. The duplicate arrives later, and only
    # then does the date become ambiguous — retroactively, against an entry
    # that is already processed.
    # ============================================================
    anchor, path = build()

    # THE BUG. Before the fix this refused with "2 entries dated 2026-08-21 —
    # disambiguate with --topic" and listed the already-DONE entry as a choice.
    rc, err = tag(anchor, "2026-08-21", DUP, "DONE")
    if rc == 0:
        ok("the duplicate tags cleanly — a tagged entry is no longer a candidate")
    else:
        no(f"the duplicate is still untaggable: {err[:220]}")

    body = path.read_text(encoding="utf-8")
    if body.count("`DONE`") == 2:
        ok("both entries carry a tag, so Inbox N can actually reach zero")
    else:
        no(f"expected 2 tags on disk, found {body.count('`DONE`')}")

    # The tag landed on the SECOND entry, not stacked onto the first.
    tagged = [l for l in body.splitlines() if l.startswith("## ") and "`DONE`" in l]
    if len(tagged) == 2 and not any(l.count("`DONE`") > 1 for l in tagged):
        ok("the two tags sit on two DIFFERENT H2 lines, one tag each")
    else:
        no(f"tags did not land on separate entries: {tagged}")

    # ============================================================
    print("== B: the good error message survives (why partition, not filter) ==")
    # ============================================================
    rc, err = tag(anchor, "2026-08-21", DUP, "DONE")
    if rc != 0 and "already carries a status tag" in err:
        ok("with every match tagged, it still says exactly why it will not act")
    else:
        no(f"the already-tagged message was lost to the filter: {err[:220]}")
    if "no entry dated" not in err:
        ok("and it is NOT the misleading `no entry dated` a plain filter gives")
    else:
        no("a plain filter crept back in — the message is now wrong")

    # ============================================================
    print("== C: genuine ambiguity still refuses, and counts only the pending ==")
    # ============================================================
    anchor, path = build(both_pending=True)
    rc, err = tag(anchor, "2026-08-21", None, "DONE")
    if rc != 0 and "disambiguate with --topic" in err:
        ok("two UNTAGGED entries on a date still refuse rather than guess")
    else:
        no(f"an ambiguous date did not refuse: {rc} {err[:180]}")
    if "2 UNTAGGED entries" in err:
        ok("and the count reported is of pending entries, not of all matches")
    else:
        no(f"the refusal counts the wrong set: {err[:220]}")

    # THE RESIDUAL LIMITATION, asserted rather than left to be rediscovered.
    # If BOTH duplicates are still untagged, neither can be selected: `--date`
    # and `--topic` are the only selectors and both match both. This fix does
    # not close that, and cannot without a new selector (an ordinal, or a
    # `--nth`), which is a CLI surface and therefore not an implementation
    # detail to decide alone.
    #
    # It is narrow in practice, and the reason is worth stating: `drop` writes
    # entries one at a time and anchors drain regularly, so the overwhelmingly
    # common shape is the SEQUENTIAL one in section A — first tagged, duplicate
    # arrives later — which IS fixed. This case needs two identical drops to
    # land before anyone touches either.
    rc, err = tag(anchor, "2026-08-21", DUP, "DONE")
    if rc != 0 and "disambiguate" in err:
        ok("two untagged identical topics are STILL unselectable — known, narrow")
    else:
        no(f"expected the known limitation, got rc={rc}: {err[:180]}")

    # And the fix must not have made that case worse: once one of them is
    # tagged by any route, the other resolves.
    body = path.read_text(encoding="utf-8")
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("## 2026-08-21") and "`" not in line:
            lines[i] = line + "    `DONE`"
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rc, err = tag(anchor, "2026-08-21", None, "MOVED → [[FIX Backlog#^T001|T001]]")
    if rc == 0:
        ok("and once either one is tagged, the other resolves on a bare --date")
    else:
        no(f"a bare --date refused with one pending entry: {err[:180]}")

    # ============================================================
    print("== D: the untouched paths ==")
    # ============================================================
    anchor, path = build()
    rc, err = tag(anchor, "2026-08-20", None, "DONE")
    if rc == 0:
        ok("a lone entry on its own date is unaffected")
    else:
        no(f"the simple case broke: {err[:160]}")

    rc, err = tag(anchor, "2099-01-01", None, "DONE")
    if rc != 0 and "no entry dated" in err:
        ok("a date with no entries at all still reports no entry dated")
    else:
        no(f"the empty-date message changed: {err[:160]}")

    rc, err = tag(anchor, "2026-08-21", "nothing matches this", "DONE")
    if rc != 0 and "no entry dated" in err:
        ok("a --topic that matches nothing still reports no entry dated")
    else:
        no(f"the no-topic-match message changed: {err[:160]}")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
