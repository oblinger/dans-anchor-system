#!/usr/bin/env python3
"""test-f314-exceptions.py — F314: a checked rule can be deviated from at a named
target, but only through a graded row in `{slug} Track/{slug} Exceptions.md`.

The defect this guards: `R-exception-discipline` has stated the shape since
2026-07-06 and `Warden Exceptions.md` has recorded three real deviations against
it, but NOTHING READ EITHER — `audit-plan.py` had no exception concept across
6,626 lines. A discipline with no enforcement surface is the shape this whole
feature exists to close, so the assertions below are about the ENGINE, never
about the prose.

Five properties, each one a way the mechanism could look wired while being inert:

  1. A graded row suppresses the named rule at the named target.
  2. An UNGRADED row (`?` — the agent's proposal) suppresses NOTHING. This is the
     approval gate; if it leaks, the agent grants itself every exception.
  3. A row whose target does not match still fails. A target glob that silently
     widened to "everything" would be indistinguishable from a working mechanism
     on any fixture with one file.
  4. `except` is counted in its own bucket and printed unconditionally, so a
     corpus with forty exceptions never reads like one with none.
  5. A malformed row is REPORTED, never silently dropped — the failure mode where
     a typo in the rule id makes an exception quietly stop applying.

Self-contained: builds a fixture anchor in tmp, no vault I/O."""
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


ap = _load("audit_plan_f314", HERE / "audit-plan.py")

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL {label}\n       got  {got!r}\n       want {want!r}")


HEADER = "| EX | Rule | Target | Grade | Justification |\n|---|---|---|---|---|\n"


def build_anchor(td, rows):
    """An anchor whose one doc fails `regex_present`, plus an exceptions table."""
    root = Path(td)
    (root / ".anchor").write_text("slug: FIX\n", encoding="utf-8")
    doc = root / "FIX Thing.md"
    doc.write_text("# FIX Thing\nno sentinel here.\n", encoding="utf-8")
    other = root / "FIX Other.md"
    other.write_text("# FIX Other\nalso no sentinel.\n", encoding="utf-8")
    if rows is not None:
        trk = root / "FIX Track"
        trk.mkdir(exist_ok=True)
        (trk / "FIX Exceptions.md").write_text(
            "# FIX Exceptions\nAccepted deviations.\n\n" + HEADER + rows,
            encoding="utf-8")
    return root, doc, other


def plan_for(root, targets):
    return {"anchor_root": str(root),
            "groupings": [{"rules": [{
                "id": "R-progressive-03",
                "check": "regex_present ^SENTINEL$",
                "targets": [p.name for p in targets],
                "_target_paths": [str(p) for p in targets]}]}]}


def statuses(report):
    return [r["status"] for r in report["results"]]


# ── 1. no table at all — the rule fails, and `except` is still printed ───────

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(td, None)
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("without an exceptions table the rule fails", statuses(rep), ["fail"])
    check("`except` is present in the counts even at zero",
          rep["counts"].get("except"), 0)
    check("the rendered header prints the except count unconditionally",
          "except 0" in ap.render_verdicts(rep), True)


# ── 2. a graded row suppresses that rule at that target ─────────────────────

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Thing.md | B | deliberate. |\n")
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("a graded row rewrites fail -> except", statuses(rep), ["except"])
    check("the excepted finding is counted, not dropped",
          rep["counts"].get("except"), 1)
    check("an excepted finding is NOT counted as a pass",
          rep["counts"].get("pass"), 0)
    check("the EX handle rides along in the detail",
          "EX001" in rep["results"][0]["detail"], True)


# ── 3. `?` is a proposal, not an approval ───────────────────────────────────

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Thing.md | ? | proposed, unapproved. |\n")
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("an ungraded (`?`) row suppresses nothing", statuses(rep), ["fail"])

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Thing.md |  | grade cell empty. |\n")
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("an empty grade cell suppresses nothing", statuses(rep), ["fail"])


