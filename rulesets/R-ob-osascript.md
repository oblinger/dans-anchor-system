# RULESET R-ob-osascript
include::
confirm:: user
description:: Ob's raw-automation hygiene — where a sanctioned wrapper exists (`notmuch`, `ctrl`, the glance form), raw `osascript` and control-flavoured `obsidian://` URLs are denied and redirected to it. Keyed by TARGET APPLICATION, so the ~45% of automation no wrapper covers passes untouched (`tool:pre:Bash` deny, rides `anchor-base`).

> [!info] Provenance
> Commissioned by Dan 2026-08-28 — *"we should go ahead and put the rule in to cover the key ones that are really getting us mashed right now."* The census that sized it: **1,314 `osascript` calls in 7 days**, of which 206 were Mail searches the estate has forbidden in writing since 2026-08-13 (`feedback_never_osascript_mail_search.md`, *"You gotta put a remembrance in for this, man. This has happened multiple times."*). That memory is loaded into every session in that project and was violated 206 times in a week — which is the whole argument for a rule: **the miss is not knowledge, and adding more documentation to a documentation failure does not converge.**

## Why this ruleset is keyed to the APPLICATION, not to `osascript`

An earlier design had the agent attest that nothing in `/io` or `ctrl` covered its case before proceeding. Dan killed it on sight, correctly: *"that also becomes kind of a boilerplate, doesn't it."*

It does, and the reason is worth keeping, because it rules out a whole family of designs. **A stated-reason escape catches laziness; it cannot catch ignorance — and ignorance is what this rule is for.** `R-ob-remote-ops-02`'s stated-reason escape works because the agent certifies a fact about *its own job* ("this probe is bounded"), which it has first-hand. Asking instead for *"nothing in `/io` or `ctrl` does this"* demands a **negative about a catalog the agent has not read** — so the agent that is wrong is wrong in exactly the way that makes its justification sincere. It does not know `local-mail` exists; it writes "nothing covers this"; it means it.

So the catalog lives in the rule. The rule knows Mail-search maps to `notmuch`, `do javascript` maps to `ctrl cpage`, `keystroke` maps to `ctrl screen type`. **The agent writes nothing, so there is nothing to turn into boilerplate**, and the deny message *delivers* the alternative at the moment of reach instead of asking whether the agent already had it. There is deliberately **no escape hatch** in this ruleset.

When a denied path is genuinely the only way, the answer is not to evade the rule — it is to say so to the user and file the gap against the wrapper that should have covered it. Each such block improves `ctrl` or `/io` and then never fires again; an escape hatch, by contrast, accumulates.

## What it does NOT touch, and why that is the design

Measured over the same 7 days, these have **no sanctioned alternative** and therefore pass untouched:

| bucket | calls/7d (08-21) | after 2026-09-03 |
|---|---|---|
| window move / size / focus | 162 | **`ctrl win`** — rule -05 |
| browser tab inventory | 80 | **`ctrl tabs`** — rule -02, widened |
| app quit / activate / close | 76 | **`ctrl win focus / quit / close`** — rules -02 / -05 (bare activate/quit only) |
| AX-targeted clicks (`click button "OK"`) | — | nothing — `ctrl screen click` is coordinates only |
| menu-bar drilling | 19 | nothing |
| Mail compose / send | 40 → 2 | nothing, and no longer worth a wrapper |
| app-specific scripting (Photos, Contacts, Preview, Terminal `do script`) | ~40 | nothing — genuine one-offs, pass by design |

**What remains outside every wrapper is app-specific scripting, AX clicks and menu drilling**, and a rule that taxed those would be routed around rather than obeyed. The `ctrl tabs` / `ctrl win` wrappers landed 2026-09-03 and rules -02 and -05 widened behind them the same day ([[Atticus P0014]]); **each rule below may only be widened once the wrapper it would redirect to actually exists.** Enforcement cannot precede the wrapper: `/io imail` is itself seven blocks of `osascript`, so a rule denying "osascript for mail" while pointing at `/io imail` would deny its own remedy.

