#!/usr/bin/env python3
"""T093 — `_head_h1` distinguishes the document's HEAD from the first `# ` in it.

`_first_h1` answered "the first H1 anywhere". All twelve callers asked it while
meaning "the H1 that heads this document". The two diverge on 220 vault docs that
open a body section with a `# LOG` / `# BRIEF` / `# TODO` marker below an earlier
`##` — a deliberate user convention — and every caller then blamed a real line
number for a defect that was not there.

    python3 test-t093-head-h1.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_S = (Path(__file__).parent / "audit-plan.py").resolve()
_spec = importlib.util.spec_from_file_location("ap", _S)
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

results = []
_td = tempfile.TemporaryDirectory()
ROOT = Path(_td.name)


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  (got {got!r}, want {want!r})"))


def write(text, name="d.md"):
    p = ROOT / name
    p.write_text(text, encoding="utf-8")
    return p


print("The predicate")

check("a plain head H1 is found, at its whole-file index",
      ap._head_h1("# Title\nOrientation.\n"), (0, "Title"))
check("a breadcrumb above the H1 does not end the head",
      ap._head_h1(":>> [[a]] → [[b]]\n# Title\nOrientation.\n"), (1, "Title"))
check("frontmatter is skipped and the index stays whole-file",
      ap._head_h1("---\ndescription: x\n---\n# Title\nOrientation.\n")[0], 3)

# The case worth the rename. `AT/@Drew Ackerman.md` and `Topic/T.md` are real.
check("a `# LOG` marker under an earlier `##` is NOT a head",
      ap._head_h1("## Contact\n\nphone\n\n# LOG\n\nentries\n"), (None, None))
check("...and the same file's first `# ` is still at the line it always was",
      ap._strip_fenced("## Contact\n\nphone\n\n# LOG\n").splitlines()[4], "# LOG")
check("a bare `##` divider with no title still ends the head",
      ap._head_h1("##\n\n# Later\n"), (None, None))
check("an H3 before any H1 ends the head too — level is irrelevant",
      ap._head_h1("### Note\n\n# Later\n"), (None, None))

# The one sanctioned pre-head element (F241 / /query parented mode). The authority
# for this list is `chk_h1_after_frontmatter`, which rejects everything else.
check("a parked `## Open Questions` block does NOT end the head",
      ap._head_h1("## Open Questions\n\n- **Q1 — x** — y\n\n# Title\nOrientation.\n"),
      (4, "Title"))
check("...including an H3 nested inside that parked block",
      ap._head_h1("## Open Questions\n\n### Resolved\n\n- **Q0** — z\n\n"
                  "# Title\nOrientation.\n"), (6, "Title"))
check("...but a DIFFERENT H2 after the parked block does end it",
      ap._head_h1("## Open Questions\n\n## Summary\n\n# Title\n"), (None, None))

check("a fenced `# Sample` is not the head (inherited from _strip_fenced)",
      ap._head_h1("```markdown\n# Sample\n```\n\n# Real\nOrientation.\n"),
      (4, "Real"))

print("\nThe callers that were being misled")

# R-progressive-03, `where:: always` — 177 of the 220 failed here, each asking for
# an orientation line under a body-section divider.
f = write("## Contact\n\nphone: 555\n\n# LOG\n\n- an entry\n")
check("orientation-line rule: a headless doc is out of scope, not failed",
      ap.chk_doc_head_orientation_line(f, ROOT, "")[0], "pass")
f = write("# Title\n## Straight into a section — no orientation line\n\nbody\n")
check("...but a REAL head with no orientation line still fails",
      ap.chk_doc_head_orientation_line(f, ROOT, "")[0], "fail")

# R-anchor-page — the slug check blamed `# LOG` for not matching the anchor slug.
f = write("## Contact\n\nphone\n\n# LOG\n\n- entry\n")
check("slug rule: reports no-H1 rather than blaming the body marker",
      ap.chk_h1_matches_slug(f, ROOT, ""), ("fail", "no H1"))

print("\nWhat this does NOT fix — closed by T101, kept as the record")

# This was the deliberate gap: `chk_h1_present` was wired only to R-decisions
# (`{anchor}/** Design/**/*.md` containing a `## Decisions` H2), so it saw 0 of the
# 220. The predicate stopped these docs being blamed at a body marker; it did not
# make them visible as headless, because no rule in scope asserted a head H1 exists.
# T101 closed the half that mattered by SCOPE rather than by widening the predicate:
# `R-fct-features` now carries `check:: h1_present` and a `where::` that actually
# reaches `{slug} Features/`, which is 684 docs and 26 findings. The 124 loose notes
# below stay deliberately out of scope — see `test-t101-head-h1-scope.py`.
f = write("## Contact\n\nphone\n\n# LOG\n\n- entry\n")
check("chk_h1_present does fail a headless doc when it runs at all",
      ap.chk_h1_present(f, ROOT, "")[0], "fail")
check("...naming where the body marker sits, so nobody adds a second H1",
      ap.chk_h1_present(f, ROOT, "")[1],
      "no head H1 (an H1 sits at line 5, below an earlier heading)")

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
