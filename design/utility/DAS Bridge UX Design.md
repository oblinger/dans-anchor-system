---
description: "the command surface that realizes these requirements"
---

# DAS Bridge UX Design

| -[[DAS Bridge UX Design]]- | : user-facing command surface<br>→ [[DAS]] → [design](hook://design) → [DAS Bridge UX Design](hook://p/DAS%20Bridge%20UX%20Design)  |
| --- | --- |
| [[DAS Bridge PRD\|PRD]]  | the requirements these verbs satisfy |
| [[DAS Bridge Testing\|Testing]]  | how each verb is exercised |
| [[bridge\|SKILL.md]]  | the live runbook |
| ... |  |

The skill is **slash-only** (`/bridge …`) — "bridge" is too common a word to be a spoken DMUX trigger. The verb surface groups into the three kinds of bridging. A bare `/bridge <host>` defaults to the **control** bridge (the most-common interactive case); `sync` and `claude` are explicit named intents.

## Control bridge

| Verb | Arguments | What it does | Output |
|---|---|---|---|
| `bridge <host>` | hostname | Default — open/attach the control (mux) session on `<host>`. Auto-resumes any configured sync for the host. | tmux pane attached via `ctrl box2`; warns if sync daemon down |
| `bridge mux <host>` | hostname | Explicit alias for the control bridge. | same as above |

## Sync bridge

| Verb | Arguments | What it does | Output / gate |
|---|---|---|---|
| `bridge sync` | — | Set up / resume file sync using all defaults from `config.yaml`. | prompts once for any missing default |
| `bridge sync <folder>` | folder | Override the synced folder; default remote + mode. | — |
| `bridge sync --remote <host>` | host | Override the remote; default folder + mode. | — |
| `bridge sync-add <host> <folder>` | host, folder | Add another folder under the host's existing mode. | — |
| `bridge sync-status <host>` | host | Show mode, folders, freshness, error count. | per-folder state JSON |
| `bridge sync-teardown <host>` | host | Stop syncing the host (files preserved both sides). | confirm; offers to remove the move-aside dir |

**Move-aside gate** (on first seed when the remote has prior content): warn + confirm before moving `<folder>` → `<folder>.old.<date>/`. **Direction gate:** seeds one-way (Send-Only → Receive-Only); flipping to two-way is an explicit `flip-bidirectional` step, never automatic.

## Claude bridge

| Verb | Arguments | What it does | Output |
|---|---|---|---|
| `bridge claude plan <host>` | host | Dry-run — report sync coverage + the `~/.claude` include/exclude that would apply. | plan JSON |
| `bridge claude apply <host>` | host `[--bridge-ip IP]` | Provision the twin — rsync `~/.claude` (include − exclude) to the remote, over the fast link if given. | per-item results |
| `bridge claude verify <host>` | host | Confirm skills + `CLAUDE.md` landed, `projects/` did NOT. | `twin_ready: true/false` |

## Configuration surface

The per-user recipe lives in `~/.config/bridge/config.yaml` (not in the skill). The user edits it directly or answers first-run prompts:

```yaml
defaults: { remote: <host>, sync_mode: syncthing }
claude_environment:
  sync: [ <folders to mirror> ]
  claude_home:
    include: [ skills, CLAUDE.md, settings.json, commands ]
    exclude: [ projects, todos, worktrees, shell-snapshots ]
```

`~/.config/bridge/hosts.yaml` holds per-host sync state (device IDs, folders, move-aside path) — written by the skill, not hand-edited.

## Output & voice conventions

- **Confirmation prompts** are explicit `[y/N]` with the exact destructive effect named (which path moves where).
- **Status output** is structured (JSON from the helpers) when machine-readable detail matters; chat summaries are one-to-three lines.
- **Verify verbs return a boolean verdict** (`twin_ready`, folder `idle`/`needBytes:0`) so the agent can gate on them.
- **Fast-link awareness:** when a Thunderbolt/USB-C bridge is present, operations prefer the `169.254.x.x` link automatically; the skill surfaces which address is in use.

## Helpers behind the verbs

| Helper | Backs |
|---|---|
| `~/.claude/skills/bridge/syncthing-helper.py` | all `bridge sync*` verbs (pair / share / wait-converge / flip / record / status / teardown / defaults) |
| `~/.claude/skills/bridge/claude-provision.py` | all `bridge claude *` verbs (plan / apply / verify) |
| `ctrl box2` / `ctrl outbox2` | the control bridge attach + readback |
