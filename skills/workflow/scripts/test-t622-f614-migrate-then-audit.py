#!/usr/bin/env python3
"""test-t622-f614-migrate-then-audit.py — TINK T622 + T621.

F614 shipped 2026-08-28 with two bugs the same shape — a guard its own
sanctioned repair could not satisfy — and MUX patched both in place:

  1. audit-q C59 tested `raw_body.lstrip().startswith("→ [[")`, but raw_body
     is the WHOLE row line, so the check flagged 100% of live T rows — the
     rows `state migrate-t` had just converted included.
  2. backlog-edit.py raised IndexError on a row with an EMPTY bracket (`[ ]`):
     `want_status.split()[0]` on whitespace. migrate-t died mid-run on it.

And T621 (Presti, SVAR T003): a row with NO bracket is visible to audit-q's
parser and invisible to ROW_FULL_RE, so migrate-t said "nothing to migrate"
while C59 kept flagging it; `state set` then told the agent to "fix the row
by hand", which Warden forbids. Plus the define-side Q gate accepted a nested
Recommendation that audit-q C10 refuses.

The test that would have caught all of it: run migrate-t on a fixture, then
assert audit-q reads what it should.
"""
import sys as _sys; _sys.dont_write_bytecode = True

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "state"
AUDITQ = HERE.parent.parent / "audit" / "scripts" / "audit-q.py"
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


ROOT = TMP / "vault"
ANCHOR = ROOT / "FIX"
BACKLOG = ANCHOR / "FIX Track" / "FIX Backlog" / "FIX Backlog.md"
DOC = ANCHOR / "FIX Design" / "FIX Features" / "FIX001 - A doc-backed feature.md"

ROWS = """---
description: fixture backlog
---

# FIX Backlog

## Now

- **T001 — An inline task with a bracket** [Ready] — plain inline body. ^T001
  - **Next:** do the inline thing.
- **T002 — An inline task with an EMPTY bracket** [ ] — parked inline body. ^T002
- **T003 — A task with no bracket at all** — bracketless inline body.
- **F001 — A doc-backed feature** [Ready] — → [[FIX001 - A doc-backed feature|F001]] — original doc-backed body. ^F001
  - **Next:** do the doc-backed thing.

## Next

## Later

## Done

- **T009 — A finished inline task** [Done] — history. ^T009
"""

FEATURE = """---
description: fixture feature
---

# [[FIX]] · F001 — A doc-backed feature
One line.

## Summary

Fixture.

## Status

Ready — fixture.
"""


def build():
    shutil.rmtree(ROOT, ignore_errors=True)
    BACKLOG.parent.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(parents=True, exist_ok=True)
    (ANCHOR / ".anchor").write_text("slug: FIX\nfeeds:\n", encoding="utf-8")
    BACKLOG.write_text(ROWS, encoding="utf-8")
    DOC.write_text(FEATURE, encoding="utf-8")
    (ROOT / "Q.md").write_text("# Q\n", encoding="utf-8")


def env():
    return {**os.environ, "ANCHOR_VAULT_ROOT": str(ROOT)}


def state(*args):
    r = subprocess.run([sys.executable, str(STATE), *args],
                       capture_output=True, text=True, env=env())
    return r.returncode, r.stdout + r.stderr


def c59_rows():
    r = subprocess.run([sys.executable, str(AUDITQ), "--scope", "backlog",
                        "--anchor", "FIX", "--dry"],
                       capture_output=True, text=True, env=env())
    out = r.stdout + r.stderr
    rows = set()
    for line in out.splitlines():
        if "C59" in line and "inline T row" in line:
            for rid in ("T001", "T002", "T003", "T009", "F001"):
                if f"'{rid}'" in line:
                    rows.add(rid)
    return rows, out


try:
    # ============================================================
    print("== A: before migration, C59 flags the inline rows and nothing else ==")
    # ============================================================
    build()
    rows, out = c59_rows()
    if rows == {"T001", "T002", "T003"}:
        ok("C59 flags exactly T001, T002, T003 — not the doc-backed F001, not the Done T009")
    else:
        no(f"C59 rows before migrate: {sorted(rows)} — expected T001, T002, T003\n{out[-800:]}")

    # ============================================================
    print("== B: migrate-t converts the bracketed rows, survives the empty bracket, names the bracketless one ==")
    # ============================================================
    rc, out = state("migrate-t", "FIX")
    if "T001 →" in out and "T002 →" in out:
        ok("T001 and T002 both migrated to docs")
    else:
        no(f"migrate-t did not convert both rows:\n{out}")
    if "IndexError" in out or "Traceback" in out:
        no(f"migrate-t crashed:\n{out}")
    else:
        ok("no crash on the `[ ]` row (MUX patch to verify_write_landed holds)")
    if "T003" in out and "no `[status]` bracket" in out and rc != 0:
        ok("the bracketless T003 is named as unparseable with the remove→define recipe, and the run exits non-zero")
    else:
        no(f"bracketless row not surfaced (rc={rc}):\n{out}")
    text = BACKLOG.read_text()
    if "→ [[FIX001 - An inline task" in text and "→ [[FIX002 - An inline task" in text:
        ok("both rows now lead with their doc pointer")
    else:
        no(f"rows not rewritten as pointers:\n{text}")

    # ============================================================
    print("== C: after migration, C59 reads the remaining gap only ==")
    # ============================================================
    rows, out = c59_rows()
    if rows == {"T003"}:
        ok("C59 reads only T003 after migrate-t — the fixer's output passes the checker")
    else:
        no(f"C59 rows after migrate: {sorted(rows)} — expected only T003\n{out[-800:]}")

    # ============================================================
    print("== D: state set on the bracketless row names the real repair path ==")
    # ============================================================
    rc, out = state("set", "FIX", "Backlog", "T003", "--status", "Ready")
    if "by hand" in out:
        no(f"refusal still says to hand-edit a state-owned backlog:\n{out}")
    elif "state remove" in out and "state define" in out:
        ok("refusal names remove → define and warns to copy the printed row first")
    else:
        no(f"unexpected refusal text:\n{out}")

    # ============================================================
    print("== E: a doc Q with a NESTED Recommendation is refused at define, as C10 would refuse it ==")
    # ============================================================
    build()
    nested = ("- **Q1 — Which way?** Context.\n"
              "    - **(A)** left.\n"
              "    - **(B)** right.\n"
              "    - **Damage:** locking — one sentence.\n"
              "    - **Recommendation:** None.\n")
    rc, out = state("define", "FIX", "FIX001 - A doc-backed feature", "Q+", "--body", nested)
    if rc != 0 and "indent 0" in out:
        ok("nested Recommendation refused at define with the C10 wording")
    else:
        no(f"nested Recommendation accepted (rc={rc}):\n{out}")
    flat = nested.replace("    - **Recommendation:** None.", "- **Recommendation:** None.")
    rc, out = state("define", "FIX", "FIX001 - A doc-backed feature", "Q+", "--body", flat)
    if rc == 0 and "defined Q" in out:
        ok("indent-0 Recommendation accepted")
    else:
        no(f"indent-0 Recommendation refused (rc={rc}):\n{out}")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
