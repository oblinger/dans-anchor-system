#!/usr/bin/env python3
"""F305 hosting pass — three answer shapes, one lifecycle, driven through
`state` alone.

V (observe, yes/no) and U (perform, done) items live in the same open-items
block as Q (choose), through the same verbs, with per-letter monotonic
numbering and per-shape mint gates:

  1.  V+ define without --why-user is REFUSED (F240 analog); a
      machine-phrased question is REFUSED regardless; labeled options or a
      Lean/Strong are REFUSED (an observation has nothing to choose —
      "Recommendation necessarily None" enforced by refusal, not boilerplate).
  2.  A good V mints as `- **V1 — …** … ^<container>-V1` in `## Open Items`,
      carrying its `*why-user:*` annotation, stamp valid.
  3.  Per-letter namespaces: Q minted beside it is Q1, not Q2.
  4.  Resolving the last Q with a V still pending does NOT migrate the block
      (the F291 contract is kind-blind: empty of ALL kinds).
  5.  resolve V takes yes/no/none — an option letter is refused; `yes`
      archives `### V1 — … (resolved …)` with `**Resolved:** yes`; as the
      last pending item it migrates the block.
  6.  Answered NO records the outcome, closes nothing else, and the summary
      says the feature is NOT verified.
  7.  U+ define without --why-user-action is REFUSED; a good U mints; resolve
      takes `done`.
  8.  set on a V is a wholesale replace; set on a missing item is refused.
  9.  `state set <row> --probe` writes `- **Probe:**` on a Backlog row on any
      bracket; a multiline value is refused; `--probe ""` removes the line.

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

# [[ZZ]] · F009 — Hosting fixture

One-line orientation.

## Summary

Body.

## Status

Implementing.
"""

td = Path(tempfile.mkdtemp())
doc = td / "F009 — Hosting fixture.md"


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


print("1. V mint gates")
reset()
err = refused(st._query_verb, "ZZ", doc, 1, "define",
              args_for(body="Does the mixed block read clearly in a week of use?"),
              letter="V")
ok("V without --why-user refused", err and "--why-user" in err, repr(err))
err = refused(st._query_verb, "ZZ", doc, 1, "define",
              args_for(body="Did the render pass on every anchor?",
                       why_user="ratification"),
              letter="V")
ok("machine-phrased V refused (F240)", err and "machine event" in err, repr(err))
err = refused(st._query_verb, "ZZ", doc, 1, "define",
              args_for(body="Which shape reads better?\n- **(A)** one\n- **(B)** two",
                       why_user="taste"),
              letter="V")
ok("V with labeled options refused", err and "observation" in err, repr(err))
err = refused(st._query_verb, "ZZ", doc, 1, "define",
              args_for(body="Is the queue easier to answer?\n- **Recommendation:** Lean yes",
                       why_user="taste"),
              letter="V")
ok("V with a Lean refused", err and "necessarily None" in err, repr(err))
ok("file untouched by the refusals", txt() == DOC)

print("2. A good V mints into ## Open Items")
rc = st._query_verb("ZZ", doc, 1, "define",
                    args_for(body="Is the mixed queue easier to answer than last week's?",
                             why_user="passive-use observation over a week"),
                    letter="V")
t = txt()
ok("define returned 0", rc == 0)
ok("block minted as ## Open Items", "## Open Items" in t)
ok("V1 bullet with block-ID", re.search(r"^- \*\*V1 — .*\^F009-V1$", t, re.M),
   t[:400])
ok("why-user annotation carried", "*why-user: passive-use observation" in t)
lines = t.splitlines()
rng = be._open_questions_range(lines)
ok("stamp valid after V write",
   rng and be.read_q_stamp(lines, *rng) == be.compute_q_stamp(lines, *rng))

print("3. Per-letter namespaces")
st._query_verb("ZZ", doc, 1, "define",
               args_for(body="**Q1 — Pick a shape** — which?\n- **(A)** one\n"
                             "- **(B)** two\n- **Recommendation:** None\n"
                             "- **Damage:** taste — user-facing wording",
                        why_ask=None),
               letter="Q")
