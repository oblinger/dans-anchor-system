---
description: "cheat sheets and spaced-repetition flashcards for an anchor topic"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Output]] → [FCT Cards](hook://p/FCT%20Cards)

# FCT Cards
Facet spec for the optional `{NAME} Cards.md` page — a three-tier mix of cheat sheets and spaced-repetition flashcards that lets an anchor double as a study deck for its own topic.

**Related:** [[FCT Brief]],  [[FCT Anchor Page]],  [[CAB Aspects]],  [[FCT Output]]
**Examples:** [[DOCPY Cheat Cards\|cheat-sheet-heavy example]],  [[TPM Core Cards\|summary+detail cards example]]

**TLDR** — A `{NAME} Cards.md` file (one per anchor, optional) holds three tiers of study material: bold-heading cheat sheets (reference, no SR), summary cards (the gist/rule), and detail cards (exceptions/gotchas). Requires an SR tag on line 1, `-?-` separators, 69-char line width, and `.` for in-card blank lines.

**Cardinality:** one per anchor — each anchor has at most one Cards file (`{NAME} Cards.md`).

The `{NAME} Cards.md` document contains cheat sheets and spaced repetition flashcards for a given topic. It lives in the anchor folder or a subfolder dedicated to cards.

**Working example:** [[CAE Cards]] — a real cards file (cheat sheets + summary + detail cards).

# Document Structure

A cards page (`{NAME} Cards.md`) is one file. Its parts, top to bottom:

- **SR tag** — a `#sr-tag` on the first line (required by the spaced-repetition plugin).
- **H1** — `# {NAME} Cards`, followed by the standard F060 dispatch-table placeholder.
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
-[[{NAME} Cards]]- \| \|` + standard separator)
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

# RULESET R-cards
include::
where:: file:{ANCHOR}/**/{NAME} Cards.md
description:: the `{NAME} Cards.md` study-deck format

What `/audit` checks on a cards page. Optional — cardinality one per anchor. Format of this set: [[FCT Ruleset]].

### RULE R-cards-01 — First line is an SR tag (checked)

The very first line is a spaced-repetition tag (e.g. `#flashcards`, `#py-cheat`) from the current tag set, so the SR plugin picks up the cards.

**Check pattern:** line 1 matches `^#[a-z0-9-]+`; the tag is one of the registered SR tags.

**Why:** the plugin scans for the tag on line 1; without it no card is scheduled.

### RULE R-cards-02 — H1 `# {NAME} Cards` + F060 dispatch placeholder follow the tag (checked)

After the SR tag, the page opens with `# {NAME} Cards` and the standard F060 dispatch-table placeholder.

**Check pattern:** the first H1 is `# {slug} Cards`, immediately followed by the dispatch-table placeholder rows.

### RULE R-cards-03 — Each SR card separates title from answer with `-?-` (checked)

Every summary/detail card puts `-?-` on its own line between the card title and the answer.

**Check pattern:** each card block contains a lone `-?-` line; no card has a title with no `-?-`.

### RULE R-cards-04 — Card lines ≤ 69 chars; blank-in-card is `.` (checked)

SR-card content lines are at most 69 characters (longer lines wrap in the review UI), and an in-card blank is written as `.` on its own line (a true blank line truncates the card). Cheat sheets are exempt from the width limit.

**Check pattern:** within any SR card, no content line exceeds 69 chars and no truly-empty line appears.

### RULE R-cards-05 — Three tiers in order: cheat sheets → summary cards → detail cards (stated)

The file is organized cheat sheets first (`## **HEADING**` + reference code block, not reviewed), then summary cards (the unifying rule), then detail cards (surprising exceptions). Summary cards teach the rule; detail cards teach the exceptions.

# BRIEF

- **This file is the facet spec for `{NAME} Cards.md`**, not a cards file itself. Edits here change the *rule* every cards page across the vault must satisfy; never paste real flashcard content into this spec.
- **Not for**: project-wide markdown rules (those live in [[R-markdown]] / CLAUDE.md), generic spaced-repetition theory, or plugin documentation. Keep the scope to the shape of `{NAME} Cards.md` and the three-tier cheat-sheet / summary-card / detail-card model.
- **Inclusion test**: a rule belongs here only if a cards-page author would break their page by violating it (SR tag on line 1, `-?-` separator, 69-char line width, `.` for in-card blank lines, F060 dispatch-table placeholder under the H1). Cross-cutting CAB rules go in their own facet spec.
- **Load-bearing constraints**: the SR tag list at the bottom of `## File Layout and Formatting Rules` is consumed by the spaced-repetition plugin — add new tags here when they enter use, never silently. The 69-character width and the `.`-for-blank-line trick are plugin-imposed; do not soften them to "recommended."
- **Naming + linking**: the canonical path is `{NAME} Docs/{NAME} User/{NAME} Cards.md`; cite the worked instance as [[CAE Cards]] — do NOT inline a reference copy of it (a cards page is its own renderable doc; embedding one blurs spec-vs-instance). Use fenced code (not tables) for the format snippets in § Formats / § File Layout so the `-?-` separator and SR formatting render literally.
- **Body discipline**: less is more — the three-tier structure (cheat sheet / summary / detail) is the load-bearing content. Resist adding tooling notes, plugin-config detail, or per-topic guidance; those belong in the cards file itself or a sibling skill, not in this spec.
