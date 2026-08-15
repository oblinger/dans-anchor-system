#!/usr/bin/env python3
"""test-f275-q-row.py — F275 `Q###` Backlog rows, POST-F329.

F329 retired the standalone-question row: questions live in docs (feature
docs or T-docs in the folder-form backlog), and the backlog hosts pointers.
This suite pins the retirement contract:

  1. `Backlog Q+ define` REFUSES with the F329 message (was: minted Q001).
  2. An EXISTING legacy Q-row stays addressable — `resolve` still moves it
     to ## Done (migration is on touch, never a forced sweep).
  3. Doc-scoped `Q+ define` still routes to the doc's Open Questions —
     that is the sanctioned home and must not be caught by the row gate.
  4. The F329 inline-Q gate: a define that ADDS a pending `- **Q<n>` sub-
     bullet to an F/T row refuses; an edit that leaves a legacy row's
     existing inline Qs untouched passes.

Self-contained: loads `state` in-process, stubs the vault I/O, tmp files only."""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import contextlib
import importlib.machinery
import importlib.util
import io
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
# T042 carries a LEGACY inline Q (pre-F329 corpus); Q001 is a legacy
# standalone question row.
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
    "- **T042 — legacy row with an inline question** [Questions] — carried from before F329. ^T042\n"
    "  - **Q1 — keep or drop the widget?** ^T042-Q1\n"
    "  - **(A)** keep it.\n"
    "  - **(B)** drop it.\n"
    "  - **Recommendation:** None — genuine fork.\n"
    "  - **Damage:** other — a real fork.\n"
    "- **Q001 — legacy standalone question, pre-F329** [Questions] — the row body is the question ^Q001\n"
    "  - **(A)** take the replacements.\n"
    "  - **(B)** leave the habits alone.\n"
    "  - **Recommendation:** None — genuine fork.\n"
    "  - **Damage:** other — a real fork.\n"
    "  - **On answer:** (A) → land it; (B) → leave it.\n"
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


def args(doc, label, verb, body=None, why_ask=None, status=None, next_step=None):
    return SimpleNamespace(
        doc=doc, label=label, verb=verb, inline=body, from_file=None,
        why_ask=why_ask, horizon=None, status=status, title=None,
        next_step=next_step, verify=None, user=None, why_user=None,
        why_user_action=None,
    )


def run(a):
    """Invoke cmd_item capturing stdout+stderr; return (rc, out, err)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = st.cmd_item("ZZQ", TMP, a)
    return rc, out.getvalue(), err.getvalue()


def reset():
    BL.write_text(BACKLOG, encoding="utf-8")


Q_BODY = (
    "- **Q+ — Swap the 3 straggler vocab words, or leave them?** "
    "[Questions] — spoken-vocabulary word list, not any feature\n"
    "  - **(A)** take the verified replacements.\n"
    "  - **(B)** leave the daily habits alone.\n"
    "  - **Recommendation:** None — genuine fork.\n"
    "  - **Damage:** other — a real fork.\n"
    "  - **On answer:** (A) → land it; (B) → leave it."
)

# ---- 1. Q+ define refuses (F329) -------------------------------------------
print("== 1. Backlog Q+ define is REFUSED (F329 — questions live in docs) ==")
reset()
try:
    run(args("Backlog", "Q+", "define", body=Q_BODY))
    no("Q+ define should refuse")
except be.BacklogEditError as e:
    ok("Q+ define refused with the F329 message") if "F329" in str(e) \
        else no(f"wrong error: {e}")
txt = BL.read_text()
ok("backlog untouched by the refused mint") if txt == BACKLOG \
    else no("refused mint still mutated the backlog")

# ---- 2. Legacy Q-row still resolves ----------------------------------------
print("== 2. an EXISTING legacy Q-row still resolves into ## Done ==")
reset()
rc, out, err = run(args("Backlog", "Q001", "resolve", body="took (A)"))
txt = BL.read_text()
done_seg = txt.split("## Done", 1)[-1]
ok("legacy Q001 resolved into ## Done as [Done]") \
    if ("- **Q001 —" in done_seg and "[Done]" in done_seg) \
    else no(f"resolve wrong:\nOUT={out!r}\nERR={err!r}\nTXT={txt}")

# ---- 3. Doc-scoped Q+ untouched --------------------------------------------
print("== 3. Q+ on a DOC still routes to the doc's Open Questions ==")
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
ok("doc-scoped Q+ still lands in the doc's Open Questions") \
    if ("## Open Items" in dtxt and "**Q1 —" in dtxt) \
    else no(f"doc-scoped Q regressed:\nOUT={out!r}\nERR={err!r}\nTXT={dtxt}")

# ---- 4. Inline-Q gate on F/T rows ------------------------------------------
print("== 4. F329 inline-Q gate — adding a Q sub-bullet to a row refuses ==")
reset()
tbody = ("- **T+ — new task carrying an inline question** [Questions] — should refuse\n"
         "  - **Q1 — inline question smuggled onto the row?**\n"
         "  - **(A)** yes.\n"
         "  - **(B)** no.\n"
         "  - **Recommendation:** None — fork.")
try:
    run(args("Backlog", "T+", "define", body=tbody))
    no("define adding an inline Q should refuse")
except be.BacklogEditError as e:
    ok("new inline Q on a T-row refused (F329)") if "F329" in str(e) \
        else no(f"wrong error: {e}")

reset()
rc, out, err = run(args("Backlog", "T042", "set", status="Questions",
                        next_step="await the answer"))
txt = BL.read_text()
ok("touch-edit of a legacy row with existing inline Qs passes") \
    if ("- **T042" in txt and "await the answer" in txt) \
    else no(f"legacy-row touch wrongly refused:\nOUT={out!r}\nERR={err!r}")

import shutil

shutil.rmtree(TMP, ignore_errors=True)
print("-" * 40)
print(f"F275 Q-row test (post-F329): {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
