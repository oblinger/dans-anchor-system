---
description: "How auditing works — design rationale, tool chain, and examples"
---
# DAS Audit
How auditing works — the rule-driven engine, the tool chain that runs it, and the detect-only posture that makes a sweep safe to run at any time.

## Philosophy

| -[[DAS Audit]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [docs](hook://docs) → [DAS Audit](hook://p/DAS%20Audit)<br>: How auditing works — design rationale, tool chain, and examples |
| --- | --- |
| Related | [[skills/audit/SKILL.md\|SKILL]],   |
| [[DAS Audit Design\|Design]]  |  |
| ... |  |

Auditing finds problems. It does NOT fix them. The output is a **punch list** — a table of fixes with concrete commands. The user reviews the punch list and tells the agent what to fix.

## Tool Chain

### cab-audit (the scanner)

`cab-audit` (formerly `cab-lint`, renamed per F078) is a Python script using tree-sitter to parse source code. It extracts class/method/field definitions and compares them against module docs. It runs in <100ms with caching. It lives at `skills/audit/scripts/cab-audit.py`.

```bash
cab-audit <path> --level 5 --json    # full scan, JSON output
cab-audit <path> --level 3           # structural only
cab-audit <path> --level 5 --pub-only  # only public APIs
```

Levels run 1 (bare-bones marker-file checks) through 9 (pedantic spacing and TOC formatting):
- 1-4: structural checks (files exist, dispatch tables wired, frontmatter/breadcrumb present)
- 5: source-to-doc comparison (module docs match source code) — the default
- 6-9: link reachability, wiki-link resolution, naming conventions, pedantic formatting

Cache: `.skl/lint/source-cache/` — keyed by file mtime. Second runs are instant.

The scanner is **detect-only by design** (migrated from the retired `/lint` skill). Even when a finding implies an obvious fix — missing dispatch row, missing module doc, misplaced file — it never edits or moves things itself; that's `/rewire`'s job. Findings either get fixed in the relevant markdown file or get a numbered, graded row in the anchor's `{slug} Track/{slug} Exceptions.md` (see [[R-exception-discipline]]). The path this line used to name, `.anchor.d/lint/exceptions.md`, never existed anywhere in the vault and nothing read it.

The agent never calls cab-audit directly for user-facing work. `/audit docs` calls it internally.

### stat (the reporter)

Audit results go to stat via `skl-stat add`. The punch list is a detail file. The user sees "N fixes needed" in Ops and clicks through.

### /code modules (the fixer)

When the user approves fixes, the agent runs `/code modules` for each item. This reads the [[DAS Module Doc]] reference example and creates/updates the doc.

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
- cab-audit caches parsed source by mtime
- Git timestamps tell us what changed
- Most runs find 0-5 stale docs, not 50

Use `--recheck` for a full pass when you suspect the incremental check missed something.

## Connection to Rules

`/audit rules` delegates entirely to `/rule check --all`. Its exception tracking is the same one the engine reads — numbered `EX` handles, graded, justified, in `{slug} Track/{slug} Exceptions.md` ([[R-exception-discipline]]). Audit just triggers it.

## Examples & related artifacts

Per the one-concept-one-list model ([[SKA File Tree Architecture]] § One concept, one list), `audit` is listed **once, as a skill (a verb)**; its satellites are reached from here:

- **Examples** — the invented specimens in `examples/` (Architecture, PRD, Decisions, Stories, Testing), which are what `/audit` is demonstrated against. The `examples/Audited/` folder this line used to name was deleted 2026-08-08: it held eleven genuine documents lifted from live projects, which [[DAS Decisions]] D1/D2 now forbid outright.
- **Scripts** — `skills/audit/scripts/` (audit's mechanism; assets of this skill).

**No separate facet.** Audit's noun-aspect — what a recorded audit report would contain — is too light to warrant its own `DAS Audit` facet file. Per the model, thin noun-content stays here on the skill page rather than spawning a facet; a facet is minted only if that spec ever becomes substantial and independently referenced.
