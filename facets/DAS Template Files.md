---
description: "file templates — one document's canonical shape"
---
# DAS Template Files
A **file template** — a `_{Name} Template.md` whose body IS a live specimen of one document, defining the canonical shape of each like item in its folder.

| -[[DAS Template Files]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Template Files](hook://p/DAS%20Template%20Files)<br>: file templates — one document's canonical shape |
| --- | --- |
| Related | [[DAS Template]] (umbrella),  [[DAS Template Folders]],  [[DAS Template Variables]] |
| Examples | [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template\|computer record]],   |
| Rules | [[R-template]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[facets/DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Disciplines Brief]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Plan Dispatch]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS TSK User Guide]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**Cardinality: many** — one `_{Name} Template.md` per templated file kind, each local to the folder/tree it governs.

## Example File Template
A file template is a **working specimen**, not a full description of one.2

![[DAS Template File Example.svg]]


| Part | What it is |
|---|---|
| **Exemplar** (everything *above* the `template notes` cut-line) | live markdown — real H1 `# {{HOSTNAME}}`, real sections, bare placeholders, a cumulative `# LOG` with a `### ...` repeat-marker. **No fences**, so it copies straight into a record. This is the part that becomes the instance. |
| **`✂ ──── template notes ──── ✂`** | the **cut-line** — anchored on the exact phrase `template notes` (≥3 dashes either side, scissors optional). Everything below it is *about the template* and is **removed on clone**. (No bare `---`, no `# About this template` heading — both superseded.) |
| **Conventions** (under the marker) | metadata about the data *as a whole*, **not tied to one variable** — e.g. "list specs in alphabetical order; values are as-of the purchase date." |
| **`## Variables`** | one bullet per placeholder: what to put **and what to do with no data** — what lets an instantiator finish with **zero** leftover `{{}}` (R-template-02; full spec [[DAS Template Variables]]). |

**Full worked example:** [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]] — a complete file template under `examples/FEX Templates/`. (FEX examples are real markdown files, not figures: they carry their own template-notes commentary below the cut-line, understood as not part of the example, so no figure is needed.)

## What's specific to file templates

- **One document per item.** A file template is right when each member of the set is a single `.md` (one computer = one file). When a member needs *more than one* document, use a [[DAS Template Folders|folder template]] instead.
- **The filename is the instance-name pattern.** Strip the `_` and ` Template` from the template's own name and what remains is the clone's name — usually variableized, often composite (`_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md` → `{{PURCHASE_DATE}} {{HOSTNAME}}.md`). A constant middle (`_Computer Template.md`) is wrong — every clone would collide on one name (R-template-04).
- **Location.** A file template lives **in the folder it governs** (the `Computers/` folder holds `_Computer Template.md` plus the real records). It is reached by sitting at the top of that folder (the leading `_` sorts it first); it does **not** earn a dispatch-table row — that obligation is only for [[DAS Template Folders|folder templates]].

## Rules

File templates are governed by the shared `R-template` ruleset on [[DAS Template]] — in particular R-template-01 (live exemplar, no fences), R-template-02 (two placeholder forms; variables defined), R-template-03 (repeating structure = pattern + `### ...`), R-template-04 (`_{pattern} Template.md` naming — the middle is the instance-name pattern), R-template-08 (the `template notes` cut-line), R-template-09 (multi-line = spanning braces), and R-template-07 (smoke test). Variable mechanics: [[DAS Template Variables]].

# BRIEF

*(Maintainer note.)* Part-view of the [[DAS Template]] facet — the model and the `R-template` ruleset live on the umbrella, so edit them there, not here. This page only adds what's **file-specific** (one document per item; no dispatch row, unlike a folder template).
