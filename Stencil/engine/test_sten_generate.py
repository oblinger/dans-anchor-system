#!/usr/bin/env python3
"""Test suite for the Stencil generator (F303 M4).

The milestone's acceptance criterion, verbatim from the F303 roadmap:
*"the generator ... instantiate a template into a new file and have M3's
matcher accept it."*  So the corpus half of this suite does exactly that for
every PROPOSAL in `design/Template Examples.md` that is generable as a
single document: bind its variables, call `sten_generate.generate`, then run
the REAL `sten_match.match` — not a hand-written expected string and not a
second, laxer matcher — against the result with the same stencil text, and
assert MATCH.

Three proposals in the corpus are NOT exercised here, each for a stated
reason:

  T2.A   a folder tree (`{slug} Log.md` + dated members); `{slug}` is a
         single-brace literal under this grammar (only `{{NAME}}` is a
         variable — F04 in test_sten_match.py already establishes it can
         match no real folder), and a folder is not a single document.
         Folder generation would pair with `match_folder`, not `match`.
  T5.A   likewise a folder tree (`Computer {{NICKNAME}}.md`); T5.B, the
         MEMBER document it names, is exercised below.
  T4.A   T4's own Overview states its direction explicitly: "match and
         reconcile only" — log entries are never rewritten (F302), so there
         is no conforming document to generate FROM this proposal, by the
         corpus's own account.

That leaves seven generable proposals: T1.A, T3.A, T3.B, T5.B, T6.A, T6.B,
T7.A.  T3.A and T3.B share one body (only the anchor mode differs, and
`generate` does not read anchor mode — it uses the stencil's OWN depth,
having no existing document to float against), so T3.B is covered by
asserting its round trip once rather than duplicating the entry bindings.

A pair may be marked CONTINGENT the same way test_sten_match.py's corpus
pairs are — not needed here, no generate-direction question is unsettled.

Standalone: `python3 test_sten_generate.py`.  No dependencies beyond the
standard library and the two sibling modules.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sten_corpus as C           # noqa: E402
import sten_match as M            # noqa: E402
import sten_generate as G         # noqa: E402

B = C.blocks()


# --------------------------------------------------------------------- units

def unit_singular_binding():
    """A stencil with no repeating structure — one value per variable."""
    out = G.generate("# {{slug}} Backlog\n{{one-line description}}\n",
                     {"slug": "TINK", "one-line description": "desc"},
                     name="unit")
    assert out == "# TINK Backlog\ndesc\n", out


def unit_hole_is_multiline():
    """A line that is nothing but a variable is a multi-line hole — the
    bound value's own embedded newlines pass through untouched."""
    out = G.generate("# X\n{{body}}\n", {"body": "line one\nline two"}, name="unit")
    assert out == "# X\nline one\nline two\n", out


def unit_binding_list_repeats_a_group():
    """Many-by-variable: a free-variable group takes a LIST, one entry per
    repetition — T3's central case, reduced to its own two lines."""
    stencil = "## {{DATE}} {{KIND}}\n{{body}}\n"
    out = G.generate(stencil, {"DATE": ["2026-01-01", "2026-01-02"],
                                "KIND": ["a", "b"],
                                "body": ["x", "y"]}, name="unit")
    assert out == ("## 2026-01-01 a\nx\n\n## 2026-01-02 b\ny\n"), out
    r = M.match(stencil, out)
    assert r.ok


def unit_one_line_group_gets_no_separator_blank():
    """A one-item repeating group (a table row) packs tight — no blank
    line is inserted between repetitions, unlike a multi-line group."""
    stencil = "| {{LEFT}}  | {{RIGHT}} |\n"
    out = G.generate(stencil, {"LEFT": ["a", "b"], "RIGHT": ["1", "2"]}, name="unit")
    assert out == "| a  | 1 |\n| b  | 2 |\n", out


def unit_binding_shared_across_a_members_artifacts():
    """T5's claim: a variable bound once is reused, not re-asked for, the
    second time the same name appears."""
    stencil = "# Computer {{NICKNAME}}\nnick: {{NICKNAME}}\n"
    out = G.generate(stencil, {"NICKNAME": "haorui"}, name="unit")
    assert out == "# Computer haorui\nnick: haorui\n", out


