#!/usr/bin/env python3
"""T101 — head-H1 coverage restored to the doc class that specifies a head.

T093 taught `_head_h1` that a `# LOG` marker below an earlier `##` is not a head,
which removed 235 false findings and left the 220 affected docs silent. Nothing
reported a missing head, because the only rule wired to `chk_h1_present` was
`R-decisions` (`{anchor}/** Design/**/*.md` containing a `## Decisions` H2), and it
sees 0 of them. A `where:: always` head-H1 rule was the obvious instrument and the
wrong one — it would indict 124 loose notes using a deliberate convention to catch
the ~20 docs where a head is actually specified.

So the scope does the discriminating. `R-fct-features` is the class whose head form
is normative (R-fct-features-03: `# [[{slug}]] · F{n} — {Title}`), and two things
were wrong with it: its `where::` matched a folder named literally `Features` while
the convention is `{slug} Features/` — **17 of 684 feature docs vault-wide, 2.5%** —
and its H1 rule carried no `check::` at all, so even those 17 were never tested.

Measured after both fixes: **684 in scope, 26 findings — 17 displaced, 9 headless.**

    python3 test-t101-head-h1-scope.py
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
(ROOT / ".anchor").write_text("slug: DKT\n", encoding="utf-8")


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  (got {got!r}, want {want!r})"))


def write(text, name="d.md"):
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


print("The two failures are told apart")

# The real shape, from `F043 — Controllable Named Views.md`: a pre-F241 `## Resolved`
# block above the H1, so the correct title sits below an earlier heading.
f = write("---\ndescription: x\n---\n## Resolved Decisions\n\n- a decision\n\n"
          "# F043 — Controllable Named Views\n\nOrientation.\n")
check("a displaced H1 is reported AT ITS LINE, not as absent",
      ap.chk_h1_present(f, ROOT, ""),
      ("fail", "no head H1 (an H1 sits at line 8, below an earlier heading)"))

# From `F040 — Interface Spec.md`: frontmatter straight into `## Summary`.
f = write("---\ndescription: x\n---\n## Summary\n\nbody\n")
check("a doc with no `# ` line at all still reports plain `no H1`",
      ap.chk_h1_present(f, ROOT, ""), ("fail", "no H1"))

# Why the message stops at the observation instead of saying "move it": in a feature
# doc a displaced H1 is a misplaced title, but in the 124 loose notes T101 kept OUT
# of scope the identical shape is a deliberate `# LOG` body marker that must stay.
# One checker cannot tell those apart — the `where::` glob is what decides.
f = write("## Contact\n\nphone\n\n# LOG\n\n- entry\n")
check("...and a loose note's body marker gets the same neutral wording",
      ap.chk_h1_present(f, ROOT, ""),
      ("fail", "no head H1 (an H1 sits at line 5, below an earlier heading)"))

print("\nPositive controls — masking must not become suppression")

f = write("---\ndescription: x\n---\n# [[DKT]] · F043 — Named Views\n\nOrientation.\n")
check("a well-formed feature doc passes",
      ap.chk_h1_present(f, ROOT, ""), ("pass", ""))
f = write("## Open Questions\n\n- **Q1 — x** — y\n\n# [[DKT]] · F1 — T\n\nOrientation.\n")
check("the parked Open-Questions block is still legal above the head (F241)",
      ap.chk_h1_present(f, ROOT, ""), ("pass", ""))
# The displaced-H1 scan reuses `_strip_fenced`, so a fenced example cannot be
# mistaken for the real title and reported at a line the author cannot act on.
f = write("## Summary\n\n```markdown\n# F1 — Sample\n```\n\nbody\n")
check("an H1 inside a fence is not reported as a displaced H1",
      ap.chk_h1_present(f, ROOT, ""), ("fail", "no H1"))

print("\nThe rule is wired and the scope reaches the corpus")

RS = _S.parent.parent.parent.parent / "rulesets" / "R-fct-features.md"
block, _lvl = ap.extract_ruleset_block(RS.read_text(encoding="utf-8"))
rs = ap.parse_ruleset_block(block, RS)
by_id = {r["id"]: r for r in rs["rules"]}
check("R-fct-features-03 carries a check:: action",
      by_id["R-fct-features-03"].get("check"), "h1_present")
check("...and is still declared (checked)",
      by_id["R-fct-features-03"].get("tier"), "checked")

glob = rs["where"].split("file:", 1)[1].strip()
for rel in ("DKT Features/F001 — A.md",            # the convention
            "DKT Track/DKT Features/F002 — B.md",  # nested under Track
            "MUX Design/DMUX Subsystem/DMUX Features/F003 — C.md",  # subsystem ns
            "Features/F004 — D.md",                # the bare folder, still matched
            "F005 — E.md",     # the feature folder IS this anchor (18 in the vault)
            "Fun.md",          # a bare `F*.md` term would swallow this — 135 did
            "DKT Features.md",                     # the index page
            "DKT Design/DKT PRD.md"):              # NOT a feature doc
    write("# x\n", rel)
_, files = ap.enumerate_scope(ROOT, "anchor", ap.sub_anchor_roots(ROOT))
got = sorted(p.relative_to(ROOT).as_posix()
             for p in ap.match_targets("file", glob, files, ROOT))
check("the glob reaches every feature-doc spelling, and nothing else",
      got, sorted(["DKT Features.md",
                   "DKT Features/F001 — A.md",
                   "DKT Track/DKT Features/F002 — B.md",
                   "MUX Design/DMUX Subsystem/DMUX Features/F003 — C.md",
                   "Features/F004 — D.md",
                   "F005 — E.md"]))
# The bug this replaced: `**/Features/F*.md` demands a segment spelled exactly
# `Features`, while the documented location is `{slug} Features/`. Measured over the
# live vault with the plan builder's own scoping, the shipped selector matched
# **zero files** — all four rules were inert, and a selector that matches nothing
# emits no verdicts, so nothing ever reported it.
old = sorted(p.relative_to(ROOT).as_posix() for p in ap.match_targets(
    "file", "**/Features/F*.md, **/{slug} Features.md", files, ROOT))
check("the OLD glob reached only the bare-`Features/` folder and the index",
      old, ["DKT Features.md", "Features/F004 — D.md"])
# Anchor-relative matching is the whole reason the third term exists: re-rooting on
# the feature folder leaves `F001 — A.md` with no directory component at all.
sub = ROOT / "DKT Features"
(sub / ".anchor").write_text("", encoding="utf-8")
_, subfiles = ap.enumerate_scope(sub, "anchor", ap.sub_anchor_roots(sub))
got_sub = sorted(p.relative_to(sub).as_posix()
                 for p in ap.match_targets("file", glob, subfiles, sub))
check("a feature folder that is ITSELF an anchor still matches its own docs",
      got_sub, ["F001 — A.md"])

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
