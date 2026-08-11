---
description: "made-up worked examples of the seven spine shapes"
---

| -[[FEX Spine Examples]]- | : made-up worked examples of the seven spine shapes<br>→ [[DAS]] → [[examples]] → [FEX Spine Examples](hook://p/FEX%20Spine%20Examples)  |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Spec | [[DAS spine]],  [[DAS Dispatch Table]],   |
| Shapes | [[Harbor Latency Budget\|breadcrumb]],  [[Bridges\|curated]],  [[Harbor Runbooks\|grouped]],  [[Devtools\|two-level]],  [[Harbor Hops\|list]],  [[Harbor Releases\|stream]],  [[Harbor Retrospectives\|external]],   |
| Related | [[FEX Dispatch Examples]],  [[DAS progressive-disclosure]],   |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[Clarifier]],  [[CSE]],  [[DAS Examples]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[ESP]],  [[Espresso]],  [[FEX Agenda]],  [[FEX API]],  [[FEX API Design]],  [[FEX Architecture]],  [[FEX Claude]],  [[FEX Completed Roadmap]],  [[FEX CSE]],  [[FEX Decisions]],  [[FEX Decisions Details]],  [[FEX Facet]],  [[FEX Figure Page]],  [[FEX Files]],  [[FEX Icebox]],  [[FEX Inbox]],  [[FEX Minimal Facet]],  [[FEX Minimal Skill]],  [[FEX Project Root]],  [[FEX Repo]],  [[FEX Roadmap]],  [[FEX Rules]],  [[FEX Scheduler]],  [[FEX Skill]],  [[FEX Stories]],  [[FEX System Design]],  [[Forum Stories]],  [[HBR PRD User Stories]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

# FEX Spine Examples
One invented page per spine shape — each *is* the shape it teaches, so it can be opened and read rather than described.

| Spine shape | The question the page is answering | Made-up example | Live counterpart |
|---|---|---|---|
| **[[DAS spine#Breadcrumb spine\|Breadcrumb]]** | I am a leaf — where do I hang? | [[Harbor Latency Budget]] | [[LUMEN Nudge]] |
| **[[DAS spine#Curated spine\|Curated]]** | I list my children by hand; the catchall is a safety valve | [[Bridges]] | [[Legal]] |
| **[[DAS spine#Grouped spine\|Grouped]]** | My children sort under a few plain labels | [[Harbor Runbooks]] | [[Rolodex]] |
| **[[DAS spine#Two-level spine\|Two-level]]** | My groups are themselves pages, with `+` | [[Devtools]] | [[SKA]] |
| **[[DAS spine#List spine\|List]]** | My children each need their own sentence | [[Harbor Hops]] | [[Disk]] |
| **[[DAS spine#Stream spine\|Stream]]** | My children are dated, so newest goes first | [[Harbor Releases]] | [[VOX]] |
| **[[DAS spine#External spine\|External]]** | What I organize is not in my folder at all | [[Harbor Retrospectives]] | [[STARTUPPER]] |

## Overview

These pages are **deliberately made up**. The vault's own pages are the right exemplars for a *live* shape — click one and watch HookAnchor render it — but this repo ships publicly, so a teaching gallery built from real vault content would leak it. The [[HBR]] / Harbor world they inhabit is invented for exactly that reason.

**Each example is named for what it is, not for what it teaches.** The identity cell and the H1 always agree — `Harbor Runbooks` is a page about runbooks that *happens* to be the grouped exemplar. Only this gallery carries an `FEX` name, because a gallery is what it is.

## What each one is there to show

**[[Harbor Latency Budget]] — that a table on a leaf is not a dispatch table.** The hardest call in practice is a leaf whose main content *is* a table: it looks like a hub and is not one. Breadcrumb, H1, one sentence, then the budget table as the heart, with no masthead anywhere.

**[[Harbor Runbooks]] — that three groups beat eight rows.** Eight runbooks under `Incident` / `Routine` / `Recovery`. The labels are plain text, not links: every child is already in this folder, and the grouping only tells you which one you want.

**[[Devtools]] — that a group label can be a page.** Sixteen tools under four `+` rows, each row a container with its own spine. This is the shape [[Harbor Runbooks]] is *not*, and the pair is meant to be read side by side. It also carries a heart — the pipeline table — so it shows a masthead and a heart on one page without them being confused.

**[[Bridges]] — that hand-listed rows are not a list spine.** Four machines, each with an authored row above a `...` safety valve. Visually identical to a list spine, opposite ownership.

**[[Harbor Retrospectives]] — that a spine can leave its own folder.** Its rows point at pages elsewhere entirely, grouped by consequence rather than location, and it carries no marker because a marker could only ever compute the wrong set.

**[[Harbor Hops]] — that `---` is not `...` written longer.** Five hops, and the machine writes one row per hop with its own description. `...` would collapse all five into a single compact row; the per-child sentence is the entire reason to choose `---`. It deliberately has **no heart**: a pure index's spine is its content.

**[[Harbor Releases]] — that the marker follows the children, not the topic.** Four dated release pages under `^^^`. The same shape serves a trip list or dated applications; a *stream* kept as H2s inside one file has no children at all and correctly ends `...`.

## The one thing they share

**Every hub ends in an electric marker, and none of them hand-writes below it.** `...`, `---`, and `^^^` differ only in what the machine writes underneath — one sweeping row, one row per child, or one row per child reversed. The reason is staleness: without a marker a newly-added child is invisible and nothing says so. In the live vault that failure is currently **16 pages deep, 44 hidden children**, worst at 14 ([[DAS spine]] § The catchall is not optional — which also records why the figure used to read 36/189, and what the checker was counting instead).

A breadcrumb page is the exception that proves it — no children, so nothing to go stale, which is why it carries no table at all.
