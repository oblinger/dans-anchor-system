#!/usr/bin/env python3
"""T035 — the ownership-gate family gets ruleset parity: R-backlog-08 and -09.

`[User]` shipped with F259 carrying a mint-time gate (`state … --status User`
refuses without `--why-user-action`) and an audit mirror (`audit-q` C51). It
never got a ruleset rule, so [[SKA groom]] listed six groomed states while
`R-backlog`'s own table listed five — the one bracket whose entire meaning is
*a person must act* was the only groomed state with no stated body contract.
That is the T552 parity shape: a contract enforced by two scripts and absent
from the prose, with nothing able to notice the drift.

What this file protects, in the order the checker can break:

  §1  the rule fires on a bare `[User]` row, and names it as such;
  §2  it does NOT fire once the `- **User:**` sub-bullet is there;
  §3  every OTHER bracket is untouched — the failure mode of a new
      bracket-keyed check is over-reach, not under-reach;
  §4  the count-prefixed `[2 User]` form is recognised, matching the
      `(?:\\d+\\s+)?` prefix R-backlog-05 already accepts on `[Questions]`;
  §5  a bracket that merely STARTS with `User` is not a `[User]` row —
      `fullmatch`, not `startswith`, because `[User]` has no sub-forms and a
      prefix match would silently claim any future `[User-something]`;
  §6  NO doc-side `user::` exemption — the mirror of R-backlog-02's `next::`
      escape, which must not be granted here because nothing writes the field;
  §7  ruleset parity — the rule, its check ref, its mend, and the table row.

Run: python3 test-t035-ownership-gate-rules.py
"""
import importlib.machinery
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
RULESET = HERE.parent.parent.parent / "rulesets" / "R-backlog.md"


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


ap = _load("audit_plan_t035", HERE / "audit-plan.py")

FAILURES = []
HEAD = "---\ndescription: fixture\n---\n\n# Demo Backlog\n\n## Now\n\n"


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def run(rows):
    """Write a one-anchor backlog holding `rows` and return (status, detail)."""
    td = tempfile.mkdtemp()
    root = Path(td)
    (root / ".anchor").write_text("slug: Demo\n", encoding="utf-8")
    trk = root / "Demo Track"
    trk.mkdir()
    f = trk / "Demo Backlog.md"
    f.write_text(HEAD + rows, encoding="utf-8")
    return ap.chk_backlog_user_action_named(f, root, None)


BARE = "- **T001 — Rotate the API key** [User] — the old key was revoked. ^T001\n"
WHY_ACTION = " \u00b7 *why-user-action: the console login is Dan's and the agent holds no session*"
ACTION = ("  - **User:** Mint a fresh key at https://console.anthropic.com/settings/keys "
          "and write it into `~/.config/anthropic/api_key`, then say 'key is in'.")
NAMED = BARE.rstrip("\n") + "\n" + ACTION + WHY_ACTION + "\n"
UNJUSTIFIED = BARE.rstrip("\n") + "\n" + ACTION + "\n"

print("1. A bare [User] row fails, and the message names what is missing")
st, detail = run(BARE)
check("verdict is fail", st, "fail")
# Computed, not hard-coded: a later edit to HEAD would silently rot a
# literal line number into an assertion that passes for the wrong reason.
ROW_LINE = len(HEAD.splitlines()) + 1
check("...names the row's line", f"line {ROW_LINE}" in detail, True)
check("...names the missing sub-bullet", "`- **User:**`" in detail, True)
check("...says what the row failed to do", "names no user-only action" in detail, True)

print("2. Both clauses are required — naming the action is not enough on its own")
check("action + why-user-action passes", run(NAMED)[0], "pass")
# The second clause is what C51 never checked. An action can be perfectly
# concrete and still be work the agent was simply too incurious to attempt;
# only the justification catches that, so a rule that stopped at clause 1
# would mirror the audit and miss half the F259 gate.
st2, d2 = run(UNJUSTIFIED)
check("...a named action with NO why-user-action still fails", st2, "fail")
check("...and is diagnosed as the missing justification, not a missing action",
      "why-user-action" in d2 and "no `- **User:**`" not in d2, True)