t = txt()
ok("Q numbered Q1 beside V1", re.search(r"^- \*\*Q1 — ", t, re.M), t[:600])
ok("V+ next number is 2", be._next_item_number(t, "V") == 2)
ok("Q+ next number is 2", be._next_item_number(t, "Q") == 2)

print("4. Resolving the last Q with a V pending does NOT migrate")
st._query_verb("ZZ", doc, 1, "resolve",
               args_for(body="picked one.", choice="A"), letter="Q")
t = txt()
ok("block still present", ("## Open Items" in t) or ("## Open Questions" in t))
ok("V1 still pending", re.search(r"^- \*\*V1 — ", t, re.M))
ok("Q1 re-zoned under ### Resolved", "### Resolved" in t)

print("5. resolve V — vocabulary + migration")
err = refused(st._query_verb, "ZZ", doc, 1, "resolve",
              args_for(body="", choice="A"), letter="V")
ok("option letter refused on a V", err and "yes / no" in err, repr(err))
rc = st._query_verb("ZZ", doc, 1, "resolve",
                    args_for(body="Observed all week; clearly easier.",
                             choice="yes"),
                    letter="V")
t = txt()
ok("resolve yes returned 0", rc == 0)
ok("block migrated once empty of ALL kinds",
   "## Open Items" not in t and "## Open Questions" not in t)
ok("archived V entry with outcome",
   re.search(r"^### V1 — .*\(resolved ", t, re.M) and "**Resolved:** yes" in t)
ok("block-ID survives migration", "^F009-V1" in t)

print("6. Answered NO reopens rather than force-closing")
reset()
SUMMARIES.clear()
st._query_verb("ZZ", doc, 1, "define",
               args_for(body="Does the new banner read better in daily use?",
                        why_user="taste"),
               letter="V")
st._query_verb("ZZ", doc, 1, "resolve",
               args_for(body="Reads worse — the counts are noise.", choice="no"),
               letter="V")
t = txt()
ok("no is recorded", "**Resolved:** no" in t)
ok("summary says NOT verified",
   any("NOT verified" in s for s in SUMMARIES),
   repr(SUMMARIES))
ok("nothing else closed — Status untouched", "Implementing." in t)

print("7. U lifecycle")
reset()
err = refused(st._query_verb, "ZZ", doc, 1, "define",
              args_for(body="Log into the vendor portal and approve the invoice."),
              letter="U")
ok("U without --why-user-action refused", err and "--why-user-action" in err,
   repr(err))
st._query_verb("ZZ", doc, 1, "define",
               args_for(body="Log into the vendor portal and approve the invoice.",
                        why_user_action="the portal login is a credential only you hold"),
               letter="U")
t = txt()
ok("U1 minted with block-ID", re.search(r"^- \*\*U1 — .*\^F009-U1$", t, re.M),
   t[:400])
ok("why-user-action annotation carried", "*why-user-action:" in t)
err = refused(st._query_verb, "ZZ", doc, 1, "resolve",
              args_for(body="", choice="yes"), letter="U")
ok("U takes done, not yes", err and "done" in err, repr(err))
rc = st._query_verb("ZZ", doc, 1, "resolve",
                    args_for(body="Approved at 09:12.", choice="done"),
                    letter="U")
ok("resolve done returned 0", rc == 0)
ok("archived U entry", "**Resolved:** done" in txt())

print("8. set on hosted V")
reset()
st._query_verb("ZZ", doc, 1, "define",
               args_for(body="Does the gallery layout feel right?",
                        why_user="taste"),
               letter="V")
err = refused(st._query_verb, "ZZ", doc, 2, "set",
              args_for(body="anything"), letter="V")
ok("set on missing V2 refused toward define",
   err and "define" in err and "V2" in err, repr(err))
st._query_verb("ZZ", doc, 1, "set",
               args_for(body="Does the REVISED gallery layout feel right?",
                        why_user="taste"),
               letter="V")
t = txt()
ok("set replaced the V wholesale", "REVISED gallery" in t)
ok("old wording gone", t.count("Does the gallery layout feel right?") == 0)

