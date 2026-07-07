# RULESET R-ob-remote-ops
include::
description:: Ob's remote-ops hygiene — remote machines are driven through the sanctioned control planes (`bridge` persistent tmux, `exp`), never one-shot SSH remote-control. First member: the F183 bridge-guard (`tool:pre:Bash` deny, rides `anchor-base`).

> [!info] Provenance
> Commissioned as [[F183 — Bridge-guard rule — catch one-shot SSH remote-control, redirect to bridge skill|F183]] (2026-06-20, user: the guard "must be driven by rules", deny action, fires on the action itself) and held until the runtime command-guard surface existed; built 2026-07-06 on the F131 veto path (`tool:pre:Bash` + `ctx.event` + `deny`). Future members of the same class: no personal password manager / Keychain on a remote without need.

### RULE R-ob-remote-ops-01 — one-shot SSH remote-control → the bridge skill (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    if "ssh" not in cmd:
        return []
    # Tokenize shell-aware (shlex): a quoted string is ONE token, so prose
    # mentioning `; ssh …` inside an argument never reads as a command-position
    # ssh (live false-positive 2026-07-06 — a --body text containing
    # "IR; ssh one-shot" was denied). Unparseable quoting falls back to a
    # whitespace split (deny-side conservative).
    import shlex
    try:
        words = shlex.split(cmd)
    except ValueError:
        words = cmd.split()
    # ssh flags that take a separate value (must not be mistaken for the host)
    argful = {"-p", "-i", "-l", "-o", "-F", "-J", "-L", "-R", "-D", "-W",
              "-E", "-b", "-c", "-e", "-m", "-B", "-I", "-P", "-S", "-w"}
    # ssh as a command word: first token, or right after a separator — never
    # scp/rsync (different words), never `which ssh` / quoted mentions.
    starts = [k for k, w in enumerate(words)
              if (w == "ssh" and (k == 0 or words[k - 1][-1:] in (";", "&", "|", "(")))
              or w.endswith(("(ssh", "`ssh"))]  # $(ssh …) / `ssh …` substitution
    for k in starts:
        toks = words[k + 1:]
        host, remote = None, []
        i = 0
        while i < len(toks):
            t = toks[i]
            if t.startswith("-"):
                i += 2 if t in argful else 1
                continue
            host, remote = t, toks[i + 1:]
            break
        if host is None or not remote:
            continue  # bare interactive `ssh <host>` — a legitimate attach
        if remote[0].strip("'\"") == "tmux":
            continue  # the bridge's own control plane (attach/send-keys/capture-pane)
        return ["DENY: Remote-control work → use the `bridge` skill (persistent tmux; "
                "the remote tmux inherits TCC/FDA from its launching Terminal). "
                "Don't one-shot SSH — every call re-establishes nothing, long jobs need "
                "nohup hacks, and the user can't observe it. "
                "See ~/.claude/skills/bridge/SKILL.md."]
    return []
```

Catches a Bash command that is **command-executing SSH** (`ssh <host> '<cmd>'`, flags tolerated) and denies it with the bridge redirect. Passes untouched: bare interactive `ssh <host>` (attach), `scp`/`rsync` (the bridge's own sync mechanisms), and `ssh <host> tmux …` (the bridge's control plane).

**Why:** the miss is discovery, not knowledge — the bridge skill exists and is right, but passive carriers (memory, CLAUDE.md) get glided past; only a rule firing on the action itself reliably redirects. Per the F183 commissioning, the guard is a declarative rule, never a hand-hacked branch in `bash-guard.sh`.
