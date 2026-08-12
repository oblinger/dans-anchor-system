#!/usr/bin/env python3
"""test-t222-em-dash-code-blindness.py — three defects in the em-dash fixer.

Found 2026-07-30 authoring SKA F286. The on-write fixer silently rewrote a
spaced double-hyphen to an em-dash INSIDE a 4-space indented code block, turning
a git pathspec separator into an em-dash and leaving a valid-looking but broken
command that would have shipped to another agent as instructions.

  1. **Indented code blocks were not code.** Both `chk_md_em_dash` and
     `_repl_outside_code` masked fences and inline spans, and neither recognized
     the 4-space indented block — legal markdown, used throughout these design
     docs. R-markdown-05's own text scopes the rule to "a definition-list bullet
     (or prose)", so a `<pre>` block was outside its stated intent all along.

  2. **Checker and fixer each defined "outside code" independently, and
     disagreed.** The checker's inline-span class excluded only newline; the
     replacer's excluded newline AND backtick. On a line with several spans they
     masked different regions, so the checker could report clean while the fixer
     still rewrote — and no test caught it, because each was internally
     consistent.

  3. **Backtick parity broke the escape hatch.** A code span whose CONTENT holds
     a backtick shifts the pairing, and everything after it on that line loses
     its masking. The first draft of T222's own backlog row was corrupted by the
     rule it describes. So "put it in backticks" is a convention, not a defence —
     the fixer must refuse a line it cannot mask with certainty.

The assertions below fail against the pre-T222 code.

    python3 test-t222-em-dash-code-blindness.py
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

DASH = "—"
results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def write(body):
    f = pathlib.Path(tempfile.mkdtemp()) / "Doc.md"
    f.write_text(body, encoding="utf-8")
    return f


print("Defect 1 — a 4-space indented code block is code")

# The original corruption, verbatim in shape: a git pathspec separator.
PATHSPEC = ("# Note\n\nRun this to stage only the tracked half:\n\n"
            "    git checkout HEAD -- 'Warden Corpus'\n\n"
            "Then re-run the harness.\n")
f = write(PATHSPEC)
check("check passes — the block is not prose",
      ap.chk_md_em_dash(f, f.parent, [])[0], "pass")
ap.fix_md_em_dash(f, f.parent, [])
check("fixer leaves the pathspec byte-identical", f.read_text(), PATHSPEC)

# ...and the same text one indent level shallower IS prose, and is still fixed.
PROSE = "# Note\n\nA handle -- its description.\n"
f = write(PROSE)
check("real prose still fails the check",
      ap.chk_md_em_dash(f, f.parent, [])[0], "fail")
ap.fix_md_em_dash(f, f.parent, [])
check("...and is still converted", f.read_text(), f"# Note\n\nA handle {DASH} its description.\n")

# The failure direction that matters: a NESTED BULLET carries four spaces of list
# indent and is prose, not code. Masking it would go silently green across most
# of the corpus.
NESTED = "# Note\n\n- top\n    - nested handle -- its description\n"
f = write(NESTED)
check("a 4-space NESTED BULLET is prose, not an indented code block",
      ap.chk_md_em_dash(f, f.parent, [])[0], "fail")
ap.fix_md_em_dash(f, f.parent, [])
check("...and is converted",
      f.read_text(), f"# Note\n\n- top\n    - nested handle {DASH} its description\n")

check("an indented run NOT opened by a blank line is not a block either",
      ap._indented_code_regions("intro text\n    still the paragraph -- here\n"), [])


print("\nDefect 2 — checker and fixer share ONE definition of code")

# A line with several spans, which is where the two classes used to diverge.
MULTI = "# Note\n\nSee `a -- b` and `c -- d` and then real -- prose.\n"
f = write(MULTI)
verdict = ap.chk_md_em_dash(f, f.parent, [])[0]
ap.fix_md_em_dash(f, f.parent, [])
after = f.read_text()
check("check fails (the unbackticked one is real)", verdict, "fail")
check("only the unbackticked occurrence is rewritten",
      after, f"# Note\n\nSee `a -- b` and `c -- d` and then real {DASH} prose.\n")
check("re-check is clean after the fix",
      ap.chk_md_em_dash(f, f.parent, [])[0], "pass")

check("no caller re-derives the span class",
      S.read_text(encoding="utf-8").count(r'(`+)[^`\n]*?\1'), 0)

# The property itself: whatever the mask hides, the replacer must preserve.
for body in [PATHSPEC, MULTI, NESTED,
             "# N\n\n```\ncode -- here\n```\n\ntext -- here\n",
             "# N\n\nprose -- one\n\n    indented -- two\n\n- bullet -- three\n"]:
    masked = ap._mask_code(body)
    # Length-preserving on purpose: a shorter replacement shifts every later
    # index and the comparison below would be measuring its own arithmetic.
    replaced = ap._repl_outside_code(body, lambda s: s.replace(" -- ", " ~~ "))
    hidden = [i for i, c in enumerate(masked) if c == " " and body[i] != " "]
    check("  masked bytes are untouched by the replacer",
          all(replaced[i:i + 1] == body[i:i + 1] for i in hidden if i < len(replaced)), True)


print(f"\nDefect 3 — odd backtick parity means REFUSE, not guess")

# The shape that corrupted T222's own row — a one-backtick span whose content is
# a triple-backtick run — is ALREADY cured, by F296's run-length-exact `_SPAN_RE`.
# Measured here rather than assumed, because the row predates that fix and reads
# as though the hole were still open.
CURED = "# Note\n\nThe fence marker is ` ``` ` and a span ` -- ` after it.\n"
f = write(CURED)
before = f.read_text()
check("T222's own corrupting shape is already masked correctly (F296's `_SPAN_RE`)",
      ap._mask_code(before).split("\n")[2].count("`"), 0)
ap.fix_md_em_dash(f, f.parent, [])
check("...so the fixer leaves it alone without needing to decline",
      f.read_text(), before)

# The residue that genuinely cannot be masked is an UNPAIRED backtick: nothing
# closes it, so every span boundary after it is a guess. That is what parity
# detects, and what the fixer must refuse.
ODD = "# Note\n\nAn unclosed `span and then -- here.\n"
f = write(ODD)
before = f.read_text()
did, msg = ap.fix_md_em_dash(f, f.parent, [])
check("fixer declines rather than rewriting", did, False)
check("...leaving the file byte-identical", f.read_text(), before)
check("...and says so", "unpaired backticks" in msg, True)

check("an EVEN-parity line is still fixed normally",
      ap.fix_md_em_dash(write("# N\n\na `x` b -- c\n"), pathlib.Path("/"), [])[0], True)


print("\nIdempotence — every fixer must be a fixpoint")

for body in [PATHSPEC, PROSE, NESTED, MULTI, ODD,
             "# N\n\n```\ncode -- here\n```\n\ntext -- here\n"]:
    f = write(body)
    ap.fix_md_em_dash(f, f.parent, [])
    once = f.read_text()
    ap.fix_md_em_dash(f, f.parent, [])
    check("  fix is a fixpoint", f.read_text(), once)


print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
