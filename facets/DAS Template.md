---
description: "the Template facet — a domain-specific, folder-local structure for the items in one folder/tree"
---
# DAS Template
The Template facet — a **domain-specific, folder-local structure**: the shared shape of the items inside one folder or tree, defined right where they live.

| -[[DAS Template]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Template](hook://p/DAS%20Template) |
| --- | --- |
| Parts | [[DAS Template Files\|Files]],  [[DAS Template Folders\|Folders]],  [[DAS Template Variables\|Variables]],   |
| Related | [[DAS Facet]] (the *global* counterpart),  [[DAS Ruleset]],  [[DAS Dispatch Table]] (the Template row),  [[rewire]] |
| Rules | [[R-template]],   |
| Examples | [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template\|file template]],  [[_{{DISK_LABEL}} Template\|folder template]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**Cardinality: many** — any folder/tree may declare its own template; each is folder-local.

**TLDR** — A template defines the **shared structure of the items in one folder/tree** — what each computer record, each disk folder, each member of a domain-specific set looks like. It is a `_{Name} Template.md` file or `_{Name} Template/` folder whose body is a **live working specimen** (real H1 / frontmatter / sections, bare `{{PLACEHOLDERS}}`, **no code fences**) plus a Variables section defining each placeholder *and what to do when there's no data*. Three parts: **[[DAS Template Files|Files]]** (file templates), **[[DAS Template Folders|Folders]]** (folder templates), **[[DAS Template Variables|Variables]]** (the `{{…}}` system, shared by both).

## Template vs Facet — local-and-domain-specific vs global-and-type-wide

This is the load-bearing distinction:

| | **Facet** | **Template** |
|---|---|---|
| Scope | **global** — checked into the standard; applies to *every* anchor of a type | **local** — applies to the items in *one* folder/tree |
| Generality | a standardized part *any* anchor of that type carries (Backlog, PRD, Architecture) | a *domain-specific* shape that exists in one place (a `Computers/` folder, a `Disks/` tree) |
| Why it exists | so all anchors of a type are predictable to agent + human | so the items in one folder are predictable, **when the shape is too specific to be a facet** |

The test: *"does this shape recur across many anchors of a type?"* If yes → it's a **[[DAS Facet|facet]]** (or a [[DAS Traits|trait]] if it's a paradigm, not a file). If it lives in **one** folder/tree and no other project would carry it — a list of *your computers*, a tree of *your disks*, the config files of *one idiosyncratic engine you built* — it is **not** a facet; it's a **template**. Templates are how a domain-specific set gets a dependable, declared shape without inflating the global standard.

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

- **[[DAS Template Files]]** — a `_{Name} Template.md` file: one document's canonical shape (a computer record, a meeting note). Opens with a worked example.
- **[[DAS Template Folders]]** — a `_{Name} Template/` folder: the canonical structure of a folder that carries more than one document (a disk folder = main record + manifest). Opens with a worked example.
- **[[DAS Template Variables]]** — the `{{PLACEHOLDER}}` system shared by both: how variables are defined, the no-data rule, and structural-vs-cumulative content.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; per-part detail is in [[DAS Template Files]] / [[DAS Template Folders]] / [[DAS Template Variables]]; design rationale is [[F220 — Template facet-or-discipline — design review + vault-wide placement sweep|F220]].)*

- **Don't regress the model** to "cross-anchor" or "genesis-only" — the local/domain-specific framing (§ Template vs Facet) was a deliberate correction of an earlier wrong draft.
- **Audit identifiers are consumed by tooling** — `template-is-spec` / `template-has-fake-cumulative-entries` / `missing-folder-template-row` / `orphan-template` (R-template-01/03/05/06) are read by [[rewire]] + audit; don't rename without updating consumers.
- **Examples must be in-repo** (`examples/FEX Templates/`), never external links — this repo is published standalone.
- **Reuse/scoping is deferred** ([[F220]] Q4) — don't harden a mechanism into a rule until it's decided.
