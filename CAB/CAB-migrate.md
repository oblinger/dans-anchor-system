# cab-migrate — Convert Between Anchor Types

Convert an anchor from one type to another, preserving all content and updating references.

## Step 1: Verify Source Anchor

- Identify current type and location via `ha -p "{NAME}"`
- List all content: anchor page, planning docs, user docs, code repos
- Note all HookAnchor commands for this anchor

## Step 2: Read Type Specs

From the CAB folder (`ha -p CAB`), read:
- Source type file from `CAB Types/`
- Target type file from `CAB Types/`
- `CAB Base.md` for the base tree

## Step 3: Create Target Structure

- Create the new folder in the appropriate location for the target type
- Copy marker file and anchor page
- Copy `{NAME} Docs/` preserving all subfolders

## Step 4: Type-Specific Migration

Read the full migration runbook at `CAB Skills/CAB Migrate.md` (in the CAB folder) for type-specific steps. Common migrations:

- **Public Repo → Split Anchor** — Separate planning from public docs, move repo to `~/ob/proj/`, create Code symlink
- **Private Repo → Split Anchor** — Create vault-side anchor, move planning docs out of repo, create Code symlink

## Step 5: Update HookAnchor

```bash
ha -d n:={NAME} a:=folder r:="{new path}"
ha -d n:="{NAME} Code" a:=open r:="{repo path}"  # if Split Anchor
```

## Step 6: Migrate Claude Code Session

The path key is the project path with `/` replaced by `-` and a leading `-`. Example: `/Users/oblinger/ob/kmr/prj/ClaudiMux` → `-Users-oblinger-ob-kmr-prj-ClaudiMux`.

**Find the most recent session** in the old project folder — don't copy all of them:

```bash
# Find the most recent .jsonl by modification time
OLD_KEY="-Users-oblinger-ob-kmr-prj-ClaudiMux"
NEW_KEY="-Users-oblinger-ob-kmr-prj-ClaudiMux-MuxUX"

LATEST=$(ls -t ~/.claude/projects/${OLD_KEY}/*.jsonl 2>/dev/null | head -1)
SESSION_ID=$(basename "$LATEST" .jsonl)

# Create the new project folder
mkdir -p ~/.claude/projects/${NEW_KEY}

# Copy ONLY the most recent session (jsonl + companion directory)
cp "$LATEST" ~/.claude/projects/${NEW_KEY}/
[ -d ~/.claude/projects/${OLD_KEY}/${SESSION_ID} ] && \
  cp -R ~/.claude/projects/${OLD_KEY}/${SESSION_ID} ~/.claude/projects/${NEW_KEY}/

# Copy the memory folder if it exists
[ -d ~/.claude/projects/${OLD_KEY}/memory ] && \
  cp -R ~/.claude/projects/${OLD_KEY}/memory ~/.claude/projects/${NEW_KEY}/
```

Copy, don't move — keep old session as backup until verified. Only copy the most recent session (by mtime) plus the memory folder. Old sessions are conversation history that doesn't apply to the new location.

After copying, verify by running `claude --resume` from the new anchor directory.

## Step 7: Test Before/After

Run tests before and after migration. If new failures appear after path fixups, attempt up to 3 retries. If still failing, rollback and flag for the user.

## Step 8: Scan for Hardcoded Paths

Scan both the vault anchor and the repo for references to the old path. Also check the Claude session folder.

```bash
# Scan repo for old vault path
grep -r "/old/vault/path/" /new/repo/path/ --include="*.py" --include="*.md" --include="*.toml" --include="*.json" --include="*.yaml" --include="*.sh" --include="*.swift" --include="*.rs" --include="*.just"

# Scan vault anchor for old repo path
grep -r "/old/repo/path/" /new/vault/path/ --include="*.md" --include="*.json" --include="*.yaml"

# Scan CLAUDE.md specifically
grep "/old/" /new/vault/path/CLAUDE.md
```

Old paths in Claude session logs (`.jsonl` files) are harmless conversation history — don't fix those.

## Step 9: Clean Up

- Remove anchor files from old location (keep code repos until verified)
- Update RID index if needed
- Verify: `ha -p {NAME}` resolves, tests pass, Claude session works
