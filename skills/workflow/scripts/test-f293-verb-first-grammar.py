#!/usr/bin/env python3
"""F293 — the v3 grammar: `state <verb> <anchor> <doc> [<label>] [flags]`.

Three changes that only work together, and the reason they had to land as one:

  * **Verb-first** is what makes per-verb flag schemas possible. v2 had to
    consume the address before it knew the verb, so every flag was declared
    globally and all thirteen printed on every invocation — `--horizon` in
    `resolve`'s usage line, `--choice` in `set`'s.
  * **Dropping cwd-inference** is what makes the address positional. The anchor
    was a flag only because it was optional, and an optional argument cannot
    sit in the middle of other positionals.
  * **Positional address** is what the first two buy.

What this pins, in the order the assertions run:

  1. Each verb's usage carries its own flags and NOT its siblings'.
  2. A flag a verb does not declare is rejected by name, by argparse — not by
     a runtime `if` inside the handler (which is how v2 refused `set
     --from-file`).
  3. The anchor is mandatory on EVERY verb, item and domain alike.
  4. Nothing infers an anchor from the working directory: standing inside an
     anchor does not make a bad anchor argument resolve.
  5. `revalidate` declares no label, so the shape that v2 needed a last-token
     heuristic to recognize is now a parse error.
  6. The retired grammars — v2's address-first form and F236's `task`/`q`
     domains — get named migrations, not argparse's "invalid choice".

Run: python3 test-f293-verb-first-grammar.py
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import contextlib
import importlib.machinery
import importlib.util
import io
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
loader = importlib.machinery.SourceFileLoader("state_mod", str(HERE / "state"))
spec = importlib.util.spec_from_loader("state_mod", loader)
st = importlib.util.module_from_spec(spec)
sys.modules["state_mod"] = st
loader.exec_module(st)
be = st.be

PASS = 0
FAIL = 0


def ok(name):
    global PASS
    PASS += 1
    print(f"  PASS: {name}")


def no(name):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {name}")


def check(name, cond, detail=""):
    ok(name) if cond else no(f"{name}{(' — ' + detail) if detail else ''}")


def usage(verb):
    """The verb's own --help text."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            st.build_parser().parse_args([verb, "--help"])
        except SystemExit:
            pass
    return buf.getvalue()


def parses(argv):
    """True if argv parses; argparse exits on failure."""
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        try:
            st.build_parser().parse_args(argv)
            return True
        except SystemExit:
            return False


print("1. Each verb's help shows its own flags and not its siblings'")
# The concrete v2 complaint: thirteen flags on every usage line regardless of
# which verb ran. Each row is (verb, must-list, must-NOT-list).
for verb, present, absent in [
    ("resolve", ["--choice"], ["--horizon", "--status", "--why-ask", "--reason"]),
    ("set", ["--status", "--horizon", "--title", "--next", "--verify", "--user"],
     ["--choice", "--why-ask", "--reason", "--from-file"]),
    ("define", ["--horizon", "--why-ask", "--from-file"],
     ["--choice", "--status", "--title", "--reason"]),
    ("remove", ["--reason"], ["--choice", "--horizon", "--status", "--body"]),
    ("revalidate", [], ["--choice", "--horizon", "--status", "--body", "--reason"]),
]:
    text = usage(verb)
    for flag in present:
        check(f"{verb} --help lists {flag}", flag in text)
    for flag in absent:
        check(f"{verb} --help does NOT list {flag}", flag not in text)

print("2. An undeclared flag is refused by the schema, not by a runtime check")
check("set accepts --status", parses(["set", "ZZ", "Backlog", "T1", "--status", "Done"]))
check("set REFUSES --from-file (v2 refused this inside the handler)",
      not parses(["set", "ZZ", "Backlog", "T1", "--from-file", "/tmp/x"]))
check("set REFUSES --choice", not parses(["set", "ZZ", "Backlog", "T1", "--choice", "(A)"]))
check("resolve REFUSES --horizon",
      not parses(["resolve", "ZZ", "Backlog", "T1", "--horizon", "Now"]))
