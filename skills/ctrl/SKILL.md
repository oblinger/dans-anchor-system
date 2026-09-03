---
name: ctrl
description: >
  Local environment control — persistent tmux sessions, Safari + Chrome browser automation, and
  screen see/drive. Four families: shell (trot/box/outbox), Safari (surf/search/jpage), Chrome CDP
  (cpage/cexec/cclick — drives your REAL Chrome, so it inherits your logged-in sessions), and screen
  (grab/click/type). Most subcommands are mapped to trigger words in CLAUDE.md.
tools: Bash
user_invocable: true
dependencies:
  - playwright>=1.40.0
---

# CTRL — Environment Control
requires:: none
subsystem:: [[DAS Utility Design]] — the Utility group's subsystem profile

Control the local macOS environment: persistent tmux shell sessions, browser automation against both Safari and your real Chrome, and direct screen control.

> **Directing the user on a live website?** [[AREC Interface directions]] binds you: never recite a web-UI path from memory — verify the URL by visiting it and confirming the expected content, or research / screen-read / drive instead.

**The one thing to know first:** the three browser families are *not* interchangeable, because they
hold **different cookie jars**. Safari (`jpage`) and Chrome (`cpage`) are separate logins, and the
sandboxed Playwright browser (`jjpage`) is logged into nothing. When a page is behind a login, the
question is not "which command extracts best" but **"which browser is signed in."**

## Shell — persistent tmux sessions

| ACTION | Description |
| ------ | ----------- |
| `ctrl trot "<cmd>"` | Run command in the persistent `trot` tmux session |
| `ctrl box "<cmd>"` | Alias for `trot` (backward compatible) |
| `ctrl outbox [N]` | Read last N lines from the trot/box session (default 50) |
| `ctrl box2..box9 "<cmd>"` | Additional independent sessions `box2`…`box9` |
| `ctrl outbox2..outbox9 [N]` | Read from the corresponding numbered session |
| `--in <session>` | Host the box as a tmux **window** in `<session>` — it appears as a tab |
| `--standalone` | Force a box of its own, ignoring `primary_session` |

Sessions persist across Claude Code sessions. **Always prefix `cd /path &&`** — the session's working
directory is not yours.

### Where a box lives

A box is a tmux **target**, not always a session of its own. By default it is created as a *window*
inside the session named by `primary_session` in the [[MY User Environment]] doc (`## tmux`), so it
shows up as a **tab in the MuxUX frame bound to that session** instead of floating as a separate
window. Read the key with `anchor-system env tmux primary_session`.

That default is **advisory**: the key is resolved, the session is checked for liveness, and a
standalone box is used when it is absent — which is what makes the key safe to carry in a
vault-synced file, since on a machine with no such session it simply does not resolve. An **explicit**
`--in` naming a dead session is a caller error and fails loudly instead; only the implicit default
falls back, and it says so on stderr.

Why it exists: a detached box session could only be seen by binding a whole MuxUX frame to it, and
that is how `trot` came to be misread as an agent frame and started capturing dictation clicks
(MUX T322/T323).

Two tmux behaviors this relies on, both verified rather than assumed:

- **`automatic-rename` is on by default**, so a hosted box's window would be renamed to whatever it
  is running and its `=host:=name` target would stop resolving mid-command. The name is pinned off
  at creation.
- **`display-message` on a window that does not exist does not fail** — it silently resolves to the
  host session's *current* window and exits 0. So the T586 occupant guard only ever probes a box
  that already exists; otherwise it reads whatever the user is looking at (in a MuxUX frame, almost
  always a `claude` pane) and refuses every first box. `send-keys` does **not** share that fallback.

A box also **declares itself a console** — `@muxux-kind console`, set on the window when hosted and on
the session when standalone. MuxUX otherwise classifies by sniffing `pane_current_command`, and
claude's argv0 is a bare version string, so any pane that has ever run claude is captured as an agent
and relaunched as one on the next restore. Declared-not-sniffed is the shape F160 already uses for
bridge sessions. The option is inert to anything that does not look for it.

