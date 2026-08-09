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

# Bindings for every generable proposal.  Provenance, MEASURED rather than
# assumed (T179): this comment used to claim every value was "lifted from the
# corpus's own specimens where one exists (T1.a, T3.a, T6.a)".  That is false
# for T1.A, and only half true for T3.A and T6.A — see the specimen-equality
# section below, which checks generated output against the real specimen
# text (not against the parser that produced the stencil) and is what a
# hand-typed, wrong binding cannot slip past silently the way it did before.
#
#   T1.A   NOT lifted.  None of `slug` / `one-line description` /
#          `dispatch table` occurs anywhere in specimen T1.a (`HERMES
#          Backlog.md`) — this env is a self-referential, TINK-flavoured
#          document describing this very test suite, invented from scratch.
#   T3.A   the FIRST LOG entry is lifted verbatim (see ENV_T3A below); the
#          SECOND is invented — repetition needs two occurrences and the
#          specimen shows only one.
#   T5.B   T7.A no single specimen to lift verbatim (T5.a is abridged and carries
#          the cut line; T7.b has no variables at all — it is the shape
#          already, not a stencil instance), so their bindings are plain,
#          stencil-shaped text.
#   T6.A   TITLE / IDENTITY / the two curated rows are lifted verbatim (see
#          ENV_T6A below); the specimen's trailing `...` catch-all row is
#          deliberately not covered — T6.A proposes only the curated rows.

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

# The FIRST LOG entry, extracted with the real matcher against the real
# specimen — not hand-typed — so it is byte-exact, including the leading
# blank line the `{{entry body}}` Hole itself captures (T3.A's stencil has
# no Blank between the heading and the Hole; T3.a's actual layout does, so
# the Hole's capture legitimately starts with "\n").  A hand-typed copy
# dropped that blank line and nothing caught it before specimen-equality did.
_T3A_ENTRY0 = M.match(B["T3.A"], B["T3.a"]).bindings

ENV_T3A = {
    "one-line description": _T3A_ENTRY0["one-line description"],
    "YYYY-MM-DD": [_T3A_ENTRY0["YYYY-MM-DD"], "2026-08-05"],
    "DAY": [_T3A_ENTRY0["DAY"], "Wed"],
    "DIRECTION": [_T3A_ENTRY0["DIRECTION"], "RECEIVED"],
    "KIND": [_T3A_ENTRY0["KIND"], "note"],
    "entry body": [
        _T3A_ENTRY0["entry body"],
        # invented second entry — the specimen shows only one occurrence
        "To: robin@northwind.example\nSubject: Following up\n\n"
        "Robin, checking in on the timeline.",
    ],
}

ENV_T5B = {
    "NICKNAME": "haorui",
    "role — one line": "Primary working machine.",
    "HOSTNAME": "haorui",
}

# TITLE / IDENTITY / the two curated rows, likewise extracted with the real
# matcher against T6.a's own lines rather than hand-typed.  The hand-typed
# version this replaces got THREE things wrong at once — "Scout Track"
# instead of the specimen's "SCOUT Track", trailing padding baked into
# LEFT/IDENTITY that duplicated padding the stencil's own literals already
# supply, and (T179's actual defect) an unescaped `|` — and every one of
# them still reported MATCH under the existential round trip below.
_T6A_HEAD = M.match("| -[[{{TITLE}}]]- | {{IDENTITY}} |",
                    B["T6.a"].split("\n")[0]).bindings
_T6A_ROWS = [M.match("| {{LEFT}}  | {{RIGHT}} |", line).bindings
            for line in B["T6.a"].split("\n")[2:4]]      # Backlog, Messages —
            # NOT the trailing `...` catch-all row, which T6.A does not cover

