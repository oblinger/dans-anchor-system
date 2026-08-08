#!/usr/bin/env python3
"""test-f270-damage-field.py — F270: the Damage field on question mint.

Two layers, mirroring test-f257:
  1. `parse_damage` / `leaned_choice` (backlog-edit.py) — the pure parsing.
  2. `_q_define_core` (state) end-to-end on a temp doc — proves the wiring:
     waste/priority AUTO-RESOLVE (define → resolve in place, never surface);
     a surface category (irreversible/locking/taste/other) SURFACES, with the
     Damage line satisfying the F257 why-ask gate; a missing Damage line WARNS
     but surfaces (soft-required rollout); a bad category is REFUSED.

Self-contained: imports the modules in-process; touches only tmp files."""
import contextlib
import importlib.machinery
import importlib.util
import io
import sys
import tempfile
from pathlib import Path

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


import re as _re


def _lean_letter(rec, first="A"):
    """The option letter a Lean/Strong recommendation names, else the first
    listed option; None when the recommendation is `None` (never gated)."""
    if not _re.search(r"\b(Lean|Strong)\b", rec, _re.IGNORECASE):
        return None
    m = _re.search(r"\(([A-Za-z]\w*)\)", rec)
    return m.group(1) if m else first


def body(rec, damage, header="Should the daemon run in-process or as a service?",
         risk="file — the daemon rewrites `commands.txt` in place"):
    """A minimal ask-format Q body: header + two options + Recommendation +
    (optional) Damage line. Pass damage=None to omit the Damage line.

    T160 — a Lean/Strong recommendation must also state the risk OF ITS LEAN,
    so the fixture carries that line whenever the recommendation has a lean.
    What this test asserts (the F270 Damage route) is unchanged by it."""
    lines = [f"- **Q1 — {header}**",
             "  - **(A)** first option.",
             "  - **(B)** second option.",
             f"- **Recommendation:** {rec}"]
    letter = _lean_letter(rec)
    if letter and risk is not None:
        lines.append(f"- **Risk of ({letter}):** {risk}")
    if damage is not None:
        lines.append(f"- **Damage:** {damage}")
    return "\n".join(lines)


# ---- 1. parse_damage / leaned_choice ---------------------------------------
print("== 1. parse_damage / leaned_choice ==")

ok("parse waste") if be.parse_damage("- **Damage:** waste — redoes a run") == ("waste", "redoes a run") \
    else no("waste not parsed")
ok("parse locking (period sep)") if be.parse_damage("- **Damage:** locking. parsers commit")[0] == "locking" \
    else no("locking not parsed")
ok("missing → (None, '')") if be.parse_damage("- **Q1 — x** no damage") == (None, "") \
    else no("missing not None")
try:
    be.parse_damage("- **Damage:** frobnicate — nope")
    no("bad category should raise")
except be.BacklogEditError:
    ok("bad category raises")

ok("leaned from Recommendation (B)") if be.leaned_choice(body("Lean (B). x", "waste")) == "(B)" \
    else no("lean choice wrong")
ok("leaned falls back to first option") if be.leaned_choice(body("None. x", "waste")) == "(A)" \
    else no("first-option fallback wrong")
ok("open-ended → —") if be.leaned_choice("- **Q1 — name it?**\n- **Recommendation:** None. pick") == "—" \
    else no("open-ended fallback wrong")

# ---- 2. _q_define_core end-to-end ------------------------------------------
print("== 2. _q_define_core auto-resolve / surface / warn / refuse ==")

st._selffire = lambda *a, **k: None
st._post_conditions_and_print = lambda *a, **k: None

DOC = ("---\ndescription: t\n---\n\n# [[ZZR]] · F1 — Temp\nOrient.\n\n"
       "## Summary\n\nbody\n")


def fresh_doc():
    f = Path(tempfile.mkdtemp()) / "F1 — Temp.md"
    f.write_text(DOC, encoding="utf-8")
    return f


def define(f, b, why_ask=None):
    """Run _q_define_core capturing stdout+stderr; return (out, err)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        st._q_define_core("ZZR", f, 1, b, why_ask=why_ask)
    return out.getvalue(), err.getvalue()


# (a) waste → auto-resolves: lands in ## Resolved, no pending Q1, prints ⚑.
f = fresh_doc()
out, _ = define(f, body("Lean (B). cheaper", "waste — only a wasted run"))
txt = f.read_text()
good = ("## Resolved" in txt and "auto-resolved (waste)" in txt
        and "**Resolved:** (B)" in txt and "auto-resolved" in out
        and "- **Q1 —" not in txt.split("## Resolved")[0])
ok("waste Q auto-resolves to the lean (B) in ## Resolved, none pending") if good \
    else no(f"waste not auto-resolved:\nOUT={out!r}\nTXT={txt}")

# (b) priority → auto-resolves too.
f = fresh_doc()
out, _ = define(f, body("Strong (A). ordering", "priority — just sequence"))
txt = f.read_text()
ok("priority Q auto-resolves") if ("auto-resolved (priority)" in txt and "**Resolved:** (A)" in txt) \
    else no(f"priority not auto-resolved:\n{txt}")

# (c) locking + Lean, NO --why-ask → SURFACES (Damage satisfies the gate), pending.
f = fresh_doc()
out, err = define(f, body("Lean (B). sticky", "locking — parsers commit to the shape"))
txt = f.read_text()
good = ("- **Q1 —" in txt and "## Resolved" not in txt
        and "*why-ask: locking:" in txt)
ok("locking Q surfaces (Lean, no --why-ask) with Damage as the justification") if good \
    else no(f"locking not surfaced/annotated:\n{txt}")

# (d) missing Damage line → warns INSTRUCTIVELY on stderr, still surfaces (soft-required).
f = fresh_doc()
out, err = define(f, body("None. genuine uncertainty", None))
txt = f.read_text()
instructive = ("Re-run" in err and "waste" in err and "**Damage:**" in err
               and "surface" in err.lower())
ok("missing Damage → instructive warn (re-run + categories) + surfaces") \
    if (instructive and "- **Q1 —" in txt) \
    else no(f"missing-damage path wrong:\nERR={err!r}\nTXT={txt}")

# (e) bad category → refused, file untouched.
f = fresh_doc()
before = f.read_text()
try:
    define(f, body("None. x", "frobnicate — nope"))
    no("bad category should refuse")
except be.BacklogEditError:
    ok("bad category refused, file untouched") if f.read_text() == before \
        else no("refused but wrote file")

print("-" * 40)
print(f"F270 Damage-field test: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
