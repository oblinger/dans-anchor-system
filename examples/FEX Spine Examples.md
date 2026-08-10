---
description: "made-up worked examples of the four spine shapes"
---

# FEX Spine Examples
One invented page per spine shape — each *is* the shape it teaches, so it can be opened and read rather than described.

| -[[FEX Spine Examples]]- | → [[DAS]] → [[examples]] → [FEX Spine Examples](hook://p/FEX%20Spine%20Examples)<br>: made-up worked examples of the four spine shapes |
| --- | --- |
| Spec | [[DAS spine]],  [[DAS Dispatch Table]],   |
| Shapes | [[FEX Breadcrumb Spine\|breadcrumb]],  [[FEX Grouped Dispatch\|grouped]],  [[FEX List Dispatch\|list]],  [[FEX Stream Spine\|stream]],   |
| Related | [[FEX Dispatch Examples]],  [[DAS progressive-disclosure]],   |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[Bridges]],  [[Clarifier]],  [[CSE]],  [[DAS Examples]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[Devtools]],  [[ESP]],  [[Espresso]],  [[FEX Agenda]],  [[FEX API]],  [[FEX API Design]],  [[FEX Architecture]],  [[FEX Claude]],  [[FEX Completed Roadmap]],  [[FEX CSE]],  [[FEX Decisions]],  [[FEX Decisions Details]],  [[FEX Facet]],  [[FEX Figure Page]],  [[FEX Files]],  [[FEX Icebox]],  [[FEX Inbox]],  [[FEX Minimal Facet]],  [[FEX Minimal Skill]],  [[FEX Project Root]],  [[FEX Repo]],  [[FEX Roadmap]],  [[FEX Rules]],  [[FEX Scheduler]],  [[FEX Skill]],  [[FEX Stories]],  [[FEX System Design]],  [[Forum Stories]],  [[HBR PRD User Stories]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

These pages are **deliberately made up**. The vault's own pages are the right exemplars for a *live* shape — click one and watch HookAnchor render it — but this repo ships publicly, so a teaching gallery built from real vault content would leak it. The [[HBR]] / Harbor world these all inhabit is invented for exactly that reason, and the four pages below are coherent within it.

## The four shapes

| Shape | The page's question | Made-up example | Live counterpart |
|---|---|---|---|
| **Breadcrumb** | I am a leaf — where do I hang? | [[FEX Breadcrumb Spine]] | [[LUMEN Nudge]] |
| **Grouped** | My children sort into a few named groups | [[FEX Grouped Dispatch]] | [[Rolodex]] |
| **List** | My children each need their own sentence | [[FEX List Dispatch]] | [[Disk]] |
| **Stream** | My children are dated, so newest goes first | [[FEX Stream Spine]] | [[VOX]] |

## What each one is there to show

**[[FEX Breadcrumb Spine]] — that a table on a leaf is not a dispatch table.** The hardest call in practice is a leaf whose main content happens to *be* a table: it looks like a hub and is not one. This page carries a latency-budget table as its overview entity, directly under the one-line summary, with no masthead anywhere — the shape [[DAS spine]] § Breadcrumb spine specifies line by line.

**[[FEX Grouped Dispatch]] — that groups beat lists when groups exist.** Sixteen tools under four named group rows. The reader holds four things, not sixteen. It also shows the `+` régime: each group label links *down* to that group's own page, so the row is a container preview rather than the whole list.

**[[FEX List Dispatch]] — that a description is what you buy by giving up grouping.** Five machines, one row each, each with a sentence. A group row spends its right cell on links; a list row spends it on prose. When the prose is the point, that is the trade.

**[[FEX Stream Spine]] — that the marker follows the children, not the topic.** Four dated release pages under `^^^`. The same shape serves a trip list or a set of dated applications; and conversely a *stream* kept as H2s inside one file has no children at all and correctly ends `...`.

## The one thing all four share

**Every hub ends in an electric marker, and none of them hand-writes below it.** `...`, `---`, and `^^^` differ only in what the machine writes underneath — a single sweeping row, one row per child, or one row per child reversed. The reason is staleness, not tidiness: without a marker a newly-added child is invisible and nothing ever says so. In the live vault that failure is currently 36 pages deep, worst at 189 hidden children ([[DAS spine]] § The catchall is not optional).

A breadcrumb page is the exception that proves it — it has no children, so there is nothing to go stale, which is why it carries no table at all.
