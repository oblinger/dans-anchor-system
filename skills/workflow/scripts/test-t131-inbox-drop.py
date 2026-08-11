#!/usr/bin/env python3
"""test-t131-inbox-drop.py — TINK T131 leg 1: the agent-inbox drop API.

`state drop <anchor> "<message>"` appends ONE pending entry to the target
anchor's [[DAS Inbox]] file — the sender half of the pattern designed at
[[ATT045 - Agent inbox pattern]]. Nothing executes; the entry waits for the
drain.

Two properties carry the whole design and are what this test is really for:

  * **An entry with NO status tag is PENDING.** ATT F045 settled the pending /
    drained distinction without new vocabulary — the drain writes `DONE` or
    `MOVED → {destination}` (R-fct-inbox-03), and their absence is the pending
    signal. So a dropped entry must carry no backtick-wrapped token on its H2,
    and a derived topic must have its backticks stripped, or a topic quoting a
    word would read as a status to every reader.
  * **`--tag` is a message TYPE, not a status.** `fact`/`handoff`/`note`/`nudge`
    say what the message IS; `DONE`/`MOVED →` say what happened to it. Two
    vocabularies, and the type must never land on the heading line.

  A. first drop  — creates the file from the standard template, entry included
  B. no tag      — the H2 carries no status; the pending signal is intact
  C. newest-first — a second drop lands ABOVE the first, below the head
  D. shape       — attribution line, blockquote, multi-line and blank lines
  E. topic       — derived at the first sentence, `--topic` wins, backticks go
  F. path        — the Inbox prefix comes off the BACKLOG filename, not the slug
  G. refusals    — an empty message refuses; nothing is created

Self-contained: loads `state` in-process against a tmpdir fixture anchor and
stubs every seam that reaches the real vault. Never touches the real vault."""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
_loader = importlib.machinery.SourceFileLoader("state_mod", str(HERE / "state"))
_spec = importlib.util.spec_from_loader("state_mod", _loader)
st = importlib.util.module_from_spec(_spec)
sys.modules["state_mod"] = st
_loader.exec_module(st)
be = st.be

st._selffire = lambda *a, **k: None
be._selffire = lambda *a, **k: None
be.append_messages = lambda *a, **k: None

PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  PASS: {m}")


def no(m):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {m}")


TODAY = date.today().isoformat()


class Args:
    def __init__(self, **kw):
        self.message = None
        self.source = None
        self.tag = None
        self.topic = None
        self.from_file = None
        self.__dict__.update(kw)


