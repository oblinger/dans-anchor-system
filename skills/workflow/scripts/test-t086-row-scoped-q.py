#!/usr/bin/env python3
"""T086 — a question hosted inside a backlog row must have a resolve verb.

R-backlog-05 declares the shape legal: a row may carry its own numbered
questions as `- **Q<n> — …**` sub-bullets instead of linking a feature doc,
and `verify_questions_constraint` honours that shape when the row claims
[Questions]. No verb addressed one. `<doc> Q<n>` reaches a doc-hosted
question, `Backlog Q<n>` reaches an F275 standalone Q-row, and a row's INLINE
Q is neither — so the only way to answer one was to rewrite the whole row by
hand, which is the edit the F247 backlog stamp exists to detect. Found
2026-08-01 trying to resolve Tink T041's Q1; same defect family as T066, a
region the system declares legal to write with no sanctioned way to write it.

The address is dotted (`Backlog T041.Q1`) because F293 settled the grammar
first: the label is the third positional, so extending what may go in that
slot leaves every verb, anchor and doc argument where it was.

What the sections below pin, in the order the risk sits:

  1. The address parses, R-row dotted name-paths included, and a plain label
     is untouched by it.
  2. The pending/resolved boundary is ONE shared function — the count, the
     promise gate, and the resolve verb read the same line. This is the whole
     hazard of the feature: a resolved row-Q keeps its `- **Q<n> —` header,
     so any reader still scanning for headers now over-counts.
  3. Resolving archives the question inside the row, keeping its options,
     block-ID and lean.
  4. A `[N Questions]` bracket is recounted; a non-Questions bracket is not
     touched, and neither is one that just hit zero.
  5. The refusals name which of the three question homes was meant.
  6. `show` reads the address in either zone.

Run: python3 test-t086-row-scoped-q.py
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
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


st = _load("state_mod", HERE / "state")
be = st.be          # the module `state` actually calls — stubbing a second
                    # copy would leave every real vault hook live

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}{(' — ' + detail) if detail else ''}")


ROW = """- **T041 — migrate 4 in-skill design folders** [3 Questions] — body prose. ^T041
  - **Next:** do the mechanical part.
  - **Q1 — Which `design/` domain does `atlas` map to?** No canonical stub exists. ^T041-Q1
    - **(A)** `doc` — atlas maintains a documentation surface
    - **(B)** `search` — atlas is a lookup/routing tool
    - **(C)** `utility` — general vault-tooling bucket
    - **Recommendation:** None
  - **Q2 — Which `design/` domain does `muse` map to?** muse is audio capture. ^T041-Q2
    - **(A)** `utility` — general tooling bucket
    - **(B)** a different domain you name
    - **Recommendation:** None
"""

TMP = Path(tempfile.mkdtemp())
BL = TMP / "ZZA Track" / "ZZA Backlog.md"
BL.parent.mkdir(parents=True, exist_ok=True)

# Stub every vault-touching hook so the path never leaves the tmpdir — the
# same isolation test-f275-q-row.py uses for the standalone-Q-row verb.
be.find_backlog = lambda slug: BL
be.find_icebox = lambda slug: None
be.refresh_q_md = lambda slug: None
be.append_messages = lambda *a, **k: None
be.write_state = lambda *a, **k: None
be.heal_backlog_if_stale = lambda *a, **k: None
be._post_conditions = lambda *a, **k: []
be._selffire = lambda *a, **k: None
st._selffire = lambda *a, **k: None


def seed(row_text=ROW):
    BL.write_text(f"# ZZA Backlog\n\n## Now\n\n{row_text}\n## Later\n",
                  encoding="utf-8")


def args(label, verb, body=None, choice=None, status=None):
    return SimpleNamespace(
        doc="Backlog", label=label, verb=verb, inline=body, from_file=None,
        choice=choice, why_ask=None, horizon=None, status=status, title=None,
        next_step=None, verify=None, user=None, why_user=None,
        why_user_action=None, reason=None,
    )


def run(a):
    """Invoke cmd_item capturing stdout+stderr; return (rc, out, err)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = st.cmd_item("ZZA", TMP, a)
        except be.BacklogEditError as e:
            return 1, out.getvalue(), str(e)
    return rc, out.getvalue(), err.getvalue()


