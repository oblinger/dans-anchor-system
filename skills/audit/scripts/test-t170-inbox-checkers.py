#!/usr/bin/env python3
"""test-t170-inbox-checkers.py — T170: R-fct-inbox's three checkers.

The defect this guards: `R-fct-inbox-01/-02/-03` were titled "(checked)" from
creation and carried **no `check::` field at all**, so they were agent judgment
wearing a checker's label. That is quieter than the failure warden warns about —
`check:: missing_fn` earns a `WARNING — registered by no imported module`, while
a rule with no `check::` line earns nothing and reads as enforced.

So this file pins the WIRING as hard as the logic: § 4 asserts each rule id
resolves to a registered checker, which is the thing that was silently false.

Red-check discipline: every positive assertion has a negative twin. The live
corpus is 13 conforming Inbox files, so a checker that returned "pass"
unconditionally would sail through the corpus — passing on it proves nothing and
is deliberately not the evidence here. Self-contained: fixtures in tmp, no vault
I/O.
"""
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


AP = _load("audit_plan_t170", HERE / "audit-plan.py")

FAILS = []
CHECKS = 0


def ok(cond, label):
    global CHECKS
    CHECKS += 1
    if cond:
        print(f"  ok    {label}")
    else:
        print(f"  FAIL  {label}")
        FAILS.append(label)


def inbox(tmp, body, name="HA Inbox.md", folder="HA Track"):
    d = Path(tmp) / folder
    d.mkdir(parents=True, exist_ok=True)
    f = d / name
    f.write_text(body, encoding="utf-8")
    return f


HEAD = ":>> [[kmr]] → [HA Inbox](hook://p/HA%20Inbox) \n# HA Inbox\nRaw input.\n\n"


# ------------------------------------------------------------------ 1. -01
print("\nR-fct-inbox-01 — the Inbox lives in a Track folder")
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    f = inbox(tmp, HEAD)
    st, _ = AP.chk_inbox_in_track_folder(f, root, {})
    ok(st == "pass", "an Inbox in `HA Track/` passes")

    g = inbox(tmp, HEAD, folder="HA Design")
    st, detail = AP.chk_inbox_in_track_folder(g, root, {})
    ok(st == "fail", "an Inbox in `HA Design/` FAILS")
    ok("HA Design" in detail, "the failure names the folder it actually found")

    missing = root / "HA Track" / "Nope Inbox.md"
    st, _ = AP.chk_inbox_in_track_folder(missing, root, {})
    ok(st == "pass", "a non-existent target passes rather than erroring")


# ------------------------------------------------------------------ 2. -02
print("\nR-fct-inbox-02 — every H2 is a dated entry heading")
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)

    f = inbox(tmp, HEAD + "## 2026-08-08 — A topic\n\n> body\n")
    st, detail = AP.chk_inbox_entry_headings(f, root, {})
    ok(st == "pass", "an untagged dated entry passes")
    ok("1 entry" in detail, "the detail counts the entry (singular)")

    # THE load-bearing case: tag absence is what pending MEANS.
    f = inbox(tmp, HEAD + "## 2026-08-08 — One\n\n## 2026-08-07 — Two\n")
    st, detail = AP.chk_inbox_entry_headings(f, root, {})
    ok(st == "pass", "TWO untagged entries still pass — absence is never a finding")
    ok("2 entries" in detail, "the detail counts both (plural)")

    f = inbox(tmp, HEAD + "## 2026-08-08 — Done one `DONE`\n")
    st, _ = AP.chk_inbox_entry_headings(f, root, {})
    ok(st == "pass", "a tagged entry passes too")

    f = inbox(tmp, HEAD + "## Some undated heading\n")
    st, detail = AP.chk_inbox_entry_headings(f, root, {})
    ok(st == "fail", "an UNDATED H2 fails")
    ok("Some undated" in detail, "the failure quotes the offending heading")

    f = inbox(tmp, HEAD + "## 2026-08-08 - hyphen not em-dash\n")
    st, _ = AP.chk_inbox_entry_headings(f, root, {})
    ok(st == "fail", "a hyphen separator fails — the form is an em-dash")

    f = inbox(tmp, HEAD + "## 2026-08-08 — Ok\n\n## Bad\n\n## 2026-08-06 — Ok\n")
    st, detail = AP.chk_inbox_entry_headings(f, root, {})
    ok(st == "fail", "one bad heading among good ones still fails")
    ok("1 H2" in detail, "the count is of BAD headings, not of all headings")

    # Fence-awareness — the reason this routes through `_h2_titles` rather than
    # scanning for `## `. A doc quoting the entry FORM as an example (the facet
    # spec does exactly this) must not have its example read as a live entry.
    f = inbox(tmp, HEAD + "## 2026-08-08 — Real\n\n```\n## Not a real heading\n```\n")
    st, _ = AP.chk_inbox_entry_headings(f, root, {})
    ok(st == "pass", "a malformed heading INSIDE a code fence is not a live entry")

    f = inbox(tmp, HEAD + "## 2026-08-08 — Real `WRONG`\n\n```\n## X `ALSO-WRONG`\n```\n")
    st, detail = AP.chk_inbox_status_tags(f, root, {})
    ok(st == "fail" and "ALSO" not in detail,
       "a bad tag in a fenced example is ignored while the live one is caught")


