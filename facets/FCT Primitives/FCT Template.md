---
description: "the Template facet — a domain-specific, folder-local structure for the items in one folder/tree; the local analog of a facet for shapes too specific to be a global facet. Split into Files / Folders / Variables."
---
# FCT Template
The Template facet — a **domain-specific, folder-local structure**: the shared shape of the items inside one folder or tree, defined right where they live.

| -[[FCT Template]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[Skill Agent]] → [ob-skills](hook://ob-skills) → [[facets]] → [[FCT Primitives]] → [FCT Template](hook://p/FCT%20Template)<br>: the Template facet — a domain-specific, folder-local structure for the items in one folder/tree |
| --- | --- |
| Parts | [[FCT Template Files\|Files]],  [[FCT Template Folders\|Folders]],  [[FCT Template Variables\|Variables]],   |
| Related | [[FCT Facet]] (the *global* counterpart),  [[FCT Ruleset]],  [[FCT Dispatch Table]] (the Template row),  [[rewire]] |
| Examples | [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template\|file template]],  [[_Disk Template\|folder template]],   |

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
The **exemplar** — everything above the `template notes` cut-line (R-template-08) — is **live markdown** (real H1, frontmatter, sections) with bare `{{PLACEHOLDERS}}`; it is **not** wrapped in code fences and is **not** a `## How to use` description of a template.
**Check pattern:** no triple-backtick fence encloses the exemplar; the file is not structured as prose *about* the form. *(Audit category: `template-is-spec`.)*
**Why:** a fenced or described "template" can't be copied into a working instance — wiki-links go inert, tables and headings don't render. A template must BE an entry.

### RULE R-template-08 — the exemplar ends at the `template notes` cut-line (checked)
A template's **exemplar** (the part that becomes the instance) ends at a **cut-line** whose anchor is the exact phrase **`template notes`**; everything from that line to end-of-file is *template metadata* (variable definitions + the notes) and is **removed on clone**. Canonical form: `✂ ──── template notes ──── ✂`. The matcher is lenient — the phrase `template notes` flanked by **≥3 dashes** of any kind, **case- and spacing-insensitive**; the `✂` scissors are an optional flourish. There is **no** bare `---` divider (ambiguous with frontmatter and horizontal rules) and **no** `# About this template` heading (superseded).
**Check pattern:** exactly one line matching `(?i)^\s*(✂\s*)?-{3,}\s*template\s+notes\s*-{3,}(\s*✂)?\s*$`; nothing below it is treated as exemplar content.
**Why:** the boundary between "copied into the record" and "instructions for whoever clones it" must be unmistakable. A cut-line carries its own metaphor (cut here; everything below is removed on clone), and a real record never contains the phrase `template notes` flanked by dashes.

### RULE R-template-02 — two placeholder forms; every variable is defined (checked)
A placeholder takes one of two forms, distinguished by **case**: an **`{{UPPER_SNAKE}}` variable** — reused across sites or structural (filename, key) — is **named and defined once** in the variable-definition list above the notes; a **`{{Mixed Case description}}`** placeholder is a **self-describing one-off**, described in place, needing **no** definition. Each definition (and each in-place description) states what to put **and what to do with no data** (fill / delete the line / delete the section). Full spec: [[FCT Template Variables]].
**Check pattern:** every distinct all-caps `{{UPPER_SNAKE}}` token appears in the definition list; `{{…}}` tokens containing a lowercase letter are self-describing and need no entry. No empty `{{}}` survives a clone.
**Why:** reuse/structure earns a named, referenceable variable with a definition; a one-off field that appears once is lighter described in place than mapped to a separate list — and forcing a definition for every field is the "scan up-and-down" overkill this rule avoids.

