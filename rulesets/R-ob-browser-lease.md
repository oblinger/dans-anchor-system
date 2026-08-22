# RULESET R-ob-browser-lease
include::
description:: One host, one browser — an agent driving Safari or Chrome outside `ctrl` must still hold the `ctrl` browser lease. Closes ATT T183's gap 1, where the sanctioned login-walled path (`open -a Safari` + osascript) would otherwise bypass the lease entirely (`tool:pre:Bash` deny, rides `anchor-base`).

> [!info] Provenance
> Commissioned as the second half of [[ATT183 - Several agents on one host still share one browser|ATT T183]] — the row calls it *"gap 1"* and is explicit that shipping the lease without it would be worse than shipping no lease: *"a lease that covers `ctrl` and nothing else is worse than no lease if anyone reads it as 'the browser is protected.'"* Built 2026-08-21 on the same `tool:pre:Bash` veto path as `R-ob-remote-ops-01`, which the T183 record names as the model.

### RULE R-ob-browser-lease-01 — driving a browser outside `ctrl` needs the `ctrl` lease (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    if "open" not in cmd and "osascript" not in cmd:
        return []
    import json, time, shlex

    # A human shell is never gated, and it needs no check to stay that way:
    # Dan's own `open -a Safari` is typed into Terminal and produces no hook
    # event at all, so this body never runs for him. (ctrl.py, which a human
    # DOES invoke, has to test `CLAUDECODE` explicitly for the same exemption.)
    #
    # 🚨 And do NOT reach for os.environ here to identify the caller. Python
    # rule bodies execute inside the resident warden daemon, whose environment
    # belongs to whichever session started it — `CLAUDECODE` is always set there
    # and `CLAUDE_CODE_SESSION_ID` is somebody else's. This rule shipped that way
    # for one revision and denied the very session that held the lease, because
    # it was comparing the holder against the daemon's owner. `ctx.agent` is the
    # only view bound to the session under judgement.

    # Tokenize shell-aware, and match `open` / `osascript` only in COMMAND
    # position — the lesson R-ob-remote-ops-01 and -02 each had to learn the
    # hard way, once from prose containing "; ssh ..." and once from an echo
    # that merely MENTIONED job-wrapper.sh. A rule that reads prose as code has
    # a hole that widens every time somebody writes about the rule.
    try:
        words = shlex.split(cmd)
    except ValueError:
        words = cmd.split()

    BROWSERS = ("safari", "chrome", "chromium", "firefox", "opera", "brave", "arc")

    def _cmd_position(k, w):
        return k == 0 or words[k - 1][-1:] in (";", "&", "|", "(")

    def _drives_browser():
        for k, w in enumerate(words):
            base = w.rsplit("/", 1)[-1]
            if not _cmd_position(k, w):
                continue
            if base == "open":
                rest = words[k + 1:]
                for i, t in enumerate(rest):
                    low = t.lower()
                    # `open -a Safari` / `open -b com.apple.Safari`
                    if t in ("-a", "-b") and i + 1 < len(rest):
                        nxt = rest[i + 1].lower()
                        if any(b in nxt for b in BROWSERS):
                            return True
                    # `open https://…` — no -a, but the default handler IS a
                    # browser, so the same shared surface moves.
                    if low.startswith(("http://", "https://")):
                        return True
            if base == "osascript":
                payload = " ".join(words[k + 1:]).lower()
                # Match the APP NAME, not a prefix of it: `tell application
                # "Google Chrome"` must fire, and a prefix test on "chrome"
                # silently misses it (it did, on the first run of this rule's
                # own fixtures). `application "System Events"` must not fire.
                import re as _re
                for name in _re.findall(r'application(?:\s+id)?\s+"([^"]*)"', payload):
                    if any(b in name for b in BROWSERS):
                        return True
                    if name.startswith("com.apple.safari") or \
                            name.startswith("com.google.chrome"):
                        return True
        return False

    if not _drives_browser():
        return []

    agent = getattr(ctx, "agent", None)
    session = getattr(agent, "session_id", "") or ""

    lease = None
    try:
        with open("/tmp/ctrl-browser.lease.json") as f:
            lease = json.load(f)
    except Exception:
        lease = None

    if session and lease and lease.get("session_id") == session \
            and time.time() < lease.get("deadline", 0):
        return []  # we hold it — proceed

    if not session:
        # Unbound: no session is attached to this event, so there is no way to
        # ask whether the caller is the holder. Fail closed — the resource is a
        # physical surface somebody may be looking at, and "I could not tell"
        # is not a reason to let a navigation through.
        return ["DENY: cannot identify the session behind this browser command, "
                "so it cannot be checked against the `ctrl` browser lease. "
                "Drive the browser through `ctrl` (which holds the lease itself) "
                "rather than around it. ATT T183 gap 1."]

    if lease is None:
        who = "nobody holds it"
    elif time.time() >= lease.get("deadline", 0):
        who = "the lease has EXPIRED and was never released by %s" % (
            lease.get("agent") or "an unlabelled session")
    else:
        who = "%s holds it — \"%s\"" % (lease.get("agent") or "another session",
                                        lease.get("reason") or "no reason given")

    return ["DENY: this host's browser is a single shared surface and you do not "
            "hold it (%s). Claim it first: `ctrl own [minutes] --reason \"...\"`, "
            "and `ctrl release` when done — expiry is an error path, not a release "
            "path. `ctrl lease` says who has it. This rule exists because the lease "
            "inside ctrl does not cover `open -a Safari` or osascript DOM extraction, "
            "and that path is the sanctioned one for login-walled sites — the most "
            "sensitive browsing there is. ATT T183 gap 1." % who]
```

Catches a Bash command that drives a browser **around** `ctrl` — `open -a Safari`, `open -b com.apple.Safari`, a bare `open https://…` (the default handler is a browser), and `osascript` speaking to Safari / Chrome / Firefox — and denies it unless the calling session holds the `ctrl` browser lease. Passes untouched: every non-browser `open` (`open report.md`, `open -a "Sublime Text"`), `osascript` driving System Events or any non-browser app, and **every command from a human shell**, which carries no `CLAUDECODE`.

**Why:** `ctrl`'s own gate sits on `ctrl`'s dispatch, so it protects exactly the calls that go through `ctrl`. The Safari + osascript path does not, and it is not a marginal one — it is the documented workaround for session-gated sites, reached precisely when `ctrl cpage`'s sandbox Chrome hits a login wall. Shipping the lease without this rule would leave a guard whose most-cited property, *"the browser is protected"*, is false on the traffic that matters most. The enforcement is deliberately split: `ctrl` owns the lease, Warden enforces it where `ctrl` is not on the path.
