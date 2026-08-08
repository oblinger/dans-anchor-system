#!/usr/bin/env python3
"""Test suite for the Stencil matcher (F303 M3).

Two halves.

**Unit** — the primitives: whitespace normalization, the two anchor depth
modes, anchor nesting, greedy binding between literals, binding consistency.

**Corpus** — the verification standard the F303 row sets: every stencil and
every specimen is lifted verbatim out of `design/Template Examples.md` or read
from the real vault file the corpus cites, and each pair carries the verdict a
human reading that specimen would give, with the sentence in the corpus that
supplies it.  The run prints a confusion matrix and names every cell that is
not a hit.

A pair may be marked CONTINGENT — its verdict depends on a grammar question the
spec has not settled.  Those are reported, never scored, and never silently
counted as passes.

Standalone: `python3 test_sten_match.py`.  Exit 0 iff every scored pair hits
and every unit test passes.
"""
from __future__ import annotations

import json
import pathlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sten_corpus as C          # noqa: E402
import sten_match as M           # noqa: E402

B = C.blocks()

# Live vault files the corpus cites.  This repo is PUBLIC, so the paths of
# private correspondence are NOT committed: they are read from an untracked
# `vault-paths.local.json` beside this file, keyed by the neutral ids below.
# A pair whose path is missing is SKIPPED AND COUNTED IN THE SUMMARY — never
# silently passed, because a privacy fix that quietly shrinks the corpus is
# just a vacuous zero wearing a different hat.
_LOCAL = pathlib.Path(__file__).with_name("vault-paths.local.json")
try:
    _PATHS = json.loads(_LOCAL.read_text(encoding="utf-8"))
except OSError:
    _PATHS = {}

PERSON_LOG_A = _PATHS.get("person_log_a")   # a correspondence log, `## ` entries
PERSON_LOG_B = _PATHS.get("person_log_b")   # same facet, `### ` entries, no KIND
HERMES = "SYS/Staff/Hermes/HERMES Track/HERMES Backlog.md"
HAORUI = "SYS/SYS Catalog/Computer/Computer haorui.md"
DANIEL = "SYS/SYS Catalog/Computer/Computer Daniel MacBook Pro.md"
SCOUT = "SYS/Staff/Scout/Scout Track/Scout Track.md"
DKT = "prj/ClaudiMux/Docket/DKT Track/DKT Track.md"

FACET = C.repo_root() / "facets" / "DAS Facet.md"
FACET_LOG = C.repo_root() / "facets" / "DAS Log.md"

# The two repairs the corpus itself prescribes but never writes out, derived
# mechanically from the blocks so they cannot drift from them.
T3_A_NESTED = B["T3.A"].replace("## {{YYYY-MM-DD}}", "## ... {{YYYY-MM-DD}}")
T4_A_ANCHORED = "## ... " + B["T4.A"].split("## ", 1)[1]


# --------------------------------------------------------------------- units

def unit_normalization():
    """T4: the two live LOG spellings differ only in invisible bytes."""
    assert M.normalize_line("**From:** Dan") == "**From:** Dan"
    assert M.normalize_line("# LOG   ") == "# LOG"
    # internal runs survive — T3.A separates DAY from DIRECTION by TWO spaces
    assert M.normalize_line("a  b") == "a  b"


def unit_anchor_depth_modes():
    """`...` is this-deep-or-deeper; `==` is exactly this deep."""
    doc = "# top\n\n## LOG\n\nbody\n"
    assert M.match("# ... LOG\nbody\n", doc).ok, "`...` must reach a deeper heading"
    assert not M.match("# == LOG\nbody\n", doc).ok, "`==` must refuse a deeper heading"
    doc1 = "# LOG\n\nbody\n"
    assert M.match("# == LOG\nbody\n", doc1).ok
    assert M.match("# ... LOG\nbody\n", doc1).ok


