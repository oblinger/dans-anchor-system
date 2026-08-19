#!/usr/bin/env python3
"""test-t244-doc-q-title.py — `--title` binds on a DOC-hosted item.

T244: `--title` is declared on the `set` subparser, but `_query_verb` never
read it. On a Backlog row it worked; on a `Q<n>` hosted in a feature doc the
call was accepted, reported `redefined Q<n>`, and had no effect -- the title
came from the T239 self-titling rule, which reads the body's FIRST LINE and
stamps `Untitled` when that line is a paragraph rather than a heading.

That is the silent-no-op shape: a flag reporting success while doing nothing.
Observed 2026-08-18 minting F336 Q1, where two `set` calls reported success
while the rendered title stayed `Q1 — Untitled`.

  A. --title on a paragraph-first body   → the title binds (not `Untitled`)
  B. the body survives                   → option sub-bullets intact
  C. no --title, paragraph-first body    → still `Untitled` (T239 unchanged)
  D. no --title, title-shaped first line → self-titles (T239 unchanged)

Drives `_query_verb` directly, which is the function the fix lives in.
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name that was seen serving code no longer on
# disk -- a green run vouching for a source it had not read.
import sys as _sys; _sys.dont_write_bytecode = True

import argparse
import importlib.machinery
import importlib.util
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
loader = importlib.machinery.SourceFileLoader("state_mod", str(HERE / "state"))
spec = importlib.util.spec_from_loader("state_mod", loader)
st = importlib.util.module_from_spec(spec)
sys.modules["state_mod"] = st
loader.exec_module(st)
be = st.be

# The post-write chain (audit-q over the vault, Q.md refresh, warden self-fire)
# needs a real anchor and is out of scope here; stub it.
st._post_conditions_and_print = lambda slug, path, summary: None
st._selffire = lambda path: None
be._selffire = lambda *a, **k: None

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")

# Deliberately longer than the 120-character ceiling the T239 self-titling rule
# applies, so this first line can never be mistaken for a title.
PARAGRAPH_BODY = (
    "Three instances do it, against a rule that says the flat form, and this "
    "opening line is deliberately far longer than the ceiling the self-titling "
    "rule applies, so it can never be read as a heading.\n"
    "  - **(A)** Flatten them.\n"
    "  - **(B)** Ratify the nesting.\n"
    "- **Recommendation:** None.\n"
    "  - **Damage:** waste — a wrong pick just re-runs one step.\n"
)

DOC = """---
description: "fixture"
---

# [[ZZT]] · F1 — A feature
One line of orientation.

## Summary

Body.

## Status

**Designing** — fixture.
"""


def args_for(body, title=None):
    return argparse.Namespace(
        inline=body, from_file=None, title=title, choice=None, reason=None,
        why_ask=None, why_user=None, why_user_action=None,
    )


def title_of(doc: Path, n):
    m = re.search(rf"^- \*\*Q{n} — (.+?)\*\*", doc.read_text(encoding="utf-8"),
                  re.M)
    return m.group(1) if m else None


TMP = Path(tempfile.mkdtemp(prefix="t244-"))
try:
    doc = TMP / "ZZT001 - A feature.md"
    doc.write_text(DOC, encoding="utf-8")

    # ---- A + B: --title binds, and the body survives ----------------------
    print("== A/B: --title binds on a doc-hosted Q, body intact ==")
    st._query_verb("ZZT", doc, 1, "define", args_for(PARAGRAPH_BODY))
    if title_of(doc, 1) != "Untitled":
        no(f"fixture precondition wrong: Q1 minted as {title_of(doc, 1)!r}, "
           f"expected the Untitled self-title")
    st._query_verb("ZZT", doc, 1, "set",
                   args_for(PARAGRAPH_BODY, title="Does a facet nest deeper?"))
    got = title_of(doc, 1)
    if got == "Does a facet nest deeper?":
        ok("--title bound to the doc-hosted Q")
    else:
        no(f"--title ignored; title is {got!r}")
    text = doc.read_text(encoding="utf-8")
    if "**(A)** Flatten them." in text and "**(B)** Ratify the nesting." in text:
        ok("option sub-bullets survived the retitle")
    else:
        no("body sub-bullets were lost by the retitle")

    # ---- C: T239 self-titling is unchanged when --title is absent ---------
    print("== C: no --title, paragraph-first body still self-titles Untitled ==")
    st._query_verb("ZZT", doc, 2, "define", args_for(PARAGRAPH_BODY))
    got = title_of(doc, 2)
    if got == "Untitled":
        ok("paragraph-first body still stamps Untitled without --title")
    else:
        no(f"T239 behavior changed: Q2 title is {got!r}")

    # ---- D: a title-shaped first line still self-titles -------------------
    print("== D: no --title, title-shaped first line still self-titles ==")
    st._query_verb("ZZT", doc, 3, "define", args_for(
        "Is the short first line still used as the title?\n\n"
        + PARAGRAPH_BODY))
    got = title_of(doc, 3)
    if got == "Is the short first line still used as the title?":
        ok("short first line still self-titles")
    else:
        no(f"T239 self-titling regressed: Q3 title is {got!r}")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\ntest-t244-doc-q-title: {PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)