print("9. The Probe field on a Backlog row")
BLOG = """# ZZ Backlog

## Now

- **T001 — Soak the counter** [Waiting 2026-09-01] — body. ^T001

## Done
"""
blog = td / "ZZ Backlog.md"
blog.write_text(BLOG, encoding="utf-8")
r = be.perform_edit(blog, "same", "T001", "Waiting 2026-09-01", "", "",
                    False, False, probe_text="once `fired` reaches 21 — re-run the soak counts")
t = blog.read_text(encoding="utf-8")
ok("Probe sub-bullet written",
   "  - **Probe:** once `fired` reaches 21 — re-run the soak counts" in t, t)
try:
    be.perform_edit(blog, "same", "T001", "Waiting 2026-09-01", "", "",
                    False, False, probe_text="line one\nline two")
    ok("multiline probe refused", False)
except be.BacklogEditError as e:
    ok("multiline probe refused", "--probe" in str(e), str(e))
r = be.perform_edit(blog, "same", "T001", "Waiting 2026-09-01", "", "",
                    False, False, probe_text="")
t = blog.read_text(encoding="utf-8")
ok("--probe \"\" removes the line", "- **Probe:**" not in t, t)

print("10. The render's doc-item reader (queries-render fallback)")
qr_path = HERE.parent.parent / "audit" / "scripts" / "queries-render.py"
qr_loader = importlib.machinery.SourceFileLoader("qr_mod", str(qr_path))
qr_spec = importlib.util.spec_from_loader("qr_mod", qr_loader)
qr = importlib.util.module_from_spec(qr_spec)
sys.modules["qr_mod"] = qr
qr_loader.exec_module(qr)
reset()
st._query_verb("ZZ", doc, 1, "define",
               args_for(body="Does the weekly digest feel worth reading?",
                        why_user="taste"),
               letter="V")
st._query_verb("ZZ", doc, 2, "define",
               args_for(body="Is the new column order right?",
                        why_user="preference"),
               letter="V")
st._query_verb("ZZ", doc, 2, "resolve",
               args_for(body="Yes, kept.", choice="yes"), letter="V")
items = qr._read_pending_items(doc, "V")
ok("reader returns only the pending V", len(items) == 1, repr(items))
ok("durable handle + anchor",
   items and items[0][0] == "V1" and items[0][2] == "F009-V1", repr(items))
ok("annotation stripped from surfaced text",
   items and "why-user" not in items[0][1], repr(items))
ok("U reader empty on this doc", qr._read_pending_items(doc, "U") == [])

print("11. A doc-hosted V satisfies the row's F171/F240 gates")
# Anchor-shaped fixture: backlog in `Zed/ZED Track/`, doc in
# `Zed/ZED Design/ZED Features/` — _hosted_pending_items resolves the arrow
# link anchor-locally.
root = td / "Zed"
(root / "ZED Track").mkdir(parents=True, exist_ok=True)
(root / "ZED Design" / "ZED Features").mkdir(parents=True, exist_ok=True)
hdoc = root / "ZED Design" / "ZED Features" / "ZED001 - Hosted.md"
hdoc.write_text(DOC, encoding="utf-8")
st._query_verb("ZED", hdoc, 1, "define",
               args_for(body="Is the layout worth keeping?", why_user="taste"),
               letter="V")
hblog = root / "ZED Track" / "ZED Backlog.md"
hblog.write_text("# ZED Backlog\n\n## Now\n\n- **F001 — Hosted** [Ready] — "
                 "→ [[ZED001 - Hosted|F001]] body. ^F001\n"
                 "  - **Next:** step.\n\n## Done\n", encoding="utf-8")
be.perform_edit(hblog, "same", "F001", "Verify", "", "", False, False)
t = hblog.read_text(encoding="utf-8")
ok("row enters [Verify] on the hosted V alone — no row question, no --why-user",
   "[Verify]" in t, t)
try:
    be.perform_edit(hblog, "same", "F001", "Verify", "", "", False, False,
                    probe_text="when X lands — check Y")
    ok("flag-only re-touch passes with the hosted V", True)
except be.BacklogEditError as e:
    ok("flag-only re-touch passes with the hosted V", False, str(e))

print("----------------------------------------")
print(f"test-f305-item-hosting: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
