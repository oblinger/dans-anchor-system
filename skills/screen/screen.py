#!/usr/bin/env python3
"""screen — see and drive a Mac's screen (grab + click + type + key).

Turns the agent from an observer into an operator on GUI surfaces. Works
on the LOCAL Mac or a REMOTE Mac over the bridge — but in both cases it
must run inside a GUI/Aqua login session, i.e. a **Terminal-launched tmux
pane**, never a bare SSH session. Direct SSH has no window-server access
("could not create image from display") and cannot post input events.

Remote usage pattern (from the driving machine):
    ssh host '/usr/local/bin/tmux new-window -t work -d -n cap \
        "~/.claude/skills/screen/screen.py grab /tmp/s.png"'
    scp host:/tmp/s.png /tmp/s.png         # then Read /tmp/s.png

Subcommands:
    grab [OUT] [-R x,y,w,h]   screenshot full screen (or region) to OUT (default /tmp/screen.png)
    size                      report capture pixels, logical points, and scale factor
    click X Y [--px] [--right] [--double]
                              click at LOGICAL points; --px = interpret X Y as capture pixels (auto /scale)
    move X Y [--px]           move the cursor
    type TEXT                 type a string
    key KEYSPEC               press a key / combo (e.g. return, cmd+j, esc)

Coordinate model: screencapture returns retina PIXELS (scale 2 on most
Macs). Clicks use LOGICAL POINTS = pixels / scale. Read a coordinate off a
screencap (pixel space), then either divide by `screen size`'s scale, or
pass it with --px and let this script divide. Backends, in preference
order: cliclick (best — install the prebuilt binary), then osascript /
System Events (built-in fallback, less reliable for some apps).
"""

import argparse
import shutil
import subprocess
import sys


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def logical_size():
    """Main-screen logical size in points via Finder desktop bounds."""
    r = _run(["osascript", "-e",
              'tell application "Finder" to get bounds of window of desktop'])
    if r.returncode == 0 and r.stdout.strip():
        # "0, 0, 2048, 1280"
        parts = [p.strip() for p in r.stdout.strip().split(",")]
        if len(parts) == 4:
            return int(parts[2]), int(parts[3])
    return None


def capture_size(path="/tmp/.screen_probe.png"):
    """Full-screen capture pixel dimensions (drives scale detection)."""
    _run(["screencapture", "-x", path])
    r = _run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path])
    w = h = None
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith("pixelWidth:"):
            w = int(line.split(":")[1])
        elif line.startswith("pixelHeight:"):
            h = int(line.split(":")[1])
    return w, h


def scale_factor():
    cw, _ = capture_size()
    log = logical_size()
    if cw and log and log[0]:
        return round(cw / log[0], 3)
    return 2.0  # sane retina default


def cmd_size(args):
    cw, ch = capture_size()
    log = logical_size()
    sf = round(cw / log[0], 3) if (cw and log and log[0]) else None
    print(f"capture_px:  {cw} x {ch}")
    print(f"logical_pts: {log[0] if log else '?'} x {log[1] if log else '?'}")
    print(f"scale:       {sf}")
    print("note: click uses logical points = capture px / scale")


def cmd_grab(args):
    out = args.out or "/tmp/screen.png"
    cmd = ["screencapture", "-x"]
    if args.region:
        cmd += ["-R", args.region]
    cmd.append(out)
    r = _run(cmd)
    if r.returncode != 0:
        print(f"grab FAILED: {r.stderr.strip() or 'unknown'}", file=sys.stderr)
        print("hint: are you inside a Terminal-launched tmux session? "
              "direct SSH cannot capture the display.", file=sys.stderr)
        sys.exit(1)
    print(out)


def _to_logical(x, y, px):
    if not px:
        return x, y
    sf = scale_factor()
    return round(x / sf), round(y / sf)


