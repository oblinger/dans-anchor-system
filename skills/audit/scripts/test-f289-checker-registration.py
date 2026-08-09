#!/usr/bin/env python3
"""F289 — a corpus supplies its own checkers, and the mapping is checked both ways.

Where a `check::` ref found its implementation used to be engine policy: the fire
path loaded exactly one file at a path assembled from a hardcoded string inside
dans-anchor-system, and that file's `CHECKERS` dict was the whole vocabulary a
ref could name. A consumer handed the engine could write `check:: my_thing` and
had nowhere on disk to put `my_thing`. `import::` on the ruleset header is the
seam; `verify_registrations` is the check that the declaration cannot lie.

**The assertion that matters is `test_foreign_corpus_supplies_its_own_checker`.**
It builds a corpus root that is not dans-anchor-system at all, puts one checker
module in it, and asserts the verdict comes from THAT module — which is the whole
claim of the feature and the one thing a test inside the DAS tree can otherwise
fake, because DAS's own registry is ambiently in scope no matter what.

Second in weight is the ghost direction, and it is worth saying why it needs a
test rather than a sweep: it fails QUIETLY BY DESIGN. `_needs_judgment` decides
mechanical-vs-agent with a membership test, so a name that is not registered
misses, the rule is promoted to agent judgment, and `run_checker`'s `unknown
checker` error never runs because the rule never reaches it. T071 fixed eleven
ghosts once and the population regrew to eleven — that regrowth is the argument
for a check instead of another sweep.

    python3 test-f289-checker-registration.py
"""
import contextlib
import importlib.util
import io
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def raises(name, fn, frag):
    try:
        fn()
    except ap.CorpusError as e:
        check(name, frag in str(e), True)
        return
    except Exception as e:
        check(name, f"{type(e).__name__}: {e}", f"CorpusError containing {frag!r}")
        return
    check(name, "no exception", f"CorpusError containing {frag!r}")


def parse(text: str) -> dict:
    """Parse one RULESET block out of markdown, through the real parser."""
    blk = ap.extract_ruleset_block(text)
    assert blk is not None
    return ap.parse_ruleset_block(blk[0], ap.REPO_ROOT / "rulesets" / "R-fixture.md")


# ── the header field ────────────────────────────────────────────────────────

print("`import::` parses off the ruleset header")

rs = parse("# RULESET R-fixture\ninclude::\nimport:: a/b.py\nwhere:: `always`\n\nbody\n")
check("a single path", rs["imports"], ["a/b.py"])
check("...and the neighbouring fields still parse", (rs["includes"], rs["where"]), ([], "always"))

check("repeated lines accumulate — one module per line is the readable form",
      parse("# RULESET R-fixture\nimport:: a/b.py\nimport:: c/d.py\n\nbody\n")["imports"],
      ["a/b.py", "c/d.py"])
check("...and several on one line, comma- or space-separated",
      parse("# RULESET R-fixture\nimport:: a/b.py, c/d.py e/f.py\n\nbody\n")["imports"],
      ["a/b.py", "c/d.py", "e/f.py"])
check("a ruleset that declares none reports none, not None",
      parse("# RULESET R-fixture\ninclude::\n\nbody\n")["imports"], [])

# `import::` is a distinct key from `include::` because the two do wildly
# different things — one flattens rules into a trait, the other executes code —
# and a reader should not have to inspect a file extension to tell which.
rs = parse("# RULESET R-fixture\ninclude:: [[R-other]]\nimport:: a/b.py\n\nbody\n")
check("include:: and import:: do not bleed into each other",
      (rs["includes"], rs["imports"]), (["R-other"], ["a/b.py"]))


# ── the seam ────────────────────────────────────────────────────────────────

print("\nA foreign corpus supplies its own checkers")


