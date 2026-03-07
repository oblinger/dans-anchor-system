# cab-create — Create a New Anchor

Create a new anchor folder with the correct structure, register it with HookAnchor, and set up Obsidian indexing.

## Step 1: Gather Information

Ask the user for:

| Question | Notes |
|----------|-------|
| **Type** | Simple, Topic, Split, Private Repo, Public Repo, or Paper |
| **Full Name** | Title Case with spaces (e.g., "Task Runner") |
| **Parent Anchor** | Where to create it (e.g., PP, prj, SYS) |
| **Description** | One-line `desc::` field |
| **TLC** (optional) | Short uppercase code (e.g., TSK). If none, full name is `{NAME}` |

If TLC exists, `{NAME}` = TLC. Otherwise `{NAME}` = Full Name.

## Step 2: Read the Type Spec

Find the CAB folder:
```bash
ha -p CAB
```

Read the type-specific file from `CAB Types/` (e.g., `Simple Anchor.md`, `Private Repo Anchor.md`). This tells you what files and folders to create beyond the base structure.

Also read `CAB Base.md` for the base file tree and `CAB Parts/CAB All Files.md` for the full reference.

## Step 3: Create the Anchor Folder

Use HookAnchor to create the initial folder under the parent:

```bash
ha --action kb_create_child --input "{Full Name}" --anchor "{Parent}"
```

If only a file is created (not a folder), create a subfolder with the same name and move the file into it.

## Step 4: Create the File Structure

Based on the type spec, create:

1. **Marker file** — `{Full Name}.md` containing `(See [[{NAME}]])`
2. **Anchor page** — `{NAME}.md` with H1 heading, `desc::` field, and link table (see `CAB Parts/CAB Page.md` for format)
3. **Docs folder** — `{NAME} Docs/` with `{NAME} Docs.md` dispatch page
4. **Plan folder** — `{NAME} Docs/{NAME} Plan/` with:
   - `{NAME} Plan.md` — dispatch page
   - `{NAME} Inbox.md` — empty inbox
   - `{NAME} PRD.md` — if this is a software project
5. **CLAUDE.md** — with role header (see `CAB Parts/CAB Claude.md` for format):
   ```
   You are the Pilot for the {Full Name} project. Role: `~/.claude/skills/role/role-pilot.md`
   ```
6. **Type-specific files** — whatever the type spec requires (Code symlink, Cards folder, etc.)

**Critical:** Every markdown file and folder must be prefixed with `{NAME}`. See `CAB Rules/CAB Naming Conventions.md` for the full rule.

## Step 5: Register

1. **Register HookAnchor command:**
   ```bash
   ha -d n:={NAME} a:=folder r:="{full path to anchor folder}"
   ```

2. **Verify:**
   ```bash
   ha -p {NAME}
   ```

3. **Update TLC index** (if TLC was assigned):
   ```bash
   cd "$(ha -p PC)" && python bin/scan_tlc.py delta --update
   ```

## Step 6: Confirm

Show the user the created structure and verify:
- Marker file exists and matches folder name
- Anchor page has correct H1, desc::, link table
- HookAnchor command resolves
- {NAME} prefix on all files and folders