def cmd_click(args):
    x, y = _to_logical(args.x, args.y, args.px)
    if shutil.which("cliclick"):
        verb = "rc" if args.right else ("dc" if args.double else "c")
        r = _run(["cliclick", f"{verb}:{x},{y}"])
        if r.returncode == 0:
            print(f"click {verb} {x},{y} (cliclick)")
            return
        print(f"cliclick failed: {r.stderr.strip()}", file=sys.stderr)
    # osascript fallback (System Events click is left-only; right-click needs cliclick)
    script = f'tell application "System Events" to click at {{{x}, {y}}}'
    if args.double:
        script = (f'tell application "System Events"\n'
                  f'  click at {{{x}, {y}}}\n  click at {{{x}, {y}}}\nend tell')
    r = _run(["osascript", "-e", script])
    if r.returncode != 0:
        print(f"click FAILED (osascript): {r.stderr.strip()}", file=sys.stderr)
        print("hint: install cliclick for reliable clicking; ensure the "
              "Terminal/tmux app has Accessibility permission.", file=sys.stderr)
        sys.exit(1)
    print(f"click {x},{y} (osascript)")


def cmd_move(args):
    x, y = _to_logical(args.x, args.y, args.px)
    if shutil.which("cliclick"):
        _run(["cliclick", f"m:{x},{y}"])
        print(f"move {x},{y} (cliclick)")
        return
    print("move requires cliclick (osascript has no cursor-move primitive)",
          file=sys.stderr)
    sys.exit(1)


def cmd_type(args):
    if shutil.which("cliclick"):
        r = _run(["cliclick", f"t:{args.text}"])
        if r.returncode == 0:
            print("typed (cliclick)")
            return
    esc = args.text.replace("\\", "\\\\").replace('"', '\\"')
    r = _run(["osascript", "-e",
              f'tell application "System Events" to keystroke "{esc}"'])
    if r.returncode != 0:
        print(f"type FAILED: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    print("typed (osascript)")


KEY_CODES = {  # osascript key codes for non-printable keys
    "return": 36, "enter": 36, "tab": 48, "space": 49, "esc": 53,
    "escape": 53, "delete": 51, "left": 123, "right": 124, "down": 125,
    "up": 126,
}


def cmd_key(args):
    spec = args.keyspec.lower()
    if shutil.which("cliclick"):
        # cliclick keypresses: kp:return, and modifier holds via kd/ku
        if "+" not in spec:
            r = _run(["cliclick", f"kp:{spec}"])
            if r.returncode == 0:
                print(f"key {spec} (cliclick)")
                return
    # osascript path (handles cmd+j etc.)
    if "+" in spec:
        *mods, base = spec.split("+")
        using = " down, ".join(f"{m} down" for m in
                               [{"cmd": "command", "opt": "option",
                                 "alt": "option", "ctrl": "control",
                                 "shift": "shift"}.get(m, m) for m in mods])
        if base in KEY_CODES:
            script = f'tell application "System Events" to key code {KEY_CODES[base]} using {{{using}}}'
        else:
            script = f'tell application "System Events" to keystroke "{base}" using {{{using}}}'
    elif spec in KEY_CODES:
        script = f'tell application "System Events" to key code {KEY_CODES[spec]}'
    else:
        script = f'tell application "System Events" to keystroke "{spec}"'
    r = _run(["osascript", "-e", script])
    if r.returncode != 0:
        print(f"key FAILED: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    print(f"key {spec} (osascript)")


def main():
    p = argparse.ArgumentParser(prog="screen", description="see and drive a Mac's screen")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("grab", help="screenshot full screen or region")
    g.add_argument("out", nargs="?", default=None)
    g.add_argument("-R", "--region", help="x,y,w,h", default=None)
    g.set_defaults(func=cmd_grab)

    s = sub.add_parser("size", help="report capture px / logical pts / scale")
    s.set_defaults(func=cmd_size)

    c = sub.add_parser("click", help="click at logical points")
    c.add_argument("x", type=int)
    c.add_argument("y", type=int)
    c.add_argument("--px", action="store_true", help="X Y are capture pixels (auto /scale)")
    c.add_argument("--right", action="store_true")
    c.add_argument("--double", action="store_true")
    c.set_defaults(func=cmd_click)

    m = sub.add_parser("move", help="move cursor")
    m.add_argument("x", type=int)
    m.add_argument("y", type=int)
    m.add_argument("--px", action="store_true")
    m.set_defaults(func=cmd_move)

    t = sub.add_parser("type", help="type a string")
    t.add_argument("text")
    t.set_defaults(func=cmd_type)

    k = sub.add_parser("key", help="press a key / combo (return, cmd+j, esc)")
    k.add_argument("keyspec")
    k.set_defaults(func=cmd_key)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
