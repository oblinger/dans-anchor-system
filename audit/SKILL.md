---
name: audit
description: >
  Anchor auditing — verify structure, rules, documentation, and publish readiness.
  Use when the user says: "audit this", "check the structure", "are the docs current",
  "lint this", "check before publish", "any broken links", "run an audit".
  Subcommands: /audit structure, /audit rules, /audit docs, /audit publish.
  Structure and docs fix by default — say "dry" anywhere in the args to preview without changing anything. Rules and publish are report-only; code is report-only unless --fix is given.
tools: Read, Write, Edit, Bash, Glob, Grep, Agent
user_invocable: true
---

# Audit

## Runbook

1. Determine which audit to run (from argument or anchor type)
2. Read the sub-skill file from this folder (it contains the full checklist inline)
3. Execute the Runbook in that file
4. Apply fixes per sub-audit defaults:
   - **`structure`, `docs`** — fix by default. **If the substring `dry` appears anywhere in the args**, skip the fix pass and announce "dry-run — fixes listed above were not applied."
   - **`rules`, `publish`** — inherently report-only at this layer; nothing to fix.
   - **`code`** — report-only by default; only fix if `--fix` is explicitly passed.
5. Post to stat:

```bash
skl-stat add "Review" "[[{NAME}]]" "Audit: N fixes needed"
```

6. Write the fixes table to the output file
7. If zero issues:

```bash
skl-stat add "Done" "[[{NAME}]]" "Audit: clean"
```

## Flags

Flags can be passed as `--<flag>` or as a bare word/substring anywhere in the arguments.

- **dry / dry-run / dry run** — *(applies to `structure` and `docs` only)* Match is a **substring**: anywhere the four letters `dry` appear in the args, the audit reports what would be fixed but doesn't apply changes. The summary explicitly says "dry-run — fixes listed above were not applied." Default behavior is fix.
- **fix** — *(applies to `code` only)* Opt into auto-fix for `/audit code`. Default is report only.
- **recheck / rechecked** — Ignore freshness timestamps, check everything (docs only).

`rules` and `publish` are inherently report-only at this layer — neither flag affects them.

## Actions

| Action | File | Compiled | Description |
|--------|------|----------|-------------|
| `/audit structure` | [[audit-structure]] | [[code-rewire.compiled]] | Files, dispatch tables, links, orphans |
| `/audit rules` | [[audit-rules]] | — | Rule violations → `/rule check --all` |
| `/audit docs` | [[audit-docs]] | [[audit-docs.compiled]] | Module docs vs source code |
| `/audit publish` | [[audit-publish]] | — | PII, credentials, sensitive paths |
| `/audit code` | [[audit-code]] | — | Code quality: silent fallbacks, dead code, magic values (Semgrep + agent) |

## Which apply

| Trait | structure | rules | docs | code | publish |
|-------|-----------|-------|------|------|---------|
| Simple | ✓ | | | | |
| Topic | ✓ | | | | ✓ |
| Code | ✓ | ✓ | ✓ | ✓ | ✓ |
| Paper | ✓ | | | | ✓ |
| Skill | ✓ | | | | ✓ |

For multi-trait anchors, run the union of all applicable checks across all traits.

`/audit` with no args → read `traits` from config, run all applicable.
