---
name: audit
description: >
  Anchor auditing — verify structure, rules, documentation, and publish readiness.
  Use when the user says: "audit this", "check the structure", "are the docs current",
  "lint this", "check before publish", "any broken links", "run an audit".
  Subcommands: /audit structure, /audit rules, /audit docs, /audit publish.
  Add --fix to any audit to execute fixes immediately.
tools: Read, Write, Edit, Bash, Glob, Grep, Agent
user_invocable: true
---

# Audit

## Steps

1. Determine which audit to run (from argument or anchor type)
2. Read the sub-skill file and its `.compiled.md` checklist
3. Execute the compiled checklist
4. If `--fix`: execute fixes immediately
5. Post to stat:

```bash
skl-stat add "[[{NAME}]]" "Review" "Audit: N fixes needed" --output
```

6. Write the fixes table to the output file
7. If zero issues:

```bash
skl-stat add "[[{NAME}]]" "Done" "Audit: clean"
```

## Flags

Flags can be passed as `--fix` or just the word `fix` or `fixed` anywhere in the arguments. Same for `recheck`/`rechecked`.

- **fix / fixed** — find AND fix in one pass. Without this, audit only reports.
- **recheck / rechecked** — ignore freshness timestamps, check everything (docs only)

## Actions

| Action | File | Compiled | Description |
|--------|------|----------|-------------|
| `/audit structure` | [[audit-structure]] | [[code-rewire.compiled]] | Files, dispatch tables, links, orphans |
| `/audit rules` | [[audit-rules]] | — | Rule violations → `/rule check --all` |
| `/audit docs` | [[audit-docs]] | [[audit-docs.compiled]] | Module docs vs source code |
| `/audit publish` | [[audit-publish]] | — | PII, credentials, sensitive paths |

## Which apply

| Type | structure | rules | docs | publish |
|------|-----------|-------|------|---------|
| Simple | ✓ | | | |
| Topic | ✓ | | | ✓ |
| Code | ✓ | ✓ | ✓ | ✓ |
| Paper | ✓ | | | ✓ |
| Skill | ✓ | | | ✓ |

`/audit` with no args → read `cab-type` from config, run all applicable.