def unit_missing_binding_fails_loudly():
    try:
        G.generate("# {{slug}} Backlog\n", {}, name="unit")
        assert False, "expected StencilError"
    except G.StencilError as e:
        assert "slug" in str(e) and "unit" in str(e)


def unit_mismatched_list_lengths_fail_loudly():
    stencil = "## {{DATE}} {{KIND}}\n"
    try:
        G.generate(stencil, {"DATE": ["a", "b"], "KIND": ["x"]}, name="unit")
        assert False, "expected StencilError"
    except G.StencilError as e:
        assert "DATE" in str(e) and "KIND" in str(e)


def unit_empty_list_fails_loudly():
    """Inside a document the count is one-or-more, never zero — that is a
    folder member's privilege only (STEN Language § many-by-variable)."""
    stencil = "## {{DATE}}\n"
    try:
        G.generate(stencil, {"DATE": []}, name="unit")
        assert False, "expected StencilError"
    except G.StencilError as e:
        assert "DATE" in str(e)


def unit_malformed_stencil_refused_not_guessed():
    """Two adjacent unbound variables with no literal between them — a
    live defect in T5.a, cited verbatim — is refused, not silently split."""
    line = next(l for l in B["T5.a"].split("\n")
               if "phonetic hint if non-obvious" in l)
    try:
        G.generate(line + "\n", {}, name="T5.a-line")
        assert False, "expected StencilError"
    except G.StencilError as e:
        assert "malformed" in str(e)


UNITS = [unit_singular_binding, unit_hole_is_multiline,
         unit_binding_list_repeats_a_group,
         unit_one_line_group_gets_no_separator_blank,
         unit_binding_shared_across_a_members_artifacts,
         unit_missing_binding_fails_loudly,
         unit_mismatched_list_lengths_fail_loudly,
         unit_empty_list_fails_loudly,
         unit_malformed_stencil_refused_not_guessed]


# ------------------------------------------------------------- corpus round trips

# Bindings for every generable proposal.  Values are lifted from the corpus's
# own specimens where one exists (T1.a, T3.a, T6.a) so a generated document
# reads as a real instance rather than an invented one; T5.B and T7.A have no
# single specimen to lift verbatim (T5.a is abridged and carries the cut
# line; T7.b has no variables at all — it is the shape already, not a
# stencil instance), so their bindings are plain, stencil-shaped text.

ENV_T1A = {
    "slug": "TINK",
    "one-line description":
        "The work queue for Tink, testing the F303 M4 generator.",
    "dispatch table":
        "| -[[TINK Backlog]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] "
        "→ [[DAS]] → [[TINK]] → [TINK Backlog](hook://p/TINK%20Backlog)  |\n"
        "| --- | --- |\n"
        "| ... | [[TINK queries]],   |",
}

ENV_T3A = {
    "one-line description":
        "Reverse-chronological correspondence and notes with Robin Calder "
        "(Northwind champion), newest first.",
    "YYYY-MM-DD": ["2026-08-03", "2026-08-05"],
    "DAY": ["Mon", "Wed"],
    "DIRECTION": ["SENT", "RECEIVED"],
    "KIND": ["reply", "note"],
    "entry body": [
        "To: robin@northwind.example\nSubject: Thanks, Robin\n\nRobin,\n\n"
        "Thanks for the update, and for running a straight process "
        "throughout.\n\nBest,\nDan",
        "To: robin@northwind.example\nSubject: Following up\n\n"
        "Robin, checking in on the timeline.",
    ],
}

ENV_T5B = {
    "NICKNAME": "haorui",
    "role — one line": "Primary working machine.",
    "HOSTNAME": "haorui",
}

ENV_T6A = {
    "TITLE": "Scout Track",
    "IDENTITY":
        "→ [[kmr]] → [[SYS]] → [[Staff]] → [[SCOUT]] → "
        "[Scout Track](hook://p/Scout%20Track)  ",
    "LEFT": ["[[Scout Backlog|Backlog]]  ", "[[Scout Messages|Messages]]  "],
    "RIGHT": ["", ""],
}

ENV_T6B = {"dispatch table": "| a | b |\n| --- | --- |\n| ... |  |"}

