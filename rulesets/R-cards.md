# RULESET R-cards
include::
where:: `file:{anchor}/**/{slug} Cards.md`
description:: the `{slug} Cards.md` study-deck format

What `/audit` checks on a cards page. Optional — cardinality one per anchor. Format of this set: [[DAS Ruleset]].

### RULE R-cards-01 — First line is an SR tag (checked)

The very first line is a spaced-repetition tag (e.g. `#flashcards`, `#py-cheat`) from the current tag set, so the SR plugin picks up the cards.

**Check pattern:** line 1 matches `^#[a-z0-9-]+`; the tag is one of the registered SR tags.

**Why:** the plugin scans for the tag on line 1; without it no card is scheduled.

### RULE R-cards-02 — H1 `# {slug} Cards` + F060 dispatch placeholder follow the tag (checked)

After the SR tag, the page opens with `# {slug} Cards` and the standard F060 dispatch-table placeholder.

**Check pattern:** the first H1 is `# {slug} Cards`, immediately followed by the dispatch-table placeholder rows.

### RULE R-cards-03 — Each SR card separates title from answer with `-?-` (checked)

Every summary/detail card puts `-?-` on its own line between the card title and the answer.

**Check pattern:** each card block contains a lone `-?-` line; no card has a title with no `-?-`.

### RULE R-cards-04 — Card lines ≤ 69 chars; blank-in-card is `.` (checked)

SR-card content lines are at most 69 characters (longer lines wrap in the review UI), and an in-card blank is written as `.` on its own line (a true blank line truncates the card). Cheat sheets are exempt from the width limit.

**Check pattern:** within any SR card, no content line exceeds 69 chars and no truly-empty line appears.

### RULE R-cards-05 — Three tiers in order: cheat sheets → summary cards → detail cards (stated)

The file is organized cheat sheets first (`## **HEADING**` + reference code block, not reviewed), then summary cards (the unifying rule), then detail cards (surprising exceptions). Summary cards teach the rule; detail cards teach the exceptions.
