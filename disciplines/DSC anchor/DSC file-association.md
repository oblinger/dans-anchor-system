---
name: file-association
description: >
  Discipline. The general pattern for TYPED content associated with a parent
  document — how it attaches, where it lives, how the parent points at it. Owns the
  three placement methods (inline H1 / sibling file / sibling folder), the
  cardinality→placement rule, the suffix-naming convention, one-way migration, the
  one-form-per-parent invariant, and parent linkage. Two orthogonal dimensions ride
  on top: dated? and cardinality. The dated case is the specialization
  [[DSC dated-entry-stream]] (Discussion, Log); non-dated typed associations (Brief,
  Decisions, …) cite this umbrella directly. NOT progressive-disclosure (reader
  layering) or markdown (text rules).
tools: Read
user_invocable: false
---

# File Association

The discipline for **typed content associated with a parent document** — Discussion, Log, Brief, Decisions, and similar. Every such association is **typed** (named by a facet suffix) and **about a specific parent** (a doc, or an anchor). This discipline owns *how it attaches*: where the bytes live and how the parent advertises them. It is NOT navigation, wiki-link semantics, or basename resolution — those are markdown / Obsidian mechanics, not authoring choices.

## The two dimensions

Every typed association varies along two orthogonal axes; together they pick the placement. Naming the variation as **dimensions** (not separate disciplines) keeps the model concrete — the grouping is always *typed content about this parent*; the dimensions just choose where it sits.

- **Dated?** — does each item carry a date and sort reverse-chronologically? **Yes** → it's a [[DSC dated-entry-stream]] (Discussion, Log) — the dated specialization adds newest-first ordering, prepend semantics, and ISO-date entry-file naming. **No** → a static typed association (Brief, Decisions) — it needs nothing beyond this umbrella.
- **Cardinality** — one item or many? Drives which placement method (below). A single Brief lives inline or as one sidecar; a stream of Discussion entries, or an accumulation of briefs, earns a folder.

In practice: **100%** of these associations are typed + parent-attached; **~90%** are dated; cardinality runs from one to many.

## The three placement methods

| # | Method | Shape | When |
|---|---|---|---|
| **1** | **Inline H1** | A `# {Facet}` H1 at the END of the parent doc, after every other H1 section (for a single item) or holding dated sub-entries (for a stream). | Default. Small enough to read in flow with the parent's body. |
| **2** | **Sibling file** | A separate file `{Parent} {Facet}[s].md` next to the parent. The parent removes its inline H1 and links to the sibling from its dispatch table / near the top. | The inline form has grown past ~1–2 screens, or visually dominates the parent's regular content. |
| **3** | **Sibling folder** | A folder `{Parent} {Facet}s/` next to the parent, containing an anchor file `{Parent} {Facet}s.md` (with a dispatch table) PLUS one file per item. | Many items, each substantial enough to deserve its own file. |

## Cardinality drives placement

- **Single, small** → method 1 (inline H1).
- **Single, large** (or a flat handful) → method 2 (sibling file / sidecar).
- **Many, each substantial** → method 3 (sibling folder), one file per item.

A **Brief** is usually single → method 1 inline (`# BRIEF`) or method 2 sidecar (`{Parent} Brief.md`). If a parent accumulates *many* briefs, the same rule escalates it to method 3 (a `{Parent} Briefs/` folder). The escalation is identical whether or not the items are dated — cardinality, not datedness, drives it.

## Naming convention

- **Parent prefix** — the parent's filename (or anchor name) leads. Parent `CAE PRD.md` → sibling `CAE PRD {Facet}[s].md`, folder `CAE PRD {Facet}s/`.
- **Plural facet suffix when extracted, multiple** (methods 2–3 holding many items): `Discussions`, `Logs`, `Briefs`. The inline form (method 1) and a single-item sidecar stay **singular** (`# BRIEF`, `{Parent} Brief.md`). Singular-vs-plural is the visual cue for inline/single vs extracted-multiple.
- **Method-3 anchor file** matches the folder name: `{Parent} {Facet}s/{Parent} {Facet}s.md`, H1 = filename.
- **Per-item file naming** is dimension-specific: dated streams prefix each file with an ISO date (`YYYY-MM-DD — <Title>.md`) — see [[DSC dated-entry-stream]]; non-dated collections name by title alone.

## Migration is one-way

`1 → 2 → 3` as the association grows. Inline outgrows readability → extract to sibling file; sibling file outgrows readability → break into a folder of per-item files. **Reverse migration is discouraged** — it loses git-blame granularity (per-item history). Allowed only as a deliberate refactor with the user's explicit ack; the agent never auto-downgrades.

## One form per parent at a time

A parent has EITHER inline H1, OR sibling file, OR sibling folder — never two simultaneously for the same facet. Mixed forms drift: new items land in the wrong place, readers don't know which is current. Migration touches both forms in one atomic step (remove inline → create sibling; or sibling file → folder).

## Linkage from parent to extracted content

When extracted (methods 2–3), the parent links to it from its **dispatch table** (or a `(See …)` line / `## See also` near the **top** — discovery is the link's job, so it sits where a reader lands, not at the bottom). The inline H1 is removed simultaneously (the one-form invariant in action). Obsidian resolves `[[{Parent} {Facet}s]]` to the folder-anchor file by basename for method 3.

## Specializations

| Sub-discipline | Adds (on top of the umbrella above) |
|---|---|
| [[DSC dated-entry-stream]] | The **dated** case — every item dated; newest-first ordering; prepend (not append) semantics; ISO-date entry-file naming; a parallel per-facet entry skeleton. Examples: Discussion, Log. |

**Non-dated typed associations** (Brief, Decisions, …) cite *this umbrella directly* — they need nothing the umbrella doesn't already provide, so they earn no specialization (per [[DSC granularity]]: specialize only when extra rules warrant it; dated does, static-single doesn't).

