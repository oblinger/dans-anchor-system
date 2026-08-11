#!/usr/bin/env python3
"""test-t160-risk-of-lean.py — TINK T160: a question carrying a Lean must state
the risk OF THAT LEAN, and the statement is a ROUTE rather than a fourth prose
field.

Dan, 2026-08-08, reading F217 Q4 and not being able to see why it was a
question: *"if there's no downside to one of the choices, and that's the one you
lean towards, do it… if all agents when they have a lean must specify a
downside, then as they write it down they'll realize this is not enough of a
risk."*

Why a route and not a fourth sentence. Three gates already sit on
question-minting and all three ask about the QUESTION — F257's `--why-ask` (why
are you surfacing it), F270's Damage (how big is the blast radius if it is got
wrong), `/crank`'s Gate 3 (right phrasing, governs stopping only). F257 is free
text and **measured 9 of 10 Leans passing while the ladder said ask none**: a
free-text gate checks that a sentence EXISTS, not that it FITS. So the first
word after the option letter is a closed casualty class, and the class decides
the outcome — F270's shape, which is the gate that worked.

  A. the parse        — casualty classes, narrative, a typo'd class refuses
  B. the requirement  — a Lean/Strong with no risk line refuses; `None` passes
  C. THE SUBJECT      — the risk must be of the LEANED option, not another one
  D. the route        — `interpretation` auto-resolves; a vault casualty surfaces
  E. F217 Q4          — the pinned fixture: a real Q that passed BOTH old gates
  F. wiring           — `_run_question_gates` end-to-end, and C20's separator

Self-contained: imports the modules in-process; touches only a tmp file. Never
touches the real vault."""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
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


def ok(m):
    global PASS
    PASS += 1
    print(f"  PASS: {m}")


def no(m):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {m}")


FORK = "Should the daemon run in-process or as a separate service?"


def body(rec, risk=None, damage="other — a wrong pick is expensive to unwind",
         on_answer=True):
    """A minimal ask-format Q body, with the fields the gates ask for."""
    out = [f"- **Q1 — {FORK}**",
           "  - **(A)** run it in-process.",
           "  - **(B)** run it as a separate service.",
           f"- **Recommendation:** {rec}"]
    if risk is not None:
        out.append(f"  - **Risk of {risk}")
    if damage is not None:
        out.append(f"  - **Damage:** {damage}")
    if on_answer:
        out.append("  - **On answer:** (A) → in-process; (B) → a service.")
    return "\n".join(out)


# ---- A: the parse -----------------------------------------------------------
print("== A: parse_risk_of_lean — class, narrative, and a typo'd class ==")

opt, cas, why = be.parse_risk_of_lean(
    body("Lean (A). x", risk="(A):** file — `commands.txt` is rewritten in place "
                             "and has no backup"))
if (opt, cas) == ("A", "file"):
    ok("option letter and casualty class parse")
else:
    no(f"got option={opt!r} casualty={cas!r}")
if why.startswith("`commands.txt` is rewritten"):
    ok("the narrative is carried through, leading em-dash stripped")
else:
    no(f"narrative wrong: {why!r}")
if be.parse_risk_of_lean(body("Lean (A). x")) == (None, None, ""):
    ok("an absent risk line parses as absent, not as an error")
else:
    no("an absent risk line did not parse as absent")
try:
    be.parse_risk_of_lean(body("Lean (A). x", risk="(A):** annoyance — meh"))
    no("an unknown casualty class should refuse")
except be.BacklogEditError as ex:
    ok("an unknown class refuses and lists the closed set") \
        if "interpretation" in str(ex) and "annoyance" in str(ex) \
        else no(f"wrong message: {ex}")

# ---- B: the requirement -----------------------------------------------------
print("== B: a Lean/Strong must carry the line; a `None` recommendation need not ==")
for strength in ("Lean (A). x", "Strong (A). x"):
    try:
        be.risk_of_lean_gate(1, body(strength), be.recommendation_strength(body(strength)))
        no(f"{strength.split()[0]} without a risk line should refuse")
    except be.BacklogEditError as ex:
        ok(f"{strength.split()[0]} without a risk line refuses") \
            if "risk OF THAT LEAN" in str(ex) else no(f"wrong message: {ex}")
b_none = body("None. genuine uncertainty")
try:
    cas, _ = be.risk_of_lean_gate(1, b_none, be.recommendation_strength(b_none))
    ok("a `Recommendation: None` is never gated — the honest ask stays free") \
        if cas is None else no(f"None was gated, returned {cas!r}")
except be.BacklogEditError as ex:
    no(f"a None recommendation was refused: {ex}")

# A class with no sentence after it is the free-text failure in miniature.
try:
    b = body("Lean (A). x", risk="(A):** file")
    be.risk_of_lean_gate(1, b, "Lean")
    no("a bare class with no sentence should refuse")
except be.BacklogEditError as ex:
    ok("a class with no sentence refuses — the sentence IS the gate") \
        if "and then stops" in str(ex) else no(f"wrong message: {ex}")