### RULE R-ob-osascript-01 — Mail SEARCH via osascript → the notmuch index (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    if "osascript" not in cmd or "Mail" not in cmd:
        return []
    import re, shlex

    def payloads(s, depth=0, out=None):
        # Every osascript payload, including one nested inside a quoted
        # `tmux send-keys ...` argument -- the census found real calls in
        # exactly that shape. Command-position only: `grep osascript notes.md`
        # must never read as an invocation, the lesson R-ob-remote-ops-01 and
        # -02 each had to learn separately.
        out = [] if out is None else out
        try:
            ws = shlex.split(s)
        except ValueError:
            ws = s.split()
        for k, w in enumerate(ws):
            if (w == "osascript" or w.endswith("/osascript")) and (
                    k == 0 or ws[k - 1][-1:] in (";", "&", "|", "(")):
                out.append(" ".join(ws[k + 1:]))
            elif depth < 2 and " " in w and "osascript" in w:
                payloads(w, depth + 1, out)
        # Heredoc BODIES (2026-09-03): a script written with `cat > x.sh <<'EOS'`
        # and run afterwards carries `osascript <<'OSA'` on a line of its own,
        # never at shell command position -- the census found 32 browser calls
        # in exactly that shape, 0 denied. A line that STARTS with osascript
        # followed by -e / a heredoc / a path / end-of-line is an invocation;
        # everything from that line to the end is its payload. Prose that merely
        # mentions osascript mid-line still never matches.
        if depth == 0:
            for m in re.finditer(r"(?m)^[ \t]*(?:\S*/)?osascript(?=\s+(?:-|<<)|\s*$)", s):
                out.append(s[m.end():])
        return out

    for p in payloads(cmd):
        if not re.search(r'tell\s+application\s+"Mail"', p, re.I):
            continue
        # Composing has NO wrapper -- osascript is the only way to send mail
        # from here, so it is not denied. Only reads are.
        if re.search(r"make\s+new\s+outgoing\s+message|outgoing\s+message", p, re.I):
            continue
        if not re.search(r"\bwhose\b|subject\s+of|sender\s+of|content\s+of|"
                         r"\bmessages\b|\bmailboxes\b|\bcount\b", p, re.I):
            continue
        return ["DENY: searching Mail with AppleScript -> use the notmuch index: "
                "notmuch search 'from:x and date:2026-08-01..' (Xapian syntax; "
                "--format=json to parse, --output=files for Maildir paths). "
                "It answers in ~15 ms where a `whose` sweep takes minutes to hours, "
                "spans every mirrored account in ONE query, needs no auth and no GUI, "
                "and does not tie up the user's own Mail.app. "
                "A NONZERO count is not coverage -- check recency before believing a "
                "miss: `mailsync --status` names any account that is stale or has no "
                "credential. Composing/sending mail is NOT denied by this rule; there "
                "is no wrapper for it yet."]
    return []