def test_foreign_corpus_supplies_its_own_checker():
    """The claim, tested where it can't be satisfied by accident.

    REPO_ROOT is repointed at a throwaway tree, so nothing under
    dans-anchor-system is reachable by the corpus-root-relative path — the
    verdict can only have come from the module the fixture ruleset named."""
    real_root, real_reg, real_imported = ap.REPO_ROOT, ap._REGISTRY, dict(ap._IMPORTED)
    real_owner = dict(ap._REGISTRY_OWNER)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "checkers").mkdir()
        (root / "checkers" / "mine.py").write_text(
            "def _widget(target, anchor_root, args):\n"
            "    return ('fail', f'widget says {args[0] if args else \"hi\"}')\n"
            "CHECKERS = {'my_widget': _widget}\n", encoding="utf-8")
        ap.REPO_ROOT = root
        ap._REGISTRY, ap._IMPORTED, ap._REGISTRY_OWNER = None, {}, {}
        try:
            fixture = [{"name": "R-mine", "imports": ["checkers/mine.py"],
                        "rules": [{"id": "R-mine-01", "check": "my_widget", "fix": None}]}]
            ap.register_imports(fixture)
            check("the foreign module's checker is in the registry",
                  "my_widget" in ap.registry(), True)
            check("...and running the ref reaches THAT implementation",
                  ap.run_checker("my_widget loud", root, root),
                  ("fail", "widget says loud"))
            check("...with no engine edit: the ref resolves as mechanical, "
                  "so the rule is not promoted to agent judgment",
                  ap._needs_judgment({"tier": "checked", "check": "my_widget"}), False)
            rep = ap.verify_registrations(fixture)
            check("...and the ruleset's own declaration covers it — no warning",
                  (rep["ghosts"], rep["undeclared"]), ([], []))

            # Two modules, one name: first wins, and the clash is reported rather
            # than silently resolved — the same discipline F280 applies to mends.
            (root / "checkers" / "other.py").write_text(
                "def _w(target, anchor_root, args):\n    return ('pass', 'other')\n"
                "CHECKERS = {'my_widget': _w}\n", encoding="utf-8")
            two = fixture + [{"name": "R-other", "imports": ["checkers/other.py"],
                              "rules": [{"id": "R-other-01", "check": "my_widget", "fix": None}]}]
            rep = ap.verify_registrations(two)
            check("a name defined twice is reported",
                  len(rep["clashes"]) >= 1 and "my_widget" in rep["clashes"][0], True)
            check("...and first wins — the verdict is still the first module's",
                  ap.run_checker("my_widget", root, root)[1], "widget says hi")
        finally:
            ap.REPO_ROOT = real_root
            ap._REGISTRY, ap._IMPORTED = real_reg, real_imported
            ap._REGISTRY_OWNER = real_owner


test_foreign_corpus_supplies_its_own_checker()

print("\nA declaration the engine cannot honour is loud, not warned")

# An import that does not resolve silently empties a ruleset's whole vocabulary,
# and every rule in it then reads as agent-judgment work with nothing anywhere to
# say it was demoted. That is the failure mode this whole feature exists to end,
# so it raises rather than appending to a warnings list somebody may not print.
raises("a missing file raises CorpusError naming the path",
       lambda: ap._load_checker_module("nowhere/at/all.py"), "nowhere/at/all.py")

with tempfile.TemporaryDirectory() as td:
    _root = Path(td)
    (_root / "empty.py").write_text("x = 1\n", encoding="utf-8")
    (_root / "boom.py").write_text("raise ValueError('kaboom')\n", encoding="utf-8")
    _real = ap.REPO_ROOT
    ap.REPO_ROOT = _root
    try:
        raises("a module with no CHECKERS dict raises",
               lambda: ap._load_checker_module("empty.py"), "no CHECKERS dict")
        raises("...and a module that blows up on import raises with the cause",
               lambda: ap._load_checker_module("boom.py"), "kaboom")
    finally:
        ap.REPO_ROOT = _real

print("\nImporting audit-plan itself short-circuits to the live module")

# Re-executing audit-plan from disk would duplicate 5,000 lines of definitions
# and hand back checker functions that are not the ones the rest of the process
# holds — so a verdict cache keyed on identity, or a test that patches a checker,
# would quietly diverge from what actually ran.
_self = ap._load_checker_module("skills/audit/scripts/audit-plan.py")
check("the self-import returns the live CHECKERS object, not a fresh copy",
      _self[0] is ap.CHECKERS, True)
check("...and the live FIXERS alongside it — a module supplies both vocabularies",
      _self[1] is ap.FIXERS, True)


# ── both directions, on the real corpus ─────────────────────────────────────

print("\nThe real corpus: every ruleset that names a checker declares where it lives")

_rulesets, _seen, _warns = [], set(), []
for _u in ("R-doc", "R-anchor"):
    for _rs in ap.flatten_umbrella(_u, _warns):
        if _rs["name"] not in _seen:
            _seen.add(_rs["name"])
            _rulesets.append(_rs)
_reachable = len(_rulesets)
for _rs in ap.all_corpus_rulesets():
    if _rs["name"] not in _seen:
        _seen.add(_rs["name"])
        _rulesets.append(_rs)
REPORT = ap.verify_registrations(_rulesets)

