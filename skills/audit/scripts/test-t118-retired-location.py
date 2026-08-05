#!/usr/bin/env python3
"""T118 — `{slug} Docs/` is retired; the checker that keeps the corpus from re-splitting.

Dan ruled 2026-08-05 that `{slug} Docs/` is withdrawn. The rewrite landed first (16
live location claims across 11 facets); this is the half that keeps it landed.

The mapping is why a checker is worth the bytes. It was **not a rename** — the retired
tree's three subfolders went to three different places: `Docs/{slug} Plan/` and
`Docs/{slug} Design/` both collapse into `{slug} Design/`, `Docs/{slug} Dev/` becomes
`{slug} Dev Docs/`, and Outputs moves under `{slug} Track/`. So a corpus that
half-remembers the old tree does not merely lag, it files documents in three different
wrong places at once, which is worse than the inconsistency it replaced.

The load-bearing design decision is that PROVENANCE SURVIVES. Four notes in the corpus
tell a reader who finds a legacy tree that the path is superseded, and those notes are
the reason the retirement is legible at all. A checker that flagged the token outright
would delete its own documentation. So the unit of judgement is the containing
paragraph, and a history word inside it is the pass.

    python3 test-t118-retired-location.py
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

REPO = _S.parent.parent.parent.parent
FACETS = REPO / "facets"

results = []
_td = tempfile.TemporaryDirectory()
ROOT = Path(_td.name)


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def verdict(body, name="DAS Probe.md"):
    """Run the checker over a synthetic facet spec; return just pass/fail."""
    p = ROOT / name
    p.write_text(body, encoding="utf-8")
    return ap.chk_no_retired_location(p, ROOT, [])[0]


print("A live location claim fails — this is the T118 falsification test")

# The exact shape the rewrite removed: a Location line stating the retired tree as
# though a reader should file there today.
check("a bare Location line naming the retired tree",
      verdict("# DAS Probe\n\n## Location\n\n`{slug} Docs/{slug} Plan/{slug} PRD.md`\n"),
      "fail")
check("...and prose stating it as current",
      verdict("# DAS Probe\n\nThe doc lives at `{slug} Docs/{slug} Dev/` in every anchor.\n"),
      "fail")
# Trailing-slash-optional: `{slug} Docs`, `{slug} Docs/`, and a deeper path all name
# the same retired tree, so all three must be caught.
check("no trailing slash is the same claim",
      verdict("# DAS Probe\n\nFiled under `{slug} Docs` at the anchor root.\n"),
      "fail")

print("\nProvenance passes — the four corpus notes are the reason this rule is scoped so")

check("`previously` clears it",
      verdict("# DAS Probe\n\nPreviously lived at `{slug} Docs/{slug} Plan/`; now `{slug} Design/`.\n"),
      "pass")
check("so does `superseded`",
      verdict("# DAS Probe\n\nThe legacy path `{slug} Docs/{slug} Plan/` is superseded.\n"),
      "pass")
check("and `deprecated`",
      verdict("# DAS Probe\n\nAnchors under `{slug} Docs/` are deprecated but still resolve.\n"),
      "pass")

print("\nParagraph, not line — a provenance lead-in covers the paths it introduces")

# Why the unit is the paragraph: history is naturally written once, as a lead-in to
# the paths it describes. A line-scoped check would pass the sentence and fail the
# bullets under it, pushing authors to repeat "previously" on every line.
check("lead-in sentence covers a following bulleted path",
      verdict("# DAS Probe\n\nThese paths were superseded by F142:\n"
              "- `{slug} Docs/{slug} Plan/`\n"
              "- `{slug} Docs/{slug} Dev/`\n"),
      "pass")
# ...and the containment must be real: a history word in a DIFFERENT paragraph does
# not launder a live claim in this one, or the rule would be trivially defeated by
# mentioning the retirement anywhere in the file.
check("a history word in another paragraph does NOT launder it",
      verdict("# DAS Probe\n\nThe `{slug} Docs/` tree was retired in 2026.\n\n"
              "## Location\n\n`{slug} Docs/{slug} Dev/{slug} Files.md`\n"),
      "fail")

print("\nAgainst the live corpus: zero findings, and the four notes are why")

specs = sorted(FACETS.rglob("*.md"))
findings = [f for f in specs
            if ap.chk_no_retired_location(f, FACETS, [])[0] != "pass"]
check("every facet spec in the repo passes as it now stands",
      [f.name for f in findings], [])
check("...over a corpus large enough for that to mean something",
      len(specs) > 50, True)

# The four surviving provenance notes, named. If one is ever rewritten into a live
# claim, the rule above catches it — but if one is DELETED, this check is what
# notices, and a reader who finds a legacy tree loses the sentence that explains it.
KEEPERS = ["DAS PRD.md", "DAS Features.md", "DAS Roadmap.md", "DAS Discussion.md"]
still_documented = [n for n in KEEPERS
                    if (FACETS / n).is_file()
                    and "{slug} Docs" in (FACETS / n).read_text(encoding="utf-8")]
check("the four deliberate provenance notes are still there",
      still_documented, KEEPERS)

print("\nThe rule is wired — an unregistered checker is silently promoted to agent judgment")

# F289's failure mode: a `check::` naming nothing registered does not error, it falls
# through to agent judgment. A free deterministic check becomes a billed one that
# reports nothing, which looks exactly like passing.
check("no_retired_location is in the CHECKERS registry",
      "no_retired_location" in ap.CHECKERS, True)
rs = (REPO / "rulesets" / "R-facet-spec.md").read_text(encoding="utf-8")
check("...and R-facet-spec-28 references it",
      "check:: no_retired_location" in rs, True)
check("...as a checked-tier rule",
      "R-facet-spec-28 — No retired location stated as live (checked)" in rs, True)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
