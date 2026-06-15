# Paper Anchor

Trait spec defining how an anchor that holds a long-form document (paper, whitepaper) is shaped — version table, sectioned editing, track-changes HTML, and Paper Flow review/merge.

Follows [[CAB Base]] with these deltas:

## When to Use

Academic papers, whitepapers, long-form documents that go through multiple revision cycles.

## Deltas from Base

- **Version table** — tracks document versions and per-section revisions on the anchor page
- **Section-based editing** — paper split into sections (s1, s2, ...) for focused work
- **Track changes** — section revisions stored as HTML with insertions/deletions
- **Paper Flow** — specialized review and merge workflow

## Structure

```
{Paper Name}/
├── {Paper Name}.md                  marker file → (See {NAME}.md)
├── {NAME}.md                        anchor page (link table + version table)
├── {NAME} YYYY-MM-DD.md             merged version (one per version date)
├── {NAME} YYYY-MM-DD s1.html        section 1 revisions (track changes)
├── {NAME} YYYY-MM-DD s2.html        section 2 revisions
├── ...
└── {NAME} Research/                 optional: research materials
```

## Version Table

The version table is the core of the Paper Anchor. It lives on the anchor page.

| Version | Markup | Notes |
| --- | --- | --- |
| [[{NAME} YYYY-MM-DD]] | s1 s2 s3 ... |  |
| [[{NAME} YYYY-MM-DD]] | (original) | s1: Intro, s2: Methods, ... |

### Row Organization
- **Row 1 (top)** — working row: where current edits go
- **Row 2** — source row: the version being revised
- **Reverse chronological order** — newest versions at top

### Markup Column
- Unedited sections: just text (`s1`)
- Edited sections: link to HTML with track changes (`[[{NAME} YYYY-MM-DD s1.html|s1]]✓`)
- `✓` indicates the section revision is complete

## Section Philosophy

Claude works best on coherent, manageable chunks. Splitting into sections allows focused attention, smaller context, and incremental progress.

- **Guideline**: Aim for sections that are coherent logical units (roughly 1-2 pages each)
- **Numbering**: Sequential (`s1`, `s2`, `s3`); insert without renumbering (`s2b`)
- **Invisible markers**: Use `<!-- s3 -->` to subdivide without visible headings

## Paper Flow

### Paper Flow Review
**Trigger:** User says "paper flow review"

1. Claude reads from row 2 (source version)
2. User specifies a section: "let's work on section 2"
3. Claude creates/updates `{NAME} {DATE} s{N}.html` with track changes
4. Revisions are relative to the source (row 2), not to previous revisions in row 1
5. The same revision file is updated across multiple sessions

### Paper Flow Merge
**Trigger:** User says "paper flow merge"

1. Claude takes all section revisions from row 1
2. For sections without revisions, pull content from row 2
3. Merge all sections into a single markdown document
4. If current date matches existing version: overwrite
5. If new date: create new file, add to Version column

## Setup Checklist

1. Create folder with paper name
2. Create marker: `{Paper Name}.md` → `(See [[{NAME}]])`
3. Create anchor page: `{NAME}.md` with link table and version table
4. Add original document as first version (row 2)
5. Decide on section structure and add descriptions in Notes column
6. Create empty row 1 for revisions
7. Register HookAnchor commands (`ha -d`)
8. Register slug in the [[slug]] index

## Audit

Type-specific structure checks for Paper Anchors.

### Required files
- Version table on the anchor page
- `{NAME} Docs/` folder with dispatch page

### Conditional structure
- Create `{NAME} Dev/` folder only when another trait requires it (e.g., Code trait)
- Add a `code:` key to `.anchor` only when the anchor gains the `code` trait

## Anchor-page example

Anchor-page kinds catalog: [[FCT Anchor Page]]. Synthetic Paper example: *(none yet)*; real instances: [[ABP]], [[ASP]].

# BRIEF

- **This file is the trait spec for Paper Anchor**, sibling to other `CAB Traits/*.md` files. It defines the on-disk shape, the version-table contract, and the Paper Flow review/merge semantics — when changed, downstream skills and audits that target Paper anchors must be re-checked.
- **Edits here are normative for every Paper Anchor in the vault**: changes to the version-table schema, section-numbering convention, or trigger phrases ("paper flow review" / "paper flow merge") ripple to existing anchors and any tooling that parses them. Treat changes as a migration, not a tweak.
- **Inclusion test** — content belongs on this page only if it is a *trait-level* rule (true for every Paper Anchor). Per-paper customizations (specific section names, particular review cadences, one-off conventions) belong on that paper's anchor page or rules file, never here.
- **Do NOT inline content that belongs elsewhere**: project-wide markdown rules → [[R-markdown]]; common dispatch-table / anchor-page shape → [[CAB Base]]; the Brief discipline itself → [[FCT Brief]]; per-anchor decisions → that anchor's `{NAME} Decisions.md`.
- **Load-bearing conventions to preserve**: the H2 names (`When to Use`, `Deltas from Base`, `Structure`, `Version Table`, `Section Philosophy`, `Paper Flow`, `Setup Checklist`, `Audit`); the `s1 s2 s3` section-numbering scheme with insertion form `s2b`; the `✓` completion marker in the Markup column; row-1-working / row-2-source orientation; reverse-chronological row order.
- **Linking conventions**: refer to this trait as `[[Paper Anchor]]`; sibling traits live under `CAB Traits/`; the umbrella catalog is [[CAB Traits]]. When citing this spec from a worked instance, link the trait name — never copy the spec body.
- **What NOT to pile here**: worked examples of specific papers, troubleshooting logs, half-finished section-numbering experiments, or one-off skill runbooks. Examples belong in the relevant Paper anchor; runbook content belongs in the corresponding skill file.
