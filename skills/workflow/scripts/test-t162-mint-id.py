#!/usr/bin/env python3
"""test-t162-mint-id.py — TINK T162 (2): a Backlog row with no id has no
address, and `state mint-id` is the sanctioned way to give it one.

The defect. Every `state` verb addresses a row by the bolded label
`ROW_HEADER_RE` reads — `- **T042 — …**`. Two live vault rows (MUX
`[BUG] Drift terminal window display freezes…`, HA `Non-anchor-doc file
descriptions out of frontmatter`) open with prose instead, so `set`, `resolve`,
`remove` and `show` could none of them name them: permanently unbracketable,
uncloseable, and invisible to every count. The only repair was to type an id
into the backlog by hand, which is exactly the write the F247 stamp and the
whole `state` grammar exist to prevent — a closed loop.

The fix mints BOTH handles at once and requires them to be equal: the bolded
`**T042 — …**` that `state` resolves, and the trailing `^T042` that an inbound
`[[MUX Backlog#^T042|T042]]` resolves. A row carrying only one of them is
readable by only one of its two readers.

  A. the census      — `_idless_rows` finds prose rows and only prose rows
  B. the mint        — both handles land, equal, and the body survives verbatim
  C. addressability  — the T162 claim itself: `show` / `set` can now reach it
  D. ambiguity       — 0 or >1 matches refuse and list, never guess
  E. collision       — an explicit id already in use refuses
  F. an existing `^anchor` refuses — replacing it breaks inbound links silently
  G. no half-write   — a refusal leaves the backlog byte-identical

Self-contained: loads `state` in-process, stubs every seam that reaches the
real vault (Warden self-fire, Messages, state.json, audit-q). Never touches the
real vault."""
import importlib.machinery
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
_loader = importlib.machinery.SourceFileLoader("state_mod", str(HERE / "state"))
_spec = importlib.util.spec_from_loader("state_mod", _loader)
st = importlib.util.module_from_spec(_spec)
sys.modules["state_mod"] = st
_loader.exec_module(st)
be = st.be

# Never touch the real vault: no Warden fire, no Messages append, no
# state.json, no audit-q subprocess, no stamp-heal walking the vault.
st._selffire = lambda *a, **k: None
be._selffire = lambda *a, **k: None
be.append_messages = lambda *a, **k: None
be.write_state = lambda *a, **k: None
be.refresh_q_md = lambda *a, **k: None
be.heal_backlog_if_stale = lambda *a, **k: None
be.find_icebox = lambda slug: None

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


BACKLOG = """---
description: fixture
---
# ZZT Backlog

## Now

- **T900 — an ordinary row that already has an id** [Ready] — body. ^T900

## Later

- **[BUG] Drift terminal window display freezes after rapid resize burst — 2026-05-12** [Waiting] — Watching for natural recurrence. **NEW** failure mode observed. Severity **[MED]**.
- **Non-anchor-doc file descriptions out of frontmatter** [Waiting] — waiting on a vault-wide standard for where per-file descriptions live.
- **Session name unification across HA and MuxUX** [Blocked F052] — unify on `session name = slug()`.
- **Rename `patch` → `anchor` throughout data model** [Blocked] ^patch-anchor-rename — parked 2026-04-30.
"""


class Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def mint(path, label, match):
    return st._row_mint_id("ZZT", path, label, Args(match=match))


