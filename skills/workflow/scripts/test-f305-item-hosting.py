#!/usr/bin/env python3
"""F305 D5 — verification is the LAST question (T127 executed).

The V<n>/U<n> item namespace is retired (it never gained a corpus instance);
a verification is the doc's FINAL question — minted at done-time, zero
options, a `yes / no` cue, Recommendation necessarily None, the doc's own
next Q number — and the `[Verify]` bracket survives as the Parked-class
claim "done, nothing waiting, only the check remains".

  1.  The final-question form mints through the ordinary Q gates: zero
      options + `yes / no` cue + `Recommendation: None` is admitted; the
      same body with a Lean is refused (a lean makes it a choice); an
      optionless body with no yes/no cue is refused.
  2.  resolve on an optionless question takes yes/no/none verbatim — an
      option letter form is not required; answered NO records the outcome,
      closes nothing, and the summary says the feature is NOT verified.
  3.  The V/U namespace is gone: ITEM_KINDS is Q-only and a `- **V1 — …**`
      bullet is not an item header.
  4.  A `[Verify]` row whose doc holds the pending final question satisfies
      the F171 companion requirement with no row `- **Verify:**` and no
      second `--why-user` (the hosted-question exemption).
  5.  `state set <row> --probe` writes `- **Probe:**` on any bracket;
      multiline refused; `--probe ""` removes (unchanged from the hosting
      pass).

Run: python3 test-f305-item-hosting.py
"""
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import re
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).parent
loader = importlib.machinery.SourceFileLoader("state_mod", str(HERE / "state"))
spec = importlib.util.spec_from_loader("state_mod", loader)
st = importlib.util.module_from_spec(spec)
sys.modules["state_mod"] = st
loader.exec_module(st)
be = st.be

SUMMARIES = []
st._post_conditions_and_print = lambda slug, path, summary: SUMMARIES.append(summary)
st._selffire = lambda path: None
be._selffire = lambda *a, **k: None

PASS = 0
FAIL = 0


def ok(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}" + (f"\n          {detail}" if detail else ""))


def args_for(body=None, choice=None, reason=None, why_ask=None, why_user=None,
             why_user_action=None):
    return types.SimpleNamespace(
        inline=body, from_file=None, choice=choice, reason=reason,
        why_ask=why_ask, why_user=why_user, why_user_action=why_user_action)


DOC = """---
description: "fixture"
---

# [[ZZ]] · F009 — Final-question fixture

One-line orientation.

## Summary

Body.

## Status

Implementing.
"""

FINAL_Q = ("**Q+ — Verified in use?** — after a week of normal use: does the "
           "mixed queue read clearly — easier to answer, not noisier? "
           "**yes / no**\n"
           "- **Recommendation:** None\n"
           "- **Damage:** taste — the user's own read of their queue")

td = Path(tempfile.mkdtemp())
doc = td / "F009 — Final-question fixture.md"


def reset():
    doc.write_text(DOC, encoding="utf-8")


def txt():
    return doc.read_text(encoding="utf-8")


def refused(fn, *a, **k):
    try:
        fn(*a, **k)
        return None
    except be.BacklogEditError as e:
        return str(e)


print("1. The final-question form and its gates")
reset()
rc = st._query_verb("ZZ", doc, 1, "define", args_for(body=FINAL_Q))
t = txt()
ok("final-question form mints (zero options + yes/no cue + Rec None)",
   rc == 0 and re.search(r"^- \*\*Q1 — Verified in use\?\*\*.*\^F009-Q1$",
                         t, re.M), t[:400])
ok("block minted as ## Open Items", "## Open Items" in t)
err = refused(st._query_verb, "ZZ", doc, 2, "define",
              args_for(body=FINAL_Q.replace("**Recommendation:** None",
                                            "**Recommendation:** Lean yes"),
                       why_ask="x"))
ok("same shape with a Lean refused (a lean makes it a choice)",
   err and "final-question form" in err, repr(err))
err = refused(st._query_verb, "ZZ", doc, 2, "define",
              args_for(body="**Q+ — Vague** — is it good?\n"
                            "- **Recommendation:** None\n"
                            "- **Damage:** taste — wording"))
ok("optionless body without the yes/no cue refused",
   err and "≥2 labeled option" in err, repr(err))

