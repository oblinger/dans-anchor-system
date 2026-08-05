---
name: migrate
description: >
  Change an anchor in place — slug, traits, structure, naming (relocation is /move's job), organization.
  Use when the user says: "migrate this", "rename the slug", "change the type",
  "move this project", "restructure this", "convert to code project",
  "reorganize", "rename", "change".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Migrate
requires:: vault, anchor-cli, skill:rewire
subsystem:: [[DAS Anchor Design]] — the Anchor group's subsystem profile

Skill specification for the `/migrate` action — changes any aspect of an existing anchor (slug, location, traits, structure, naming) without losing files.

Change anything about an anchor. The user specifies what to change and the skill intelligently reorganizes.

## Safety Rule

**Never delete. Never lose.** Files may be moved to parallel locations where the user will find them, but nothing is deleted and nothing is moved to a location the user wouldn't expect.

## What can be migrated

| Change | What happens |
|--------|-------------|
| **slug** | Rename all {slug}-prefixed files, folders, wiki-links, config |
| **Location** | Move the anchor folder, update HookAnchor, breadcrumbs, symlinks |
| **Traits** | Add/remove traits — create trait-required files and folders |
| **Structure** | Reorganize folders, move files to standard locations |
| **Naming** | Rename files to match conventions (kebab-case, Title Case) |
| **Claude session** | Move `.claude/projects/` config to match new path |

## 🚨 AGENT MIGRATIONS — read this before moving a named-agent home 🚨

*Note: this skill CANNOT migrate the running agent itself. If the migrating agent = the target, see § Self-migration (bottom) — that flow requires a launcher script + session-file copy the running process cannot do to itself.*

Moving a named agent (Atticus, HERMES, EMBER, Ash, …) to a new cwd has **several critical steps**. **The session-file copy IS one of them and cannot be skipped**, but it is not the *only* step. A proper migration renames every surface: session data, persona file, anchor scaffolding, dispatch tables, and the vault-wide link graph.

Steps (do in this order):

1. **Move the target agent's session data.** This is the load-bearing step people forget — miss it and `claude --continue` at the new cwd silently starts a blank session (no warning, no fallback, agent history gone).
   ```bash
   SRC="$HOME/.claude/projects/-<old-encoded-cwd>"
   DST="$HOME/.claude/projects/-<new-encoded-cwd>"
   mkdir -p "$DST"
   cp -Rp "$SRC"/. "$DST/"      # entire project dir contents, preserving mtimes
   ```
   Keep the source as a backup (don't `mv`). `cp -Rp` preserves mtimes so `--continue` resumes the correct newest session.

2. **Move the persona file** (and any name-prefixed facets — CLAUDE.md, dated notes, etc.) via `anchor update <src> <dst> --root ~/ob/kmr --mkpath`. This moves the file AND rewrites every vault-wide `[[OldName Persona]]` → `[[NewName Persona]]` in one pass. If the migration is a rename (e.g. `Scout` → `EMBER`), all name-prefixed files under the identity home go through the same tool.

3. **Create the new anchor.** Write `.anchor` (slug + traits + description) and the anchor page `{NewName}.md` at the identity home.

4. **Optionally remove the old anchor.** If the old identity home is now empty of unique content, its `.anchor` + anchor page can be deleted. Optional; leaving the old scaffolding as a redirect stub is also fine.

5. **Update Atlas** via `/atlas update <NewName>` — reroute to the new slug.

6. **Update `Staff.md` dispatch** — Bench row, Universal row, etc. — to reference the new persona doc + anchor page.

7. **`ha --rescan`** so the new slug is discoverable to `⌘O`.

8. **Verify:**
   - `ha -p <NEW_SLUG>` resolves to `{NewName}.md`
   - `ls ~/.claude/projects/-<new-encoded-cwd>/*.jsonl | wc -l` matches source count
   - Newest `.jsonl` mtime in the new path is preserved
   - No orphan `[[OldName Persona]]` refs vault-wide (except historical / guarded surfaces)

9. Report ✓/✗ per step.

### On content-anchor moves (WHEN to move content vs identity)

The **content anchor** and the **identity home** are separate concerns:
- Identity home = `Staff/{Name}/` — persona, CLAUDE.md, name-prefixed identity docs.
- Content anchor = wherever the domain content lives (`Topic/BUY/`, `Topic/Startup/SCOUT/`, `SYS/`, etc.) — the actual asset tree the agent curates.

The **default agent migration is identity-only.** Content anchors and their contents stay put; only the persona + session move. This is what happened for HERMES (BUY content stayed at `Topic/BUY/`) and EMBER (SCOUT content stayed at `Topic/Startup/SCOUT/`).

If a full anchor relocation is genuinely wanted (rare — usually a restructure, not a rename), see `/move`.

### Self-migration — this skill can't do it

If the migrating agent = the target agent, the running process can't safely rewrite its own session file mid-conversation, and `exec claude --continue` from within the same session doesn't work as an in-place move. Use the launcher-script pattern instead — a bash script that runs from Terminal, copies the current session's `.jsonl` + `tool-results/` from `-<old-cwd>` to `-<new-cwd>`, then `cd new-cwd && exec claude --continue`. The prerequisite is that the source claude session be CLOSED first so its `.jsonl` is fully flushed.

Memory backing this rule: [[launch-migration-copies-jsonl]] — the incident that made this necessary.

## Runbook

1. Read `.anchor` file (or frontmatter) to get current state
2. Ask the user what to change (if not specified in the command)
3. Compute the diff: what files/links/config need to change
4. Show the plan to the user — wait for approval
5. Execute: use `anchor-mv` for file renames, update config, update HookAnchor
6. **If this is an agent migration with conversation continuity: apply the .jsonl copy sequence above BEFORE the `cd + exec claude --continue`.** Missing this step is the single most common failure mode — it looks like the migration didn't work; actually it worked but --continue found nothing to resume.
7. Verify: run `/rewire` to ensure everything is wired correctly
8. **Old-name sweep — mandatory final step.** After the mechanical rename lands, grep the vault for the old name/slug and read every hit; don't blind-replace. The anchor tools rewrite `[[wiki-links]]` and hook URLs, but stale references survive in `# H1` headings, YAML `description:`, prose paragraphs, code comments, sub-headers, and anywhere the name appears as bare text. Focus first on **the migrated identity's own folder** (`Staff/{Name}/` — persona doc, tracking indexes, any local README, the anchor page itself) — that's where stale self-references live and are almost always wrong: an H1 that says "SKA" on a page now called "Tink"; a persona that opens "I am LUM" after the slug moved to LUMEN. Legit refs stay: **domain references** (Hermes mentioning [[BUY]], Tink mentioning [[SKA]] as the curated content anchor), **historical logs** ("named 2026-07-24, previously called X"), and **cross-anchor pointers** to what the old name meant at the time. Judgment call is per-hit. Report `kept N, rewrote M` at the end so the sweep's calls are visible.
