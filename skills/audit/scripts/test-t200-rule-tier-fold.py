#!/usr/bin/env python3
"""test-t200-rule-tier-fold.py — a malformed tier must not silently disable the rule above it.

`_RULE_RE` admitted four tiers. A `RULE` heading it rejects is **skipped**, and a
skipped heading does not terminate the rule above it — so the `check::` line
beneath folds onto its predecessor, which then runs a checker that is not its
own and reports that verdict as its own.

That is not hypothetical. `R-rocks-03` (cardinality) ran `R-rocks-04`'s
name-expansion checker and answered *"name is 'R0001' — not an abbreviation,
nothing to expand"* — green on every rock group in the vault, never once
evaluated. It was the SECOND occurrence in the same ruleset: T156 records
`(checked, warn)` folding rule 05 onto rule 04 five days earlier. It recurs
because a malformed tier makes a rule invisible to the very checks that would
catch it — every other consumer reads PARSED rules, where the bad heading is
already gone.

Three things are pinned here, and the fold test is the one that matters:
  * `retired` / `governing` parse (both are live in the corpus);
  * neither is promoted to billed agent judgment — `_needs_judgment` is a
    MEMBERSHIP test, so admitting a tier without excluding it starts charging an
    LLM call for every retired rule on every audit;
  * `R-ruleset-06` (`all_rules_have_tier`) fails on a heading that would fold,
    and stays silent on the 37 Warden rules that share the `RULE` sentinel but
    belong to the other engine — in BOTH spellings, heading parenthetical and
    body field. Keying on one spelling alone produced 11 and then 8 false
    positives; neither was a defect count, each measured which spelling the
    checker had not yet learned.

Usage: python3 test-t200-rule-tier-fold.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = FAIL = 0


def _load():
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ap"] = m
    spec.loader.exec_module(m)
    return m


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS  {label}")
    else:
        FAIL += 1
        print(f"FAIL  {label}")


def tier_verdict(m, body):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "R-demo.md"
        p.write_text(body, encoding="utf-8")
        return m.chk_all_rules_have_tier(p, Path(td), None)


HEAD = "# RULESET R-demo\ninclude::\nwhere:: `**/*.md`\ndescription:: demo.\n\n"


def main():
    m = _load()

    # ---- 1. the six tiers parse -------------------------------------------
    for tier in ("checked", "sampled", "stated", "tracked", "retired", "governing"):
        h = f"### RULE R-demo-01 — a title ({tier})"
        check(m._RULE_RE.match(h) is not None, f"tier ({tier}) parses")

    # ---- 2. an unknown tier still does NOT parse — that is the guard's job --
    check(m._RULE_RE.match("### RULE R-demo-01 — a title (checked, warn)") is None,
          "unknown tier (checked, warn) still refused by _RULE_RE")

    # ---- 3. neither new tier is promoted to billed agent judgment ----------
    for tier in ("tracked", "retired", "governing"):
        check(m._needs_judgment({"tier": tier, "check": None}) is False,
              f"({tier}) rule is not sent to agent judgment")
    check(m._needs_judgment({"tier": "stated", "check": None}) is True,
          "(stated) rule with no checker DOES still need judgment (control)")

    # ---- 4. THE FOLD — the defect this whole file exists for ---------------
    # Rule 01 declares its own checker; rule 02's heading is malformed and
    # carries a different one. Rule 01 must keep its own.
    block = (HEAD
             + "### RULE R-demo-01 — cardinality (checked)\ncheck:: rocks_single_per_anchor\n\nbody.\n\n"
             + "### RULE R-demo-02 — names are short (retired)\ncheck:: rock_name_short_and_expanded\n\nbody.\n"
             ).splitlines()
    rs = m.parse_ruleset_block(block, m.REPO_ROOT / "R-demo.md")
    rules = {r["id"]: r for r in rs["rules"]}
    check("R-demo-02" in rules,
          "fold — the (retired) rule is visible to the parser at all")
    check((rules.get("R-demo-01", {}).get("check") or "")
          .startswith("rocks_single_per_anchor"),
          "fold — rule 01 keeps its OWN checker, not rule 02's")
    check((rules.get("R-demo-02", {}).get("check") or "")
          .startswith("rock_name_short_and_expanded"),
          "fold — rule 02 carries its own checker rather than donating it")

    # ---- 5. R-ruleset-06 fails on a heading that would fold ----------------
    st, msg = tier_verdict(m, HEAD
                           + "### RULE R-demo-01 — a title (checked)\ncheck:: x\n\nb.\n\n"
                           + "### RULE R-demo-02 — a title (checked, warn)\ncheck:: y\n\nb.\n")
    check(st == "fail" and "fold" in msg, "R-ruleset-06 FAILS on an unknown tier")

    # ---- 6. ...and on a heading with no tier and no engine fields ----------
    st, _ = tier_verdict(m, HEAD + "### RULE R-demo-01 — a title\n\njust prose.\n")
    check(st == "fail", "R-ruleset-06 fails on a heading with no tier at all")

    # ---- 7. Warden rules are exempt — BOTH spellings ----------------------
    st, _ = tier_verdict(m, HEAD
                         + "### RULE R-demo-01 — guard (when:: tool:pre:Edit)\nmend:: x\n\nb.\n")
    check(st == "pass", "Warden rule, moment in the HEADING → exempt")

    st, _ = tier_verdict(m, HEAD
                         + "### RULE R-demo-01 — guard\nwhen:: write:markdown\nif:: `x`\n\nb.\n")
    check(st == "pass", "Warden rule, moment on a BODY line → exempt")

    st, _ = tier_verdict(m, HEAD + "### RULE R-demo-01 — guard\nif:: `x`\n\nb.\n")
    check(st == "pass", "Warden rule declaring only if:: → exempt")

    # ---- 8. a rule carrying check:: is OURS, exempt from the exemption -----
    st, _ = tier_verdict(m, HEAD
                         + "### RULE R-demo-01 — guard\nwhen:: write:markdown\ncheck:: x\n\nb.\n")
    check(st == "fail", "a rule with check:: needs a tier even if it also has when::")

    # ---- 9. fenced examples are not rules ---------------------------------
    st, _ = tier_verdict(m, HEAD + "### RULE R-demo-01 — a title (checked)\ncheck:: x\n\n"
                         + "```\n### RULE R-teaching-99 — no tier here\n```\n")
    check(st == "pass", "a RULE heading inside a fence is ignored")

    # ---- 10. a well-formed ruleset passes ---------------------------------
    st, _ = tier_verdict(m, HEAD
                         + "### RULE R-demo-01 — a (checked)\ncheck:: x\n\nb.\n\n"
                         + "### RULE R-demo-02 — b (retired)\n\nb.\n\n"
                         + "### RULE R-demo-03 — c (governing)\n\nb.\n")
    check(st == "pass", "all-six-tiers ruleset passes")

    print("-" * 40)
    print(f"T200 rule-tier fold test: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
