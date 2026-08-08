#!/usr/bin/env python3
"""test-t131-inbox-banner.py — TINK T131 leg 2: the `Inbox N` awareness signal.

Leg 1 (`state drop`) writes a PENDING entry with no status tag — that absence
is the whole pending signal. Leg 2 surfaces the count on the Q.md banner.

**The blocker this test encodes.** `R-fct-inbox-02` says every Inbox H2 carries
a backtick-wrapped status tag, so on its face every entry `drop` writes breaks
it. That ruleset is SKA's. It is not edited here, and it does not have to be:
the counter defines PROCESSED positively against `R-fct-inbox-03`'s tag
VOCABULARY (`DONE` / `MOVED → …`) — which is undisputed, and which ATT F045 was
right to say needs no change — and counts everything else as pending. Cases D
and E are the load-bearing ones: they prove the count is indifferent to WHERE
the tag sits, which is the only thing `-02` actually governs. However SKA
settles `-02`, this count keeps working.

  A. no Inbox file → 0, and the banner omits the field entirely
  B. untagged entries are pending; the banner shows `Inbox N` in zone 1
  C. a `DONE` / `MOVED →` tag on the H2 marks an entry processed
  D. the same tag on an ATTRIBUTION LINE marks it processed too (no -02 shape)
  E. an unbacktick'd DONE in prose does NOT (the vocabulary is backticked)
  F. undated H2s are not entries; the file's head is not miscounted
  G. `Inbox 0` is omitted, so every live banner is byte-identical — which is
     why this landed with no re-render and no R-query-16 lag interval
  H. the R-query-16 lock accepts the new form AND still rejects a malformed one

Self-contained: temp dirs only."""
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def load(path, name):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


aq = load(HERE / "audit-q.py", "aq_t131")
ap = load(HERE / "audit-plan.py", "ap_t131")

PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  ok    {m}")


def no(m, got=None, want=None):
    global FAIL
    FAIL += 1
    print(f"  FAIL  {m}")
    if got is not None or want is not None:
        print(f"          got  {got!r}")
        print(f"          want {want!r}")


HEAD = ("# ZZ Inbox\n\nDrops land here newest-first; draining writes `DONE` or\n"
        "`MOVED → {destination}` per [[DAS Inbox]].\n\n")


def count(body):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "ZZ Backlog.md").write_text("# ZZ Backlog\n", encoding="utf-8")
        (root / "ZZ Inbox.md").write_text(HEAD + body, encoding="utf-8")
        return aq.count_pending_inbox("ZZ", root / "ZZ Backlog.md")


E1 = "## 2026-08-08 — First thing\n\n> a message\n\n"
E2 = "## 2026-08-07 — Second thing\n\n> another message\n\n"

# ---------------------------------------------------------------- A
print("A: no Inbox file at all")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / "ZZ Backlog.md").write_text("# ZZ Backlog\n", encoding="utf-8")
    n = aq.count_pending_inbox("ZZ", root / "ZZ Backlog.md")
ok("counts 0") if n == 0 else no("counts 0", n, 0)
b = aq.format_status_banner("A", "[[ZZ|ZZ]]", 1, 0, 1, 0, 0, 0, 0, 0, inbox=0)
if "Inbox" not in b and b.startswith("# [A]  [[ZZ|ZZ]]  -  Ready 1    User 0   |   "):
    ok("and the banner omits the field entirely")
else:
    no("and the banner omits the field entirely", b, "no Inbox field")

# ---------------------------------------------------------------- B
print("\nB: untagged entries are pending")
n = count(E1 + E2)
ok("both counted") if n == 2 else no("both counted", n, 2)
b = aq.format_status_banner("A", "[[ZZ|ZZ]]", 1, 0, 1, 0, 0, 0, 0, 0, inbox=2)
if "Ready 1    User 0    Inbox 2   |   Now 1" in b:
    ok("and it sits in zone 1, right after User, with four-space separation")
else:
    no("and it sits in zone 1, right after User", b, "…User 0    Inbox 2   |   …")

# ---------------------------------------------------------------- C
print("\nC: a sanctioned tag on the H2 marks the entry processed")
n = count("## 2026-08-08 — First thing `DONE`\n\n> a message\n\n" + E2)
ok("one pending") if n == 1 else no("one pending", n, 1)
n = count("## 2026-08-08 — First `MOVED → [[ZZ Backlog#^F001|F001]]`\n\n> m\n\n" + E2)
ok("MOVED → counts as processed too") if n == 1 else \
    no("MOVED → counts as processed too", n, 1)

