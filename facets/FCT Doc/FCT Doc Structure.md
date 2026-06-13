---
description: "the Doc Structure facet — the canonical top-to-bottom layering every document follows (progressive disclosure specialized for a single document)"
---

# FCT Doc Structure
The standard top-to-bottom structure every document follows — progressive disclosure specialized for a single document: each layer reveals more depth for a more-committed reader. This is the **main facet for any document**; the other doc facets (Brief, Discussion, Ruleset) describe regions *within* this structure.

| -[[FCT Doc Structure]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Doc]] → [FCT Doc Structure](hook://p/FCT%20Doc%20Structure)<br>: the canonical document layering — progressive disclosure for a document |
| --- | --- |
| Related | [[DSC progressive-disclosure]] (the discipline this specializes),  [[FCT Brief]],  [[FCT Anchor Page]] |
| Document examples | [[FEX Manifest]] (facet spec),  [[FEX Retention]] (discipline),  [[FCT Brief]] (facet spec) |
| Anchor examples | [[HBR]] (project),  [[FEX Snapshot]] (skill),  [[FEX Repo]] (repo) |

## Overview
[[DSC progressive-disclosure]] is the general discipline — reveal information in layers so a reader gets the gist first and drills in only as far as they need. **Doc Structure** is that discipline applied to a *single document*: a fixed top-to-bottom order of layers, each aimed at a more-committed reader than the last. Every document the system owns — anchor page, facet spec, feature doc, design doc, user guide — follows this skeleton; specific document kinds (e.g. [[FCT Anchor Page]]) refine it but never violate the layer order.

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

### 4. Top table — **required once the document runs more than ~3 pages of content**
The **top table** is the document's progressive-disclosure entry point — the navigation surface a reader hits right after the H1 / summary. **One rule picks the form:**

> **Is this an anchor file? → dispatch table. If not → content outline table.**

- **Anchor file → dispatch table** — breadcrumb masthead + member / links zone (per [[DSC Dispatch Table]] / [[FCT Anchor Page]]).
- **Non-anchor file → content outline table** — left column links to the document's own sections (in-document `[[#Heading]]` links); right column says, in one line, what each section is. A table of contents *with descriptions*.
- **Short docs (≲ 3 pages) → no top table needed.**

*(The **content outline table** likely deserves its own facet — e.g. `FCT Content Outline` — described inline here for now.)*

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
description:: The canonical top-to-bottom information order for a document (progressive disclosure). The audit reads this one rule and walks the document top-down to check its structure.

Embedded ruleset for the Doc Structure facet. One compact ordering rule; per-element rules can be split out later if finer-grained auditing is wanted.

### RULE R-doc-structure-01 — Canonical top-to-bottom order (checked)

A document's top is laid out in this fixed order — each element optional unless noted, none out of sequence:

**H1 → summary line → [central figure] → [top table] → [TLDR] → [Overview] → body (→ bottom `# BRIEF`)**

Embedded constraints:
- **H1 (required):** `# {slug} - {Name}` for an anchor page, `# {Name}` otherwise; optionally suffixed ` — {phrase}`.
- **Summary line:** one sentence on the line **immediately after the H1, with no blank line between** — UNLESS the H1 already carries the ` — {phrase}` (one or the other carries the "what this is", not both).
- **Central figure:** optional; if present, sits before the table.
- **Top table:** **required once the document runs more than ~3 pages of content** — one rule: **anchor file → dispatch table; non-anchor file → content outline table** (left column = in-document `[[#Heading]]` links, right column = one-line description of each section); placed before the first body section.
- **TLDR, then Overview:** optional, in that order, after the table and before the body.

**Check pattern:** line 1 matches `^# `; the line immediately after the H1 is non-blank (the summary) OR the H1 contains ` — `; count `^## ` headings — if > 3, a table appears before the first body `^## ` (dispatch masthead `^\| -\[\[.+\]\]- \|` for an anchor page, else any `^\|.*\|` outline table); no element appears out of the order above.

**Why:** progressive disclosure — each layer down serves a more-committed reader, and a fixed order means a glance-reader and the audit both know exactly where to look.

# BRIEF
- **This is the main / umbrella facet for a document** — it defines the whole top-to-bottom skeleton; the other doc facets (Brief, Discussion, Ruleset) describe regions inside it. It is listed **first** in the [[FCT Doc]] group for that reason.
- **This is the spec for the skeleton**, not an instance — never paste a real document here.
- **Open to confirm:** whether the under-H1 *summary line* (§2) and the below-table *TLDR* (§5) are one element (collapsing for small docs) or two distinct ones. Modeled here as two, collapsing when there's no table.
- **RULESET:** one compact ordering rule (`R-doc-structure-01`) — the audit reads it and walks the document top-down. Split into per-element rules later only if finer-grained auditing is wanted.
- **Don't duplicate [[FCT Anchor Page]] or [[FCT Brief]]** — this facet is the *general* layering; those refine or own specific layers. Stay document-scoped (anchor-folder / multi-file structure is [[FCT Folder]] / [[FCT Anchor Tree]]).