## What this discipline is NOT

- **NOT progressive-disclosure.** That owns *what the reader sees first vs. later* — preface zones, altitudes, dispatch-table *patterns*. File-association owns *where the author puts related content* on disk and how the parent points at it.
- **NOT a generic "linking" discipline.** Wiki-links, hook URIs, breadcrumbs, frontmatter `parent::` fields are Obsidian/markdown mechanics, not authoring choices. This discipline covers only the *structural / file-shaped* association patterns.
- **NOT for one-off cross-references.** A wiki-link from one doc to another is just a wiki-link. File-association is for *patterns* — repeatable shapes multiple facets share.

## When to cite

When authoring a doc facet (or any facet) that declares *how its content sits relative to a parent*. Name the dimension and the methods it supports:

> Discussion is a [[DSC dated-entry-stream]] (dated). Methods supported: 1 (inline, default) and 2 (sibling file).
> Brief is a static typed association ([[DSC file-association]], non-dated). Methods: 1 (inline `# BRIEF`, default) and 2 (sidecar); 3 if a parent accumulates many.

The facet doesn't re-explain the methods — it names which it supports and which is default.

## See also

- [[DSC dated-entry-stream]] — the dated specialization.
- [[FCT Brief]] / [[FCT Discussion]] — doc facets citing this discipline (Brief directly; Discussion via the dated specialization).
- [[FCT Log]] — facet using the dated-entry-stream shape at the anchor scope.
- [[DSC progressive-disclosure]] — sibling discipline; what-the-reader-sees-when.
- [[DSC granularity]] — why static-single associations cite the umbrella rather than spawning a specialization.
- [[DSC markdown]] — sibling discipline; how the markdown text itself is written.


# RULESET R-file-association
include::
where:: anchor
description:: Rules for the general typed-association pattern — three placement methods, cardinality→placement, parent + plural-suffix naming, one-way migration, one-form-per-parent, parent linkage, sibling-folder shape, and the citing-facet method declaration.

Embedded ruleset for the file-association discipline, co-located with the spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. These are the **general** association rules (promoted up from the dated specialization per F154); the dated-only rules live in [[R-dated-entry-stream]]. Catalog stub at [[R-file-association]] under [[R-doc]].

### RULE R-file-association-01 — Three named placement methods (stated)

The discipline defines exactly three placement methods: inline `# {Facet}` H1 (1), sibling file `{Parent} {Facet}[s].md` (2), sibling folder `{Parent} {Facet}s/` (3). Citing facets pick a subset and declare a default; no fourth method is introduced ad hoc.

**Check pattern:** for each citing facet, assert its method declaration is a subset of {1, 2, 3} with a named default.

**Why:** a bounded method set is the point — readers (and the agent) learn three shapes and recognize them everywhere. Ad-hoc methods erode the discipline.

### RULE R-file-association-02 — Cardinality drives placement (stated)

The placement method follows cardinality: single+small → method 1 (inline); single+large or a flat handful → method 2 (sibling); many+substantial → method 3 (folder). Datedness does not change this — cardinality does.

**Check pattern:** stated; a folder (method 3) holding one item, or an inline H1 dominating the parent, is a smell to flag.

**Why:** keeps placement predictable and keeps small associations from prematurely earning folders.

### RULE R-file-association-03 — Naming is parent prefix + plural facet suffix when extracted (checked)

When extracted (methods 2–3 holding multiple items): the file/folder name is `{Parent Name} {Facet}s` (plural suffix). The inline form and a single-item sidecar stay singular. Method 3's inner anchor file matches the folder name.

**Check pattern:** regex-match extracted instances against `{Parent}\s+\w+s\.md|/`; assert the method-3 anchor file matches its folder name.

**Why:** the plural signals the extracted-multiple form; the parent prefix preserves what the association is *about*.

### RULE R-file-association-04 — Migration is one-way (stated)

Associations migrate `1 → 2 → 3` as they grow. Reverse migration is allowed only as a deliberate refactor with explicit user ack; the agent never auto-downgrades.

**Why:** downgrading loses git-blame granularity (per-item history); the cost is paid once on extraction and reversing pays it again for nothing.

### RULE R-file-association-05 — One form per parent at a time (checked)

A parent has at most one materialized form of a given facet's association: inline H1 XOR sibling file XOR sibling folder. Mixed coexistence is forbidden.

**Check pattern:** per (parent, facet) pair, count materialized forms; assert ≤ 1.

**Why:** mixed forms drift — new items land in the wrong place; readers don't know which is current.

### RULE R-file-association-06 — Dispatch linkage from parent when extracted (checked)

When extracted to method 2 or 3, the parent links to it from its dispatch table (or a `(See …)` line near the top); the inline `# {Facet}` H1 is removed simultaneously.

**Check pattern:** for each extracted instance, grep the parent for a wiki-link to it AND assert no inline `# {Facet}` H1 remains.

**Why:** the link makes the extracted association discoverable; the simultaneous H1 removal enforces one-form-per-parent.

### RULE R-file-association-07 — Sibling-folder shape (checked)
check:: file_association_folder_structure

Method 3: the folder `{Parent} {Facet}s/` contains an anchor file `{Parent} {Facet}s.md` (H1 = filename) with a dispatch table of all items, PLUS one file per item. (Per-item file naming is dimension-specific — dated streams add an ISO prefix per [[R-dated-entry-stream]].)

**Check pattern:** for each method-3 folder, assert the anchor file exists, the dispatch lists every item file, and item files follow the facet's naming.

**Why:** the folder form is only useful if its structure is predictable.
