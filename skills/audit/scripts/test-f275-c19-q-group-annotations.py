#!/usr/bin/env python3
"""F270/F275 — C19 must accept the two Q-group lines `state define` requires.

`state define <anchor> <doc> Q<n>` REFUSES to mint a question that lacks
`- **On answer:**` (F275 M3) or carries a `- **Damage:**` outside the
`{waste, priority, irreversible, locking, taste, other}` vocabulary (F270).
So every correctly-minted standalone Q arrives carrying both lines.

`check_c19_option_bullets` reads every non-option sub-bullet between the Q
header and its Recommendation as a malformed option, exempting only an
allowlist of annotation prefixes — and that allowlist was never told about
the two new pieces. The writer gate and the reader gate therefore enforced
contradictory shapes: the only way to mint a clean Q was to violate `state`,
and an agent trusting audit-q would "fix" the finding by deleting the
`On answer:` line, after which `state` refuses the next edit to that row.

C20 in the same file already knew about both (`^\\s*-\\s+\\*\\*(Damage|On
answer…`, calling them *"piece 6"* and *"piece 7 on the same footing"*), which
is what makes this a one-place omission rather than a design disagreement.
Found and fixed by Lumen 2026-08-12 on LUMEN Q001 — the first standalone Q
minted after F275 made `On answer:` mandatory, so it fires on every Q from
here forward rather than being legacy debt.

The exemption must stay NARROW: C19's whole job is catching a sub-bullet that
looks like an alternative but carries no `(X)` label, so the assertions below
pin an unlabeled bullet still failing in both branches.

Run: python3 test-f275-c19-q-group-annotations.py
"""
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

AUDIT_Q = Path(__file__).resolve().parent / "audit-q.py"

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}{(' — ' + detail) if detail else ''}")


spec = importlib.util.spec_from_loader(
    "aq_f275", importlib.machinery.SourceFileLoader("aq_f275", str(AUDIT_Q)))
assert spec is not None and spec.loader is not None
aq = importlib.util.module_from_spec(spec)
sys.modules["aq_f275"] = aq
spec.loader.exec_module(aq)

TMP = Path(tempfile.mkdtemp())


def lines_of(findings):
    return sorted(f.surface_line for f in findings)


# --------------------------------------------------------------------------
# 1. The sub-bullet branch — a row-hosted Q on a backlog. The branch only
#    inspects sub-bullets at exactly `q_indent + 2`, so the Q header sits at
#    indent 2 under its row and its pieces at indent 4 — the real nesting.
# --------------------------------------------------------------------------
BACKLOG = """# ZZF Backlog

## Now

- **T001 — a row hosting its question inline** [Questions] — body prose. ^T001
  - **Q1 — which way?** Context sentence. ^T001-Q1
    - **(A)** the first way
    - **(B)** the second way
    - **On answer:** the losing branch is deleted, not left behind a flag.
    - **Damage:** locking
    - **Recommendation:** None

- **T002 — a row whose Q has a genuinely unlabeled alternative** [Questions] — body. ^T002
  - **Q1 — which other way?** Context sentence. ^T002-Q1
    - **(A)** the first way
    - do the other thing instead
    - **On answer:** something changes.
    - **Damage:** waste
    - **Recommendation:** None
"""

bl = TMP / "ZZF Backlog.md"
bl.write_text(BACKLOG, encoding="utf-8")
entries = aq.extract_q_entries(bl, "ZZF")
c19 = [f for f in aq.check_c19_option_bullets(entries) if f.surface_file == bl]

print("1. sub-bullet branch (backlog row)")
check("two pending Qs extracted", len(entries) == 2, f"got {len(entries)}")
check("`On answer:` raises no C19", 9 not in lines_of(c19), f"got {lines_of(c19)}")
check("`Damage:` raises no C19", 10 not in lines_of(c19), f"got {lines_of(c19)}")
check("a truly unlabeled sub-bullet is STILL flagged", 16 in lines_of(c19),
      f"got {lines_of(c19)}")
check("exactly one finding — the allowlist did not widen", len(c19) == 1,
      f"got {lines_of(c19)}")


# --------------------------------------------------------------------------
# 2. The H3 branch — options live at indent 0 under an H3-form Q, and carries
#    its own copy of the allowlist, so it needs its own assertion.
# --------------------------------------------------------------------------
H3_DOC = """---
description: fixture
---

# ZZF001 — fixture
Orientation.

## Open Questions
<!-- state:q 00 -->

### Q1 — which way?
Context sentence. ^F001-Q1

- **(A)** the first way
- **(B)** the second way
- **On answer:** the design section is written against the winner.
- **Damage:** taste
- **Recommendation:** None

### Q2 — which other way?
Context sentence. ^F001-Q2

- **(A)** the first way
- just pick something
- **On answer:** something changes.
- **Damage:** other
- **Recommendation:** None

## Summary

body
"""

fd = TMP / "ZZF001 - fixture.md"
fd.write_text(H3_DOC, encoding="utf-8")
fd_entries = aq.extract_q_entries(fd, "F001")
fd_c19 = [f for f in aq.check_c19_option_bullets(fd_entries) if f.surface_file == fd]

print("\n2. H3 branch (feature doc)")
check("two pending Qs extracted", len(fd_entries) == 2, f"got {len(fd_entries)}")
check("`On answer:` raises no C19", 16 not in lines_of(fd_c19), f"got {lines_of(fd_c19)}")
check("`Damage:` raises no C19", 17 not in lines_of(fd_c19), f"got {lines_of(fd_c19)}")
check("a truly unlabeled bullet is STILL flagged", 24 in lines_of(fd_c19),
      f"got {lines_of(fd_c19)}")
check("exactly one finding — the allowlist did not widen", len(fd_c19) == 1,
      f"got {lines_of(fd_c19)}")


# --------------------------------------------------------------------------
# 3. C20 — the neighbour that already knew. It must stay quiet on both, or the
#    two checkers have simply swapped which one is wrong.
# --------------------------------------------------------------------------
print("\n3. C20 stays quiet on the same fixtures")
c20_bl = [f for f in aq.check_c20_blank_after_recommendation(entries)
          if f.surface_file == bl]
c20_fd = [f for f in aq.check_c20_blank_after_recommendation(fd_entries)
          if f.surface_file == fd]
check("no C20 on the backlog fixture", c20_bl == [], f"got {lines_of(c20_bl)}")
check("no C20 on the feature-doc fixture", c20_fd == [], f"got {lines_of(c20_fd)}")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