def unit_anchor_nesting_is_relative():
    """Depth inside an anchor is relative to where the anchor matched."""
    deep = "# a\n\n## LOG\n\n### entry\n\nx\n"
    assert M.match("## ... LOG\n\n### entry\n", deep).ok
    # the same stencil written one level up still works, because it is relative
    assert M.match("# ... LOG\n\n## entry\n", deep).ok


def unit_greedy_binding_between_literals():
    """T5.b: `Computer Daniel MacBook Pro.md` must bind a phrase, not a token."""
    r = M.match("# Computer {{NICKNAME}}", "# Computer Daniel MacBook Pro")
    assert r.ok and r.bindings["NICKNAME"] == "Daniel MacBook Pro", r.bindings


def unit_binding_is_shared_across_a_members_artifacts():
    """T5's claim #2: one binding, reused — so a disagreement is a failure."""
    ok = M.match("# Computer {{NICKNAME}}\nnick: {{NICKNAME}}",
                 "# Computer haorui\nnick: haorui")
    assert ok.ok
    bad = M.match("# Computer {{NICKNAME}}\nnick: {{NICKNAME}}",
                  "# Computer haorui\nnick: something else")
    assert not bad.ok


def unit_open_world_permits_extra_content():
    """A stencil states what is present, never what is absent."""
    r = M.match("## Ready\n\n## Now\n",
                "## Ready\n\n- an item nothing describes\n\n## Now\n")
    assert r.ok


def unit_adjacent_variables_are_flagged():
    _, notes = M.parse_stencil("x {{A}}{{B}}\n")
    assert notes and "adjacent variables" in notes[0]


def unit_folder_cardinality():
    """Bound member = exactly one; free member = 0+ (many-by-variable)."""
    r = M.match_folder(["{{X}} Log.md", "ATT Log.md"], ["ATT Log.md"])
    assert r.ok
    bad = M.match_folder(["ATT Log.md"], ["something else.md"])
    assert not bad.ok


UNITS = [unit_normalization, unit_anchor_depth_modes,
         unit_anchor_nesting_is_relative, unit_greedy_binding_between_literals,
         unit_binding_is_shared_across_a_members_artifacts,
         unit_open_world_permits_extra_content,
         unit_adjacent_variables_are_flagged, unit_folder_cardinality]


# -------------------------------------------------------------- corpus pairs

MATCH, NO, CONTINGENT = "MATCH", "NO MATCH", "CONTINGENT"


def blk(k):
    return lambda: B[k]


def vault(rel):
    """Getter for a live vault file. Returns None when the path is not
    configured locally, which marks the pair SKIPPED rather than failing or —
    worse — silently dropping it from the denominator."""
    if not rel:
        return lambda: None
    return lambda: C.read(rel)


def repo(p):
    return lambda: p.read_text(encoding="utf-8")


