#!/usr/bin/env python3
"""T089 — an F102 refusal must say which substring it read as the doc pointer.

The reproduction (2026-08-01, closing Scout T001): a Done body whose prose
described a rename as `` `prj/Ask/` `` followed by an arrow and `[[Ask Project]]`
made `state set … --status Done` refuse with *"[Done] refused: target
[[Ask Project]] has no `## Status` H2."* The arrow was ordinary prose
punctuation. What made it cost more than a retry is that the refusal named a
REAL doc with a REAL missing H2, so it read as a legitimate F102 block — the
natural repair is to go add a `## Status` block to an unrelated anchor page.

The detector stays positionless. The corpus is why: 215 rows lead with the
arrow-link, 58 put it trailing, 25 carry prose after it, so demanding the
leading slot would silently skip the F102 gate on 83 rows. A gate that quietly
stops firing is worse than one that fires loudly and explains itself.

So what is pinned here is the explanation, not a narrowing:

  1. The refusal quotes the matched `→ [[…]]` substring verbatim.
  2. When several arrows appear it says how many and which lost, because a
     second arrow is the strongest signal that one of them is prose.
  3. It says the repair is in the ROW, not in the target doc — the specific
     wrong turn the original refusal invited.
  4. Both refusal paths carry it: no-Status-H2 AND wrong-Status-word.
  5. The skip notes are untouched — a body with no arrow still skips quietly.

Run: python3 test-t089-pointer-provenance.py
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import io
import contextlib
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
loader = importlib.machinery.SourceFileLoader("be_mod", str(HERE / "backlog-edit.py"))
spec = importlib.util.spec_from_loader("be_mod", loader)
be = importlib.util.module_from_spec(spec)
sys.modules["be_mod"] = be
loader.exec_module(be)

PASS = 0
FAIL = 0


def ok(name):
    global PASS
    PASS += 1
    print(f"  PASS: {name}")


def no(name, detail=""):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {name}{(' — ' + detail) if detail else ''}")


def check(name, cond, detail=""):
    ok(name) if cond else no(name, detail)


def refusal(status, body, existing="Ready"):
    """Return the BacklogEditError text, or None if the call was allowed."""
    try:
        be.verify_status_block(status, body, existing)
        return None
    except be.BacklogEditError as err:
        return str(err)


def notes(status, body, existing="Ready"):
    """Return whatever landed on stderr (the skip notes)."""
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        try:
            be.verify_status_block(status, body, existing)
        except be.BacklogEditError:
            pass
    return buf.getvalue()


# These used to be REAL vault docs, "picked for the property each assertion
# needs rather than invented, because `find_file_by_basename` resolves against
# the live vault." That coupling broke the suite: `Tink Persona.md` was renamed
# to `Tink Persona.md`, and since the resolver is case-SENSITIVE the lookup
# returned None, so `verify_status_block` took its can't-locate-the-target skip
# path and never refused. Twelve of twenty assertions then failed on a `None`
# refusal — not one of them about pointer provenance, the thing under test.
#
# A test of a REFUSAL MESSAGE has no business depending on what the vault
# happens to contain today. Stubbing the resolver makes it hermetic: the names
# below are now arbitrary labels, and the fixture supplies the one property
# each assertion needs (a doc that exists and has no `## Status` H2).
# Restored 2026-08-18 (T245).
PROSE_TARGET = "ZZT Prose Target"      # a doc that exists, with no `## Status` H2
LOSING_TARGET = "ZZT Losing Target"    # ditto — the arrow that loses last-wins

_FIXTURES = Path(tempfile.mkdtemp(prefix="t089-"))
for _name in (PROSE_TARGET, LOSING_TARGET):
    (_FIXTURES / f"{_name}.md").write_text(
        f"---\ndescription: fixture\n---\n\n# {_name}\nNo Status H2 here.\n",
        encoding="utf-8")

_real_find = be.find_file_by_basename
be.find_file_by_basename = lambda basename: (
    p if (p := _FIXTURES / f"{basename}.md").exists() else _real_find(basename))

print("1. A prose arrow is quoted back, so the agent can see what matched")
r = refusal("Done", f"renamed `prj/Ask/` → [[{PROSE_TARGET}]] and moved the tests")
check("the call is still refused (positionless matching is unchanged)",
      r is not None)
check("the refusal still names the target it resolved",
      r and PROSE_TARGET in r, repr(r))
check("the matched substring is quoted verbatim",
      r and f"→ [[{PROSE_TARGET}]]" in r, repr(r))
check("the refusal says the arrow may be prose punctuation",
      r and "prose" in r.lower(), repr(r))
check("the refusal points the repair at THIS row, not the target doc",
      r and "in THIS row, not in the target doc" in r, repr(r))
check("the refusal names both ways out — reword, or add a real pointer",
      r and "reword" in r and "leading `→ [[F<n> — …]]`" in r, repr(r))

print("2. Multiple arrows are the strongest prose signal — say so")
two = f"moved `a/` → [[{LOSING_TARGET}]] then `b/` → [[{PROSE_TARGET}]]"
r = refusal("Done", two)
check("the count is reported", r and "holds 2 `→ [[…]]` sequences" in r, repr(r))
check("last-wins is stated explicitly", r and "LAST wins" in r, repr(r))
check("the losing arrow is named too",
      r and LOSING_TARGET in r, repr(r))
check("the winner is still the last one",
      r and f"target [[{PROSE_TARGET}]]" in r, repr(r))

print("3. A single arrow does not claim a count it does not have")
r = refusal("Done", f"→ [[{PROSE_TARGET}]]")
check("no misleading multi-arrow sentence", r and "sequences" not in r, repr(r))
check("but the matched substring is still quoted",
      r and f"→ [[{PROSE_TARGET}]]" in r, repr(r))

print("4. The wrong-Status-word path carries the same explanation")
# Both refusal paths are reachable from the same misidentification, so the
# provenance has to hang off the pointer, not off one branch.
src = (HERE / "backlog-edit.py").read_text(encoding="utf-8")
after = src.split("def verify_status_block", 1)[1]
check("provenance is appended to the no-`## Status`-H2 refusal",
      after.count("has no `## Status` H2") and
      after.split("has no `## Status` H2")[1].split("raise")[0].count("{provenance}") == 1)
check("provenance is appended to the status-mismatch refusal",
      after.split("`## Status` body begins with")[1].split("\n    #")[0]
      .count("{provenance}") == 1)
check("it is computed once, at the point the pointer is chosen",
      after.count("_pointer_provenance(body, arrow_links)") == 1)

print("5. Quiet skips stay quiet — this adds no new refusals")
check("a body with no arrow still skips",
      refusal("Done", "plain prose with [[Tink Persona]] and no arrow") is None)
check("and says so on stderr",
      "no `→ [[…]]` doc reference" in notes("Done", "plain prose, no arrow"))
check("an empty body still skips", refusal("Done", "") is None)
check("a re-touch at the same status still skips",
      refusal("Done", f"renamed `x` → [[{PROSE_TARGET}]]", existing="Done") is None)
check("an unresolvable target still skips, without provenance noise",
      refusal("Done", "moved `x` → [[No Such Doc Anywhere In The Vault]]") is None)

shutil.rmtree(_FIXTURES, ignore_errors=True)

print(f"\ntest-t089-pointer-provenance: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