Test: `tests/live/test-box-hosting.sh` — 18 checks, real tmux round trips, scratch sessions only.

## Safari — navigate and extract

| ACTION | Description |
| ------ | ----------- |
| `ctrl surf "<url>"` | Open URL in a new Safari tab |
| `ctrl navigate "<url>"` | Navigate the *current* Safari tab (`--new-tab` to override) |
| `ctrl new-tab` | Create an empty Safari tab |
| `ctrl tab "<url>"` | Open in a new tab without extracting, keeping the current tab active |
| `ctrl search "<query>"` | Google search — `--results N`, `--json`, `--new-tab` |
| `ctrl jsearch "<query>"` | Google search returning JSON — `--output <file>` |
| `ctrl jpage "<url>"` | Navigate + extract page content as JSON — `--output <file>` |
| `ctrl jgetlist` | Extract a repeating list structure from the current page — `--min-items N` |
| `ctrl jjpage <url\|->` | Extract via **Playwright** (sandboxed; `-` uses the current Safari URL) |

## Chrome CDP — drives your REAL Chrome

**This is the family that inherits your logged-in sessions.** Anything you are signed into in Chrome
is readable here with no token — this is how Sentry and Slack are reached (see [[SVT Sentry]],
[[SVT Slack]]).

| ACTION | Description |
| ------ | ----------- |
| `ctrl cpage <tab\|url>` | Extract page content — tab number (`1`, `2`, `-1`, `-2`) or a URL to open. `--yaml`, `--html`, `--output <file>`, `--font [N]` |
| `ctrl clist` | Extract list structure by finding the common font |
| `ctrl cexec "<js>" [tab]` | **Execute JavaScript in the page** and return its value |
| `ctrl cclick "<sel>" [tab]` | Click an element by CSS selector |
| `ctrl ctype "<sel>" "<text>" [tab]` | Type into an element (fires real keyboard events) |
| `ctrl cfill "<sel>" "<text>" [tab]` | Fill an input directly (faster than `ctype`) |
| `ctrl cwait "<sel>" [tab]` | Wait for an element — `--timeout <ms>` (default 10000) |
| `ctrl cupload <file>` | Upload a file to the page via CDP |
| `ctrl cnativefile <file>` | Drive the macOS native file-picker dialog — `--wait-time <sec>` |

### Gotchas that cost real time

- **`[tab]` defaults to the LAST tab.** Every `c*` command takes an optional trailing tab argument —
  a number *or a URL*. Omit it and your JS may run silently against an unrelated page and return
  plausible nonsense. **Pass the URL whenever the target matters.**
- **`cpage` is not enough for heavy SPAs.** On app-shell sites (Slack) it captures a connection or
  loading overlay rather than content. Use `cexec` against the live DOM instead.
- **Virtualized lists only exist while scrolled into view** — query once and take what you need; a
  repeat query minutes later can return entirely different nodes.
- **Fetching authenticated binaries** (images, downloads) — `curl` cannot, because the cookie lives
  in Chrome. Do it in-page and hand back base64:
  ```
  ctrl cexec 'fetch(URL,{credentials:"include"}).then(r=>r.blob()).then(b=>new Promise(res=>{var fr=new FileReader();fr.onload=()=>res(fr.result.split(",")[1]);fr.readAsDataURL(b)}))' "<tab-url>"
  ```
  then base64-decode locally. Verified to ~800 KB in one return.

## Screen — see and drive the Mac

| ACTION | Description |
| ------ | ----------- |
| `ctrl screen grab [OUT] [-R x,y,w,h]` | Screenshot full screen or region (default `/tmp/screen.png`); `--display N\|all` |
| `ctrl screen size` | Report capture px / logical pts / scale |
| `ctrl screen click X Y` | Click at logical points — `--px`, `--right`, `--double` |
| `ctrl screen move X Y` | Move the cursor — `--px` |
| `ctrl screen type "<text>"` | Type a string |
| `ctrl screen key <KEYSPEC>` | Press a key/combo (`return`, `cmd+j`, `esc`) |