print("3. No other bracket is touched — over-reach is the real risk here")
# Each of these lacks a `- **User:**` sub-bullet. If any fires, the rule has
# stopped being about `[User]` and started being about every row in the vault.
for br in ("Ready", "Active", "Questions", "Blocked", "Blocked F302",
           "Waiting 2026-09-03", "Watching 7d", "Verify", "Verify-by 2026-09-01",
           "Designing", "Done"):
    row = f"- **T002 — Some other row** [{br}] — body text that is long enough. ^T002\n"
    check(f"[{br}] does not fire", run(row)[0], "pass")

print("4. The count-prefixed form is recognised, as on [Questions]")
st, detail = run(BARE.replace("[User]", "[2 User]"))
check("[2 User] fires", st, "fail")
check("...and echoes the bracket it saw", "[2 User]" in detail, True)
check("[2 User] passes when fully formed", run(NAMED.replace("[User]", "[2 User]"))[0], "pass")

print("5. A bracket that merely STARTS with User is not a [User] row")
# `fullmatch`, not `startswith`. `[Verify*]` legitimately has sub-forms
# (`Verify-by …`) so R-backlog-04 prefix-matches; `[User]` has none, and a
# prefix match would silently annex any bracket coined later.
check("[Users] does not fire", run(BARE.replace("[User]", "[Users]"))[0], "pass")
check("[User-action] does not fire", run(BARE.replace("[User]", "[User-action]"))[0], "pass")

print("6. There is NO doc-side `user::` exemption (the R-backlog-02 mirror)")
# R-backlog-02 lets a derived row off when its arrow-linked doc carries
# `next::`. Granting the same here would exempt everything, because no writer
# produces a `user::` field — the exemption would read as coverage and provide
# none. Two halves: the field does not exist upstream, and planting one anyway
# does not buy the row a pass.
be = _load("backlog_edit_t035",
           HERE.parent.parent / "workflow" / "scripts" / "backlog-edit.py")
check("backlog-edit exposes read_doc_next", hasattr(be, "read_doc_next"), True)
check("...and no read_doc_user beside it", hasattr(be, "read_doc_user"), False)

td = tempfile.mkdtemp()
root = Path(td)
(root / ".anchor").write_text("slug: Demo\n", encoding="utf-8")
(root / "Demo Doc.md").write_text(
    "# Demo Doc\nuser:: go click the dialog\nnext:: do the thing\n", encoding="utf-8")
trk = root / "Demo Track"
trk.mkdir()
bl = trk / "Demo Backlog.md"
bl.write_text(
    HEAD + "- **T001 — Rotate the API key** [User] — → [[Demo Doc|T001]] — body. ^T001\n",
    encoding="utf-8")
st, _ = ap.chk_backlog_user_action_named(bl, root, None)
check("a doc-side `user::` does NOT excuse the row", st, "fail")

print("7. R-backlog-09 — a surfaced Verify is user-grade and names its faculty")
WHY = " \u00b7 *why-user: taste \u2014 whether the strip reads right is Dan's own judgement*"
GOOD = ("- **T003 \u2014 Colour split** [Verify] \u2014 shipped 2026-08-01. ^T003\n"
        "  - **Verify:** Looking at the Drift strip now, can you tell a WORKING tab "
        "apart from a WAITING tab at a glance?" + WHY + "\n")


def run9(rows):
    td = tempfile.mkdtemp()
    root = Path(td)
    (root / ".anchor").write_text("slug: Demo\n", encoding="utf-8")
    trk = root / "Demo Track"
    trk.mkdir()
    f = trk / "Demo Backlog.md"
    f.write_text(HEAD + rows, encoding="utf-8")
    return ap.chk_backlog_verify_is_user_grade(f, root, None)


check("a taste question with why-user passes", run9(GOOD)[0], "pass")
check("...the same question WITHOUT why-user fails",
      run9(GOOD.replace(WHY, ""))[0], "fail")
