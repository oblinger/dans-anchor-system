---
description: "the live-integration selftest ruleset (R-warden-selftest) — fires on easily-driven moments, writes an observable marker so a live hook is provable"
---

# [[Warden]] · Warden Selftest Ruleset

The **live-integration selftest** ([[F221 — Live-integration test class|F221]]). Each rule below fires on an easily-driven moment and **appends a marker line to `~/.warden/selftest.log`** — a side effect observable from *outside* the session, so a real Claude Code hook firing is provable by reading the log (the user's *"look at the log, see that it actually triggered."*). The ruleset is named `R-warden-selftest`, so its keying trait is `warden-selftest`: it is **inert everywhere** except an anchor that declares `traits: [warden-selftest]` (active-set gating, [[F211 — Rule compiler and installer|F211]]). Drop that "funky trait" into a scratch anchor's `.anchor` and any agent operating there fires these rules.

Each body reads `ctx.moment` / `ctx.anchor` (supplied by the dispatcher) and returns a steer string as well, so both the log side-channel and the steer-injection path are exercised.

# RULESET R-warden-selftest
description:: live-integration selftest — write an observable marker per fired moment

### RULE R-warden-selftest-01 — mark a Write (when:: tool:post:Write)
when:: tool:post:Write

```python
import json, os, time


def body(ctx):
    p = os.path.join(os.environ.get("WARDEN_HOME") or os.path.expanduser("~/.warden"), "selftest.log")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    rec = {"ts": round(time.time(), 3), "rule": "R-warden-selftest-01",
           "moment": getattr(ctx, "moment", "tool:post:Write"),
           "anchor": getattr(ctx, "anchor", "?")}
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return f"[warden selftest] R-warden-selftest-01 fired at {rec['moment']} in {rec['anchor']}"
```

### RULE R-warden-selftest-02 — mark a markdown write (when:: write:markdown)
when:: write:markdown

```python
import json, os, time


def body(ctx):
    p = os.path.join(os.environ.get("WARDEN_HOME") or os.path.expanduser("~/.warden"), "selftest.log")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    rec = {"ts": round(time.time(), 3), "rule": "R-warden-selftest-02",
           "moment": getattr(ctx, "moment", "write:markdown"),
           "anchor": getattr(ctx, "anchor", "?")}
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return f"[warden selftest] R-warden-selftest-02 fired at {rec['moment']} in {rec['anchor']}"
```

### RULE R-warden-selftest-03 — mark a session start (when:: session:start)
when:: session:start

```python
import json, os, time


def body(ctx):
    p = os.path.join(os.environ.get("WARDEN_HOME") or os.path.expanduser("~/.warden"), "selftest.log")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    rec = {"ts": round(time.time(), 3), "rule": "R-warden-selftest-03",
           "moment": getattr(ctx, "moment", "session:start"),
           "anchor": getattr(ctx, "anchor", "?")}
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return f"[warden selftest] R-warden-selftest-03 fired at {rec['moment']} in {rec['anchor']}"
```

### RULE R-warden-selftest-04 — mark a prompt submit (when:: prompt:submit)
when:: prompt:submit

```python
import json, os, time


def body(ctx):
    p = os.path.join(os.environ.get("WARDEN_HOME") or os.path.expanduser("~/.warden"), "selftest.log")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    rec = {"ts": round(time.time(), 3), "rule": "R-warden-selftest-04",
           "moment": getattr(ctx, "moment", "prompt:submit"),
           "anchor": getattr(ctx, "anchor", "?")}
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return f"[warden selftest] R-warden-selftest-04 fired at {rec['moment']} in {rec['anchor']}"
```
