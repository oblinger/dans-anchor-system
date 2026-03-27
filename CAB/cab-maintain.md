# Maintain — Keep Derived Files in Sync

Maintain standing synchronization orders for an anchor. When source files change, derived files are updated to match.

## When to Use

- When the system reports "⚠ Maintenance needed" (triggered by the maintain hook)
- When you want to add a new maintenance relationship: "maintain the Actions table on DEV.md"
- When you want to check what's being maintained: "show me the maintenance table"
- Invoked as `/cab maintain` or `/code maintain`

## Running Maintenance

When maintenance is needed:

1. Read `{NAME} Maintenance.md` from the Plan folder
2. For each row flagged as out of date, perform the action described
3. After completing each action, the system updates the state file

```bash
# Check what needs maintenance (usually run automatically by the hook)
python3 ~/.claude/skills/cab/maintain-check.py <anchor-path>
```

## Adding a Maintenance Entry

When the user asks to maintain something (e.g., "keep the Actions table synced to DEV.md"), add a row to `{NAME} Maintenance.md`:

| Column | What to write |
|--------|---------------|
| **Trigger** | What triggers this maintenance. See trigger types below. |
| **Action** | The type of maintenance: `copy`, `check`, `sync` |
| **Description** | English description of what to do. Be specific enough that any agent can execute it without ambiguity. |

### Trigger types

| Trigger format | When it fires | Example |
|----------------|--------------|---------|
| `./path/to/file` | File's mtime is newer than last verified | `./skills/dev/SKILL.md` |
| `./path/**/*.ext` | Any matching file is newer | `./Code/src/**/*.rs` |
| `:pr` | Agent runs maintain with `:pr` flag (before PR) | `:pr` |
| `:commit` | Agent runs maintain with `:commit` flag (before commit) | `:commit` |
| `:daily` | More than 24 hours since last verified | `:daily` |

**File triggers** — paths relative to the anchor root. Always start with `./`. Follow symlinks (including `Code`). The maintain-check script stats these files and compares to recorded mtime.

**Event triggers** — prefixed with `:`. The script ignores these during background mtime checking. They're only processed when the agent explicitly runs maintain with the event flag: `python3 maintain-check.py <path> --event pr`.

### Example entries

```markdown
| Trigger | Action | Description |
|---------|--------|-------------|
| `./skills/dev/SKILL.md` | copy | Copy the Actions table to bottom of DEV.md, replacing any existing copy |
| `./Code/src/**/*.rs` | check | Verify all source files have module docs |
| `:pr` | check | Verify dispatch tables wired, lint level 3 passes |
| `:commit` | check | Verify no blanket lint exceptions added |
| `:daily` | sync | Push planning docs to Google Drive |
```

### Action types

| Action | What it means |
|--------|---------------|
| **copy** | Read the source, extract the specified content, write it to the specified target location. Description says what and where. |
| **check** | Verify a condition is true. Description says what to check. Report if not true. |
| **sync** | Bidirectional sync via rclone. Description says the remote path. |

## How the Hook Works

A PostToolUse hook on Read checks every 30 seconds:
1. Is there a `.skl/maintain/` directory? If not, exit (1ms).
2. Is there a `pending.md` with content? If yes, output it to the agent.
3. Is it time to check? If not, exit (2ms).
4. Kick off background `maintain-check.py` which compares source mtimes to state.
5. If anything is out of date, writes to `pending.md` for the next Read to pick up.

Total cost on every Read: ~3ms. Background check every 30 seconds.

## State File

`.skl/maintain/state.json` tracks when each source was last verified. Managed by `maintain-check.py` — don't edit manually.
