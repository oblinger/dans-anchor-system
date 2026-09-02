---
name: stacked-table
description: "*Slot* — a table whose related columns stack into one cell, sub-rows separated by structural `<br/>`"
tools: Read
user_invocable: false
group: slot
---

# Stacked table

A **stacked table** is a markdown table that folds related columns into one physical column — each cell holding sub-rows separated by `<br/>` — so a wide record fits a readable table. Minted 2026-09-01 on [[MED Pills]] (Drug/Dose · Filled-by/#Rx · Last-ordered/Run-out).

**The header declares the schema.** A header cell written `Drug<br/>Dose` declares a 2-stack; every body cell in that column carries exactly one structural `<br/>`. The table is self-describing — no side config, no separate schema doc.

**Two spellings of the break carry two meanings, and the polarity is load-bearing:**

- **`<br/>` — structural.** The sub-column separator, typed only deliberately (agents, scripts, templates). Arity-checked against the header.
- **`<br>` — cosmetic.** A soft wrap inside one sub-cell, for a value too long for the column — and exactly what **Obsidian's Shift+Return emits**, so a hand-added wrap is legal as typed. Parsers and checks ignore it.

The polarity is chosen so the casual keystroke is the harmless spelling: an accidental Shift+Return can only *under*-declare structure (a missing `<br/>`, which the arity check flags), never mint a phantom sub-row. A literal newline inside a row is never a break — it ends the row and shatters the table. Missing sub-values are `—`.

## When this facet applies

Any hand-maintained table whose header cells contain `<br/>`. That header row is the facet's selector — the ruleset reaches the table by content, not by file placement.

## Graduation — heavy writes mean the table wants to be electric

A stacked table is the right form for low-churn, hand-tended data. When agents start generating many rows, the rows have a store somewhere and the table should become a **render** of it (the [[DAS electric-zone]] pattern: queries.md from the backlog, dispatch zones from the command store). No write API for stacked tables exists on purpose — reads are cheap inline, malformed writes are caught by the arity check, and heavy-write tables graduate out rather than getting gymnastics tooling. (Dan + Atticus, 2026-09-01.)

## Ruleset

[[R-stacked-table]] — arity, polarity, and the no-literal-newline invariant.
