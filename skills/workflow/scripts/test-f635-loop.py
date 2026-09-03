#!/usr/bin/env python3
"""test-f635-loop.py — TINK F635: `loop`, a stone that carries a workflow.

Fixture vault in a tempdir (MED and BUY own stones; TRAFFIC is the watch list
with `accepts: due, done, importance`), two specimen workflows (the Cigna
refill, the eBay return), and a private notmuch database so the `mail:` probe
is exercised against the real instrument. Never touches the real vault; the
clock is pinned with LOOP_NOW.

  A. refusal — a workflow step with no probe is refused at `loop start`,
     naming the step; nothing is written (Success Criteria 1).
  B. refusal — missing `requires::` binding; `when` finer than an hour;
     `miss → dan` on a mail-only probe; TRAFFIC's accepts keys absent.
  C. start — keys written (workflow/step/entered/tempo), enrolled on TRAFFIC,
     TRAFFIC's control file carries the line, `## Log` opened, receipt.
  D. key probe — before the rendezvous a miss is "waiting"; after it the miss
     branch is taken under --apply (open → press, importance high); setting
     `ordered::` makes the next scan hit (press → confirm); a `portal:` step
     lands in `due`'s "needs an agent check" bucket.
  E. mail probe — the eBay loop at `label` scans unknown with an empty index,
     hit once the message is planted, and advances under --apply (Success
     Criteria 2).
  F. advance/close — `--to` a non-step is refused; close writes `closed::`,
     recalls from TRAFFIC, the line is gone; a closed loop refuses advance.
  G. self-workflow and channel fallback — a stone whose `workflow::` is a
     self-link resolves to its own `## Workflow`; a stone with only
     `channel::` resolves through the channel page's `workflow::`.
  H. rule 7 — a hand-written line on TRAFFIC's control file is reported.
  I. stale — past rendezvous and undecided routes to the owner.
  J. audit checkers — R-loop-01/02/06 through `loop_checks.CHECKERS`: a
     clean loop passes all three, a non-loop passes as "not a loop", and a
     malformed twin fails exactly the rule its defect belongs to.
  K. lint — a workflow page validates on its own: the clean Cigna template
     lists four steps and says ok; the no-probe twin exits 1 naming the step.
"""
import sys as _sys; _sys.dont_write_bytecode = True

import contextlib
import importlib.machinery
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, fname):
    loader = importlib.machinery.SourceFileLoader(name, str(HERE / fname))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


loop = _load("loop_mod", "loop")
stone = loop.stone
stone._LINE_MAX_CACHE = 0
# Hermetic: config mode with one type, regardless of the user's global.yaml.
stone._GLOBAL_STONES_CACHE = {"_": "pebbles", "pebbles": {}}

PASS = FAIL = 0


def ok(msg):
    global PASS; PASS += 1; print(f"  PASS: {msg}")


def no(msg):
    global FAIL; FAIL += 1; print(f"  FAIL: {msg}")


def check(cond, msg):
    (ok if cond else no)(msg)


def run(argv, now=None):
    """(rc, stdout, stderr) of one `loop` invocation."""
    loop._INDEX.clear()
    out, err = io.StringIO(), io.StringIO()
    env_before = os.environ.get("LOOP_NOW")
    if now:
        os.environ["LOOP_NOW"] = now
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = loop.main(["loop"] + argv)
    finally:
        if env_before is None:
            os.environ.pop("LOOP_NOW", None)
        else:
            os.environ["LOOP_NOW"] = env_before
    return rc, out.getvalue(), err.getvalue()


def mint(root, slug, line):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = stone.main(["stone", "new", slug, "--line", line, "--root", str(root)])
    assert rc == 0, out.getvalue()
    return out.getvalue().split("minted ")[1].split(" in ")[0].split(" ")[1]


def stone_path(root, slug, sid):
    return root / slug / f"{slug} Track" / f"{slug} Pebbles" / f"{slug} {sid}.md"


def control_path(root, slug):
    return root / slug / f"{slug} Track" / f"{slug} Pebbles" / f"{slug} Pebbles.md"