```

Catches an `osascript` payload that tells **Mail** to read, search or count. Passes: composing and sending (no wrapper exists), and any command that merely mentions Mail in prose.

**Why reads and not composes.** 206 of the 263 Mail calls in the census were reads, and every one of them had a first-class alternative roughly four orders of magnitude faster. The 40 composes had none. Denying both would have made the rule wrong 40 times a week for no gain, and a rule that is visibly wrong stops being read as authority.

### RULE R-ob-osascript-02 — driving a browser with osascript → `ctrl` (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    if "osascript" not in cmd:
        return []
    import re, shlex

    def payloads(s, depth=0, out=None):
        out = [] if out is None else out
        try:
            ws = shlex.split(s)
        except ValueError:
            ws = s.split()
        for k, w in enumerate(ws):
            if (w == "osascript" or w.endswith("/osascript")) and (
                    k == 0 or ws[k - 1][-1:] in (";", "&", "|", "(")):
                out.append(" ".join(ws[k + 1:]))
            elif depth < 2 and " " in w and "osascript" in w:
                payloads(w, depth + 1, out)
        # Heredoc BODIES (2026-09-03): a script written with `cat > x.sh <<'EOS'`
        # and run afterwards carries `osascript <<'OSA'` on a line of its own,
        # never at shell command position -- the census found 32 browser calls
        # in exactly that shape, 0 denied. A line that STARTS with osascript
        # followed by -e / a heredoc / a path / end-of-line is an invocation;
        # everything from that line to the end is its payload. Prose that merely
        # mentions osascript mid-line still never matches.
        if depth == 0:
            for m in re.finditer(r"(?m)^[ \t]*(?:\S*/)?osascript(?=\s+(?:-|<<)|\s*$)", s):
                out.append(s[m.end():])
        return out

    BROWSERS = (r'"(Safari|Google Chrome|Google Chrome Beta|Google Chrome Canary|'
                r'Brave Browser|Chromium|Firefox)"')
    for p in payloads(cmd):
        if not re.search(r"tell\s+application\s+(id\s+)?" + BROWSERS, p, re.I):
            continue
        if re.search(r"do\s+javascript|execute\s+javascript", p, re.I):
            return ["DENY: running JavaScript in a browser via AppleScript -> use ctrl. "
                    "`ctrl cpage <tab|url>` extracts a page through Chrome CDP against "
                    "your REAL Chrome (so it inherits logged-in sessions), `ctrl cexec` "
                    "runs JS there, and `ctrl jpage <url>` is the Safari equivalent. "
                    "These return structured JSON instead of a string you re-parse, and "
                    "they do not depend on Safari's AllowJavaScriptFromAppleEvents being "
                    "set. Claim the browser lease first (`ctrl own`) -- it is one surface "
                    "per machine. Tab INVENTORY and quit/activate are not denied; nothing "
                    "covers those yet."]
        if re.search(r"set\s+URL\b|open\s+location|make\s+new\s+tab|"
                     r"make\s+new\s+document", p, re.I):
            return ["DENY: navigating a browser via AppleScript -> use ctrl. "
                    "`ctrl surf <url>` (new tab), `ctrl tab <url>` (new tab, keeps "
                    "focus), `ctrl navigate <url>` (current tab), `ctrl new-tab`. "
                    "Claim the browser lease first (`ctrl own`)."]
        # Widened 2026-09-03 (ATT P0014) once `ctrl tabs` existed: the census's
        # largest uncovered bucket was "which tab am I on / bring it front".
        if re.search(r"\b(URL|title|name)\s+of\s+(active|current)\s+tab|"
                     r"\btabs\s+of\b|active\s+tab\s+index|current\s+tab\s+of|"
                     r"set\s+(active\s+tab\s+index|current\s+tab)\b", p, re.I):
            return ["DENY: reading or switching browser tabs via AppleScript -> "
                    "`ctrl tabs` lists every open tab in Safari / Chrome / Chrome Beta "
                    "as S3 / C2 / B1 rows with the active one starred (--json for "
                    "rows), and `ctrl tabs --activate C2` brings one to the front "
                    "(takes the browser lease). No lease needed to list."]
        # Bare activate/quit: the tell names the browser and the script does
        # nothing else. Unanchored on purpose -- the raw-line payload still
        # carries its `-e '` prefix and the shlex payload has lost its quotes.
        if (re.search(r"tell\s+application\s+(id\s+)?\"?(Safari|Google Chrome( Beta| Canary)?|"
                      r"Brave Browser|Chromium|Firefox)\"?\s+(to\s+)?(activate|quit)\b", p, re.I)
                and not re.search(r"\b(set|get|do|make|click|keystroke|open|return|repeat|"
                                  r"delete|save|spotlight|reveal|select|close|count|exists)\b", p, re.I)):
            return ["DENY: activating or quitting a browser via AppleScript -> "
                    "`ctrl win focus <app>` / `ctrl win quit <app>` (focus on a "
                    "browser takes the lease); `ctrl tabs --activate <id>` when it "
                    "is a particular tab you want in front."]
    return []
