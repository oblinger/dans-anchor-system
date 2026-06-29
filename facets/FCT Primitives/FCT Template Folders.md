---
description: "folder templates — a folder's canonical multi-doc structure"
---
# FCT Template Folders
A **folder template** — a `_{Name} Template/` folder whose marker + skeleton define the canonical structure of a folder that carries more than one document per item.

| -[[FCT Template Folders]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [[FCT Primitives]] → [FCT Template Folders](hook://p/FCT%20Template%20Folders)<br>: folder templates — a folder's canonical multi-doc structure |
| --- | --- |
| Related | [[FCT Template]] (umbrella),  [[FCT Template Files]],  [[FCT Template Variables]],  [[FCT Dispatch Table]] (the Template row) |
| Examples | [[_Disk Template\|disk folder]],   |

## Reference example

A folder template for a *disk* — each disk is a folder because it carries more than one document (a main record **plus** a generated manifest). The marker doc, shown live:

![[_Disk Template]]

## Reading the example

A folder template is a `_{Name} Template/` **folder**, not a single file. Its parts:

- **The marker — `_{Name} Template/_{Name} Template.md`.** Same name as the folder, inside it. Its body is the live exemplar of the folder's *main* document (here, the disk's record) — same anatomy as a [[FCT Template Files|file template]] (exemplar above `---`, About, Variables).
- **The skeleton (optional).** Other starter files the folder should contain. In the example the manifest is *named* in `# About this template` but added later — so the template ships only the marker; a skeleton file would be included literally when the folder always starts with it.
- **`# About this template`** says *why a folder and not a file*: the item needs more than one document, so it gets its own folder.

## What's specific to folder templates

- **Use when an item needs >1 document.** One disk = a folder (record + manifest); one computer = a single file ([[FCT Template Files|file template]]). That is the file-vs-folder decision.
- **Cloned as a unit.** Copy the whole `_{Name} Template/` folder → `{Item}/`, rename the marker to `{Item}.md`, fill/drop placeholders, add skeleton docs as they're produced.
- **Earns a dispatch row.** Because a folder template sits *inside* the folder being templated, the folder's [[FCT Dispatch Table|dispatch]] carries a **`Template`** row at the top of the auto-managed zone (left cell `Template`, right cell `[[_{Name} Template]]`). [[rewire]] recognizes `_*/` folders and inserts the row when missing (audit category `missing-folder-template-row`). This is the one obligation file templates do *not* have.

## Rules

Folder templates are governed by the shared `R-template` ruleset on [[FCT Template]] — especially R-template-04 (the `_{Name} Template/` folder holds a same-named marker), R-template-05 (the `Template` dispatch row), and R-template-06 (reachability). The marker's own body obeys the same exemplar/variables rules as a file template. Variable mechanics: [[FCT Template Variables]].

# BRIEF

- **This page is the folder-template part of the [[FCT Template]] facet** — a `_{Name} Template/` folder (marker + optional skeleton). Sibling: [[FCT Template Files]]; shared placeholder system: [[FCT Template Variables]].
- **Lead with the live reference example** ([[_Disk Template]] transcluded). Don't fence the exemplar (R-template-01); transclude the real instance.
- **The two folder-specific load-bearing facts:** the same-named marker inside the folder (R-template-04), and the `Template` dispatch row that file templates don't have (R-template-05, inserted by [[rewire]]). Keep both crisp.
- **File-vs-folder test:** >1 document per item → folder template (here); one document → [[FCT Template Files|file template]].
- **Rules live on the umbrella's `R-template`** — cite, don't duplicate.
