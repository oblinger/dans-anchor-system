# RULESET R-masterguard
include::
description:: The master archive is a write-once surface (ATT T178) — deny any Bash command that writes into `/Volumes/<X>/__MASTERS__/` unless a write session is explicitly open on that volume. Rides the **Atticus anchor only** (`traits: [Container, masterguard]`) — Dan's ruling on [[ATT Backlog#^T182|ATT T182]], 2026-08-21: disk custody is one agent's job, and every *other* agent is walled off from backup drives entirely by `R-backupguard` rather than gated by this rule. Fires at `tool:pre:Bash` — which means a `Write`/`Edit` tool call to a master path is **not** caught here; see [[ATT Backlog#^T252|T252]].

> [!info] Provenance
> Commissioned as [[ATT Backlog#^T181|T181]], split out of [[ATT Backlog#^T178|T178]] when the write-once rule was ratified 2026-08-13. The rule was written down that day ([[Disk Conventions]] § The write-once rule, [[Disk Procedures]] § P5) and half-instrumented: `master_sweep` catches orphan scratch before a clone can make it permanent, which is the *completeness* half. This is the *immutability* half. Until it existed, an agent could copy over an existing master path and nothing would notice — while the ledger went on asserting the old checksum, which is worse than making no claim at all. [[ATT Backlog#^T147|T147]] and [[ATT Backlog#^T180|T180]] are the same lesson twice: an unenforced claim reports success against a weaker test than the one specified, and a discipline with no mechanism decays.

### RULE R-masterguard-01 — writes to the master archive need an open write session (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    # Cheap reject first: this rule fires on every Bash call in the vault.
    if "__MASTERS__" not in cmd:
        return []

    import os
    import re
    import shlex

    # `__MASTERS__` at the VOLUME ROOT means "this drive IS the master" — the
    # discipline is Disk Conventions', not this rule's invention. A clone holds
    # the same subtree one level down (`Clone of 10T/__MASTERS__/`) and is NOT
    # the master, so it must pass: otherwise this rule would deny the very
    # clone-the-master procedure (P2) it exists to protect the source of.
    MASTER = re.compile(r"^/Volumes/([^/]+)/__MASTERS__(/|$)")

    def vol_of(tok):
        m = MASTER.match(tok.strip("'\"<>"))
        return m.group(1) if m else None

    def split(s):
        try:
            return shlex.split(s)
        except ValueError:
            return s.split()          # unparseable quoting — deny-side conservative

    SEPS = (";", "&&", "||", "|", "&")

    def segments(words, depth=0):
        """Simple commands, including those nested inside quoted payloads.

        Most master work reaches the drive through the bridge, as
        `ssh host "tmux send-keys -t w 'rm -rf /Volumes/10T/__MASTERS__/x' Enter"`.
        After one shlex pass the whole remote command is ONE token, so a rule
        that only looked at top-level tokens would see no master path at all and
        wave through exactly the commands that matter most. Recurse into any
        token that still mentions a master path. Two levels covers the bridge
        form; the bound stops a pathological string from spinning.
        """
        cur = []
        for w in words:
            if w in SEPS:
                if cur:
                    yield cur
                cur = []
                continue
            cur.append(w)
            if depth < 3 and "__MASTERS__" in w and vol_of(w) is None:
                inner = split(w)
                if inner != [w]:
                    for seg in segments(inner, depth + 1):
                        yield seg
        if cur:
            yield cur

    # Verbs whose destination is the LAST non-flag argument. Reading FROM the
    # master is always allowed, which is why position matters and mere mention
    # does not: `cp /Volumes/10T/__MASTERS__/x /tmp/` is a read.
    DEST_LAST = ("cp", "mv", "rsync", "ditto", "install", "scp")
    # Verbs that mutate every path they are handed.
    ANY_ARG = ("rm", "rmdir", "unlink", "shred", "truncate", "mkdir", "touch",
               "chmod", "chown", "chflags", "ln", "mkfifo", "tee")

    # Glued redirects (`>/Volumes/...`) split so the target is its own token.
    flat = []
    for w in split(cmd):
        if w[:1] == ">" and len(w.lstrip(">")) > 0:
            flat.append(">>" if w[:2] == ">>" else ">")
            flat.append(w.lstrip(">"))
        else:
            flat.append(w)

    hits = []
    for seg in segments(flat):
        for k, w in enumerate(seg):
            if w in (">", ">>") and k + 1 < len(seg):
                v = vol_of(seg[k + 1])
                if v:
                    hits.append((v, "a shell redirect into the master"))
        base = os.path.basename(seg[0].strip("'\""))
        args = [a for a in seg[1:] if a not in (">", ">>")]
        nonflag = [a for a in args if a[:1] != "-"]
        if base in DEST_LAST and nonflag:
            v = vol_of(nonflag[-1])
            if v:
                hits.append((v, "`%s` writing INTO the master" % base))
        elif base in ANY_ARG:
            for a in args:
                v = vol_of(a)
                if v:
                    hits.append((v, "`%s` mutating a master path" % base))
        elif base == "dd":
            for a in args:
                if a.startswith("of="):
                    v = vol_of(a[3:])
                    if v:
                        hits.append((v, "`dd of=` targeting the master"))
        elif base in ("zip", "tar") and nonflag:
            v = vol_of(nonflag[0])
            if v:
                hits.append((v, "`%s` writing its archive into the master" % base))

    if not hits:
        return []

    # The escape is a deliberate physical act on the drive itself, not a flag.
    # The sentinel sits at the VOLUME ROOT, so creating it is not itself a write
    # to `__MASTERS__` and this rule does not lock the agent out of opening one.
    # Disk Procedures P4 removes it at close-out; a sentinel left behind is a
    # finding master_sweep reports.
    hits = [h for h in hits
            if not os.path.exists("/Volumes/%s/.write-session" % h[0])]
    if not hits:
        return []

    vol, why = hits[0]
    return ["DENY: %s. /Volumes/%s/__MASTERS__/ is a WRITE-ONCE surface — content "
            "at a path never changes, and every write goes through a deliberate "
            "session so the ledger's write-ahead row lands first (Disk Procedures "
            "P1/P5). Nothing here is a formality: a 15.4 GB abandoned scratch file "
            "sat on this drive for seven weeks and was found by accident, and an "
            "overwrite is worse than that because the ledger keeps asserting the "
            "OLD checksum afterwards. To proceed, open a session on the drive: "
            "  echo \"$(date -u +%%FT%%TZ) <who> <why>\" > /Volumes/%s/.write-session "
            "and close it with Disk Procedures P4 (master_sweep, then remove the "
            "sentinel) before unmounting." % (why, vol, vol)]
```

Catches a Bash command that **writes into a master archive** — a redirect, `cp`/`mv`/`rsync`/`ditto`/`install`/`scp` with the master as destination, any of `rm`/`mkdir`/`touch`/`chmod`/`ln`/`tee`/… handed a master path, `dd of=`, or `zip`/`tar` building an archive there — and denies it unless `/Volumes/<X>/.write-session` exists.

Passes untouched: every **read** of the master (`ls`, `find`, `shasum`, `cat`, `cp <master> /tmp/`), any write to a **clone** (`/Volumes/8T/Clone of 10T/__MASTERS__/…` — one level down, so not a master by Disk Conventions), and everything on a volume with an open write session.

**Why the sentinel rather than a flag.** A `--force` becomes reflex; the same reasoning `R-ob-remote-ops-02` applies to `# oneshot:`. Here it can be stronger than a sentence, because the drive itself can hold the state: opening a session is a deliberate act on the physical thing being protected, it names who and why, it survives across agents and sessions, and it has a natural close in P4. It also composes — `master_sweep` reports a sentinel someone forgot to remove, so an abandoned write session is as visible as abandoned scratch.

**Why writes are gated even when the path is new.** The rule as stated forbids only *changing* content at an existing path, so an add is legal — but P1 requires the ledger's write-ahead `PENDING` row *before* any bytes land, and gating adds too is what makes that ordering happen. Statting the destination to allow unlogged adds would be more precise about the letter of the rule and would silently drop the procedure the rule depends on.
