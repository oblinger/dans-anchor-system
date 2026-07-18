#!/usr/bin/env python3
"""test-f257-question-gate.py — F257: the question-mint gate (the F240 sibling
for Open Questions). A Lean/Strong recommendation-bearing Q cannot be minted
without a --why-ask justification; an agent-territory-phrased Q (ordering /
batching / rollback / cosmetic rename) is refused regardless; a None Q and an
already-`*why-ask:*`-annotated re-touch pass freely.

Two layers:
  1. `question_mint_gate` + its parsing primitives (backlog-edit.py) — the pure
     logic, the single source both the `state` write and the audit C50 mirror
     share.
  2. `_q_define_core` (state) end-to-end on a temp doc — proves the wiring
     (define refuses / annotates), with the post-write side effects stubbed so
     the real vault / audit-q is never touched.

Self-contained: imports the modules in-process; touches only a tmp file."""
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
be = st.be  # reuse state's backlog-edit module — one class identity, so
            # `except be.BacklogEditError` matches errors raised inside state.

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")


def body(header, rec):
    """A minimal ask-format Q body: header line + two options + Recommendation."""
    return (f"- **Q1 — {header}**\n"
            f"  - **(A)** first option.\n"
            f"  - **(B)** second option.\n"
            f"- **Recommendation:** {rec}")


REAL_FORK = "Should the daemon run in-process or as a separate service?"
ORDERING = "Which order should I apply the three migrations?"

# ---- 1. parsing primitives --------------------------------------------------
print("== 1. recommendation_strength / agent-territory / annotation ==")

ok("strength Lean") if be.recommendation_strength(body(REAL_FORK, "Lean (A). x")) == "Lean" \
    else no(f"got {be.recommendation_strength(body(REAL_FORK, 'Lean (A). x'))!r}")
ok("strength Strong") if be.recommendation_strength(body(REAL_FORK, "Strong (B). y")) == "Strong" \
    else no("Strong not parsed")
ok("strength None") if be.recommendation_strength(body(REAL_FORK, "None. pure preference")) == "None" \
    else no("None not parsed")

ok("agent-territory: 'which order' flagged") if be.is_agent_territory_question(body(ORDERING, "Lean (A). x")) \
    else no("ordering not flagged")
ok("real fork NOT flagged") if not be.is_agent_territory_question(body(REAL_FORK, "Lean (A). x")) \
    else no("real fork false-flagged")
# A NEW interface-sticky name stays askable (F068) — not agent-territory.
ok("naming a new module NOT flagged") if not be.is_agent_territory_question(
    body("How should we name the new worker module?", "None. preference")) \
    else no("new-module naming false-flagged")

# ---- 2. question_mint_gate — the two-tier refusals --------------------------
print("== 2. question_mint_gate refusals + passes ==")

# (a) None → passes freely, body unchanged.
b_none = body(REAL_FORK, "None. genuine uncertainty")
try:
    out = be.question_mint_gate(1, b_none, None)
    ok("None Q passes freely") if out == b_none else no("None Q body mutated")
except be.BacklogEditError as ex:
    no(f"None Q wrongly refused: {ex}")

# (b) Lean, no --why-ask → refused.
try:
    be.question_mint_gate(1, body(REAL_FORK, "Lean (A). x"), None)
    no("Lean without --why-ask should refuse")
except be.BacklogEditError as ex:
    ok("Lean without --why-ask refused") if "why-ask" in str(ex) else no(f"wrong msg: {ex}")

# (b') Strong, no --why-ask → refused.
try:
    be.question_mint_gate(1, body(REAL_FORK, "Strong (A). x"), None)
    no("Strong without --why-ask should refuse")
except be.BacklogEditError:
    ok("Strong without --why-ask refused")

# (c) Lean + --why-ask → passes, annotation lands on the Recommendation line.
try:
    out = be.question_mint_gate(1, body(REAL_FORK, "Lean (A). x"),
                                "interface-sticky daemon topology, hard to undo")
    good = ("*why-ask: interface-sticky" in out
            and out.count("*why-ask:") == 1
            and "**Recommendation:** Lean (A). x · *why-ask:" in out)
    ok("Lean + --why-ask passes and annotates the Recommendation line") if good \
        else no(f"annotation misplaced:\n{out}")
except be.BacklogEditError as ex:
    no(f"Lean + --why-ask wrongly refused: {ex}")

# (d) ordering-phrased Q → refused EVEN with --why-ask (Tier-1, no override).
try:
    be.question_mint_gate(1, body(ORDERING, "Lean (A). x"), "I really want to ask")
    no("agent-territory Q should refuse even with --why-ask")
except be.BacklogEditError as ex:
    ok("agent-territory refused despite --why-ask") if "agent-territory" in str(ex) \
        else no(f"wrong msg: {ex}")

# (e) grandfathered re-touch — already `*why-ask:*`-annotated, no --why-ask → passes.
annotated = body(REAL_FORK, "Lean (A). x · *why-ask: prior justification*")
try:
    out = be.question_mint_gate(1, annotated, None)
    ok("annotated Q grandfathered on re-touch") if out == annotated \
        else no("annotated re-touch mutated")
except be.BacklogEditError as ex:
    no(f"annotated re-touch wrongly refused: {ex}")

# ---- 3. _q_define_core end-to-end (wiring) ----------------------------------
print("== 3. _q_define_core define refuses / annotates on a temp doc ==")

# Stub the post-write side effects so no vault / audit-q is touched.
st._selffire = lambda *a, **k: None
st._post_conditions_and_print = lambda *a, **k: None

DOC = ("---\ndescription: t\n---\n\n# [[ZZR]] · F1 — Temp\nOrient.\n\n"
       "## Summary\n\nbody\n")


def fresh_doc():
    f = Path(tempfile.mkdtemp()) / "F1 — Temp.md"
    f.write_text(DOC, encoding="utf-8")
    return f


# define a Lean Q with no --why-ask → refused, file unchanged.
f = fresh_doc()
before = f.read_text()
try:
    st._q_define_core("ZZR", f, 1, body(REAL_FORK, "Lean (A). x"), why_ask=None)
    no("define(Lean, no --why-ask) should refuse")
except be.BacklogEditError:
    ok("define refuses a Lean Q without --why-ask") if f.read_text() == before \
        else no("define refused but wrote the file anyway")

# define the same Lean Q with --why-ask → written, annotation present.
f = fresh_doc()
try:
    st._q_define_core("ZZR", f, 1, body(REAL_FORK, "Lean (A). x"),
                      why_ask="architecture lock-in the user must ratify")
    txt = f.read_text()
    ok("define writes a Lean Q + renders the why-ask annotation") \
        if ("*why-ask: architecture lock-in" in txt and "**Q1 —" in txt) \
        else no(f"define wrote but annotation missing:\n{txt}")
except be.BacklogEditError as ex:
    no(f"define(Lean, --why-ask) wrongly refused: {ex}")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
