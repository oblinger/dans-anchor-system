#!/usr/bin/env python3
"""T652 — a `DONE — <note>` tag on an Inbox entry drains it.

13 of AUP's 16 entries sat pending for five days (2026-09-02) because four
agents wrote the note the vault asks for and the counter required a bare
backtick after DONE. Three facts must hold and agree: the counter pattern,
the R-fct-inbox-03 checker pattern (a byte-equal restatement, since
audit-plan cannot import audit-q at load), and the `state inbox-tag` writer.
Run: python3 test-t652-inbox-suffix.py
"""
import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "state"
AUDIT = Path.home() / ".claude" / "skills" / "audit" / "scripts"
PASS = FAIL = 0


def check(label, ok):
    global PASS, FAIL
    PASS += ok
    FAIL += not ok
    print(("  ok:   " if ok else "  FAIL: ") + label)


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


audit_q = _load("audit_q_t652", AUDIT / "audit-q.py")
audit_plan = _load("audit_plan_t652", AUDIT / "audit-plan.py")
state_mod = _load("state_t652", STATE)

print("pattern")
check("counter and checker patterns are byte-equal",
      audit_q._INBOX_DONE_RE.pattern == audit_plan._INBOX_TAG_RE.pattern)
YES = ["`DONE`", "`DONE — fact absorbed`", "`DONE—note`", "`DONE - note`",
       "`DONE – en dash`", "`MOVED → X`", "`MOVED → [[A#^T1|T1]] — folded`"]
NO = ["`DONE-ish`", "`DONEX`", "DONE — bare", "`HANDLED`", "`MOVED`"]
for s in YES:
    check(f"matches {s}", bool(audit_q._INBOX_DONE_RE.search(s)))
for s in NO:
    check(f"rejects {s}", not audit_q._INBOX_DONE_RE.search(s))

print("writer")
norm = state_mod._normalize_inbox_tag
check("DONE stays bare", norm("DONE") == "DONE")
check("DONE — note normalizes", norm("DONE   —  fact absorbed ") == "DONE — fact absorbed")
check("DONE - note (ascii) normalizes", norm("DONE - fact absorbed") == "DONE — fact absorbed")
check("MOVED keeps note", norm("MOVED → X — folded") == "MOVED → X — folded")
for bad in ["MOVED", "DONE-ish", "HANDLED", "DONE — `tick`"]:
    try:
        norm(bad)
        check(f"refuses {bad!r}", False)
    except BaseException:  # BacklogEditError subclasses SystemExit
        check(f"refuses {bad!r}", True)

print("end to end")
SLUG = "ZZZSUF"
with tempfile.TemporaryDirectory(prefix="t652-") as td:
    root = Path(td) / SLUG
    track = root / f"{SLUG} Track"
    track.mkdir(parents=True)
    (root / ".anchor").write_text(f"slug: {SLUG}\n")
    (root / f"{SLUG}.md").write_text(f"# {SLUG}\n")
    backlog = track / f"{SLUG} Backlog.md"
    backlog.write_text(f"---\ndescription: s\n---\n\n# {SLUG} Backlog\n\n## Now\n\n## Next\n\n## Later\n\n## Done\n")
    inbox = track / f"{SLUG} Inbox.md"
    inbox.write_text(
        f"---\ndescription: {SLUG} inbox\n---\n\n# {SLUG} Inbox\n\n"
        "## 2026-09-02 — hand tagged    `DONE — written by hand`\n\n> a\n\n"
        "## 2026-09-01 — to drain\n\n> b\n\n"
        "## 2026-08-31 — stays pending\n\n> c\n")
    check("hand-suffixed DONE already counts drained; 2 pending",
          audit_q.count_pending_inbox(SLUG, backlog) == 2)
    env = dict(os.environ, ANCHOR_VAULT_ROOT=td, ANCHOR_LOCK_DIR=td + "/locks")
    r = subprocess.run([sys.executable, str(STATE), "inbox-tag", SLUG, "--date", "2026-09-01",
                        "--tag", "DONE — absorbed into T1"],
                       capture_output=True, text=True, env=env, cwd=root)
    check("inbox-tag accepts a suffixed DONE", r.returncode == 0)
    text = inbox.read_text()
    check("tag landed in em-dash form",
          "## 2026-09-01 — to drain    `DONE — absorbed into T1`" in text)
    check("counter now reads 1 pending", audit_q.count_pending_inbox(SLUG, backlog) == 1)
    verdict, detail = audit_plan.chk_inbox_status_tags(inbox, root, None)
    check(f"R-fct-inbox-03 passes ({detail})", verdict == "pass")
    r = subprocess.run([sys.executable, str(STATE), "inbox-list", SLUG],
                       capture_output=True, text=True, env=env, cwd=root)
    check("inbox-list shows only the untagged entry",
          "1 of 3 entries pending" in r.stderr and "stays pending" in r.stdout
          and "to drain" not in r.stdout)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