ENV_T7A = {
    "FACET_NAME": "Stencil",
    "one-line summary":
        "A facet is a named, recurring document/folder kind.",
    "dispatch table":
        "| -[[DAS Stencil]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] "
        "→ [[DAS]] → [DAS Stencil](hook://p/DAS%20Stencil)  |\n"
        "| --- | --- |\n"
        "| Related | [[DAS Facets]],   |",
    "facet-slug": "sten-generate",
}

GENERABLE = [
    ("T1.A", ENV_T1A),
    ("T3.A", ENV_T3A),
    ("T3.B", ENV_T3A),      # same body as T3.A; only the anchor mode differs
    ("T5.B", ENV_T5B),
    ("T6.A", ENV_T6A),
    ("T6.B", ENV_T6B),
    ("T7.A", ENV_T7A),
]

NOT_GENERABLE = {
    "T2.A": "folder tree; `{slug}` is a single-brace literal (F04), and a "
            "folder is not a single document — match_folder's territory.",
    "T5.A": "folder tree; T5.B (its member) is exercised instead.",
    "T4.A": "T4 Overview: \"Direction: match and reconcile only\" — log "
            "entries are never rewritten (F302), so there is no document "
            "to generate.",
}


def run_round_trips(verbose: bool):
    print("\n=== corpus round trips: generate(S, env) then match(S, generated) ===")
    rows = []
    for label, env in GENERABLE:
        stencil = B[label]
        gen = G.generate(stencil, env, name=label)
        r = M.match(stencil, gen)
        rows.append((label, r.ok, gen, r))
        mark = "ok " if r.ok else "XX "
        print(f"  {mark}{label:<8} generate → match: {'MATCH' if r.ok else 'NO MATCH'}")
        if verbose or not r.ok:
            print("      --- generated text ---")
            for l in gen.split("\n"):
                print("      " + l)
            for f in r.failures:
                print("      ! " + f)
    ok = all(row_ok for _, row_ok, *_ in rows)
    return ok, {label: gen for label, row_ok, gen, r in rows}


def run_negative_direction(generated: dict):
    """A generator that emits something so generic every stencil accepts it
    is worthless — check that stencils the corpus keeps apart still refuse
    each other's generated documents, mirroring N01/N03's verdicts."""
    print("\n=== negative direction: generated documents still refused ===")
    checks = [
        ("T7.A", "T1.A", False,
         "a generated Backlog is not a facet spec (mirrors N03)"),
        ("T1.A", "T7.A", False,
         "a generated facet spec is not a Backlog (mirrors N01)"),
        ("T7.A", "T3.A", False,
         "a generated LOG section carries no facet structure"),
        ("T3.A", "T7.A", False,
         "a generated facet spec carries no LOG heading"),
        ("T1.A", "T5.B", False,
         "a generated Computer page is not a Backlog"),
        # positive control: a stencil must still accept its own family
        ("T1.A", "T1.A", True, "control — T1.A must still match its own generated instance"),
    ]
    bad = []
    for stencil_label, doc_label, want, why in checks:
        r = M.match(B[stencil_label], generated[doc_label])
        got = r.ok
        mark = "ok " if got == want else "XX "
        print(f"  {mark}{stencil_label} vs generate({doc_label}): "
              f"expected {'MATCH' if want else 'NO MATCH'}, got "
              f"{'MATCH' if got else 'NO MATCH'} — {why}")
        if got != want:
            bad.append((stencil_label, doc_label, want, got))
    return not bad


def main():
    verbose = "-v" in sys.argv
    failed = []
    print("=== unit tests ===")
    for fn in UNITS:
        try:
            fn()
            print(f"  ok  {fn.__name__}")
        except AssertionError as e:
            failed.append(fn.__name__)
            print(f"  XX  {fn.__name__}: {e}")

    print(f"\n=== corpus coverage ===")
    print(f"  {len(GENERABLE)} of {len(GENERABLE) + len(NOT_GENERABLE)} "
          f"proposals are generable as a single document:")
    for label, env in GENERABLE:
        print(f"    generable      {label}")
    for label, why in NOT_GENERABLE.items():
        print(f"    not generable  {label}  — {why}")

    rt_ok, generated = run_round_trips(verbose)
    neg_ok = run_negative_direction(generated)

    green = rt_ok and neg_ok and not failed
    print("\n" + ("SUITE GREEN" if green else "SUITE RED"))
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