TMP = Path(tempfile.mkdtemp())
try:
    def fresh(name="ZZT Backlog.md"):
        p = TMP / name
        p.write_text(BACKLOG, encoding="utf-8")
        return p

    # ---- A: the census ---------------------------------------------------
    print("== A: _idless_rows sees prose rows, and only prose rows ==")
    bl = fresh()
    census = st._idless_rows(bl.read_text(encoding="utf-8").splitlines(keepends=True))
    titles = [t for _i, t, _s in census]
    if len(census) == 4:
        ok("4 id-less rows found in the fixture")
    else:
        no(f"expected 4 id-less rows, found {len(census)}: {titles}")
    if not any("T900" in t for t in titles):
        ok("the row that HAS an id is not in the census")
    else:
        no("an id-bearing row was miscounted as id-less")
    if any(t.startswith("[BUG] Drift") for t in titles):
        ok("the MUX-shaped `[BUG] …` row is in the census")
    else:
        no(f"the `[BUG] …` row was missed: {titles}")

    # ---- B: the mint -----------------------------------------------------
    print("== B: mint-id writes both handles, equal, and keeps the body ==")
    bl = fresh()
    rc = mint(bl, "T+", "Non-anchor-doc file descriptions")
    txt = bl.read_text(encoding="utf-8")
    row = next((l for l in txt.splitlines()
                if "Non-anchor-doc file descriptions" in l), "")
    if rc == 0:
        ok("mint-id returned 0")
    else:
        no(f"mint-id returned {rc}")
    if row.startswith("- **T901 — Non-anchor-doc file descriptions out of frontmatter**"):
        ok("the row-id was minted as the next free T number (T901)")
    else:
        no(f"unexpected row head: {row[:90]!r}")
    if row.rstrip().endswith("^T901"):
        ok("the matching `^T901` block anchor was appended")
    else:
        no(f"block anchor missing or wrong: {row[-30:]!r}")
    if "[Waiting] — waiting on a vault-wide standard for where per-file " \
       "descriptions live." in row:
        ok("bracket and body survived the splice verbatim")
    else:
        no(f"body was altered: {row!r}")
    # The other three id-less rows are untouched.
    if len(st._idless_rows(txt.splitlines(keepends=True))) == 3:
        ok("exactly one row was changed — the other three stay id-less")
    else:
        no("mint-id touched more than the matched row")

    # ---- C: addressability — the actual T162 claim -----------------------
    print("== C: the minted row is now reachable by the ordinary verbs ==")
    lines = txt.splitlines(keepends=True)
    if st._row_span(lines, "T901") is not None:
        ok("_row_span (what `show` uses) now finds the row")
    else:
        no("_row_span still cannot find the row — it is still unaddressable")
    _l, _h, index = be.scan_backlog(txt)
    if "T901" in index:
        ok("scan_backlog (what every editor uses) indexes the row")
    else:
        no("scan_backlog does not index the row")
    if index.get("T901", (None, None, None))[2] == "Later":
        ok("the row kept its horizon (## Later)")
    else:
        no(f"horizon changed to {index.get('T901', (None,) * 3)[2]!r}")

    # A `[BUG]`-shaped title round-trips through ROW_FULL_RE, which is what
    # `set`/`resolve` parse a row line with — the bold runs in its body are the
    # hazard, since the title group is non-greedy to the first `**`.
    bl2 = fresh("ZZT2 Backlog.md")
    mint(bl2, "F+", "Drift terminal window display freezes")
    bug = next(l for l in bl2.read_text(encoding="utf-8").splitlines()
               if "Drift terminal" in l)
    m = be.ROW_FULL_RE.match(bug)
    if m and m.group("rid") == "F001":
        ok("a `[BUG] …` row with **bold** in its body parses back as F001")
    else:
        no(f"ROW_FULL_RE could not parse the minted row: {bug[:100]!r}")
    if m and m.group("title", ).endswith("2026-05-12"):
        ok("the title group stops at the closing `**`, not at inner bold")
    else:
        no(f"title mis-parsed: {(m.group('title') if m else None)!r}")

    # ---- D: ambiguity ----------------------------------------------------
    print("== D: 0 or >1 matches refuse and list, never guess ==")
    bl = fresh()
    before = bl.read_text(encoding="utf-8")
    try:
        mint(bl, "T+", "no such row anywhere")
        no("a zero-match --match should refuse")
    except be.BacklogEditError as ex:
        if "no id-less row" in str(ex) and "Session name unification" in str(ex):
            ok("zero matches refuse AND list the candidates")
        else:
            no(f"wrong zero-match message: {ex}")
    try:
        mint(bl, "T+", "o")           # matches every one of the four
        no("an ambiguous --match should refuse")
    except be.BacklogEditError as ex:
        if "names 4 id-less rows" in str(ex):
            ok("an ambiguous match refuses and reports the count")
        else:
            no(f"wrong ambiguity message: {ex}")

    # ---- E: explicit-id collision ----------------------------------------
    print("== E: an explicit id already in use refuses ==")
    try:
        mint(bl, "T900", "Non-anchor-doc")
        no("minting T900 over a live row should refuse")
    except be.BacklogEditError as ex:
        if "already names a row" in str(ex):
            ok("a taken explicit id refuses")
        else:
            no(f"wrong collision message: {ex}")

    # ---- F: an existing block anchor is not replaced ---------------------
    print("== F: a row that already carries a `^anchor` refuses ==")
    try:
        mint(bl, "T+", "Rename `patch`")
        no("a row with ^patch-anchor-rename should refuse")
    except be.BacklogEditError as ex:
        if "already carries the block anchor" in str(ex) \
                and "^patch-anchor-rename" in str(ex):
            ok("an existing block anchor refuses, naming the anchor at risk")
        else:
            no(f"wrong existing-anchor message: {ex}")

    # ---- G: no half-write ------------------------------------------------
    print("== G: every refusal above left the backlog byte-identical ==")
    if bl.read_text(encoding="utf-8") == before:
        ok("four refusals, zero bytes changed")
    else:
        no("a refused mint-id still wrote to the backlog")

    # A landed mint is idempotent-safe in the sense that matters: the row is no
    # longer in the census, so a second identical call refuses rather than
    # stacking a second id onto the same line.
    bl = fresh()
    mint(bl, "T+", "Session name unification")
    try:
        mint(bl, "T+", "Session name unification")
        no("a second mint onto the same row should refuse")
    except be.BacklogEditError as ex:
        ok("a re-mint refuses — the row is no longer id-less") \
            if "no id-less row" in str(ex) else no(f"wrong re-mint message: {ex}")
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
