#!/usr/bin/env python3
"""test-t041-block-id-definition.py — `_scope_to_block_id_region` anchors on
the line that DEFINES a block-id, not on one that merely references it.

Why this exists. The scan used `if marker in line` and took the first hit, so
a `[[Doc#^T041|T041]]` wiki-link sitting in an earlier row's prose won the
race against the real `… ^T041` definition at the end of the target row. The
region then covered the *linking* row instead, and every check scoped through
this helper (C2, C46, backlog-edit's Q-marker check) read the wrong row.

Found on MUX 2026-08-02: F250's body links `[[MUX Backlog#^T041|T041]]`, so
C46 scoped T041 to F250's one-line `Next:`, found no `- **Q1 —` sub-bullet
there, and reported that T041 "carries no inline Q sub-bullets" while the row
plainly carried one. Note the shape of the false report — it accused the
correctly-authored row, and the actual cause was in an unrelated row 17 lines
earlier. See MUX T041.

Block-ids are end-of-line in Obsidian, so anchoring the match there makes a
reference inert without needing to parse `[[…]]`.

Self-contained: loads audit-q.py in-process and asserts on returned regions.
"""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).parent

loader = importlib.machinery.SourceFileLoader("audit_q_mod", str(HERE / "audit-q.py"))
spec = importlib.util.spec_from_loader("audit_q_mod", loader)
assert spec is not None
aq = importlib.util.module_from_spec(spec)
sys.modules["audit_q_mod"] = aq
loader.exec_module(aq)

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}")
        if detail:
            print("\n".join("        " + l for l in detail.splitlines()[:10]))


# The exact shape that broke: an earlier row links #^T041; the real row
# defines ^T041 and carries the question.
BACKLOG = """## Now

- **F250 — architecture** [Ready] — body. ^F250
  - **Next:** the code question moved to [[MUX Backlog#^T041|T041]] because F250 moves no code.

- **T041 — the CLI reports success for work it never did** [Questions] — body. ^T041
  - **Next:** Answer Q1.
  - **Q1 — delete the daemon, or wire it?** ^T041-Q1
    - **(A)** Delete.
    - **(B)** Wire.
  - **Recommendation:** None.

- **T042 — something else** [Ready] — body. ^T042
"""


def main():
    region = aq._scope_to_block_id_region(BACKLOG, "T041")
    lines = region.splitlines()

    check("region starts at the DEFINING line, not the linking one",
          bool(lines) and lines[0].startswith("- **T041 "),
          f"got first line: {lines[0] if lines else '<empty>'}")

    check("region carries the row's Q sub-bullet",
          any(l.lstrip().startswith("- **Q1 ") for l in lines), region)

    check("region stops before the next top-level row",
          not any("T042" in l for l in lines), region)

    # A reference-only block-id must still resolve to nothing, rather than
    # silently falling back to the referencing line.
    check("a block-id that is only ever referenced yields an empty region",
          aq._scope_to_block_id_region(
              "- **F1 — x** — see [[D#^T999|T999]]. ^F1\n", "T999") == "")

    # Prefix safety: ^T04 must not match a ^T041 definition.
    check("a shorter block-id does not match a longer definition",
          aq._scope_to_block_id_region(BACKLOG, "T04") == "")

    # The plain case must keep working.
    r250 = aq._scope_to_block_id_region(BACKLOG, "F250").splitlines()
    check("an ordinary row still resolves to its own region",
          bool(r250) and r250[0].startswith("- **F250 "),
          f"got: {r250[0] if r250 else '<empty>'}")

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