st, d = run9(GOOD.replace(WHY, ""))
check("...and the message names what is missing", "why-user" in d, True)

# Half 1: machine phrasing is refused even WITH a justification. This is the
# assertion that keeps the two halves from collapsing into one — an
# implementation that just looked for the annotation would pass this and be
# wrong in exactly the way F240's gate exists to prevent.
MECH = ("- **T004 \u2014 Hook wiring** [Verify] \u2014 shipped. ^T004\n"
        "  - **Verify:** Did the PostToolUse hook fire on the last write?" + WHY + "\n")
check("a machine-event question fails DESPITE why-user", run9(MECH)[0], "fail")
check("...and is diagnosed as agent-grade, not as missing a faculty",
      "machine event" in run9(MECH)[1], True)

# The borrow, not a copy (T120). If this ever becomes a local re-implementation
# the checker can drift out of agreement with the writer that mints the rows.
be9 = ap._be_mod()
check("the phrasing test is borrowed from backlog-edit",
      ap.chk_backlog_verify_is_user_grade.__doc__ is not None
      and hasattr(be9, "is_mechanical_verify"), True)

print("8. R-backlog-09 stays inside its scope")
PROBE = ("- **T005 \u2014 Soak** [Watching 7d] \u2014 expires 2026-09-01. ^T005\n"
         "  - **Probe:** once `fired` reaches 21 \u2014 re-run the soak counts.\n")
check("a Watching row with only a Probe is untouched", run9(PROBE)[0], "pass")
for br in ("Ready", "Active", "Questions", "User", "Blocked", "Done"):
    row = (f"- **T006 \u2014 Other** [{br}] \u2014 body text long enough here. ^T006\n"
           "  - **Verify:** stray verify text with no annotation at all.\n")
    check(f"[{br}] is out of scope for -09", run9(row)[0], "pass")
check("R-backlog-09 is registered",
      ap.registry().get("backlog_verify_is_user_grade") is not None, True)

print("9. R-fct-features-05 — a pending Q has earned its way to the user")
FEAT_RULESET = HERE.parent.parent.parent / "rulesets" / "R-fct-features.md"
DOC_HEAD = "# [[Demo]] \u00b7 F1 \u2014 Demo\nOrientation line.\n\n## Open Questions\n<!-- state:q 00 -->\n\n"


def runF(qblock):
    td = tempfile.mkdtemp()
    root = Path(td)
    (root / ".anchor").write_text("slug: Demo\n", encoding="utf-8")
    d = root / "Demo Features"
    d.mkdir()
    f = d / "Demo001 - Demo.md"
    f.write_text(DOC_HEAD + qblock + "\n## Summary\n\nbody.\n", encoding="utf-8")
    return ap.chk_features_question_why_ask(f, root, None)


OPTS = ("  - **(A)** do it one way.\n  - **(B)** do it the other way.\n")
LEAN = "- **Recommendation:** Lean (A) \u2014 it is simpler."
NONE_REC = "- **Recommendation:** None \u2014 genuinely no basis to choose."
WHY_ASK = " \u00b7 *why-ask: the schema is interface-sticky once written*"

q_lean_bare = "- **Q1 \u2014 Which frontmatter schema?** \u2014 context here. ^F1-Q1\n" + OPTS + LEAN + "\n"
q_lean_ok = q_lean_bare.replace(LEAN + "\n", LEAN + WHY_ASK + "\n")
q_none = q_lean_bare.replace(LEAN, NONE_REC)

st, d = runF(q_lean_bare)
check("a Lean with no why-ask fails", st, "fail")
check("...and the message names the annotation", "why-ask" in d, True)
check("the same Q passes once why-ask is present", runF(q_lean_ok)[0], "pass")
# The asymmetry IS the design: the rule taxes confident asks, never uncertain
# ones. A checker that flagged `None` would push agents to delete their
# recommendation rather than justify it.
check("Recommendation: None passes untouched", runF(q_none)[0], "pass")

