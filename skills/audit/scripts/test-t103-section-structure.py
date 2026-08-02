#!/usr/bin/env python3
"""T103 class (a), the SUPPRESSION half — a rule met by a picture of the thing.

Sibling of `test-t103-fence-blind-checkers.py`, which covered the other direction
(a fenced example judged as a live *violation*). These are worse because they are
silent: the checker returns `pass`, so nothing in any report ever indicates that
the document satisfied the rule with an illustration.

**The seam is the point.** `_section_body` finds section boundaries on the
fence-stripped copy but returned the ORIGINAL lines — correctly, because a section
whose body IS a code block must not read as empty. Callers asking a STRUCTURAL
question (is there an H3 here, a table row, a bullet name, an image embed) needed
the other half, and re-derived it at the call site. Two did so and documented why
at length (`_bold_item_names`, `_subsystems_table_rows` — T102); two did not
(`chk_tests_table_present`, `chk_architecture_diagram_section_with_embed`) and a
fenced sample satisfied both rules outright. The `structure=` flag makes it one
decision per caller instead of a trap that had been sprung three times.

Asking the seam question — rather than working T103's list — is what surfaced the
last two: `chk_strategy_subsections_present_ordered` (a fenced list of the four
required H3s satisfies the rule on a doc declaring none) and
`chk_design_workflow_modern_names` (a doc quoting the RETIRED phase names in a
fence, to say they are retired, is failed for its own explanation).

**Measured, and the honest result is zero — twice over.** Back-to-back over the
vault at each rule's own `where::`: 155,716 verdicts, **0 status moves**. Latent
exposure is near-zero as well: across 7,377 docs, 0 carry a fenced `| Examples |`
row, a fenced-only embed under `## Architecture diagram`, a fenced first table
under `## Tests`, a fenced `[[X Stories]]`, or fenced-only `## Strategy` H3s; 5
carry a `[[R-x]]` reachable only through an inline span, and none of those 5 is a
facet spec, so R-facet-spec-18 does not reach them either. Unlike the first half
of class (a) — 17 docs with a fenced masthead row, 79 with a fenced table row —
this half is not sitting one scope-widening from firing. It is recorded as what it
is: eight reproducible defects with no corpus today, fixed because the seam that
produced four of them is now closed rather than because findings were removed.

**One measurement overruled the fix.** See `test_dispatch_area_is_wider_than_table`.

    python3 test-t103-section-structure.py
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
FENCE = "```markdown\n"


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def doc(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def anchor(name, dot=""):
    d = ROOT / name
    d.mkdir(parents=True, exist_ok=True)
    (d / ".anchor").write_text(dot, encoding="utf-8")
    return d


A = anchor("Fx")

print("The seam — `structure=` picks which copy comes back")

LINES = ["## S", "prose", FENCE.rstrip(), "| fenced | row |", "```", "| real | row |", "## Next"]
check("structure=False returns the ORIGINAL lines (content question)",
      ap._section_body(LINES, r"^## S\b"),
      ["prose", "```markdown", "| fenced | row |", "```", "| real | row |"])
check("structure=True blanks the fenced lines (structural question)",
      ap._section_body(LINES, r"^## S\b", structure=True),
      ["prose", "", "", "", "| real | row |"])
check("boundaries are found on the stripped copy either way — a fenced `## `"
      " does not close the section",
      ap._section_body(["## S", "a", FENCE.rstrip(), "## Fake", "```", "b", "## Real"],
                       r"^## S\b", structure=True),
      ["a", "", "", "", "b"])
# The IndexError guard from T102: `"\n".join(...).splitlines()` drops trailing
# empties, so a doc ENDING inside a fence made `marks` shorter than `lines`.
check("a section running to a doc that ends inside a fence does not raise",
      ap._section_body(["## S", "a", FENCE.rstrip(), "x"], r"^## S\b", structure=True),
      ["a", "", ""])

print("\nA rule is not satisfied by a picture of the thing it requires")

p = doc("Fx/Arch.md", "# Arch\nOrientation.\n\n## Architecture diagram\n\nEmbed it like this:\n\n"
        + FENCE + "![[example-diagram.svg]]\n```\n\n(diagram still to be drawn)\n")
check("a FENCED ![[embed]] does not satisfy the Architecture-diagram rule",
      ap.chk_architecture_diagram_section_with_embed(p, A, []),
      ("fail", "## Architecture diagram has no image embed"))

p = doc("Fx/T.md", "# T\nOrientation.\n\n## Tests\n\nA coverage table looks like:\n\n"
        + FENCE + "| [[Unit Test]] | what it covers |\n| --- | --- |\n| [[a]] | b |\n```\n\n"
        "| Kind | Covers |\n| --- | --- |\n| plain text, no link | b |\n\n## Overview\n")
check("the FENCED sample is not 'the coverage table' — the real one below is judged",
      ap.chk_tests_table_present(p, A, []),
      ("fail", "1 kind row(s) without a [[wiki-link]] first cell"))

p = doc("Fx/S.md", "# S\nOrientation.\n\n## Strategy\n\nThe four subsections read:\n\n" + FENCE
        + "### Test Kinds\n### Completeness Targets\n### Responsibilities\n### Tier Mapping\n```\n\n(to be written)\n")
check("a FENCED list of the four required H3s satisfies nothing",
      ap.chk_strategy_subsections_present_ordered(p, A, [])[0], "fail")

p = doc("Fx/Fx.md", "# DAS Fx\nOrientation.\n\n" + FENCE + "| Examples | [[Some Instance]] |\n```\n")
check("a FENCED Examples row is not an Examples row",
      ap.chk_facet_examples_row(p, A, []), ("fail", "no Examples row in masthead"))

p = doc("Fx/Fx3.md", "# DAS Fx3\nOrientation.\n\nA facet names its ruleset as `[[R-example]]` in prose.\n")
check("a BACKTICKED [[R-x]] is not a linked ruleset — one layer below the fence",
      ap.chk_facet_has_ruleset(p, A, []),
      ("fail", "no embedded # RULESET R- and no linked [[R-...]] ruleset"))

p = doc("Fx/PRD.md", "# PRD\nOrientation.\n\nStories may be extracted to a folder:\n\n"
        + FENCE + "| Stories | [[Fx Stories]] |\n```\n\n## User Stories\n\n### US-WRONG-1: bad id\n")
# The worst shape in this file: the escape returns `pass` with a reason that reads
# as a deliberate deferral, so the rule is not merely wrong — it looks decided.
check("a FENCED [[X Stories]] does not defer the whole user-story rule",
      ap.chk_user_stories_use_rid_numbering(p, A, []),
      ("fail", "user stories not in US-Fx-N format: US-WRONG-1"))

p = doc("Fx/W.md", "# W\nOrientation.\n\n## Design Workflow\n\nPRD → Architecture → Tests. "
        "The retired names were:\n\n" + FENCE + "System Design\nTesting Strategy\n```\n")
check("a doc quoting the RETIRED phase names in a fence is not failed for them",
      ap.chk_design_workflow_modern_names(p, A, []), ("pass", ""))

print("\n...and the live structure is still seen — the fix must not blind them")

p = doc("Fx/Arch2.md", "# Arch2\nOrientation.\n\n## Architecture diagram\n\n![[real.svg]]\n")
check("a REAL embed still passes", ap.chk_architecture_diagram_section_with_embed(p, A, []), ("pass", ""))
p = doc("Fx/Fx4.md", "# DAS Fx4\nOrientation.\n\n| Examples | [[Real Instance]] |\n")
check("a REAL Examples row still passes", ap.chk_facet_examples_row(p, A, []),
      ("pass", "examples row present"))
p = doc("Fx/Fx5.md", "# DAS Fx5\nOrientation.\n\n  | Examples | [[Real]] |\n")
check("a legally-indented (<=3sp) REAL Examples row is now FOUND — it was missed",
      ap.chk_facet_examples_row(p, A, []), ("pass", "examples row present"))
p = doc("Fx/Fx6.md", "# DAS Fx6\nOrientation.\n\nSee [[R-example]] for the rules.\n")
check("a REAL [[R-x]] link still satisfies the ruleset rule",
      ap.chk_facet_has_ruleset(p, A, []), ("pass", "linked sibling ruleset"))
p = doc("Fx/W2.md", "# W2\nOrientation.\n\n## Design Workflow\n\nPRD → System Design → Tests.\n")
check("REAL legacy phase names in the workflow body still fail",
      ap.chk_design_workflow_modern_names(p, A, [])[0], "fail")
p = doc("Fx/PRD2.md", "# PRD2\nOrientation.\n\n| Stories | [[Fx Stories]] |\n\n## User Stories\n\n### US-WRONG-1: x\n")
check("a REAL [[X Stories]] row still defers to R-stories",
      ap.chk_user_stories_use_rid_numbering(p, A, []), ("pass", "folder form (deferred to R-stories)"))

print("\nThe corpus overruled the rule's own wording")


def test_dispatch_area_is_wider_than_table():
    """R-file-association-07 says the anchor carries "a dispatch TABLE of all
    items", and its Check pattern says "the dispatch lists every item file". Read
    literally, links must be harvested from table rows — and harvesting from the
    whole document, which is what the checker did, means "the doc mentions them
    somewhere", prose and fenced examples included.

    Narrowing to table rows measured **five new failures**, and the fifth is
    decisive: `examples/HBR/HBR Design/HBR Features` is THIS REPO'S reference
    method-3 folder, and its three feature docs are a bullet list under a `^^^`
    auto-management separator, not table rows. Four other real folders in the
    vault use the same shape. When the wording and the corpus disagree and the
    reference instance is on the corpus's side, the wording is what is narrow —
    so the dispatch AREA is table rows plus list items, and R-file-association-07's
    text was corrected to say so rather than five compliant folders being failed.
    """
    d = ROOT / "Par Notes"
    d.mkdir(parents=True, exist_ok=True)
    (d / "Item One.md").write_text("# Item One\n", encoding="utf-8")
    head = ("# Par Notes\nOrientation.\n\n| -[[Par Notes]]- | → [[kmr]] |\n| --- | --- |\n"
            "| Related | [[Somewhere Else]] |\n")

    (d / "Par Notes.md").write_text(
        head + "\nProse mentioning [[Item One]] in passing — the dispatch lists nothing.\n",
        encoding="utf-8")
    check("a PROSE mention is not the dispatch listing the item",
          ap.chk_file_association_folder_structure(d, ROOT, []),
          ("fail", "dispatch table links none of the 1 item files"))

    (d / "Par Notes.md").write_text(head + "\n" + FENCE + "- [[Item One]] — a sample row\n```\n",
                                    encoding="utf-8")
    check("a FENCED example listing is not the dispatch either",
          ap.chk_file_association_folder_structure(d, ROOT, []),
          ("fail", "dispatch table links none of the 1 item files"))

    (d / "Par Notes.md").write_text(head + "| [[Item One]] | the item |\n", encoding="utf-8")
    check("a TABLE-row listing counts (the rule's literal wording)",
          ap.chk_file_association_folder_structure(d, ROOT, []),
          ("pass", "folder structure OK: 1 items linked"))

    (d / "Par Notes.md").write_text(head + "| ^^^ | |\n\n- [[Item One]] — the item\n",
                                    encoding="utf-8")
    check("a BULLET listing under the masthead counts — the HBR Features shape",
          ap.chk_file_association_folder_structure(d, ROOT, []),
          ("pass", "folder structure OK: 1 items linked"))


test_dispatch_area_is_wider_than_table()

print("\nThe table primitives reach the last `rows[2:]` site")

# `_subsystems_table_rows` kept its own spelling of "a table row" (`lstrip()`) and
# its own blanket header skip (`rows[2:]`) after T103b replaced both everywhere else.
LINES = ["## Subsystems", "| Name | What |", "| --- | --- |", "| [[A]] | a |",
         "", "| Legend | Meaning |", "| --- | --- |", "| x | y |", "## Next"]
check("a second table's header/separator are not read as subsystem rows",
      ap._subsystems_table_rows(LINES), ["| [[A]] | a |"])
check("a legally-indented subsystems table is found",
      ap._subsystems_table_rows(["## Subsystems", "  | Name | What |", "  | --- | --- |",
                                 "  | [[A]] | a |", "## Next"]),
      ["  | [[A]] | a |"])
check("no ## Subsystems section is still None (distinct from an empty one)",
      ap._subsystems_table_rows(["## Other", "x"]), None)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
