---
description: "folder templates — a folder's canonical multi-doc structure"
group: folder
---

| -[[DAS Template Folders]]- | → [[DAS]] → [[FCT]] → [DAS Template Folders](hook://p/DAS%20Template%20Folders)  |
| --- | --- |
| Related | [[DAS Template]] (umbrella),  [[DAS Template Files]],  [[DAS Template Variables]],  [[DAS Dispatch Table]] (Template row) |
| Examples | [[_{{DISK_LABEL}} Template\|disk folder]],   |
| Rules | [[R-template]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS At Entity]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS Subs]],  [[DAS System Design]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Template Folders
A **folder template** — a `_{Name} Template/` folder whose marker + skeleton define the canonical structure of a folder that carries more than one document per item.

**Cardinality: many** — one `_{Name} Template/` per templated folder kind, local to its tree.

## At a glance

A tiny folder template — the gist (a fuller worked instance is the FEX example below):

![[DAS Template Folder Example.svg|3000]] 

A folder template is a `_{Name} Template/` **folder**, not a single file. Its parts:

| Part | What it is |
|---|---|
| **The folder** (`_{Name} Template/`) | cloned as a unit → `{Item}/`. Use when one item needs **more than one** document. |
| **The marker** (`_{Name} Template/_{Name} Template.md`) | same name, inside the folder; its body is the live exemplar of the folder's *main* document — same anatomy as a [[DAS Template Files\|file template]]. |
| **Skeleton** (optional) | other starter files the folder always contains. In the example the manifest is *named* but added later, so the template ships only the marker. |
| **`✂ … template notes … ✂`** | the cut-line; below it, the template notes say *why a folder and not a file* (the item needs >1 document) and define the **unified variable** shared by the folder name, the marker, and the sibling members (R-template-10). |

**Full worked example:** [[_{{DISK_LABEL}} Template]] — a complete folder template under `examples/FEX Templates/`: a variableized folder name, a marker + a `{{DISK_LABEL}} Manifest.md` member, all sharing the unified `{{DISK_LABEL}}`.

## What's specific to folder templates

- **Use when an item needs >1 document.** One disk = a folder (record + manifest); one computer = a single file ([[DAS Template Files|file template]]). That is the file-vs-folder decision.
- **Cloned as a unit.** Copy the whole `_{Name} Template/` folder → `{Item}/`, rename the marker to `{Item}.md`, fill/drop placeholders, add skeleton docs as they're produced.
- **Earns a dispatch row.** Because a folder template sits *inside* the folder being templated, the folder's [[DAS Dispatch Table|dispatch]] carries a **`Template`** row at the top of the auto-managed zone (left cell `Template`, right cell `~~[[_{Name} Template]]~~`). [[rewire]] recognizes `_*/` folders and inserts the row when missing (audit category `missing-folder-template-row`). This is the one obligation file templates do *not* have.
- **Its anchor is a directory, and that is the whole of it.** A folder template is the one kind whose anchor needs no reading — a directory anchors at a directory and governs its contents ([[DAS Template]] § Anchor). The depth-marker question does not arise: it is what distinguishes a *document* template that governs a whole file from one that governs a heading's subtree, and a folder template is neither. What *does* apply is the scope ladder ([[DAS Template]] § Scope): a folder template placed in a facet home, a trait home, or the packaged root reaches every anchor at that rung, with the nearest template to an item winning.
- **The dispatch-row obligation follows the folder, not the rung.** A folder template hoisted up the ladder still carries its row in whatever folder it sits in — the row exists because the template is *inside* something, which stays true wherever it lives.

## Rules

Folder templates are governed by the shared `R-template` ruleset on [[DAS Template]] — especially R-template-04 (the `_{Name} Template/` folder holds a same-named marker), R-template-05 (the `Template` dispatch row), and R-template-06 (reachability). The marker's own body obeys the same exemplar/variables rules as a file template. Variable mechanics: [[DAS Template Variables]].

# BRIEF

*(Maintainer note.)* Part-view of the [[DAS Template]] facet — the model and the `R-template` ruleset live on the umbrella, so edit them there, not here. This page only adds what's **folder-specific**: the in-folder same-named marker (R-template-04) and the `Template` dispatch row file templates lack (R-template-05, inserted by [[rewire]]).
