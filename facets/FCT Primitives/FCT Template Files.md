---
description: "file templates — one document's canonical shape"
---
# FCT Template Files
A **file template** — a `_{Name} Template.md` whose body IS a live specimen of one document, defining the canonical shape of each like item in its folder.

| -[[FCT Template Files]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [[FCT Primitives]] → [FCT Template Files](hook://p/FCT%20Template%20Files)<br>: file templates — one document's canonical shape |
| --- | --- |
| Related | [[FCT Template]] (umbrella),  [[FCT Template Folders]],  [[FCT Template Variables]] |
| Examples | [[_Computer Template\|computer record]],   |

## At a glance

A tiny file template — the gist (a fuller worked instance is the FEX example below):

![[FCT Template File Example.svg]]

A file template is a **working specimen**, not a description of one. Its parts:

| Part | What it is |
|---|---|
| **Exemplar** (above the `---`) | live markdown — real H1 `# {{HOSTNAME}}`, real sections, bare `{{UPPER_SNAKE}}` placeholders. **No fences**, so it copies straight into a working record. |
| **Cumulative section** (`# LOG`) | header only at creation — no placeholder entries underneath (R-template-03). |
| **`---` divider** | separates the exemplar (above) from the template's own metadata (below). |
| **`# About this template`** | the clone target (`{Hostname}.md` in the same folder) + one line on *why this is a template, not a facet*: a list of your computers exists in exactly one place, so its shape is local. |
| **`## Variables`** | one bullet per placeholder: what to put **and what to do with no data** — what lets an instantiator finish with **zero** leftover `{{}}` (R-template-02; full spec [[FCT Template Variables]]). |

**Full worked example:** [[_Computer Template]] — a complete file template under `examples/FEX Templates/`. (FEX examples are real markdown files, not figures: they carry their own "About this template" commentary at the bottom, understood as not part of the example, so no figure is needed.)

## What's specific to file templates

- **One document per item.** A file template is right when each member of the set is a single `.md` (one computer = one file). When a member needs *more than one* document, use a [[FCT Template Folders|folder template]] instead.
- **The filename is usually a variable.** `{Hostname}.md` — the clone is named from the item's key. State that in `# About this template`.
- **Location.** A file template lives **in the folder it governs** (the `Computers/` folder holds `_Computer Template.md` plus the real records). It is reached by sitting at the top of that folder (the leading `_` sorts it first); it does **not** earn a dispatch-table row — that obligation is only for [[FCT Template Folders|folder templates]].

## Rules

File templates are governed by the shared `R-template` ruleset on [[FCT Template]] — in particular R-template-01 (live exemplar, no fences), R-template-02 (every placeholder defined), R-template-03 (cumulative sections header-only), R-template-04 (`_{Name} Template.md` naming), and R-template-07 (smoke test). Variable mechanics: [[FCT Template Variables]].

# BRIEF

- **This page is the file-template part of the [[FCT Template]] facet** — a `_{Name} Template.md` defining one document's canonical shape. Sibling: [[FCT Template Folders]]; shared placeholder system: [[FCT Template Variables]].
- **Lead with the live reference example** ([[_Computer Template]] transcluded), then read its parts. Don't fence a markdown exemplar here — it would go inert (R-template-01); transclude the real instance instead.
- **File vs folder decision is load-bearing:** one document per item → file template (here); item needs >1 document → [[FCT Template Folders|folder template]]. Keep that test crisp.
- **Rules live on the umbrella's `R-template`** — don't duplicate the ruleset here; cite it.
