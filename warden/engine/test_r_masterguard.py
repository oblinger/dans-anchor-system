#!/usr/bin/env python3
"""Fixtures for R-masterguard-01, with the ATT T261 bridged-sentinel case.

The rule denies a Bash command that WRITES into `/Volumes/<X>/__MASTERS__/`
unless a write session is open on that volume. What T261 fixed is *where it
looks for the session*.

The trap, stated once so it does not have to be re-derived: **rule bodies
execute inside the resident Warden daemon, on the machine the daemon runs on.**
Every master drive the estate actually works on is mounted on a different
machine and reached over the bridge, so the original
`os.path.exists("/Volumes/10T/.write-session")` was asking the laptop whether a
drive attached to Dexter had a session open. It answered False every time,
however correctly the session had been opened — and it would answer True if the
laptop ever mounted a same-named volume with a stale sentinel, passing a write
aimed at somebody else's drive. Same family as the `os.environ` trap in
`test_r_ob_browser_lease.py`: the daemon's view of the world is not the
caller's.

The load-bearing case below is BRIDGED-HOLDER-PASSES. The one after it is just
as important and easier to lose: when the volume is not local and no host is
named, the rule must say **"cannot be checked"** and NOT reuse the "no session"
message — an unverifiable session is not an open one, but it is also not the
same failure, and collapsing the two sends the agent to fix the wrong thing.

Runnable standalone (`python3 test_r_masterguard.py`) — no test framework.
Exits non-zero on any failure.
"""
import re
import subprocess
import sys
import types
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from warden_root import corpus_root  # noqa: E402

RULESET = corpus_root() / "rulesets" / "R-masterguard.md"
VOL = "10T"
SENTINEL = "/Volumes/%s/.write-session" % VOL

LOCAL_WRITE = "rsync -a /tmp/x/ '/Volumes/10T/__MASTERS__/_ARCHIVES_/2018-07-00 x/'"
BRIDGED_WRITE = (
    "ssh dexter.local \"tmux send-keys -t 'bridge-dexter:agent-atticus' "
    "'rsync -a /tmp/x/ /Volumes/10T/__MASTERS__/_ARCHIVES_/y/' Enter\"")
NO_HOST_WRITE = "cp /tmp/x '/Volumes/10T/__MASTERS__/_ARCHIVES_/y'"

ALWAYS_PASS = [
    "cp '/Volumes/10T/__MASTERS__/_ARCHIVES_/y' /tmp/",          # read out
    "shasum -a 256 '/Volumes/10T/__MASTERS__/_ARCHIVES_/y'",     # read
    "ls -la /Volumes/10T/__MASTERS__/",                          # read
    "rsync -a /tmp/x/ '/Volumes/8T/Clone of 10T/__MASTERS__/y/'",  # clone, not master
    "echo 'never rm -rf /Volumes/10T/__MASTERS__/x, obviously'",  # prose
]


def load_body():
    src = RULESET.read_text()
    m = re.search(r"```python\n(.*?)```", src, re.S)
    if not m:
        raise SystemExit("no python block in %s" % RULESET)
    ns = {}
    exec(m.group(1), ns)
    return ns["body"]


def ctx_for(cmd):
    event = types.SimpleNamespace(tool="Bash", target=None, input={"command": cmd})
    return types.SimpleNamespace(event=event,
                                 agent=types.SimpleNamespace(session_id="s", is_bound=True))


class World:
    """Patches the three facts the rule reads about the outside world.

    `mounted_here` / `sentinel_here` describe THIS machine; `remote_rc` is what
    the probe of the drive-holding host returns (None = the probe itself blew
    up, which must be treated as unknown rather than as absent).
    """

    def __init__(self, mounted_here, sentinel_here=False, remote_rc=None):
        self.mounted_here, self.sentinel_here, self.remote_rc = (
            mounted_here, sentinel_here, remote_rc)
        self.probes = 0

    def _run(self, argv, **kw):
        self.probes += 1
        if self.remote_rc is None:
            raise subprocess.TimeoutExpired(argv, 8)
        return types.SimpleNamespace(returncode=self.remote_rc, stdout=b"", stderr=b"")

    def __enter__(self):
        self._p = [
            mock.patch("os.path.ismount",
                       lambda p: self.mounted_here and p == "/Volumes/" + VOL),
            mock.patch("os.path.exists",
                       lambda p: self.sentinel_here and p == SENTINEL),
            mock.patch("subprocess.run", self._run),
        ]
        for p in self._p:
            p.start()
        return self

    def __exit__(self, *a):
        for p in self._p:
            p.stop()


def main():
    body = load_body()
    fails = []

    def check(name, cmd, world, want_deny, want_text=None, want_probes=None):
        with world:
            out = body(ctx_for(cmd))
        got_deny = bool(out)
        if got_deny != want_deny:
            fails.append("%s: expected %s, got %s%s" % (
                name, "DENY" if want_deny else "PASS",
                "DENY" if got_deny else "PASS",
                (" — %s" % out[0][:90]) if out else ""))
            return
        if want_text and (not out or want_text not in out[0]):
            fails.append("%s: denied, but not with the %r message — got %r"
                         % (name, want_text, out[0][:120] if out else None))
        if want_probes is not None and world.probes != want_probes:
            fails.append("%s: expected %d remote probe(s), made %d"
                         % (name, want_probes, world.probes))

    # --- the drive is on THIS machine: unchanged behaviour, and no probe ---
    check("local-holder-passes", LOCAL_WRITE,
          World(mounted_here=True, sentinel_here=True), False, want_probes=0)
    check("local-no-session-denies", LOCAL_WRITE,
          World(mounted_here=True, sentinel_here=False), True,
          want_text="WRITE-ONCE", want_probes=0)

    # --- THE T261 CASE: the drive is on the host the command names ---
    check("bridged-holder-passes", BRIDGED_WRITE,
          World(mounted_here=False, remote_rc=0), False, want_probes=1)
    check("bridged-no-session-denies", BRIDGED_WRITE,
          World(mounted_here=False, remote_rc=1), True, want_text="WRITE-ONCE")

    # --- cannot judge: must say so, and must NOT reuse the no-session text ---
    check("unmounted-and-no-host-says-cannot-check", NO_HOST_WRITE,
          World(mounted_here=False), True, want_text="CANNOT BE CHECKED",
          want_probes=0)
    check("probe-failure-says-cannot-check", BRIDGED_WRITE,
          World(mounted_here=False, remote_rc=None), True,
          want_text="CANNOT BE CHECKED")

    # --- a stale local sentinel must not authorise a write to another box ---
    check("stale-local-sentinel-does-not-pass-a-bridged-write", BRIDGED_WRITE,
          World(mounted_here=False, sentinel_here=True, remote_rc=1), True,
          want_text="WRITE-ONCE")

    # --- reads, clones and prose are untouched, and cost no probe ---
    for cmd in ALWAYS_PASS:
        check("always-passes: %s" % cmd[:44], cmd,
              World(mounted_here=False), False, want_probes=0)

    total = 7 + len(ALWAYS_PASS)
    if fails:
        print("FAIL — %d of %d fixtures:" % (len(fails), total))
        for f in fails:
            print("  · %s" % f)
        return 1
    print("PASS — %d/%d fixtures for R-masterguard-01" % (total, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