# ---------------------------------------------------------------- D
print("\nD: the SAME tag on an attribution line — no dependence on -02's shape")
# This is the case that makes leg 2 unblocked. `-02` governs whether the tag
# sits on the H2; this counter never asks.
n = count("## 2026-08-08 — First thing\n\n*from: Dan · `DONE`*\n\n> a message\n\n" + E2)
ok("still processed") if n == 1 else no("still processed", n, 1)
n = count("## 2026-08-08 — First thing\n\n> a message\n\n- `MOVED → elsewhere`\n\n" + E2)
ok("…and on a sub-bullet too") if n == 1 else no("…and on a sub-bullet too", n, 1)

# ---------------------------------------------------------------- E
print("\nE: an unbackticked DONE in prose is not a tag")
n = count("## 2026-08-08 — First thing\n\n> we are DONE arguing about this\n\n" + E2)
ok("still pending") if n == 2 else no("still pending", n, 2)

# ---------------------------------------------------------------- F
print("\nF: only dated H2s are entries")
n = count("## Notes\n\nsome prose\n\n" + E1)
ok("the undated H2 is not counted") if n == 1 else \
    no("the undated H2 is not counted", n, 1)
n = count("")
ok("an entry-less file counts 0") if n == 0 else no("an entry-less file counts 0", n, 0)

# ---------------------------------------------------------------- G
print("\nG: Inbox 0 leaves the banner byte-identical to the pre-T131 form")
old = ("# [A]  [[ZZ queries|ZZ]]  -  Ready 1    User 0   |   "
       "Now 1    Next 0    Later 0   |   Parked 0    Waiting 0    Icebox 0")
new = aq.format_status_banner("A", "[[ZZ queries|ZZ]]", 1, 0, 1, 0, 0, 0, 0, 0)
ok("identical") if new == old else no("identical", new, old)
# …and the live vault is in that state, which is why no re-render was needed.
live = [p for p in (Path.home() / "ob" / "kmr").rglob("* Inbox.md")
        if not any(x in p.parts for x in (".trash", "Yore", "Closet"))]
pend = sum(aq.count_pending_inbox(p.name[:-len(" Inbox.md")],
                                  p.parent / f"{p.name[:-len(' Inbox.md')]} Backlog.md")
           for p in live)
print(f"        (live vault: {len(live)} Inbox files, {pend} pending entries)")

# ---------------------------------------------------------------- H
print("\nH: R-query-16 moved in the same pass as the format string")
with tempfile.TemporaryDirectory() as td:
    q = Path(td) / "ZZ queries.md"
    for label, banner, want in (
            ("with Inbox",
             aq.format_status_banner("A", "[[ZZ|ZZ]]", 1, 0, 1, 0, 0, 0, 0, 0,
                                     inbox=3), "pass"),
            ("without Inbox",
             aq.format_status_banner("A", "[[ZZ|ZZ]]", 1, 0, 1, 0, 0, 0, 0, 0),
             "pass"),
            ("with Inbox AND the {N} suffix",
             aq.format_status_banner("A", "[[ZZ|ZZ]]", 1, 0, 1, 0, 0, 0, 0, 0,
                                     "    {4}", inbox=3), "pass"),
            ("single-spaced (malformed)",
             "# [A]  [[ZZ|ZZ]]  -  Ready 1 User 0 | Now 1 Next 0 Later 0 | "
             "Parked 0 Waiting 0 Icebox 0", "fail"),
            ("Inbox in the wrong zone",
             "# [A]  [[ZZ|ZZ]]  -  Ready 1    User 0   |   Now 1    Next 0    "
             "Later 0   |   Inbox 3    Parked 0    Waiting 0    Icebox 0",
             "fail")):
        q.write_text(banner + "\n\nbody\n", encoding="utf-8")
        got = ap.chk_queries_banner_form(q, Path(td), [])[0]
        ok(f"{label} → {want}") if got == want else \
            no(f"{label} → {want}", got, want)

print("\n" + "-" * 40)
print(f"test-t131-inbox-banner: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
