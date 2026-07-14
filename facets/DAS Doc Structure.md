---
description: "the Doc Structure facet — the canonical top-to-bottom layering every document follows (progressive disclosure specialized for a single document)"
---

# DAS Doc Structure
The standard top-to-bottom structure every document follows — progressive disclosure specialized for a single document: each layer reveals more depth for a more-committed reader. This is the **main facet for any document**; the other doc facets (Brief, Discussion, Ruleset) describe regions *within* this structure.

| -[[DAS Doc Structure]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Doc Structure](hook://p/DAS%20Doc%20Structure) |
| --- | --- |
| Related | [[DAS progressive-disclosure]] (the discipline this specializes),  [[DAS Brief]],  [[DAS Anchor Page]], |
| Examples | [[FEX Minimal Facet\|minimal — short doc, no table]],  [[HBR Architecture\|fuller — non-anchor doc with structured body]],  [[FEX Manifest\|facet spec]],  [[FEX Retention\|discipline]],  [[DAS Brief\|facet spec]],  [[HBR\|project]],  [[FEX Snapshot\|skill]],  [[FEX Repo\|repo]],   |
| Rules | [[R-doc-structure]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[facets/DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Disciplines Brief]],  [[DAS Dispatch]],  [[DAS Dispatch Table Design]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Plan Dispatch]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS TSK User Guide]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

## Overview
[[DAS progressive-disclosure]] is the general discipline — reveal information in layers so a reader gets the gist first and drills in only as far as they need. **Doc Structure** is that discipline applied to a *single document*: a fixed top-to-bottom order of layers, each aimed at a more-committed reader than the last. Every document the system owns — anchor page, facet spec, feature doc, design doc, user guide — follows this skeleton; specific document kinds (e.g. [[DAS Anchor Page]]) refine it but never violate the layer order.

**Cardinality: one per document.** Every authored `.md` file has exactly one Doc Structure — each document follows this top-to-bottom skeleton once. Across an anchor the facet applies to each individual document independently.

## The standard structure (top to bottom)

The fixed order **every non-trivial page opens with** — any page that either has substructure (at least one document/page beneath it) or carries more than ~2 pages of its own content. The top layers are always present; lower layers appear only when the document is big enough to warrant them.

### 0. Breadcrumb — *optional; only on a non-anchor doc with no dispatch table*
- A non-anchor page that has **no dispatch table** opens with a `:>>` breadcrumb line **above** the H1, with **no blank line** between the breadcrumb and the H1.
- An **anchor page carries its breadcrumb inside the dispatch table's first cell instead** (per [[DAS Dispatch Table]]) — never both a `:>>` line and a dispatch masthead.

### 1. H1 — names the document *(required)*
- **Anchor document** (a `{slug}.md` anchor page): `# {slug} - {Name}` — the slug, then the readable name.
- **Non-anchor document**: `# {Name}` — just the document's name.
- **Optional defining phrase**: either form may be followed by ` — {phrase}` that defines/explains the document, or gives it a fuller name.

### 2. Summary line — one sentence, directly under the H1, **no blank line** *(names what the document is)*
- **Typically EITHER the H1's `— {phrase}` OR this summary line carries the "what this is" — not both.** Use whichever fits the document.
- See the **Document / Anchor examples** rows above for one of each H1 form (name-only vs slug-prefixed).

### 3. Central figure — *optional, comes next*
A single defining/central figure (Excalidraw + embedded export, never ASCII) when a picture orients faster than prose. Very optional — most documents have none.

### 4. Top table — the **document table** *(presence governed by two independent rules)*
The **top table** (the *document table*) is the document's progressive-disclosure entry point — the navigation surface a reader hits right after the H1 / summary. There are **two distinct kinds**, each governed by its own rule, and a document may carry zero, one, or (rarely) both:

**(a) Dispatch table — iff the document is an anchor.**
- **Anchor file → MUST have a dispatch table** — breadcrumb masthead + member / links zone (per [[DAS Dispatch Table]] / [[DAS Anchor Page]]). **No anchor is ever table-less** (enforced by `R-anchor-page-22`); a leaf / topic anchor still carries breadcrumb + a `...` auto-summary.
- **Non-anchor file → MUST NOT have a dispatch table.** A breadcrumb-masthead dispatch table on a non-anchor document (e.g. a user-story file, a feature doc, a plain content page) is a violation — remove it. Back-links to a parent / sibling belong in a `## Related` / `## See also` section, not a masthead.

**(b) Table of contents table — iff the document is long (more than ~3 pages of content).**
- **Long document (more than ~3 pages) → MUST have a TOC table** — a content-outline table: left column links to the document's own sections (in-document `[[#Heading]]` links), right column says in one line what each section is. A table of contents *with descriptions*.
- **Short document (≲ 3 pages) → MUST NOT have a TOC table** — it adds navigation overhead a reader who can scroll the whole document doesn't need.

**(c) Specialized tables.** Some specialized documents legitimately carry *another kind of table* at the top — e.g. a stories **index** table (`{slug} Stories.md`), a status board, a glossary. These are neither a dispatch table nor a TOC table; they are the document's content, and rules (a) / (b) do not forbid them.

*(The **TOC / content-outline table** likely deserves its own facet — e.g. `DAS Content Outline` — described inline here for now.)*

### 5. TLDR — *optional; immediately below the table, before any Overview*
A short gist for the reader who has navigated past the table and wants the bottom line before committing to the body. (For a small document with no table, the summary line under the H1 already serves this role — a separate TLDR isn't needed.)

### 6. Overview — *optional `## Overview` H2*
A paragraph, added only when the summary / TLDR isn't enough.

### 7. Body — the document's sections
The actual content the document holds. At the very bottom, the agent-facing `# BRIEF` (per [[DAS Brief]]) when the document needs maintenance notes.

**Why this order — progressive disclosure.** A glance-reader gets what they need from the H1 + summary; a navigator uses the table; a committed reader reads TLDR → Overview → Body; the maintaining agent reads the Brief. Each layer down serves a more-committed reader.

## Relationship to other facets
- **[[DAS progressive-disclosure]]** — the general discipline; this facet is its document-scoped specialization.
- **[[DAS Anchor Page]]** — a specific document kind (the `{slug}.md` anchor page) that refines this skeleton with the dispatch-table form.
- **[[DAS Brief]]** — owns the bottom (agent-facing) layer; its three-reader-zones model seeded this facet.
- **[[DAS Ruleset]] / [[DAS Discussion]]** — other regions that live *within* the Body.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body and ruleset above.)*

- **Spec, not an instance** — never paste a real document here.
- **Listed first in the [[DAS Doc]] group** — it's the umbrella facet defining the whole skeleton; keep it first.
- **Don't duplicate [[DAS Anchor Page]] or [[DAS Brief]]** — this facet is the *general* layering; those refine / own specific layers. Stay document-scoped (folder / multi-file structure is [[DAS Folder]] / [[DAS Anchor Tree]]).
- **Rule numbers are monotonic-forever** — never recycle `R-doc-structure-NN`.
- **Open to confirm** — whether the under-H1 *summary line* (§2) and the below-table *TLDR* (§5) are one element or two (modeled as two, collapsing when there's no table).