# ------------------------------------------------------------------ 3. -03
print("\nR-fct-inbox-03 — only DONE and MOVED → … are read by anything")
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)

    f = inbox(tmp, HEAD + "## 2026-08-08 — A `DONE`\n")
    st, _ = AP.chk_inbox_status_tags(f, root, {})
    ok(st == "pass", "`DONE` is sanctioned")

    f = inbox(tmp, HEAD + "## 2026-08-08 — A `MOVED → TINK Backlog T171`\n")
    st, _ = AP.chk_inbox_status_tags(f, root, {})
    ok(st == "pass", "`MOVED → <destination>` is sanctioned")

    f = inbox(tmp, HEAD + "## 2026-08-08 — A `HANDLED`\n")
    st, detail = AP.chk_inbox_status_tags(f, root, {})
    ok(st == "fail", "an INVENTED tag fails — the author thinks it is processed "
                     "and every consumer counts it pending forever")
    ok("HANDLED" in detail, "the failure names the invented tag")

    f = inbox(tmp, HEAD + "## 2026-08-08 — A `Done`\n")
    st, _ = AP.chk_inbox_status_tags(f, root, {})
    ok(st == "pass", "lowercase `Done` is not tag-SHAPED, so it is prose, not a bad tag")

    # False-positive guard: ordinary backticked prose in a heading.
    f = inbox(tmp, HEAD + "## 2026-08-08 — Fix `audit-q.py` and the `slug` field\n")
    st, _ = AP.chk_inbox_status_tags(f, root, {})
    ok(st == "pass", "backticked prose in a heading does not manufacture a finding")

    # Scoping: a tag-shaped token in the BODY is out of scope by design.
    f = inbox(tmp, HEAD + "## 2026-08-08 — A\n\n> we should mark it `HANDLED` maybe\n")
    st, _ = AP.chk_inbox_status_tags(f, root, {})
    ok(st == "pass", "a tag-shaped word in body prose is out of scope, as documented")

    f = inbox(tmp, HEAD + "## 2026-08-08 — A `DONE`\n\n## 2026-08-07 — B `NOPE`\n")
    st, detail = AP.chk_inbox_status_tags(f, root, {})
    ok(st == "fail", "one bad tag among good ones still fails")
    ok("NOPE" in detail and "DONE" not in detail.replace("`DONE`", ""),
       "the failure names only the offender")


# ------------------------------------------------------- 4. the WIRING itself
print("\nThe wiring — each rule id resolves to a registered checker")
for name in ("inbox_in_track_folder", "inbox_entry_headings", "inbox_status_tags"):
    ok(name in AP.CHECKERS, f"`{name}` is registered in CHECKERS")
    ok(callable(AP.CHECKERS.get(name)), f"`{name}` resolves to something callable")

rs_path = AP.REPO_ROOT / "rulesets" / "R-fct-inbox.md"
text = rs_path.read_text(encoding="utf-8")
for rid, checker in (("R-fct-inbox-01", "inbox_in_track_folder"),
                     ("R-fct-inbox-02", "inbox_entry_headings"),
                     ("R-fct-inbox-03", "inbox_status_tags")):
    blk = text.split(f"### RULE {rid} ")[1].split("### RULE")[0]
    ok(f"check:: {checker}" in blk, f"{rid} declares `check:: {checker}`")
    ok("(checked)" in text.split(f"### RULE {rid} ")[1].split("\n")[0],
       f"{rid}'s title says (checked), matching its now-real checker")

ok("import:: skills/audit/scripts/audit-plan.py" in text,
   "the ruleset imports the module its checkers live in — without this the "
   "check:: names resolve to nothing and the rules go back to agent judgment")

# -04 must NOT claim to be checked: it asserts something about a file's history
# across edits, which no single-file check can see.
ok("R-fct-inbox-04" in text and "(stated)" in text.split("### RULE R-fct-inbox-04 ")[1].split("\n")[0],
   "-04 still says (stated) — it is about history no single-file check can observe")

print(f"\nT170 inbox checkers: {CHECKS - len(FAILS)}/{CHECKS} passed")
if FAILS:
    print("\nFAILURES:")
    for f in FAILS:
        print(f"  - {f}")
    sys.exit(1)
print("SUITE GREEN")