PAIRS = [
    # ---- specimen against specimen: the corpus's own byte-exact blocks -----
    ("P01", "T1.A", "T1.a", blk("T1.A"), blk("T1.a"), MATCH,
     "T1: `templates/backlog.md` governs every `{slug} Backlog.md`; T1.a is the instance."),
    ("P02", "T3.A", "T3.a", blk("T3.A"), blk("T3.a"), MATCH,
     "T3: `LOG` sits at H1 here, and `...` is this-deep-or-deeper."),
    ("P03", "T3.B", "T3.a", blk("T3.B"), blk("T3.a"), MATCH,
     "T3: `==` is exactly-this-deep, and LOG is exactly H1 in this file."),
    ("P04", "T4.A", "T4.c", blk("T4.A"), blk("T4.c"), NO,
     "T4: the two real spellings are incompatible; reconciliation is "
     "'did TO and SUBJECT bind', which needs the match to fail and report."),
    ("P05", "T4.A", "T3.a", blk("T4.A"), blk("T3.a"), MATCH,
     "T4: T3.a is 'the house form' — bare `To:` / `Subject:` — which is what T4.A writes."),
    ("P06", "T4.A", "T4.a", blk("T4.A"), blk("T4.a"), NO,
     "T4: 'T4.a and T4.b are not entry headers at all' — pasted correspondence inside a body."),
    ("P07", "T4.A", "T4.b", blk("T4.A"), blk("T4.b"), NO,
     "T4: same — a tilde-fenced quote inside an entry body, not an entry header."),
    ("P08", "T6.A", "T6.a", blk("T6.A"), blk("T6.a"), MATCH,
     "T6: 'T6.A is expressible with the three constructs and nothing else'."),
    ("P09", "T6.A", "T6.b", blk("T6.A"), blk("T6.b"), MATCH,
     "T6: 'the same pattern spans the separator and swallows the electric zone'."),
    ("P10", "T7.A", "T7.b", blk("T7.A"), blk("T7.b"), MATCH,
     "T7: 'This is the acceptance test passing.'"),

    # ---- stencil against the real vault file the case cites ---------------
    ("P11", "T3.A", "person-log-A", blk("T3.A"), vault(PERSON_LOG_A), MATCH,
     "The real file behind the `@Robin Calder` pseudonym; LOG at H1, entries at H2."),
    ("P12", "T3.A", "person-log-B", blk("T3.A"), vault(PERSON_LOG_B), NO,
     "T4: \"T3.A's `## {{YYYY-MM-DD}}…`, read as 'one deeper than wherever LOG "
     "matched', is **wrong for this file**\" — entries are H3 here."),
    ("P13", "T3.A-nested", "person-log-A", lambda: T3_A_NESTED, vault(PERSON_LOG_A), MATCH,
     "T4's prescribed repair — the entry heading is itself an anchor."),
    ("P14", "T3.A-nested", "person-log-B", lambda: T3_A_NESTED, vault(PERSON_LOG_B), NO,
     "T4 asserts this form 'is correct for both'.  Reading the real file says "
     "otherwise: its entries are `### 2022-12-19  Summary of email for Nick.` — "
     "no DIRECTION, no KIND, no em-dash.  Depth was never the only difference."),
    ("P15", "T3.B", "person-log-B", blk("T3.B"), vault(PERSON_LOG_B), NO,
     "Same file; `==` cannot reach H3 entries either."),
    ("P16", "T4.A-anchored", "person-log-A", lambda: T4_A_ANCHORED, vault(PERSON_LOG_A), MATCH,
     "T4.A carries no anchor marker; anchored, it locates the house-form entry."),
    ("P17", "T5.B", "Computer haorui.md", blk("T5.B"), vault(HAORUI), NO,
     "T5.B asserts the SAME `{{NICKNAME}}` appears in filename, H1 and the nickname "
     "line.  The live member's nickname line reads `\"haorui\", phonetic \"how-ray\"`, "
     "so the three do not agree and a reader checking them would say so."),
    ("P18", "T5.B", "Computer Daniel MacBook Pro.md", blk("T5.B"), vault(DANIEL), NO,
     "Same, and worse: the nickname line is `\"the laptop\", \"primary\", \"this Mac\"`."),
    ("P19", "T6.A", "Scout Track.md", blk("T6.A"), vault(SCOUT), MATCH,
     "T6.a is quoted from this file."),
    ("P20", "T6.A", "DKT Track.md", blk("T6.A"), vault(DKT), MATCH,
     "T6.b is quoted from this file."),
    ("P21", "T7.A", "facets/DAS Facet.md", blk("T7.A"), repo(FACET), NO,
     "The acceptance test's own instance no longer carries `# RULESET R-facet-spec` "
     "— the ruleset now lives at `rulesets/R-facet-spec.md`.  T7.b is a stale "
     "snapshot, and the live file violates the structure its own "
     "`# Facet Document Structure` list marks REQUIRED."),
    ("P22", "T7.A", "facets/DAS Log.md", blk("T7.A"), repo(FACET_LOG), NO,
     "A second facet spec: it has no `# Log Document Structure` heading, so the "
     "shape T7.A generalizes from does not generalize."),

    # ---- negative controls: a matcher that says yes to everything is useless
    ("N01", "T1.A", "facets/DAS Facet.md", blk("T1.A"), repo(FACET), NO,
     "Negative control — a facet spec is not a Backlog."),
    ("N02", "T3.A", "HERMES Backlog.md", blk("T3.A"), vault(HERMES), NO,
     "Negative control — no LOG heading anywhere in the file."),
    ("N03", "T7.A", "HERMES Backlog.md", blk("T7.A"), vault(HERMES), NO,
     "Negative control — a Backlog is not a facet spec."),
    ("N04", "T1.A", "(empty document)", blk("T1.A"), lambda: "", NO,
     "Negative control — the empty document must not satisfy a stencil."),
    ("N05", "T6.A", "T7.a", blk("T6.A"), blk("T7.a"), NO,
     "Negative control — a bullet list is not a dispatch table."),

    # ---- vacuity probes: documented behaviour, not defects to hide --------
    ("V01", "T6.B", "Scout Track.md", blk("T6.B"), vault(SCOUT), MATCH,
     "`{{dispatch table}}` is a bare hole.  Under open world it matches, and binds "
     "the whole file.  Recorded so the vacuity is visible rather than assumed away."),
    ("V02", "T6.B", "(empty document)", blk("T6.B"), lambda: "", MATCH,
     "Same hole against nothing.  A stencil that is one variable is unfalsifiable."),

    # ---- contingent: the verdict turns on a question the spec has not settled
    ("C01", "T1.A", "HERMES Backlog.md", blk("T1.A"), vault(HERMES), CONTINGENT,
     "T1 Overview: 'Section *order* is also unstated'.  The live file today runs "
     "Notes / Ready / Next / Later / Now while T1.A and the 2026-08-04 block both "
     "run Ready / Notes / …  Order-sensitive reading: NO MATCH.  Order-free: MATCH."),
]