### RULE R-template-03 — repeating structure shows a pattern + a level-marked `...` (checked)
A section whose content repeats after creation (a LOG, a change history) ships **one variableized entry-pattern** followed by a **`...` repeat-marker at the structural level of the unit that repeats** — e.g. `### ...` beneath a `### {{date}} — …` entry means *another H3 entry* recurs, not the detail line. The pattern's fields stay `{{placeholders}}`, so it is never a fake concrete entry.
**Check pattern:** a repeating section carries a `{{…}}`-pattern + a `...`/`### ...` marker whose heading-level matches the repeating unit; no fake *filled* entry (`### 2026-06-29 — …`) appears. *(Audit category: `template-has-fake-cumulative-entries`.)*
**Why:** an empty header taught nothing about the shape; a *filled* entry invites pollution. A variableized pattern + a level-marked `...` shows the shape and what repeats without inviting a fake row.

### RULE R-template-04 — naming is `_{pattern} Template`; the middle IS the instance-name pattern (checked)
File templates are `_{pattern} Template.md`; folder templates are `_{pattern} Template/` holding a same-named marker. **Strip the leading `_` and the trailing ` Template` and what remains is the instance name** — so the `{pattern}` middle is the *instance-filename (or folder-name) pattern*, and is usually **variableized**, often **composite** (e.g. `_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md` → `{{PURCHASE_DATE}} {{HOSTNAME}}.md`). The leading underscore is structural (sort-to-top + meta marker).
**Check pattern:** the basename matches `^_.+ Template(\.md)?$`; a folder template holds a same-named marker; a constant middle (`_Computer Template.md`) that would clone every instance to one name is flagged.
**Why:** the strip rule is how an instance gets its name; a constant middle produces collisions (every clone named the same), so the middle must carry the variable(s) that distinguish instances.

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

### RULE R-template-09 — single-line is inline braces; multi-line is spanning braces (checked)
A placeholder holding **one line** sits in **inline braces** (`{{event title}}`); a placeholder holding a **multi-line block** uses **braces that span their own lines** — `{{` on its own line, the content between, `}}` on its own line. The spanning form is the explicit "this value is a block" signal.
**Check pattern:** multi-line values use line-spanning `{{ … }}`; single-line values use inline `{{…}}`. No positional guessing is relied on.
**Why:** an explicit brace-span removes ambiguity about whether a value is one line or a block, and survives reflow where a position-based convention (inline vs own-line) would not.

### RULE R-template-10 — folder templates share one variable namespace; an unbound filename variable repeats (checked)
In a **folder template** (`_{pattern} Template/`), every `{{VARIABLE}}` across the folder name, the member file names, and the bodies binds to **one unified value** — a single substitution fills the folder name, the marker name, sibling member names (e.g. `{{DISK_LABEL}} Manifest.md`), and the H1s together. A member file whose name carries an **unbound** variable is a **repeatable slot** — one instance per value (the inter-file analog of the intra-file `### ...`); no `...`-in-filename is used.
**Check pattern:** member names reuse the folder template's variables (one namespace); a member with an unbound-variable name is treated as repeatable; no literal `...` appears in a filename.
**Why:** unifying the namespace is what makes "name the folder and every file inside it from one value" work; and an unbound filename variable already means "one per value," so filename repetition needs no extra glyph.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; per-part detail is in [[FCT Template Files]] / [[FCT Template Folders]] / [[FCT Template Variables]]; design rationale is [[F220 — Template facet-or-discipline — design review + vault-wide placement sweep|F220]].)*

- **Don't regress the model** to "cross-anchor" or "genesis-only" — the local/domain-specific framing (§ Template vs Facet) was a deliberate correction of an earlier wrong draft.
- **Audit identifiers are consumed by tooling** — `template-is-spec` / `template-has-fake-cumulative-entries` / `missing-folder-template-row` / `orphan-template` (R-template-01/03/05/06) are read by [[rewire]] + audit; don't rename without updating consumers.
- **Examples must be in-repo** (`examples/FEX Templates/`), never external links — this repo is published standalone.
- **Reuse/scoping is deferred** ([[F220]] Q4) — don't harden a mechanism into a rule until it's decided.
