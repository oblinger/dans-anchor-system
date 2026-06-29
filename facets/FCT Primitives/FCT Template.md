---
description: "the Template facet — a domain-specific, folder-local structure for the items in one folder/tree; the local analog of a facet for shapes too specific to be a global facet. Split into Files / Folders / Variables."
---
# FCT Template
The Template facet — a **domain-specific, folder-local structure**: the shared shape of the items inside one folder or tree, defined right where they live.

| -[[FCT Template]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [[FCT Primitives]] → [FCT Template](hook://p/FCT%20Template)<br>: the Template facet — a domain-specific, folder-local structure for the items in one folder/tree |
| --- | --- |
| Parts | [[FCT Template Files\|Files]],  [[FCT Template Folders\|Folders]],  [[FCT Template Variables\|Variables]],   |
| Related | [[FCT Facet]] (the *global* counterpart),  [[FCT Ruleset]],  [[FCT Dispatch Table]] (the Template row),  [[rewire]] |
| Examples | [[_Computer Template\|file template]],  [[_Disk Template\|folder template]],   |

**TLDR** — A template defines the **shared structure of the items in one folder/tree** — what each computer record, each disk folder, each member of a domain-specific set looks like. It is a `_{Name} Template.md` file or `_{Name} Template/` folder whose body is a **live working specimen** (real H1 / frontmatter / sections, bare `{{PLACEHOLDERS}}`, **no code fences**) plus a Variables section defining each placeholder *and what to do when there's no data*. Three parts: **[[FCT Template Files|Files]]** (file templates), **[[FCT Template Folders|Folders]]** (folder templates), **[[FCT Template Variables|Variables]]** (the `{{…}}` system, shared by both).

## Template vs Facet — local-and-domain-specific vs global-and-type-wide

This is the load-bearing distinction:

| | **Facet** | **Template** |
|---|---|---|
| Scope | **global** — checked into the standard; applies to *every* anchor of a type | **local** — applies to the items in *one* folder/tree |
| Generality | a standardized part *any* anchor of that type carries (Backlog, PRD, Architecture) | a *domain-specific* shape that exists in one place (a `Computers/` folder, a `Disks/` tree) |
| Why it exists | so all anchors of a type are predictable to agent + human | so the items in one folder are predictable, **when the shape is too specific to be a facet** |

The test: *"does this shape recur across many anchors of a type?"* If yes → it's a **[[FCT Facet|facet]]** (or a [[TRT|trait]] if it's a paradigm, not a file). If it lives in **one** folder/tree and no other project would carry it — a list of *your computers*, a tree of *your disks*, the config files of *one idiosyncratic engine you built* — it is **not** a facet; it's a **template**. Templates are how a domain-specific set gets a dependable, declared shape without inflating the global standard.

A template can also serve as the **starting instance** when you create a new item (clone → rename → fill/drop placeholders), but that genesis use is secondary to its primary role: *standardizing the shape of what's already in the folder*.

## Seeding from a type, then specializing

A template need not be hand-built from scratch. When an anchor of a given **type** is created, the type can **seed** a starting template into the new anchor — a sensible default shape pasted in — which the agent or user then **specializes over time** for that project. The local template thus *starts* as the global standard's default and diverges as the project's domain demands; it's the bridge from the global facet/type down to a project-specific shape. The same `_{Name} Template` form is reused this way as **instances throughout the skill hierarchy** — each a local specialization of the shared standard. *(Seeding-on-creation is a wiring detail for the anchor-creation flow, not yet built.)*

## Scope & applicability — where a template governs

A `_{Name} Template` governs the items in **its own folder** (and, by default, the tree beneath it). Detection is by the `_{Name} Template` name (the leading underscore sorts it to the top and marks it meta).

**Reuse beyond one folder (advanced — partly open).** A template is *not* a facet, so it isn't globally checked-in — but a shape may still want reuse across a few places without being promoted to a facet (e.g. the rule files of an idiosyncratic constraint engine used in two projects). Two mechanisms are under consideration; this is **not yet settled**:

- **Hierarchy climb** — a template placed *higher* in the tree governs every folder beneath it; an item looks *up* the tree for the nearest governing `_{Name} Template`.
- **Template alias** — a folder drops a small pointer (a `_{Name} Template` alias) that says "use the template defined over *there*," naming a template elsewhere.

Open question for the design review ([[F220 — Template facet-or-discipline — design review + vault-wide placement sweep|F220]] Q4): which mechanism (or both), and how an item resolves *which* template applies. Until settled, treat a template as governing its own folder/subtree only.

## The three parts

- **[[FCT Template Files]]** — a `_{Name} Template.md` file: one document's canonical shape (a computer record, a meeting note). Opens with a worked example.
- **[[FCT Template Folders]]** — a `_{Name} Template/` folder: the canonical structure of a folder that carries more than one document (a disk folder = main record + manifest). Opens with a worked example.
- **[[FCT Template Variables]]** — the `{{PLACEHOLDER}}` system shared by both: how variables are defined, the no-data rule, and structural-vs-cumulative content.

# RULESET R-template
include::
where:: file: **/_* Template.md, **/_* Template/**
description:: the Template facet — a domain-specific, folder-local structure for the items in one folder/tree

### RULE R-template-01 — the exemplar IS a live instance, never a description (checked)
The content above the `---` divider is **live markdown** — real H1, frontmatter, sections — with bare `{{PLACEHOLDERS}}`; it is **not** wrapped in code fences and is **not** a `## How to use` description of a template.
**Check pattern:** no triple-backtick fence encloses the exemplar; the file is not structured as prose *about* the form. *(Audit category: `template-is-spec`.)*
**Why:** a fenced or described "template" can't be copied into a working instance — wiki-links go inert, tables and headings don't render. A template must BE an entry.

### RULE R-template-02 — every placeholder is defined in a Variables section, with no-data handling (checked)
Each distinct `{{PLACEHOLDER}}` in the exemplar has one bullet in a `## Variables` section stating what to put **and what to do when there is no data** (fill / delete the line / delete the section). Full spec: [[FCT Template Variables]].
**Check pattern:** the set of `{{…}}` tokens in the exemplar equals the set defined under `## Variables`; each definition names the empty-case behavior.
**Why:** without explicit no-data handling, an instantiator leaves empty `{{}}` placeholders — a tooling failure, not an unavoidable artifact.

### RULE R-template-03 — cumulative sections are header-only (checked)
A section whose content accrues after creation (LOG, history) ships with the **header only** — no placeholder entries underneath.
**Check pattern:** no `{{…}}`-bearing entry sits under a cumulative-section header. *(Audit category: `template-has-fake-cumulative-entries`.)*
**Why:** a fake `### {{YYYY-MM-DD}}` entry invites the instantiator to leave it (pollution) or invent a fake event (also pollution); the empty header invites real entries when real events occur.

### RULE R-template-04 — naming is `_{Name} Template` (checked)
File templates are `_{Name} Template.md`; folder templates are `_{Name} Template/` containing `_{Name} Template/_{Name} Template.md`. The leading underscore is structural (sort-to-top + meta marker).
**Check pattern:** the basename matches `^_.+ Template(\.md)?$`; a folder template holds a same-named marker file.
**Why:** the underscore-prefixed, `Template`-suffixed name is how tooling, sort order, and readers recognize a template; a parallel scheme breaks all three.

### RULE R-template-05 — folder templates carry a Template dispatch row (checked)
A folder that contains a `_*/` folder template has a `Template` row in its dispatch table linking the template. Detail: [[FCT Template Folders]].
**Check pattern:** for each folder holding a `_*/` template, its dispatch page contains a `Template` row. *(Audit category: `missing-folder-template-row`; [[rewire]] inserts it.)*
**Why:** the template is the folder's "start here" affordance; without the row it's invisible to anyone working in the folder.

### RULE R-template-06 — every template is reachable (sampled)
A folder-level template is reachable from its folder's dispatch (R-template-05); a reused/elevated template is reachable from the folders it governs (per § Scope & applicability).
**Check pattern:** no `_*` template is unreachable from any dispatch or governed folder. *(Audit category: `orphan-template`.)*
**Why:** an unreachable template is dead meta-content — it can't be found at the moment it matters.

### RULE R-template-07 — the smoke test passes (sampled)
Copying the template, renaming it, and replacing-or-deleting every `{{VARIABLE}}` per the Variables section yields a usable instance: no leftover placeholders, no fake-looking sections.
**Check pattern:** a spot-instantiation leaves zero `{{…}}` tokens and no empty structural sections.
**Why:** the smoke test is the single end-to-end check that the template actually produces conformant instances.

# BRIEF

- **This is the Template facet umbrella** — the concept (a domain-specific, folder-local structure) + the load-bearing **Template-vs-Facet** distinction (local/one-place vs global/type-wide) + the scope/reuse model. Per-part detail lives in the three children: [[FCT Template Files]], [[FCT Template Folders]], [[FCT Template Variables]]. Design rationale: [[F220 — Template facet-or-discipline — design review + vault-wide placement sweep|F220]].
- **Keep the corrected model load-bearing.** A template is NOT cross-anchor and is NOT just "how an item starts." It is the *local* analog of a facet: it standardizes the items of one folder/tree when the shape is too domain-specific to be a global facet (the Computer-folder / Disk-tree / one-off-engine cases). A facet that would only ever exist in one place is a template.
- **The four audit identifiers are load-bearing** — `template-is-spec`, `template-has-fake-cumulative-entries`, `missing-folder-template-row`, `orphan-template` map to R-template-01/03/05/06 and are consumed by [[rewire]] + audit tooling. Don't rename without updating consumers.
- **Examples are real in-repo instances, shown live** (never embedded as a fenced block — a fence makes the example's markdown inert, the exact failure R-template-01 forbids; never an external link — this repo is standalone). The two worked examples are [[_Computer Template]] (file) and [[_Disk Template]] (folder), under `examples/FEX Templates/`.
- **Reuse/scoping (§ Scope & applicability) is unsettled** — the hierarchy-climb vs template-alias mechanisms are recorded as [[F220]] Q4, not yet decided. Don't harden either into a rule until the review settles it.
