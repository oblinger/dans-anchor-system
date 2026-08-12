---
name: file-association
description: >
  Discipline. The general pattern for TYPED content associated with a parent —
  Discussion, Log, Brief, Decisions and their kin. Owns the three placement methods (inline H1 /
  sibling file / sibling folder), the cardinality→placement rule, the suffix-naming
  convention, one-way migration, the one-form-per-parent invariant, and parent
  linkage. The parent may be a document OR an anchor. Two dimensions ride on top:
  dated? and cardinality. The dated case is the specialization [[DAS stream]]
  (Discussion, Log); undated associations (Brief, Decisions) cite this umbrella
  directly. NOT progressive-disclosure (reader layering) or markdown (text rules).
tools: Read
user_invocable: false
group: folder
---

# File Association

The discipline for **typed content associated with a parent** — Discussion, Log, Brief, Decisions and their kin. Every such association is **typed** (named by a facet suffix) and **about a specific parent**. This discipline owns *how it attaches*: where the bytes live and how the parent advertises them. It is NOT navigation, wiki-link semantics, or basename resolution — those are markdown and Obsidian mechanics, not authoring choices.

**This discipline is machinery, and its name is not vocabulary.** Nothing needs to say "file association" out loud; facets cite it by link. The class of facets that use it has deliberately **not** been given a spoken name — [[DAS stream|Stream]] names the one member-kind worth talking about, and the rest simply say *"see this discipline for how it attaches."* A collective name (`attached facet` was the candidate) is parked until there are enough members to justify it.

## The parent may be a document or an anchor

This is load-bearing and easy to lose. An association is *about* something, and that something is either:

- **a document** — [[DAS Discussion|Discussion]] rides on the PRD it discusses; [[DAS Brief|Brief]] rides on the file it explains how to maintain;
- **an anchor** — [[DAS Log|Log]] rides on the whole anchor, materializing as `{slug} Log/` at the anchor root and advertised from the anchor page's dispatch table.

Both cases are the same pattern. The placement methods below are **orthogonal** to which kind of parent it is: an anchor-wide Log folder is method 3 with an anchor parent, not a fourth method. The older `doc-scoped` / `anchor-scoped` vocabulary names the two parent kinds — it does not divide what uses this discipline from what does not, and reading it that way is the standing trap.

## The two dimensions

Every association varies along two orthogonal axes; together they pick the placement. Naming the variation as **dimensions** (not separate disciplines) keeps the model concrete — the grouping is always *typed content about this parent*; the dimensions just choose where it sits.

- **Dated?** — does each item carry a date and sort reverse-chronologically? **Yes** → it is a [[DAS stream|stream]] (Discussion, Log) — the dated specialization adds newest-first ordering, prepend semantics, and ISO-date entry-file naming. **No** → a static association (Brief, Decisions) — it needs nothing beyond this umbrella.
- **Cardinality** — one item or many? Drives which placement method. A single Brief lives inline or as one sidecar; a stream of Discussion entries, or an accumulation of briefs, earns a folder.

In practice: **100%** of these are typed + parent-attached; **~90%** are dated; cardinality runs from one to many.

## The three placement methods

| # | Method | Shape | When |
|---|---|---|---|
| **1** | **Inline H1** | A `# {Facet}` H1 at the END of the parent doc, after every other H1 section (for a single item) or holding dated sub-entries (for a stream). | Default. Small enough to read in flow with the parent's body. |
| **2** | **Sibling file** | A separate file `{Parent} {Facet}[s].md` next to the parent. The parent removes its inline H1 and links to the sibling from its dispatch table / near the top. | The inline form has grown past ~1–2 screens, or visually dominates the parent's regular content. |
| **3** | **Sibling folder** | A folder `{Parent} {Facet}s/` next to the parent, containing an anchor file `{Parent} {Facet}s.md` (with a dispatch area) PLUS one file per item. | Many items, each substantial enough to deserve its own file. |

A citing facet picks a subset of the three and names its default; no fourth method is introduced ad hoc.

## Cardinality drives placement

- **Single, small** → method 1 (inline H1).
- **Single, large** (or a flat handful) → method 2 (sibling file / sidecar).
- **Many, each substantial** → method 3 (sibling folder), one file per item.

A **Brief** is usually single → method 1 inline (`# BRIEF`) or method 2 sidecar (`{Parent} Brief.md`). If a parent accumulates *many* briefs, the same rule escalates it to method 3 (a `{Parent} Briefs/` folder). The escalation is identical whether or not the items are dated — cardinality, not datedness, drives it.

## Naming convention

- **Parent prefix** — the parent's filename (or anchor name) leads. Parent `CAE PRD.md` → sibling `CAE PRD {Facet}[s].md`, folder `CAE PRD {Facet}s/`.
- **Plural facet suffix when extracted, multiple** (methods 2–3 holding many items): `Discussions`, `Logs`, `Briefs`. The inline form (method 1) and a single-item sidecar stay **singular** (`# BRIEF`, `{Parent} Brief.md`). Singular-vs-plural is the visual cue for inline/single vs extracted-multiple.
- **Method-3 anchor file** matches the folder name: `{Parent} {Facet}s/{Parent} {Facet}s.md`, H1 = filename.
- **Per-item file naming** is dimension-specific: dated streams prefix each file with an ISO date (`YYYY-MM-DD — <Title>.md`) — see [[DAS stream]]; undated collections name by title alone.

