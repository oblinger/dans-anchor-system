#!/usr/bin/env python3
"""T109 — a Q must not carry its options inline on the header line.

Two gates cover the same rule from opposite sides and this test pins both:

  * the WRITE gate — `state._validate_ask_format_body` refuses a `Q<n> define`
    body without ≥2 own-line `- **(A)**` bullets, so the shape cannot enter
    through `state` at all;
  * the AUDIT gate — audit-q **C8** flags the shape on docs already on disk,
    which is the only path that reaches pre-gate corpus.

C8 is the half that was broken: its proximity regex allowed only 80 chars
between the two labels and its char class omitted `C`, so a Q whose options are
a sentence apart — the ordinary case — passed clean. The live regressions are
the two `HA Backlog.md` rows asserted at the end.

Run: python3 test-t109-inline-options.py
"""
import importlib.machinery
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

HOME = Path.home()
AUDIT_Q = HOME / ".claude" / "skills" / "audit" / "scripts" / "audit-q.py"
STATE = HOME / ".claude" / "skills" / "workflow" / "scripts" / "state"
HA_BACKLOG = HOME / "ob" / "kmr" / "prj" / "Hook Anchor" / "HA Track" / "HA Backlog.md"

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}{(' — ' + detail) if detail else ''}")


def _load(name, path):
    spec = importlib.util.spec_from_loader(
        name, importlib.machinery.SourceFileLoader(name, str(path)))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


aq = _load("aq_t109", AUDIT_Q)

# ---------------------------------------------------------------- detector

print("has_inline_alternatives — the C8 predicate")

# Real shape: options separated by a full sentence each. 153 and 255 chars
# apart in the live HA rows, both far past the retired 80-char window.
LONG = ("- **Q1 — remediation strategy?** — (A) land the safe additive fingerprint "
        "hardenings now, since they can only reduce false-hits on the soaking code, "
        "and hold the rest for design; (B) hold everything until the soak completes.")
check("options a sentence apart are flagged", aq.has_inline_alternatives(LONG))

check("(A) … (C) is flagged (the omitted-`C` regression)",
      aq.has_inline_alternatives("- **Q1 — pick?** (A) do it (C) skip it"))
check("lowercase prose alternatives are flagged",
      aq.has_inline_alternatives("- **Q1 — pick?** Options: (a) socket; (b) deep-link"))
check("case-folded: (a) and (B) count as two labels",
      aq.has_inline_alternatives("- **Q1 — pick?** (a) this or (B) that"))

check("a single label is not an inline option list",
      not aq.has_inline_alternatives("- **Q1 — should the (A) case extend?**"))
check("the SAME label twice is not two options",
      not aq.has_inline_alternatives("- **Q1 — pick?** (A) do it, or not (A)"))
check("a clean header carries no labels",
      not aq.has_inline_alternatives("- **Q1 — Which isolation mechanism?** Context here."))
check("labels past (D) are out of range",
      not aq.has_inline_alternatives("- **Q1 — pick?** (E) one (F) two"))

# ------------------------------------------------------------- write gate

print("\nwrite gate — state._validate_ask_format_body")
st = _load("state_t109", STATE)

MASHED = ("- **Q1 — remediation strategy?** — (A) land the hardenings now; "
          "(B) hold everything until the soak completes.\n"
          "  - **Damage:** taste — needs your eyes\n")
WELL = ("- **Q1 — remediation strategy?** Context here.\n"
        "  - **(A)** land the hardenings now\n"
        "  - **(B)** hold everything\n"
        "  - **Recommendation:** None\n"
        "  - **Damage:** taste — needs your eyes\n")


def refused(body):
    """True when the ask-format gate rejects `body`. BacklogEditError is caught
    as BaseException on purpose — the script's error path exits rather than
    propagating a plain Exception."""
    try:
        st._validate_ask_format_body(body)
        return False
    except BaseException:
        return True


check("mashed body refused at define time", refused(MASHED))
check("well-formed body accepted", not refused(WELL))

# ------------------------------------------------------------- audit gate

print("\naudit gate — C8 end to end on a doc")


def audit_codes(q_block):
    tmp = Path(tempfile.mkdtemp())
    doc = tmp / "F001 — t109 fixture.md"
    doc.write_text(
        "---\ndescription: fixture\n---\n\n# F001 — t109 fixture\nOrientation.\n\n"
        "## Open Questions\n\n" + q_block +
        "\n## Summary\n\nbody\n\n## Status\n\n**Questions**\n",
        encoding="utf-8")
    r = subprocess.run([sys.executable, str(AUDIT_Q), "--scope", "feature-doc",
                        "--feature-doc", str(doc), "--dry"],
                       capture_output=True, text=True, timeout=60)
    return [c for c in ("C8", "C9", "C10", "C19")
            if any(f"] {c} " in ln for ln in r.stdout.splitlines())]


# The exact hole: every option inline, but a well-placed own-line
# Recommendation, so C9/C10/C19 all pass and C8 is the only check left.
HOLE = ("- **Q1 — remediation strategy?** — (A) land the safe additive fingerprint "
        "hardenings now, since they can only reduce false-hits on the soaking code, "
        "and hold the rest for design; (B) hold everything until the soak "
        "completes, then remediate as one batch. ^F001-Q1\n"
        "- **Recommendation:** Lean (A) — additive fixes strictly harden the code.\n")
codes = audit_codes(HOLE)
check("all-inline options + clean Recommendation is caught by C8",
      "C8" in codes, f"codes={codes}")

CLEAN = ("- **Q1 — remediation strategy?** Context sentence. ^F001-Q1\n"
         "  - **(A)** land the hardenings now\n"
         "  - **(B)** hold everything\n"
         "- **Recommendation:** Lean (A) — additive fixes harden the code.\n")
codes = audit_codes(CLEAN)
check("well-formed Q raises no Q-format finding", codes == [], f"codes={codes}")

# ------------------------------------------------------- live regressions

print("\nlive corpus — the two rows Dan pointed at")
if not HA_BACKLOG.exists():
    print(f"  SKIP: {HA_BACKLOG} not present")
else:
    lines = HA_BACKLOG.read_text(encoding="utf-8").splitlines()
    hits = [(i, ln) for i, ln in enumerate(lines, 1)
            if aq.Q_HEADER_RE.match(ln)
            and aq.has_inline_alternatives(aq._strip_code_spans(ln))]
    check("HA Backlog inline-option Q headers are detected", len(hits) >= 2,
          f"found {len(hits)}")
    for i, ln in hits[:4]:
        print(f"      HA Backlog.md:{i} — {ln.strip()[:70]}…")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