# The scope distinction is load-bearing and was not obvious: flattening R-doc +
# R-anchor reaches 24 rulesets and the corpus holds 89. A ghost in the other 65
# costs nothing today because the rule never runs — but it is exactly the ref
# that will be wrong on the day something includes it.
check("the umbrella closure is a minority of the corpus, so the verification "
      "runs over the whole population", _reachable < len(_rulesets), True)

check("no ruleset's ref resolves only globally — every one names its own module",
      REPORT["undeclared"], [])
check("...and no name is defined twice", REPORT["clashes"], [])

# The conflation that produced a false ghost, asserted so it cannot come back.
check("a `fix::` ref resolves through FIXERS, not CHECKERS — `breadcrumb_position` "
      "is a registered fixer with no checker of that name",
      ("breadcrumb_position" in ap.fixer_registry()
       and "breadcrumb_position" not in ap.registry()), True)
check("...so it is not reported as a ghost",
      any("breadcrumb_position" in g for g in REPORT["ghosts"]), False)

# A ratchet, not a gate: the six below are pre-existing and each has a home. New
# ones must not join them silently, and closing one must shrink this list in the
# same commit — T074 did exactly that on 2026-08-02, taking the four
# `R-svg-jiggle-02..05` checks out by registering them.
#
# F289's design recorded ELEVEN ghosts and this list started as that eleven. Two
# corrections since, both measured:
#   - `R-doc-structure-01 — fix:: breadcrumb_position` was never a ghost. The
#     first cut checked `fix::` refs against CHECKERS; they resolve through
#     FIXERS, where `breadcrumb_position` has always been registered. 11 -> 10.
#   - T074 registered the four `svg_*` checks. 10 -> 6.
# The five `R-svg-jiggle-06..10` fixes stay: they are resolutions inside the
# repair loop, selected against a cost function and re-detected after each move,
# not standalone fixers the on-write hook could fire one at a time.
#
# The regrowth this check exists to catch then happened, and this is the record
# of it: [[R-rocks]] landed with nine `check::` refs and no implementations, and
# EIGHT of them showed up here as new ghosts (2026-08-07, T156). The ninth never
# reached the report — `RULE R-rocks-05` was headed `(checked, warn)`, which is
# not one of the four tiers `_RULE_RE` admits, so the parser skipped the heading
# and folded rule 05's `check::` onto rule 04. A ruleset can therefore lose a
# rule outright without losing a ref, which is worth knowing when this list next
# grows: count the refs in the FILE against the ids in the report. T156 wrote all
# nine checkers and fixed the tier, so the set is back to the frozen six.
KNOWN_GHOSTS = {
    "R-md-03": {"md_angle_brackets_backtick_only"},
    "R-svg-jiggle-06": {"slide_label_along_edge"},
    "R-svg-jiggle-07": {"flip_label_across_edge"},
    "R-svg-jiggle-08": {"nudge_box"},
    "R-svg-jiggle-09": {"shrink_arrowhead"},
    "R-svg-jiggle-10": {"try_widen"},
}
_got = {}
for _line in REPORT["ghosts"]:
    _rid, _rest = _line.split(" — ", 1)
    _got.setdefault(_rid, set()).add(_rest.split("'")[1])
check("the ghost population is exactly the frozen known set — a new one fails "
      "here rather than silently becoming a billed agent-judgment task",
      _got, KNOWN_GHOSTS)


print("\nThe live warden engine actually resolves what a name match only guesses at (T172)")

# Everything above compares two STRINGS — the name a rule declares against the
# name a module defines — and stops there. That is exactly the gap T172 found:
# `R-svg-jiggle-06..10` pass every check above (their `fix::` name matches a
# real name somewhere in the corpus' vocabulary) while `warden compile` printed
# "registered by no imported module" for all five, because name-matching and
# resolving are different questions and this file only ever asked the first
# one. Ask the ENGINE that actually runs on write — the live copy at
# ~/ob/grove/warden/engine, not dans-anchor-system's own divergent copy under
# warden/engine/ (T172 found the two differ; reconciling them is out of scope
# here) — by running its real corpus-mode compiler over this corpus and
# reading what it prints, the same way `warden compile` does.
_wc_path = Path.home() / "ob" / "grove" / "warden" / "engine" / "warden_compile.py"
_wc_spec = importlib.util.spec_from_file_location("wc", _wc_path)
wc = importlib.util.module_from_spec(_wc_spec)
_wc_spec.loader.exec_module(wc)
sys.path.insert(0, str(_wc_path.parent))
import warden_scan  # noqa: E402 — the live engine's own scan step, corpus-mode input

