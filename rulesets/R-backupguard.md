# RULESET R-backupguard
include::
confirm:: user
description:: The estate's backup drives are one agent's custody — deny **every** write to `/Volumes/<X>/` from any anchor but [[Atticus|Atticus]], at `tool:pre:Bash`, `tool:pre:Write` and `tool:pre:Edit`. Fails closed: an unrecognised volume is treated as a backup drive, not waved through. Rides `anchor-base`, so it fires vault-wide; the exemption is the `masterguard` trait, which only Atticus's `.anchor` declares. Commissioned by Dan on [[Atticus Backlog#^T182|ATT T182]], 2026-08-21: *"no other agent may write to a backup… That way, we have one agent who's got the sole responsibility."*

> [!info] Provenance
> Filed as [[Atticus Backlog#^T252|T252]] alongside Dan's answer to [[Atticus Backlog#^T182|T182]]. That row asked whether [[R-masterguard]] should ride every anchor or stay on Atticus; Dan chose *stay*, **and added this second guard**, which is the better shape: the two rules want different verbs. Atticus must be able to write masters, so what he needs is a speed bump — the `.write-session` sentinel. Every other agent has no business on the drive at all, so what they need is a wall. One rule branching on identity would have been worse than two rules with one job each.
>
> It also closes a hole [[R-masterguard]] has carried since it was written: that rule fires at `tool:pre:Bash` only, so a `Write` or `Edit` tool call straight to a master path was never caught. This one binds all three write-capable moments.

### RULE R-backupguard-01 — no agent but Atticus writes to an external volume (when:: tool:pre:Bash)

```python
def body(ctx):
    # The exemption is a LOCATION, not an identity. Warden resolves rules from
    # the anchor the session is working in and exposes no per-agent value, so
    # "only Atticus" is really "only a session operating from an anchor that
    # declares `masterguard`" — today, `SYS/Staff/Atticus/.anchor` alone. Any
    # agent cwd'd there is exempt; Atticus working elsewhere is not. That gap is
    # real and small, and stating it is better than implying a stronger claim.
    if "masterguard" in (getattr(ctx, "traits", None) or []):
        return []

    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    # Cheap reject first: this rule fires on every Bash call in the vault.
    if "/Volumes/" not in cmd:
        return []

    import os
    import re
    import shlex

    # Not a drive: `∑` is a symlink to `/` (the boot volume, governed by
    # everything else), and the two TimeMachine paths are the OS's own. Every
    # other name under /Volumes/ is treated as a backup drive whether or not
    # the catalog knows it — see the fail-closed note below.
    NOT_A_DRIVE = ("∑", "com.apple.TimeMachine.localsnapshots", ".timemachine")
    VOL = re.compile(r"^/Volumes/([^/]+)(/|$)")

    def vol_of(tok):
        m = VOL.match(tok.strip("'\"<>"))
        if not m:
            return None
        v = m.group(1)
        if v in NOT_A_DRIVE:
            return None
        return v

    def split(s):
        try:
            return shlex.split(s)
        except ValueError:
            return s.split()          # unparseable quoting — deny-side conservative

    SEPS = (";", "&&", "||", "|", "&")

    def segments(words, depth=0):
        """Simple commands, including those nested inside quoted payloads.

        Drive work reaches a drive through the bridge as
        `ssh host "tmux send-keys -t w 'rm -rf /Volumes/BLACK/x' Enter"`. After
        one shlex pass the remote command is ONE token, so a rule reading only
        top-level tokens would wave through exactly the calls that matter most.
        """
        cur = []
        for w in words:
            if w in SEPS:
                if cur:
                    yield cur
                cur = []
                continue
            cur.append(w)
            if depth < 3 and "/Volumes/" in w and vol_of(w) is None:
                inner = split(w)
                if inner != [w]:
                    for seg in segments(inner, depth + 1):
                        yield seg
        if cur:
            yield cur

    # Reading FROM a drive is always allowed — `ls`, `find`, `shasum`, `cat`,
    # and `cp /Volumes/BLACK/x /tmp/` are how the catalog gets measured at all.
    # So position matters and mere mention does not.
    DEST_LAST = ("cp", "mv", "rsync", "ditto", "install", "scp")
    ANY_ARG = ("rm", "rmdir", "unlink", "shred", "truncate", "mkdir", "touch",
               "chmod", "chown", "chflags", "ln", "mkfifo", "tee")
    # Whole-volume verbs. These take no destination in the ordinary sense and
    # would sail past the two lists above, while being the fastest way to
    # destroy a drive that exists. `newfs_*` and `asr restore` have no read
    # form at all, so any of them aimed at a drive is a write.
    ALWAYS_VOLUME = ("newfs_apfs", "newfs_hfs", "asr")
    # `diskutil` is the exception, and it is an ALLOWLIST rather than a
    # deny-list — same fail-closed direction as the volume names themselves.
    # A deny-list here was wrong on its first test: it carried `apfs`, which
    # swallowed `diskutil apfs listCryptoUsers`, the exact command T184 used to
    # establish that 10T and 8T each have one crypto user and no recovery key.
    # Denying the instrument the catalog is measured with is worse than useless
    # — it teaches the next agent to route around the guard.
    DISKUTIL_READ = ("info", "information", "list", "verifyvolume", "verifydisk",
                     "mount", "mountdisk", "unmount", "unmountdisk", "eject")
    APFS_READ = ("list", "listcryptousers", "listusers", "listsnapshots",
                 "listvolumegroups", "unlockvolume")

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
                    hits.append((v, "a shell redirect onto the drive"))
        base = os.path.basename(seg[0].strip("'\""))
        args = [a for a in seg[1:] if a not in (">", ">>")]
        nonflag = [a for a in args if a[:1] != "-"]
        if base in DEST_LAST and nonflag:
            v = vol_of(nonflag[-1])
            if v:
                hits.append((v, "`%s` writing ONTO the drive" % base))
        elif base in ANY_ARG:
            for a in args:
                v = vol_of(a)
                if v:
                    hits.append((v, "`%s` mutating a path on the drive" % base))
        elif base == "dd":
            for a in args:
                if a.startswith("of="):
                    v = vol_of(a[3:])
                    if v:
                        hits.append((v, "`dd of=` targeting the drive"))
        elif base in ("zip", "tar") and nonflag:
            v = vol_of(nonflag[0])
            if v:
                hits.append((v, "`%s` writing its archive onto the drive" % base))
        elif base in ALWAYS_VOLUME:
            for a in args:
                v = vol_of(a)
                if v:
                    hits.append((v, "`%s` operating on the whole volume" % base))
        elif base == "diskutil":
            verb = (nonflag[0].lower() if nonflag else "")
            if verb == "apfs":
                ok = len(nonflag) > 1 and nonflag[1].lower() in APFS_READ
            else:
                ok = verb in DISKUTIL_READ
            if not ok:
                for a in args:
                    v = vol_of(a)
                    if v:
                        hits.append((v, "`diskutil %s` — not one of the read-only "
                                        "subcommands the catalog is measured with"
                                        % (verb or "?")))

    if not hits:
        return []

    # The escape is for a volume that genuinely is not a backup drive — a
    # camera card, a scratch USB. The sentinel sits at the VOLUME ROOT, which
    # this rule denies writing to, so a walled-off agent cannot create its own
    # exemption: only Dan by hand, or Atticus, can place one.
    hits = [h for h in hits
            if not os.path.exists("/Volumes/%s/.not-a-backup" % h[0])]
    if not hits:
        return []

    vol, why = hits[0]
    return ["DENY: %s. /Volumes/%s/ is treated as one of the estate's backup "
            "drives, and those are Atticus's sole custody — Dan's ruling on ATT "
            "T182, 2026-08-21: one agent has the keys, nobody else does. This is "
            "not a permission you can raise; it is whose job it is. Hand the work "
            "over instead: `state drop ATT --source <you> --tag drive` with what "
            "you need written and why. If /Volumes/%s is genuinely NOT a backup "
            "drive (a camera card, a scratch USB), ask Dan or Atticus to place "
            "/Volumes/%s/.not-a-backup at its root and this rule goes quiet for "
            "it." % (why, vol, vol, vol)]
```

Catches a Bash command that **writes onto any external volume** — a redirect, `cp`/`mv`/`rsync`/`ditto`/`install`/`scp` with the drive as destination, any of `rm`/`mkdir`/`touch`/`chmod`/`ln`/`tee`/… handed a drive path, `dd of=`, `zip`/`tar` building an archive there, or a whole-volume verb (`diskutil eraseVolume`, `asr restore`, `newfs_*`).

Passes untouched: every **read** of a drive (`ls`, `find`, `shasum`, `cat`, `cp <drive> /tmp/`), the read-only `diskutil` subcommands the catalog is measured with (`info`, `list`, `verifyVolume`, `mount`, `unmount`, `eject`, and `apfs list` / `listCryptoUsers` / `listUsers` / `listSnapshots` / `unlockVolume`), anything on `/Volumes/∑` or the TimeMachine paths, and everything from an anchor carrying `masterguard`.

**`diskutil` is an allowlist, and that is not a stylistic choice.** The first draft carried a deny-list, and it listed `apfs` — which swallowed `diskutil apfs listCryptoUsers`, the single command [[Atticus Backlog#^T184|T184]] used to establish that 10T and 8T each carry one crypto user and no recovery key, and the one [[Atticus Backlog#^T246|T246]] still needs for BLACK. The red-check caught it on the first run. A guard that denies the instrument its own catalog is measured with does not get obeyed; it gets routed around, which is how a discipline dies. So the read verbs are named and everything else is denied — the same fail-closed direction as the volume names.

**Verified both ways.** `Warden Corpus/harness/redcheck-backupguard.py` fires all three rules against 22 synthetic events: 11 that must DENY (`cp`/`rsync`/`rm`/redirect/`dd`/`tar` onto a drive, `diskutil eraseVolume`, an `rm` buried two quoting levels deep inside a bridge `ssh … tmux send-keys …` payload, an unrecognised volume name, and a `Write`/`Edit` straight at a master path), and 11 that must PASS (reads, the measurement subcommands, `/Volumes/∑`, a command naming no volume, a vault Write, and all three moments from an anchor carrying `masterguard`). The fixture assembles `/Volumes` and `__MASTERS__` from fragments, because the *first* attempt to write it was itself denied by [[R-masterguard]] — a heredoc carrying a literal master path is a Bash command that writes to the master as far as the guard can tell. That is the guards working, and it is worth knowing before writing the next test.

### RULE R-backupguard-02 — no agent but Atticus Writes a file onto an external volume (when:: tool:pre:Write)

```python
def body(ctx):
    if "masterguard" in (getattr(ctx, "traits", None) or []):
        return []
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    import os
    import re
    NOT_A_DRIVE = ("∑", "com.apple.TimeMachine.localsnapshots", ".timemachine")
    # Resolve first: a symlink into a drive (`~/mnt10T -> /Volumes/10T`) reaches
    # the same bytes without the literal prefix. Cheap — one syscall — and only
    # available on this path, which is why the Bash rule above is string-based
    # and this one is not.
    try:
        real = os.path.realpath(target)
    except OSError:
        real = target
    m = re.match(r"^/Volumes/([^/]+)(/|$)", real)
    if not m or m.group(1) in NOT_A_DRIVE:
        return []
    vol = m.group(1)
    if os.path.exists("/Volumes/%s/.not-a-backup" % vol):
        return []
    return ["DENY: Write to /Volumes/%s/ — the estate's backup drives are "
            "Atticus's sole custody (ATT T182, Dan, 2026-08-21). Hand the work "
            "over with `state drop ATT --source <you> --tag drive`. If this "
            "volume is genuinely not a backup drive, ask Dan or Atticus to place "
            "/Volumes/%s/.not-a-backup at its root." % (vol, vol)]
```

### RULE R-backupguard-03 — no agent but Atticus Edits a file on an external volume (when:: tool:pre:Edit)

```python
def body(ctx):
    if "masterguard" in (getattr(ctx, "traits", None) or []):
        return []
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    import os
    import re
    NOT_A_DRIVE = ("∑", "com.apple.TimeMachine.localsnapshots", ".timemachine")
    try:
        real = os.path.realpath(target)
    except OSError:
        real = target
    m = re.match(r"^/Volumes/([^/]+)(/|$)", real)
    if not m or m.group(1) in NOT_A_DRIVE:
        return []
    vol = m.group(1)
    if os.path.exists("/Volumes/%s/.not-a-backup" % vol):
        return []
    return ["DENY: Edit of a file on /Volumes/%s/ — the estate's backup drives "
            "are Atticus's sole custody (ATT T182, Dan, 2026-08-21). Hand the "
            "work over with `state drop ATT --source <you> --tag drive`. If this "
            "volume is genuinely not a backup drive, ask Dan or Atticus to place "
            "/Volumes/%s/.not-a-backup at its root." % (vol, vol)]
```

**Why it fails closed.** A guard built from a *list of backup-drive names* goes wrong the first time a drive is renamed or remounts as `10T 1`, and it goes wrong silently — the write lands and nothing reports it. BIG BLUE has already been renamed once. So the default is deny, and the allowlist holds only the three `/Volumes/` entries that are not drives at all. The cost is that a legitimately-unrelated volume needs a sentinel; the benefit is that a newly-attached drive is dangerous by default rather than safe by default, which is the direction an error should point on a surface with no undo.

**Why the exemption is the `masterguard` trait and not a name.** Warden resolves rules from the anchor the session is working in and exposes no per-agent value. Keying the exemption on the trait that *already* marks the custodian anchor makes the coupling say what it means: the one anchor gated by the careful-write rule is the one exempt from the wall, and there is no second place to keep in sync. It also means the exemption travels correctly if Atticus's tree ever moves. What it does not do is identify an *agent* — any session operating from that anchor is exempt, and Atticus working from another anchor is not. Widening it would take a deliberate `traits: [masterguard]` in some other `.anchor`, which is Dan's edit to make.

**What a Warden rule cannot do.** It intercepts tool calls, so it guards against **accident, not intent** — a script, a Python `shutil.copy`, or anything spawned outside the hooked moments still reaches the drive. What actually makes "one agent has the keys" true is physical: 10T and 8T each carry exactly one crypto user, a passphrase, with no recovery key, and auto-unlock lives in haorui's keychain. That is the lock. This is the seatbelt.
