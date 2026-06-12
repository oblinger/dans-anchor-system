---
name: progressive-disclosure
description: Discipline. Layered information presentation across the vault — the **preface zone** every doc may carry (dispatch table → TLDR → figure), the **three levels** of progressive disclosure (project anchor / folder anchor / within-doc), and the **five named dispatch-table patterns** (Grouped / List / Compact at anchor-folder; Linear / Matrix within-doc). Cited by [[CAB Anchor Page]], [[CAB Features]], [[CAB Architecture]], [[CAB UX Design]], and the `md` skill.
user_invocable: false
---

# Progressive Disclosure Discipline

Progressive disclosure is *layered information presentation — each layer delivers as much as a reader at that depth needs, no more.* The discipline names the layers, the elements at each layer, and the order in which they appear. What distinguishes a conformant doc from an ad-hoc one:

- **Preface zone** — H1 → dispatch table → TLDR → figure → first body H2. No preamble.
- **Three levels** — project anchor page → folder/subsystem anchor page → within-doc dispatch. Two clicks from root to any leaf.
- **Five named dispatch patterns** — Grouped / List / Compact (anchor-folder); Linear / Matrix (within-doc). Size rule: >15 entries → Grouped.
- **Content first, meta last** — the first contentful sentence delivers the subject, not the document. "This document specifies..." goes in a tail `## Scope` section, or gets deleted.
- **Per-facet preface requirements** — TLDR required on Features only (PRDs explicitly excluded); figure required on Architecture + UX.

This is a discipline, not a user-invocable skill — other CAB facets and skills cite it via `[[progressive-disclosure]]` and Claude Code loads it into context before they run.


## Why this exists — the problem it solves

Today the discipline is implicit in [[CAB Anchor Page]] and the `md` skill's dispatch-table sub-command. Many anchors invented their own variations. Without naming the patterns and codifying when each applies, every author makes the same micro-decisions from scratch, and the same drift accumulates anchor-by-anchor.

This discipline names the patterns, gives them one home, and makes drift detectable by audit.

A second motivation: readers come at a doc with different intent. A grazer wants the gist in 5 seconds; a navigator wants the structure in 30 seconds; the focused reader wants the full body. The **preface zone** above the document body explicitly serves the first two — TLDR for grazers, dispatch table / figure for navigators — so the body itself doesn't have to compromise.


## The three levels of progressive disclosure

1. **Project anchor page** (`{NAME}.md`) — top-level dispatch to everything important *inside* the anchor, plus relevant external links. The navigational backbone: from any doc in the anchor, the breadcrumb jumps back to `{NAME}.md` from which the reader reaches anywhere else in one or two more clicks.
2. **Folder / subsystem anchor page** — same pattern at smaller scope: `{NAME} Track/{NAME} Track.md`, `{NAME} Design/{NAME} Architecture/{NAME} Architecture.md`, etc. Each is a local dispatch hub for its sub-tree.
3. **Within-document** — a doc that's long enough or structured enough to need internal navigation carries an internal dispatch (Linear or Matrix per § Dispatch-table patterns) under its preface zone. Acts like an outline.

The two-level ideal: **project anchor → subsystem anchor → leaf doc**. Two clicks from project root to any leaf.


## The preface zone

The zone above a document's body, in canonical order:

```markdown
# {Document Title}

| -[[{Document}]]- | ><br>: One-line description |
| --- | --- |
| ... (dispatch table — Grouped / List / Compact / Linear / Matrix per Q4) |  |

**TLDR**

- **<Descriptor>** — <one-line summary>
- **<Descriptor>** — <one-line summary>
- ...

![Organizing figure](path/to/figure.svg)

(Optional one or two sentences describing the figure or its significance.)

## {First body section}

(document body begins here)
```

**Order:** H1 → dispatch table (if present) → TLDR (if present) → figure (if present) → optional 1-2-sentence figure caption → first H2 (body begins).

**No preamble** between H1 and the first H2 beyond the preface zone. The H2 is typically `## Overview` or another section-appropriate heading — it just begins; no "Body" wrapper, no transition text.

**Author rule:** include each preface element only when it adds value. Short single-purpose docs may have none of them — H1 title and `description:` frontmatter alone are sufficient. Whether each element is *required* on a given doc type is set by that facet's spec; see § Per-facet preface requirements.


## Content first. Meta last, or never.

The single rule that catches most preface-zone failures:

> **The first contentful sentence delivers the subject, not the document.**