print("2. resolve on an optionless question: yes/no verbatim, no closes nothing")
err = refused(st._query_verb, "ZZ", doc, 1, "resolve",
              args_for(body="", choice="A"), letter="Q")
ok("an option letter is meaningless on an optionless Q",
   err is None or "no option (A)" in (err or ""), repr(err))
reset()
st._query_verb("ZZ", doc, 1, "define", args_for(body=FINAL_Q))
SUMMARIES.clear()
rc = st._query_verb("ZZ", doc, 1, "resolve",
                    args_for(body="Watched a week; clearly easier.",
                             choice="yes"))
t = txt()
ok("resolve yes returned 0 and archived verbatim",
   rc == 0 and "**Resolved:** yes" in t, t[-400:])
reset()
st._query_verb("ZZ", doc, 1, "define", args_for(body=FINAL_Q))
SUMMARIES.clear()
st._query_verb("ZZ", doc, 1, "resolve",
               args_for(body="Counts read as noise.", choice="no"))
t = txt()
ok("no is recorded", "**Resolved:** no" in t)
ok("summary says NOT verified", any("NOT verified" in s for s in SUMMARIES),
   repr(SUMMARIES))
ok("nothing else closed — Status untouched", "Implementing." in t)

print("3. The V/U namespace is retired")
ok("ITEM_KINDS is Q-only", be.ITEM_KINDS == ("Q",), repr(be.ITEM_KINDS))
ok("a V bullet is not an item header",
   be._ITEM_HEADER_BULLET_RE.match("- **V1 — x** — y") is None)
ok("a U bullet is not an item header",
   be._ITEM_HEADER_BULLET_RE.match("- **U2 — x** — y") is None)

print("4. A hosted final question satisfies the [Verify] row gates")
root = td / "Zed"
(root / "ZED Track").mkdir(parents=True, exist_ok=True)
(root / "ZED Design" / "ZED Features").mkdir(parents=True, exist_ok=True)
hdoc = root / "ZED Design" / "ZED Features" / "ZED001 - Hosted.md"
hdoc.write_text(DOC, encoding="utf-8")
st._query_verb("ZED", hdoc, 1, "define", args_for(body=FINAL_Q))
hblog = root / "ZED Track" / "ZED Backlog.md"
hblog.write_text("# ZED Backlog\n\n## Now\n\n- **F001 — Hosted** [Ready] — "
                 "→ [[ZED001 - Hosted|F001]] body. ^F001\n"
                 "  - **Next:** step.\n\n## Done\n", encoding="utf-8")
try:
    be.perform_edit(hblog, "same", "F001", "Verify", "", "", False, False)
    ok("row enters [Verify] on the hosted final Q alone", True)
except be.BacklogEditError as e:
    ok("row enters [Verify] on the hosted final Q alone", False, str(e))
try:
    be.perform_edit(hblog, "same", "F001", "Verify", "", "", False, False,
                    probe_text="when X lands — check Y")
    ok("flag-only re-touch passes with the hosted final Q", True)
except be.BacklogEditError as e:
    ok("flag-only re-touch passes with the hosted final Q", False, str(e))

print("5. The Probe field")
BLOG = """# ZZ Backlog

## Now

- **T001 — Soak the counter** [Waiting 2026-09-01] — body. ^T001

## Done
"""
blog = td / "ZZ Backlog.md"
blog.write_text(BLOG, encoding="utf-8")
be.perform_edit(blog, "same", "T001", "Waiting 2026-09-01", "", "",
                False, False,
                probe_text="once `fired` reaches 21 — re-run the soak counts")
t = blog.read_text(encoding="utf-8")
ok("Probe sub-bullet written",
   "  - **Probe:** once `fired` reaches 21 — re-run the soak counts" in t, t)
try:
    be.perform_edit(blog, "same", "T001", "Waiting 2026-09-01", "", "",
                    False, False, probe_text="line one\nline two")
    ok("multiline probe refused", False)
except be.BacklogEditError as e:
    ok("multiline probe refused", "--probe" in str(e), str(e))
be.perform_edit(blog, "same", "T001", "Waiting 2026-09-01", "", "",
                False, False, probe_text="")
t = blog.read_text(encoding="utf-8")
ok("--probe \"\" removes the line", "- **Probe:**" not in t, t)

print("----------------------------------------")
print(f"test-f305-item-hosting: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
