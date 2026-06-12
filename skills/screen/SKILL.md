---
name: screen
description: See and drive a Mac's screen — screen grab plus click / move / type / key — on the local machine or a remote one over the bridge. Lets the agent visually verify GUI state and operate GUI surfaces (dismiss dialogs, click buttons, grant-flow assists) instead of routing every interaction through the user. Backed by screen.py; works only inside a GUI/Aqua login session (a Terminal-launched tmux pane), never bare SSH. Clicking needs the Terminal/tmux app to hold Accessibility; cliclick is the preferred backend with an osascript fallback.
---

# Screen

The agent can both **see** a Mac's screen and **act** on it — capture the display, then click, move, type, and press keys. This closes the GUI verification-and-control loop: instead of asking the user to dismiss a dialog or click Continue, the agent does it. Pairs with the [[devops]] heartbeat discipline (screencap is the visual half of the watcher loop) and the [[bridge]] control plane (it carries the capability to a remote Mac for free).

Helper: `~/.claude/skills/screen/screen.py` (bridged to remotes via `bridge claude`).

## The one hard constraint — GUI-session context

Both seeing and acting require a process inside the user's **GUI/Aqua login session**. A bare SSH session is NOT in it:

- `ssh host screencapture …` → *"could not create image from display"* (no window-server access).
- SSH-posted click/key events → silently dropped.

The fix is the same as the control bridge's TCC trick: run inside a **Terminal-launched tmux session**. That session inherits the GUI context (and the launching Terminal's TCC). So from a driving machine:

    ssh host '/usr/local/bin/tmux new-window -t work -d -n cap \
        "~/.claude/skills/screen/screen.py grab /tmp/s.png"'
    scp host:/tmp/s.png /tmp/s.png        # then Read /tmp/s.png

Locally, just run `screen.py …` from a Terminal/tmux (not a non-GUI context).

## Permissions

- **Grab** needs **Screen Recording** granted to the Terminal app that launched the tmux server. (If a capture comes back small and near-black, that grant is missing.)
- **Click / move / type / key** need **Accessibility** granted to that same Terminal app (it's the process posting the events). Without it, events are dropped.
- These are one-time grants per machine, on the Terminal app — System Settings → Privacy & Security → Screen Recording / Accessibility.

## Subcommands

    screen.py grab [OUT] [-R x,y,w,h]   screenshot full screen or a region → OUT (default /tmp/screen.png)
    screen.py size                      report capture pixels, logical points, scale factor
    screen.py click X Y [--px] [--right] [--double]
    screen.py move X Y [--px]
    screen.py type "TEXT"
    screen.py key KEYSPEC               return | esc | tab | cmd+j | shift+tab | ...

## Coordinates — the scale gotcha

`screencapture` returns **retina pixels** (scale 2 on most Macs: a 2048×1280 display captures as 4096×2560). Clicks use **logical points** = pixels ÷ scale.

Workflow to click what you see:
1. `screen.py grab` → Read the PNG. Estimate the target in capture-pixel space (or as a fraction of the image).
2. Either run `screen.py size` to get the scale and divide yourself, OR pass the pixel coordinate with `--px` and let the script divide: `screen.py click --px 2000 1100`.
3. Verify with a follow-up `grab` — clicking blind is risky; always re-capture to confirm the effect (this is the screen analog of the verify-after-fix discipline).

For precise targeting, prefer fraction-of-screen reasoning over guessing absolute pixels; re-grab and nudge if the first click misses.

## Backends

- **cliclick** (preferred) — single binary, reliable for all apps: `cliclick c:x,y`. Install the **prebuilt binary** (drop in ~/bin) to avoid the Intel Xcode-license wall that `brew install cliclick` hits. The script auto-detects it.
- **osascript / System Events** (fallback, built-in) — `click at {x,y}`, `keystroke`, `key code`. Works without installs but is less reliable for some apps and can't move the cursor or right-click cleanly. The script falls back to this when cliclick is absent.

## When to use vs not

- **Use** for: GUI state verification (did the window appear? does it look right?), dismissing/advancing dialogs, assisting permission flows, driving subjective/visual test steps, any "I can see it, I should be able to click it" moment.
- **Don't use** for things with a non-GUI path — prefer a CLI, file write, or IPC call over synthesizing clicks when one exists (synthetic input is the last resort, not the first).
- **TCC prompts themselves** still often need the human (first-launch Accessibility for a freshly-installed app may not even appear without a Finder double-click). Use `screen` to *assist and verify*, not to assume every permission can be self-granted.

## Related

- [[devops]] — heartbeat + watcher discipline; screen grab is the visual half of observation.
- [[bridge]] — carries screen.py to a remote Mac and provides the GUI-session tmux context.
- [[io]] — sibling IO capabilities.

---

_v1 2026-06-12 — authored mid-drive (Muxbridge bring-up) so the agent could finish GUI verification without routing every click through the user. Grab is battle-tested; click/type via cliclick-or-osascript is new and will be hardened with use (grid-overlay targeting + right-click are planned)._
