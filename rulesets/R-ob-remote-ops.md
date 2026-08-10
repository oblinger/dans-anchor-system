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
        rc = remote[0].strip("'\"")
        if len(remote) == 1:
            # a quoted remote command is ONE token after the outer shlex.split
            # (e.g. `ssh host "tmux send-keys -t '...' '...' Enter"`) — retokenize
            # just that token to find its actual first word.
            try:
                parts = shlex.split(remote[0])
            except ValueError:
                parts = remote[0].split()
            rc = parts[0] if parts else ""
        if rc == "tmux":
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

### RULE R-ob-remote-ops-02 — detached remote launch → `bridge run` (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    if "tmux" not in cmd:
        return []
    # The launcher itself launches detached -- that is its job. It identifies
    # itself by the wrapper it invokes, so the exemption cannot be spoofed by
    # simply naming a window "job-something".
    if "job-wrapper.sh" in cmd:
        return []
    # Stated-reason escape. A bare --force becomes reflex; a sentence does not.
    # Same shape as --why-ask / --why-user / --why-user-action elsewhere in the
    # estate: proceed, but leave an auditable record of the judgement.
    import re
    if re.search(r"#\s*oneshot:\s*\S", cmd):
        return []
    import shlex
    try:
        words = shlex.split(cmd)
    except ValueError:
        words = cmd.split()
    # Retokenize any single quoted blob (`ssh host "tmux new-window -d ..."`),
    # so the subcommand is visible whichever quoting form was used.
    flat = list(words)
    for w in words:
        if "tmux" in w and " " in w:
            try:
                flat.extend(shlex.split(w))
            except ValueError:
                flat.extend(w.split())
    detached = False
    for k, w in enumerate(flat):
        if w != "tmux":
            continue
        rest = flat[k + 1:]
        if not rest:
            continue
        sub = rest[0]
        if sub in ("new-window", "new-session", "new") and "-d" in rest:
            detached = True
            break
    if not detached:
        return []
    return ["DENY: launching detached remote work → use `bridge run` "
            "(~/.claude/skills/bridge/bridge run <host> --job <name> --script <path>). "
            "It wraps the WHOLE job in caffeinate, records the job's process group, "
            "and arms the liveness watch as part of starting it — so `bridge jobs <host>` "
            "can tell a silent-but-working job from a wedged one. "
            "A hand-rolled `tmux new-window -d` gives none of that: on 2026-08-09 one was "
            "reported as running for 105 minutes while blocked on a spun-down disk (ATT F054). "
            "For a genuinely bounded probe, append `# oneshot: <why this needs no watch>`."]
```

Catches a Bash command that launches **detached** remote work — `tmux new-window -d`, `new-session -d` — and redirects it to `bridge run`. Passes untouched: the launcher itself (identified by `job-wrapper.sh`, not by a window name), every foreground `tmux` verb (`list-windows`, `capture-pane`, `send-keys`, `kill-window`), and any command carrying a stated `# oneshot: <reason>`.

**Why:** `R-ob-remote-ops-01` exempts `ssh <host> tmux …` as the bridge's control plane, and that exemption is the gap — every job launched on 2026-08-09, including the one that wedged, went through it. The hazard is not "a remote command" but **starting something and walking away**: a foreground command returns, so a human or agent sees it; a detached one is only ever as observable as whatever was set up to watch it, and setting that up is the step that gets skipped under time pressure. The escape hatch demands a sentence rather than a flag, because the failure this guards against is not ignorance of the rule — it is fluent, hurried bypassing of one.
