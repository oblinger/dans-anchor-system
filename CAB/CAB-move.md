# cab-move — Move an Anchor to a New Location

Move an anchor folder and update all systems that index by path.

**CRITICAL: Never use `cp` to move anchors.** Duplicate files with the same name cause Obsidian wiki-links to resolve to the wrong copy silently. Always use `mv`, then zip the source as a recoverable backup.

## Step 1: Move the Folder

```bash
# Zip the source as a safety net, then move
zip -r "/old/path/{NAME}.zip" "/old/path/{NAME}"
mv "/old/path/{NAME}" "/new/path/{NAME}"
```

The zip stays at the old location as a recoverable snapshot. Delete it once the move is verified (Step 7).

## Step 2: Migrate Claude Code Sessions

Sessions are stored in `~/.claude/projects/` with paths encoded (slashes and spaces become dashes).

```bash
# Use claude-mv if available
claude-mv ~/old/path ~/new/path

# Or manual rename
cd ~/.claude/projects/
mv -- -old-path-encoded -new-path-encoded
```

## Step 3: Reindex HookAnchor

```bash
ha -d n:={NAME} a:=folder r:="{new full path}"
ha -p {NAME}  # verify
```

## Step 4: Scan for Hardcoded Paths

Search for old path references:
```bash
grep -r "/old/path/" /new/path/ --include="*.py" --include="*.md" --include="*.toml" --include="*.json" --include="*.yaml" --include="*.sh"
```

Check especially: CLAUDE.md, justfile, .env, pyproject.toml, test fixtures, symlink targets.

## Step 5: Rebuild Docs (if applicable)

If the anchor has published docs, rebuild:
```bash
cd /new/path/{repo} && mkdocs build
```

## Step 6: Update RID Index

If the anchor has a RID, verify the RID index entry points to the new location.

## Step 7: Verify

```bash
ha -p {NAME}
cd /new/path/{NAME} && claude --continue
```

Check git remotes still work. Obsidian wiki-links are relative and should still resolve.

## Step 8: Clean Up Source Zip

Once everything is verified, delete the backup zip from the old location:
```bash
rm "/old/path/{NAME}.zip"
```
