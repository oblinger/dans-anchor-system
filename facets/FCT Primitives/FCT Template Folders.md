---
description: "folder templates — a folder's canonical multi-doc structure"
---
# FCT Template Folders
A **folder template** — a `_{Name} Template/` folder whose marker + skeleton define the canonical structure of a folder that carries more than one document per item.

| -[[FCT Template Folders]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[Skill Agent]] → [ob-skills](hook://ob-skills) → [[facets]] → [[FCT Primitives]] → [FCT Template Folders](hook://p/FCT%20Template%20Folders)<br>: folder templates — a folder's canonical multi-doc structure |
| --- | --- |
| Related | [[FCT Template]] (umbrella),  [[FCT Template Files]],  [[FCT Template Variables]],  [[FCT Dispatch Table]] (the Template row) |
| Examples | [[_Disk Template\|disk folder]],   |

## At a glance

A tiny folder template — the gist (a fuller worked instance is the FEX example below):

![[FCT Template Folder Example.svg]]

A folder template is a `_{Name} Template/` **folder**, not a single file. Its parts:

| Part | What it is |
|---|---|
| **The folder** (`_{Name} Template/`) | cloned as a unit → `{Item}/`. Use when one item needs **more than one** document. |
| **The marker** (`_{Name} Template/_{Name} Template.md`) | same name, inside the folder; its body is the live exemplar of the folder's *main* document — same anatomy as a [[FCT Template Files|file template]]. |
| **Skeleton** (optional) | other starter files the folder always contains. In the example the manifest is *named* but added later, so the template ships only the marker. |
| **`# About this template`** | one line on *why a folder and not a file*: the item needs >1 document, so it gets its own folder. |

**Full worked example:** [[_Disk Template]] — a complete folder template under `examples/FEX Templates/` (a real markdown marker, with its commentary at the bottom).

## What's specific to folder templates

- **Use when an item needs >1 document.** One disk = a folder (record + manifest); one computer = a single file ([[FCT Template Files|file template]]). That is the file-vs-folder decision.
- **Cloned as a unit.** Copy the whole `_{Name} Template/` folder → `{Item}/`, rename the marker to `{Item}.md`, fill/drop placeholders, add skeleton docs as they're produced.
- **Earns a dispatch row.** Because a folder template sits *inside* the folder being templated, the folder's [[FCT Dispatch Table|dispatch]] carries a **`Template`** row at the top of the auto-managed zone (left cell `Template`, right cell `[[_{Name} Template]]`). [[rewire]] recognizes `_*/` folders and inserts the row when missing (audit category `missing-folder-template-row`). This is the one obligation file templates do *not* have.

## Rules

Folder templates are governed by the shared `R-template` ruleset on [[FCT Template]] — especially R-template-04 (the `_{Name} Template/` folder holds a same-named marker), R-template-05 (the `Template` dispatch row), and R-template-06 (reachability). The marker's own body obeys the same exemplar/variables rules as a file template. Variable mechanics: [[FCT Template Variables]].

# BRIEF

*(Maintainer note.)* Part-view of the [[FCT Template]] facet — the model and the `R-template` ruleset live on the umbrella, so edit them there, not here. This page only adds what's **folder-specific**: the in-folder same-named marker (R-template-04) and the `Template` dispatch row file templates lack (R-template-05, inserted by [[rewire]]).
