---
description: "the Doc Structure facet — the canonical top-to-bottom layering every document follows (progressive disclosure specialized for a single document)"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Doc]] → [FCT Doc Structure](hook://p/FCT%20Doc%20Structure)

# FCT Doc Structure
The standard top-to-bottom structure every document follows — progressive disclosure specialized for a single document: each layer reveals more depth for a more-committed reader. This is the **main facet for any document**; the other doc facets (Brief, Discussion, Ruleset) describe regions *within* this structure.

**Related:** [[DSC progressive-disclosure]] (the discipline this specializes),  [[FCT Brief]],  [[FCT Anchor Page]]
**Examples:** [[CAE Minimal Facet\|minimal — short doc, no table]],  [[HBR Architecture\|fuller — non-anchor doc with structured body]]
**Document examples:** [[FEX Manifest]] (facet spec),  [[FEX Retention]] (discipline),  [[FCT Brief]] (facet spec)
**Anchor examples:** [[HBR]] (project),  [[FEX Snapshot]] (skill),  [[FEX Repo]] (repo)

## Overview
[[DSC progressive-disclosure]] is the general discipline — reveal information in layers so a reader gets the gist first and drills in only as far as they need. **Doc Structure** is that discipline applied to a *single document*: a fixed top-to-bottom order of layers, each aimed at a more-committed reader than the last. Every document the system owns — anchor page, facet spec, feature doc, design doc, user guide — follows this skeleton; specific document kinds (e.g. [[FCT Anchor Page]]) refine it but never violate the layer order.

**Cardinality: one per document.** Every authored `.md` file has exactly one Doc Structure — each document follows this top-to-bottom skeleton once. Across an anchor the facet applies to each individual document independently.

## The standard structure (top to bottom)

The fixed order. The top layers are always present; lower layers appear only when the document is big enough to warrant them.

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
- **Anchor file → MUST have a dispatch table** — breadcrumb masthead + member / links zone (per [[FCT Dispatch Table]] / [[FCT Anchor Page]]). **No anchor is ever table-less** (enforced by `R-anchor-page-22`); a leaf / topic anchor still carries breadcrumb + a `...` auto-summary.
- **Non-anchor file → MUST NOT have a dispatch table.** A breadcrumb-masthead dispatch table on a non-anchor document (e.g. a user-story file, a feature doc, a plain content page) is a violation — remove it. Back-links to a parent / sibling belong in a `## Related` / `## See also` section, not a masthead.

**(b) Table of contents table — iff the document is long (more than ~3 pages of content).**
- **Long document (more than ~3 pages) → MUST have a TOC table** — a content-outline table: left column links to the document's own sections (in-document `[[#Heading]]` links), right column says in one line what each section is. A table of contents *with descriptions*.
- **Short document (≲ 3 pages) → MUST NOT have a TOC table** — it adds navigation overhead a reader who can scroll the whole document doesn't need.

**(c) Specialized tables.** Some specialized documents legitimately carry *another kind of table* at the top — e.g. a stories **index** table (`{NAME} Stories.md`), a status board, a glossary. These are neither a dispatch table nor a TOC table; they are the document's content, and rules (a) / (b) do not forbid them.

*(The **TOC / content-outline table** likely deserves its own facet — e.g. `FCT Content Outline` — described inline here for now.)*

### 5. TLDR — *optional; immediately below the table, before any Overview*
A short gist for the reader who has navigated past the table and wants the bottom line before committing to the body. (For a small document with no table, the summary line under the H1 already serves this role — a separate TLDR isn't needed.)

### 6. Overview — *optional `## Overview` H2*
A paragraph, added only when the summary / TLDR isn't enough.

### 7. Body — the document's sections
The actual content the document holds. At the very bottom, the agent-facing `# BRIEF` (per [[FCT Brief]]) when the document needs maintenance notes.

**Why this order — progressive disclosure.** A glance-reader gets what they need from the H1 + summary; a navigator uses the table; a committed reader reads TLDR → Overview → Body; the maintaining agent reads the Brief. Each layer down serves a more-committed reader.

## Relationship to other facets
- **[[DSC progressive-disclosure]]** — the general discipline; this facet is its document-scoped specialization.
- **[[FCT Anchor Page]]** — a specific document kind (the `{slug}.md` anchor page) that refines this skeleton with the dispatch-table form.
- **[[FCT Brief]]** — owns the bottom (agent-facing) layer; its three-reader-zones model seeded this facet.
- **[[FCT Ruleset]] / [[FCT Discussion]]** — other regions that live *within* the Body.

# RULESET R-doc-structure
include::
where:: every authored document — any `.md` the system owns, identified by a leading `# ` H1
description:: the canonical document layering — progressive disclosure for a document

Embedded ruleset for the Doc Structure facet. One compact ordering rule; per-element rules can be split out later if finer-grained auditing is wanted.

### RULE R-doc-structure-01 — Canonical top-to-bottom order (checked)

A document's top is laid out in this fixed order — each element optional unless noted, none out of sequence:

**H1 → summary line → [central figure] → [top table] → [TLDR] → [Overview] → body (→ bottom `# BRIEF`)**

Embedded constraints:
- **H1 (required):** `# {slug} - {Name}` for an anchor page, `# {Name}` otherwise; optionally suffixed ` — {phrase}`.
- **Summary line:** one sentence on the line **immediately after the H1, with no blank line between** — UNLESS the H1 already carries the ` — {phrase}` (one or the other carries the "what this is", not both).
- **Central figure:** optional; if present, sits before the table.
- **Top table (the document table):** governed by two independent rules — `R-doc-structure-02` (dispatch table iff anchor) and `R-doc-structure-03` (TOC table iff long); placed before the first body section. See those rules for the must / must-not conditions.
- **TLDR, then Overview:** optional, in that order, after the table and before the body.

**Check pattern:** line 1 matches `^# `; the line immediately after the H1 is non-blank (the summary) OR the H1 contains ` — `; the document table, when present, sits before the first body `^## `; no element appears out of the order above. (Table presence itself is checked by `R-doc-structure-02` / `-03`.)

**Why:** progressive disclosure — each layer down serves a more-committed reader, and a fixed order means a glance-reader and the audit both know exactly where to look.

### RULE R-doc-structure-02 — Dispatch table iff the document is an anchor (checked)
check:: dispatch_table_iff_anchor

The breadcrumb-masthead **dispatch table** appears on a document **if and only if** that document is an anchor (its file is the `{slug}.md` / anchor file of an anchor folder, marked by a sibling `.anchor` or by being the folder's namesake page).

- **Anchor document → MUST carry a dispatch table** (per [[FCT Dispatch Table]] / [[FCT Anchor Page]]).
- **Non-anchor document → MUST NOT carry a dispatch table.** User-story files, feature docs, individual design docs, and plain content pages are not anchors; a breadcrumb masthead on them is a violation. Parent / sibling back-links belong in a `## Related` or `## See also` section instead.

**Check pattern:** detect a dispatch masthead by `^\| -\[\[.+\]\]- \|` as the first table row. Assert it is present when the file is an anchor file and absent otherwise. Anchor-ness: the file is named `{folder} .md` matching its enclosing folder, or a sibling `.anchor` marker designates it.

**Why:** the dispatch table is the *anchor* navigation surface — breadcrumb up the tree plus the anchor's member links. On a non-anchor it is noise that falsely implies the document roots a subtree, and it pushes the real content below the fold. This is the rule that makes a story file with a masthead (e.g. a `US-<RID>-<N>` file) fail.

### RULE R-doc-structure-03 — TOC table iff the document is long (checked)
check:: toc_table_iff_long

A **table-of-contents table** (content-outline table — left column links the document's own `[[#Heading]]` sections, right column describes each in one line) appears **if and only if** the document runs more than roughly three pages of content.

- **Long document (more than ~3 pages) → MUST carry a TOC table.**
- **Short document (about 3 pages or fewer) → MUST NOT carry a TOC table** — it is navigation overhead for a document a reader can simply scroll.
- **Specialized exception:** a document may carry *another kind of table* at the top (a stories index, a status board, a glossary) that is neither a dispatch table nor a TOC table. Such content tables are permitted regardless of length and are not the subject of this rule.

**Check pattern:** estimate length by content (heading count + body lines as a page proxy). If long, assert a content-outline table (in-document `[[#...]]` links) precedes the first body section. If short, assert no such TOC table is present. A specialized content table (neither dispatch masthead nor in-document-heading TOC) does not count either way.

**Why:** the TOC earns its space only when the document is too long to scan; on a short document it is friction. Tying presence to length keeps every document's top as light as it can be while still navigable.

# BRIEF
- **This is the main / umbrella facet for a document** — it defines the whole top-to-bottom skeleton; the other doc facets (Brief, Discussion, Ruleset) describe regions inside it. It is listed **first** in the [[FCT Doc]] group for that reason.
- **This is the spec for the skeleton**, not an instance — never paste a real document here.
- **Open to confirm:** whether the under-H1 *summary line* (§2) and the below-table *TLDR* (§5) are one element (collapsing for small docs) or two distinct ones. Modeled here as two, collapsing when there's no table.
- **RULESET:** the ordering rule (`R-doc-structure-01`) plus the two document-table rules — `R-doc-structure-02` (dispatch table iff anchor) and `R-doc-structure-03` (TOC table iff long). The two table rules are independent: a doc can have a dispatch table (anchor) and a TOC table (long) at once, or neither (short non-anchor). Specialized content tables (e.g. a stories index) are exempt from both. Rule numbers are monotonic-forever — never recycle.
- **Don't duplicate [[FCT Anchor Page]] or [[FCT Brief]]** — this facet is the *general* layering; those refine or own specific layers. Stay document-scoped (anchor-folder / multi-file structure is [[FCT Folder]] / [[FCT Anchor Tree]]).