The reader's first glance must land on **what the subject is**, not on the fact that a document exists about it.

### Five tests

1. **First-sentence test** — read aloud. Does it teach you something specific about the subject? Ship it. Does it tell you the document exists / is normative / specifies fields / contains sections? Rewrite.
2. **"This document..." veto** — `This document`, `This page`, `This section`, `Here we describe`, `The following sets out`, `This is the spec for` are all meta. None belong in the preface zone. They go in a tail `## Scope` or `## About` section, or get deleted entirely.
3. **Italicize the canonical phrasing of the definition.** The first definitional sentence is the load-bearing one — italic the phrase that carries the definition so the reader's eye knows where to land. Example: `An anchor is a *named logical collection of items and content that can be referenced as a whole.*`
4. **Right after the definition: 3-5 short bullets naming the distinguishing properties.** Each bullet is one info-packed line, optionally linking to a deep section. This pattern (definition → key-fields list) is progressive disclosure at the H1 level — content first, structure right behind.
5. **Dense ≠ long.** A 30-word info-packed sentence beats a 200-word meta-prose paragraph. The TLDR is allowed to be short.

### Canonical good example

See `prj/ClaudiMux/Skill Docket App/Docket/DKT Docs/DKT User/DKT Standard/Anchor.md` — the opening (H1 → italicized definition → 4-bullet distinguishing-properties list → § Standard fields) is the reference exemplar for this discipline. § Scope and § Informative references at the bottom of that doc show where meta-prose belongs when it's needed at all.

### Bad vs good — same H1, same topic

❌ Bad (meta as preface — what agents kept producing):

> # Anchor
>
> This document is the normative standard for anchors in the Docket system. It specifies what an anchor is, the standard fields that may appear in an anchor declaration, the five-position scan the crate performs to discover anchor declarations, the resolution algorithm that disambiguates them, the warnings catalog, and the DAG that connects anchors. Below we describe each in turn.

✅ Good (content as preface — what landed in Anchor.md):

> # Anchor
>
> An anchor is a *named logical collection of items and content that can be referenced as a whole.* Every anchor is backed by a filesystem folder. What distinguishes an anchor from an ordinary folder:
>
> - **Slug** — a short canonical identifier (`DKT`, `MUX`, `HA`), globally unique within the item store.
> - **Declaration** — one of five forms (§ Declaration) naming the slug and optionally other fields. An empty `.anchor` file is enough.
> - **Standard fields** — slug, title, description, traits, docket declarations, parents, children, code path, root flag. All optional except slug.
> - **Position in the anchor DAG** — anchors have parents and children; the default DAG follows the filesystem and can be overridden per anchor.

The bad version takes 80 words to say nothing about anchors. The good version takes ~75 words to deliver one definition + four distinguishing properties + four tooltip-deep links. Both occupy the same vertical screen real estate. Only one is content.


## Dispatch-table patterns

**Five named patterns — three at anchor / folder level + two within-document:**

| Where | Pattern | Shape | When |
|---|---|---|---|
| Anchor / folder | **Grouped** | rows = labeled groups of related links | many targets (>15); strong categorical structure |
| Anchor / folder | **List** | one row per entry, optional description column | moderate count; per-entry description adds value |
| Anchor / folder | **Compact** | single row, comma-separated enumeration | few targets; no per-entry description |
| Within-doc | **Linear** | one column of section links | linear outline (TOC) |
| Within-doc | **Matrix** | grid (rows × columns) | sections × aspects |


### Anchor / folder dispatch — three patterns

**Grouped pattern** — each row is a *group of related links*. Used when the anchor dispatches to >15 targets with strong categorical structure. Row label names the group; the cell carries multiple wiki-links comma-separated. Hand-authored (no separator row):

```
| -[[NAME]]- | ><br>: description |
| --- | --- |
| External | [Landing](https://...), [GitHub](https://github.com/...), [Docs](...) |
| Design | [[Arch]], [[UX]], [[Decisions]] |
| Track | [[Backlog]], [[Roadmap]], [[Features]] |
| User | [[Guide]], [[Reference]], [[Tutorials]] |
```

**List pattern** — each row is *one entry*, optionally with a description column. Used for moderate target count where per-entry description adds value. May be auto-generated via separator rows: `---` (alphabetical), `+++` (with grandchildren), `^^^` (reverse-chronological); or hand-authored with no separator (frozen):