def set_key(path, key, value):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    lines.insert(1, f"{key}:: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def keys_of(path):
    return dict(stone._parse_stone(path.read_text(encoding="utf-8"))[0])


CIGNA = """# MED Cigna Refill

## Workflow

requires:: window-open, run-out
raise:: daily

| step | when | probe | hit | miss |
|---|---|---|---|---|
| open | `window-open` | `key: ordered` | confirm | press |
| press | `+7d` · importance high | `key: ordered` | confirm | dan |
| confirm | `ordered+3d` | `portal: [[@Cigna]] — Orders and Balances shows the order` | arrive | open · importance critical |
| arrive | `run-out-3d` | `mail: from:express-scripts subject:delivered` · `key: arrived` | close | dan |

## Notes
Prose after the table is not part of the workflow.
"""

EBAY = """# BUY eBay Return

## Workflow

requires:: return-id, ship-by
raise:: weekly

| step | when | probe | hit | miss |
|---|---|---|---|---|
| label | `+3d` | `mail: subject:"Ready to Ship"` | ship | owner |
| ship | `ship-by-7d` · importance high | `key: tracking` | refund | dan |
| refund | `shipped+10d` | `mail: subject:refund` · `key: refunded` | close | owner |
"""

NO_PROBE = CIGNA.replace("| press | `+7d` · importance high | `key: ordered` |",
                         "| press | `+7d` · importance high |  |")
BAD_WHEN = CIGNA.replace("`+7d` · importance high", "`22:30`")
MAIL_ONLY_DAN = CIGNA.replace("`mail: from:express-scripts subject:delivered` · `key: arrived`",
                              "`mail: from:express-scripts subject:delivered`")
# Legal but silent: a mail-only step whose miss goes to a STEP — the branch can never fire (§ K warns).
MAIL_ONLY_STEP = MAIL_ONLY_DAN.replace("| close | dan |", "| close | press |")

HANDOFF = ["--set", "due=2026-10-01", "--set", "done=the supply is on the shelf",
           "--set", "importance=nominal", "--set", "lapses=Eliquis runs out 2026-10-01"]
BINDINGS = ["--set", "window-open=2026-09-12", "--set", "run-out=2026-10-01"]


def build(root: Path):
    for slug, extra in (("MED", ""), ("BUY", ""), ("TRAFFIC", "accepts: due, done, importance\n")):
        d = root / slug
        d.mkdir(parents=True)
        (d / ".anchor").write_text(f"slug: {slug}\n{extra}stones:\n  pebbles:\n", encoding="utf-8")
    (root / "MED" / "MED Cigna Refill.md").write_text(CIGNA, encoding="utf-8")
    (root / "MED" / "MED No Probe.md").write_text(NO_PROBE, encoding="utf-8")
    (root / "MED" / "MED Bad When.md").write_text(BAD_WHEN, encoding="utf-8")
    (root / "MED" / "MED Mail Only.md").write_text(MAIL_ONLY_DAN, encoding="utf-8")
    (root / "MED" / "MED Mail Step.md").write_text(MAIL_ONLY_STEP, encoding="utf-8")
    (root / "BUY" / "BUY eBay Return.md").write_text(EBAY, encoding="utf-8")
    (root / "AT").mkdir()
    (root / "AT" / "@Cigna.md").write_text("# @Cigna\n\nworkflow:: [[MED Cigna Refill]]\n", encoding="utf-8")


def notmuch_env(tmp: Path):
    mail = tmp / "mail"
    (mail / "inbox" / "cur").mkdir(parents=True)
    (mail / "inbox" / "new").mkdir()
    (mail / "inbox" / "tmp").mkdir()
    cfg = tmp / "notmuch-config"
    cfg.write_text(f"[database]\npath={mail}\n[user]\nname=Fixture\nprimary_email=fixture@example.com\n"
                   f"[new]\ntags=inbox\n[search]\nexclude_tags=\n", encoding="utf-8")
    os.environ["NOTMUCH_CONFIG"] = str(cfg)
    subprocess.run(["notmuch", "new"], capture_output=True, check=True)
    return mail


def plant(mail: Path, subject: str, frm: str, mid: str):
    (mail / "inbox" / "cur" / f"{mid}.eml:2,S").write_text(
        f"From: {frm}\nTo: fixture@example.com\nSubject: {subject}\n"
        f"Date: Tue, 01 Sep 2026 10:00:00 -0700\nMessage-ID: <{mid}@example.com>\n\nbody\n",
        encoding="utf-8")
    subprocess.run(["notmuch", "new"], capture_output=True, check=True)


def main():
    if not shutil.which("notmuch"):
        print("notmuch is not installed — the mail: probe cannot be exercised"); return 2
    tmp = Path(tempfile.mkdtemp(prefix="f635-"))
    root = tmp / "vault"
    build(root)
    mail = notmuch_env(tmp)
    R = ["--root", str(root)]
    T0 = "2026-09-10T12:00"

    print("A. refusal — step with no probe, nothing written")
    sid = mint(root, "MED", "September Cigna order — Eliquis + Atorvastatin")
    rc, out, err = run(["start", "MED", sid, "--workflow", "[[MED No Probe]]"] + BINDINGS + HANDOFF + R, T0)
    check(rc == 1 and "step press: no probe" in err, f"refused naming the step: {err.strip().splitlines()[-2:] }")
    check("workflow" not in keys_of(stone_path(root, "MED", sid)), "stone keys untouched")
    check(not control_path(root, "TRAFFIC").exists(), "TRAFFIC control file not created")

    print("B. refusals — binding, when, mail-only dan, accepts")
    rc, out, err = run(["start", "MED", sid, "--workflow", "[[MED Cigna Refill]]",
                        "--set", "run-out=2026-10-01"] + HANDOFF + R, T0)
    check(rc == 1 and "requires `window-open::`" in err, "missing requires:: binding refused")
    rc, out, err = run(["start", "MED", sid, "--workflow", "[[MED Bad When]]"] + BINDINGS + HANDOFF + R, T0)
    check(rc == 1 and "finer than one hour" in err, "22:30 refused as finer than one hour")
    rc, out, err = run(["start", "MED", sid, "--workflow", "[[MED Mail Only]]"] + BINDINGS + HANDOFF + R, T0)
    check(rc == 1 and "no probe can return `miss`" in err, "miss → dan on a mail-only probe refused")
    rc, out, err = run(["start", "MED", sid, "--workflow", "[[MED Cigna Refill]]"] + BINDINGS
                       + ["--set", "lapses=x"] + R, T0)
    check(rc == 1 and "TRAFFIC accepts only" in err and "`due::`" in err, "TRAFFIC accepts keys enforced before any write")
    rc, out, err = run(["start", "MED", sid, "--workflow", "[[BUY eBay Return]]"] + BINDINGS + HANDOFF + R, T0)
    check(rc == 1 and "outside the owner's anchor (MED/)" in err, "R-loop-08: workflow outside the owner's anchor refused")
    check("workflow" not in keys_of(stone_path(root, "MED", sid)), "still nothing written after five refusals")

    print("C. start — keys, enrollment, receipt")
    rc, out, err = run(["start", "MED", sid, "--workflow", "[[MED Cigna Refill]]", "--channel", "[[@Cigna]]"]
                       + BINDINGS + HANDOFF + R, T0)
    k = keys_of(stone_path(root, "MED", sid))
    check(rc == 0, f"start ok: {err.strip()}")
    check(k.get("workflow") == "[[MED Cigna Refill]]" and k.get("step") == "open"
          and k.get("entered") == "2026-09-10" and k.get("tempo") == "daily", f"keys written: {k}")
    check(k.get("enrolled") == "TRAFFIC", "enrolled:: TRAFFIC")
    cp = control_path(root, "TRAFFIC")
    check(cp.is_file() and f"[[MED {sid}|MED:]]" in cp.read_text(), "TRAFFIC control carries the line")
    body = stone_path(root, "MED", sid).read_text()
    check("## Log" in body and "started at `open`" in body, "## Log opened with the start entry")
    check("rendezvous 2026-09-12" in out and "enrolled on TRAFFIC" in out, f"receipt: {out.strip().splitlines()[-1]}")
    rc, out, err = run(["start", "MED", sid, "--workflow", "[[MED Cigna Refill]]"] + R, T0)
    check(rc == 1 and "already a loop" in err, "second start refused")

    print("D. key probe — miss waits, then branches; ordered:: hits; portal step needs an agent")
    rc, out, err = run(["scan"] + R, "2026-09-11T12:00")
    check("miss" in out and "waiting — rendezvous 2026-09-12" in out, "before rendezvous: miss waits")
    rc, out, err = run(["scan"] + R, "2026-09-13T12:00")
    check("→ press (miss branch)" in out, "after rendezvous: miss branch reported")
    check(keys_of(stone_path(root, "MED", sid)).get("step") == "open", "report mode did not advance")
    rc, out, err = run(["scan", "--apply"] + R, "2026-09-13T12:00")
    k = keys_of(stone_path(root, "MED", sid))
    check(k.get("step") == "press" and k.get("entered") == "2026-09-13" and k.get("importance") == "high",
          f"--apply: open → press, entered reset, importance high: {k}")
    check("open → press" in stone_path(root, "MED", sid).read_text(), "log line for the branch")
    rc, out, err = run(["due"] + R, "2026-09-21T12:00")
    check("script-probable" in out and f"MED {sid}" in out and "`press`" in out, "due: press is script-probable")
    set_key(stone_path(root, "MED", sid), "ordered", "2026-09-14")
    rc, out, err = run(["scan", "--apply"] + R, "2026-09-15T12:00")
    k = keys_of(stone_path(root, "MED", sid))
    check("hit" in out and k.get("step") == "confirm", "ordered:: set → hit → confirm")
    rc, out, err = run(["show", "MED", sid] + R, "2026-09-18T12:00")
    check("when      ordered+3d → 2026-09-17  (arrived)" in out and "portal:" in out, "show: rendezvous and portal probe")
    rc, out, err = run(["due"] + R, "2026-09-18T12:00")
    check("needs an agent check" in out and "`confirm`" in out, "due: confirm needs an agent check")
    rc, out, err = run(["scan"] + R, "2026-09-18T12:00")
    check("agent" in out and "→ agent" in out, "scan: portal step reports agent, never advances")

    print("E. mail probe — unknown, then hit on a planted message")
    bid = mint(root, "BUY", "T480 return — label from eBay")
    rc, out, err = run(["start", "BUY", bid, "--workflow", "[[BUY eBay Return]]",
                        "--set", "return-id=5312345678", "--set", "ship-by=2026-09-30",
                        "--set", "due=2026-09-30", "--set", "done=refund lands", "--set", "importance=high",
                        "--set", "lapses=$287.86"] + R, T0)
    check(rc == 0 and keys_of(stone_path(root, "BUY", bid)).get("tempo") == "weekly", f"eBay loop started: {err.strip()}")
    rc, out, err = run(["scan"] + R, "2026-09-11T12:00")
    check(f"BUY {bid}" in out and "unknown" in out and "no mail matching" in out, "empty index → unknown")
    rc, out, err = run(["scan", "--apply"] + R, "2026-09-14T12:00")
    check("→ owner (past rendezvous, undecided)" in out
          and keys_of(stone_path(root, "BUY", bid)).get("step") == "label", "unknown past rendezvous routes to owner, never branches")
    plant(mail, "Your return is Ready to Ship", "ebay@ebay.com", "rts-1")
    rc, out, err = run(["scan"] + R, "2026-09-14T12:00")
    check("hit" in out and "id:rts-1@example.com" in out, "planted message → hit with the message id")
    rc, out, err = run(["scan", "--apply"] + R, "2026-09-14T12:00")
    k = keys_of(stone_path(root, "BUY", bid))
    check(k.get("step") == "ship" and k.get("importance") == "high", f"--apply: label → ship: {k}")

    print("F. advance / close")
    rc, out, err = run(["advance", "BUY", bid, "--to", "nowhere", "--evidence", "x"] + R, T0)
    check(rc == 1 and "not a step" in err, "--to a non-step refused")
    rc, out, err = run(["advance", "BUY", bid, "--to", "dan", "--evidence", "x"] + R, T0)
    check(rc == 1 and "is a route, not a step" in err, "--to dan refused")
    rc, out, err = run(["advance", "MED", sid, "--to", "arrive", "--evidence", "portal shows order 4471"] + R, "2026-09-18T12:00")
    check(rc == 0 and keys_of(stone_path(root, "MED", sid)).get("step") == "arrive", "advance --to arrive")
    rc, out, err = run(["close", "MED", sid, "--evidence", "bottles on the shelf"] + R, "2026-09-25T12:00")
    k = keys_of(stone_path(root, "MED", sid))
    check(rc == 0 and k.get("closed") == "2026-09-25" and "enrolled" not in k, f"closed:: written, enrollment gone: {err.strip()}")
    check(f"[[MED {sid}|MED:]]" not in control_path(root, "TRAFFIC").read_text(), "line recalled from TRAFFIC")
    check(f"[[BUY {bid}|BUY:]]" in control_path(root, "TRAFFIC").read_text(), "the other loop's line stays")
    rc, out, err = run(["advance", "MED", sid, "--evidence", "x"] + R, T0)
    check(rc == 1 and "closed" in err, "a closed loop refuses advance")
    rc, out, err = run(["due"] + R, "2026-09-25T12:00")
    check(f"MED {sid}" not in out, "closed loop is not due")

    print("G. self-workflow and channel fallback")
    s2 = mint(root, "MED", "One-off: return the BP cuff")
    p2 = stone_path(root, "MED", s2)
    p2.write_text(p2.read_text() + "\n## Workflow\n\n| step | when | probe | hit | miss |\n|---|---|---|---|---|\n"
                  "| box | `+2d` | `mail: subject:cuff` | close | owner |\n", encoding="utf-8")
    rc, out, err = run(["start", "MED", s2, "--workflow", f"[[MED {s2}]]", "--set", "due=2026-09-20",
                        "--set", "done=cuff returned", "--set", "importance=low", "--set", "lapses=$40"] + R, T0)
    check(rc == 0 and keys_of(p2).get("step") == "box", f"self-link workflow resolves: {err.strip()}")
    s3 = mint(root, "MED", "October Cigna order")
    rc, out, err = run(["start", "MED", s3, "--channel", "[[@Cigna]]"] + BINDINGS + HANDOFF + R, T0)
    k = keys_of(stone_path(root, "MED", s3))
    check(rc == 0 and k.get("step") == "open" and k.get("workflow") == "[[MED Cigna Refill]]",
          f"channel:: supplies the workflow, recorded on the stone: {err.strip()}")
    rc, out, err = run(["check", "MED", s3] + R, T0)
    check(rc == 0 and "[[MED Cigna Refill]]" in out, "check resolves through the channel")

    print("H. rule 7 — hand-written line on the watch list")
    cp = control_path(root, "TRAFFIC")
    cp.write_text(cp.read_text() + "Call the dentist back\n", encoding="utf-8")
    rc, out, err = run(["due"] + R, T0)
    check("WARN" in out and "hand-written line 'Call the dentist back'" in out, "hand-written line reported")

    print("I. stale")
    rc, out, err = run(["stale"] + R, "2026-09-20T12:00")
    check(f"MED {s2}" in out and "→ owner MED" in out, "undecided past rendezvous routes to its owner")

    print("J. audit checkers — one pass, partitioned by rule")
    checks = _load("loop_checks_mod", "loop_checks.py").CHECKERS
    saved_root = loop.stone.DEFAULT_ROOT
    loop.stone.DEFAULT_ROOT = root
    loop._INDEX.clear()
    try:
        good = stone_path(root, "BUY", bid)
        verdicts = {n: fn(good, root, None) for n, fn in checks.items()}
        check(all(v[0] == "pass" for v in verdicts.values()), f"clean loop passes all three: {verdicts}")
        plain = mint(root, "MED", "not a loop at all")
        v = checks["loop_keys_complete"](stone_path(root, "MED", plain), root, None)
        check(v[0] == "pass" and "not a loop" in v[1], "a plain stone is not judged")
        bad = stone_path(root, "MED", s3)
        text = bad.read_text()
        bad.write_text(text.replace("lapses:: ", "lapses-x:: ").replace("run-out:: ", "run-out-x:: ")
                       .replace("step:: open", "step:: nowhere"))
        v1 = checks["loop_keys_complete"](bad, root, None)
        v2 = checks["loop_step_resolves"](bad, root, None)
        v6 = checks["loop_bindings_present"](bad, root, None)
        check(v1[0] == "fail" and "lapses" in v1[1] and "run-out" not in v1[1], f"01 fires on the missing key only: {v1}")
        check(v2[0] == "fail" and "nowhere" in v2[1] and "lapses" not in v2[1], f"02 fires on the bad step only: {v2}")
        check(v6[0] == "fail" and "run-out" in v6[1] and "nowhere" not in v6[1], f"06 fires on the missing binding only: {v6}")
        bad.write_text(text)
    finally:
        loop.stone.DEFAULT_ROOT = saved_root

    print("K. lint — a workflow page, no stone")
    rc, out, err = run(["lint", "[[MED Cigna Refill]]"] + R, T0)
    check(rc == 0 and "4 step(s)" in out and "ok — a stone carrying `window-open::`, `run-out::`" in out, f"clean template lints ok: {out.splitlines()[0] if out else err}")
    rc, out, err = run(["lint", str(root / "MED" / "MED No Probe.md")] + R, T0)
    check(rc == 1 and "DEFECT" in out and "step press: no probe" in out, "no-probe twin exits 1 naming the step")
    rc, out, err = run(["lint", "[[MED Mail Step]]"] + R, T0)
    check(rc == 0 and "WARN step arrive: miss branch unreachable" in out and "`miss → press` never fires" in out,
          "mail-only step with miss → step lints ok with a WARN")
    rc, out, err = run(["lint", "[[MED Mail Only]]"] + R, T0)
    check(rc == 1 and "WARN" not in out, "miss → dan on mail-only stays a defect, not a warning")
    rc, out, err = run(["lint", "[[MED Nowhere]]"] + R, T0)
    check(rc == 1 and "matches no file" in err, "unresolvable link is an error, not a pass")

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
