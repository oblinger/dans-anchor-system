---
description: "cheat sheets and spaced-repetition flashcards for an anchor topic"
---

# DAS Cards
Facet spec for the optional `{slug} Cards.md` page — a three-tier mix of cheat sheets and spaced-repetition flashcards that lets an anchor double as a study deck for its own topic.

| -[[DAS Cards]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Cards](hook://p/DAS%20Cards) |
| --- | --- |
| Related | [[DAS Brief]],  [[DAS Anchor Page]],  [[DAS Aspects]],  [[DAS Output]],   |
| Examples | [[DOCPY Cheat Cards\|cheat-sheet-heavy example]],  [[TPM Core Cards\|summary+detail cards example]],   |
| Rules | [[R-cards]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Backlog]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[facets/DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Disciplines Brief]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Outputs]],  [[DAS Plan Dispatch]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS TSK User Guide]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — A `{slug} Cards.md` file (one per anchor, optional) holds three tiers of study material: bold-heading cheat sheets (reference, no SR), summary cards (the gist/rule), and detail cards (exceptions/gotchas). Requires an SR tag on line 1, `-?-` separators, 69-char line width, and `.` for in-card blank lines.

**Cardinality:** one per anchor — each anchor has at most one Cards file (`{slug} Cards.md`).

The `{slug} Cards.md` document contains cheat sheets and spaced repetition flashcards for a given topic. Its canonical path is `{slug} Docs/{slug} User/{slug} Cards.md` — it lives in the anchor folder or a subfolder dedicated to cards.

**Working example:** [[CAE Cards]] — a real cards file (cheat sheets + summary + detail cards).

# Document Structure

A cards page (`{slug} Cards.md`) is one file. Its parts, top to bottom:

- **SR tag** — a `#sr-tag` on the first line (required by the spaced-repetition plugin).
- **H1** — `# {slug} Cards`, followed by the standard F060 dispatch-table placeholder.
- **Cheat sheets** — `## **HEADING**` + grouped code-block reference content (not reviewed as cards).
- **Summary cards** — SR cards (`title` / `-?-` / answer) teaching the unifying rule behind a cheat sheet.
- **Detail cards** — SR cards for surprising exceptions / gotchas.

The literal format of each part is given below; the three-tier model is detailed in § Three-Tier Structure.

## Formats

Three kinds of entries — cheat sheets, summary cards, and detail cards:

**Cheat sheet** — reference only, not spaced repetition:

## **`PYTHON STRING METHODS`**
```
CASE:    lower  upper  capitalize  title
STRIP:   strip  lstrip  rstrip
SPLIT:   split  rsplit  splitlines  join
SEARCH:  find  rfind  index  rindex  count
TEST:    in  startswith  endswith
MODIFY:  replace  zfill  center  ljust  rjust
FORMAT:  f"..."  format  %
```

**Summary card** — SR card for the gist/rule:

> 4 string case methods
> -?-
> ```
> "hELLo".lower()       → 'hello'
> "hELLo".upper()       → 'HELLO'
> "hELLo".capitalize()  → 'Hello'  ˹first up, rest low˺
> "hELLo".title()       → 'Hello'  ˹each word capped˺
> ```

**Detail card** — SR card for a surprising exception:

> strip() takes a character SET
> -?-
> `"_-ab-_".strip('_-')  → 'ab'`
> Strips any char in the set, not the substring.
> Order doesn't matter: `strip('-_')` is the same.

## File Layout and Formatting Rules

> `#sr-tag` — a spaced repetition tag (first line; required by the SR plugin)
>
-[[{slug} Cards]]- \| \|` + standard separator)
>
> `## **CHEAT SHEET TOPIC A**`
> code block with grouped reference content
>
> `## **CHEAT SHEET TOPIC B**`
> code block with grouped reference content
>
> `Summary card title`
> `-?-`
> gist of a cheat sheet — the unifying principle
>
> `Detail: surprising behavior X`
> `-?-`
> one specific gotcha or exception

- **Tag** — first line must be an SR tag (see list below) so the spaced repetition plugin picks up the cards
- **Max line width: 69 characters** — longer lines wrap in the review UI
- **Card separator** — `-?-` on its own line between card title and answer
- **Blank lines inside a card** — use `.` on its own line instead of a true blank line, which cuts off the card
- **Cheat sheets** have no width constraint (not reviewed as cards)

Current SR tags: `#flashcards` `#cv` `#ai` `#ml` `#ml2` `#dl` `#card` `#py-cheat` `#py-detail` `#pytorch` `#numpy` `#leet` `#comp` `#stat` `#docpy-anth-detail` `#docpy-anth-cheat` `#afi`

## Three-Tier Structure

### 1. Cheat Sheets (top of file, not spaced repetition)

Plain reference material — not flashcards, not tested. Something you look at to understand a topic quickly. Each cheat sheet has a bold `## **HEADING**` and a code block that groups an interface or concept area into a scannable summary.

### 2. Summary Cards (spaced repetition)

Flashcards that capture the **cohesive unifying principles** behind a cheat sheet. These deliberately violate the typical SR rule of "one atomic idea per card" — they teach the gist, the big picture, the rule.

One cheat sheet might produce 1–3 summary cards depending on how much content it covers. The goal is to internalize the organizing logic behind the reference material.

### 3. Detail Cards (spaced repetition)

Flashcards about **counterintuitive, surprising exceptions** — things that would trip you up even if you understood the general rule. These follow the standard SR approach: one isolated, specific gotcha per card.

- Summary cards teach the **rule**
- Detail cards teach the **exceptions to the rule**

## Maintenance

Add cheat sheets as reference material is learned. Add summary and detail cards as understanding deepens. The SR plugin handles scheduling automatically.

# BRIEF

*(Maintainer note — this file is the facet spec for `{slug} Cards.md`, not a cards file itself: edits here change the rule every cards page must satisfy, so never paste real flashcard content in, and cite the worked instance as [[CAE Cards]] rather than inlining a copy. Inclusion test: a rule belongs here only if a cards-page author would break their page by violating it; cross-cutting CAB rules go in their own facet spec. The SR tag list in § File Layout and Formatting Rules is consumed by the spaced-repetition plugin — add new tags there when they enter use, never silently.)*