```
| -[[NAME]]- | ><br>: description |
| --- | --- |
| [[Architecture]] | System overview + subsystem docs |
| [[Decisions]] | Project decisions (formerly Principles + Rules) |
| [[Backlog]] | Active work tracking |
```

**Compact pattern** — single row, comma-separated enumeration of children. Used for lightweight dispatch with few targets and no per-entry description. Auto-generated via the `...` separator row:

```
| -[[NAME]]- | ><br>: description |
| --- | --- |
| ... | [[Architecture]], [[Decisions]], [[Backlog]], [[User Guide]] |
```


### Separator-row alignment (existing CAB convention)

| Separator | Pattern produced | Auto-managed |
|---|---|---|
| `...` | Compact | Yes — single row, comma-separated children |
| `---` | List | Yes — alphabetical, one row per child with descriptions |
| `+++` | List | Yes — with grandchildren in description column |
| `^^^` | List | Yes — reverse-chronological (dates float to top) |
| `!!!` | (one-shot clip) | One-time delete-everything-below |
| (none) | Grouped or List | Frozen — fully hand-authored |


### Within-document dispatch — two patterns

- **Linear pattern** — single column of section links (think TOC). Each row points at one H2/H3 inside the doc.
- **Matrix pattern** — grid: rows × columns. E.g., rows = top-level sections, columns = aspects (overview, examples, edge cases). Useful for docs with regular cross-cutting structure.


## Size-based pattern selection (anchor / folder dispatch)

**Rule:** when the dispatch table would have more than **15 entries**, use the **Grouped** pattern.

Rationale: a flat List or Compact of 16+ entries forces the reader to scan a long undifferentiated set. Grouping into 3-6 categories with 3-5 entries each gives the reader a navigable index — they pick a group first, then the entry.

Below 15 entries, choose between List and Compact:
- **List** when each entry has a one-line description worth seeing.
- **Compact** when the entries are self-documenting (their names tell the reader everything) and no description is needed.


## Per-facet preface requirements

This central table records which preface elements each CAB facet requires. The list grows as facets are evaluated.

| Facet | Dispatch table | TLDR | Figure |
|---|---|---|---|
| All facets that associate with a folder | **Required** | (per col 3) | (per col 4) |
| [[CAB Anchor Page]] | Required | Optional | Optional |
| [[CAB Features]] | Optional | **Required** | Optional |
| [[CAB Architecture]] (top-level doc) | Required | Optional | **Required** |
| [[CAB Architecture]] (subsystem doc) | Required | Optional | **Required** |
| [[CAB UX Design]] (post-F113: `CAB UX`) | Required | Optional | **Required** |
| [[CAB PRD]] | Required | **NOT required** (explicitly — too heterogeneous) | Optional |
| [[CAB Decisions]] (post-F113) | Required | Optional | Optional |
| [[CAB Interface]] | Required | Optional | Optional |
| [[CAB Log]] (post-F113) | Optional | Optional | Optional |
| [[CAB Testing]] | Required | **Required** | Optional |
| Other facets associated with a folder | Required | Optional | Optional |

**Reading the table:**

- **Dispatch table:** required on every facet that is a folder (i.e., every folder anchor page). For flat-file facets (e.g., a single `.md` file like `{NAME} PRD.md`), the dispatch table is still required as the in-doc internal-navigation aid (Linear or Matrix pattern).
- **TLDR:** required on **Feature docs and Testing docs**. Feature docs reduce cleanly to 3-5 one-line bullets capturing the gist; Testing docs reduce cleanly to the testing posture + the bar per kind (e.g., "Heavy unit + integration, modest e2e; every public function unit-tested, every subsystem boundary integration-tested, one e2e per user story"). Other facets may add the requirement over time as the user identifies docs where a TLDR genuinely helps. PRDs are **explicitly excluded** (too heterogeneous to compress meaningfully; forcing one produces filler).
- **Figure:** required on Architecture (both top-level and subsystem) and UX Design. SVG preferred.

**Growth posture:** each list grows bottom-up via individual facet-spec amendments. When a new facet spec is authored (or an existing one updated), it declares its own preface requirements; this central table accumulates them.


## TLDR formatting

A TLDR is a **description list of short single-line bullets**, each with a 2-3-word bolded descriptor followed by an em-dash and a concise body:

```markdown
**TL;DR.**

- **Core idea** — <one-line summary of the core idea>
- **Mechanism** — <one-line summary of the mechanism>
- **Trade-offs** — <one-line summary of the trade-offs>
```