check("define REFUSES --reason",
      not parses(["define", "ZZ", "Backlog", "T1", "--reason", "why"]))
# T057: `define --title` parsed, ran, reported success, and silently dropped the
# title — a Q rendered `- **Q1 — Untitled**`. No handler ever read it; it was
# only reachable because v2 declared every flag on every verb. `define` takes
# its title from the body's first line, so the schema simply does not have one.
check("define REFUSES --title (T057's silent discard, structurally)",
      not parses(["define", "ZZ", "MyDoc", "Q1", "--title", "Real title"]))

print("3. The anchor is mandatory on every verb")
for argv, desc in [
    (["define", "ZZ", "Backlog", "F+"], "define"),
    (["set", "ZZ", "Backlog", "F1"], "set"),
    (["resolve", "ZZ", "Backlog", "F1"], "resolve"),
    (["remove", "ZZ", "Backlog", "F1"], "remove"),
    (["revalidate", "ZZ", "MyDoc"], "revalidate"),
    (["triage", "ZZ"], "triage"),
    (["crank", "ZZ", "start"], "crank"),
    (["groom-list", "ZZ"], "groom-list"),
    (["summary-line", "ZZ", "--recommend", "crank"], "summary-line"),
    (["status", "ZZ", "show"], "status"),
    (["roadmap", "ZZ", "status", "get", "--feature", "F1"], "roadmap"),
]:
    check(f"{desc} parses with an anchor", parses(argv))
    without = [argv[0]] + argv[2:]
    check(f"{desc} REFUSES a missing anchor", not parses(without),
          f"parsed {without!r}")
check("no verb accepts -a/--anchor any more",
      not parses(["set", "--anchor", "ZZ", "Backlog", "T1", "--status", "Done"]))

print("4. Anchor resolution never consults the working directory")
with tempfile.TemporaryDirectory() as td:
    root = Path(td) / "Fixture"
    (root / "Fixture Track").mkdir(parents=True)
    (root / ".anchor").write_text("slug: ZZV\n", encoding="utf-8")
    (root / "Fixture Track" / "ZZV Backlog.md").write_text(
        "# ZZV Backlog\n\n## Now\n\n## Done\n", encoding="utf-8")
    deep = root / "Fixture Track"
    prev = os.getcwd()
    try:
        os.chdir(deep)
        # v2 mode 3 walked UP from here, found `.anchor`, and silently used it.
        try:
            st.resolve_anchor("NoSuchAnchorAnywhere")
            no("standing inside an anchor still resolves a bad anchor argument")
        except be.BacklogEditError as err:
            check("a bad anchor errors even while standing inside a real one",
                  "NoSuchAnchorAnywhere" in str(err), str(err))
        slug, path = st.resolve_anchor(str(root))
        check("an explicit path still resolves, and reads its slug",
              (slug, path.resolve()) == ("ZZV", root.resolve()),
              f"{slug} {path}")
    finally:
        os.chdir(prev)

print("5. The doc verb declares no label")
check("revalidate takes <anchor> <doc>", parses(["revalidate", "ZZ", "MyDoc"]))
check("revalidate REFUSES a label", not parses(["revalidate", "ZZ", "MyDoc", "Q1"]))

print("6. Retired grammars get a named migration")
tomb = st._tombstone(["state", "Backlog", "F5", "set", "--status", "Done"])
check("a v2-form call is tombstoned, not left to argparse", tomb is not None)
check("the tombstone names F293", tomb and "F293" in tomb, repr(tomb))
check("the tombstone shows the v3 shape",
      tomb and "state <verb> <anchor> <doc>" in tomb, repr(tomb))
check("`state task` keeps its own F236 migration",
      (st._tombstone(["state", "task", "create"]) or "").count("F236") == 1)
check("`state q` keeps its own F236 migration",
      (st._tombstone(["state", "q", "add"]) or "").count("F236") == 1)
check("a real verb is not tombstoned",
      st._tombstone(["state", "resolve", "ZZ", "Backlog", "Q1"]) is None)

print(f"\ntest-f293-verb-first-grammar: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
