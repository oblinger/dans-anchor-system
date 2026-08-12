#!/usr/bin/env python3
"""T212 — the two orphan checkers that belonged to R-markdown, and what wiring
them exposed.

`--verify-registry` listed `md_fence_no_markdown` and
`md_angle_brackets_html_or_spaced` as registered-and-called-by-nothing. They are
not the same kind of orphan, and the difference is the point:

  * `md_fence_no_markdown` is **R-markdown-11's implementation** — its docstring
    says so — sitting unwired while the rule read `(checked)` with no `check::`,
    i.e. billed as an LLM judgment against every `.md` file in every anchor the
    set is armed on. Wiring it converted 8,158 vault-wide judgments into
    mechanical verdicts and surfaced 223 real findings.

  * `md_angle_brackets_html_or_spaced` is a **second implementation of
    R-markdown-13**, which already had one. Orphan there meant superseded, and
    the measurement said so: 20 fails to the wired checker's 15, three of the
    five extra false. It is deleted, and this file asserts it stays deleted.

Wiring the first exposed a duplicate RULE (`-03` and `-11` ask the same question
with different scopes, so a `python` fence holding `[[` in a regex fails one and
passes the other); measuring the second exposed two defects in the *wired*
checker — it missed `Box<dyn Error>`, the generic R-markdown-13's own text names,
because its matcher allowed nothing between the tag name and the `>`.

Run: python3 test-t212-markdown-orphan-wiring.py
"""
import importlib.machinery
import importlib.util
import re
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


ap = _load("audit_plan_t212_md", HERE / "audit-plan.py")

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  ok   {label}")
    else:
        failed += 1
        print(f"  FAIL {label}\n         got  {got!r}\n         want {want!r}")


def verdict(checker: str, body: str, name="doc.md"):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / name
        p.write_text(body, encoding="utf-8")
        return ap.CHECKERS[checker](p, p.parent, [])[0]


def angle(body):
    return verdict("md_stray_angle_tag", "# T\n\n" + body + "\n")


# ── R-markdown-13: the widening, stated as the cases that motivated it ───────
# Each `fail` below PASSED before T212, and each is a form the rule's own text
# already claimed to cover.

check("`Box<dyn Error>` — the generic the rule text names — now fails",
      angle("It returns `x` as Box<dyn Error> on error."), "fail")
check("a multi-word placeholder `<the actual question>` now fails",
      angle("Write <the actual question> here."), "fail")
check("a single-token stray tag still fails (no regression)",
      angle("Name it <Widget> for now."), "fail")

# The guards the widening must not break. `a < b` is kept out of scope by
# requiring the closing `>`, not by enumerating exceptions — so it survives a
# matcher that now admits arbitrary text before that `>`.
check("`a < b` is still not a tag", angle("The invariant a < b holds."), "pass")
check("an inline code span is still literal",
      angle("Use `Box<dyn Error>` in the signature."), "pass")
check("real HTML with attributes is still allowed",
      angle('A <span style="color:red">note</span> renders fine.'), "pass")
check("an HTML comment is not a stray tag",
      angle("<!-- a note to the author -->"), "pass")
check("`.html` files are still skipped",
      verdict("md_stray_angle_tag", "<Widget>\n", name="page.html"), "pass")

# A backslash escape is one of the remediations the rule offers. Flagging it
# fails an author for having applied the fix — and the widening is what made
# that reachable, because `\<keep where, delete which\>` has spaces in it.
check("a backslash-escaped `\\<…\\>` is exempt (it is the offered fix)",
      angle(r"Merge them — \<keep where, delete which, how to combine\>."),
      "pass")
check("...and a half-escaped opener is still exempt at the open end",
      angle(r"Merge them — \<keep where>."), "pass")

# Q002 (Dan, 2026-08-01) revoked the single-letter exemption; T084 swept the
# sites. The rule text still promised it until T212. Asserted here so the
# exemption cannot be quietly reinstated by whoever next reads that promise.
check("single-letter `F<n>` is NOT exempt (Q002)",
      angle("The question F<n> is asked."), "fail")
check("...and the rule text no longer promises the exemption",
      "single-letter placeholders (`F<n>`), and whitespace"
      in (ap.REPO_ROOT / "rulesets" / "R-markdown.md").read_text(), False)

# ── the deletion: one rule, one implementation ───────────────────────────────

check("the superseded second implementation is gone from the registry",
      "md_angle_brackets_html_or_spaced" in ap.CHECKERS, False)
check("...and its function is gone from the module",
      hasattr(ap, "chk_md_angle_brackets_html_or_spaced"), False)

# ── R-markdown-11: wired, and R-markdown-03 retired as its duplicate ─────────

FENCE_MD = "# T\n\n```\n# A heading\n\nSee [[Some Doc]].\n```\n"
FENCE_PY = "# T\n\n```python\nlink = r'\\[\\[(.+?)\\]\\]'   # matches [[wiki]]\n```\n"

check("an untagged fence holding live markdown fails",
      verdict("md_fence_no_markdown", FENCE_MD), "fail")
check("a language-tagged fence is literal source and passes",
      verdict("md_fence_no_markdown", FENCE_PY), "pass")

rs = (ap.REPO_ROOT / "rulesets" / "R-markdown.md").read_text()


def rule_block(n):
    m = re.search(rf"^### RULE R-markdown-{n} —.*?(?=^### RULE |\Z)", rs,
                  re.M | re.S)
    return m.group(0) if m else ""


check("R-markdown-11 now carries its check:: ref",
      "check:: md_fence_no_markdown" in rule_block("11"), True)
check("R-markdown-03 is retired rather than left as a second live rule",
      bool(re.match(r"^### RULE R-markdown-03 — .*\(retired\)$",
                    rule_block("03").splitlines()[0])), True)
check("...and it does not carry a check:: of its own",
      # A LINE that begins `check::` is a ref; the same token in prose is the
      # retirement note naming what -11 was wired to, and must not count.
      any(ln.startswith("check::") for ln in rule_block("03").splitlines()),
      False)

# The tier vocabulary must actually admit `(retired)`, or the retirement is the
# R-rocks-04 fold all over again: a heading `_RULE_RE` skips does not terminate
# the rule above it, so the NEXT `check::` folds onto the wrong rule. Asserted
# against the parser rather than against the six-tier list in R-ruleset-06.
_src = ap.REPO_ROOT / "rulesets" / "R-markdown.md"
_block, _ = ap.extract_ruleset_block(_src.read_text(), "R-markdown")
_parsed = ap.parse_ruleset_block(_block, _src)
ids = [r["id"] for r in _parsed["rules"]]
check("`(retired)` is a tier the parser admits, so -03 parses as a rule",
      "R-markdown-03" in ids, True)
check("...and -04, the rule directly beneath it, still parses",
      "R-markdown-04" in ids, True)

# The duplicate this retirement removes was not a tidiness problem: the two
# rules disagreed on the SAME file. -03 scoped to any fenced block, -11 exempts
# language-tagged fences as literal source. A python fence quoting `[[` failed
# one and passed the other, and both were LLM-billed on every markdown file.
check("the retired rule records what it was superseded by",
      "R-markdown-11" in rule_block("03"), True)

print()
if failed:
    print(f"test-t212-markdown-orphan-wiring: {passed} passed, {failed} failed")
    sys.exit(1)
print(f"test-t212-markdown-orphan-wiring: {passed} passed, 0 failed")
