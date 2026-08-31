#!/usr/bin/env python3
"""T629–T632 (Tink Inbox drain, 2026-08-30) — four F614-fallout fixes:

  T629  `_read_banner_counts` resolves `{slug} queries.md` against the Track
        folder (folder-form backlogs put the backlog one level down), and
        REFUSES on an empty scrape instead of reporting all-zero counts.
  T630  `state define` is all-or-nothing: a doc minted for a row whose
        bracket contract is then refused is rolled back.
  T631  Q.md banner dedupe keys on the `[[{X} queries|…]]` link TARGET, so a
        relabelled anchor's old section is recognised and replaced.
  T632  a struck pointer (`→ ~~[[Old|T1]]~~`) inside a doc's next:: /
        description / orientation never reaches the derived row line.
"""
import sys as _sys; _sys.dont_write_bytecode = True
import importlib.machinery, importlib.util, io, contextlib, os, re, tempfile, time
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    _sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


st = _load("state_mod", HERE / "state")
be = st.be
PASS = FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")
def check(c, m): ok(m) if c else no(m)

# ---- T629 -------------------------------------------------------------------
print("== T629: banner counts on a folder-form backlog ==")
with tempfile.TemporaryDirectory() as td:
    trk = Path(td) / "ZZ Track"
    folder_bl = trk / "ZZ Backlog" / "ZZ Backlog.md"
    folder_bl.parent.mkdir(parents=True)
    folder_bl.write_text("# ZZ Backlog\n\n## Now\n\n## Done\n", encoding="utf-8")
    flat_bl = Path(td) / "flat" / "ZY Track" / "ZY Backlog.md"
    flat_bl.parent.mkdir(parents=True)
    flat_bl.write_text("# ZY Backlog\n", encoding="utf-8")
    check(st._track_dir(folder_bl, "ZZ") == trk, "folder form: Track dir is one level above the backlog folder")
    check(st._track_dir(flat_bl, "ZY") == flat_bl.parent, "flat form: Track dir is the backlog's own parent")
    q = trk / "ZZ queries.md"
    q.write_text("---\ndescription: x\n---\n# [U]  [[ZZ queries|ZZ]]  -  Ready 3    User 1   |   Now 2\n", encoding="utf-8")
    later = time.time() + 5
    os.utime(q, (later, later))          # newer than the backlog → no re-render attempt
    counts = st._read_banner_counts(folder_bl, "ZZ")
    check(counts.get("runnable") == 3 and counts.get("user") == 1,
          f"counts come from the Track-folder render on a folder-form backlog ({counts})")
    q.unlink()
    try:
        st._read_banner_counts(folder_bl, "ZZ")
        no("an absent render must refuse, not report zeros")
    except be.BacklogEditError as ex:
        check("refusing to report counts" in str(ex) and "ZZ queries.md" in str(ex),
              "absent render refuses and names the path it looked at")

# ---- T630 -------------------------------------------------------------------
print("== T630: define rolls the minted doc back when the row is refused ==")
st._selffire = lambda *a, **k: None
be._selffire = lambda *a, **k: None
be.find_icebox = lambda slug: None
with tempfile.TemporaryDirectory() as td:
    bl = Path(td) / "ZZ Track" / "ZZ Backlog" / "ZZ Backlog.md"
    bl.parent.mkdir(parents=True)
    bl.write_text("# ZZ Backlog\n\n## Now\n\n## Done\n", encoding="utf-8")
    args = SimpleNamespace(horizon="Now", why_user=None, why_user_action=None,
                           inline=None, from_file=None)
    real_delegate = st._delegate_row_edit

    def refusing(*a, **k):
        raise be.BacklogEditError("[User] refused: T001 needs a - **User:** action")
    st._delegate_row_edit = refusing
    row = "- **T001 — Needs your login** [User] — log into the thing"
    try:
        st._row_define("ZZ", bl, "T001", args, raw_override=row)
        no("refusal did not propagate")
    except be.BacklogEditError:
        docs = list(bl.parent.glob("ZZ001*.md"))
        check(not docs, f"refused row leaves no orphan doc behind (found {[d.name for d in docs]})")
    # a doc that already existed is NOT the mint's to delete
    pre = bl.parent / "ZZ002 - Pre-existing.md"
    pre.write_text("# pre\n", encoding="utf-8")
    try:
        st._row_define("ZZ", bl, "T002", args, raw_override="- **T002 — Pre-existing** [User] — x")
    except be.BacklogEditError:
        pass
    check(pre.is_file(), "a pre-existing doc survives a refused define (only the mint's own file is withdrawn)")
    # success path keeps the doc
    st._delegate_row_edit = lambda *a, **k: 0
    st._row_define("ZZ", bl, "T003", args, raw_override="- **T003 — Fine** [Ready] — x\n  - **Next:** go")
    check(bool(list(bl.parent.glob("ZZ003*.md"))), "an accepted define keeps its doc")
    st._delegate_row_edit = real_delegate

