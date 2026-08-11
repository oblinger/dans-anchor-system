#!/usr/bin/env python3
"""test-t198-head-h1-in-spine.py — `# BRIEF` is not the page's H1.

`Spine.h1` was `l.startswith("# ")` scanned from the body start: the first `# `
line anywhere wins. On the widespread convention of opening a body section with
`# BRIEF` / `# LOG` / `# MEETINGS` below an earlier `##`, that hands back a
"head" hundreds of lines into the body, and every check anchored on it — S03,
S05, S06 and the whole heart analysis — then reports a real line number for a
defect that is not there.

This is T093's bug, and T093 already fixed it: `_first_h1` was renamed
`_head_h1` precisely because "the first H1 anywhere" and "the H1 that heads this
document" are different questions, and F296 routed sixteen call sites through
the one definition. `spine.py` was written afterwards and hand-spelled the old
pattern again, making it the seventeenth site — and reintroducing the bug on
**215** in-scope pages, measured 2026-08-11.

So the assertion here is single-sourcing, not a second opinion about what an H1
is: `Spine.h1` must agree with `_head_h1` on every shape, including the ones
`startswith("# ")` gets wrong in the *other* direction (a legally indented `# `,
which CommonMark admits up to three spaces and the old pattern missed on 3
pages). A copy of the logic would pass these tests today and drift tomorrow,
which is the failure this file exists to prevent — so it checks agreement with
the primitive, not against a hard-coded expectation.

Usage: python3 test-t198-head-h1-in-spine.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = FAIL = 0


def _load(name, fname=None):
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(name, HERE / (fname or f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
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


MASTHEAD = """| -[[Demo]]- | : a demo page.<br>→ [[kmr]] → [Demo](hook://p/Demo) |
| --- | --- |
| Related | [[Other]],   |
"""

CASES = [
    ("a real H1 is still the H1",
     "# Demo\nOrientation line.\n", True),
    ("`# BRIEF` below an earlier `##` is NOT the head",
     "## Topics\nsome notes\n\n# BRIEF\nagent-facing text\n", False),
    ("`# LOG` below an earlier `##` is NOT the head — the @person-page shape",
     ":>> [[kmr]] → [[AT]] → [Someone](hook://p/Someone)\n\n"
     "## Contact\nnotes\n\n# LOG\n\n### 2026-01-01\nentry\n", False),
    ("masthead then H1 then `# BRIEF` — the H1 wins, not the BRIEF",
     MASTHEAD + "\n# Demo\nOrientation line.\n\n# BRIEF\nagent text\n", True),
    ("a legally indented H1 (up to three spaces) is found",
     "   # Demo\nOrientation line.\n", True),
    ("four spaces is an indented code block, not a heading",
     "    # Demo\nsome text\n", False),
    ("a `# comment` inside a fence is not the head",
     "```bash\n# from anywhere\nls\n```\n\nprose\n", False),
    ("frontmatter `#` comment is not the head",
     "---\n# status_doc: x\ndescription: y\n---\n\nprose\n", False),
    ("`## Open Questions` parked above the H1 does not end the head (F241)",
     "## Open Questions\n\n- **Q1 — a thing** — context\n\n# Demo\nOrientation.\n", True),
]


def main():
    ap = _load("ap", "audit-plan.py")
    sp = _load("spine")

    for label, body, expect_found in CASES:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "Demo.md"
            p.write_text(body, encoding="utf-8")
            got = sp.Spine(p).h1
        want = ap._head_h1(body)[0]
        check(got == want, f"agrees with _head_h1 — {label}")
        check((got is not None) == expect_found,
              f"{'finds' if expect_found else 'no'} head H1 — {label}")

    # The regression proper: the old pattern's answer, spelled out, so a revert
    # to `startswith('# ')` fails here rather than passing quietly.
    buried = "## Topics\nnotes\n\n# BRIEF\ntext\n"
    old = next((i for i, l in enumerate(buried.split("\n")) if l.startswith("# ")), None)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "Demo.md"
        p.write_text(buried, encoding="utf-8")
        new = sp.Spine(p).h1
    check(old is not None and new is None,
          "the old hand-spelled scan found `# BRIEF` (line %s); Spine.h1 now does not" % old)

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