def show(label):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = st.cmd_show("ZZA", TMP, SimpleNamespace(
                doc="Backlog", label=label))
        except be.BacklogEditError as e:
            return 1, out.getvalue(), str(e)
    return rc, out.getvalue(), err.getvalue()


print("1. The dotted address parses, and only when it is really one")
check("a plain row label is not a row-scoped address",
      st.parse_row_q_label("T041") is None)
check("nor is a doc-hosted Q", st.parse_row_q_label("Q1") is None)
check("`T041.Q1` splits into row + number",
      st.parse_row_q_label("T041.Q1") == ("T041", 1))
check("a two-digit Q is not truncated",
      st.parse_row_q_label("F157.Q12") == ("F157", 12))
# `.+` is greedy on purpose: an R-row's handle is itself a dotted name-path,
# so the LAST `.Q<digits>` is the question and the rest is the row.
check("an R-row name-path keeps its own dots",
      st.parse_row_q_label("R-Scaffolding.5.2.Q3") == ("R-Scaffolding.5.2", 3))
check("a cross-anchor row id works too",
      st.parse_row_q_label("DMUX-F034.Q2") == ("DMUX-F034", 2))
check("`.Q` without a number is not an address",
      st.parse_row_q_label("T041.Qx") is None)

print("2. The pending/resolved boundary is one shared function")
sub = ROW.splitlines()[1:]
check("both questions are pending to start",
      be.count_row_pending_qs(sub) == 2, be.count_row_pending_qs(sub))
archived = sub + ["  - **Resolved**",
                  "    - **Q9 — an answered one** (resolved 2026-08-01)",
                  "      - **Resolved:** (A) — something"]
check("a question below the zone head is not pending",
      be.count_row_pending_qs(archived) == 2, be.count_row_pending_qs(archived))
check("the zone head truncates the prefix, it does not filter",
      len(be.row_pending_q_lines(archived)) == len(sub))
# audit-q must be READING this function, not carrying a copy of the old scan:
# C24 auto-fixes the bracket, so a divergent count would write the row's
# bracket back up on every run. Identity cannot be the assertion — audit-q
# loads backlog-edit under its own module name — so the check is that the
# name it exposes was DEFINED in backlog-edit, not in audit-q.
aq = _load("aq_mod", HERE.parent.parent / "audit" / "scripts" / "audit-q.py")
check("audit-q imports the boundary rather than re-expressing it",
      aq.row_pending_q_lines.__module__ == "backlog_edit_for_audit",
      aq.row_pending_q_lines.__module__)
check("and it agrees line-for-line with the copy `state` writes through",
      aq.row_pending_q_lines(archived) == be.row_pending_q_lines(archived))

print("3. Resolving archives the question inside the row")
seed()
rc, out, err = run(args("T041.Q1", "resolve", body="atlas is vault tooling.",
                        choice="(C)"))
check("the command succeeds", rc == 0, err)
text = BL.read_text(encoding="utf-8")
check("a `- **Resolved**` zone was opened", "- **Resolved**" in text, text)
check("the question is stamped resolved",
      "**Q1 — Which `design/` domain does `atlas` map to?** (resolved" in text,
      text)
check("the chosen option is named with its own text",
      "**Resolved:** (C) — `utility` — general vault-tooling bucket" in text,
      text)
check("the note is kept", "atlas is vault tooling." in text, text)
check("every option survives the archive",
      "- **(A)** `doc`" in text and "- **(B)** `search`" in text, text)
check("the block-ID rides along — inbound links keep resolving",
      "^T041-Q1" in text, text)
check("the lean is recorded apart from the outcome",
      "**Lean:** None" in text, text)
check("Q2 is untouched and still pending",
      "  - **Q2 — Which `design/` domain does `muse` map to?**" in text, text)
