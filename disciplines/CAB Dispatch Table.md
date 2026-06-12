---
description: Dispatch Table discipline — the top-of-file table convention used in most anchor pages and many facet pages. First row is the breadcrumb cell; subsequent rows group related links by category. Includes the (See …) line variant for files without a dispatch table.
---

# CAB Dispatch Table

| -[[CAB Dispatch Table]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAB]] → [[CAB Disciplines]] → [CAB Dispatch Table](hook://p/CAB%20Dispatch%20Table)<br>: the top-of-page navigation table — its own spec, dogfooded |
| --- | --- |
| Anchor | [[CAB Disciplines]] (parent catalog),  [[CAB]] |
| Design | [[CAB Dispatch Table Design\|Design]] — rationale + standing decisions |
| Related | [[Collection]],  [[progressive-disclosure]],  [[audit-dispatch\|/audit dispatch]],   |

The top-of-file table convention that gives most anchor pages and many facet pages their navigation surface.

**Examples** — below the masthead (this page's member zone is its four live exemplars; each row is itself a tiny member list, dogfooding the form):

| [[CAE]] | masthead-only — breadcrumb + structural rows, no member zone |
| --- | --- |
| [[SKL]] | member groups (`+`) — > 15 members, expandable group rows |
| [[SKA Access]] | flat member list — ≤ 15 members, hand-ordered |
| [[SYS]] | hybrid — manual category rows + `...` auto-staging |

## What it is

A markdown table placed immediately under the H1 of a page. The first row carries the breadcrumb cell (anchor path + hook URL); subsequent rows group related links by category. Wiki-links inside table cells escape the pipe as `[[Target\|Display]]`.

## Anatomy of a dispatch row

```markdown
| -[[<This Page>]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAB]] → [[CAB Disciplines]] → [CAB Dispatch Table](hook://p/CAB%20Dispatch%20Table)<br>: <one-line description> |
| --- | --- |
| <Category 1> | [[Link A\|A]],  [[Link B\|B]],  … |
| <Category 2> | [[Link C\|C]],  [[Link D\|D]],  … |
| Related | [[<This Page> Guide\|Guide]],  …other related links… |
| --- | |

## Structure — Masthead + Member zone

A dispatch table has up to **two zones** (worked examples: [[CAE Dispatch Examples]]):

### Masthead — the fixed top block (always present)

Hand-authored, one-of-a-kind to this anchor, and deliberately **small** — a switchboard, not a directory. The breadcrumb identity row plus **at most three standard rows**:

1. **Breadcrumb row** (identity) — a title cell followed by the parent-chain path ending in the page's hook link (full schema in § Anatomy above; rendered live in [[CAE]]). Carries the **up-edge** of the [[anchor-dag]] (parent link). Always present.
2. **Anchor row** (general dispatch) — the anchor's own contents: its parent catalog and primary sub-pages. The **down-edges** to what this anchor holds.
3. **Design row** (design-flow dispatch) — **only if the anchor has a design flow** — points into the design pipeline ([[FCT Design Dispatch|Design]] → PRD / Stories / Decisions / …). Absent on anchors with no design folder.
4. **Related row** — cross-links to siblings and related material, plus any genuine one-off links the user pinned on purpose (preserve them).

That's the whole masthead: identity + Anchor + (Design) + Related. Anything **enumerable** — members, sub-items, worked examples — is **not** a masthead row; it drops to the Member zone below. (This page is the live demonstration: its masthead is Anchor + Related, and its four examples hang underneath as the member zone.)

A non-collection anchor with no design flow is **Masthead-only** — just the breadcrumb + Anchor + Related.

#### The unified placement rule (one law, not a rule per row)

RULE (masthead-placement): the masthead is **exactly** the breadcrumb row plus the standard rows **Anchor**, **Design** (only if the anchor has a design flow), and **Related** — in that order, and no others. Each kind of standard information has **one** row it must occupy, and that row is present **iff** that information exists:

| Information — *if it exists* | …lives in this row |
|---|---|
| the parent / up-edge | **breadcrumb** (always present) |
| the anchor's own contents / down-edges | **Anchor** |
| an entry into the design pipeline | **Design** (only if a design flow exists) |
| cross-links to related / sibling anchors, plus any deliberately-pinned one-off links | **Related** |
| **anything enumerable** — members, sub-items, worked examples | **none** — it drops to the Member zone |

This is the single law for masthead content, replacing any per-row rules: a standard row exists **exactly when** its information does, standard information never scatters into ad-hoc rows, and the canonical row *names* are fixed (`Anchor` / `Design` / `Related` — e.g. never "Sibling" for the last one).

### Member zone — the members (only on a [[Collection]] anchor)

Below the Masthead, a [[Collection]] anchor enumerates its **members**. Two **orthogonal** axes:

**Axis 1 — layout (the [[progressive-disclosure]] pattern):**
- **Member list** — flat; one row (or compact line) per member. Use ≤ ~15 members.
- **Member groups** — members under labeled group rows; a group row may carry a **`+`** to mark it expandable (it has children of its own). Use > 15 members (the progressive-disclosure size rule; the graduation is [[granularity]]).

**Axis 2 — automation (who orders the rows):**
- **Manual** — hand-ordered rows; the author controls order and pinning.
- **Auto** — children auto-listed below a **`---`** separator (`| --- | |`), or as a **`...`** compact single-row enumeration. The agent fills them; order is mechanical.
- **Hybrid** — pinned **manual** rows *above* the `---` line (highlights the author chose), with **auto** fill below.

The two axes combine freely: a member list or member groups can each be manual, auto, or hybrid.

### Syntax markers

| Marker | Means |
|---|---|
| `\| --- \| \|` | separator — children **auto-list** below it |
| `...` | **compact** auto-enumeration in one cell (few members, no per-member description) |
| `+` (suffix on a row label — e.g. a group row written `Group+`) | the row is an **expandable group** (member groups layout) |

Dated members (a [[dated-entry-stream]] Collection like a Log) list newest-first with ISO-prefixed names.

**The member zone *is* the [[Collection]] anchor's face** — and `/audit dispatch` ([[audit-dispatch]]) builds/repairs exactly this structure.

## Classification — a discipline (the form), not a facet

A dispatch table is the **form** of a top-of-page switchboard — a reusable navigation convention, not an authored-content part of one document. That is why it lives here as a **discipline** rather than as a facet:

- **Form vs role.** This discipline owns the table *form* (breadcrumb cell, category rows, the switchboard shape). The *role* of "dispatching for an anchor" belongs to the [[FCT Anchor Page]] **facet** — the anchor page *uses* this discipline to render its switchboard. ~95% of dispatch tables in the vault are exactly that: an anchor page dispatching to its anchor's contents.
- **Not a doc facet.** Contrast with the doc facets [[CAB Discussion]] and [[CAB Brief]], which are *content containers* — bounded regions you author doc-specific content into. A dispatch table is **derived navigation**: its rows are determined by *what it points to* (the anchor's structure, or a doc's sections), not authored as standalone content. Derived-convention → discipline; authored-content-container → doc facet.
- **Boundary with [[progressive-disclosure]].** This discipline owns the table *form* (cell shape, row anatomy, pipe-escape, the `(See …)` variant). `progressive-disclosure` owns *which pattern* — Compact / List / Grouped — and the `>15 → Grouped` size rule. **Form here; pattern there.**
- **Two different "anchor" facets — don't conflate.** The [[FCT Anchor Page]] facet (the structure of the `{NAME}.md` *entry page*, which hosts the dispatch table) is separate from the **anchor spec** itself (what makes a folder *be* an anchor — the `.anchor` file's slug / traits / DAG edges, specified via the anchor crate and the Docket implementation). The dispatch table lives on the anchor *page*, never in the anchor *spec*.

### Alternative formulation (noted — we may revisit)

Because ~95% of dispatch tables are the anchor page's switchboard, keeping this as a *standalone discipline* is slightly messy — most of the spec is really describing its application in that one spot. An alternative formulation: **fold the dispatch table into the [[FCT Anchor Page]] facet** — either as its own facet of the anchor page, or merged directly into the Anchor Page facet spec. We keep it a separate discipline because the form **recurs on non-anchor pages** — the per-sub-folder dispatch pages ([[FCT Design Dispatch]], [[FCT User Dispatch]], …) and plain top-of-doc TOCs — where there is no Anchor Page facet to host it. If that non-anchor 5% proves negligible in practice, merging into Anchor Page would be the cleaner home; this note exists so the decision is reopenable.

## Current state

The convention is in active use across the vault; this spec covers the anatomy, the `(See …)` variant, and the classification above. Still TBD for full prescriptive coverage: required-cell enforcement, exhaustive grouping conventions, and the TOC interaction (deferred to [[Anchor TOC Format]]).

## The (See …) variant — for files without a dispatch table

When a file has no dispatch table (typically smaller content pages), the related-links surface becomes a single `(See …)` line under the H1:

```markdown
# Some Page

(See [[Some Page Guide]], [[Related Topic]], [[Other Anchor]])

…rest of content…
```

Format rules:
- Single set of parentheses around the whole list.
- The word `See` capitalized; no colon after it.
- Comma-separated wiki-links inside the parens.
- The Guide (if any) goes first.

## Worked examples

- [[FCT Facets]] — dispatch table with multiple category rows.
- [[SV Roots]] — dispatch table with a `Related` row pointing at [[SV Roots Brief]].

## Related

- [[CAB Disciplines]] — parent catalog.
- [[CAB Brief]] — the Brief discipline; uses the `Related` row or `(See …)` line to surface from the source file.
- [[Anchor TOC Format]] — distinct topic; TOC is generated, not the dispatch table.

# BRIEF

- **This file is the spec for the Dispatch Table discipline** — the prescriptive rules for the top-of-file table convention used across anchor and facet pages. Edit here only to refine the convention itself.
- **NOT a catalog of pages that use dispatch tables** — don't pile worked-example links here beyond a small representative set; per-page application of the convention belongs in those pages' own files or in [[FCT Facets]] / trait specs.
- **Inclusion test** — content belongs on this page if it is a *rule* about dispatch-table shape (row order, cell format, breadcrumb syntax, escape conventions, the `Related` row, the `(See …)` variant). Anything about *how a specific anchor uses* its dispatch table goes in that anchor's docs.
- **Two surface forms coexist** — full dispatch table (under H1, breadcrumb row + category rows) and the `(See …)` line variant for files without a dispatch table. Keep both spec'd in lockstep; don't let one drift.
- **Load-bearing constraints** — the pipe-escape rule for wiki-links inside cells (`[[Target\|Display]]`), the breadcrumb cell shape (`→ [[kmr]] → … → [Name](hook://...)`), and the `Related`-row convention (Brief first, comma-separated thereafter) are downstream-cited from many places; changing them requires a vault-wide sweep.
- **Sibling-discipline boundary** — TOC generation is governed by [[Anchor TOC Format]] (figure-space mechanics, regeneration tooling), not here. Don't inline TOC rules into this spec; cross-reference instead.
- **Current state is skeleton** — the page is a stub pending a full prescriptive spec; new rules added here should be marked as such if not yet enforced vault-wide.