```

Catches `do javascript`, navigation, tab inventory / switching, and a bare `activate` / `quit` against any browser. Passes: closing windows, and any script whose browser work is more than activate/quit (the wrapper would not cover it).

**Heredoc bodies count (2026-09-03).** The first week after shipping, the census found 32 browser `do JavaScript` calls and 0 denials: every one was a script written with `cat > x.sh <<'EOS'` and run afterwards, so `osascript` sat on a line of the file body and never at shell command position. The shared `payloads()` helper in -01/-02/-03 now also treats a line that *starts* with `osascript` followed by `-e`, a heredoc, or end-of-line as an invocation and reads the rest of the text as its payload. Prose that mentions osascript mid-line still passes; `grep osascript notes.md` still passes. Fixtures: the Wells order-page script → denied; the same AppleScript quoted in a note → passes. ([[Atticus P0014]])

### RULE R-ob-osascript-03 — synthesised keystrokes and coordinate clicks → `ctrl screen` (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    if "osascript" not in cmd or "System Events" not in cmd:
        return []
    import re, shlex

    def payloads(s, depth=0, out=None):
        out = [] if out is None else out
        try:
            ws = shlex.split(s)
        except ValueError:
            ws = s.split()
        for k, w in enumerate(ws):
            if (w == "osascript" or w.endswith("/osascript")) and (
                    k == 0 or ws[k - 1][-1:] in (";", "&", "|", "(")):
                out.append(" ".join(ws[k + 1:]))
            elif depth < 2 and " " in w and "osascript" in w:
                payloads(w, depth + 1, out)
        # Heredoc BODIES (2026-09-03): a script written with `cat > x.sh <<'EOS'`
        # and run afterwards carries `osascript <<'OSA'` on a line of its own,
        # never at shell command position -- the census found 32 browser calls
        # in exactly that shape, 0 denied. A line that STARTS with osascript
        # followed by -e / a heredoc / a path / end-of-line is an invocation;
        # everything from that line to the end is its payload. Prose that merely
        # mentions osascript mid-line still never matches.
        if depth == 0:
            for m in re.finditer(r"(?m)^[ \t]*(?:\S*/)?osascript(?=\s+(?:-|<<)|\s*$)", s):
                out.append(s[m.end():])
        return out

    for p in payloads(cmd):
        if "System Events" not in p:
            continue
        if re.search(r"\bkeystroke\b|\bkey\s+code\b", p, re.I):
            return ["DENY: synthesising keystrokes with System Events -> use "
                    "`ctrl screen type \"<text>\"` / `ctrl screen key <keyspec>` "
                    "(return, cmd+j, esc). System Events' keystroke DROPS CHARACTERS "
                    "under load -- a recorded failure in this estate -- and it types "
                    "into whatever happens to be frontmost, which is how a line lands in "
                    "someone's half-written command. NEVER inject keystrokes blind: "
                    "confirm what is focused first (`ctrl screen grab`). If the target is "
                    "a tmux pane, drive it with tmux send-keys, not the GUI."]
        # Coordinate clicks have a wrapper; AX-targeted clicks (click button "OK",
        # click menu item ...) do NOT -- `ctrl screen click` takes points, and
        # nothing walks the accessibility tree. Denying those would deny the only
        # route that exists.
        if re.search(r"\bclick\s+at\b", p, re.I):
            return ["DENY: clicking by coordinate with System Events -> use "
                    "`ctrl screen click X Y` (logical points; --px for pixels, --right, "
                    "--double). Pair it with `ctrl screen grab` and `ctrl screen size` so "
                    "the coordinates come from what is actually on screen rather than "
                    "from assumption. Clicking a NAMED element (click button \"OK\", "
                    "click menu item) is not denied -- nothing covers the accessibility "
                    "tree yet."]
    return []
