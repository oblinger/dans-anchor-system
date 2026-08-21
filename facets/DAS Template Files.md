---
description: "file templates — one document's canonical shape"
group: file
---

| -[[DAS Template Files]]- | → [[DAS]] → [[FCT]] → [DAS Template Files](hook://p/DAS%20Template%20Files)  |
| --- | --- |
| Related | [[DAS Template]] (umbrella),  [[DAS Template Folders]],  [[DAS Template Variables]]  |
| Examples | [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template\|computer record]],   |
| Rules | [[R-template]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS At Entity]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS Subs]],  [[DAS System Design]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Template Files
A **file template** — a `_{Name} Template.md` whose body IS a live specimen of one document, defining the canonical shape of each like item in its folder.

**Cardinality: many** — one `_{Name} Template.md` per templated file kind, each local to the folder/tree it governs.

## Example File Template
A file template is a **working specimen**, not a full description of one.2

![[DAS Template File Example.svg|3000]] 


| Part | What it is |
|---|---|
| **Exemplar** (everything *above* the `template notes` cut-line) | live markdown — real H1 `# {{HOSTNAME}}`, real sections, bare placeholders, a cumulative `# LOG` with a `### ...` repeat-marker. **No fences**, so it copies straight into a record. This is the part that becomes the instance. |
| **`✂ ──── template notes ──── ✂`** | the **cut-line** — anchored on the exact phrase `template notes` (≥3 dashes either side, scissors optional). Everything below it is *about the template* and is **removed on clone**. (No bare `---`, no `# About this template` heading — both superseded.) |
| **Conventions** (under the marker) | metadata about the data *as a whole*, **not tied to one variable** — e.g. "list specs in alphabetical order; values are as-of the purchase date." |
| **`## Variables`** | one bullet per placeholder: what to put **and what to do with no data** — what lets an instantiator finish with **zero** leftover `{{}}` (R-template-02; full spec [[DAS Template Variables]]). |

**Full worked example:** [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]] — a complete file template under `examples/FEX Templates/`. (FEX examples are real markdown files, not figures: they carry their own template-notes commentary below the cut-line, understood as not part of the example, so no figure is needed.)

## What's specific to file templates

- **One document per item.** A file template is right when each member of the set is a single `.md` (one computer = one file). When a member needs *more than one* document, use a [[DAS Template Folders|folder template]] instead.
- **The instance name is declared, not derived from the filename** (reversed 2026-08-20, [[TINK570 - Template identity moves inside the document|F570]]). Below the cut-line a template carries `stencil:: V1.0` — which is what makes it a stencil template at all, and names the [[STEN Language]] grammar it was written against — and `path:: {{PURCHASE_DATE}} {{HOSTNAME}}.md`, naming the file it produces. **The filename is now a human label**: any semantic name, `_` by convention so it sorts to the top, and only the title-case ` Template` suffix required, as a prefilter rather than proof.

  This is the exact reverse of the old rule, and worth stating because the corpus is still full of the old form. `R-template-04` used to require a **variableized** middle and flagged a constant one (`_Computer Template.md`) as a collision risk — which produced names like `_{{DATE}} {{REPORT_TITLE}} Buy Survey Template.md`, unreadable in an `ls` precisely because they were carrying machinery. With the path declared, the collision cannot happen and **the form the old rule flagged is the recommended one**.

  A declared path also expresses what a filename structurally could not: a filename is **one path segment**, so a template could only ever produce a sibling in its own folder. `path:: {{YEAR}}/{{MONTH}}/{{SLUG}}.md` places an instance into a subtree.
- **Location.** A file template lives **in the folder it governs** (the `Computers/` folder holds `_Computer Template.md` plus the real records). It is reached by sitting at the top of that folder (the leading `_` sorts it first); it does **not** earn a dispatch-table row — that obligation is only for [[DAS Template Folders|folder templates]]. Location is also what sets the template's **scope**, per [[DAS Template]] § Scope: a template higher up the ladder (a facet home, a trait home, the packaged root) governs correspondingly further, and the nearest one to an item wins.
- **The anchor is the first line, and the default is the whole file.** A specimen opening with an ordinary `# H1` anchors at the document root and governs everything. A specimen opening with a **depth marker** anchors instead at any heading whose text matches it, and governs only the subtree beneath — see [[DAS Template]] § Anchor for the model. Nothing existing changes: whole-file is the default and carries no marker.

  Two file templates may govern the same document when their anchors are **disjoint** — one at the root, one at `LOG` — and neither names the other. Where a template's anchor sits *inside* another's, the outer one shows the heading and **nothing beneath it**: that absence is deliberate, and half an example there is a defect, because it would contradict the spec that actually owns the region.

  The optional `_{Name} Section Template.md` spelling is **readability only**, not mechanism. It keeps such a template inside the `_* Template` family `R-template` selects on and tells a human scanning `ls` what they are looking at. **If the name and the first line ever disagree, the form wins and the name is the defect** — the same precedence that makes every other property of a template positional.

## Rules

File templates are governed by the shared `R-template` ruleset on [[DAS Template]] — in particular R-template-01 (live exemplar, no fences), R-template-02 (two placeholder forms; variables defined), R-template-03 (repeating structure = pattern + `### ...`), R-template-04 (`_{pattern} Template.md` naming — the middle is the instance-name pattern), R-template-08 (the `template notes` cut-line), R-template-09 (multi-line = spanning braces), and R-template-07 (smoke test). Variable mechanics: [[DAS Template Variables]].

# BRIEF

*(Maintainer note.)* Part-view of the [[DAS Template]] facet — the model and the `R-template` ruleset live on the umbrella, so edit them there, not here. This page only adds what's **file-specific** (one document per item; no dispatch row, unlike a folder template).
