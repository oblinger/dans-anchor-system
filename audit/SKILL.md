---
name: audit
description: >
  Anchor auditing — verify structure, rules, documentation, code quality, and publish readiness.
  Each sub-audit reports findings and writes a backlog entry. **Audit never fixes** — fixing is
  downstream work, pulled from the backlog later.
  Use when the user says: "audit this", "check the structure", "are the docs current",
  "lint this", "check before publish", "any broken links", "run an audit".
  Subcommands: /audit structure, /audit rules, /audit docs, /audit publish, /audit code.
  Add "dry" anywhere in the args to print findings without writing a backlog entry.
tools: Read, Write, Edit, Bash, Glob, Grep, Agent
user_invocable: true
---

# Audit

Audits diagnose. They never fix. Each sub-audit produces a single **backlog entry** under `## Upcoming` in `{NAME} Backlog.md`, with **one sub-bullet per finding**. The fix work happens later, when someone pulls that backlog item — sub-bullets are the natural split points if the work needs to be broken up.

## Runbook

### Single sub-audit (`/audit structure`, `/audit docs`, `/audit rules`, `/audit publish`, `/audit code`)

1. Read the sub-skill file from this folder (it contains the full checklist inline).
2. Execute the runbook in that file. It scans, reports findings, and writes the backlog entry.
3. Print a one-line summary: `<kind>: N findings → B<n>` (or `<kind>: clean — no entry written`).

### Bare `/audit` (orchestrator — runs all applicable sub-audits)

1. Determine the anchor's traits from `.anchor` config or frontmatter; pick the sub-audits that apply (see § Which apply).
2. **Dispatch each sub-audit as a worker** (Agent tool, `subagent_type=general-purpose`). The orchestrator does *not* execute sub-audit runbooks itself — it only collects results.
   - Pass each worker: the anchor path, the sub-skill file path, and any flags (`dry`, `recheck`).
   - Each worker scans, reports, writes its own backlog entry, and reports back the B-number(s) it wrote (or "clean").
3. After all workers return, print a per-sub-audit summary line, then post one stat update:

```bash
skl-stat add "Review" "[[{NAME}]]" "Audit: <total> findings across <K> sub-audits"
```

Use `Done` + `Audit: clean` if every sub-audit returned zero findings.

## Why workers for the orchestrator

A full audit can surface hundreds of findings across sub-audits. If the orchestrator runs each sub-audit inline, its context fills up before the last sub-audit has even started. Dispatching to workers keeps each sub-audit's scratch state in its own context, and the orchestrator only sees the final summary line per worker.

## Flags

Flags can be passed as `--<flag>` or as a bare word/substring anywhere in the arguments.

- **dry / dry-run / dry run** — Match is a **substring**: anywhere the four letters `dry` appear in the args, the audit reports findings to the console but **does not write a backlog entry**. Useful for quick exploratory passes. Default behavior is to write the entry.
- **recheck / rechecked** — Ignore freshness timestamps, check everything (`docs` only).

There is no `--fix` flag. Audits never fix.

## Backlog entry format

Each sub-audit writes (or appends, if needed) a single named-list item under `## Upcoming` in `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`:

```
- **B<n> — <Kind> audit: <N> findings (<YYYY-MM-DD>)** — work surfaced by `/audit <kind>`. Sub-bullets are candidate splits if this needs to be broken up.
  - <Finding 1 — file:line / category — short description>
  - <Finding 2 — …>
  - …
```

**B-number assignment.** Read the Backlog file, scan for existing `**B<n>` markers, pick the lowest unused integer (per [[CAB Backlog]] § Format).

**One entry per sub-audit run.** Each invocation of `/audit <kind>` writes exactly one entry — no merging with prior audit entries (those are stable references). If a prior entry from the same sub-audit is still under `## Upcoming` and untouched, the user can decide whether to consolidate manually.

**Sub-bullets are findings, one each.** Don't pre-group findings into super-bullets — keep one finding per line so each is independently actionable. If the audit naturally produces categories (e.g. `audit docs` has `missing-doc`, `stale-classes`, etc.), order sub-bullets by category, then by file path.

## Actions

| Action | File | Compiled | Description |
|--------|------|----------|-------------|
| `/audit structure` | [[audit-structure]] | [[code-rewire.compiled]] | Files, dispatch tables, links, orphans |
| `/audit rules` | [[audit-rules]] | — | Rule violations from `/rule check --all` |
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

`/audit` with no args → read `traits` from config, run all applicable sub-audits as workers.
