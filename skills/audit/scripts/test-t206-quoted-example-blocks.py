#!/usr/bin/env python3
"""test-t206-quoted-example-blocks.py — a QUOTED masthead is not the page's own.

`Spine` skipped code fences for exactly this reason: a spec page that shows the
house head as a template would otherwise read as carrying a real breadcrumb on
top of its real masthead. `design/Template Examples.md` quotes real pages
**verbatim and unfenced** on purpose — its own § names that as an accepted cost
of a copy-pasteable corpus — so the fence test could not see any of it.

Two checkers then got the same file wrong at once, and neither noticed:

  - A spine sweep HOISTED example T1.a's quoted `[[HERMES Backlog]]` masthead
    out of its block and installed it as `Template Examples.md`'s own identity
    row (`07414a8e`, `9e5542b6`). The page then declared itself to be a
    different page — the failure `R-spine.md` warns about in its own text,
    where it refuses to print a live specimen for this reason.
  - The `S04` fixer rewrote example T6.b's quoted `[[DKT Track]]` identity cell
    to lead with its description, while the real `DKT Track.md` it quotes still
    leads with its breadcrumb. It repaired the evidence and left the defect.

Neither checker reported anything. What caught it was T177's manifest hashes in
`Stencil/engine/test_sten_corpus_integrity.py`, which are the only instrument in
the system that grades a quoted specimen against the bytes it is supposed to
quote — and both specimens were restored to bytes those hashes confirm.

Case 3 is the one to keep. Covering only `example` left the page's detected
identity row on a `| -[[{{TITLE}}]]- |` masthead inside a `proposal` block —
the same defect one delimiter over, found by re-running the classifier rather
than by trusting the fix.

Usage: python3 test-t206-quoted-example-blocks.py
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


sp = _load("spine")

QUOTED_MASTHEAD = (
    "| -[[HERMES Backlog]]- | → [[kmr]] → [[SYS]] → [HERMES Backlog](hook://p/X) |\n"
    "| --- | --- |\n"
    "| ... | [[HERMES Messages]],   |\n"
)


def page(body, name="Corpus.md"):
    td = tempfile.mkdtemp()
    p = Path(td) / name
    p.write_text(body, encoding="utf-8")
    return sp.Spine(p)


# 1 — a masthead inside `<!-- begin example -->` is not this page's spine.
s = page("# Corpus\nWhat this is.\n\n"
         "<!-- begin example T1.a -->\n" + QUOTED_MASTHEAD + "<!-- end example T1.a -->\n")
check(s.table_start is None, "a masthead inside an example block is not the page's own")
check(s.shape() == "none", "...so the page's shape is `none`, not `curated`")

# 2 — a quoted `:>>` breadcrumb likewise. This is the direction the fence test
#     was originally added for, now reached through the other delimiter.
s = page("# Corpus\nWhat this is.\n\n"
         "<!-- begin example T2.a -->\n:>> [[kmr]] → [Thing](hook://p/Thing)\n"
         "<!-- end example T2.a -->\n")
check(s.breadcrumb is None, "a breadcrumb inside an example block is not the page's own")

# 3 — the `proposal` delimiter is load-bearing. Covering only `example` left a
#     `| -[[{{TITLE}}]]- |` masthead as the real corpus page's identity row.
s = page("# Corpus\nWhat this is.\n\n"
         "<!-- begin proposal T6.A -->\n| -[[{{TITLE}}]]- | {{IDENTITY}} |\n"
         "| --- | --- |\n<!-- end proposal T6.A -->\n")
check(s.table_start is None, "a masthead inside a PROPOSAL block is not the page's own")

# 4 — the page's REAL spine still registers, above and below a quoted block.
#     Without this the fix would trade a false positive for a false negative.
s = page("| -[[Corpus]]- | : the corpus.<br>→ [[kmr]] → [Corpus](hook://p/Corpus) |\n"
         "| --- | --- |\n| ... | [[Other]],   |\n\n"
         "# Corpus\nWhat this is.\n\n"
         "<!-- begin example T1.a -->\n" + QUOTED_MASTHEAD + "<!-- end example T1.a -->\n")
check(s.table_start == 0, "the page's own masthead above a quoted block still registers")
check(s.marker == "...", "...including its marker")

s = page("# Corpus\nWhat this is.\n\n"
         "<!-- begin example T1.a -->\n" + QUOTED_MASTHEAD + "<!-- end example T1.a -->\n\n"
         ":>> [[kmr]] → [Corpus](hook://p/Corpus)\n")
check(s.breadcrumb is not None, "the page's own breadcrumb BELOW a quoted block still registers")

# 5 — code fences keep working. The mask gained a delimiter; it must not have
#     traded one for the other.
s = page("# Corpus\nWhat this is.\n\n```markdown\n" + QUOTED_MASTHEAD + "```\n")
check(s.table_start is None, "a fenced masthead is still skipped")

# 6 — an unterminated example block does not swallow the rest of the file into
#     "quoted" and blind every later check. A half-written page is a premise
#     this system has already been burned by (T187).
s = page("<!-- begin example T1.a -->\n" + QUOTED_MASTHEAD +
         "\n# Corpus\nWhat this is.\n")
check(all(s.quoted[1:4]), "an unterminated block still quotes what follows it")
check(s.h1 is not None, "...and the H1 is still located, since `_head_h1` reads text")

print(f"\nT206 quoted example blocks: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