FOLDER_PAIRS = [
    ("F01", "T5.A", "SYS/SYS Catalog/Computer/",
     lambda: C.fenced_tree("T5.A"), "SYS/SYS Catalog/Computer", {}, False, MATCH,
     "T5.b: two live members, one of them a phrase with spaces — the case for "
     "greedy binding between literals."),
    ("F02", "T2.A", "templates/log/",
     lambda: C.fenced_tree("T2.A"),
     "SYS/Bespoke/Skill Agent/dans-anchor-system/templates/log", {}, False, MATCH,
     "T2.A is 'the shipped folder, untouched' — it matches itself."),
    ("F03", "T2.A", "SYS/Staff/Atticus/ATT Log/ (single-brace read as a variable)",
     lambda: C.fenced_tree("T2.A"), "SYS/Staff/Atticus/ATT Log",
     {"slug": "ATT"}, True, MATCH,
     "An instantiated Log folder.  `{slug} Log.md` binds once; the dated member is "
     "free, so zero of them is permitted — which is why the one dated file present, "
     "`2026-07-20 Agent naming brainstorm.md`, can violate the naming and still pass."),
    ("F04", "T2.A", "SYS/Staff/Atticus/ATT Log/ (grammar exactly as written)",
     lambda: C.fenced_tree("T2.A"), "SYS/Staff/Atticus/ATT Log", {}, False, NO,
     "STEN Language defines only `{{NAME}}` as a variable, so `{slug}` is a literal "
     "and matches no real file.  T2.A cannot match any instantiated Log folder."),
]


