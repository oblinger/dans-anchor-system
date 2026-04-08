---
description: dated agent-generated outputs — audit reports, analysis
---
# CAB Outputs

Agent-generated dated outputs — audit reports, code analysis results, automated assessments. Created automatically by `stat add` when an output name is provided.

## Location

`{RID} Docs/{RID} Plan/{RID} Outputs/` — inside the planning documentation tree. Created automatically by the stat command on first use.

## Structure

```
{Anchor}/
├── {RID} Docs/
│   └── {RID} Plan/
│       └── {RID} Outputs/
│           ├── {RID} Outputs.md              dispatch page
│           ├── 2026-03-28 Fallbacks Audit.md
│           └── 2026-04-01 Test Coverage.md
```

## Naming

- Files use `{date} {name}.md` format
- No RID prefix on files inside Outputs (date provides uniqueness)
- Date format: `YYYY-MM-DD`
- The stat command auto-generates the date and creates the file

## Creation

Outputs are created by the stat system:

```bash
stat add "Ready" "Fallbacks Audit" "5 HIGH, 14 MEDIUM findings"
```

The stat command:
1. Creates `{RID} Outputs/` folder if it doesn't exist
2. Creates `{date} {name}.md` with today's date
3. Returns the file path so the agent can write to it
4. Puts `[[{date} {name}]]` in the Output column of the stat table

## Dispatch Page

`{RID} Outputs/{RID} Outputs.md` — reverse chronological table:

```markdown
| Date | Output | Status |
|------|--------|--------|
| 2026-03-28 | [[2026-03-28 Fallbacks Audit]] | Ready — 5 HIGH, 14 MEDIUM |
```

## Distinction from WP

| Outputs | WP |
|---------|-----|
| Agent-generated | Human+agent collaboration |
| Auto-created by stat | Manually created via `/cab wp` |
| Inside Docs/Plan/ | At anchor root |
| Reports, analysis | Papers, presentations |
| Files only | Folders (may contain multiple files) |