# ---- T631 -------------------------------------------------------------------
print("== T631: Q.md dedupe keys on the queries-doc target ==")
src = (HERE.parent.parent / "audit" / "scripts" / "queries-render.py").read_text(encoding="utf-8")
m = re.search(r"QMD_BANNER_RE_TEMPLATE = \((.*?)\n\)", src, re.S)
tmpl = eval("(" + "\n".join(l for l in m.group(1).splitlines() if not l.strip().startswith("#")) + ")")
rx = re.compile(tmpl.format(name=re.escape("Atticus")))
check(bool(rx.match("# [U]  [[Atticus queries|Atticus]]  -  Ready 0")), "current-label banner matches")
check(bool(rx.match("# [U]  [[Atticus queries|ATT]]  -  Ready 1")), "old-label banner on the same queries doc matches (the orphan is recognised)")
check(bool(rx.match("# [U]  [[Atticus Triage|ATT]]  -  Ready 1")), "legacy Triage target under an old label matches")
check(not rx.match("# [U]  [[Atticus Rocks|ATT]]  -  x"), "a non-queries target under an old label does not match (only the label or the queries/Triage target keys)")
check(not rx.match("# [U]  [[Winnie queries|Winnie]]  -  Ready 0"), "another anchor's banner does not match")
check(not rx.match("# [U]  [[Atticus queries and more|X]]"), "a longer target sharing the prefix does not match")

# ---- T632 -------------------------------------------------------------------
print("== T632: struck pointers never reach the derived line ==")
sp = be._strip_struck_pointers
check(sp("→ ~~[[Old Name|T177]]~~ — On 2026-08-27: rotate") == "On 2026-08-27: rotate", "leading struck pointer + dash removed")
check(sp("keep this — → ~~[[Old|T1]]~~") == "keep this —" or sp("keep this — → ~~[[Old|T1]]~~").startswith("keep this"), "trailing struck pointer removed")
check(sp("→ ~~[[Only|T1]]~~") is None, "a field that was only a struck pointer yields None (falls through)")
check(sp("plain text") == "plain text" and sp("") is None, "text without a struck pointer is untouched")
with tempfile.TemporaryDirectory() as td:
    doc = Path(td) / "ZZ001 - thing.md"
    doc.write_text("---\ndescription: \"→ ~~[[ZZ001 - old|T001]]~~ — the description\"\n---\n\n"
                   "# [[ZZ]] · T001 — thing\n→ ~~[[ZZ001 - old|T001]]~~ — orientation here\n\n"
                   "next:: → ~~[[ZZ001 - old|T001]]~~ — do the next thing\n", encoding="utf-8")
    check(be.doc_derived_line(doc) == "do the next thing", f"next:: with a struck pointer derives clean ({be.doc_derived_line(doc)!r})")
    doc.write_text(doc.read_text(encoding="utf-8").replace("next:: → ~~[[ZZ001 - old|T001]]~~ — do the next thing\n", ""), encoding="utf-8")
    check(be.doc_derived_line(doc) == "the description", "description with a struck pointer derives clean")

print("-" * 40)
print(f"{PASS} passed, {FAIL} failed")
_sys.exit(1 if FAIL else 0)
