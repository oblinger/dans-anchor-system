---
description: "`bridge` connects this Mac to another machine — control / sync / claude / agent."
---
# DAS Bridge
`bridge` connects this Mac to another machine. It is an umbrella over four kinds of bridging — two mechanisms (**control**, **sync**) and two goals built on them (**claude**, **agent**). This page is the command reference; the runbook and gotchas live in the [[skills/bridge/SKILL.md|SKILL]].

| -[[DAS Bridge]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [docs](hook://docs) → [DAS Bridge](hook://p/DAS%20Bridge)<br>: `bridge` connects this Mac to another machine — control / sync / claude / agent. |
| --- | --- |
| Related | [[skills/bridge/SKILL.md\|SKILL]],  [[Bridge Design\|Design]],  [[Bridge Testing\|Testing]],   |
| ... |  |

**The four kinds.** **control** (`bridge <host>`) — SSH + tmux + TCC inheritance, so the agent drives the remote as a local box with your Full Disk Access. **sync** (`bridge sync`) — mirror folder trees at identical absolute paths (Syncthing / NFS / rsync). **claude** (`bridge claude`) — provision the remote to run a Claude instance as an environment-twin (skills + CLAUDE.md + vault content; transcripts excluded). **agent** (`bridge agent`) — deploy a working Claude *agent* on the remote with a task brief, running end-to-end in tmux with a status doc + heartbeat.

## Commands

A bare hostname defaults to the **control** bridge; `sync` / `claude` / `agent` are explicit named intents.

| | Command | What it does |
|---|---|---|
| | **CONTROL** — *drive the remote as a local box (FDA-bearing)* | |
| | `bridge <host>` · `bridge mux <host>` | Open the SSH + tmux control bridge. Commands run in the remote pane inherit the launching Terminal's TCC (FDA / screen / GUI control). |
| | **SYNC** — *mirror folders at identical paths (one mode per host)* | |
| | `bridge sync` | Sync using every default from `config.yaml` (remote + folder + mode). |
| | `bridge sync <folder>` | Override the folder; default remote + mode. |
| | `bridge sync --remote <host>` | Override the remote; default folder + mode. |
| | `bridge sync-add <host> <folder>` | Add another folder under the host's existing mode. |
| | `bridge sync-status <host>` | Print mode, folders, freshness, errors. |
| | `bridge sync-teardown <host>` | Stop syncing this host (files preserved both sides). |
| | **CLAUDE** — *make the remote a Claude environment-twin* | |
| | `bridge claude [host]` | Provision `~/.claude` (skills + CLAUDE.md, minus transcripts) + shared memory + anchor-system config; composes `sync` for content. Then `bridge <host>` in and run `claude`. |
| | **AGENT** — *deploy a working Claude agent on the remote* | |
| | `bridge agent <host> --brief <path>` | Env-twin check → vault push-pull → ship brief → tmux launch → status doc + heartbeat. One `agent` session per host. |

### Options

**`bridge sync` modes** (one per host; switching = teardown + re-init): `syncthing` (live bidirectional convergence — default) · `nfs` (live mount, zero lag; private network only) · `rsync` (explicit push/pull batch — the hard-gate mode, no daemon).

**`bridge agent` flags:**

| Flag | Effect |
|---|---|
| `--brief <path>` | The task spec the agent reads on bootstrap (required). |
| `--restart` | Tear down the existing `agent` session and start fresh. |
| `--no-sync` | Skip the vault push-pull step (trusted-fresh vault). |
| `--no-layout` | Skip laptop-side window arrangement. |
| `--session <name>` | Override the session name (to run a concurrent second agent — rare). |
| `--role <path>` | Override the agent's cwd (default = invoker's cwd). |
| `--model <id>` | Override the model (default = invoker's model). |

## Config

Per-user paths + hosts live in `~/.config/bridge/config.yaml` (defaults + the `claude_environment` manifest) and `~/.config/bridge/hosts.yaml` (per-host sync state). The skill knows the *shape* of a bridge; config holds *this machine's* concrete values. The vault path is not duplicated here — it comes from `~/.config/anchor-system/global.yaml` `vault_root`.

## Critical rule

**Never drive remote work with one-shot `ssh <host> '<cmd>'`** — no state, no TCC inheritance, no observability. Use the persistent tmux control plane; a live Warden rule ([[R-ob-remote-ops]]-01) denies one-shot SSH at `tool:pre:Bash` and redirects here (bare attaches, `scp`/`rsync`, in-bridge `tmux` pass). And the one load-bearing setup choice: start the canonical remote mux session **from Terminal.app on the remote's own screen, never over SSH** — only a Terminal-launched server inherits Full Disk Access, window-server access, and GUI-app control.
