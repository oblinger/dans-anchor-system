# RULESET R-ob-commons
include::
description:: The commons operating model — repos whose history is machine-owned. Agents never commit or push them; an hourly sweep does, without attribution. Members: the vault (`~/ob/kmr`) and `~/ob/grove/commons`.

> [!info] Provenance
> Ruled by Dan 2026-08-22, after measuring that agent commits in the vault were both costly and unreliable: `git` itself is fast (0.12s status, 0.22s add on a 1.0 GB repo), but every commit is a tool-call round trip plus real reasoning about what to stage — and with 15 concurrent sessions an agent staging broadly commits *other* agents' half-finished work under its own message, so the provenance being paid for was already partly false. The vault has carried an hourly `km` commit-and-push since long before this rule; the rule stops agents duplicating it. Dan: *"there's just no provenance, no attribution. That's it. I think I'd rather that."*
>
> **Deliberately NOT a member: the other 18 repos under `~/ob/grove/`** (warden, dict-a-mux, ob-utils, sv, …). Those are code repos with release discipline, and `repo_sweep`'s design states the opposite norm for them — *"an agent commits the repo it touched in the turn it touched it; every commit this task makes means the norm failed"*. Adding one is a one-line change to `COMMONS` below; do it only on an explicit ruling.

### RULE R-ob-commons-01 — agents do not commit or push a commons repo (when:: tool:pre:Bash)

```python
def body(ctx):
    import os, shlex
    from pathlib import Path

    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    if "git" not in cmd:
        return []

    # The repos whose history is machine-owned. Paths, not names: a worktree or
    # a symlinked alias resolves into one of these or it does not.
    COMMONS = [Path.home() / "ob" / "kmr",
               Path.home() / "ob" / "grove" / "commons"]

    try:
        words = shlex.split(cmd)
    except ValueError:
        words = cmd.split()

    # `git` in COMMAND position only — never `echo "git commit"`, never a
    # --grep=commit search, never a path that happens to contain the word.
    starts = [k for k, w in enumerate(words)
              if (w == "git" or w.endswith("/git"))
              and (k == 0 or words[k - 1][-1:] in (";", "&", "|", "("))]
    if not starts:
        return []

    # The session's cwd, not os.getcwd() -- the latter is the DAEMON's, which is
    # never the caller's (the ATT T183 lesson, same as R-dispatch-guard).
    sess = getattr(getattr(ctx, "agent", None), "_session", None) or {}
    sess_cwd = sess.get("cwd") or ""

    # Subcommands that WRITE shared history. Reads are untouched on purpose:
    # `git show HEAD:path` is how an agent undoes its own mistake, and costs
    # nothing when unused.
    WRITES = {"commit", "push", "revert", "reset", "rebase", "merge", "cherry-pick"}
    # Flags that consume the next token, so its value is never read as the
    # subcommand or as a -C path.
    ARGFUL = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

    # A `cd` earlier in the SAME command line moves the base for every git that
    # follows it.  Without this the rule judged by session cwd alone, which is
    # wrong in both directions: `cd ~/ob/grove/warden && git commit` was denied
    # (false positive, hit live 2026-08-22), and `cd ~/ob/kmr && git commit`
    # from outside would have passed (false negative -- the one that matters).
    cd_base = None
    for k, w in enumerate(words):
        if w == "cd" and (k == 0 or words[k - 1][-1:] in (";", "&", "|", "(")) \
                and k + 1 < len(words) and not words[k + 1].startswith("-"):
            cd_base = words[k + 1]

    for k in starts:
        toks = words[k + 1:]
        target, sub, i = None, None, 0
        while i < len(toks):
            t = toks[i]
            if t == "-C" and i + 1 < len(toks):
                target = toks[i + 1]
                i += 2
                continue
            if t in ARGFUL:
                i += 2
                continue
            if t.startswith("-"):
                i += 1
                continue
            sub = t
            break
        if sub not in WRITES:
            continue

        base = target or cd_base or sess_cwd
        if not base:
            continue  # cannot resolve where this would run -- don't guess
        try:
            # expandvars as well as expanduser: a command written
            # `git -C "$HOME/ob/kmr/..." commit` reaches here with $HOME
            # UNEXPANDED (shlex does not expand, expanduser only knows ~).
            # Left unhandled it resolved to a nonexistent path, whose
            # .git walk climbed out to the vault and denied a NESTED repo
            # -- the exact false positive this rule must not produce.
            here = Path(os.path.expandvars(os.path.expanduser(base))).resolve()
        except OSError:
            continue
        # Resolve the ENCLOSING REPO, not the path prefix.  Five separate git
        # repos live inside the vault -- dans-anchor-system, Career Agents,
        # SV/ww/SVAI, the HookAnchor website, an Obsidian plugin -- and every
        # one of them is a satellite that KEEPS the commit-in-the-turn norm.
        # A path-prefix test would have silently blocked all five, which is the
        # opposite of what this rule is for.  km handles them as EXTRA_REPOS.
        # An UNRESOLVABLE target is never denied.  A shell variable the rule
        # cannot see -- `git -C "$D" commit`, D set earlier in the same line --
        # survives shlex and expandvars as the literal `$D` and resolves to a
        # path that does not exist.  Walking up from a phantom lands in the
        # vault and denies a satellite (hit live 2026-08-22, on two different
        # variables).  Failing OPEN here is deliberate: this guard exists to
        # break a habit, not to defeat a determined bypass, and a false
        # positive blocking legitimate satellite work costs far more than a
        # false negative letting one commit through.
        if not here.exists():
            continue
        repo = None
        probe = here
        while True:
            if (probe / ".git").exists():
                repo = probe
                break
            if probe.parent == probe:
                break
            probe = probe.parent
        if repo is None:
            continue  # not in a repo at all -- nothing to guard
        for root in COMMONS:
            try:
                rroot = root.resolve()
            except OSError:
                continue
            if repo == rroot:
                return ["DENY: `git %s` inside %s -- this repo is COMMONS: its history "
                        "is machine-owned. An hourly `km` sweep commits and pushes "
                        "everything, so your work IS being saved; you do not commit it, "
                        "and there is no attribution by design. Reads (`git show`, "
                        "`git log`, `git diff`) are still open -- use them freely. "
                        "Record WHY a change was made in the document itself (a dated "
                        "bullet, a `## History` line, the BRIEF), which is where this "
                        "vault's durable reasoning has always lived. "
                        "See ~/ob/kmr/CLAUDE.md -- The commons: you do not commit here."
                        % (sub, str(rroot).replace(str(Path.home()), "~"))]
    return []
```

Catches a Bash command that would **write shared history** in a commons repo — `commit`, `push`, `revert`, `reset`, `rebase`, `merge`, `cherry-pick` — resolved by `git -C <path>` when present and by the session's cwd otherwise. Passes untouched: every read (`show`, `log`, `diff`, `status`, `ls-files`), every `git` in a non-commons repo, `git add`/`git mv` (harmless on their own — the sweep commits whatever is staged either way), and any command where the target directory cannot be resolved.

**Why a rule and not a norm.** The same reason F183 gave for the bridge guard: passive carriers get glided past. A vault-wide CLAUDE.md line tells an agent once, at session start, and fifteen sessions later someone commits out of habit — which is exactly how the estate acquired 350 agent commits a week nobody had asked for.

**Why `add` and `mv` are not blocked.** Neither writes history. `git mv` in particular is *not* load-bearing for rename tracking — git records no renames at all and detects them at diff time by content similarity, so a plain `mv` swept up an hour later is followed identically.
