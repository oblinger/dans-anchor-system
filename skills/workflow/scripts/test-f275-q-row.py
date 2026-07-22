#!/usr/bin/env python3
"""test-f275-q-row.py — F275 M2/M3: `Q###` as a first-class Backlog row.

A standalone feature-less question row (`state Backlog Q+ define`) is a sibling
to F/T rows, but the row body IS the question — so it runs the same ask-format
+ F270 Damage + F257 gates as a doc-scoped Q, PLUS the hard-required F275
`On answer:` clause (M3). This drives the full path through `cmd_v2` (routing +
mint + gates + row write) on a temp backlog, with every vault-touching hook
stubbed (mirrors test-f247 / test-f270):

  1. Mint + surface — a `locking` Damage row lands [Questions], id Q001, with
     its option/Recommendation/Damage/On-answer sub-bullets and the F257
     `*why-ask:*` annotation (Damage subsumes --why-ask).
  2. On-answer HARD-required — the same body minus `- **On answer:**` is refused.
  3. Ask-format — a body with no Recommendation / <2 options is refused.
  4. Auto-resolve — a `waste` Damage row lands [Done] with an
     `auto-resolved (waste)` note and never surfaces.
  5. Mint numbering — a second `Q+` mints Q002 (scans Backlog Q-rows).
  6. Resolve — `Backlog Q001 resolve` moves the row to ## Done.
  7. Collision guard — the doc-scoped `Q` world is untouched: a `Q+ define` on a
     *doc* (not Backlog) still routes to the doc's Open Questions.

Self-contained: loads `state` in-process, stubs the vault I/O, tmp files only."""
import contextlib
import importlib.machinery
import importlib.util
import io
import re
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


st = _load("state_mod", HERE / "state")
be = st.be

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")

# A realistic backlog with the horizon sections the row machinery needs.
BACKLOG = (
    "---\n"
    'description: "workflow-state backlog"\n'
    "---\n"
    "\n"
    "# ZZQ Backlog\n"
    "\n"
    "Intro line.\n"
    "\n"
    "## Now\n"
    "\n"
    "- **F001 — seed** [Ready] — → [[F001 — seed]] ^F001\n"
    "\n"
    "## Later\n"
    "\n"
    "## Done\n"
    "\n"
    "_None._\n"
)

TMP = Path(tempfile.mkdtemp())
BL = TMP / "ZZQ Track" / "ZZQ Backlog.md"
BL.parent.mkdir(parents=True, exist_ok=True)

# Stub every vault-touching hook so the path never leaves the tmpdir.
be.find_backlog = lambda slug: BL
be.find_icebox = lambda slug: None
be.refresh_q_md = lambda slug: None
be.append_messages = lambda *a, **k: None
be.write_state = lambda *a, **k: None
be.heal_backlog_if_stale = lambda *a, **k: None
be._selffire = lambda *a, **k: None
st._selffire = lambda *a, **k: None


def args(doc, label, verb, body=None, why_ask=None):
    return SimpleNamespace(
        doc=doc, label=label, verb=verb, inline=body, from_file=None,
        why_ask=why_ask, horizon=None, status=None, title=None,
        next_step=None, verify=None, user=None, why_user=None,
        why_user_action=None,
    )


