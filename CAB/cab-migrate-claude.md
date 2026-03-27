# Migrate Claude — Move a Claude Code Session to a New Path

When an anchor folder moves, the Claude Code session config must move too. Claude Code stores per-project config at `~/.claude/projects/{encoded-path}/` where the path is encoded by replacing `/` with `-` and dropping the leading `-`.

## Steps

### 1. Determine old and new paths

- **Old path**: the original absolute path of the anchor folder
- **New path**: the current absolute path of the anchor folder

### 2. Encode both paths

Replace `/` with `-`, drop the leading `-`:
```
/Users/oblinger/ob/kmr/prj/Forum → -Users-oblinger-ob-kmr-prj-Forum
```

### 3. Check if old project config exists

```bash
ls ~/.claude/projects/{old-encoded}/
```

If it exists, it may contain:
- `settings.local.json` — user-granted permissions
- `CLAUDE.md` — project-specific instructions (separate from the anchor's CLAUDE.md)
- `memory/` — project memory files
- `memory/MEMORY.md` — memory index

### 4. Move the project config

```bash
mv ~/.claude/projects/{old-encoded} ~/.claude/projects/{new-encoded}
```

If the old config doesn't exist, create the new folder:
```bash
mkdir -p ~/.claude/projects/{new-encoded}
```

### 5. Update path references inside the config

Check all files in the project config for references to the old path and update them:
- `settings.local.json` — may have path-specific permissions
- `memory/*.md` — may reference old file locations

### 6. Verify CLAUDE.md exists at new anchor root

The anchor's `CLAUDE.md` must exist at the new path. If it was lost in the move, recreate it with the standard pilot role header.

### 7. Test

```bash
cd {new-path} && claude
```

Claude should start and load the project config.

## Common Pitfalls

- **Forgetting the project config folder** — the CLAUDE.md at the anchor root is NOT the session config. The session config is at `~/.claude/projects/`.
- **Path encoding** — the folder name uses `-` not `/`. A path like `/Users/oblinger/ob/kmr/prj/Forum` becomes `-Users-oblinger-ob-kmr-prj-Forum`.
- **Memory files** — if the project had memory, those files reference the old path and need updating.
