---
description: "the Template facet — a specimen of the shape its items share, whose anchor and scope are both read off the artifact itself"
group: file, folder
---

| -[[DAS Template]]- | → [[DAS]] → [[FCT]] → [DAS Template](hook://p/DAS%20Template)  |
| --- | --- |
| Parts | [[DAS Template Files\|Files]],  [[DAS Template Folders\|Folders]],  [[DAS Template Variables\|Variables]],   |
| Related | [[DAS Facet]] (packaged address),  [[DAS Ruleset]],  [[DAS Dispatch Table]] (Template row),  [[rewire]]  |
| Rules | [[R-template]],   |
| Examples | [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template\|file template]],  [[_{{DISK_LABEL}} Template\|folder template]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS At Entity]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS Subs]],  [[DAS System Design]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Template
The Template facet — a **live specimen of the shape its items share**, declaring by its own form what it attaches to and by its own location how far that reaches.

**Cardinality: many** — any folder/tree may declare its own template, and more than one may govern the same document when their anchors are disjoint.

**TLDR** — A template defines the **shared structure of the items in one folder/tree** — what each computer record, each disk folder, each member of a domain-specific set looks like. It is a `_{Name} Template.md` file or `_{Name} Template/` folder whose body is a **live working specimen** (real H1 / frontmatter / sections, bare `{{PLACEHOLDERS}}`, **no code fences**) plus a Variables section defining each placeholder *and what to do when there's no data*. Three parts: **[[DAS Template Files|Files]]** (file templates), **[[DAS Template Folders|Folders]]** (folder templates), **[[DAS Template Variables|Variables]]** (the `{{…}}` system, shared by both).

**Two things about a template are read off the artifact itself and never declared in a key: what it attaches to (§ Anchor) and how far it reaches (§ Scope).** A template is a *specimen*, so its own form and its own location are what it specifies. That is the whole of the model below.

## Template vs Facet — two addresses, not two kinds

**They are the same template language; what differs is how far it reaches.** Dan, 2026-08-04: *"A facet is a template that is defined alongside the skills and is a global and packaged and shareable artifact. A template, by contrast, is associated with the file system and the files and the folder tree they're associated with… notice that that's really more about the scope of applicability and shareability, but less about the language."*

So the distinction below is a **position on the § Scope ladder**, not a difference in kind:

| | **Facet** | **Template** |
|---|---|---|
| Address | the packaged tree — checked into the standard, shipped with it | the content tree — sits with the items it describes |
| Reach | *every* anchor of a type | typically one folder/tree, but any rung of the ladder its location names |
| Generality | a standardized part *any* anchor of that type carries (Backlog, PRD, Architecture) | usually a *domain-specific* shape that exists in one place (a `Computers/` folder, a `Disks/` tree) |
| Why it exists | so all anchors of a type are predictable to agent + human | so the items in one folder are predictable, **when the shape is too specific to be worth packaging** |

**Read the table as a default, not a boundary.** "Local" was load-bearing when scope was binary; since § Scope it is only the ladder's *first* rung, and a template that sits in a facet home or the packaged root reaches exactly as far as its location says. What still separates the two is the tree it is checked into — packaged and shareable, or living beside the content — which is the difference Dan actually named.

The test is unchanged and is about *generality*, not mechanism: *"does this shape recur across many anchors of a type?"* If yes → it belongs in the packaged tree as a **[[DAS Facet|facet]]** (or a [[DAS Traits|trait]] if it's a paradigm rather than a file). If it lives in one folder/tree and no other project would carry it — a list of *your computers*, a tree of *your disks*, the config files of *one idiosyncratic engine you built* — it stays a **template** beside its items. Templates are how a domain-specific set gets a dependable, declared shape without inflating the global standard.

**One consequence worth stating, because it changes how facet specs get authored:** if the two are one language, then **every facet spec should carry a template plus examples in that format**. The specimen becomes the normative statement of the shape and the facet page is the prose around it — rather than the shape being described twice, once in prose and once in whatever the examples happen to do.

A template can also serve as the **starting instance** when you create a new item (clone → rename → fill/drop placeholders), but that genesis use is secondary to its primary role: *standardizing the shape of what's already in the folder*.

## Seeding from a type, then specializing

A template need not be hand-built from scratch. When an anchor of a given **type** is created, the type can **seed** a starting template into the new anchor — a sensible default shape pasted in — which the agent or user then **specializes over time** for that project. The local template thus *starts* as the global standard's default and diverges as the project's domain demands; it's the bridge from the global facet/type down to a project-specific shape. The same `_{Name} Template` form is reused this way as **instances throughout the skill hierarchy** — each a local specialization of the shared standard. *(Seeding-on-creation is a wiring detail for the anchor-creation flow, not yet built.)*

## Anchor — what a template attaches to

A template's **anchor** is the thing it describes the shape of. There are three, and each is read off the artifact rather than declared:

| the template | anchors at | governs |
|---|---|---|
| a directory (`_{Name} Template/`) | a directory | its contents |
| a document with no depth marker | the document root | the whole file |
| a document opening with a depth marker | any heading whose text matches | the subtree beneath that heading |

**A whole-file template is the default and carries no marker**, so nothing that exists today changes. A template becomes sub-document only by *saying so* in its first line, with a depth marker whose heading text is either a literal (`LOG`) or a variable. Depth **floats**: `# LOG` in one file and `## LOG` in another are the same anchor, and headings *inside* the specimen are relative to it.

**There is no separate "section template" kind, and that is the point.** An earlier draft of this model had section as a third granularity rung below file and folder. It was collapsed ([[TINK302 - Section templates and the scope ladder|F302]] Q4) once the rule side made the answer obvious: `{slug} Backlog.md` is governed by `R-backlog` *and* `R-doc` *and* `R-markdown` *and* `R-state-region` at once, with no merge step, because a rule is a **predicate** and predicates conjoin freely. Templates were the one place in the system still assuming one artifact gets one authority. Drop that assumption and a section template is not a new rung — it is an ordinary document template that happens to attach lower down.

**What makes composition legible is the anchor, not a merge algorithm.** Two templates may coexist over one file when their anchors are **disjoint**; the same anchor claimed twice is a checkable defect, not something to reconcile. Each template describes only what sits under its own anchor and **elides** what another owns — so merging never has to be defined at all.

**A template never names its delegates; the delegate declares itself.** A whole-file template is *silent* about the section templates that may attach inside it: it does not name them, does not know they exist, and does not change when one is added — exactly as `R-markdown` declares its own `where::` without `R-backlog` having to invite it. Three reasons this direction is the right one: conjunction only holds if each participant declares itself; authoring stays O(1) (templating a region nobody had templated before adds *one* file, rather than editing every file template that could contain that region); and a delegation pointer would be a second copy of a scope the template already states positionally.

**What the file template owes is not a pointer but an absence.** Under a heading another template owns, it shows the heading and nothing beneath. Half an example there would contradict the real spec — the same defect as an anchor collision, and equally checkable. The discoverability cost of silence is real (it cannot distinguish *"LOG is unspecified"* from *"LOG is specified elsewhere"*), and the fix is to **derive** the "also governed by" list from every template's anchor and scope rather than hand-author it. A hand-written cross-reference can go stale; a computed one cannot.

**Worked shape.** `AT/_@{{PERSON}} Template.md` opens `# @{{PERSON}}`, anchors at the document root, and carries the page shape including a bare `# LOG` heading with nothing under it. A second template anchors at `LOG` and specifies the dated entry beneath. Neither mentions the other; `ls AT/` shows both.

## Scope — how far a template reaches

Scope is the template's **location**, and the ladder runs nearest-first:

| rung | how it is known |
|---|---|
| this folder + its subtree | the template sits in a content folder (`AT/`) |
| wherever facet F is present | it sits in F's own home (`facets/DAS Log/`) |
| wherever trait T is declared | it sits in T's own home (`traits/collection/`) |
| global | it sits at the packaged root (`templates/`) |

**First match wins, and "first" means nearest to the item.** This settles [[F220 — Template facet-or-discipline — design review + vault-wide placement sweep|F220]] Q4, which had deferred the question until a real case clarified it. The hierarchy-climb mechanism it floated is simply what this ladder's first rung *is*; the precedence rule it would have needed — *anything in the file tree beats any trait or facet association* — stops being a rule to remember and becomes a consequence, since the content tree is nearer the item than the packaged tree.

Two costs, both small and both honest. `facets/` and `traits/` are flat files today, so a facet or trait that acquires a template gains a folder — which is the vault's existing folder-exists-IFF-it-has-content discipline rather than a new one (`facets/Skill Anchor/` is already a folder for exactly this reason). And the one thing position genuinely cannot express is a shape defined *here* but governing *there*: that is F220's **template alias**, and it survives as a file whose body is a link, not as a key.

**Migration cost is zero.** Every existing template already declares its granularity by being what it is, and its scope by sitting where it sits. Detection remains the `_{Name} Template` name — the leading underscore sorts it to the top and marks it meta.

## The three parts

- **[[DAS Template Files]]** — a `_{Name} Template.md` file: one document's canonical shape (a computer record, a meeting note). Opens with a worked example.
- **[[DAS Template Folders]]** — a `_{Name} Template/` folder: the canonical structure of a folder that carries more than one document (a disk folder = main record + manifest). Opens with a worked example.
- **[[DAS Template Variables]]** — the `{{PLACEHOLDER}}` system shared by both: how variables are defined, the no-data rule, and structural-vs-cumulative content.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; per-part detail is in [[DAS Template Files]] / [[DAS Template Folders]] / [[DAS Template Variables]]; design rationale is [[F220 — Template facet-or-discipline — design review + vault-wide placement sweep|F220]].)*

- **Don't regress the model** to "cross-anchor" or "genesis-only" — the local/domain-specific framing (§ Template vs Facet) was a deliberate correction of an earlier wrong draft.
- **Audit identifiers are consumed by tooling** — `template-is-spec` / `template-has-fake-cumulative-entries` / `missing-folder-template-row` / `orphan-template` (R-template-01/03/05/06) are read by [[rewire]] + audit; don't rename without updating consumers.
- **Examples must be in-repo** (`examples/FEX Templates/`), never external links — this repo is published standalone.
- **Reuse/scoping is settled** (2026-08-20, [[TINK302 - Section templates and the scope ladder|F302]] Q2 — it closes [[F220]] Q4's deferral). Both axes are **positional**: anchor from the artifact's form, scope from its location, nearest-wins. If you find yourself proposing a `scope::` or `granularity::` key, that argument has been had and lost — a template is a specimen, so its own form and place are the declaration, and a key would be a second copy that can disagree with it.
- **Section is not a third granularity.** It was, in the first draft; Q4 collapsed it into an anchored document template. Re-introducing a "section template" kind would restore the one-artifact-one-authority assumption the collapse removed, and would bring back the need for a merge algorithm that this model never has to define.
- **Don't add a delegation pointer** from a file template to the section templates inside it. It is authoring cost that grows, a second copy of a scope already stated positionally, and a cross-reference that can go stale — the "also governed by" view is *derived*, per § Anchor.