def run_pairs(verbose: bool):
    rows = []
    skipped = []
    for pid, sl, tl, sget, tget, expect, why in PAIRS:
        s_txt, t_txt = sget(), tget()
        if s_txt is None or t_txt is None:
            skipped.append((pid, f"{sl} × {tl}"))
            continue
        r = M.match(s_txt, t_txt)
        actual = MATCH if r.ok else NO
        rows.append((pid, f"{sl} × {tl}", expect, actual, why, r))
    for pid, sl, tl, mget, folder, env, sbv, expect, why in FOLDER_PAIRS:
        r = M.match_folder(mget(), C.listdir(folder), env=env,
                           single_brace_vars=sbv)
        actual = MATCH if r.ok else NO
        rows.append((pid, f"{sl} × {tl}", expect, actual, why, r))

    if skipped:
        print(f"\n  SKIPPED {len(skipped)} pair(s) — no vault-paths.local.json; "
              f"these are NOT counted as passing:")
        for pid, name in skipped:
            print(f"    - {pid}  {name}")

    tp = tn = fp = fn = 0
    misses, contingent = [], []
    for pid, name, expect, actual, why, r in rows:
        if expect == CONTINGENT:
            contingent.append((pid, name, actual, why))
            continue
        if expect == MATCH and actual == MATCH:
            tp += 1
        elif expect == NO and actual == NO:
            tn += 1
        elif expect == NO and actual == MATCH:
            fp += 1
            misses.append((pid, name, expect, actual, why, r))
        else:
            fn += 1
            misses.append((pid, name, expect, actual, why, r))

    print("\n=== corpus verdicts ===")
    for pid, name, expect, actual, why, r in rows:
        mark = "ok " if expect == actual else ("·· " if expect == CONTINGENT else "XX ")
        print(f"{mark}{pid}  {name:<52} expected {expect:<10} got {actual}")
        if verbose or expect not in (actual, CONTINGENT):
            print(f"       why: {why}")
            for f in r.failures:
                print(f"       ! {f}")

    n = tp + tn + fp + fn
    print("\n=== confusion matrix ===")
    print(f"  scored pairs: {n}   (+{len(contingent)} contingent, unscored)")
    print(f"                       matcher says MATCH   matcher says NO MATCH")
    print(f"  human says MATCH     {tp:>6} (hit)          {fn:>6} (FALSE NEGATIVE)")
    print(f"  human says NO MATCH  {fp:>6} (FALSE POS)    {tn:>6} (hit)")

    if contingent:
        print("\n=== contingent (verdict turns on an unsettled grammar question) ===")
        for pid, name, actual, why in contingent:
            print(f"  {pid}  {name}\n       matcher (order-sensitive) says {actual}\n       {why}")

    if misses:
        print("\n=== every cell that is not a hit ===")
        for pid, name, expect, actual, why, r in misses:
            print(f"  {pid}  {name}: expected {expect}, got {actual}")
    return not misses


def run_adversarial():
    """Near-misses built by MUTATING real corpus bytes.

    The corpus negatives are all obviously-different documents, which a matcher
    that says yes to almost anything would still pass.  These are one-byte-class
    edits to real specimens: each must flip the verdict.  Reported separately
    from the corpus matrix, because a mutated document is not a vault instance.
    """
    print("\n=== adversarial near-misses (mutations of real corpus bytes) ===")
    cases = [
        ("A01", "T3.a with LOG no longer a heading at all",
         B["T3.A"], B["T3.a"].replace("# LOG", "LOG", 1), False),
        ("A01b", "T3.a's H1 LOG against an anchor whose floor is H2",
         B["T3.A"].replace("# ... LOG", "## ... LOG"), B["T3.a"], False),
        ("A02", "T3.a entry heading with a hyphen where the em-dash was",
         B["T3.A"], B["T3.a"].replace(" — ", " - "), False),
        ("A03", "T3.a entry heading with ONE space where T3.A demands two",
         B["T3.A"], B["T3.a"].replace("Mon  SENT", "Mon SENT"), False),
        ("A04", "T6.a row with one space before the middle pipe",
         B["T6.A"], B["T6.a"].replace("]]  |", "]] |"), False),
        ("A05", "T6.a with the identity row deleted",
         B["T6.A"], "\n".join(B["T6.a"].split("\n")[1:]), False),
        ("A06", "T7.b with the RULESET heading text altered",
         B["T7.A"], B["T7.b"].replace("# RULESET R-facet-spec", "# Ruleset"), False),
        ("A07", "T1.a with `## Later` removed",
         B["T1.A"], B["T1.a"].replace("## Later\n\n", ""), False),
        ("A08", "T3.a unchanged (control — the mutations' baseline must pass)",
         B["T3.A"], B["T3.a"], True),
        ("A09", "T3.a with U+00A0 substituted for the two ASCII spaces",
         B["T3.A"], B["T3.a"].replace("Mon  SENT", "Mon  SENT"), True),
    ]
    bad = []
    for aid, name, s, d, want in cases:
        got = M.match(s, d).ok
        mark = "ok " if got == want else "XX "
        if got != want:
            bad.append((aid, name, want, got))
        print(f"  {mark}{aid}  {name:<58} expected "
              f"{'MATCH' if want else 'NO MATCH':<9} got "
              f"{'MATCH' if got else 'NO MATCH'}")
    if bad:
        print("  --- the matcher is looser (or tighter) than the language says:")
        for aid, name, want, got in bad:
            print(f"      {aid} {name}: wanted {want}, got {got}")
    return not bad


