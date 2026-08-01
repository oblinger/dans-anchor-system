#!/usr/bin/env python3
"""test-f250-residuals.py — F253 Step 2: the non-CRITICAL F250 Fable-scan
residual fixes in the `state` CLI.

  #6  (HIGH) `_sync_roadmap_on_done` over-flipped — it marked EVERY line
      mentioning the F-number `[x]`: milestone headings, deferred `[~]` rows,
      and secondary cross-refs. Now: inline rows only, primary (first) F-ref
      only, unchecked `[ ]` boxes only, unique-match-or-refuse.
  #11 (MED)  `_find_doc_by_basename` surfaced one real doc as several candidates
      (symlink mirrors / Closet copies) → false "ambiguous" refusal. Now skips
      `/symlinks/` + `/Closet/` and dedupes by resolved path.
  #12 (LOW)  `"revalidate" in argv` membership hijacked dispatch whenever the
      word appeared anywhere. F250 narrowed that to a shape-matcher; F293
      deleted the ambiguity outright — the verb is now the FIRST token, so
      dispatch never has to guess which token was meant to be one. The case
      list below survives as a regression pin on the new grammar.

Self-contained: imports the `state` module in-process, builds fixtures in a
tmpdir, cleans up. Never touches the real vault (warden self-fire disabled)."""
import importlib.machinery
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

STATE = Path(__file__).parent / "state"
loader = importlib.machinery.SourceFileLoader("state_mod", str(STATE))
spec = importlib.util.spec_from_loader("state_mod", loader)
st = importlib.util.module_from_spec(spec)
sys.modules["state_mod"] = st
loader.exec_module(st)
st._warden_selffire = None  # disable warden self-fire for fixture writes

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")

