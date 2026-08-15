---
description: "the subs facet — an optional root-level {slug} Subs/ folder holding week-scale subprojects, each a {SLUG}{NNN} - Name/ folder numbered from the anchor's own F-mint"
group: folder
---

| -[[DAS Subs]]- | → [[DAS]] → [[FCT]] → [DAS Subs](hook://p/DAS%20Subs)  |
| --- | --- |
| Related | [[DAS Features]],  [[DAS Backlog]],  [[DAS Dot Anchor]],  [[DAS Anchor Page]],   |
| Examples | [[A2X Subs\|worked instance]] (holding [[A2X009 - Improved Make Miss Classifier\|A2X009]] and [[A2X010 - Vasu Demo\|A2X010]]) |
| Rules | [[R-subs]],   |

# DAS Subs
Week-scale subprojects inside an anchor — an optional root-level `{slug} Subs/` folder holding one `{SLUG}{NNN} - Name/` folder per subproject, numbered from the anchor's own F-mint so no new slug is ever created.

**TLDR** — a **subproject** is a focused sub-effort of days-to-weeks that deserves its own folder: it starts as one feature-doc-like page and may grow sibling docs, its own spine, even its own backlog — all optional. The subproject folder is `{SLUG}{NNN} - Name/`, where `{SLUG}{NNN}` is the anchor slug fused to an F-number minted by the ordinary `state define <anchor> Backlog F+` — a subproject is *just a big feature* from the mint's point of view, which is what keeps collision-avoidance free. Every internal file carries the `{SLUG}{NNN}` prefix. **Cardinality: one** — at most one `{slug} Subs/` folder per anchor, elective, holding many subproject folders. Retirement is the ordinary feature lifecycle: the backlog row goes `[Done]` and the folder stays as the record or is yored wholesale — no slug retirement, because no slug was minted. Decided as [[TINK331 - Subproject convention: short-lived sub-efforts inside an anchor|TINK F331]], 2026-08-14.

## Location

`{anchor}/{slug} Subs/` — at the **anchor root**, sibling of `{slug} Design/`, `{slug} Track/`, and `{slug} Log/`. Not inside Track or Design (Dan's explicit ruling, F331 Q2): subprojects grow many internal files and would visually swamp a flat Features listing, and a subproject is neither pure design content nor pure tracking metadata.

The folder holds an index page `{slug} Subs.md` with a dispatch table and a `...` catch-all, so a subproject folder dropped in is surfaced without being hand-listed. The **container folder itself carries no `.anchor`** — it is a zone of the parent anchor, not an anchor of its own.

## Naming grammar

- **Folder** — `{SLUG}{NNN} - Name/` (plain ASCII hyphen, space each side). `{SLUG}` is the parent anchor's slug in its own casing; `{NNN}` is the F-number, zero-padded to three digits.
- **Top page** — `{SLUG}{NNN} - Name.md`, the folder-doc form the workflow resolvers already handle.
- **Internal files** — `{SLUG}{NNN} <doc name>.md` (e.g. `A2X010 Vasu Tasks.md`). The short fused prefix keeps every filename unambiguous vault-wide while visibly naming the parent universe.
- **`.anchor`, when present** — declares the subproject's **own** fused slug (`slug: A2X010`), never the parent's; a duplicate parent slug makes anchor resolution ambiguous.

## Numbering — the mint is the registry

Subprojects draw numbers from the anchor's existing F-sequence via `state define <anchor> Backlog F+`, interleaving with plain features in one monotonic namespace. No separate registry, no new slug vocabulary, no reuse hazard: the backlog row minted alongside the folder is the subproject's tracking handle for its whole life.

## Discovery

No standing alias by default. The parent anchor's dispatch table carries a hand-authored row (above the separator) linking the live subprojects — the path is always: jump to the parent page, click through. An `ha` alias for the single currently-hot subproject is an optional convenience, deleted at close-out.

## Retirement

The backlog row goes `[Done]`; the folder either stays in place as the feature's record or is yored wholesale. Nothing else to clean up — no slug was minted, so the year-prefix slug-retirement convention is never involved. This cheapness is the point: subprojects are minted far more often than real anchors.

## When appropriate

**Use a subproject when** a sub-effort will accumulate several files over days-to-weeks and reads as one focused project. **Do not when** the work fits a single feature doc — that stays a plain `{SLUG}{NNN} - Title.md` in `{slug} Design/{slug} Features/`, and the Subs folder is never scaffolded ahead of need.

## Tooling

The workflow resolvers (`backlog-edit.py`) glob `* Subs/{stem}/{stem}.md` and `* Subs/{stem}.md` beside the Features locations, so `state` verbs resolve a subproject's top page exactly as they resolve a feature doc.

## Audit

[[R-subs]] — zone location and index page, subproject folder/top-page naming, internal-file prefix, `.anchor` discipline, and the live-backlog-row invariant. All stated, not yet checked: the convention is one day old with one live instance, and checkers wait for a second instance to show which invariants actually bind.

# BRIEF

- **What this is** — the folder-form home for week-scale sub-efforts, specified by [[TINK331 - Subproject convention: short-lived sub-efforts inside an anchor|TINK F331]]. The pilot instance is [[A2X Subs]]; treat it as normative for layout.
- **The container folder must NOT be an anchor.** Only the subproject folders inside it may carry `.anchor` (declaring their own fused slug). HookAnchor's daemon has repeatedly auto-stamped an empty `.anchor` onto the container folder when nearby files change — remove it when it appears; a container `.anchor` makes the zone resolve as a competing anchor.
- **Never put the parent's slug in a subproject's `.anchor`** — resolution goes ambiguous. The fused slug (`slug: A2X010`) or nothing.
- **Subprojects are not Features-folder content.** A numbered folder in `{slug} Design/{slug} Features/` is the *folder-doc feature* form; the Subs folder exists precisely to keep multi-file subprojects from swamping that listing. One home per item, chosen by whether it reads as one doc or one project.