# A resolved Q is not pending — this is the slicing borrowed from audit-q, and
# getting it wrong would nag questions that have already been answered.
resolved = ("### Resolved\n\n" + q_lean_bare)
check("a Q under ### Resolved is not pending", runF(resolved)[0], "pass")
check("a doc with no Open Questions block passes", runF("")[0], "pass")
check("R-fct-features-05 is registered",
      ap.registry().get("features_question_why_ask") is not None, True)

ftext = FEAT_RULESET.read_text(encoding="utf-8")
m5 = re.search(r"### RULE R-fct-features-05\b.*?(?=\n### RULE |\n## |\Z)", ftext, re.S)
check("R-fct-features-05 exists", bool(m5), True)
if m5:
    b5 = m5.group(0)
    check("...wires the checker", "check:: features_question_why_ask" in b5, True)
    check("...wires a mend", "mend:: features-decide-or-justify" in b5, True)
    check("...says it is NOT merely C50 restated", "not merely `audit-q` C50" in b5, True)
    check("...names the reachability hole it closes", "never swept" in b5, True)
    check("...carries the measured arming figures",
          "87 clean, 0 agent-territory, 28" in b5, True)
    check("...has a Check pattern (R-ruleset-07)", "**Check pattern:**" in b5, True)
check("the -05 mend section exists", "### MEND features-decide-or-justify" in ftext, True)

print("10. The ruleset states it (the T552 parity discipline)")
text = RULESET.read_text(encoding="utf-8")
m = re.search(r"### RULE R-backlog-08\b.*?(?=\n### RULE |\n## |\Z)", text, re.S)
check("R-backlog-08 exists", bool(m), True)
if m:
    body = m.group(0)
    check("...wires the checker", "check:: backlog_user_action_named" in body, True)
    check("...wires a mend", "mend:: backlog-name-the-user-action" in body, True)
    check("...states the no-doc-escape decision", "no doc-side escape" in body.lower(), True)
    check("...names both other enforcement points",
          "--why-user-action" in body and "C51" in body, True)
    check("...states that it has two clauses", "two clauses" in body, True)
    check("...carries the measured arming figures for BOTH clauses",
          "29 of 29 named their action" in body and "29 of 29 carried" in body, True)
check("the mend section exists",
      "### MEND backlog-name-the-user-action" in text, True)

m9 = re.search(r"### RULE R-backlog-09\b.*?(?=\n### RULE |\n## |\Z)", text, re.S)
check("R-backlog-09 exists", bool(m9), True)
if m9:
    b9 = m9.group(0)
    check("...wires the checker", "check:: backlog_verify_is_user_grade" in b9, True)
    check("...wires a mend", "mend:: backlog-earn-the-surfacing" in b9, True)
    check("...states that machine phrasing is refused regardless",
          "regardless of the justification" in b9, True)
    check("...names the borrow rather than a copy", "borrowed, never re-implemented" in b9, True)
    check("...carries the measured arming figures",
          "48 clean, 0 machine-phrased, 8" in b9, True)
    check("...has a Check pattern (R-ruleset-07)", "**Check pattern:**" in b9, True)
check("the -09 mend section exists",
      "### MEND backlog-earn-the-surfacing" in text, True)
check("the checker is registered under that name",
      ap.registry().get("backlog_user_action_named") is not None, True)

# The table was the drifted copy — six groomed states in the skill, five here.
tbl = re.search(r"\n\| # \| Groomed state \|.*?\n\n", text, re.S)
check("the groomed-states table exists", bool(tbl), True)
if tbl:
    check("...now carries the [User] state", "**User-action**" in tbl.group(0), True)
    check("...and points it at this rule", "R-backlog-08" in tbl.group(0), True)
    check("...and still has all six states",
          len(re.findall(r"^\| \d+ \|", tbl.group(0), re.M)), 6)

print()
if FAILURES:
    print(f"test-t035-ownership-gate-rules: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t035-ownership-gate-rules: all checks pass")
