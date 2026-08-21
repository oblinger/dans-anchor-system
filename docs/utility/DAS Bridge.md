---
description: "`bridge` connects this Mac to another machine — control (SSH + tmux + TCC inheritance), sync (folder mirroring at identical paths), claude (environment-twin), agent (a working Claude agent deployed on the remote)."
---

| -[[DAS Bridge]]- | : `bridge` connects this Mac to another machine — tmux / install / doctor / sync / agent.<br>→ [[DAS]] → [docs](hook://docs) → [DAS Bridge](hook://p/DAS%20Bridge)  |
| --- | --- |
| Related | [[skills/bridge/SKILL.md\|SKILL]],  [[DAS Bridge Design\|Design]],  [[DAS Bridge Testing\|Testing]],   |
| ... |  |

# DAS Bridge
`bridge` connects this Mac to another machine. Every operation is a verb of **one packaged dispatcher** — `~/.claude/skills/bridge/bridge` — invoked by full path (it rides the skills repo, so it exists on any provisioned machine; no `~/bin`, no PATH assumptions, nothing user-specific). Agents never improvise raw ssh. This page is the solution overview + command reference; the runbook and gotchas live in the [[skills/bridge/SKILL.md|SKILL]]; design rationale in SKA F279.

## The solution in one picture

**`bridge tmux <host>`** stands up a symmetric pair of tmux sessions, both named `bridge-<host>`:

- **Remote side** — the session runs in a Terminal window **on the remote machine's own screen**, launched there (never over ssh) so its panes inherit the Terminal's TCC grants: Full Disk Access, Screen Recording, Accessibility. That window is simultaneously the **viewer**: the user glances at the remote screen and sees every command the agent executes and every result, live. `ctrl` and the rest of the environment work there because `bridge install` put them there.
- **Local side** — a tmux session `bridge-<host>` ssh-attached to the remote one. The agent drives with `tmux send-keys -t bridge-<host> "<cmd>" Enter` and reads with `tmux capture-pane -t bridge-<host> -p`.

**`bridge install <host>`** is the idempotent converge — "make it so": provisions the environment (skills, CLAUDE.md, settings, `ctrl`), wires the skills repo, makes Syncthing **launchd-durable** (survives reboots), and writes a provision stamp. Run it once to set up; run it again any time to reconverge. `refresh` is an alias.

**A sub-second preflight** runs automatically in front of every verb — config sanity, stamp age, session liveness locally (~10 ms), plus one remote ping only when a warm SSH ControlMaster socket exists (~100 ms; the dispatcher keeps sockets warm with `ControlPersist`). On failure it names the fix (`run: bridge install <host>`). **`bridge doctor <host>`** is the slow, careful, **read-only** backup — the full diagnostic table. Doctor never mutates; install never merely reports. That read/write split is the interface.

## Commands

| Command | What it does |
| --- | --- |
| **CONTROL** | — *drive the remote as a local box, visibly* |
| `bridge tmux <host>` | The flagship connect (above). `--session S` overrides the `bridge-<host>` name; `--viewer` only re-throws the viewer window; `--force` restarts a degraded server even with busy panes (default: refuse). Renamed from `bridge mux` — tmux is what's being bridged. |
| **CONVERGE** | — *make the twin right, idempotently* |
| `bridge install <host>` | Env files (claude-provision: `~/.claude` minus transcripts, `~/.config/anchor-system`, `bin` utilities like `ctrl`) + skills-repo wiring + launchd-durable Syncthing + provision stamp. Alias: `refresh`. |
| `bridge skills <host>` | Just the skills wiring: symlink the remote's `~/.claude/skills` into the repo named by config `skills_repo` (vault-synced copy preferred; clone from `url` only on non-twin machines — never alongside a sync-covered path). |
| **DIAGNOSE** | — *read-only, never mutates* |
| `bridge doctor <host>` | Full table: reach / Aqua launch-context / TCC caps / sync daemon / launchd / stamp / ctrl / local session. Each FAIL names its fix. |
| **SYNC** | — *mirror folders at identical paths* |
| `bridge sync <host>` | Syncthing status/revive for the host's recorded folders. Share creation and teardown stay in `syncthing-helper.py` (move-aside confirmation gate). |
| **AGENT** | — *deploy a working Claude agent on the remote* |
| `bridge agent <host> --brief <path>` | Env-twin check → vault push-pull → ship brief → tmux launch → status doc + heartbeat. One `agent` session per host. (F007; flags in the SKILL.) |

## Config

Per-user values live in `~/.config/bridge/config.yaml` (defaults, the `claude_environment` manifest, `skills_repo`) and `~/.config/bridge/hosts.yaml` (per-host sync state). The dispatcher knows the *shape* of a bridge; config holds *this machine's* concrete values — bridge stays generic, and only the config names user-specific things like `dans-anchor-system`. The vault path comes from `~/.config/anchor-system/global.yaml` `vault_root`, never duplicated here.

## Critical rules

- **Never drive remote work with one-shot `ssh <host> '<cmd>'`** — no state, no TCC inheritance, no observability. A live Warden rule ([[R-ob-remote-ops]]-01) denies it at `tool:pre:Bash` and redirects here.
- **The one load-bearing setup choice:** the remote tmux server must be launched **from Terminal in the remote's own Aqua session, never over SSH** — only that server inherits FDA, window-server access, and GUI control. `bridge tmux` automates exactly this (a `.command` opened into the Aqua session) and verifies it; the TCC grants themselves (Settings → Privacy & Security toggles for Terminal) are a one-time user action per machine that the tool walks you to.
