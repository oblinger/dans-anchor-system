---
name: spine
description: Discipline. Exactly two ways to open a file — a breadcrumb or a dispatch table — chosen by one question, plus the fixed line order that follows each.
user_invocable: false
---

# Spine Discipline
The routing zone every document opens with — two forms, six shapes, and the one question that chooses between them.

| -[[DAS spine]]- | → [[DAS]] → [[disciplines]] → [DAS spine](hook://p/DAS%20spine)<br>: Discipline. Exactly two ways to open a file — a breadcrumb or a dispatch table — chosen by one question, plus the fixed line order that follows each. |
| --- | --- |
| Related | [[DAS Dispatch Table]],  [[DAS progressive-disclosure]],  [[DAS Disciplines\|Disciplines]],  [[DAS\|dans-anchor-system]],   |
| Rules | [[R-spine]],  [[R-dispatch-table]],  [[R-exception-discipline]],   |
| Shapes | [[PKM Discussion\|S1 breadcrumb]],  [[FCT\|S2 redirect]],  [[Rolodex\|S3 masthead-only]],  [[DAS Anchor\|S4 dot-dot-dot]],  [[DAS WP Design\|S5 dash]],  [[VOX\|S6 caret]],   |
| Examples | [[FEX Dispatch Examples\|dispatch gallery]],  [[TINK308 - Spine: the routing zone every document opens with\|F308 census]],   |

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

## The six shapes

The two families are the decision; the six shapes are the calibration. They are selected by the **terminal separator** — the axis HookAnchor already dispatches on — so the shape a page is in is a fact about its last table row, not a judgement about its contents. Counts are [[TINK308 - Spine: the routing zone every document opens with|F308]]'s census of 7,627 files; the exemplars are live pages, verified to resolve, so each one can be opened to see the shape rather than read about it.

| Shape | When it applies | Live examples | Live pages |
|---|---|---|---|
| **S1 — Breadcrumb** | Organizes nothing and owes no named siblings. A `:>>` path as the first body line, no table. | [[PKM Discussion]] · [[ABIO Safety]] · [[MGR Architecture Diagrams]] · [[JOBS Figure]] | 1,266 |
| **S2 — Redirect line** | Organizes nothing but owes two or three named destinations — or *is* a slug marker standing in for its anchor page. A `(See …)` line, no table. | [[AI Safety]] · [[MED Food]] · [[Flashcards]] — slug-marker sub-form: [[FCT]] · [[ANC]] | 86 |
| **S3 — Masthead only** | Organizes a **fixed, hand-picked** set. Every row authored, **no separator** — so nothing auto-surfaces and a new child does *not* appear. | [[Rolodex]] · [[MENTORS]] · [[SV Design]] · [[STARTUPPER]] | 157 |
| **S4 — Masthead + `...`** | Children should surface but need no per-child sentence: one compact row. **The anchor-page default.** | [[DAS Traits]] · [[DAS Anchor]] · [[SKA pilot-flow]] · [[SVAR]] | 822 |
| **S5 — Masthead + `---`** | Each child earns its own row and a description. Alphabetical, machine-ordered. | [[DAS WP Design]] · [[DAS Ctrl Design]] · [[Move Design]] | 226 |
| **S6 — Masthead + `^^^`** | The same as S5 with **dated** children, so reverse-alphabetical puts newest first. The stream shape. | [[EOC Log]] · [[MED Log]] · [[SV Log]] · [[Trips]] · [[VOX]] | 23 |

**S1 → S2 and S5 → S6 are each one question, not two.** A leaf either has named destinations to hand the reader or it does not; an enumerated list either is dated or it is not. That is what keeps the set closed rather than a taste ladder — **S3 → S4 → S5 is the only run with judgement in it**, and even there the question is single: *is this set fixed, is it enumerable-but-uninteresting, or does each member need a sentence?*

**Two spec'd markers are deliberately not shapes.** `+++` (alphabetical with grandchildren) and `!!!` (clip) each occur in exactly one file vault-wide — the same file, the spec that defines them. Under the standing rule that *a shape with no live exemplar is a shape you invented*, both stay out. The `+` row marker is likewise not a shape: it is a **per-row** régime, and all 21 pages carrying one also carry a terminal separator, so a page is never *in* `+` — it is in one of the six **and** uses `+` on some rows.

**This page is an S3**, and that is the honest classification: it fronts no folder, so a `...` catch-all would auto-surface nothing. Its rows are hand-picked and stay that way.

### Where the examples live, and why not in a folder here

The natural instinct is to make this discipline an anchor **folder** and put the six shapes' examples inside it. The house pattern says otherwise, and the reason is [[project_fex_hbr_examples|examples are real instances]]: a gallery of *copies* rots the moment the vault moves on, and a copied exemplar cannot be clicked to see how the shape actually behaves under HookAnchor. So examples are **live pages, linked** — every exemplar in the table above is a real document doing that shape for real reasons.

Where a discipline needs more than a table's worth, the gallery goes in `examples/` as a `FEX <Topic> Examples` doc — [[FEX Dispatch Examples]] is the worked case, and `FEX Spine Examples` is the slot if this table ever outgrows one row per shape. That keeps galleries in one place rather than one per discipline folder, and it is why `disciplines/` holds files rather than a folder per discipline.

## The escape, when a document genuinely needs a third opening

A rule that admits no exception gets weakened the first time it is genuinely wrong, and a weakened rule stops catching the cases it was right about. So the two-way rule is strict *because* there is a way out: a numbered, graded row in the anchor's `{slug} Track/{slug} Exceptions.md`, scoped to the one document, with a sentence saying why the strict fix is not being taken ([[R-exception-discipline]]).

**On the spine rules specifically, the agent asks before it writes the row.** Most checked rules let an agent record a proposal freely, graded `?`, and that proposal suppresses nothing until the user grades it. Every rule in [[R-spine]] instead carries `confirm:: user` — the set declares it once, so a rule added later inherits it — because there should not be many exceptions to a two-way rule and each one deserves a conversation. An ungraded row against them **fails** the anchor's exception table, so the proposal cannot sit as a permanent pending; the agent asks, and records the grade it is given.

Grading is the user's act either way, and the grade is a scale: `A`–`C` suppresses the finding, `D` or lower records the refusal while the finding goes on failing — so *"I read this and the answer is no"* is a thing the table can hold, rather than something that has to be said by deleting the row and losing why it was ever proposed.

The live case is `Agent Purview`, `Agent Conventions` and `Agent Roster` — [[Agent Memory]]'s own siblings — which open frontmatter → H1 → summary, with neither a breadcrumb nor a masthead. That is a third opening this rule says should not exist. Whether they are a legitimate variant or four documents needing a breadcrumb is a real question, not a formality; either way the answer gets written down where the audit can see it.

## Why this is a discipline rather than a facet

A facet describes one *kind* of document. The spine governs the opening of **every** document of every kind, so it cannot be owned by any facet — which is exactly how the routing rules ended up scattered across `R-progressive` and `R-dispatch-table` with no single home.

**[[R-spine]] is that home, extracted 2026-08-08 (F308 M2).** It owns the choice of opening — `R-spine-01` (never both forms), `-02` (breadcrumb → H1 → orientation line), `-03` (an index doc fronting a folder carries a dispatch table) — and `R-progressive` now mentions routing nowhere. [[R-dispatch-table]] keeps the masthead's internals and is deliberately not folded in: those rules govern the *content* of one spine form, not which form a document gets, and merging them would put two authorities over one table.
