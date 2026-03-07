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

```bash
cp -R ~/.claude/projects/{OLD_PATH_KEY} ~/.claude/projects/{NEW_PATH_KEY}
```

Copy, don't move — keep old session as backup until verified.

## Step 7: Test Before/After

Run tests before and after migration. If new failures appear after path fixups, attempt up to 3 retries. If still failing, rollback and flag for the user.

## Step 8: Scan for Hardcoded Paths

```bash
grep -r "/old/path/" /new/path/ --include="*.py" --include="*.md" --include="*.toml" --include="*.json" --include="*.yaml" --include="*.sh"
```

## Step 9: Clean Up

- Remove anchor files from old location (keep code repos until verified)
- Update TLC index if needed
- Verify: `ha -p {NAME}` resolves, tests pass, Claude session works