# ---- C: the SUBJECT — the thing none of the three existing gates has --------
print("== C: the risk must be of the LEANED option, not of one already rejected ==")
try:
    b = body("Lean (A). x", risk="(B):** file — a service writes its own state file")
    be.risk_of_lean_gate(1, b, "Lean")
    no("a risk stated of the NON-leaned option should refuse")
except be.BacklogEditError as ex:
    if "leans (A)" in str(ex) and "stated of (B)" in str(ex):
        ok("risk-of-the-rejected-option refuses, naming both letters")
    else:
        no(f"wrong subject message: {ex}")
b = body("Lean (A). x", risk="(A):** time — costs Dan a 20-minute re-read of the migration")
cas, _ = be.risk_of_lean_gate(1, b, "Lean")
if cas == "time":
    ok("a risk of the leaned option passes")
else:
    no(f"the leaned-option risk was not accepted: {cas!r}")
# A Recommendation with no explicit letter falls back to the listed options.
b = body("Lean, weakly.", risk="(C):** file — some other file")
try:
    be.risk_of_lean_gate(1, b, "Lean")
    no("a letter naming no listed option should refuse")
except be.BacklogEditError as ex:
    ok("an option letter this question never listed refuses") \
        if "names no option" in str(ex) else no(f"wrong message: {ex}")

# ---- D: the route -----------------------------------------------------------
print("== D: the class is the route — interpretation closes, a vault casualty opens ==")
if be.RISK_AUTO_RESOLVE == ("interpretation",):
    ok("`interpretation` is the only auto-resolving class")
else:
    no(f"RISK_AUTO_RESOLVE is {be.RISK_AUTO_RESOLVE!r}")
for cls in ("file", "interface", "commitment", "time"):
    if cls not in be.RISK_AUTO_RESOLVE:
        ok(f"`{cls}` names something in the vault, so it surfaces")
    else:
        no(f"`{cls}` wrongly auto-resolves")

# ---- E: the pinned fixture — F217 Q4 ----------------------------------------
print("== E: F217 Q4 — a real Lean that passed BOTH existing gates, 2026-08-08 ==")
# Reconstructed from the transcript in SKA's F217 doc. This question was filed
# `Damage: waste`, F270 auto-resolved it, and the agent re-filed it under
# `other` and pushed it through anyway. F257's --why-ask passed it too. It is
# the worked example Dan was reading when he stated the rule.
F217Q4 = "\n".join([
    "- **Q4 — May the read-only survey run before the sit-down, or does your "
    '"nothing here runs unattended" cover it too?**',
    "  - **(A)** Yes — run the read-only census now. No page moves, no format "
    "decision, no edits outside the subtype catalogue.",
    "  - **(B)** No — the ruling covers the survey too, because choosing "
    "subtype categories already prejudges the target form.",
    "  - **(C)** Yes but narrow — census only the five reference pages the row "
    "already names.",
    "- **Recommendation:** Lean **(A)**. A census that moves nothing cannot "
    "prejudge the form — it reports what exists. · *why-ask: It re-reads a "
    "direct instruction of yours, and reinterpreting your words to widen my own "
    "runway is exactly what this row exists to prevent.*",
    "  - **Damage:** other — nothing here is expensive to redo; what is not "
    "undoable is having read a direct instruction of yours narrowly in order to "
    "widen my own runway.",
    "  - **On answer:** (A) → run Phase 1 to completion and STOP at the "
    "catalogue. (B) → F217 stays [User]. (C) → census the five named pages only.",
])

# It passes F257 (it carries a why-ask) and F270 routes it to the user (`other`).
try:
    be.question_mint_gate(4, F217Q4, None)
    ok("F217 Q4 still passes F257 — the gate that let it through")
except be.BacklogEditError as ex:
    no(f"the fixture no longer reproduces the F257 pass: {ex}")
if be.parse_damage(F217Q4)[0] == "other" \
        and "other" not in be.DAMAGE_AUTO_RESOLVE:
    ok("F270 still routes it to the user — the re-file that beat that gate")
else:
    no("the fixture no longer reproduces the F270 surface")

# T160 catches it: as written it states no risk of its lean at all.
try:
    be.risk_of_lean_gate(4, F217Q4, be.recommendation_strength(F217Q4))
    no("T160 should refuse F217 Q4 as written — this is the whole row")
except be.BacklogEditError as ex:
    ok("T160 refuses F217 Q4 as written, where both existing gates passed it") \
        if "risk OF THAT LEAN" in str(ex) else no(f"wrong message: {ex}")

# And when the agent writes the sentence honestly, it deflates: the transcript
# says the worry "was not a risk to the vault but a risk of reading your
# 2026-08-01 instruction more narrowly than you meant it."
honest = F217Q4 + ("\n  - **Risk of (A):** interpretation — the only thing at "
                   "stake is my reading your 2026-08-01 instruction more "
                   "narrowly than you meant it; the census moves no page.")