# ── 4. the target actually scopes it ────────────────────────────────────────

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Thing.md | A | scoped to one doc. |\n")
    rep = ap.execute_plan(plan_for(root, [doc, other]), None)
    check("the exception applies to its target and not its sibling",
          statuses(rep), ["except", "fail"])

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | ** | A | anchor-wide, deliberately. |\n")
    rep = ap.execute_plan(plan_for(root, [doc, other]), None)
    check("`**` is how an anchor-wide exception is written",
          statuses(rep), ["except", "except"])

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-99 | FIX Thing.md | A | wrong rule id. |\n")
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("a row naming a different rule does not suppress", statuses(rep), ["fail"])


# ── 5. malformed rows are reported, never silently dropped ──────────────────

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 |  | A | target cell empty. |\n"
            "| EX002 | R-progressive-03 | FIX Thing.md | A |  |\n"
            "| EX003 | R-progressive-03 | FIX Thing.md | Z | bad grade. |\n")
    rows, declined, problems = ap.load_exceptions(root)
    check("no malformed row is admitted", rows, [])
    check("a malformed row is not quietly filed as merely declined", declined, [])
    check("every malformed row is reported", len(problems), 3)
    check("the report names the offending EX handle",
          all(any(h in p for p in problems) for h in ("EX001", "EX002", "EX003")),
          True)
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("a malformed table suppresses nothing", statuses(rep), ["fail"])


# ── 6. only a `fail` is excepted — never an error, never a pass ─────────────

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-broken-01 | FIX Thing.md | A | anchor-wide. |\n")
    plan = {"anchor_root": str(root),
            "groupings": [{"rules": [{
                "id": "R-broken-01",
                "check": "no_such_checker_exists",
                "targets": [doc.name], "_target_paths": [str(doc)]}]}]}
    rep = ap.execute_plan(plan, None)
    check("an exception never rewrites a checker error", statuses(rep), ["error"])


# ── 7. a stale exception (matching no finding) is surfaced ──────────────────

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Gone.md | A | doc was deleted. |\n")
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("an exception that matched nothing is reported as stale",
          rep.get("stale_exceptions"), ["EX001"])


# ── 8. the on-write path honors the table BEFORE the fixer runs ─────────────
#
# The sharp edge: a rule carrying a `fix::` would otherwise auto-repair a
# document that has an approved deviation, erasing on the next save the very
# thing the exception records. The exception has to win over the fixer, not
# merely over the message.

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Thing.md | A | deliberate. |\n")
    before = doc.read_text(encoding="utf-8")
    plan = {"anchor_root": str(root),
            "groupings": [{"rules": [{
                "id": "R-progressive-03",
                "check": "regex_present ^SENTINEL$",
                "fix": "md_trailing_ws",
                "targets": [doc.name], "_target_paths": [str(doc)]}]}]}
    rep = ap.execute_on_write(plan, None)
    check("on-write: an excepted fail raises no message", rep["messages"], [])
    check("on-write: the fixer does not run on an excepted target", rep["fixed"], [])
    check("on-write: the deviation is reported, not silent",
          [e["handle"] for e in rep["excepted"]], ["EX001"])
    check("on-write: the file is untouched", doc.read_text(encoding="utf-8"), before)

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Thing.md | ? | proposed. |\n")
    plan = {"anchor_root": str(root),
            "groupings": [{"rules": [{
                "id": "R-progressive-03",
                "check": "regex_present ^SENTINEL$",
                "targets": [doc.name], "_target_paths": [str(doc)]}]}]}
    rep = ap.execute_on_write(plan, None)
    check("on-write: a proposed (`?`) row still raises the message",
          [m["rule"] for m in rep["messages"]], ["R-progressive-03"])


# ── 9. the grade is a scale, not a rubber stamp: A-C suppress, D and below do not ──
#
# Dan 2026-08-08: "we just auto fail if it's got a rating of D or lower or just
# not there." Before this, every letter A-F did the same thing, which made the
# column a binary wearing a scale's clothes and left no way to say "I read this
# and the answer is no" except to delete the row — losing the record of why the
# deviation was ever proposed, so the next agent proposes it again.

