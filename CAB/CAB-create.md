# cab-create — Create a New Anchor

Create a new anchor folder with the correct structure, all doc files, dispatch tables wired, and HookAnchor registration. Every file that might be needed is created upfront — empty files are better than missing files.

## Step 1: Gather Information

Ask the user for:

| Question | Notes |
|----------|-------|
| **Type** | Simple, Topic, Code, Paper, or Skill |
| **Full Name** | Title Case with spaces (e.g., "Task Runner") |
| **Parent Anchor** | Where to create it (e.g., PP, prj, SYS/Bespoke) |
| **Description** | One-line `description:` in frontmatter |
| **RID** (optional) | Short uppercase code (e.g., TSK). If none, full name is `{NAME}` |

If RID exists, `{NAME}` = RID. Otherwise `{NAME}` = Full Name.

## Step 2: Read the Type Spec and Reference Examples

Read the type-specific file from `~/.claude/skills/cab/cab-types/` (e.g., `Code Anchor.md`, `Skill Anchor.md`).

Then read the CAB part specs — each has a **Reference Example** at the top showing exactly what the file should look like. These examples are the single source of truth for both setup and rewire. Key ones to read:

- **[[CAB Anchor Page]]** → dispatch table format and standard rows
- **[[CAB Folder]]** → marker file format
- **[[CAB Plan Dispatch]]** → Plan dispatch page format
- **[[CAB Dev Dispatch]]** → Dev dispatch page format
- **[[CAB User Dispatch]]** → User dispatch page format
- **[[CAB PRD]]**, **[[CAB System Design]]**, **[[CAB Roadmap]]**, etc. → each planning doc's format

Create every file to match its reference example, substituting `{NAME}` with the actual RID.

## Step 3: Create the Anchor Folder

Use HookAnchor to create the initial folder under the parent:

```bash
ha --action kb_create_child --input "{Full Name}" --anchor "{Parent}"
```

## Step 4: Create the Full File Structure

Based on the type, create ALL files upfront. **Do not skip files** — empty files with proper headings are better than missing files that need to be created later.

### All Types (base structure)

1. **Marker file** — `{Full Name}.md` containing `(See Anchor [[{NAME}]])`
2. **Anchor page** — `{NAME}.md` with breadcrumb, H1, `description:` in frontmatter, and dispatch table. Use the dispatch table format from [[CAB Anchor Page]].
3. **CLAUDE.md** — with role header:
   ```
   You are the Pilot for the {Full Name} project. Role: `~/.claude/skills/role/role-pilot.md`
   ```

### Code Anchor (full skeleton)

In addition to the base:

4. **Docs folder** — `{NAME} Docs/` with `{NAME} Docs.md` dispatch page
5. **Plan folder** — `{NAME} Docs/{NAME} Plan/` with ALL planning docs:
   - `{NAME} Plan.md` — dispatch page
   - `{NAME} PRD.md` — product requirements (empty template)
   - `{NAME} UX Design.md` — UX specification (empty template)
   - `{NAME} System Design.md` — architecture (empty template)
   - `{NAME} Discussion.md` — design conversations (empty with date header)
   - `{NAME} Roadmap.md` — milestones (empty template)
   - `{NAME} Backlog.md` — deferred work (empty)
   - `{NAME} Inbox.md` — raw input (empty)
   - `{NAME} Open Questions.md` — unresolved decisions (empty)
   - `{NAME} Research.md` — landscape investigation, tools, prior art (empty)
   - `{NAME} Features/` — feature specs folder (empty)
6. **Dev folder** — `{NAME} Docs/{NAME} Dev/` with:
   - `{NAME} Dev.md` — dispatch page
   - `{NAME} Files.md` — file tree (empty, monospace cssclass)
   - `{NAME} Architecture.md` — system architecture (empty template)
7. **User folder** — `{NAME} Docs/{NAME} User/` with:
   - `{NAME} User.md` — dispatch page
   - `{NAME} User Guide.md` — end-user guide (empty template)
8. **Code symlink or .git** — depending on inline vs linked mode

### Topic Anchor

Items 4-5 from Code Anchor (Docs + Plan), but NO Dev or User folders.

### Simple Anchor

Just the base (items 1-3). No Docs folder.

### Paper Anchor

Base + Docs + version table on the anchor page.

### Skill Anchor

`SKILL.md` with frontmatter instead of standard anchor page. Also:
- Create `SKL User Docs/SKL {Name} Guide.md` — user-facing documentation
- Add a row to `SKL User Docs/SKL User Guide.md` index
- Add `[[SKL {Name} Guide\|{Name} Guide]]` as first link in the SKA dispatch table row for this skill

## Step 5: Wire Dispatch Tables

**Table formatting:** Tables MUST have a blank line before them or they won't render. Escape the pipe in wiki-link aliases inside tables: `[[target\|alias]]` not `[[target|alias]]`. An unescaped `|` breaks the table column.

Every dispatch page must link to its children:
- Anchor page dispatch table → Plan, Dev, User rows with inline links
- Plan dispatch page → links to PRD, System Design, Discussion, Roadmap, etc.
- Dev dispatch page → links to Files, Architecture
- User dispatch page → links to User Guide
- Docs dispatch page → links to Plan, Dev, User

**All files must be linked before finishing.** Run `cab-lint --level 3` to verify.

## Step 6: Initialize Config

Create `.skl/config.yaml` for the new anchor:

```bash
cd "{full path to anchor folder}"
cab-config init --type {type}
```

This creates `.skl/config.yaml` with the RID, type, and auto-detected paths to now, rules, backlog, inbox, and code. Also creates the Now file if it doesn't exist.

## Step 7: Register

```bash
ha -d n:={NAME} a:=folder r:="{full path to anchor folder}"
ha -p {NAME}  # verify
```

## Step 8: Confirm

Show the user the created structure. Verify:
- `cab-lint . --level 3` passes with no structural warnings
- Marker file matches folder name
- Anchor page has breadcrumb, `description:` in frontmatter, dispatch table
- All dispatch pages link to their children
- `{NAME}` prefix on all files and folders