cas, why = be.risk_of_lean_gate(4, honest, be.recommendation_strength(honest))
if cas == "interpretation" and cas in be.RISK_AUTO_RESOLVE:
    ok("the honest sentence routes to `interpretation` → auto-resolve, not ask")
else:
    no(f"the honest F217 Q4 risk routed to {cas!r}")

# ---- F: wiring --------------------------------------------------------------
print("== F: _run_question_gates end-to-end, plus C20's separator ==")
b = body("Lean (A). x", risk="(A):** interpretation — only my own reading of "
                             "your instruction is at stake")
gated, auto, cat, why = st._run_question_gates(
    1, b, "interface-sticky daemon topology")
if auto and cat == "interpretation":
    ok("an interpretation-only risk auto-resolves through the shared gate")
else:
    no(f"auto={auto} cat={cat!r}")
banner = st._auto_resolve_banner("Q1", cat, "(A)")
if "T160" in banner and "waste/priority" not in banner:
    ok("the banner names the T160 route, not F270's")
else:
    no(f"banner mis-attributes the route: {banner}")

b2 = body("Lean (A). x", risk="(A):** file — `commands.txt` is rewritten with no backup")
gated2, auto2, cat2, _ = st._run_question_gates(1, b2, "architecture lock-in")
if not auto2 and cat2 == "other":
    ok("a vault casualty still surfaces, and the reason stays F270's Damage")
else:
    no(f"a `file` risk auto-resolved: auto={auto2} cat={cat2!r}")

# F270's own route still short-circuits before T160 — a waste Q has no lean left
# to defend and must not be asked for a risk line it does not need.
b3 = body("Lean (A). x", damage="waste — a wrong pick just re-runs one step")
_g, auto3, cat3, _w = st._run_question_gates(1, b3, None)
if auto3 and cat3 == "waste":
    ok("F270 waste still auto-resolves without demanding a T160 risk line")
else:
    no(f"the F270 short-circuit broke: auto={auto3} cat={cat3!r}")

# T137 — the C20 trailing-blank separator must recognise `Risk of (X):` as a
# Recommendation continuation, or a row-hosted Q ending in one gets no blank and
# C20 fires on every single one, unfixably.
if st._REC_CONTINUATION_RE.match("  - **Risk of (A):** file — a thing"):
    ok("`Risk of (X):` counts as a Recommendation continuation for C20")
else:
    no("C20's separator logic does not know about the Risk line (T137 shape)")
for other in ("  - **Damage:** waste — x", "  - **On answer:** (A) → y"):
    if st._REC_CONTINUATION_RE.match(other):
        ok(f"still a continuation: {other.strip()[:22]}")
    else:
        no(f"broke an existing continuation: {other!r}")

# The doc-scoped define path refuses too, and writes nothing.
st._selffire = lambda *a, **k: None
st._post_conditions_and_print = lambda *a, **k: None
DOC = "---\ndescription: t\n---\n\n# [[ZZR]] · F1 — Temp\nOrient.\n\n## Summary\n\nbody\n"
f = Path(tempfile.mkdtemp()) / "F1 — Temp.md"
f.write_text(DOC, encoding="utf-8")
try:
    st._q_define_core("ZZR", f, 1, body("Lean (A). x"), why_ask="architecture lock-in")
    no("`define` should refuse a Lean Q with no risk line")
except be.BacklogEditError:
    ok("`define` refuses, and left the doc untouched") if f.read_text() == DOC \
        else no("define refused but wrote the doc anyway")

# ---- G: money — a casualty OUTSIDE the vault --------------------------------
print("== G: `money` — a casualty outside the vault (CFO report, 2026-08-10) ==")
# Munger could not mint a real user decision about an options-collar floor:
# every class named vault damage, and the gate's own advice for an unnameable
# casualty is "then auto-resolve" — i.e. decide someone's money without asking.
# So `money` must both parse AND stay out of RISK_AUTO_RESOLVE.
_opt, _cas, _why = be.parse_risk_of_lean(
    body("Lean (A). x",
         risk="(A):** money — a collar filled at the wrong floor pays the "
              "spread on both legs and cannot be unwound at yesterday's mark"))
if (_opt, _cas) == ("A", "money"):
    ok("`money` parses as a casualty class")
else:
    no(f"got option={_opt!r} casualty={_cas!r}")
if _why.startswith("a collar filled at the wrong floor"):
    ok("the money narrative carries through")
else:
    no(f"narrative wrong: {_why!r}")
if "money" not in be.RISK_AUTO_RESOLVE:
    ok("`money` does NOT auto-resolve — it reaches the user")
else:
    no("`money` wrongly auto-resolves — the gate would spend it silently")
try:
    be.parse_risk_of_lean(body("Lean (A). x", risk="(A):** cash — nope"))
    no("a near-miss class (`cash`) should still refuse")
except be.BacklogEditError as ex:
    ok("a near-miss refuses, and `money` is offered in the message") \
        if "money" in str(ex) else no(f"money missing from the closed set: {ex}")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
