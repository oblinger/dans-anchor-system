---
description: "made-up worked examples of the four spine shapes and the one exception"
---

| -[[FEX Spine Examples]]- | : made-up worked examples of the four spine shapes and the one exception<br>→ [[DAS]] → [[examples]] → [FEX Spine Examples](hook://p/FEX%20Spine%20Examples)  |
| --- | --- |
| Spec | [[DAS spine]],  [[DAS Dispatch Table]],   |
| Shapes | [[Harbor Latency Budget\|breadcrumb]],  [[Bridges\|custom]],  [[Harbor Runbooks\|custom-grouped]],  [[Devtools\|custom-two-level]],  [[Harbor Hops\|list]],  [[Harbor Releases\|stream]],  [[Harbor Retrospectives\|custom-outward]],   |
| Related | [[FEX Dispatch Examples]],  [[DAS progressive-disclosure]],   |

# FEX Spine Examples
One invented page per shape — each *is* the shape it teaches, so it can be opened and read rather than described. **[[Harbor Latency Budget]] is the validated one:** Dan reads the first exemplar and holds it correct, and the rest are authored to be consistent with it.

| Spine shape | The question the page is answering | Made-up example | Live counterpart |
|---|---|---|---|
| **[[DAS spine#Breadcrumb spine\|Breadcrumb]]** | I am a leaf — where do I hang? | [[Harbor Latency Budget]] | [[LUMEN Nudge]] |
| **[[DAS spine#Custom spine\|Custom]]** — flat | I name my children by hand; the `...` is a safety valve | [[Bridges]] | [[HUD]] |
| **[[DAS spine#Custom spine\|Custom]]** — grouped | …and they sort under a few plain-text labels | [[Harbor Runbooks]] | [[Rolodex]] |
| **[[DAS spine#Custom spine\|Custom]]** — two-level | …and each label is itself a page, marked `+` | [[Devtools]] | [[SKA]] |
| **[[DAS spine#Custom spine\|Custom]]** — outward-pointing | …and what it names is not in my folder at all, so there is no `...` | [[Harbor Retrospectives]] | [[STARTUPPER]] |
| **[[DAS spine#List spine\|List]]** | The machine writes a row per child, each with its own sentence | [[Harbor Hops]] | [[Disk]] |
| **[[DAS spine#Stream spine\|Stream]]** | The same, reversed — my children are dated, so newest goes first | [[Harbor Releases]] | [[VOX]] |
| *[[DAS spine#Exceptions\|Exception]]* — redirect | *I organize nothing; I hand you two or three destinations and stop* | — | [[AI Safety]] |

**Four shapes, four of the rows one shape wearing four arrangements, and one exception.** Rows 2–5 are all the **custom** spine — what separates them is how the author laid the rows out and what they point at, which is worth learning and is not a difference in what the page *is*. Only the last row is not a spine ([[DAS spine]] § Exceptions).

**The redirect has no made-up example yet**, because the Harbor world has nothing to redirect to. It is the one row of this gallery that cannot be opened and read, which is a gap in the gallery rather than in the taxonomy.

**Every page in this table was run through `spine_check` on 2026-08-12, and two of them were teaching the opposite of what they said.** [[Bridges]] and [[Devtools]] each named their children by hand — `Bridges Studio`, `Devtools Build` — and **every one of those links dangled**, because neither page fronted a folder. Their mandatory `...` therefore had nothing of their own to sweep and swept the flat `examples/` directory instead: **45 unrelated pages apiece**, rendered directly beneath a callout reading *"the catchall should stay nearly empty."* Both now front real folders with real children, matching [[Harbor Runbooks]], and both check clean. The repair also resolved five links from [[Harbor Latency Budget]] — the validated exemplar — which had been pointing into the same void.

**The one refinement that came out of the sweep.** [[STARTUPPER]] is a **custom** spine, not an exception, and Dan was right to ask why it had been filed as one. But it fronts no folder — its members live all over `AT/` and are gathered by a tag — so its `...` could only sweep its sibling *group* pages, which are not members. Its own BRIEF had predicted that in writing and instructed *"do NOT add a `...` catchall"*; the marker was there anyway, carrying exactly the five wrong pages it had named. Removed. This is the boundary of Q5's *"you still want the dot, dot, dot"* ruling and does not contradict it: the marker is mandatory because a **folder** can gain a child nobody lists, so on a page that fronts no folder the rationale is absent and the marker is actively harmful. [[DAS spine]] § The catchall is not optional already states it that way — *"the mandatory marker turns on whether the page fronts a folder"* — and [[Harbor Retrospectives]] is the made-up exemplar of the same arrangement.

**[[Legal]] was the custom-flat counterpart until 2026-08-12 and [[HUD]] replaced it, on Dan's read: *"the legal table is messed up… a lot of white space… it's certainly not a representative example."*** He was right twice over. Two of Legal's hand rows carry **6,118** and **2,625** characters of links in a single cell, which no table renders legibly — a page whose children have children, doing on one row what a sub-page should do. And underneath that it had been **actively corrupted**: HookAnchor's daemon had prepended a *second* identity cell above the first, separated by a **6,550-character** padded alignment row, which is where the white space came from. That duplication appeared after the page was committed clean, so it was written by the daemon rather than by hand — filed as [[HA Backlog#^F282|HA F282]]. The duplicate is removed and Legal checks clean; the two oversized rows are the user's content to restructure, not a spine defect. [[HUD]] is the better teacher anyway: seven hand rows each carrying its own gloss, every child named, and a `...` that is **present and empty** — which is precisely the case Q5 was ruling on.

**The redirect row reads as `[S01] no spine at all` to the checker, and that is correct.** [[AI Safety]] is listed as an *exception* precisely because a redirect is not a spine; the checker has no notion of a sanctioned exception, so every redirect page in the vault reports S01. Worth knowing before the count is read as a defect total.

## Overview

These pages are **deliberately made up**. The vault's own pages are the right exemplars for a *live* shape — click one and watch HookAnchor render it — but this repo ships publicly, so a teaching gallery built from real vault content would leak it. The [[HBR]] / Harbor world they inhabit is invented for exactly that reason.

**Each example is named for what it is, not for what it teaches.** The identity cell and the H1 always agree — `Harbor Runbooks` is a page about runbooks that *happens* to be the grouped-custom exemplar. Only this gallery carries an `FEX` name, because a gallery is what it is.

## What each one is there to show

**[[Harbor Latency Budget]] — that a table on a leaf is not a dispatch table.** The hardest call in practice is a leaf whose main content *is* a table: it looks like a hub and is not one. Breadcrumb, H1, one sentence, then the budget table as the heart, with no masthead anywhere.

**[[Harbor Runbooks]] — that three groups beat eight rows.** Eight runbooks under `Incident` / `Routine` / `Recovery`. The labels are plain text, not links: every child is already in this folder, and the grouping only tells you which one you want.

**[[Devtools]] — that a group label can be a page.** Sixteen tools under four `+` rows, each row a container with its own spine. This is the shape [[Harbor Runbooks]] is *not*, and the pair is meant to be read side by side. It also carries a heart — the pipeline table — so it shows a masthead and a heart on one page without them being confused.

**[[Bridges]] — that hand-listed rows are not a list spine.** Four machines, each with an authored row above a `...` safety valve. Visually identical to a list spine, opposite ownership — and ownership is the whole selector, which is why these two are the pair that teaches the shape set.

**[[Harbor Retrospectives]] — that a spine can leave its own folder and still be a custom spine.** Its rows point at pages elsewhere entirely, grouped by consequence rather than location. It carries no marker, and the reason is not that it points outward — it is that it fronts no folder, so there is nothing for a marker to sweep. [[STARTUPPER]], the live counterpart, points just as far outward and *does* carry a `...`, because it does front one.

**[[Harbor Hops]] — that `---` is not `...` written longer.** Five hops, and the machine writes one row per hop with its own description. `...` would collapse all five into a single compact row; the per-child sentence is the entire reason to choose `---`. It deliberately has **no heart**: a pure index's spine is its content.

**[[Harbor Releases]] — that the marker follows the children, not the topic.** Four dated release pages under `^^^`. The same shape serves a trip list or dated applications; a *stream* kept as H2s inside one file has no children at all and correctly ends `...`.

## The one thing they share

**Every hub ends in an electric marker, and none of them hand-writes below it.** `...`, `---`, and `^^^` differ only in what the machine writes underneath — one sweeping row, one row per child, or one row per child reversed. The reason is staleness: without a marker a newly-added child is invisible and nothing says so. In the live vault that failure is currently **16 pages deep, 44 hidden children**, worst at 14 ([[DAS spine]] § The catchall is not optional — which also records why the figure used to read 36/189, and what the checker was counting instead).

A breadcrumb page is the exception that proves it — no children, so nothing to go stale, which is why it carries no table at all.
