# CAB Page Conventions

The anchor page (`{NAME}.md`) is the primary entry point for the project. See also [[CAB Anchor Page]] for the structural description.

## Description Field
- Include a `description:` field in the YAML frontmatter for the slug index
- Format (in frontmatter): `description: Brief description of the project`
- This is extracted when building the slug table
- Older anchors may use `desc::` inline — migrate to `description:` in frontmatter.

## Anchor Link Table
The anchor page begins with a link table. Example:

| {NAME} Docs | -------------------------------- |
| ------------ | ------------------------------------------------- |
| External | [Repo](url), [Docs](url) |
| {NAME} Docs | [[{NAME} PRD]], [[{NAME} Features]] |
| - Execution | [[{NAME} Roadmap]] |
| User Docs | [[User Guide]], [[Architecture Docs]], [[api/index\|API]] |

### External Row
Links to resources outside the Obsidian vault:
- **REPO** — GitHub repository URL
- **DOCS** — Published documentation site (GitHub Pages)
- **LEGACY** — Link to legacy/archived version if this replaces an older project

### Planning Row
Links to planning documents (private, not published):
- **{NAME} DOCS** — Anchor for the planning subfolder
- **{NAME} PRD** — Product Requirements Document
- **{NAME} FEATURES** — Feature design log; **dated sections**

### Execution Row
Links to task tracking documents (sub-row of Planning):
- **{NAME} ROADMAP** — Milestone-based task organization
- **{NAME} BACKLOG** — Deferred work and low-priority ideas

### User Docs Row
Links to published end-user documentation:
- **USER GUIDE** — Task-oriented tutorials and how-tos
- **ARCHITECTURE DOCS** — System design, class documentation
- **API** — Generated API reference (from docstrings)

## Body Content
- Below the link table, add project-specific content as needed
- Overview, key concepts, quick reference, etc.
- Keep it dense and scannable; move lengthy content to sub-documents

## CAB Page Rules
- All documentation must be linked from the anchor page
- If content would generate a lot of text directly in the anchor page, move it to a sub-document and link to it
- Goal is a dense, scannable page with links to details

# BRIEF

- **This file is the convention spec for `{NAME}.md` anchor pages** — the rules that govern the description field, the anchor link table, the row taxonomy (External / Planning / Execution / User Docs), and the body-content discipline. Edits here change how every anchor page is shaped.
- **NOT for structural decomposition of the anchor page itself** — that lives in [[CAB Anchor Page]] (which this file cross-references). Don't restate structural rules here; describe *conventions* (field names, row formats, naming) only.
- **Inclusion test for a new convention row**: it must be a *page-level convention* (frontmatter field, link-table row, body-discipline rule) that applies across all anchors, not a per-anchor-type variation. Anchor-type variations belong in `CAB <Type>.md` facets.
- **Row naming is load-bearing** — the row labels (External / {NAME} Docs / - Execution / User Docs) are referenced by audit scripts and downstream tooling. Don't rename without checking [[CAB Anchor Page]] and the slug/anchor scanners.
- **Keep the body dense** — this is itself a convention page; resist piling examples or rationale here. Examples belong in the worked instances ([[SYS]], [[KM]], etc.); rationale belongs in CAB design discussion.
- **Cross-references**: [[CAB Anchor Page]] (structural sibling), `description:` field consumed by the slug index. Changes to the `description:` format require coordinated update of the slug scanner.
