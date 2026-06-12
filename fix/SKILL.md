---
name: fix
description: >
  Fix common environment problems — permissions, auth, session config, workarounds.
  Use when the user says: "fix permissions", "fix auth", "reauth google",
  "fix the session", "clean up", "something's broken", "fix claude".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Fix

User-invocable skill that runs a self-contained recovery procedure for a known runtime breakage (auth, permissions, session config, macOS quirks).

Fix common environment problems. Each fix is a self-contained procedure in this folder.

## When NOT to use this skill

`/fix` is for **runtime breakage** — broken auth, dead session, can't reach the daemon, app misbehaving, settings drift that broke something that used to work. For Claude Code config and permissions specifically, prefer the built-ins:

| Use built-in instead | When |
|---|---|
| `update-config` | Modify `settings.json` / `settings.local.json` — add permissions, set env vars, configure hooks, change theme/model. Not "broken" — just "configure." |
| `fewer-permission-prompts` | Drowning in permission prompts; want to scan recent transcripts and add a curated allowlist. |
| `keybindings-help` | Rebind keys / add chord shortcuts / modify `~/.claude/keybindings.json`. |

If something *was* working and now isn't, that's `/fix`. If you're configuring something fresh or tuning behavior, reach for the matching built-in.

## Runbook

1. Determine which fix to run (from argument or user description)
2. Read the fix file from this folder
3. Execute the procedure
4. Report the result — if user action is required, say so loudly

## Fixes

| Usage | File | Description |
|-------|------|-------------|
| | **Claude Code** | |
| `/fix claude permissions` | [[fix-claude-permissions]] | Clean settings.local.json files that override global bypass |
| `/fix claude session` | [[fix-claude-session]] | Move project config after an anchor moves |
| | **Google / Auth** | |
| `/fix gauth` | [[fix-google-reauth]] | Re-authorize Google API (token expires every 7 days) |
| | **Obsidian** | |
| `/fix obsidian-comments` | [[fix-obsidian-python-comments]] | Python `#` in code blocks breaks Obsidian folding |
| | **macOS** | |
| `/fix mac sudo` | [[fix-mac-sudo-nopassword]] | Configure sudo without password for admin group |
| `/fix mac unsigned` | [[fix-mac-unsigned-apps]] | Open apps blocked by Gatekeeper ("unidentified developer") |
| `/fix mac key-repeat` | [[fix-mac-key-repeat]] | Fast key repeat + disable press-and-hold for accents |
| `/fix mac dotfiles` | [[fix-mac-finder-dotfiles]] | Show/hide hidden files in Finder |
| `/fix mac mail-archive` | [[fix-mac-mail-delete-to-archive]] | Make Delete key archive in Apple Mail instead of trash |