**Header style.** `**TL;DR.**` (with the punctuated abbreviation and trailing period) is the preferred form — it reads cleanly in both Obsidian and plain markdown, and the period signals "this is a label, the bullets are the content." `**TLDR**` (no punctuation) is also accepted; pick one and stay consistent within a project.

**Preferred bullet shape (the canonical form).** All things equal: a description list where **most bullets fit on a single short line** (target ≤ 80-100 chars). The descriptor is the recall handle; the body is the gist. A reader skimming sees both at once, in one eye-fixation per bullet.

**Length tolerance.** A small minority of bullets may run to a longer line when the topic genuinely needs it (multi-clause posture statements, lists of named tiers, tier-mapping bullets that enumerate). Treat that as the exception. A TLDR where most bullets sprawl to multiple lines isn't a TLDR — it's a section of body text mislabeled.

**Bullet count.** **Three to eight bullets** is the working range. Three to five for a tight doc that compresses cleanly. Six to eight for a richer doc whose structure earns more bullets (e.g., a testing strategy with posture + 3-4 bars + tier mapping). More than eight means the reader has to read a TLDR-of-the-TLDR; refactor.

**Cover the whole doc, not one aspect.** A good TLDR spans the major sections of the body, one bullet per section's gist. A TLDR that recites only one part of the doc fails the grazer; the reader has to read the body to discover the doc's other sections.

**When required:** TLDR is required on **Feature documents** (per [[CAB Features]]) and **Testing documents** (per [[CAB Testing]]). Always optional on other types; if included, must follow the format above. PRDs are explicitly excluded. **Worked examples:** [[MUX Testing]] (8 bullets, covers posture + tiers + scope + cadence + tier mapping) and [[CAE Testing]] (similar shape at smaller scale).


## Figure placement

When a doc carries an organizing figure (system diagram, architecture sketch, flow chart, etc.), it lives in the preface zone, **after the TLDR**, **before the body H2s**.

- **Format preference:** SVG (existing convention; see `md` skill).
- Optional **1-2 sentences** after the figure to caption or contextualize it.
- The figure is preface material, not body material — the body's first H2 follows it.

**Author rule:** the figure should be *organizing* — it shows the doc's structure at a glance. Decorative figures don't belong in the preface zone; they live inline in the body where they illustrate the specific point at hand.


## Relationship to existing facets and skills

- **[[CAB Anchor Page]]** — cites this discipline. Anchor page dispatch tables follow Grouped / List / Compact pattern per the size rule; preface zone (dispatch + optional TLDR + optional figure) follows this discipline's ordering.
- **`md` skill** — its dispatch-table and TOC sub-commands reference the named patterns in their templates and emit conformant output.
- **[[CAB Features]]** — TLDR required (initial scope). Feature docs reduce cleanly to 3-5 one-line bullets capturing the gist.
- **[[CAB Architecture]]** — figure required. May include a TLDR voluntarily.
- **[[CAB UX Design]]** (post-F113: `CAB UX`) — figure required.
- **[[CAB PRD]]** — TLDR explicitly NOT required (heterogeneous content).
- **[[CAB Decisions]]** (post-F113) — TLDR not applicable; each decision is its own one-liner.
- **Audit:** post-F113, this discipline lands in `{NAME} Decisions.md` as one or more `D<NN>` decisions at the per-anchor tier.


## Anti-patterns

- **A 16-entry flat List.** That's a wall of links. Above 15, switch to Grouped.
- **A TLDR with 8+ bullets.** That's an outline, not a TLDR. Cut to 3-5 or drop it.
- **A TLDR on a PRD.** PRDs are too heterogeneous; the TLDR will read as filler. Explicitly forbidden by this discipline.
- **A figure as preface decoration.** The preface-zone figure must be *organizing* — shows the doc's structure. Inline illustrative figures live in the body.
- **Prose between H1 and first body H2.** The preface zone is dispatch / TLDR / figure (in that order). Nothing else fits there. No "this document covers …" lead-in paragraph; the TLDR is that lead-in if needed.
- **Body content masquerading as preface.** The dispatch table is navigational; the TLDR is summarizing; the figure is organizing. None of them contain new information that isn't elsewhere in the doc.
- **Meta-prose at the top.** "`This document is the normative standard for...`" / "`This page specifies...`" / "`The following describes...`". Deferral disguised as introduction. Goes to a tail `## Scope` or `## About` section, or gets deleted. See § Content first. Meta last, or never.