TMP = Path(tempfile.mkdtemp())
try:
    # A fixture anchor whose DISPLAY name differs from its slug — the exact
    # `Scout Backlog.md` vs `slug: SCOUT` shape that makes deriving the Inbox
    # filename from the slug wrong.
    anchor = TMP / "Zeta"
    track = anchor / "Zeta Track"
    track.mkdir(parents=True)
    (anchor / ".anchor").write_text("slug: ZZT\n", encoding="utf-8")
    backlog = track / "Zeta Backlog.md"
    backlog.write_text("# Zeta Backlog\n\n## Now\n\n"
                       "- **T900 — a row** [Ready] — body. ^T900\n",
                       encoding="utf-8")
    be.find_backlog = lambda slug: backlog
    inbox = track / "Zeta Inbox.md"

    def drop(message=None, **kw):
        return st.cmd_drop("Zeta", anchor, Args(message=message, **kw))

    # ---- A: first drop creates the file ----------------------------------
    print("== A: the first drop creates the Inbox from the standard template ==")
    rc = drop("Family names for the roster are in the shared doc. Please file them.",
              source="atticus", tag="handoff")
    if rc == 0 and inbox.is_file():
        ok("drop returned 0 and created the Inbox file")
    else:
        no(f"rc={rc}, exists={inbox.is_file()}")
    txt = inbox.read_text(encoding="utf-8")
    head_ok = (txt.startswith("---\n")
               and "description: Zeta inbox" in txt
               and "\n# Zeta Inbox\n" in txt
               and "| -[[Zeta Inbox]]- | |" in txt
               and "| --- | |" in txt)
    if head_ok:
        ok("frontmatter + H1 + dispatch-table placeholder all present")
    else:
        no(f"template head is wrong:\n{txt[:300]}")

    # ---- B: no status tag — the pending signal ---------------------------
    print("== B: the entry carries NO status tag (that absence IS 'pending') ==")
    h2 = next(l for l in txt.splitlines() if l.startswith("## "))
    if h2 == f"## {TODAY} — Family names for the roster are in the shared doc":
        ok("H2 is `## YYYY-MM-DD — Topic` and nothing else")
    else:
        no(f"unexpected H2: {h2!r}")
    if "`" not in h2:
        ok("no backtick-wrapped token on the H2 line")
    else:
        no(f"H2 carries a backticked token — reads as a status tag: {h2!r}")
    if "DONE" not in txt.split("## ")[1] and "MOVED →" not in txt.split("## ")[1]:
        ok("neither sanctioned status tag was written by the drop")
    else:
        no("the drop wrote a status tag — the entry is not pending")
    # The type label rides the attribution line, never the heading.
    if "handoff" not in h2 and "*from: atticus · tag: handoff*" in txt:
        ok("--tag rode the attribution line, not the heading")
    else:
        no("--tag landed on the heading, where it reads as a status")

    # ---- C: newest-first --------------------------------------------------
    print("== C: a second drop lands ABOVE the first, below the file head ==")
    drop("Second message about the deploy window.", source="user")
    txt2 = inbox.read_text(encoding="utf-8")
    order = [l for l in txt2.splitlines() if l.startswith("## ")]
    if len(order) == 2 and "Second message" in order[0] and "Family names" in order[1]:
        ok("newest entry is first")
    else:
        no(f"ordering wrong: {order}")
    if txt2.index("# Zeta Inbox") < txt2.index("## "):
        ok("the H1 and dispatch table stayed above every entry")
    else:
        no("an entry was spliced above the file head")
    if "| --- | |" in txt2 and txt2.index("| --- | |") < txt2.index("## "):
        ok("the dispatch-table placeholder is untouched and still above")
    else:
        no("the dispatch table was disturbed")

    # ---- D: entry shape ---------------------------------------------------
    print("== D: multi-line messages become blockquotes, blank lines included ==")
    drop("First para line one.\nline two.\n\nSecond para.", topic="Shape check")
    body = inbox.read_text(encoding="utf-8").split(f"## {TODAY} — Shape check")[1]
    body = body.split("\n## ")[0]
    quoted = [l for l in body.splitlines() if l.startswith(">")]
    if quoted == ["> First para line one.", "> line two.", ">", "> Second para."]:
        ok("every message line is quoted; the blank line became a bare `>`")
    else:
        no(f"blockquote wrong: {quoted}")
    if "*from:" not in body and "*tag:" not in body:
        ok("no attribution line when neither --source nor --tag is given")
    else:
        no("an empty attribution line was emitted")

    # ---- E: topic derivation ----------------------------------------------
    print("== E: topic derivation — first sentence, --topic wins, backticks go ==")
    if st._inbox_topic("Short one. And a second sentence here.") == "Short one":
        ok("cut at the first sentence end, not at a character count")
    else:
        no(f"got {st._inbox_topic('Short one. And a second sentence here.')!r}")
    long_msg = "x" * 200
    t = st._inbox_topic(long_msg)
    if len(t) <= st._INBOX_TOPIC_MAX and t.endswith("…"):
        ok(f"a sentence-less message truncates to <= {st._INBOX_TOPIC_MAX} with an ellipsis")
    else:
        no(f"truncation wrong: {len(t)} chars, {t[-3:]!r}")
    if st._inbox_topic("ignored", explicit="Explicit headline") == "Explicit headline":
        ok("--topic wins over derivation")
    else:
        no("--topic was ignored")
    if "`" not in st._inbox_topic("The `DONE` flag is stuck on rebuild"):
        ok("backticks are stripped — a topic can never impersonate a status tag")
    else:
        no("a backticked topic survived: it would read as a status tag")
    if st._inbox_topic("- > **A markdown-marked opening.** rest") \
            .startswith("A markdown-marked opening"):
        ok("leading list/quote/bold markers are stripped from the topic")
    else:
        no(f"markers survived: {st._inbox_topic('- > **A markdown-marked opening.** rest')!r}")

    # ---- F: the path comes off the BACKLOG name ---------------------------
    print("== F: the Inbox prefix is the Backlog's prefix, not the slug ==")
    p, bl = st._inbox_path("Zeta", anchor)
    if p == track / "Zeta Inbox.md":
        ok("`Zeta Backlog.md` → `Zeta Track/Zeta Inbox.md` (slug is ZZT)")
    else:
        no(f"resolved to {p}")
    if bl == backlog:
        ok("the backlog path is returned for the Messages log")
    else:
        no("the backlog path was not returned")
    # No backlog at all → fall back to the single Track folder, never guess.
    bare = TMP / "Bare"
    (bare / "Bare Track").mkdir(parents=True)
    (bare / ".anchor").write_text("slug: BARE\n", encoding="utf-8")

    def _raise(slug):
        raise be.BacklogEditError("no backlog")
    _saved, be.find_backlog = be.find_backlog, _raise
    try:
        p2, bl2 = st._inbox_path("Bare", bare)
        if p2 == bare / "Bare Track" / "Bare Inbox.md" and bl2 is None:
            ok("a backlog-less anchor falls back to its one Track folder")
        else:
            no(f"fallback resolved to {p2}")
        empty = TMP / "Empty"
        empty.mkdir()
        try:
            st._inbox_path("Empty", empty)
            no("an anchor with no Track folder should refuse")
        except be.BacklogEditError as ex:
            ok("no Track folder refuses rather than inventing a location") \
                if "Track" in str(ex) else no(f"wrong message: {ex}")
    finally:
        be.find_backlog = _saved

    # ---- G: refusals -------------------------------------------------------
    print("== G: an empty message refuses and creates nothing ==")
    fresh = TMP / "Fresh"
    (fresh / "Fresh Track").mkdir(parents=True)
    (fresh / ".anchor").write_text("slug: FRSH\n", encoding="utf-8")
    fresh_bl = fresh / "Fresh Track" / "Fresh Backlog.md"
    fresh_bl.write_text("# Fresh Backlog\n\n## Now\n", encoding="utf-8")
    _saved2, be.find_backlog = be.find_backlog, lambda slug: fresh_bl
    try:
        try:
            st.cmd_drop("Fresh", fresh, Args(message="   \n  \n"))
            no("a whitespace-only message should refuse")
        except be.BacklogEditError as ex:
            ok("an empty message refuses") if "requires a message" in str(ex) \
                else no(f"wrong message: {ex}")
        if not (fresh / "Fresh Track" / "Fresh Inbox.md").exists():
            ok("the refused drop created no Inbox file")
        else:
            no("a refused drop still created the Inbox")
    finally:
        be.find_backlog = _saved2
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
