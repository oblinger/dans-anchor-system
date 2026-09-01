"""T290 — a declared slug names the folder note (ATT T290, Dan 2026-08-30).

`chk_entry_page_matches_slug` long passed any anchor whose note `_entry_page`
could RESOLVE — `{slug}.md` first, `{folder}.md` as fallback — which made the
rule's own text ("the entry page is named {slug}.md") unenforced whenever a
slug was declared but the note kept the folder name. The T290 arm fails that
fallback hit. These fixtures observe each branch fire and each carve-out hold,
because the live corpus is at zero (T289's cleanup) and a green sweep over a
clean corpus proves nothing about the rule's ability to fail.

Run with:  python3 -m pytest skills/audit/tests/test_t290_slug_names_note.py
"""

import importlib.util
import pathlib
import sys

_AUDIT_PLAN_PATH = pathlib.Path(__file__).parent.parent / "scripts" / "audit-plan.py"
_spec = importlib.util.spec_from_file_location("audit_plan_t290", _AUDIT_PLAN_PATH)
assert _spec is not None and _spec.loader is not None
ap = importlib.util.module_from_spec(_spec)
sys.modules["audit_plan_t290"] = ap
_spec.loader.exec_module(ap)


def _anchor(tmp_path, folder, slug=None, files=()):
    root = tmp_path / folder
    root.mkdir(parents=True)
    (root / ".anchor").write_text(f"slug: {slug}\n" if slug else "")
    for f in files:
        (root / f).write_text("# x\n")
    return root


def test_slug_note_present_passes(tmp_path):
    root = _anchor(tmp_path, "Agent Recipes", slug="AREC", files=["AREC.md"])
    verdict, msg = ap.chk_entry_page_matches_slug(root, root, [])
    assert verdict == "pass"


def test_folder_note_under_declared_slug_fails(tmp_path):
    root = _anchor(tmp_path, "Agent Recipes", slug="AREC", files=["Agent Recipes.md"])
    verdict, msg = ap.chk_entry_page_matches_slug(root, root, [])
    assert verdict == "fail"
    assert "AREC.md" in msg and "T290" in msg


def test_no_slug_folder_note_passes(tmp_path):
    root = _anchor(tmp_path, "Agent Recipes", files=["Agent Recipes.md"])
    verdict, msg = ap.chk_entry_page_matches_slug(root, root, [])
    assert verdict == "pass"


def test_restatement_slug_passes(tmp_path):
    # slug == folder basename: {folder}.md IS {slug}.md; R-dot-anchor-03 owns
    # the restatement finding, not this rule.
    root = _anchor(tmp_path, "Notes", slug="Notes", files=["Notes.md"])
    verdict, msg = ap.chk_entry_page_matches_slug(root, root, [])
    assert verdict == "pass"


def test_missing_note_stays_the_other_finding(tmp_path):
    # No note at all is the ep-is-None branch — same verdict and message shape
    # as before T290, not the rename message.
    root = _anchor(tmp_path, "Empty", slug="EMP")
    verdict, msg = ap.chk_entry_page_matches_slug(root, root, [])
    assert verdict == "fail"
    assert "no entry page" in msg


def test_stone_group_carveout(tmp_path):
    # A book group: kind-template control file as namesake, slug declared.
    # Renaming its note to the slug breaks R-stone-01/-02/-07 (T289), so the
    # rule must not fire.
    root = _anchor(tmp_path, "Hermes Book", slug="HERMESBOOK",
                   files=["Hermes Book.md"])
    verdict, msg = ap.chk_entry_page_matches_slug(root, root, [])
    assert verdict == "pass"
    assert "stone group" in msg


def test_warden_corpus_carveout(tmp_path):
    root = _anchor(tmp_path, "Warden Corpus/cases/c1/fixture", slug="FX1",
                   files=["fixture.md"])
    verdict, msg = ap.chk_entry_page_matches_slug(root, root, [])
    assert verdict == "pass"
    assert "corpus fixture" in msg