def run(a):
    """Invoke cmd_v2 capturing stdout+stderr; return (rc, out, err)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = st.cmd_v2("ZZQ", TMP, a)
    return rc, out.getvalue(), err.getvalue()


def q_body(damage="locking — parsers commit to the shape", on_answer=True,
           rec="Lean (A). the swap is low-risk", options=2, status="Questions"):
    lines = [f"- **Q+ — Swap the 3 straggler vocab words, or leave them?** "
             f"[{status}] — spoken-vocabulary word list, not any feature"]
    if options >= 1:
        lines.append("  - **(A)** take the verified replacements.")
    if options >= 2:
        lines.append("  - **(B)** leave the daily habits alone.")
    lines.append(f"  - **Recommendation:** {rec}")
    if damage is not None:
        lines.append(f"  - **Damage:** {damage}")
    if on_answer:
        lines.append("  - **On answer:** (A) → edit the word list, land it; "
                     "(B) → leave it untouched.")
    return "\n".join(lines)


def reset():
    BL.write_text(BACKLOG, encoding="utf-8")


# ---- 1. Mint + surface ------------------------------------------------------
print("== 1. Q+ define — locking Damage surfaces as a [Questions] Q001 row ==")
reset()
rc, out, err = run(args("Backlog", "Q+", "define", body=q_body()))
txt = BL.read_text()
good = ("- **Q001 —" in txt and "[Questions]" in txt
        and "- **(A)**" in txt and "- **(B)**" in txt
        and "**Recommendation:**" in txt and "**On answer:**" in txt
        and "*why-ask: locking:" in txt)
ok("Q001 row minted [Questions] with options/Recommendation/On-answer + why-ask annotation") \
    if good else no(f"surface path wrong:\nOUT={out!r}\nERR={err!r}\nTXT={txt}")

# ---- 2. On-answer hard-required --------------------------------------------
print("== 2. missing `On answer:` is REFUSED (hard, F275 M3) ==")
reset()
try:
    run(args("Backlog", "Q+", "define", body=q_body(on_answer=False)))
    no("missing On-answer should refuse")
except be.BacklogEditError as e:
    ok("missing On-answer refused") if "On answer" in str(e) \
        else no(f"wrong error: {e}")

# ---- 3. Ask-format ----------------------------------------------------------
print("== 3. ask-format — no Recommendation / <2 options refused ==")
reset()
nored = "\n".join(l for l in q_body().splitlines() if "Recommendation" not in l)
try:
    run(args("Backlog", "Q+", "define", body=nored))
    no("missing Recommendation should refuse")
except be.BacklogEditError:
    ok("missing Recommendation refused")
reset()
try:
    run(args("Backlog", "Q+", "define", body=q_body(options=1)))
    no("single option should refuse")
except be.BacklogEditError:
    ok("<2 options refused")

# ---- 4. Auto-resolve (waste) -----------------------------------------------
print("== 4. waste Damage auto-resolves to [Done], never surfaces ==")
reset()
rc, out, err = run(args("Backlog", "Q+", "define",
                        body=q_body(damage="waste — a wrong pick just re-edits one file")))
txt = BL.read_text()
good = ("[Done]" in txt and "auto-resolved (waste)" in txt
        and "auto-resolved" in out and "[Questions]" not in txt)
ok("waste Q001 lands [Done] with auto-resolved note, prints ⚑, none pending") \
    if good else no(f"auto-resolve wrong:\nOUT={out!r}\nTXT={txt}")

# ---- 5. Mint numbering ------------------------------------------------------
print("== 5. a second Q+ mints Q002 (scans Backlog Q-rows) ==")
reset()
run(args("Backlog", "Q+", "define", body=q_body()))
run(args("Backlog", "Q+", "define", body=q_body()))
txt = BL.read_text()
ok("two Q+ mints yield Q001 and Q002") \
    if ("- **Q001 —" in txt and "- **Q002 —" in txt) \
    else no(f"mint numbering wrong:\n{txt}")

# ---- 6. Resolve -------------------------------------------------------------
print("== 6. Backlog Q001 resolve moves the row to ## Done ==")
reset()
run(args("Backlog", "Q+", "define", body=q_body()))
rc, out, err = run(args("Backlog", "Q001", "resolve", body="took (A)"))
txt = BL.read_text()
done_seg = txt.split("## Done", 1)[-1]
ok("Q001 resolved into ## Done as [Done]") \
    if ("- **Q001 —" in done_seg and "[Done]" in done_seg and "resolved" in done_seg) \
    else no(f"resolve wrong:\nOUT={out!r}\nTXT={txt}")

# ---- 7. Collision guard — doc-scoped Q untouched ---------------------------
print("== 7. Q+ on a DOC still routes to the doc's Open Questions ==")
doc = TMP / "ZZQ PRD.md"
doc.write_text("---\ndescription: t\n---\n\n# [[ZZQ]] PRD\nOrient.\n\n## Summary\n\nbody\n",
               encoding="utf-8")
st._post_conditions_and_print = lambda *a, **k: None
dbody = ("- **Q+ — doc-scoped question?**\n"
         "  - **(A)** first.\n"
         "  - **(B)** second.\n"
         "- **Recommendation:** None. genuine fork\n"
         "- **Damage:** other — a real fork")
rc, out, err = run(args(str(doc), "Q+", "define", body=dbody))
dtxt = doc.read_text()
ok("doc-scoped Q+ still lands in the doc's Open Questions (no Backlog collision)") \
    if ("## Open Questions" in dtxt and "**Q1 —" in dtxt) \
    else no(f"doc-scoped Q regressed:\nOUT={out!r}\nERR={err!r}\nTXT={dtxt}")

import shutil
shutil.rmtree(TMP, ignore_errors=True)
print("-" * 40)
print(f"F275 Q-row test: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