ENV_T6A = {
    "TITLE": _T6A_HEAD["TITLE"],
    "IDENTITY": _T6A_HEAD["IDENTITY"],
    # unescaped here on purpose — Part 1 of T179 makes escaping the
    # GENERATOR's job, so a binding carries the plain `|` and `generate`
    # re-escapes it for the table row that renders it.
    "LEFT": [b["LEFT"].replace("\\|", "|") for b in _T6A_ROWS],
    "RIGHT": [b["RIGHT"] for b in _T6A_ROWS],
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


# --------------------------------------------------- specimen equality (T179)
#
# `run_round_trips` below asks an EXISTENTIAL question — does some stencil
# accept the generated text — and both directions of that question run
# through the SAME `parse_stencil`, so a malformation both sides express
# identically (the T6.A unescaped-`|` defect) is invisible to it.  This asks
# the stronger question: does the generated text match the corpus's OWN
# specimen, not the parser that produced the stencil.
#
# label -> specimen label is "same digits, lowercase letter" — not assumed,
# checked against `sten_corpus.blocks()` below (`unit_specimen_map_matches_corpus`).
# T3.B is the one declared exception: there is no `T3.b` block in the corpus
# — T3.B shares T3.A's body verbatim (`generate` does not read anchor mode)
# and so is checked against the SAME specimen, T3.a, not one of its own.
SPECIMEN_OF = {"T1.A": "T1.a", "T3.A": "T3.a", "T3.B": "T3.a", "T6.A": "T6.a"}
ALIASED_SPECIMEN = {"T3.B"}          # excused from the by-convention check


def unit_specimen_map_matches_corpus():
    """SPECIMEN_OF is a claim about the corpus's own labelling, not a
    hand-trusted assumption — every pair must be two real blocks in
    `sten_corpus.blocks()`, and (aside from the declared alias above) must
    differ by exactly the letter's case."""
    for stencil_label, specimen_label in SPECIMEN_OF.items():
        assert stencil_label in B, f"{stencil_label} not a corpus block"
        assert specimen_label in B, f"{specimen_label} not a corpus block"
        if stencil_label in ALIASED_SPECIMEN:
            continue
        num_s, letter_s = stencil_label.split(".")
        num_e, letter_e = specimen_label.split(".")
        assert num_s == num_e and letter_s.lower() == letter_e, (
            f"{stencil_label} / {specimen_label}: not a stencil/specimen pair "
            f"by the same-digits-lowercase-letter convention")


UNITS.append(unit_specimen_map_matches_corpus)

# Which of SPECIMEN_OF's pairs get checked, and how — T1.A is EXCLUDED even
# though T1.a exists: measured above, none of ENV_T1A's values occur in it,
# so there is nothing of the specimen for generated text to reproduce.
#   "specimen-is-prefix"  the specimen's full text must open the generated
#                          text — used where generate legitimately emits MORE
#                          than the specimen shows (T3's invented 2nd entry).
#   "generated-is-prefix" the generated text must open the specimen's full
#                          text — used where the specimen legitimately shows
#                          MORE than the proposal covers (T6.A's proposal
#                          never emits the catch-all row T6.a carries).
SPECIMEN_EQUALITY = [
    ("T3.A", "T3.a", "specimen-is-prefix"),
    ("T3.B", "T3.a", "specimen-is-prefix"),
    ("T6.A", "T6.a", "generated-is-prefix"),
]


def run_specimen_equality(generated: dict):
    print("\n=== specimen equality: generate(S, env) vs the corpus's own specimen ===")
    bad = []
    for stencil_label, specimen_label, mode in SPECIMEN_EQUALITY:
        gen = generated[stencil_label]
        specimen = B[specimen_label]
        if mode == "specimen-is-prefix":
            ok = gen.startswith(specimen)
        elif mode == "generated-is-prefix":
            ok = specimen.startswith(gen.rstrip("\n"))
        else:
            raise AssertionError(f"unknown mode {mode!r}")
        mark = "ok " if ok else "XX "
        print(f"  {mark}{stencil_label:<8} vs {specimen_label} ({mode}): "
              f"{'MATCH' if ok else 'MISMATCH'}")
        if not ok:
            bad.append((stencil_label, specimen_label, mode))
    return not bad


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
    se_ok = run_specimen_equality(generated)
    neg_ok = run_negative_direction(generated)

    green = rt_ok and se_ok and neg_ok and not failed
    print("\n" + ("SUITE GREEN" if green else "SUITE RED"))
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
