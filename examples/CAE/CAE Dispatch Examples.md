---
description: "Worked examples of the dispatch-table structure (Masthead + Member zone) — real, live anchor pages demonstrating each alternative. Per CAB Dispatch Table § Structure."
---

| -[[CAE Dispatch Examples]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [CAE Dispatch Examples](hook://p/CAE%20Dispatch%20Examples)<br>: live worked examples of each dispatch-table structure |
| --- | --- |
| Spec | [[DSC Dispatch Table]] § Structure |
| Builder | [[audit-dispatch\|/audit dispatch]],   |

# CAE Dispatch Examples

A gallery of the dispatch-table alternatives from [[DSC Dispatch Table]] § Structure — each a **live, real** anchor page (click through to see it render), not a fenced copy. Recall the model: every dispatch table is a **Masthead** (breadcrumb + structural rows + curated links) optionally followed by a **Member zone** (a [[Collection]] anchor's members, as a *member list* or *member groups*, *manual / auto / hybrid*), with the markers `---` (auto-list), `...` (compact auto), `+` (expandable group).

## The four kinds

| #   | Kind                       | What it shows                                                                                                                         | Live example   |
| --- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| 1   | **Masthead-only**          | breadcrumb + anchor-kind **structural rows** (Design / Architecture / User Docs / Dev Docs), no member zone — a non-collection anchor | [[CAE]]        |
| 2   | **Member groups** (`+`)    | members under labeled, **expandable** group rows (`Anchor+`, `Doc+`, `Search+`) — the > 15 grouped layout                             | [[SKL]]        |
| 3   | **Flat member list**       | one row per member, hand-ordered — the ≤ 15 flat layout, manual                                                                       | [[SKA Access]] |
| 4   | **Hybrid** (manual + auto) | curated category rows the author pinned, plus a **`...`** compact-auto staging row at the bottom                                      | [[SYS]]        |
| 5   | **With a figure**          | the page ordering when an anchor page carries a figure: **H1 → one-liner → figure (no title) → dispatch table**                       | [[CAE Figure Page]] |

## 1 — Masthead-only ([[CAE]])

`[[CAE]]` is a [[Code Anchor]]. Its dispatch table is **all Masthead, no Member zone** — because CAE isn't a [[Collection]]; it's one project with structural parts, not a set of like members. Read it and notice:
- the **breadcrumb identity row** (the title cell naming the page, plus the kmr → … → CAE path) — the up-edge;
- **structural rows** keyed by the anchor's parts: [[CAE Design|Design]], [[CAE Architecture|Architecture]], [[CAE User Docs|User Docs]], [[CAE Dev Docs|Dev Docs]] — each a down-link to a sub-folder dispatch page;
- a `Related` row and an `External` row (curated links).

This is what *most* project anchors look like: Masthead only.

## 2 — Member groups with `+` ([[SKL]])

`[[SKL]]` is the user-facing skill library — a [[Collection]] with **many** members (every published skill), so it uses **member groups**: rows like [[SKL Anchor|Anchor]], [[SKL Hygiene|Hygiene]], [[SKL Doc|Doc]], [[SKL Search|Search]] — each with a trailing `+`. The **`+`** marks each group row as *expandable* — it's itself a dispatch page of its members. This is the > 15 grouped layout (the [[progressive-disclosure]] size rule; the graduation from flat→grouped is [[granularity]]).

## 3 — Flat member list ([[SKA Access]])

`[[SKA Access]]` is a small [[Collection]] (the accessor skills). Few members → a **flat member list**, one row per member: [[SKA Bridge]], [[SKA ctrl]], [[SKA io]], [[exp]]. Hand-ordered (manual). No grouping, no `+` — when a collection is small, the flat list is correct; it graduates to member groups only past ~15 ([[granularity]]).

## 4 — Hybrid: manual rows + `...` auto-staging ([[SYS]])

`[[SYS]]` is the curation anchor — a big, evolving [[Collection]] of everything. Its table is **hybrid**: hand-curated **category rows** the author ordered by meaning (`Top`, `Direct`, `Topic`, `Bespoke`, `Content`, …) — the *manual* part — followed by a `| ... |` **compact-auto staging row** at the bottom where newly-added, not-yet-categorized children land automatically. New items appear in `...`; when they earn a category, the author moves them up into a manual row. That's the manual-pins-above / auto-fill-below hybrid.

## 5 — With a figure ([[CAE Figure Page]])

`[[CAE Figure Page]]` shows the **page ordering when an anchor page carries a figure** — orthogonal to the four layouts above (any of them can carry a figure). Justified by [[progressive-disclosure]], top to bottom: **H1** (`<slug> - <Name>`) → **one line** saying *what the page is* (broadest stroke; an optional Overview may follow) → **the figure**, with *no title above it* → **the dispatch table** directly below. When a figure is present it's typically the page's link surface — the picture carries no clickable links, so the table supplies the navigation it can't.

## How these map to the axes

| Example | Layout axis | Automation axis |
|---|---|---|
| [[CAE]] | (masthead-only — no member zone) | — |
| [[SKL]] | **member groups** (`+`) | manual |
| [[SKA Access]] | **member list** (flat) | manual |
| [[SYS]] | member list (category rows) | **hybrid** (manual + `...` auto) |

The fifth combination — a fully **auto** member list (children listed below a bare `| --- | |` with no manual pins) — is the simplest: a folder of like children where the agent just enumerates them. `/audit dispatch` ([[audit-dispatch]]) produces any of these shapes from a folder, choosing layout by member count and automation by whether the author has pinned rows.
