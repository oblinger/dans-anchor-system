#!/usr/bin/env python3
"""test-t131-inbox-drain.py — T131 leg 3: the drain round-trips.

Seeds a scratch Inbox with N pending entries, drains them through the real
`state inbox-tag` CLI (in-process, argv and all — not just the bare
function), and asserts three things agree afterward: every drained entry
carries a well-formed status tag, `count_pending_inbox` (audit-q.py) reads
0, and the three R-fct-inbox checkers (audit-plan.py) all pass. All three
are IMPORTED, not restated — the failure this project already shipped once
was a drain that disagreed with the `Inbox N` banner about which entries
were pending, because each side spelled out its own copy of the rule.

Part 2 is the RED CHECK: if this file's Part 1 assertions can pass against
a tag-writer that is secretly a no-op (or one that writes an unsanctioned
tag), the test proves nothing. Two broken stub writers are run as real
subprocesses (not just a monkeypatched in-process function — the concrete
failure mode is a shipped SCRIPT that silently does the wrong thing) and
the same three-way check above must go RED against each.

Anti-stale-bytecode discipline (the trap this repo has been burned by
before): a `__pycache__` entry invalidates on (mtime, size), not content,
so two same-length stub variants written to the same path within the same
wall-clock second can serve the FIRST one's cached bytecode to the SECOND
run and silently report the wrong stub's behavior. Guarded three ways here:
every stub subprocess runs under `python3 -B` (never WRITES a new cache
entry), `__pycache__` beside the stub path is removed before every run
(never READS a stale one), and the two stub bodies are padded to distinct
lengths (so even a same-second write can't alias on (mtime, size)).

Self-contained: scratch anchors live in tempdirs; nothing under `~/ob/kmr`
is touched, and neither is HA's real (live, two-agent-owned) Inbox.
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT_SCRIPTS = HERE.parent.parent / "audit" / "scripts"
STATE_PATH = HERE / "state"

PASS = 0
FAIL = 0


def ok(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {label}")
    else:
        FAIL += 1
        print(f"  FAIL: {label}")


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


# The three imports under test — the whole point is that THIS file never
# restates count_pending_inbox's regexes or the checkers' logic; it only
# calls them.
state_mod = _load("state_t131_test", STATE_PATH)
audit_q = _load("audit_q_t131_test", AUDIT_SCRIPTS / "audit-q.py")
audit_plan = _load("audit_plan_t131_test", AUDIT_SCRIPTS / "audit-plan.py")

SLUG = "ZZZDRAIN"

ENTRIES = [
    ("2026-08-01", "Alpha entry", "Alpha body text."),
    ("2026-08-02", "Beta entry", "Beta body text."),
    ("2026-08-03", "Gamma entry", "Gamma body text."),
]

HEAD = (
    "---\n"
    f"description: {SLUG} inbox — raw input dropped for later processing.\n"
    "---\n"
    f"\n# {SLUG} Inbox\n"
    "Drop zone for raw input; an entry with no status tag is pending, and "
    "draining writes `DONE` or `MOVED → {destination}` per [[DAS Inbox]].\n"
    f"\n| -[[{SLUG} Inbox]]- | |\n"
    "| --- | --- |\n"
    "| --- | |\n"
)


def seed_anchor(root):
    """A fresh scratch anchor with N pending entries. Returns (anchor_dir,
    inbox_path, backlog_path)."""
    root = Path(root)
    track = root / f"{SLUG} Track"
    track.mkdir(parents=True, exist_ok=True)
    (root / ".anchor").write_text(f"slug: {SLUG}\n", encoding="utf-8")
    backlog = track / f"{SLUG} Backlog.md"
    backlog.write_text(
        f"---\ndescription: scratch\n---\n\n# {SLUG} Backlog\n\n## Now\n\n"
        "## Next\n\n## Later\n\n## Icebox\n\n## Done\n",
        encoding="utf-8")
    body = HEAD
    # Newest-first, same order `drop` would leave them in.
    for date, topic, text in reversed(ENTRIES):
        body += f"\n## {date} — {topic}\n\n> {text}\n"
    inbox = track / f"{SLUG} Inbox.md"
    inbox.write_text(body, encoding="utf-8")
    return root, inbox, backlog


def three_way_check(inbox_path, backlog_path):
    """(all_tagged, pending_count, checker_results) — the same three facts
    the real drain must leave agreeing."""
    text = inbox_path.read_text(encoding="utf-8")
    all_tagged = all(
        f"## {date} — {topic}" in text
        and audit_q._INBOX_DONE_RE.search(
            text.splitlines()[
                [i for i, l in enumerate(text.splitlines())
                 if l.startswith(f"## {date} — {topic}")][0]])
        for date, topic, _ in ENTRIES
    )
    pending = audit_q.count_pending_inbox(SLUG, backlog_path)
    checks = {
        "in_track_folder": audit_plan.chk_inbox_in_track_folder(inbox_path, None, {})[0],
        "entry_headings": audit_plan.chk_inbox_entry_headings(inbox_path, None, {})[0],
        "status_tags": audit_plan.chk_inbox_status_tags(inbox_path, None, {})[0],
    }
    return all_tagged, pending, checks


print("1. ROUND TRIP — drain N pending entries through the real CLI")

with tempfile.TemporaryDirectory() as tmp:
    anchor_dir, inbox_path, backlog_path = seed_anchor(tmp)

    pending_before = audit_q.count_pending_inbox(SLUG, backlog_path)
    ok(pending_before == len(ENTRIES),
       f"seed: {len(ENTRIES)} entries all read as pending ({pending_before})")

    tags = ["DONE", "MOVED → ZZZDRAIN Roadmap#M1", "DONE"]
    for (date, topic, _text), tag in zip(ENTRIES, tags):
        rc = state_mod.main(
            ["state", "inbox-tag", str(anchor_dir), "--date", date,
             "--topic", topic, "--tag", tag])
        ok(rc == 0, f"inbox-tag {date} — {topic!r} → {tag!r} exits 0")

    all_tagged, pending, checks = three_way_check(inbox_path, backlog_path)
    ok(all_tagged, "every drained entry's heading now carries a status tag")
    ok(pending == 0, f"count_pending_inbox (imported) now reads 0 (got {pending})")
    for name, status in checks.items():
        ok(status == "pass", f"chk_inbox_{name} (imported) passes on the drained file")

    # Idempotency / vocabulary guards, still through the real CLI.
    rc = state_mod.main(["state", "inbox-tag", str(anchor_dir), "--date", ENTRIES[0][0],
                          "--topic", ENTRIES[0][1], "--tag", "DONE"])
    ok(rc != 0, "re-tagging an already-processed entry is refused")

    rc = state_mod.main(["state", "inbox-tag", str(anchor_dir), "--date", "2099-01-01",
                          "--tag", "MOVED"])
    ok(rc != 0, "a bare MOVED with no destination is refused")


print("\n2. RED CHECK — a broken writer must make the SAME check go red")

STUB_ARGS_DOC = """Each stub takes: <inbox_path> <date> <topic-substring> <tag>
and is expected to behave like the sanctioned writer for that one call —
except each is deliberately broken in a specific, named way.
"""

STUB_NOOP = '''#!/usr/bin/env python3
""" {pad} """
import sys
# Deliberately broken: claims success, writes nothing at all.
inbox_path, date, topic, tag = sys.argv[1:5]
print(f"tagged {{date}} (NOOP STUB — nothing actually written)")
sys.exit(0)
'''

STUB_WRONGTAG = '''#!/usr/bin/env python3
""" {pad} """
import re
import sys

# Deliberately broken: writes an UNSANCTIONED tag instead of the one asked for.
inbox_path, date, topic, _tag = sys.argv[1:5]
p = sys.argv[1]
lines = open(p, encoding="utf-8").read().splitlines()
pat = re.compile(r"^## " + re.escape(date) + r" — .*" + re.escape(topic) + r".*$")
for i, line in enumerate(lines):
    if pat.match(line):
        lines[i] = line + "    `HANDLED`"     # not in the sanctioned vocabulary
        break
open(p, "w", encoding="utf-8").write("\\n".join(lines) + "\\n")
sys.exit(0)
'''


def run_stub(stub_dir, src_template, pad_len, inbox_path, date, topic, tag):
    """Write ONE stub to a FIXED path (same path reused across variants —
    that's the actual collision risk), clear any pycache next to it so a
    stale entry can't be read, and run it under `-B` so it can't write a
    fresh one either. `pad_len` gives each variant a distinct file size."""
    stub_path = stub_dir / "stub_writer.py"
    src = src_template.format(pad="x" * pad_len)
    stub_path.write_text(src, encoding="utf-8")
    pycache = stub_dir / "__pycache__"
    if pycache.is_dir():
        shutil.rmtree(pycache)
    r = subprocess.run(
        [sys.executable, "-B", str(stub_path), str(inbox_path), date, topic, tag],
        capture_output=True, text=True, timeout=30)
    return r


with tempfile.TemporaryDirectory() as tmp:
    stub_dir = Path(tmp) / "stubs"
    stub_dir.mkdir()

    # --- Variant A: no-op writer -------------------------------------------
    with tempfile.TemporaryDirectory() as tmp2:
        anchor_dir, inbox_path, backlog_path = seed_anchor(tmp2)
        for date, topic, _ in ENTRIES:
            r = run_stub(stub_dir, STUB_NOOP, 37, inbox_path, date, topic, "DONE")
            ok(r.returncode == 0, f"NOOP stub subprocess itself ran cleanly ({date})")
        all_tagged, pending, checks = three_way_check(inbox_path, backlog_path)
        ok(not all_tagged, "RED: NOOP stub — headings do NOT carry tags (correctly caught)")
        ok(pending == len(ENTRIES),
           f"RED: NOOP stub — count_pending_inbox still reads {len(ENTRIES)} (got {pending})")

    # --- Variant B: writes an unsanctioned tag ------------------------------
    with tempfile.TemporaryDirectory() as tmp3:
        anchor_dir, inbox_path, backlog_path = seed_anchor(tmp3)
        for date, topic, _ in ENTRIES:
            r = run_stub(stub_dir, STUB_WRONGTAG, 91, inbox_path, date, topic, "DONE")
            ok(r.returncode == 0, f"WRONGTAG stub subprocess itself ran cleanly ({date})")
        all_tagged, pending, checks = three_way_check(inbox_path, backlog_path)
        # `HANDLED` is not `DONE`/`MOVED → …`, so audit_q's OWN tag regex does
        # not recognize it — the entries still read PENDING (a stricter,
        # equally-correct catch than the checker below).
        ok(pending == len(ENTRIES),
           f"RED: WRONGTAG stub — count_pending_inbox still reads {len(ENTRIES)} "
           f"(an unsanctioned tag is not a tag) (got {pending})")
        ok(checks["status_tags"] == "fail",
           f"RED: WRONGTAG stub — chk_inbox_status_tags catches the invented "
           f"tag (got {checks['status_tags']!r})")

    # --- Sanity: distinct stub file sizes, the literal anti-collision check -
    len_a = len(STUB_NOOP.format(pad="x" * 37))
    len_b = len(STUB_WRONGTAG.format(pad="x" * 91))
    ok(len_a != len_b,
       f"the two stub variants are different lengths on disk ({len_a} vs {len_b}) "
       f"— (mtime, size) cannot alias them even written in the same second")


print("\n3. Black-box sanity — the REAL `state` script, as a subprocess, still GREEN")

with tempfile.TemporaryDirectory() as tmp4:
    anchor_dir, inbox_path, backlog_path = seed_anchor(tmp4)
    pycache = STATE_PATH.parent / "__pycache__"
    if pycache.is_dir():
        shutil.rmtree(pycache)
    for (date, topic, _text), tag in zip(ENTRIES, ["DONE", "MOVED → X#Y", "DONE"]):
        r = subprocess.run(
            [sys.executable, "-B", str(STATE_PATH), "inbox-tag", str(anchor_dir),
             "--date", date, "--topic", topic, "--tag", tag],
            capture_output=True, text=True, timeout=30)
        ok(r.returncode == 0, f"real `state inbox-tag` subprocess exits 0 for {date}")
    all_tagged, pending, checks = three_way_check(inbox_path, backlog_path)
    ok(all_tagged, "GREEN: real state — every entry tagged")
    ok(pending == 0, f"GREEN: real state — count_pending_inbox reads 0 (got {pending})")
    for name, status in checks.items():
        ok(status == "pass", f"GREEN: real state — chk_inbox_{name} passes")


print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
