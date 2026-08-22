#!/usr/bin/env python3
"""Fixtures for R-ob-browser-lease-01 (ATT T183 gap 1).

The rule denies a Bash command that drives a browser AROUND `ctrl` — `open -a
Safari`, a bare `open https://…`, osascript speaking to Safari/Chrome — unless
the session behind the event holds the `ctrl` browser lease.

Three things this pins, each of which has already been shipped wrong once:

  1. **Prose is not code.** `R-ob-remote-ops-01` denied a `--body` text that
     merely contained "; ssh …", and `-02` exempted a whole compound command
     because an `echo` MENTIONED job-wrapper.sh. So the pass set here includes
     an echo and a grep whose text names `open -a Safari`.
  2. **App names match whole, not by prefix.** The first run of these fixtures
     caught `tell application "Google Chrome"` sailing through, because the
     check was built as `'application "' + browser`, and "chrome" is not a
     prefix of "google chrome".
  3. **Identity comes from `ctx.agent`, never `os.environ`.** Rule bodies run
     inside the resident daemon, whose environment belongs to whichever session
     started it. The first revision of this rule compared the lease holder
     against `os.environ['CLAUDE_CODE_SESSION_ID']` and therefore denied the
     session that actually held the lease. The HOLDER-PASSES case below is the
     regression test for exactly that.

Runnable standalone (`python3 test_r_ob_browser_lease.py`) — no test framework.
Exits non-zero on any failure.
"""
import json
import re
import sys
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from warden_root import corpus_root  # noqa: E402

RULESET = corpus_root() / "rulesets" / "R-ob-browser-lease.md"
LEASE_PATH = "/tmp/ctrl-browser.lease.json"
ME = "sess-under-test"

MUST_DENY = [
    'open -a Safari "https://example.com"',
    'open -b com.apple.Safari https://x.com',
    'open "https://news.ycombinator.com"',
    'osascript -e \'tell application "Safari" to get URL of current tab of front window\'',
    'osascript -e \'tell application "Google Chrome" to activate\'',
    'osascript -e \'tell application id "com.apple.Safari" to do JavaScript "1"\'',
]

MUST_PASS = [
    'open /tmp/report.md',
    'open -a "Sublime Text" foo.py',
    'open -a Finder .',
    'osascript -e \'tell application "System Events" to keystroke "a"\'',
    'osascript -e \'tell application "Terminal" to activate\'',
    'echo "do not open -a Safari here, it is prose"',
    'grep -rn "open -a Safari" ~/notes',
    'ctrl surf https://example.com',
]


def load_body():
    src = RULESET.read_text()
    m = re.search(r"```python\n(.*?)```", src, re.S)
    if not m:
        raise SystemExit(f"no python block in {RULESET}")
    ns = {}
    exec(m.group(1), ns)
    return ns["body"]


def ctx_for(cmd, session=ME):
    """A ctx shaped like the one warden_hook builds: event + agent view."""
    agent = types.SimpleNamespace(session_id=session, is_bound=bool(session))
    event = types.SimpleNamespace(tool="Bash", target=None, input={"command": cmd})
    return types.SimpleNamespace(event=event, agent=agent)


def write_lease(session, deadline_in=300, agent="scout", reason="LEGO lookup"):
    json.dump({"session_id": session, "agent": agent, "reason": reason,
               "acquired": time.time(), "deadline": time.time() + deadline_in},
              open(LEASE_PATH, "w"))


def main():
    body = load_body()
    failures = []

    # Never clobber a lease a live session is actually holding.
    backup = Path(LEASE_PATH).read_text() if Path(LEASE_PATH).exists() else None
    try:
        write_lease("sess-someone-else")
        for cmd in MUST_DENY:
            if not body(ctx_for(cmd)):
                failures.append(f"should DENY but passed: {cmd}")
        for cmd in MUST_PASS:
            if body(ctx_for(cmd)):
                failures.append(f"should PASS but denied: {cmd}")

        # THE regression case — the holder proceeds.
        write_lease(ME, agent="ATT", reason="holding it right now")
        if body(ctx_for('open -a Safari https://x.com')):
            failures.append("denied the session that HOLDS the lease "
                            "(identity read from the wrong place?)")

        # An expired lease is not a held lease, even for its own holder.
        write_lease(ME, deadline_in=-60, agent="ATT")
        if not body(ctx_for('open -a Safari https://x.com')):
            failures.append("allowed a browser drive on an EXPIRED lease")

        # No lease file at all.
        Path(LEASE_PATH).unlink(missing_ok=True)
        if not body(ctx_for('open -a Safari https://x.com')):
            failures.append("allowed a browser drive with no lease at all")

        # Unbound agent — cannot be checked, so it fails closed.
        write_lease(ME, agent="ATT")
        if not body(ctx_for('open -a Safari https://x.com', session="")):
            failures.append("allowed a browser drive from an UNBOUND session")
    finally:
        if backup is not None:
            Path(LEASE_PATH).write_text(backup)
        else:
            Path(LEASE_PATH).unlink(missing_ok=True)

    total = len(MUST_DENY) + len(MUST_PASS) + 4
    if failures:
        print(f"FAIL — {len(failures)} of {total} fixtures:")
        for f in failures:
            print(f"  · {f}")
        return 1
    print(f"PASS — {total}/{total} fixtures for R-ob-browser-lease-01")
    return 0


if __name__ == "__main__":
    sys.exit(main())