**Screen capture is a last resort, not a fetch.** It records whatever else is on the display —
banking tabs, mail, private documents — and driving it steals focus from the user. Reach for a
browser family first; use `screen` only when nothing else can see the target.

## Other

| ACTION | Description |
| ------ | ----------- |
| `ctrl edit <file>` | Open a file in Sublime Text |
| `ctrl x excal <file>` | Load a `.excalidraw` file into Excalidraw |
| `ctrl x excalsave <file>` | Save the current Excalidraw drawing to a file |

## The interactive gate (TINK F640)

On Dan's active machine (`interactive_hosts` in `~/.config/ctrl/config.yaml`) a **data verb** —
`surf`, `search`, `cpage`, `jpage`, `jgetlist`, `tab`, and the rest of the browser family — refuses
by default and prints the bridge form for Dexter. Screen verbs (`box`, `outbox`, `own`, `release`,
`lease`, `edit`, `screen`, `x`) always run. Hosts not listed (Dexter) are untouched.

| Form | What happens |
|---|---|
| `ctrl cpage <url>` | Refused at once, exit 2, bridge form on stderr. |
| `ctrl --bridge cpage <url> …` | Prints the exact `bridge tmux` + `send-keys` + `capture-pane` (+ `scp` for `--output`) lines that run the same call on Dexter; exit 0. The only way to get the form. |
| `ctrl --interactive cpage <url> …` | A disinterested judge (`claude -p`, haiku) reads the session's last 3 user messages and last 10 tool calls — never the agent's own reasoning — and answers *is this agent interacting with the user, or gathering data?* Pass → runs. Fail → exit 2, message names the evidence and points at `--bridge`. |

Interactive means Dan is waiting on this specific result now. Crawls, sweeps, loops, and research he said he
would look at later are data gathering and belong on Dexter. Every judgement posts one line to `ob_check`
topic `ctrl.judge`; records sit in `~/.config/ctrl/judge/`. Test: `tests/live/test-f640-judge.py`.

## Trigger Words

These trigger words in CLAUDE.md map to ctrl subcommands:

| Trigger | Command |
|---------|---------|
| **trot** `<cmd>` | `ctrl trot "<cmd>"` |
| **outbox** | `ctrl outbox` |
| **surf** `<url>` | `ctrl surf "<url>"` |

## Usage

The script is at `~/.claude/skills/ctrl/ctrl.py`; `ctrl` in `~/bin` is a symlink to it.
`ctrl --help` is authoritative — this page should match it.

```bash
ctrl box "cd /path && make build"          # persistent session
ctrl outbox 100                            # last 100 lines
ctrl surf "https://example.com"            # Safari, new tab
ctrl search --results 5 "query"            # parsed Google results
ctrl cpage "https://example.com" --yaml    # real-Chrome extraction
ctrl cexec 'document.title' "https://example.com"   # JS, explicit tab
ctrl screen grab /tmp/shot.png             # screenshot
```

## Notes

- **When a WebFetch fails**, route by wall type per CLAUDE.md: a *bot wall* (403/999/Cloudflare) →
  `ctrl cpage`; a *login wall* on a session-gated site → whichever browser holds the session, which
  is usually Chrome (`cpage`/`cexec`) and sometimes Safari (`jpage`).
- Session-gated access **is** the credential, and it dies when that profile logs out. If an agent
  needs a site regularly, a real API token is the durable answer.
- `ctrl search --results N` parses Google results into structured data.
- **Doc drift is the failure mode here.** This file previously listed a `ctrl shell` subcommand that
  does not exist, and omitted the entire Chrome CDP family (9 commands) plus `screen`, `box2`–`box9`,
  `x`, and `edit` — 24 subcommands, 7 documented. When adding a subcommand to `ctrl.py`, add its row
  here in the same change.
