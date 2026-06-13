---
description: cheat sheets and flashcards
---
# FCT Cards

Facet spec for the optional `{NAME} Cards.md` page — a three-tier mix of cheat sheets and spaced-repetition flashcards (summary + detail) that lets an anchor double as a study deck for its own topic.

**Location:** `{NAME} Docs/{NAME} User/{NAME} Cards.md`


The `{NAME} Cards.md` document contains cheat sheets and spaced repetition flashcards for a given topic. It lives in the anchor folder or a subfolder dedicated to cards.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example

```
CAE Cards/
└── CAE Cards.md
```

**CAE Cards.md:**

```markdown
#flashcards

# CAE Cards

| -[[CAE Cards]]- | |
| --- | --- |
| --- | |


## **`CAE CLI COMMANDS`**
```
ADD:     tsk add "cmd" --at TIME --pri N
LIST:    tsk list [--status STATUS]
STATUS:  tsk status ID
CANCEL:  tsk cancel ID
HISTORY: tsk history [--limit N]
RETRY:   tsk retry ID
```

> 6 tsk CLI commands
> -?-
> ```
> add      — schedule a new task
> list     — show tasks by status
> status   — detail for one task
> cancel   — remove a pending task
> history  — past task results
> retry    — re-queue a failed task
> ```

> tsk add --pri range
> -?-
> 1 (lowest) to 10 (highest), default 5.
> Higher priority tasks run first when
> multiple tasks are ready simultaneously.
```




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
> `# {NAME} Cards` — H1, followed by the standard F060 dispatch-table placeholder (`\| -[[{NAME} Cards]]- \| \|` + standard separator)
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

- **This file is the facet spec for `{NAME} Cards.md`**, not a cards file itself. Edits here change the *rule* every cards page across the vault must satisfy; never paste real flashcard content into this spec.
- **Not for**: project-wide markdown rules (those live in [[R-markdown]] / CLAUDE.md), generic spaced-repetition theory, or plugin documentation. Keep the scope to the shape of `{NAME} Cards.md` and the three-tier cheat-sheet / summary-card / detail-card model.
- **Inclusion test**: a rule belongs here only if a cards-page author would break their page by violating it (SR tag on line 1, `-?-` separator, 69-char line width, `.` for in-card blank lines, F060 dispatch-table placeholder under the H1). Cross-cutting CAB rules go in their own facet spec.
- **Load-bearing constraints**: the SR tag list at the bottom of `## File Layout and Formatting Rules` is consumed by the spaced-repetition plugin — add new tags here when they enter use, never silently. The 69-character width and the `.`-for-blank-line trick are plugin-imposed; do not soften them to "recommended."
- **Naming + linking**: the canonical path is `{NAME} Docs/{NAME} User/{NAME} Cards.md`; cite the worked example as [[CAE Cards]] and keep the reference block in sync if that file's shape changes. Use fenced code (not tables) for the cheat-sheet and card examples so the `-?-` separator and SR formatting render literally.
- **Body discipline**: less is more — the three-tier structure (cheat sheet / summary / detail) is the load-bearing content. Resist adding tooling notes, plugin-config detail, or per-topic guidance; those belong in the cards file itself or a sibling skill, not in this spec.
