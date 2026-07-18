---
description: "`bridge` connects this Mac to another machine — control (SSH + tmux + TCC inheritance), sync (folder mirroring at identical paths), claude (environment-twin), agent (a working Claude agent deployed on the remote)."
---
# DAS Bridge
`bridge` connects this Mac to another machine — the umbrella over four kinds of bridging: **control** (SSH + tmux + TCC inheritance, so the agent drives the remote as a local box with your Full Disk Access), **sync** (file mirroring — Syncthing / NFS / rsync — so folders appear at identical absolute paths on both machines), **claude** (a composite goal: provision the remote to run a Claude instance as an environment-twin — skills + CLAUDE.md + vault content, transcripts deliberately excluded), and **agent** (deploy a working Claude agent on the remote with a task brief, running end-to-end in tmux with a status doc and heartbeat).

| -[[DAS Bridge]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [docs](hook://docs) → [DAS Bridge](hook://p/DAS%20Bridge)<br>: `bridge` connects this Mac to another machine — control / sync / claude / agent. |
| --- | --- |
| Related | [[skills/bridge/SKILL.md\|SKILL]],  [[Bridge Design\|Design]],  [[Bridge Testing\|Testing]],   |
| ... |  |

`bridge <host>` with a bare hostname defaults to the **control** bridge (the common interactive case); `sync` / `claude` / `agent` are explicit named intents. Two contracts run through everything: **same-relative-path** (the remote path always matches the local path absolutely, preserving wiki-links and path-keyed tooling) and **per-user recipe in config** (the skill knows the *shape* of a bridge; `~/.config/bridge/config.yaml` holds this user's concrete hosts + paths).

Critical rule: **never drive remote work with one-shot `ssh <host> '<cmd>'`** — it has no state, no TCC inheritance, and no observability. Use the skill's persistent tmux control plane instead; a live Warden rule ([[R-ob-remote-ops]]-01) denies one-shot SSH at `tool:pre:Bash` and redirects here (bare attaches, `scp`/`rsync`, and in-bridge `tmux` commands pass). The single load-bearing setup choice: start the canonical remote mux session **from Terminal.app on the remote's own screen, never over SSH** — a Terminal-launched server inherits Full Disk Access, window-server access, and GUI-app control; an SSH-launched one has none of that.