for grade, suppresses in (("A", True), ("B", True), ("C", True),
                          ("D", False), ("E", False), ("F", False)):
    with tempfile.TemporaryDirectory() as td:
        root, doc, other = build_anchor(
            td, f"| EX001 | R-progressive-03 | FIX Thing.md | {grade} | judged. |\n")
        rep = ap.execute_plan(plan_for(root, [doc]), None)
        check(f"grade {grade} {'suppresses' if suppresses else 'does NOT suppress'}",
              statuses(rep), ["except"] if suppresses else ["fail"])

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Thing.md | D | not good enough. |\n")
    rows, declined, problems = ap.load_exceptions(root)
    check("a D-graded row is well-formed, not an error", problems, [])
    check("a D-graded row is not admitted", rows, [])
    check("a D-graded row is kept as a declined record", [d["handle"] for d in declined],
          ["EX001"])
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("a refused row is reported, never silently inert",
          [d["handle"] for d in rep["declined_exceptions"]], ["EX001"])
    check("a refused row is NOT reported as stale — it did exactly what it says",
          rep.get("stale_exceptions"), [])
    check("the verdict render names the refusal",
          "EX001" in ap.render_verdicts(rep) and "below the C floor" in
          ap.render_verdicts(rep), True)


# ── 10. `confirm:: user` — the agent may not except a rule on its own say-so ──
#
# The gate is the grade, because a grade is the user's act. So an ungraded row
# against a confirm-rule is a table waiting on a conversation, and it goes RED
# until the conversation happens. Without this, "ask me first" is a sentence in a
# document that reads identically whether or not anyone obeys it — the exact
# failure R-exception-discipline itself spent a month demonstrating.

def exc_file(root):
    return root / "FIX Track" / "FIX Exceptions.md"


# The live catalog is the authority on which rules carry the marker; asserting it
# here is what makes the marker's disappearance a test failure rather than a
# silent loss. F308 M2 moves these rules into `R-spine` — when it does, the
# marker moves with them and this tuple is updated in the same pass.
SPINE_RULES = ("R-progressive-01", "R-progressive-03", "R-progressive-04")
for rid in SPINE_RULES:
    check(f"{rid} (spine) requires user confirmation",
          ap.rule_requires_user_confirmation(rid), True)
check("a rule with no marker does not require confirmation",
      ap.rule_requires_user_confirmation("R-progressive-02"), False)
check("an unresolvable rule id does not silently become a confirm-rule",
      ap.rule_requires_user_confirmation("R-nonexistent-01"), False)

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Thing.md | ? | proposed by the agent. |\n")
    status, detail = ap.chk_exceptions_table_wellformed(exc_file(root), root, [])
    check("an ungraded row against a confirm-rule fails the table", status, "fail")
    check("the failure names the row and the reason",
          "EX001" in detail and "confirm" in detail, True)

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Thing.md | B | user graded it. |\n")
    status, detail = ap.chk_exceptions_table_wellformed(exc_file(root), root, [])
    check("a graded row against a confirm-rule passes", status, "pass")

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-03 | FIX Thing.md | D | user refused it. |\n")
    status, detail = ap.chk_exceptions_table_wellformed(exc_file(root), root, [])
    check("a REFUSED row against a confirm-rule also passes the table — the "
          "conversation happened and the answer was no", status, "pass")
    check("the table reports the non-suppressing row rather than reading clean",
          "not suppressing" in detail, True)

with tempfile.TemporaryDirectory() as td:
    root, doc, other = build_anchor(
        td, "| EX001 | R-progressive-02 | FIX Thing.md | ? | proposed by the agent. |\n")
    status, detail = ap.chk_exceptions_table_wellformed(exc_file(root), root, [])
    check("an ungraded row against an ordinary rule is fine — the agent may "
          "propose freely where the rule does not demand a conversation", status, "pass")


print(f"test-f314-exceptions: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
