#!/usr/bin/env python3
"""test-f296-fence-blind-fixers.py — code inside a fence is not content to fix.

Two checker/fixer pairs decided line-by-line whether a line was prose, and both
tested the RAW line. A fenced literal example is byte-identical to the thing it
is an example of, so the on-write fixer rewrote both — then the re-check passed
and the driver reported it "fixed". Nothing surfaced to the author.

  1. `chk_md_em_dash` / `fix_md_em_dash` (via `_repl_outside_code`) paired fence
     runs ANYWHERE on a line rather than at line start. `_mask_code` was repaired
     for exactly that on 2026-08-01; these were left behind on the old pattern.
     A zero-width-space-escaped nested fence — which renders literally instead of
     closing the block it sits inside — mis-paired against the outer opener and
     left the real inner block exposed.

  2. `chk_md_table_pipe_escape` / `fix_md_table_pipe_escape` had no fence
     awareness at all. This is the higher-traffic one: the corpus documents its
     own table conventions, and a wiki-link in a table cell is the single
     most-shown example form.

Both were found by the F296 Fable scan and independently re-verified before the
fix. The assertions below fail against the pre-F296 code.

    python3 test-f296-fence-blind-fixers.py
"""
import importlib.util
import pathlib
import sys
import tempfile

S = (pathlib.Path(__file__).parent / "audit-plan.py").resolve()
_spec = importlib.util.spec_from_file_location("ap", S)
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

ZW = "​"          # the zero-width space that escapes a nested fence
results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"  (got {got!r}, want {want!r})"))


def write(body, name="Doc.md"):
    f = pathlib.Path(tempfile.mkdtemp()) / name
    f.write_text(body, encoding="utf-8")
    return f


print("Table-pipe escape: a fenced example row is not a table row")

FENCED_ROW = ("# Note\nWhat this is.\n\n"
              "The row form is written like this:\n\n"
              "```\n| [[A|B]] | cell |\n```\n")
f = write(FENCED_ROW)
check("check passes on a fenced example row",
      ap.chk_md_table_pipe_escape(f, f.parent, [])[0], "pass")
check("fixer leaves the fenced example byte-identical",
      (ap.fix_md_table_pipe_escape(f, f.parent, [])[0], f.read_text(encoding="utf-8")),
      (False, FENCED_ROW))

# The rule itself must still work — masking must not become suppression.
REAL_ROW = "# Note\nWhat this is.\n\n| [[A|B]] | cell |\n"
f = write(REAL_ROW)
check("a REAL unescaped table row still fails",
      ap.chk_md_table_pipe_escape(f, f.parent, [])[0], "fail")
check("and the fixer still escapes it",
      (ap.fix_md_table_pipe_escape(f, f.parent, [])[0],
       "[[A\\|B]]" in f.read_text(encoding="utf-8")), (True, True))

# Line numbers must survive masking — masking blanks, it does not delete.
f = write("# Note\nWhat this is.\n\n```\n| [[X|Y]] |\n```\n\n| [[A|B]] | c |\n")
check("the real row after a fence is reported at its true line (8)",
      "line 8" in ap.chk_md_table_pipe_escape(f, f.parent, [])[1], True)

print("Em-dash: a zw-escaped nested fence does not expose the block it wraps")

NESTED = ("# T\nWhat this is.\n\n"
          "```markdown\n"
          f"shown literally: {ZW}```python\n"
          "code_a = 1  -- real code\n"
          f"{ZW}```\n"
          "```\n")
f = write(NESTED)
check("check passes — the inner block is inside the outer fence",
      ap.chk_md_em_dash(f, f.parent, [])[0], "pass")
check("fixer leaves the nested-fence file byte-identical",
      (ap.fix_md_em_dash(f, f.parent, [])[0], f.read_text(encoding="utf-8")),
      (False, NESTED))

PROSE = "# T\nWhat this is.\n\nA sentence -- with a typed em-dash.\n"
f = write(PROSE)
check("a REAL spaced double-hyphen in prose still fails",
      ap.chk_md_em_dash(f, f.parent, [])[0], "fail")
check("and the fixer still converts it",
      (ap.fix_md_em_dash(f, f.parent, [])[0], "—" in f.read_text(encoding="utf-8")),
      (True, True))

print("Angle brackets: the same masking, so the same fence pairing")

f = write("# T\nWhat this is.\n\n"
          "```markdown\n"
          f"literal: {ZW}```cpp\n"
          "std::vector<int> v;\n"
          f"{ZW}```\n"
          "```\n")
check("generic inside a zw-escaped nested fence is not flagged",
      ap.chk_md_angle_brackets_html_or_spaced(f, f.parent, [])[0], "pass")

f = write("# T\nWhat this is.\n\nA stray List<int> in prose.\n")
check("a REAL stray generic in prose still fails",
      ap.chk_md_angle_brackets_html_or_spaced(f, f.parent, [])[0], "fail")

print("One fence pattern, shared")

check("`_repl_outside_code` uses the module-level `_FENCE_RE`",
      ap._FENCE_RE.pattern.startswith("(?m)^[ \\t]{0,3}"), True)
check("tilde fences pair too",
      ap.chk_md_table_pipe_escape(
          write("# N\nWhat this is.\n\n~~~\n| [[A|B]] |\n~~~\n"),
          pathlib.Path("."), [])[0], "pass")

print("Ruleset extraction: a `#` comment in a fenced example does not end the block")

