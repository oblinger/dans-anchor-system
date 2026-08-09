---
name: spine
description: Discipline. Exactly two ways to open a file — a breadcrumb or a dispatch table — chosen by one question, plus the fixed line order that follows each.
user_invocable: false
---

# Spine Discipline

**Every file in the system opens one of exactly two ways.** Either a **breadcrumb** or a **dispatch table**. There is no third opening, and the choice is not a matter of taste.

The spine is the routing zone at the top of a document. Everything below it belongs to [[DAS progressive-disclosure]]; this discipline governs only the top, and it governs it strictly, because the top is the only part a scanning reader is guaranteed to see.

## The one question that selects the spine

> **Does this document organize other files?**

- **No** — it is about one thing, and owes the reader no named siblings. **Breadcrumb spine.**
- **Yes** — it stands over a set of children a reader should be handed. **Dispatch-table spine.**

That is the whole test. It is about the document's *role*, not its length, importance, or how much work went into it. A long, central, carefully-written document that organizes nothing takes a breadcrumb.

**The failure this exists to stop is a single-entity document wearing a dispatch table.** A masthead announces "I route you onward"; when the document routes nowhere, every row is either empty or invented, and the reader's first impression is of a hub that turns out to be a leaf. This is the common error and it is worth naming: the pull is that a masthead *looks* more finished. It isn't — it is a promise the document cannot keep.

## Breadcrumb spine — the line order is fixed

Five lines, in this order, immediately after frontmatter:

| Line | Content |
|---|---|
| 1 | `:>> [[kmr]] → [[SYS]] → … → [Name](hook://p/Name)` — the breadcrumb, first body line |
| 2 | `# Name` — the H1, with **no blank line** between it and the breadcrumb |
| 3 | One sentence saying what this document is |
| 4 | *(blank)* |
| 5 | **The overview entity** — the one main thing the document exists to hold |

Line 5 is the load-bearing one and the one most often got wrong. A document about one thing has one *main* thing in it — a table, a figure, a checklist, a short list. **That goes first, directly under the summary**, before any prose that explains it. If a reader has to scroll past three paragraphs of context to reach the table the page exists for, the spine has failed even though lines 1–4 are perfect.

Supporting detail — a second table for internal bookkeeping, the reasoning, the caveats — goes *below* the overview entity, never above it.

## Dispatch-table spine

A masthead: the breadcrumb folded into the table's first row, then governed rows, then an optional terminal separator that decides what auto-surfaces. The row vocabulary and the separator semantics are [[DAS Dispatch Table]]'s; do not restate them here.

**Never hand-author the electric zone** — everything below the separator is recomputed. See the vault's `CLAUDE.md`.

## The six shapes are refinements of these two

[[TINK308 - Spine: the routing zone every document opens with|F308]] measures the vault and resolves the two families into six shapes, selected by the terminal separator, which is the axis the machine already dispatches on:

- **Breadcrumb family** — S1 breadcrumb (organizes nothing), S2 redirect line (organizes nothing but owes two or three named destinations).
- **Masthead family** — S3 masthead only (fixed hand-picked set, no separator), S4 `...` (children surface, no per-child sentence — the anchor-page default), S5 `---` (each child earns a row and a description), S6 `^^^` (same, dated, newest first).

Read the two families as the decision and the six as the calibration. If the one question above does not settle a document, the six shapes will; if they also do not, the document is probably two documents.

## The escape, when a document genuinely needs a third opening

A rule that admits no exception gets weakened the first time it is genuinely wrong, and a weakened rule stops catching the cases it was right about. So the two-way rule is strict *because* there is a way out: a numbered, graded row in the anchor's `{slug} Track/{slug} Exceptions.md`, scoped to the one document, with a sentence saying why the strict fix is not being taken ([[R-exception-discipline]]).

**On the spine rules specifically, the agent asks before it writes the row.** Most checked rules let an agent record a proposal freely, graded `?`, and that proposal suppresses nothing until the user grades it. The three rules that enforce the spine — `R-progressive-01`, `-03`, `-04` — instead carry `confirm:: user`, because there should not be many exceptions to a two-way rule and each one deserves a conversation. An ungraded row against them **fails** the anchor's exception table, so the proposal cannot sit as a permanent pending; the agent asks, and records the grade it is given.

Grading is the user's act either way, and the grade is a scale: `A`–`C` suppresses the finding, `D` or lower records the refusal while the finding goes on failing — so *"I read this and the answer is no"* is a thing the table can hold, rather than something that has to be said by deleting the row and losing why it was ever proposed.

The live case is `Agent Purview`, `Agent Conventions` and `Agent Roster` — [[Agent Memory]]'s own siblings — which open frontmatter → H1 → summary, with neither a breadcrumb nor a masthead. That is a third opening this rule says should not exist. Whether they are a legitimate variant or four documents needing a breadcrumb is a real question, not a formality; either way the answer gets written down where the audit can see it.

## Why this is a discipline rather than a facet

A facet describes one *kind* of document. The spine governs the opening of **every** document of every kind, so it cannot be owned by any facet — which is exactly how the routing rules ended up scattered across `R-progressive` and `R-dispatch-table` with no single home. `R-spine` (F308 M2) is the ruleset that will enforce this; until it lands, this discipline is the statement of record and the rules live in the two places F308 names.
