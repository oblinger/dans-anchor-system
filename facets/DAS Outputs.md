---
description: dated agent-generated outputs — audit reports, analysis
group: file
---

| -[[DAS Outputs]]- | → [[DAS]] → [[FCT]] → [DAS Outputs](hook://p/DAS%20Outputs)  |
| --- | --- |
| Related | [[DAS WP]],  [[DAS Status]],  [[DAS Backlog]],  [[DAS Facet]],   |
| Examples | [[MUX Outputs\|example dispatch page]],   |
| Rules | [[R-fct-outputs]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Outputs
Dated agent-generated outputs (audit reports, code analysis, automated assessments) parked under `{slug} Outputs/` and auto-managed by the `stat` command.

**TLDR** — A folder of dated `{date} {name}.md` files auto-created by `stat add`; cardinality **many** (any number of output files per anchor). The dispatch page (`{slug} Outputs.md`) is **one per anchor**; individual output files are **many**. Never list specific files here — instances live in per-anchor dispatch pages.

The DAS facet that specifies the Outputs zone — dated agent-generated reports (audit findings, code analysis, automated assessments) parked under `{slug} Track/{slug} Outputs/` and auto-managed by the `stat` command.

Agent-generated dated outputs — audit reports, code analysis results, automated assessments. Created automatically by `stat add` when an output name is provided. **Cardinality: many** — any number of dated output files may exist per anchor.

## Location

`{slug} Track/{slug} Outputs/` — alongside the anchor's other activity records. Created automatically by the stat command on first use.

## Structure

```
{Anchor}/
└── {slug} Track/
    └── {slug} Outputs/
        ├── {slug} Outputs.md              dispatch page
        ├── 2026-03-28 Fallbacks Audit.md
        └── 2026-04-01 Test Coverage.md
```

## Naming

- Files use `{date} {name}.md` format
- No slug prefix on files inside Outputs (date provides uniqueness)
- Date format: `YYYY-MM-DD`
- The stat command auto-generates the date and creates the file

## Creation

Outputs are created by the stat system:

```bash
stat add "Ready" "Fallbacks Audit" "5 HIGH, 14 MEDIUM findings"
```

The stat command:
1. Creates `{slug} Outputs/` folder if it doesn't exist
2. Creates `{date} {name}.md` with today's date
3. Returns the file path so the agent can write to it
4. Puts `[[{date} {name}]]` in the Output column of the stat table

## Dispatch Page

`{slug} Outputs/{slug} Outputs.md` — H1 + F060 dispatch-table placeholder, then a reverse chronological topic table:

```markdown
# {slug} Outputs

| -[[{slug} Outputs]]- |  |
| --- | --- |
| --- | |

| Date | Output | Status |
|------|--------|--------|
| 2026-03-28 | [[2026-03-28 Fallbacks Audit]] | Ready — 5 HIGH, 14 MEDIUM |
```

-[[{date} {name}]]- \| \|` + standard separator) above the report body.

## Distinction from WP

| Outputs | WP |
|---------|-----|
| Agent-generated | Human+agent collaboration |
| Auto-created by stat | Manually created via `/cab wp` |
| Inside Docs/Plan/ | At anchor root |
| Reports, analysis | Papers, presentations |
| Files only | Folders (may contain multiple files) |

# BRIEF

*(Maintainer note — additions belong here only if they apply to ALL Outputs folders across ALL anchors; per-anchor or per-output specifics do not. The path `{slug} Track/{slug} Outputs/` and the `{date} {name}.md` naming (no slug prefix, date provides uniqueness) are encoded in the `stat` command and `/cab wp`'s distinction logic — renaming the zone or changing the date format breaks `stat add` and orphans every existing dispatch entry, so sweep callers before touching them. Hold the Outputs-vs-WP boundary (§ Distinction from WP) — blurring it cascades into ambiguous tooling behavior. Sibling facets [[DAS WP]], [[DAS Backlog]], [[DAS Status]] back-cite this spec, so update them in the same pass on any terminology or structure change.)*