def run_mode_experiments():
    """Measure the two grammar questions instead of arguing them."""
    print("\n=== experiment 1: variable extent ===")
    print("STEN Language recommends (A): 'a variable reaches until the next literal")
    print("the stencil names.'  Read literally, a trailing variable on a line spans")
    print("into the following lines.  Run every scored document pair both ways:")
    flips = []
    for pid, sl, tl, sget, tget, expect, why in PAIRS:
        a = M.match(sget(), tget())
        b = M.match(sget(), tget(), extent="strict-a")
        if a.ok != b.ok:
            flips.append((pid, f"{sl} × {tl}", a.ok, b.ok))
    print(f"  {len(flips)} of {len(PAIRS)} pairs change verdict under the literal reading:")
    for pid, name, a, b in flips:
        print(f"    {pid}  {name}: line-wise={'MATCH' if a else 'NO MATCH'}  "
              f"strict-(A)={'MATCH' if b else 'NO MATCH'}")

    print("\n=== experiment 2: many-by-variable as [0+] ===")
    print("If a pattern holding a free variable may match ZERO times, an item can")
    print("never fail.  Re-run every pair the corpus says must NOT match:")
    broken = []
    for pid, sl, tl, sget, tget, expect, why in PAIRS:
        if expect != NO:
            continue
        r = M.match(sget(), tget(), multiplicity="min0free")
        if r.ok:
            broken.append((pid, f"{sl} × {tl}"))
    nos = sum(1 for p in PAIRS if p[5] == NO)
    print(f"  {len(broken)} of {nos} required-failures become MATCH under [0+]:")
    for pid, name in broken:
        print(f"    {pid}  {name}")

    print("\n=== experiment 3: what T6.A cannot stop ===")
    dkt = C.read(DKT)
    occ = M.count_occurrences("| {{LEFT}}  | {{RIGHT}} |", dkt)
    lines = M.normalize_lines(dkt)
    sep = next(i for i, l in enumerate(lines) if l == "| --- | |")
    above = sum(1 for i, _ in occ if i < sep)
    below = sum(1 for i, _ in occ if i > sep)
    print(f"  DKT Track.md: T6.A's row pattern matches {len(occ)} lines — "
          f"{above} above the `| --- | |` separator (line {sep + 1}) and "
          f"{below} below it, inside the electric zone HookAnchor recomputes.")
    return flips, broken, (len(occ), above, below)


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
    ok = run_pairs(verbose)
    adv = run_adversarial()
    run_mode_experiments()
    green = ok and adv and not failed
    print("\n" + ("SUITE GREEN" if green else "SUITE RED"))
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