```

Catches `keystroke`, `key code`, and coordinate clicks. Passes: window geometry, `frontmost`, process-existence probes, menu-bar drilling, and every accessibility-tree click.

### RULE R-ob-osascript-04 — never drive Obsidian; glance a note by opening the FILE (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    import re, shlex
    GLANCE = ("Glance a note by opening the FILE -- `open \"/abs/path/to/Note.md\"`. "
              "Obsidian Double Click is the registered handler for .md, so that lands "
              "the note in a NEW TAB in Dan's own Obsidian (measured 2026-08-28: "
              "18 tabs -> 19). Know it only by name? `open \"$(ha -p 'Some Note')\"`. "
              "A path has nothing to remember; the URI it replaced carried TWO "
              "load-bearing parameters and agents kept dropping one of them.")

    # A heredoc body is DATA, not command position. Strip it before anything
    # else looks at the string -- otherwise writing documentation ABOUT this
    # rule trips this rule, which is exactly what happened to
    # R-ob-remote-ops-01 (TINK T609) and then, within the hour, to the first
    # cut of THIS rule while it was being written up. A guard that cannot be
    # described without firing is a guard people learn to disable.
    scan = re.sub(r"<<-?\s*'?\"?(\w+)'?\"?\n.*?\n\1\b", " ", cmd, flags=re.S)

    if "osascript" in scan:
        def payloads(s, depth=0, out=None):
            out = [] if out is None else out
            try:
                ws = shlex.split(s)
            except ValueError:
                ws = s.split()
            for k, w in enumerate(ws):
                if (w == "osascript" or w.endswith("/osascript")) and (
                        k == 0 or ws[k - 1][-1:] in (";", "&", "|", "(")):
                    out.append(" ".join(ws[k + 1:]))
                elif depth < 2 and " " in w and "osascript" in w:
                    payloads(w, depth + 1, out)
            return out
        for p in payloads(scan):
            if re.search(r'tell\s+application\s+(id\s+)?"Obsidian"|tell\s+process\s+"Obsidian"', p, re.I):
                return ["DENY: driving Obsidian with AppleScript. " + GLANCE]

    # `obsidian://` needs no osascript, so it is checked separately -- but only
    # as a genuine ARGUMENT, never as text. The URI must be a whole token (after
    # quote-stripping), which is what separates `open "obsidian://open?..."` from
    # a sentence that merely names the scheme. Same discipline as command-position
    # matching above; the difference is that here the token IS the payload.
    try:
        words = shlex.split(scan)
    except ValueError:
        words = scan.split()
    for w in words:
        if not re.match(r"obsidian://", w, re.I):
            continue
        return ["DENY: hand-built obsidian:// URI. " + GLANCE +
                " Advanced-URI command execution (commandid=, eval=) is "
                "remote-controlling Dan's editor and is never the answer; a bare "
                "obsidian://open is worse than useless -- it does not open a tab at "
                "all, it REPLACES the contents of the focused one, which is the "
                "CMX P0001 clobber that destroyed his reading position for months. "
                "The whole URI surface is retired for agents: open the file."]
    return []
```

Catches AppleScript against Obsidian and **every** hand-built `obsidian://` URI. Passes: any prose that merely names the scheme, and any heredoc that documents it.

**This is the blanket deny that was originally asked for, and it became correct once a redirect target existed.** The first cut carved out `obsidian://open?…&paneType=tab`, because that URI *was* the sanctioned glance and there was nothing else to name. Dan's answer removed the premise: *"the glance mechanism for obsidian for a markdown file should just be to open the markdown file. I think double click will actually work properly for that."* Measured the same hour — a plain `open` on a `.md` takes the tab count 18 → 19, because Obsidian Double Click is the registered `.md` handler and routes through Advanced URI, which never clobbers.