TMP = Path(tempfile.mkdtemp())
try:
    # ---- #6: _sync_roadmap_on_done precision --------------------------------
    print("== #6 roadmap auto-sync flips only the feature's own inline [ ] row ==")
    anchor = TMP / "ANCHOR"
    bl = anchor / "ZZR Track" / "ZZR Backlog.md"
    bl.parent.mkdir(parents=True, exist_ok=True)
    bl.write_text("# ZZR Backlog\n", encoding="utf-8")
    rm = anchor / "ZZR Design" / "ZZR Roadmap.md"
    rm.parent.mkdir(parents=True, exist_ok=True)
    ROADMAP = (
        "# ZZR Roadmap\n\n"
        "## [ ] M1 — Milestone touching [[F250 — state|F250]]\n\n"
        "- [ ] **1 · [[F250 — state|F250]]** — de-risks [[F247 — sole|F247]].\n"
        "- [~] **2 · [[F251 — audit|F251]]** — deferred, do not flip.\n"
        "- [x] **3 · [[F252 — muse|F252]]** — already done.\n"
        "- [ ] **A · [[F260 — dup|F260]]** — first dup.\n"
        "- [ ] **B · [[F260 — dup2|F260]]** — second dup.\n"
    )

    def reset_roadmap():
        rm.write_text(ROADMAP, encoding="utf-8")

    # (a) F250 resolves → its inline [ ] flips to [x]; heading + [~] untouched.
    reset_roadmap()
    msg = st._sync_roadmap_on_done("ZZR", bl, "F250")
    out = rm.read_text(encoding="utf-8")
    if (msg and "- [x] **1 · [[F250" in out
            and "## [ ] M1 — Milestone touching [[F250" in out
            and "- [~] **2 · [[F251" in out):
        ok("F250 Done flips its inline row; milestone heading + [~] deferred untouched")
    else:
        no(f"F250 sync wrong — msg={msg!r}\n{out}")

    # (b) F247 appears ONLY as a secondary cross-ref on the F250 row (no own
    #     primary row) → no flip (primary-F-ref discipline).
    reset_roadmap()
    msg = st._sync_roadmap_on_done("ZZR", bl, "F247")
    out = rm.read_text(encoding="utf-8")
    if msg is None and "- [ ] **1 · [[F250" in out:
        ok("F247 (secondary cross-ref only) does not flip the F250 row")
    else:
        no(f"F247 wrongly flipped a row — msg={msg!r}\n{out}")

    # (c) F251 is deferred [~] → never flipped.
    reset_roadmap()
    msg = st._sync_roadmap_on_done("ZZR", bl, "F251")
    out = rm.read_text(encoding="utf-8")
    if msg is None and "- [~] **2 · [[F251" in out:
        ok("F251 deferred [~] row is never flipped to [x]")
    else:
        no(f"F251 deferred row wrongly touched — msg={msg!r}\n{out}")

    # (d) F260 has two primary rows → ambiguous → refuse (unique-match).
    reset_roadmap()
    msg = st._sync_roadmap_on_done("ZZR", bl, "F260")
    out = rm.read_text(encoding="utf-8")
    if (msg is None and "- [ ] **A · [[F260" in out
            and "- [ ] **B · [[F260" in out):
        ok("F260 ambiguous (two primary rows) → no flip, both untouched")
    else:
        no(f"F260 ambiguity not refused — msg={msg!r}\n{out}")

    # ---- #12: the verb token, and nothing else, decides dispatch -----------
    print("== #12 the word 'revalidate' in a value cannot hijack dispatch ==")
    parser = st.build_parser()
    cases = [
        (["revalidate", "SKA", "MyDoc"], "revalidate", "the genuine doc verb"),
        (["remove", "SKA", "Backlog", "F5", "--reason", "revalidate"],
         "remove", "revalidate as a --reason value"),
        (["set", "SKA", "Backlog", "F5", "--body", "please revalidate this"],
         "set", "revalidate inside a body value"),
        (["define", "SKA", "revalidate", "F5"], "define",
         "a doc literally named 'revalidate'"),
    ]
    for argv, want, desc in cases:
        got = parser.parse_args(argv).verb
        if got == want:
            ok(f"{desc} → {want}")
        else:
            no(f"{desc}: routed to {got!r}, want {want!r}")

    # The doc verb declares no label, so the v2 shape that needed a
    # last-token check to disambiguate is now a parse error by construction.
    try:
        parser.parse_args(["revalidate", "SKA", "MyDoc", "Q1"])
        no("revalidate accepted a label it does not declare")
    except SystemExit:
        ok("revalidate refuses a <label> — the doc verb takes none")

    # ---- #11: _find_doc_by_basename dedup + skip -----------------------------
    print("== #11 basename search dedupes symlink copies + skips /symlinks/,/Closet/ ==")
    root = TMP / "search"
    real = root / "ANCHOR" / "ZZR Track"
    real.mkdir(parents=True, exist_ok=True)
    (real / "Foo.md").write_text("x", encoding="utf-8")
    # A symlinked dir pointing back at the tree → Foo.md reachable twice.
    link = root / "ANCHOR" / "mirror"
    try:
        os.symlink(real, link, target_is_directory=True)
        foo = st._find_doc_by_basename(root, "foo.md")
        if len(foo) == 1:
            ok("Foo.md reachable via a symlinked dir returns a single candidate")
        else:
            no(f"Foo.md deduped wrong — {len(foo)} matches: {foo}")
    except OSError as e:
        no(f"symlink unsupported in test env — skipped dedup check ({e})")

    # A copy living under /symlinks/ is skipped; the real one is found once.
    sk = root / "ANCHOR" / "symlinks"
    sk.mkdir(parents=True, exist_ok=True)
    (sk / "Bar.md").write_text("y", encoding="utf-8")
    (real / "Bar.md").write_text("z", encoding="utf-8")
    bar = st._find_doc_by_basename(root, "bar.md")
    if len(bar) == 1 and "/symlinks/" not in str(bar[0]):
        ok("Bar.md under /symlinks/ is skipped; only the live copy is returned")
    else:
        no(f"/symlinks/ not skipped — {len(bar)} matches: {bar}")

finally:
    import shutil
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
