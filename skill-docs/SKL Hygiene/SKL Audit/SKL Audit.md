---
description: How auditing works — design rationale, tool chain, and examples
---
# SKL Audit Guide
## Philosophy

| -[[SKL Audit]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Hygiene]] → [SKL Audit](hook://p/SKL%20Audit)<br>: the `/audit` skill |
| --- | --- |
| Related | [[skills/audit/SKILL.md\|SKILL]],   |
| [[SKL Audit Design\|Design]] |  |

Auditing finds problems. It does NOT fix them. The output is a **punch list** — a table of fixes with concrete commands. The user reviews the punch list and tells the agent what to fix.

## Tool Chain

### cab-lint (the scanner)

`cab-lint` is a Python script using tree-sitter to parse source code. It extracts class/method/field definitions and compares them against module docs. It runs in <100ms with caching.

```bash
cab-lint <path> --level 5 --json    # full scan, JSON output
cab-lint <path> --level 3           # structural only
cab-lint <path> --level 5 --pub-only  # only public APIs
```

Levels:
- 1-3: structural checks (files exist, dispatch tables wired)
- 4-5: source-to-doc comparison (module docs match source code)

Cache: `.skl/lint/source-cache/` — keyed by file mtime. Second runs are instant.

The agent never calls cab-lint directly for user-facing work. `/audit docs` calls it internally.

### stat (the reporter)

Audit results go to stat via `skl-stat add`. The punch list is a detail file. The user sees "N fixes needed" in Ops and clicks through.

### /code modules (the fixer)

When the user approves fixes, the agent runs `/code modules` for each item. This reads the [[FCT Module Doc]] reference example and creates/updates the doc.

## Audit Types by Anchor Type

| Anchor Type | structure | rules | docs | publish |
|-------------|-----------|-------|------|---------|
| Simple | ✓ | | | |
| Topic | ✓ | | | ✓ |
| Code | ✓ | ✓ | ✓ | ✓ |
| Paper | ✓ | | | ✓ |
| Skill | ✓ | | | ✓ |

Type-specific checks are in the `## Audit` section of each type spec file in `~/.claude/skills/CAB/cab-traits/`.

## Why Incremental

`/audit docs` defaults to incremental — only checking files where source is newer than docs. This is fast because:
- cab-lint caches parsed source by mtime
- Git timestamps tell us what changed
- Most runs find 0-5 stale docs, not 50

Use `--recheck` for a full pass when you suspect the incremental check missed something.

## Connection to Rules

`/audit rules` delegates entirely to `/rule check --all`. The rule system has its own exception tracking (EX numbers, grades, For/Against). Audit just triggers it.

## Examples & related artifacts

Per the one-concept-one-list model ([[SKA File Tree Architecture]] § One concept, one list), `audit` is listed **once, as a skill (a verb)**; its satellites are reached from here:

- **Examples** — the `examples/Audited/` world: real artifacts (Architecture, PRD, Decisions, Stories, Testing) in their audited form — the FEX fixture for what `/audit` produces and checks. Specific example audit-run docs are added there and linked from this page (never a standalone `FEX Audit` index entry).
- **Scripts** — `skills/audit/scripts/` (audit's mechanism; assets of this skill).

**No separate facet.** Audit's noun-aspect — what a recorded audit report would contain — is too light to warrant its own `FCT Audit` file. Per the model, thin noun-content stays here on the skill page rather than spawning a facet; a facet is minted only if that spec ever becomes substantial and independently referenced.
