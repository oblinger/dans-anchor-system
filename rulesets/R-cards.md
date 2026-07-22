# RULESET R-cards
include::
where:: `file:{anchor}/**` whose **first line is an SR tag** (`^#[a-z0-9-]+`) — a `{slug} {topic}.md` study-card file
description:: the `{slug} {topic}.md` study-card format (one cheat sheet + its summary & detail cards)

What `/audit` checks on a study-card file — one cheat sheet plus the summary and detail cards distilled from it, one file per sheet. Optional — cardinality one per cheat-sheet topic (an anchor has as many as it has topics). The identifying signal is the line-1 SR tag (R-cards-01); the anchor page indexes the files. Format of this set: [[DAS Ruleset]]. Facet: [[DAS Cards]]; worked example: [[numpy bcast]].

### RULE R-cards-01 — First line is an SR tag (checked)

The very first line is a spaced-repetition tag (e.g. `#numpy`, `#flashcards`, `#py-cheat`) from the current tag set, so the SR plugin picks up the cards. This line is also what identifies the file as a study-card file at all.

**Check pattern:** line 1 matches `^#[a-z0-9-]+`; each tag on the line is one of the registered SR tags.

**Why:** the plugin scans for the tag on line 1; without it no card is scheduled.

### RULE R-cards-02 — H1 is a backlink to the anchor + the topic, then a one-line summary (checked)

After the SR tag, the file opens with `# [[{parent}]] {topic}` — the anchor page as a live wiki-link backlink, then the topic name — immediately followed by a one-line summary of the topic. A study-card file is a **content leaf**, so it takes this backlink H1, **not** an anchor dispatch table. The `{topic}` in the H1 matches the `{topic}` in the filename (`{slug} {topic}.md`).

**Check pattern:** the first H1 matches `# \[\[{parent}\]\] {topic}`; the next non-blank line is a one-line summary (no dispatch-table placeholder).

### RULE R-cards-03 — Each SR card separates title from answer with `-?-` (checked)

Every summary/detail card puts `-?-` on its own line between the card title and the answer.

**Check pattern:** each card block contains a lone `-?-` line; no card has a title with no `-?-`.

### RULE R-cards-04 — Card lines ≤ 69 chars; blank-in-card is `.` (checked)

SR-card content lines are at most 69 characters (longer lines wrap in the review UI), and an in-card blank is written as `.` on its own line (a true blank line truncates the card). The cheat sheet is exempt from the width limit.

**Check pattern:** within any SR card, no content line exceeds 69 chars and no truly-empty line appears.

### RULE R-cards-05 — One sheet, then its two card tiers, in order: cheat sheet → summary cards → detail cards (stated)

The file carries exactly one cheat sheet (`## **HEADING**` + reference code block, not reviewed) at the top, then `## Summary Cards` (the unifying rule of that sheet), then `## Detail Cards` (its surprising exceptions). Summary cards teach the rule; detail cards teach the exceptions. Multiple topics mean multiple files — never several cheat sheets in one file.