**Why a path beats the URI it replaces.** The URI carried two load-bearing parameters and agents kept dropping one: `-b md.obsidian` (or the doc lands on a HUD, since the HUD apps are rebadged Obsidian binaries that can win the URL scheme) and `&paneType=tab` (or the glance destroys what Dan was reading). A file path has neither, cannot clobber, cannot land on a HUD, and needs nothing remembered — the routing decision moves into ODC, where it is code under test rather than a string every agent retypes. This is the general principle the whole ruleset runs on: **the wrapper had to exist before the deny could be honest**, and here shipping ODC's fix that morning is what made the blanket deny available by the afternoon.

### RULE R-ob-osascript-05 — window geometry, frontmost, bare activate/quit → `ctrl win` (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    if "osascript" not in cmd:
        return []
    import re, shlex

    def payloads(s, depth=0, out=None):
        out = [] if out is None else out
        try:
            ws = shlex.split(s)
        except ValueError:
            ws = s.split()
        for k, w in enumerate(ws):
            if (w == "osascript" or w.endswith("/osascript")) and (
                    k == 0 or ws[k - 1][-1:] in (";", "&", "|", "(")):
                out.append(" ".join(ws[k + 1:]))
            elif depth < 2 and " " in w and "osascript" in w:
                payloads(w, depth + 1, out)
        if depth == 0:
            for m in re.finditer(r"(?m)^[ \t]*(?:\S*/)?osascript(?=\s+(?:-|<<)|\s*$)", s):
                out.append(s[m.end():])
        return out

    WIN = ("`ctrl win list [app]` (every visible window: app, position, size, "
           "title, * = frontmost), `ctrl win front`, `ctrl win focus <app>`, "
           "`ctrl win move <app> X Y W H`, `ctrl win quit <app>`, "
           "`ctrl win close <app>`. Screen verbs: no bridge, no lease unless the "
           "app is a browser.")
    for p in payloads(cmd):
        # Window geometry and frontmost through System Events.
        if re.search(r'tell\s+application\s+"System Events"', p, re.I) and re.search(
                r"\b(position|size|bounds)\s+of\b|set\s+(position|size|bounds)\b|"
                r"\bfrontmost\b", p, re.I):
            return ["DENY: window geometry / frontmost via System Events -> " + WIN]
        # A tell whose whole body is activate or quit: the app is being brought
        # front or closed, nothing else. A longer script that activates and
        # then does app-specific work is NOT this rule's business.
        if (re.search(r"tell\s+application\s+(id\s+)?\"?[A-Za-z][\w .-]*\"?\s+(to\s+)?(activate|quit)\b", p, re.I)
                and not re.search(r"\b(set|get|do|make|click|keystroke|open|return|repeat|"
                                  r"delete|save|spotlight|reveal|select|close|count|exists|"
                                  r"display)\b", p, re.I)):
            return ["DENY: bare activate/quit via AppleScript -> " + WIN]
    return []
```

Added 2026-09-03 once `ctrl win` existed (ATT P0014). Catches: `set position/size/bounds`, reading `position/size/bounds of`, `frontmost` through System Events, and a tell whose entire body is `activate` or `quit`. Passes: AX clicks (`click button "OK"`), menu drilling, app-specific scripting that happens to `activate` first (Photos, Preview), `display notification`. Those have no wrapper, and the pebble's gate still holds for them.

# BRIEF

**Widening a rule here is gated on a wrapper existing, not on judgement.** Every clause above names what it redirects to, and the clauses that are absent are absent because their redirect target does not exist yet. If you are tempted to add `tell application "Photos"` or window geometry, check first that there is a command to name in the deny message — a deny that says "don't, and I can't tell you what instead" trains agents to route around the whole ruleset, which costs more than the calls it stops.

**Do not add a stated-reason escape.** It was considered and rejected on 2026-08-28 for a specific reason recorded above: the failure mode here is ignorance rather than haste, and a self-certified negative about an unread catalog is sincere exactly when it is wrong. That is the opposite of `R-ob-remote-ops-02`, where the escape is sound because the agent certifies something it actually knows.