check("the question did not leave the row", text.count("- **T041 —") == 1, text)
check("the `- **Next:**` sub-bullet is undisturbed",
      "  - **Next:** do the mechanical part." in text, text)
check("the summary reports what is still open",
      "1 still open on the row" in out, out)
check("the backlog stamp was refreshed, so the write is not a hand-edit",
      "<!-- state:backlog " in text, text)

print("4. The bracket is recounted, and only when it is a Questions bracket")
check("[3 Questions] became [Questions] at one remaining",
      "**T041 — migrate 4 in-skill design folders** [Questions]" in text, text)
rc, out, err = run(args("T041.Q2", "resolve", body="utility.", choice="(A)"))
check("the second resolve succeeds", rc == 0, err)
text2 = BL.read_text(encoding="utf-8")
check("both archived questions share the one zone head",
      text2.count("- **Resolved**") == 1, text2)
check("Q2's archive landed under it too", "^T041-Q2" in text2, text2)
check("the row reports zero open", "0 still open on the row" in out, out)
# At zero, what the row SHOULD say next is a judgment ([Ready] needs a Next
# per F171, [Done] needs the work finished) and C24 already reports it with
# that judgment attached — so the verb declines to guess.
check("at zero the bracket is left for C24 to judge, not guessed",
      "[Questions]" in text2, text2)
# A row may legitimately host questions under another bracket — T041 itself
# sat at [Ready] with three open. Resolving one must not restatus it.
seed(ROW.replace("[3 Questions]", "[Ready]"))
rc, out, err = run(args("T041.Q1", "resolve", body="x", choice="(C)"))
check("a [Ready] row keeps its bracket",
      rc == 0 and "[Ready]" in BL.read_text(encoding="utf-8"), err)

print("5. The promise gate reads pending, not history")
answered = ("- **T041 — t** [Questions] — body\n"
            "  - **Resolved**\n"
            "    - **Q1 — done** (resolved 2026-08-01)\n"
            "      - **Resolved:** (A) — x\n")
try:
    be.verify_questions_constraint("Questions", answered, row_id="T041")
    check("a row whose every Q is archived can no longer claim [Questions]",
          False, "no refusal raised")
except be.BacklogEditError as err_:
    check("a row whose every Q is archived can no longer claim [Questions]",
          True)
    check("and the refusal is about the missing link, not the archive",
          "wiki-link" in str(err_), str(err_))
be.verify_questions_constraint("Questions", ROW, row_id="T041")
check("a row with a pending Q still honours the promise", True)

print("6. Refusals name which of the three question homes was meant")
seed()
rc, out, err = run(args("T041.Q7", "resolve", body="x", choice="(A)"))
check("an unknown Q is refused", rc != 0)
check("and the open ones are listed",
      "open questions on this row: Q1, Q2" in err, err)
run(args("T041.Q1", "resolve", body="x", choice="(C)"))
rc, out, err = run(args("T041.Q1", "resolve", body="x", choice="(A)"))
check("resolving the same Q twice is refused", rc != 0)
check("the refusal explains the archive is not re-resolvable",
      "cannot be resolved twice" in err, err)
rc, out, err = run(args("T041.Q2", "set", status="Ready"))
check("a non-resolve verb is refused on the address", rc != 0)
check("and it says only resolve takes one", "Only `resolve` does" in err, err)
rc, out, err = run(args("T041.Q2", "resolve", body="x", choice="(Z)"))
check("an option letter that is not on the list is refused", rc != 0)
check("and the real options are named",
      "(A), (B)" in err, err)

print("7. `show` reads the address too, in either zone")
rc, out, err = show("T041.Q2")
check("a pending Q prints", rc == 0 and "Q2 — Which" in out, out + err)
check("and is labelled pending", "pending)" in err, err)
rc, out, err = show("T041.Q1")
check("an already-resolved Q prints rather than reporting itself missing",
      rc == 0 and "(resolved" in out, out + err)
check("and is labelled resolved", "resolved)" in err, err)
rc, out, err = show("T041.Q7")
check("a Q that was never asked is still an error", rc != 0)

print(f"\ntest-t086-row-scoped-q: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
