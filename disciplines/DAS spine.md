---
name: spine
description: Discipline. The spine states a page's position in the structure — upward always, downward when it has children — in one of four shapes.
user_invocable: false
---

# Spine Discipline
The top-of-file zone that says where this page sits in the structure: what it hangs under, and what hangs under it.

| -[[DAS spine]]- | → [[DAS]] → [[disciplines]] → [DAS spine](hook://p/DAS%20spine)<br>: Discipline. The spine states a page's position in the structure — upward always, downward when it has children — in one of four shapes. |
| --- | --- |
| Related | [[DAS Dispatch Table]],  [[DAS progressive-disclosure]],  [[DAS Disciplines\|Disciplines]],  [[DAS\|dans-anchor-system]],   |
| Rules | [[R-spine]],  [[R-dispatch-table]],  [[R-exception-discipline]],   |
| Shapes | [[LUMEN Nudge\|breadcrumb spine]],  [[Rolodex\|grouped spine]],  [[Disk\|list spine]],  [[VOX\|stream spine]],   |
| Examples | [[FEX Spine Examples\|made-up gallery]],  [[FEX Grouped Dispatch]],  [[FEX List Dispatch]],  [[FEX Dispatch Examples\|dispatch gallery]],   |

## What a spine is

**A spine states the page's position in the structure.** That is the whole definition, and it has two directions:

- **Upward — what this page hangs under.** The breadcrumb: `kmr → SYS → Staff → LUMEN → LUMEN Nudge`. Every page owes this.
- **Downward — what hangs under this page.** The dispatch rows. Only a page with children owes this.

Those are not two competing forms to choose between; they are the two halves of one job. **A dispatch table already contains its breadcrumb** — it is folded into the identity row, right of the `-[[Name]]-` cell — so a masthead is a breadcrumb that also points down. That is why no page carries both: the table *is* the breadcrumb, extended.

So the question a page faces is not "which opening?" but **"do I have children?"**

- **No children** — a leaf. Upward only. **Breadcrumb spine.**
- **Children** — a hub. Both directions. **Dispatch spine**, in one of three shapes below.

That is the whole test, and it is about the document's *position*, not its length, importance, or how much work went into it. A long, central, carefully-written document at the bottom of the tree takes a breadcrumb.

**The failure this exists to stop is a leaf wearing a dispatch table.** A masthead announces "I route you onward"; when the page routes nowhere, every row is empty or invented, and the reader's first impression is of a hub that turns out to be a leaf. The pull is that a masthead *looks* more finished. It isn't — it is a promise the page cannot keep.

## The four shapes

The shape is chosen by two independent questions, not one:

- **Layout — how are the children expressed?** As named groups, or as one row each.
- **Automation — who writes the rows?** The author, above the marker; or the machine, below it.

Layout is the interesting axis; automation is a mechanical consequence. Counts are from a vault scan of 1,234 masthead pages plus [[TINK308 - Spine: the routing zone every document opens with|F308]]'s breadcrumb census.

| Shape | Downward expression | Live example | Pages |
|---|---|---|---|
| **Breadcrumb spine** | none — this page is a leaf | [[LUMEN Nudge]] · [[HA Config]] · [[MUX Testing]] | 1,266 |
| **Grouped spine** | children sorted into a few named groups, plus a `...` catchall | [[Rolodex]] · [[FEX Grouped Dispatch]] · [[DAS Skills]] | 814 |
| **List spine** | one row per child, each able to carry a description | [[Disk]] · [[FEX List Dispatch]] · [[Career]] | 231 |
| **Stream spine** | one row per **dated** child, newest first | [[VOX]] · [[EOC Log]] · [[Trips]] | 23 |

### Grouped is the preferred hub shape

Given a folder of fifteen children, a flat list of fifteen rows and three named groups of five carry the same links — but the three groups are the ones a reader can hold in their head. [[Rolodex]] is the worked case: **Corporate**, **Professional**, **Personal**, and the reader understands the whole contact system at a glance. The same page as a fifteen-row list would be complete and unreadable.

**Prefer grouped whenever natural groups exist.** Reach for a list spine when they don't, or when the per-child *description* is the point — which is the one thing grouping costs you, since a group row spends its right-hand cell on links rather than prose. [[Disk]] is where that trade is visibly worth paying: each drive gets its own row and its own sentence.

A grouped spine with **zero** groups is just a catchall, and that is fine — it is the commonest shape in the vault (581 of the 814) and the right default for a folder whose children need no sentence and form no natural clusters.

### The catchall is not optional

**Every hub ends in an electric marker.** Not because the page needs it today, but because of what happens tomorrow: someone adds a file to the folder and does not update the masthead. With a catchall the new child appears in the `...` row automatically — unsorted, but *visible*. Without one it is invisible, and nothing ever tells you.

That is a measured failure, not a hypothetical. **36 pages in the vault front a folder that has children and carry no marker at all.** The worst is `SKA Features` — **189 children, none surfaced by its own page**. Others: `ASIO` (33), `START Ideas` (26), `Food` (23), `ATT Features` (19), `MUX Architecture` (18), `META` (14).

So a hub's rows are always *author's rows first, machine's rows last*. The three markers differ only in what the machine writes below them:

- **`...`** — one compact row sweeping every child not already named above. The grouped spine's ending.
- **`---`** — one row per child, alphabetical. The list spine's ending.
- **`^^^`** — the same, reversed, so date-named children read newest-first. The stream spine's ending.

**A page that fronts no folder has nothing to sweep**, and correctly carries no marker — 121 pages sit there legitimately. The rule is not "every masthead needs a marker"; it is **"every masthead over a folder needs one."**

**Never hand-author the zone below the marker** — it is recomputed, and anything typed there is silently discarded on the next rebuild. See the vault's `CLAUDE.md`.

### Two markers are deliberately not shapes

`+++` (alphabetical with grandchildren) and `!!!` (clip) each occur in exactly one file vault-wide — the same file, the spec that defines them. Under the standing rule that *a shape with no live exemplar is a shape you invented*, both stay out. The `+` row marker is likewise not a shape but a **per-row** régime, marking a group label as an expandable container with its own page ([[FEX Grouped Dispatch]] shows it); all 21 pages carrying one also carry a marker, so a page is never *in* `+` — it is in one of the four **and** uses `+` on some rows.

## Breadcrumb spine — the line order is fixed

Five lines, in this order, immediately after frontmatter:

| Line | Content |
|---|---|
| 1 | `:>> [[kmr]] → [[SYS]] → … → [Name](hook://p/Name)` — the breadcrumb, first body line |
| 2 | `# Name` — the H1, with **no blank line** between it and the breadcrumb |
| 3 | One sentence saying what this document is |
| 4 | *(blank)* |
| 5 | **The overview entity** — the one main thing the document exists to hold |

Line 5 is the load-bearing one and the one most often got wrong. A document about one thing has one *main* thing in it — a table, a figure, a checklist. **That goes first, directly under the summary**, before any prose explaining it. If a reader must scroll past three paragraphs to reach the table the page exists for, the spine has failed even though lines 1–4 are perfect.

[[LUMEN Nudge]] is the exemplar: breadcrumb, H1, one sentence, then immediately the table of what is coming up — the entire reason the page exists. Note that this table is **content, not navigation**: a primary data table on a leaf is not a dispatch table and does not make the page a hub.

Supporting detail — a second table for bookkeeping, the reasoning, the caveats — goes *below* the overview entity, never above it.

## Dispatch spine

The row vocabulary, the identity cell, and the fixed row order are [[DAS Dispatch Table]]'s; the automation semantics are summarized above but owned there. Do not restate either here.

**This page carries no marker deliberately** — `disciplines/DAS spine.md` fronts no folder, so a catchall would sweep nothing. Its rows are hand-picked and stay that way. By the rule above that is correct, not an omission.

### Where the examples live, and why not in a folder here

The instinct is to make this discipline an anchor **folder** with the shapes' examples inside it. The house pattern says otherwise, for two reasons that pull in opposite directions and settle in the same place.

**Live pages, for the real shapes.** Every exemplar in the table above is a real document doing that shape for real reasons — an example is a real instance, never a copy, because a copied exemplar rots the moment the vault moves on and cannot be clicked to see the shape behave under HookAnchor.

**Made-up pages, for the teaching gallery.** Real vault content in a published repo leaks the vault, so the synthetic worlds ([[FEX Grouped Dispatch]], [[FEX List Dispatch]], [[FEX Spine Examples]]) are deliberately invented — coherent fictional instances rather than real ones.

Either way the gallery lives in `examples/` as a `FEX <Topic>` doc, not in a folder per discipline. That is why `disciplines/` holds files.

## The escape, when a page genuinely needs a third opening

A rule that admits no exception gets weakened the first time it is genuinely wrong, and a weakened rule stops catching the cases it was right about. So the rule is strict *because* there is a way out: a numbered, graded row in the anchor's `{slug} Track/{slug} Exceptions.md`, scoped to the one document, with a sentence saying why the strict fix is not being taken ([[R-exception-discipline]]).

**On the spine rules specifically, the agent asks before it writes the row.** Most checked rules let an agent record a proposal freely, graded `?`, suppressing nothing until the user grades it. Every rule in [[R-spine]] instead carries `confirm:: user` — the set declares it once, so a rule added later inherits it — because there should not be many exceptions here and each deserves a conversation. An ungraded row against them **fails** the anchor's exception table, so a proposal cannot sit as a permanent pending; the agent asks, and records the grade it is given.

Grading is the user's act either way, and the grade is a scale: `A`–`C` suppresses the finding, `D` or lower records the refusal while the finding goes on failing — so *"I read this and the answer is no"* is a thing the table can hold, rather than something said by deleting the row and losing why it was ever proposed.

The live case is `Agent Purview`, `Agent Conventions` and `Agent Roster` — [[Agent Memory]]'s own siblings — which open frontmatter → H1 → summary, with neither a breadcrumb nor a masthead. That is a third opening this rule says should not exist. Whether they are a legitimate variant or three documents needing a breadcrumb is a real question, not a formality; either way the answer gets written where the audit can see it.

## Why this is a discipline rather than a facet

A facet describes one *kind* of document. The spine governs the opening of **every** document of every kind, so it cannot be owned by any facet — which is exactly how the routing rules ended up scattered across `R-progressive` and `R-dispatch-table` with no single home.

**[[R-spine]] is that home, extracted 2026-08-08 (F308 M2).** It owns the choice of opening — `R-spine-01` (never both forms), `-02` (breadcrumb → H1 → orientation line), `-03` (an index doc fronting a folder carries a dispatch table) — and `R-progressive` now mentions routing nowhere. [[R-dispatch-table]] keeps the masthead's internals and is deliberately not folded in: those rules govern the *content* of one spine form, not which form a page gets, and merging them would put two authorities over one table.

# Log

**2026-08-09 — the six shapes became four, and the axis was wrong.** The first cut of this page keyed six shapes (S1–S6) on "the terminal separator," which was wrong in three ways the user caught by reading the exemplars:

- **The marker is not terminal.** For `---` and `^^^` it sits in the *middle*, with machine-written child rows below it. Only `...` happens to be last, because its electric zone is a single sweeping row. The marker is a **boundary**, which is what the vault `CLAUDE.md` says; "terminal" was this page's invention.
- **`Rolodex` was cited as "masthead-only, no separator." It ends `...`.** It is the vault's best *grouped* spine, and citing it for the absence of the thing it has inverted its lesson.
- **"S3 — no separator" was not a shape but a bug class.** 36 folder-fronting pages carry no marker and hide their children, `SKA Features` worst at 189. Folded into § The catchall is not optional.

The user's reframing replaced the old selector ("does this document organize other files?") with **position in the structure, up and down** — which explains why the identity row contains a breadcrumb, a fact the two-forms framing could not account for. Naming follows the user's spine-family vocabulary (breadcrumb / grouped / list / stream). The apparent collision with the existing [[FEX List Dispatch]] — a *manual* flat list ending `...`, where the new "list spine" is *machine* rows below `---` — dissolved once layout and automation were separated: both are one-row-per-child, differing only in who writes the rows.

Exemplars replaced in the same pass: `PKM Discussion` → [[LUMEN Nudge]] (the user asked for a breadcrumb page whose primary entity is a table; `PKM Discussion` has no primary entity and is arguably a stream), and `DAS WP Design` → [[Disk]] (the old one had zero child rows below its `---`, a degenerate list — 94 of 231 list spines share that defect).

**Still open:** whether the `(See …)` redirect line (86 pages) is a spine at all. Carried as [[TINK308 - Spine: the routing zone every document opens with|F308]] Q5.
