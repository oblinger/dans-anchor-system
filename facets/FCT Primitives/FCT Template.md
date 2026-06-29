---
description: "the Template facet — the standardized starting instance of a doc or folder; a `_{Name} Template` artifact that IS a live exemplar (bare `{{PLACEHOLDERS}}`, no fences) plus a Variables section telling the instantiator how to fill or drop each one"
---
# FCT Template
The Template facet — the standardized **starting instance** of a doc or folder: a `_{Name} Template` artifact that *is* a live exemplar of the form it teaches, plus a Variables section telling the instantiator how to fill or drop each placeholder.

| -[[FCT Template]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [[FCT Primitives]] → [FCT Template](hook://p/FCT%20Template)<br>: the Template facet — the standardized starting instance of a doc or folder |
| --- | --- |
| Anchor | [[FCT Primitives]] (parent) |
| Related | [[FCT Facet]] (the spec a template materializes),  [[FCT Ruleset]],  [[FCT Dispatch Table]] (the Template row),  [[rewire]] (inserts the row),  [[FCT Anchor Page]] |
| Examples | [[_PHUNT Template\|file template — with cumulative-section handling]],  [[_Corp Template\|folder template]],   |

**TLDR** — **Cardinality: many; cross-anchor.** A template is the **genesis companion** to a [[FCT Facet|facet]] spec: the spec says what an artifact *is at rest*, the template says what it *starts as*. It is a `_{Name} Template.md` file or `_{Name} Template/` folder whose body is a **live working specimen** — real H1 / frontmatter / sections, with bare `{{UPPER_SNAKE}}` placeholders where live data goes and **no code fences** — followed by a **Variables** section that defines each placeholder *and what to do when there is no data*, so the instantiator honestly deletes an empty placeholder rather than leaving it. Smoke test: copy → rename → replace-or-delete every `{{VARIABLE}}` → a usable entry with no leftover placeholders and no fake sections.

## What it is

A **template** is the standardized starting instance of a doc or folder. It exists so that creating a new instance of some facet — a Backlog, a feature doc, a person record, a research-report folder — reliably *starts in the standard shape* instead of being re-derived by hand each time.

This is the **genesis half** of what the anchor standard promises. A [[FCT Facet|facet spec]] standardizes an artifact's *at-rest shape* ("what a conformant X looks like"); a template standardizes that artifact's *creation-time shape* ("how a new X reliably starts conformant"). The template is the **executable starting-point of the spec** — the bridge between the abstract facet spec and the concrete instance. Where a flow reproduces a doc skeleton by hand (the way `/feature` rebuilds the feature-doc shape each time), that skeleton is a *de facto* template that was never materialized; the Template facet is how it becomes a *declared, dependable* one.

A template **is** an instance of the form it teaches — not a description of the form, not a meta-doc *about* it. The rendered content of the file is a working specimen.

## How it's detected

**File or folder existence**, keyed on the `_{Name} Template` name (leading underscore sorts it to the top of the listing and marks it as meta-content):

- a **`_{Name} Template.md`** file, or
- a **`_{Name} Template/`** folder containing a marker `_{Name} Template/_{Name} Template.md` plus optional skeleton files.

**Cardinality: many**, and **cross-anchor** — unlike a one-per-anchor facet (Backlog, PRD), templates recur wherever a doc or folder kind is instantiated. This breadth is why Template is a *reflexive* facet (its instances template *other* facets and folders), sitting with the other reflexive primitives [[FCT Facet]] and [[FCT Ruleset]] under [[FCT Primitives]] — but it is still a facet by the system's test: a concrete artifact you **build and audit**, not a way of thinking.

## Anatomy — three parts

A template artifact has three parts, top to bottom:

1. **Exemplar** — live markdown above the `---` divider. Same H1, frontmatter, sections, and tables as a real entry, with **bare `{{UPPER_SNAKE_CASE}}` placeholders** for the fields to fill. **No code fences around the exemplar** — fences make wiki-links inert, render tables as plain text, and hide headings from the outline, so a fenced "template" cannot be copied into a working instance.
2. **About this template** — a short paragraph below the divider: the naming pattern for cloned instances and any non-obvious structural rules.
3. **Variables** — one bullet per `{{PLACEHOLDER}}` in the exemplar, stating what to put **and, critically, what to do when there is no data**. This is the load-bearing addition: it lets an LLM or human instantiator *honestly delete* a placeholder rather than leave it in or invent fake content.

A full live specimen of each part is in the linked Examples (rather than fenced here, which would make the example's own markdown inert — the exact failure this facet forbids).

## Empty-at-creation vs structural placeholders

Two kinds of content need different treatment:

| Kind | Example | Treatment |
|---|---|---|
| **Structural placeholder** — the form genuinely has this content at creation (the instantiator HAS the data) | a paper's title + abstract; a comparison table's rows | keep as `{{VARIABLE}}`; define each in Variables. |
| **Cumulative section** — content accrues *after* creation, not at it | an interaction log; a change history; recurring meeting notes | **header only** (e.g. `# LOG`); no placeholder entries underneath. |

Forcing a fake entry into a cumulative section (shipping `### {{YYYY-MM-DD}}  {{Topic}}` under a `# LOG`) invites the instantiator to either leave it (polluting the entry) or invent a fake event (also polluting). Empty header → real entries get added when real events happen.

## Two kinds — file and folder

| Kind | Form | Use |
|---|---|---|
| **File template** | `_{Name} Template.md` | canonical starting content for a new markdown document. |
| **Folder template** | `_{Name} Template/` | canonical starting structure for a new folder; contains the marker `_{Name} Template/_{Name} Template.md` plus optional skeleton files. |

## Naming

Always **`_{Name} Template`** — file with `.md`, folder without extension. The leading underscore sorts the template to the top of its folder and marks it as meta-content; `{Name}` is the entity or folder the template describes (`_PRD Template.md`, `_Corp Template/`, `_PHUNT Template.md`).

## Two locations

| Location | What lives there | Dispatch row? |
|---|---|---|
| **Central library** — a vault-wide `Templates/` area, or alongside the facet spec it materializes | generic templates: one starter per facet or doc shape. Looked up by name. | **No** — reached by name; it would clutter every dispatch table. |
| **Inline** — inside the folder being templated | folder-specific templates (corp folders under `Corp/`, experiments under `experiments/`, …). | **Yes** — the folder's own dispatch links its template. |

**Only folder-level templates earn a dispatch-row link.** Generic vault-wide templates are reached by name.

## Dispatch-table integration

When a folder contains a `_*/` folder template, the folder's [[FCT Dispatch Table|dispatch]] carries a **`Template`** row at the top of the auto-managed zone (left cell `Template`, right cell the `[[_{Name} Template]]` link). [[rewire]] recognizes `_*/` folders and inserts the row when missing.

## Relationship to the facet it templates

A template **materializes a facet's creation-time contract**: a facet spec MAY declare its canonical template, and that template is the standardized first instance of the facet. The pairing is **opt-in** — a facet *may* carry a template, not *must* — so simple anchors take on no template weight, and the standard stays small (one uniform Template concept replacing N hand-reproduced skeletons).

# RULESET R-template
include::
where:: file: **/_* Template.md, **/_* Template/**
description:: the Template facet — the standardized starting instance of a doc or folder

### RULE R-template-01 — the exemplar IS a live instance, never a description (checked)
The content above the `---` divider is **live markdown** — real H1, frontmatter, sections — with bare `{{PLACEHOLDERS}}`; it is **not** wrapped in code fences and is **not** a `## How to use` / `## Canonical entry shape` description of a template.
**Check pattern:** no triple-backtick fence encloses the exemplar; the file is not structured as a prose description of the form. *(Audit category: `template-is-spec`.)*
**Why:** a fenced or described "template" can't be copied into a working instance — wiki-links go inert, tables and headings don't render. A template must BE an entry.

### RULE R-template-02 — every placeholder is defined in a Variables section, with no-data handling (checked)
Each distinct `{{PLACEHOLDER}}` in the exemplar has one bullet in a `## Variables` section stating what to put **and what to do when there is no data** (fill / delete the line / delete the section).
**Check pattern:** the set of `{{…}}` tokens in the exemplar equals the set defined under `## Variables`; each definition names the empty-case behavior.
**Why:** without explicit no-data handling, an instantiator leaves empty `{{}}` placeholders — a tooling failure, not an unavoidable artifact.

### RULE R-template-03 — cumulative sections are header-only (checked)
A section whose content accrues after creation (LOG, history, recurring notes) ships with the **header only** — no placeholder entries underneath.
**Check pattern:** no `{{…}}`-bearing entry sits under a cumulative-section header. *(Audit category: `template-has-fake-cumulative-entries`.)*
**Why:** a fake `### {{YYYY-MM-DD}}` entry invites the instantiator to leave it (pollution) or invent a fake event (also pollution); the empty header invites real entries when real events occur.

### RULE R-template-04 — naming is `_{Name} Template` (checked)
File templates are `_{Name} Template.md`; folder templates are `_{Name} Template/` containing `_{Name} Template/_{Name} Template.md`. The leading underscore is structural (sort-to-top + meta marker).
**Check pattern:** the basename matches `^_.+ Template(\.md)?$`; a folder template holds a same-named marker file.
**Why:** the underscore-prefixed, `Template`-suffixed name is how tooling, sort order, and readers recognize a template; a parallel naming scheme breaks all three.

### RULE R-template-05 — folder templates carry a Template dispatch row (checked)
A folder that contains a `_*/` folder template has a `Template` row in its dispatch table linking the template.
**Check pattern:** for each folder holding a `_*/` template, its dispatch page contains a `Template` row. *(Audit category: `missing-folder-template-row`; [[rewire]] inserts it.)*
**Why:** the template is the folder's "start here" affordance; without the row it's invisible to anyone working in the folder.

### RULE R-template-06 — every template is reachable (sampled)
A folder-level template is reachable from its folder's dispatch (R-template-05); a generic template is reachable by name from the central `Templates/` area.
**Check pattern:** no `_*` template is unreachable from any dispatch or the central library index. *(Audit category: `orphan-template`.)*
**Why:** an unreachable template is dead meta-content — it can't be found at the moment of creation, which is the only moment it matters.

### RULE R-template-07 — the smoke test passes (sampled)
Copying the template, renaming it, and replacing-or-deleting every `{{VARIABLE}}` per the Variables section yields a usable instance: no leftover placeholders, no fake-looking sections.
**Check pattern:** a spot-instantiation leaves zero `{{…}}` tokens and no empty structural sections.
**Why:** the smoke test is the single end-to-end check that the template actually produces conformant instances — the whole point of the facet.

# BRIEF

- **This is the Template facet definition** — the spec for what a `_{Name} Template` artifact IS (a starter instance) and how to validate it. It folds the legacy [[CAB Template]] convention into the FCT frame; sibling to [[FCT Facet]] and [[FCT Ruleset]] under [[FCT Primitives]]; the design rationale (facet-vs-discipline, belongs-in-the-anchor-standard) is recorded in [[F220 — Template facet-or-discipline — design review + vault-wide placement sweep|F220]].
- **A template is the genesis companion to a facet spec** — facet spec = at-rest shape; template = creation-time shape. Keep this framing load-bearing: it is *why* Template belongs in the anchor standard (the standardization promise has a genesis half), and *why* it's a facet (a concrete build-and-audit artifact), not a discipline.
- **Don't embed a fenced markdown exemplar in this spec.** A fenced template makes its own markdown inert — the exact failure R-template-01 forbids. Show anatomy in prose; link a **live** instance in the Examples row. (This spec may fence *non-markdown* illustration only.)
- **The four audit identifiers are load-bearing** — `template-is-spec`, `template-has-fake-cumulative-entries`, `missing-folder-template-row`, `orphan-template` are consumed by [[rewire]] and audit tooling; they map to R-template-01/03/05/06. Don't rename without updating consumers.
- **Two load-bearing rules not to relax:** the `_{Name} Template` naming (sort-to-top + meta marker), and the two-locations rule (only *folder* templates earn a dispatch row; generic templates are reached by name — broadening the row obligation pollutes every dispatch).
- **Examples are real instances, never embedded** (per [[FCT Facet]] R-facet-spec-20/-25): the row spans the two kinds — a **file** template ([[_PHUNT Template]], showing cumulative-section handling) and a **folder** template ([[_Corp Template]]). The in-repo [[CAE]] world also carries a feature-doc file template (`CAE Features/_template.md`) usable as a worked example.
- **Cardinality is many + cross-anchor**, and Template is **reflexive** (it templates other facets/folders) — keep it among the [[FCT Primitives]] reflexive kinds, not in a per-area facet group.