# Finding 3. `extract_ruleset_block` ended the block at the first heading of
# level <= its own, with no fence tracking. A shell `# comment` is level 1, which
# is <= everything — so the block stopped at the fence and every RULE after it
# left the engine entirely: never planned, never judged, never reported N/A.
# This is the one failure mode with NO output at all, so nothing in a corpus
# would ever indicate it. Fenced shell examples are ordinary in rule bodies.
RS = ("# RULESET R-x\n"
      "where:: `always`\n"
      "description:: a ruleset with a fenced shell example\n"
      "\n"
      "### RULE R-x-01 — first (checked)\n"
      "check:: first_checker\n"
      "\n"
      "Run it like this:\n"
      "\n"
      "```bash\n"
      "# just a comment, not a heading\n"
      "echo hi\n"
      "```\n"
      "\n"
      "### RULE R-x-02 — second (checked)\n"
      "check:: second_checker\n"
      "\n"
      "### RULE R-x-03 — third (checked)\n"
      "check:: third_checker\n")
blk = ap.extract_ruleset_block(RS, "R-x")
check("the block spans past the fenced `# comment`", blk is not None and len(blk[0]) > 12, True)
parsed = ap.parse_ruleset_block(blk[0], pathlib.Path(ap.REPO_ROOT) / "rulesets" / "R-x.md")
check("all three rules survive extraction",
      [r["id"] for r in parsed["rules"]], ["R-x-01", "R-x-02", "R-x-03"])
check("their `check::` actions come through",
      [r["check"] for r in parsed["rules"]],
      ["first_checker", "second_checker", "third_checker"])

# A REAL sibling heading must still end the block — masking is not suppression.
RS2 = RS + "\n# Position in the catalog\n\nSits under R-doc.\n"
blk2 = ap.extract_ruleset_block(RS2, "R-x")
check("a real level-1 sibling heading still ends the block",
      any("Position in the catalog" in l for l in blk2[0]), False)

# A fenced EXAMPLE of a RULE heading is a picture of the form, not a rule.
RS3 = ("# RULESET R-y\n"
       "where:: `always`\n"
       "\n"
       "### RULE R-y-01 — real (checked)\n"
       "check:: real_checker\n"
       "\n"
       "Authored like this:\n"
       "\n"
       "```\n"
       "### RULE R-y-99 — illustration (checked)\n"
       "check:: illustration_checker\n"
       "```\n")
p3 = ap.parse_ruleset_block(ap.extract_ruleset_block(RS3, "R-y")[0],
                            pathlib.Path(ap.REPO_ROOT) / "rulesets" / "R-y.md")
check("a fenced RULE example does not become a phantom rule",
      [r["id"] for r in p3["rules"]], ["R-y-01"])
check("and it does not overwrite the real rule's action",
      p3["rules"][0]["check"], "real_checker")

# Values are still read from the REAL line — `_mask_code` blanks inline spans,
# and `where:: `file:…`` is authored with them (F172). Matching structure on the
# masked line must not cost the value.
check("a backticked `where::` value still parses",
      ap.parse_ruleset_block(ap.extract_ruleset_block(RS, "R-x")[0],
                             pathlib.Path(ap.REPO_ROOT) / "rulesets" / "R-x.md")["where"],
      "always")

print("Backlog rows: a fenced block inside a row does not close the row")

# Finding 4, second half. The first half of that finding — that F275 standalone
# Q-rows are indented and so invisible to `_backlog_rows` — was MEASURED AND
# REJECTED: all 21 indented label-shaped bullets across the vault's 37 backlogs
# are row-hosted `- **Q<n> —` sub-bullets, which are subs BY DESIGN (R-backlog-05,
# read through T086's `count_row_pending_qs`). The writer's indent-tolerant
# `ROW_HEADER_RE` exists to match those sub-headers, which is not the same claim
# as rows being indented. Assertion A pins the behaviour that was correct already,
# so a future "fix" cannot regress it.

A = ("## Ready\n\n"
     "- **T001 — parent** [Questions] — body\n"
     "  - **Q1 — a row-hosted question** — options\n"
     "  - **Next:** do the thing\n")
rows = ap._backlog_rows(A)
check("an indented `- **Q1 —` stays a SUB, not a second row", len(rows), 1)
check("and it is visible in the row's subs", len(rows[0][3]), 2)

# The real half: a row documenting a command opens a fence at column 0, which
# the "col-0 non-list line closes the row" arm read as the end of the row.
B = ("## Ready\n\n"
     "- **T002 — parent** [Ready] — body showing a command\n"
     "```bash\n"
     "state show Tink Backlog T002\n"
     "```\n"
     "  - **Next:** do the thing\n")
rows = ap._backlog_rows(B)
check("a col-0 fence does not close the row", len(rows), 1)
check("the `- **Next:**` after the fence still belongs to the row",
      any("Next:" in s for s in rows[0][3]), True)
check("and the fenced lines are NOT counted as sub-bullets", len(rows[0][3]), 1)

# A fenced EXAMPLE of a row is not a row.
C = ("## Ready\n\n"
     "- **T003 — parent** [Ready] — the row form is written like this:\n"
     "```\n"
     "- **T999 — illustration** [Ready] — body\n"
     "```\n"
     "  - **Next:** do the thing\n")
check("a fenced example row does not become a row", len(ap._backlog_rows(C)), 1)

# Masking must not become suppression: a real col-0 paragraph still closes a row.
D = ("## Ready\n\n"
     "- **T004 — parent** [Ready] — body\n"
     "\n"
     "Loose prose at column zero.\n"
     "  - **Next:** orphaned, must NOT attach\n")
rows = ap._backlog_rows(D)
check("a real col-0 prose line still closes the row", len(rows[0][3]), 0)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
