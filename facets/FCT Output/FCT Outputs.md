---
description: dated agent-generated outputs — audit reports, analysis
---
# FCT Outputs
Dated agent-generated outputs (audit reports, code analysis, automated assessments) parked under `{slug} Outputs/` and auto-managed by the `stat` command.

| -[[FCT Outputs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Output]] → [FCT Outputs](hook://p/FCT%20Outputs)<br>: dated agent-generated outputs — audit reports, analysis |
| --- | --- |
| Related | [[FCT WP]],  [[CAB Stat]],  [[CAB Backlog]],  [[FCT Facet]],   |
| Examples | [[MUX Outputs\|example dispatch page]],   |

**TLDR** — A folder of dated `{date} {name}.md` files auto-created by `stat add`; cardinality **many** (any number of output files per anchor). The dispatch page (`{slug} Outputs.md`) is **one per anchor**; individual output files are **many**. Never list specific files here — instances live in per-anchor dispatch pages.

The CAB facet that specifies the Outputs zone — dated agent-generated reports (audit findings, code analysis, automated assessments) parked under `{slug} Docs/{slug} Plan/{slug} Outputs/` and auto-managed by the `stat` command.

Agent-generated dated outputs — audit reports, code analysis results, automated assessments. Created automatically by `stat add` when an output name is provided. **Cardinality: many** — any number of dated output files may exist per anchor.

## Location

`{slug} Docs/{slug} Plan/{slug} Outputs/` — inside the planning documentation tree. Created automatically by the stat command on first use.

## Structure

```
{Anchor}/
├── {slug} Docs/
│   └── {slug} Plan/
│       └── {slug} Outputs/
│           ├── {slug} Outputs.md              dispatch page
│           ├── 2026-03-28 Fallbacks Audit.md
│           └── 2026-04-01 Test Coverage.md
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
# {NAME} Outputs

| -[[{NAME} Outputs]]- |  |
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

- **This file is the CAB facet spec for the Outputs zone** — it defines location, naming, structure, and dispatch-page shape for `{slug} Outputs/`. Authority over the Outputs convention lives here; other docs cite it, do not redefine it.
- **NOT a catalog of outputs** — never list specific output files (audits, analyses) here. Those live in per-anchor `{slug} Outputs.md` dispatch pages. This spec is rule-shaped, not instance-shaped.
- **Inclusion test for additions:** a rule, naming convention, or structural constraint that applies to ALL Outputs folders across ALL anchors belongs here. Per-anchor or per-output specifics do not.
- **Load-bearing — do not edit naming or path without sweeping callers**: the `stat` command, `/cab wp`'s distinction logic, and per-anchor dispatch pages all encode `{slug} Docs/{slug} Plan/{slug} Outputs/` and `{date} {name}.md` (no slug prefix on individual files, date provides uniqueness). Renaming the zone or changing the date format breaks `stat add` and orphans every existing dispatch entry.
- **Hold the line on the Outputs-vs-WP distinction** — the comparison table is load-bearing; edits that blur the boundary (e.g. allowing manual creation under Outputs, or human-collaborative work) cascade into ambiguous tooling behavior. Re-read § Distinction from WP before relaxing any row.
- **Dispatch-page format is prescriptive** — H1 + F060 dispatch-table placeholder + reverse-chronological topic table. Individual output files carry the standard top-of-doc (H1 + dispatch-table placeholder). Don't drift to a different shape without coordinating with the `stat` script.
- **Sibling facets** ([[FCT WP]], [[CAB Backlog]], [[CAB Stat]]) cite this spec — when changing terminology or structure, search for back-cites and update them in the same pass.

# RULESET R-fct-outputs
include::
where:: file: **/{slug} Docs/{slug} Plan/{slug} Outputs/{slug} Outputs.md
description:: The rules every Outputs folder and its dispatch page must satisfy — location, naming, dispatch-page shape, and individual output-file format.

### RULE R-fct-outputs-01 — Outputs live inside the Plan subtree (checked)
The Outputs folder lives at `{slug} Docs/{slug} Plan/{slug} Outputs/`, not at the anchor root or elsewhere.
**Check pattern:** the dispatch page path matches `*/{slug} Docs/{slug} Plan/{slug} Outputs/{slug} Outputs.md`.
**Why:** the Outputs zone is part of the planning documentation tree; placing it elsewhere breaks the `stat` command's path assumptions.

### RULE R-fct-outputs-02 — Individual output files use `{YYYY-MM-DD} {Name}.md` (checked)
Each output file uses `YYYY-MM-DD` as the date prefix and no slug prefix; the name follows the date.
**Check pattern:** filenames inside `{slug} Outputs/` (other than the dispatch page) match `^\d{4}-\d{2}-\d{2} .+\.md$`.
**Why:** the date provides uniqueness within the folder; a slug prefix is redundant and would break the `stat` command's naming contract.

### RULE R-fct-outputs-03 — Dispatch page is H1 + placeholder + reverse-chrono table (sampled)
`{slug} Outputs.md` contains: an H1 (`# {NAME} Outputs`), the standard F060 dispatch-table placeholder, then a reverse-chronological table with `Date | Output | Status` columns.
**Check pattern:** the dispatch page has an H1, the two-row placeholder table, and a `| Date |` table.
**Why:** the shape is prescriptive so the `stat` command can reliably update the table and agents can parse it consistently.

### RULE R-fct-outputs-04 — Individual output files carry top-of-doc header (sampled)
-[[{date} {name}]]-` + separator row) before the report body.
**Check pattern:** the first non-empty lines of each output file are an H1 followed by a two-row table.
**Why:** standard top-of-doc navigation — consistent with all other anchor pages.