## Migration is one-way

`1 → 2 → 3` as the association grows. Inline outgrows readability → extract to sibling file; sibling file outgrows readability → break into a folder of per-item files. **Reverse migration is discouraged** — it loses git-blame granularity (per-item history). Allowed only as a deliberate refactor with the user's explicit ack; the agent never auto-downgrades.

## One form per parent at a time

A parent has EITHER inline H1, OR sibling file, OR sibling folder — never two simultaneously for the same facet. Mixed forms drift: new items land in the wrong place, readers do not know which is current. Migration touches both forms in one atomic step (remove inline → create sibling; or sibling file → folder).

## Linkage from parent to extracted content

When extracted (methods 2–3), the parent links to it from its **dispatch table** (or a `(See …)` line / `## See also` near the **top** — discovery is the link's job, so it sits where a reader lands, not at the bottom). The inline H1 is removed simultaneously (the one-form invariant in action). Obsidian resolves `[[{Parent} {Facet}s]]` to the folder-anchor file by basename for method 3.

## Specializations

| Sub-discipline | Adds (on top of the umbrella above) |
|---|---|
| [[DAS stream]] | The **dated** case — every item dated; newest-first ordering; prepend (not append) semantics; ISO-date entry-file naming; a parallel per-facet entry skeleton. Examples: Discussion, Log. |

**Undated associations** (Brief, Decisions, …) cite *this umbrella directly* — they need nothing the umbrella does not already provide, so they earn no specialization (per [[DAS granularity]]: specialize only when extra rules warrant it; dated does, static-single does not).

## Who cites this today

| Facet | Cites | Methods declared | Parent |
|---|---|---|---|
| [[DAS Discussion\|Discussion]] | [[DAS stream]] | 1 + 2, default 1 | document |
| [[DAS Log\|Log]] | [[DAS stream]] | 2 + 3, default 3 | anchor |
| [[DAS Brief\|Brief]] | this discipline directly | 1 default, 2 sidecar, 3 on accumulation | document |

Citing this is a property several facets share, not a facet's home in the catalog — [[DAS Facets]] partitions by subsystem and those three sit in three different groups. Discussion and Log are additionally **streams**; Brief is not, and has no collective name of its own beyond being a facet with two forms.

## What this discipline is NOT

- **NOT progressive-disclosure.** That owns *what the reader sees first vs. later* — preface zones, altitudes, dispatch-table *patterns*. This discipline owns *where the author puts related content* on disk and how the parent points at it.
- **NOT a generic "linking" discipline.** Wiki-links, hook URIs, breadcrumbs, frontmatter `parent::` fields are Obsidian/markdown mechanics, not authoring choices. This discipline covers only the *structural / file-shaped* attachment patterns.
- **NOT for one-off cross-references.** A wiki-link from one doc to another is just a wiki-link. This is for *patterns* — a repeatable shape multiple facets share.

## When to cite

When authoring a facet that declares *how its content sits relative to a parent*. Name the dimension and the methods it supports:

> Discussion is a [[DAS stream|stream]]. Methods supported: 1 (inline, default) and 2 (sibling file).
> Brief is a static typed association ([[DAS file-association]], undated). Methods: 1 (inline `# BRIEF`, default) and 2 (sidecar); 3 if a parent accumulates many.

The facet does not re-explain the methods — it names which it supports and which is default. That division is the whole point: **the facet says what it is for and what goes in it; the discipline does the heavy lifting on how it attaches.**

## History

**Briefly renamed to `Rider` and reverted, 2026-08-06.** The rename was an attempt to give the class a spoken name; it failed the voice-engine rule (dictation renders *rider* as *writer*) and, more usefully, revealed that the umbrella does not need a spoken name at all. The vocabulary went to [[DAS stream|Stream]] instead, where it carries meaning. Two things from that pass were kept: § The parent may be a document or an anchor, which makes explicit what the older text said in a single clause, and § Who cites this today. Prior generalization step: [[F154 — Promote file-association to the general association discipline; slim stream; Brief cites it|F154]]. Decision record: [[TINK310 - Stream: one reverse-chronological facet at three volumes|F310]].

## See also

- [[DAS stream]] — the dated specialization.
- [[DAS Brief]] / [[DAS Discussion]] — facets citing this discipline (Brief directly; Discussion via the dated specialization).
- [[DAS Log]] — an association with an anchor parent.
- [[DAS progressive-disclosure]] — sibling discipline; what-the-reader-sees-when.
- [[DAS granularity]] — why static-single associations cite the umbrella rather than spawning a specialization.
- [[DAS markdown]] — sibling discipline; how the markdown text itself is written.

The companion ruleset lives at [[R-file-association]].
