---
description: the shared facet behind pebbles and rocks — one file per item, a hand-arranged control file that orders them, and propagation along the feed DAG
---

# DAS Stone
Facet spec for a **stone group** — a `{slug} Track/{slug} {Kind}s/` folder holding one file per item, ordered by a hand-arranged control file, and propagated to downstream anchors along the `feeds:` DAG.

| -[[DAS Stone]]- | → [[DAS]] → [[FCT]] → [DAS Stone](hook://p/DAS%20Stone)  |
| --- | --- |
| [[DAS Stone Design\|Design]]  | [[DAS Stone Keys\|Keys]],   |
| Examples | [[HBR Rocks\|example]],  [[MED Rocks]],   |
| Related | [[DAS Backlog]],  [[DAS Agenda]],   |
| Rules | [[R-stone]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — Pebbles and rocks are the same shape of thing at two sizes, so they are one facet parameterised by **kind**, not two facets that resemble each other.

**Cardinality:** any number of kinds; at most one group per kind per anchor.

## What a stone group is

A **stone** is one unit of work-worth-naming: a **pebble** is small and nagging, a **rock** is a multi-week chunk. Both materialise identically — a folder under the anchor's Track facet, one markdown file per stone, and a **control file** carrying the human's ordering.

The kinds are open-ended and declared in configuration. Nothing about `pebble` or `rock` is hard-coded; they are the two that ship.

| | `pebble` | `rock` |
|---|---|---|
| folder | `{slug} Pebbles/` | `{slug} Rocks/` |
| control file | `{slug} Pebble` | `{slug} Rock` |
| stone file | `{slug} P0001` | `{slug} R0001` |
| stone display | `{slug}:` | `{slug}:` |
| header display | `-{slug}-` | `-{slug}-` |

Folder names default to plural per [[DAS Facets]]; the control-file name is **configuration, not convention** — it is invisible to the mechanism, because a header is identified by what it links to rather than by what it is called.

## The one idea everything else follows from

**A control-file line is simultaneously a human's ordering decision and a machine's reference.** It opens with a link whose *target* is a numbered stone file and whose *display* is a short provenance label:

    [[VEC R0001|VEC:]] decide Aria

which reads `VEC: decide Aria`. Because the display carries the source anchor, that exact line can be pasted into any downstream anchor's control file and still reads correctly *and* still resolves to the original stone. **Propagation is therefore line-copying rather than rendering**, which is what lets a downstream control file stay hand-editable instead of becoming a generated block nobody may touch.

## Who edits what

This inverts the usual split, and the inversion is the point:

- **Agents** create, edit and delete **stone files**. They do not normally touch a control file.
- **The user** arranges **control files** — order, grouping, what is published.
- **`stone`** keeps the two consistent and propagates along the feed DAG.

## Headers, and how publishing works

A **header** is any line whose first link targets a control file. Pointing at *this* file's own control file makes it the **self-section**; pointing at another anchor's makes it that anchor's **import site**. An anchor publishes a stone by placing its line **below the self-section**.

Each downstream anchor chooses where imports land by writing a header for the source: a bare header takes block form, a header followed by a plain-text colon takes inline comma-separated form, and an absent header means the top of the file.

## Keys

A stone carries `key:: value` parameters, **at the top of the file, above the prose**. Full vocabulary and the reasoning: [[DAS Stone Keys]].

## Rules

The ruleset is below. **Every rule is `stated`, not `checked`, and that is deliberate** — a folder-shaped facet's `where::` currently selects nothing, so a `check::` here would read as enforced and enforce nothing. That is the defect this project has hit three times in two days; it is not shipping a fourth. The rules convert to `checked` when the selector is fixed.

# RULESET R-stone

include::
description:: Structural rules for a stone group — folder location and naming, the control file, the header-by-link-target rule, stone numbering, and the key block's position.

Ruleset for the Stone facet — spec: [[DAS Stone]]. **Not yet adopted by [[R-facet]]**, and must not be added to its `include::` until the rules below are genuinely checkable; an inert ruleset in the umbrella is worse than an absent one, because it reads as coverage.

### RULE R-stone-01 — The group lives at `{slug} Track/{slug} {Kind}s/` (stated)
A stone group is a folder under the anchor's Track facet, named for its kind, carrying its own anchor page. Not under Design, not at the anchor root.

### RULE R-stone-02 — One file per stone, numbered and never recycled (stated)
`{slug} {PREFIX}{NNNN}`, monotonic forever. A recycled number silently re-points stale cross-anchor references, and a copied control line is indistinguishable from a fresh one, so nothing could detect it.

### RULE R-stone-03 — The prefix is not derived from the kind's name (stated)
Renaming a kind must not rename its stones. The prefix is an opaque identifier whose only job is uniqueness within the anchor; deriving it from the kind makes a rename touch every stone file and every control line that references one, including copies already propagated into other anchors.

### RULE R-stone-04 — A header is identified by its link target (stated)
A line is a header when its **first** link targets a control file — never by how it renders. The first-link restriction keeps a stone whose `line::` mentions a control file from being read as one.

### RULE R-stone-05 — Control-file names are reserved against stone names (stated)
The mint refuses any stone whose filename would equal a control file's. `{slug} {1–2 letters}` is not an empty namespace, so without this the scheme can silently overwrite a stone.

### RULE R-stone-06 — Keys sit at the top, above the prose (stated)
`key:: value` lines precede the body. See [[DAS Stone Keys]] for the vocabulary and for why frontmatter was rejected.

# BRIEF

**This spec is the *shared* half only.** Anything true of every kind belongs here; anything true of one kind belongs to that kind's own facet — [[DAS Rocks]] and [[DAS Pebble]] — which declare their own `key::` vocabulary on top of this one. If you find yourself writing the word "pebble" into a rule here, it belongs there instead.

**Do not arm [[R-stone]] by adding it to [[R-facet]]'s `include::` until a folder-shaped facet's `where::` can actually select its instances.** Adding it early produces exactly the failure this facet was written in the middle of: a ruleset whose rules all read `(checked)`, an audit that reports no failures, and zero rules firing on either live instance. Convert the `stated` rules to `checked` in the same pass that fixes the selector, and verify by running them against a real group and seeing them fire.

**The control-file name is configuration and must stay that way.** It is invisible to the mechanism because headers resolve by link target. Any rule that hard-codes `{slug} Rock` is a bug, not a tightening.
