---
description: "file templates — one document's canonical shape"
---
# FCT Template Files
A **file template** — a `_{Name} Template.md` whose body IS a live specimen of one document, defining the canonical shape of each like item in its folder.

| -[[FCT Template Files]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[Skill Agent]] → [ob-skills](hook://ob-skills) → [[facets]] → [[FCT Primitives]] → [FCT Template Files](hook://p/FCT%20Template%20Files)<br>: file templates — one document's canonical shape |
| --- | --- |
| Related | [[FCT Template]] (umbrella),  [[FCT Template Folders]],  [[FCT Template Variables]] |
| Examples | [[_Computer Template\|computer record]],   |

## Example File Template
A file template is a **working specimen**, not a full description of one.

![[FCT Template File Example.svg]]


| Part | What it is |
|---|---|
| **Exemplar** (everything *above* `# About this template`) | live markdown — real H1 `# {{HOSTNAME}}`, real sections, bare `{{UPPER_SNAKE}}` placeholders, an empty cumulative `# LOG`. **No fences**, so it copies straight into a record. This is the part that becomes the instance. |
| **`# About this template`** | the **unambiguous end-of-exemplar marker** — a reserved H1 a real record would never contain. Everything from here down is *about the template* and is **discarded on clone**. (No bare `---` divider — that's ambiguous with frontmatter and horizontal rules.) |
| **Conventions** (under the marker) | metadata about the data *as a whole*, **not tied to one variable** — e.g. "list specs in alphabetical order; values are as-of the purchase date." |
| **`## Variables`** | one bullet per placeholder: what to put **and what to do with no data** — what lets an instantiator finish with **zero** leftover `{{}}` (R-template-02; full spec [[FCT Template Variables]]). |

**Full worked example:** [[_Computer Template]] — a complete file template under `examples/FEX Templates/`. (FEX examples are real markdown files, not figures: they carry their own "About this template" commentary at the bottom, understood as not part of the example, so no figure is needed.)

## What's specific to file templates

- **One document per item.** A file template is right when each member of the set is a single `.md` (one computer = one file). When a member needs *more than one* document, use a [[FCT Template Folders|folder template]] instead.
- **The filename is usually a variable.** `{Hostname}.md` — the clone is named from the item's key. State that in `# About this template`.
- **Location.** A file template lives **in the folder it governs** (the `Computers/` folder holds `_Computer Template.md` plus the real records). It is reached by sitting at the top of that folder (the leading `_` sorts it first); it does **not** earn a dispatch-table row — that obligation is only for [[FCT Template Folders|folder templates]].

## Rules

File templates are governed by the shared `R-template` ruleset on [[FCT Template]] — in particular R-template-01 (live exemplar, no fences), R-template-02 (every placeholder defined), R-template-03 (cumulative sections header-only), R-template-04 (`_{Name} Template.md` naming), and R-template-07 (smoke test). Variable mechanics: [[FCT Template Variables]].

# BRIEF

*(Maintainer note.)* Part-view of the [[FCT Template]] facet — the model and the `R-template` ruleset live on the umbrella, so edit them there, not here. This page only adds what's **file-specific** (one document per item; no dispatch row, unlike a folder template).