_ix_path = ap.REPO_ROOT / ".warden" / "rules-index.json"
_prior_bearing, _prior_seen = warden_scan.load_index(str(_ix_path))
_files, _seen, _ = warden_scan.build_index(str(ap.REPO_ROOT), _prior_bearing, _prior_seen, rescan=False)
_index = {"root": str(ap.REPO_ROOT), "files": _files, "seen": _seen}

_engine_err = io.StringIO()
with contextlib.redirect_stderr(_engine_err):
    wc.compile_corpus(ap.REPO_ROOT, _index, "all", "test-f289-resolution-check")
_engine_warnings = [ln for ln in _engine_err.getvalue().splitlines()
                    if "registered by no imported module" in ln]
_svg_engine_warnings = [ln for ln in _engine_warnings if "R-svg-jiggle" in ln]

check("the live warden engine's compile-time resolver prints ZERO "
      "'registered by no imported module' warnings for R-svg-jiggle — this is "
      "the assertion that would have failed on day one for R-svg-jiggle-06..10, "
      "before warden_compile.py's fix:: ref collection was corrected to match "
      "what compile_rule() actually wires (a fix:: only reaches the IR when "
      "its own rule also carries check::)",
      _svg_engine_warnings, [])

# R-md-03's `check:: md_angle_brackets_backtick_only` is a genuinely
# unregistered checker — a real, pre-existing, unrelated gap (no fix::
# involved at all), left exactly as found; T172 scoped this to the
# R-svg-jiggle fix:: resolution, not a corpus-wide checker sweep. Recorded
# so a future zero-warning ratchet does not have to rediscover it.
check("...and the one remaining corpus warning is the known, unrelated "
      "R-md-03 checker gap, not a regression of this fix",
      _engine_warnings, [ln for ln in _engine_warnings if "R-md-03" in ln])


def test_a_new_ghost_is_caught():
    """The falsification. A verification that never fires is not a verification,
    and the ghost check is the one that has to work: nothing else in the system
    produces any output at all when a ref misses."""
    fixture = [{"name": "R-typo", "imports": ["skills/audit/scripts/audit-plan.py"],
                "rules": [{"id": "R-typo-01", "check": "h1_presnt", "fix": None},
                          {"id": "R-typo-02", "check": "h1_present", "fix": None}]}]
    rep = ap.verify_registrations(fixture)
    check("a typo'd ref is reported as a ghost",
          len(rep["ghosts"]) == 1 and "h1_presnt" in rep["ghosts"][0], True)
    check("...and the correctly-spelled neighbour is not",
          any("h1_present'" in g for g in rep["ghosts"]), False)
    check("...and the message says what it costs — the rule becomes agent judgment",
          "agent judgment" in rep["ghosts"][0], True)


def test_extraction_safety_is_what_undeclared_measures():
    """The reason a purely global registry is not enough.

    A ruleset whose refs resolve only because a NEIGHBOUR declared the import is
    fine inside one corpus and broken the moment it is extracted into a new one —
    it breaks because its dependency was covered by a file it never named. The
    warning is the only thing that distinguishes the two situations, since both
    run identically."""
    declares = {"name": "R-a", "imports": ["skills/audit/scripts/audit-plan.py"],
                "rules": [{"id": "R-a-01", "check": "h1_present", "fix": None}]}
    freeloads = {"name": "R-b", "imports": [],
                 "rules": [{"id": "R-b-01", "check": "h1_present", "fix": None}]}
    rep = ap.verify_registrations([declares, freeloads])
    check("the freeloading ruleset is flagged", len(rep["undeclared"]), 1)
    check("...naming the ruleset, the ref, and why it is a problem",
          ("R-b" in rep["undeclared"][0] and "h1_present" in rep["undeclared"][0]
           and "only" in rep["undeclared"][0]), True)
    check("...while the declaring one is silent, though both resolve at runtime",
          any("R-a-01" in u for u in rep["undeclared"]), False)
    check("...and neither is a ghost — this is about the declaration, not the ref",
          rep["ghosts"], [])


test_a_new_ghost_is_caught()
test_extraction_safety_is_what_undeclared_measures()

print("\nThe orphan direction is surfaced for a human, not asserted")

# An uninvoked checker is either a rule waiting to be written or dead code, and
# only reading each one tells you which — so this asserts the report exists and
# is non-trivial, and deliberately does not freeze the number.
check("orphans are reported", len(REPORT["orphans"]) > 0, True)
check("...and every orphan is a real registered name",
      all(n in ap.registry() for n in REPORT["orphans"]), True)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
