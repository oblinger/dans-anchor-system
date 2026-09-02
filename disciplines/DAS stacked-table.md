---
name: stacked-table
description: "*Slot* — a table whose related columns stack into one cell, sub-rows separated by structural `<br/>`, declared by an explicit marker."
tools: Read
user_invocable: false
group: slot
---

| -[[DAS stacked-table]]- | : *Slot* — a table whose related columns stack into one cell, sub-rows separated by structural `<br/>`, declared by an explicit marker.<br>→ [[DAS]] → [[disciplines]] → [DAS stacked-table](hook://p/DAS%20stacked-table)  |
| --- | --- |
| Ruleset | [[R-stacked-table]],   |
| Examples | [[MED Pills]],   |

# DAS stacked-table

A **stacked table** is a markdown table that folds related columns into one physical column — each cell holding sub-rows separated by `<br/>` — so a wide record fits a readable table. Minted 2026-09-01 on [[MED Pills]] (Drug/Dose · Filled-by/#Rx · Last-ordered/Run-out).

**The header declares the schema.** A header cell written `Drug<br/>Dose` declares a 2-stack; every body cell in that column carries exactly one structural `<br/>`. The table is self-describing — no side config, no separate schema doc.

**Two spellings of the break carry two meanings, and the polarity is load-bearing:**

- **`<br/>` — structural.** The sub-column separator, typed only deliberately (agents, scripts, templates). Arity-checked against the header.
- **`<br>` — cosmetic.** A soft wrap inside one sub-cell, for a value too long for the column — and exactly what **Obsidian's Shift+Return emits**, so a hand-added wrap is legal as typed. Parsers and checks ignore it.

The polarity is chosen so the casual keystroke is the harmless spelling: an accidental Shift+Return can only *under*-declare structure (a missing `<br/>`, which the arity check flags), never mint a phantom sub-row. A literal newline inside a row is never a break — it ends the row and shatters the table. Missing sub-values are `—`.

## When this facet applies

Any table whose first header cell begins with the visible marker **`[=]`** — typeable as-is, no rewrite needed. The full form: every sub-row line of **that one corner cell** starts `[=] ` — the stack drawn once, in the top-left, and only there (body rows stay clean; a `[=]` in a body row is a finding). The reader sees the stack in the corner and knows the whole table follows it. The count of `[=]` lines in the header's first cell is the arity for the whole table. (Dan 2026-09-01: an invisible HTML-comment marker was considered and rejected — the marker must be on screen, cost no extra rows, and die only by deliberate deletion.)

## Cardinality

**Many** — a document may carry any number of stacked tables; each is declared and checked independently by its own marker.

## Graduation — heavy writes mean the table wants to be electric

A stacked table is the right form for low-churn, hand-tended data. When agents start generating many rows, the rows have a store somewhere and the table should become a **render** of it (the [[DAS electric-zone]] pattern: queries.md from the backlog, dispatch zones from the command store). No write API for stacked tables exists on purpose — reads are cheap inline, malformed writes are caught by the arity check, and heavy-write tables graduate out rather than getting gymnastics tooling. (Dan + Atticus, 2026-09-01.)

## Ruleset

[[R-stacked-table]] — arity, polarity, and the no-literal-newline invariant.

# BRIEF

Minted 2026-09-01 in-session (Dan + Atticus) out of the [[MED Pills]] restructure. Design decisions, each Dan's ruling: (1) the two-spelling polarity — `<br/>` structural / `<br>` cosmetic — chosen AFTER observing that Obsidian's Shift+Return writes a bare `<br>`, so the casual keystroke had to be the harmless spelling; (2) the explicit `<!-- stacked -->` marker replaced the header-content selector because a selector living in an editable cell dies silently ("it silently fails… I feel like we should propose a marker"); (3) no get/set tooling — reads are cheap inline, the arity check guards writes, heavy-write tables graduate to electric renders. When editing this spec keep the polarity's *reason* attached to the polarity — the assignment looks arbitrary without it and a future editor will be tempted to "simplify" it back to one spelling.
