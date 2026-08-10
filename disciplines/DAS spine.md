---
name: spine
description: "Discipline. The spine is everything above the H1 — the page's position in the structure, in one of five shapes; the heart is what comes directly below."
user_invocable: false
---

| -[[DAS spine]]- | : Discipline. The spine is everything above the H1 — the page's position in the structure, in one of five shapes; the heart is what comes directly below.<br>→ [[DAS]] → [[disciplines]] → [DAS spine](hook://p/DAS%20spine)  |
| --- | --- |
| Related | [[DAS Dispatch Table]],  [[DAS progressive-disclosure]],  [[DAS Disciplines\|Disciplines]],  [[DAS\|dans-anchor-system]],   |
| Rules | [[R-spine]],  [[R-dispatch-table]],  [[R-exception-discipline]],   |
| Shapes | [[LUMEN Nudge\|breadcrumb]],  [[Rolodex\|grouped]],  [[SKA\|two-level]],  [[Disk\|list]],  [[VOX\|stream]],   |
| Examples | [[FEX Spine Examples\|made-up gallery]],  [[Harbor Runbooks]],  [[Devtools]],  [[Harbor Hops]],  [[Harbor Releases]],   |

# Spine Discipline
Everything above the H1: where this page hangs, and what hangs under it — plus the heart directly below, which is what the page is *about*.

## What a spine is

**A spine states the page's position in the structure.** That is the whole definition, and it has two directions:

- **Upward — what this page hangs under.** The breadcrumb: `kmr → SYS → Staff → LUMEN → LUMEN Nudge`. Every page owes this.
- **Downward — what hangs under this page.** The dispatch rows. Only a page with children owes this.

Those are not two competing forms to choose between; they are the two halves of one job. **A dispatch table already contains its breadcrumb** — it is folded into the identity row, right of the `-[[Name]]-` cell — so a masthead is a breadcrumb that also points down. That is why no page carries both: the table *is* the breadcrumb, extended.

So the question a page faces is not "which opening?" but **"do I have children?"**

- **No children** — a leaf. Upward only. **Breadcrumb spine.**
- **Children** — a hub. Both directions. **Dispatch spine**, in one of four shapes below.

That is the whole test, and it is about the document's *position*, not its length, importance, or how much work went into it. A long, central, carefully-written document at the bottom of the tree takes a breadcrumb.

**The failure this exists to stop is a leaf wearing a dispatch table.** A masthead announces "I route you onward"; when the page routes nowhere, every row is empty or invented, and the reader's first impression is of a hub that turns out to be a leaf. The pull is that a masthead *looks* more finished. It isn't — it is a promise the page cannot keep.

## The five shapes

The shape is chosen by two independent questions, not one:

- **Layout — how are the children expressed?** Under named labels, or one row each.
- **Automation — who writes the rows?** The author, above the marker; or the machine, below it.

Layout is the interesting axis; automation is a mechanical consequence. Counts are from a vault scan of 1,234 masthead pages plus [[TINK308 - Spine: the routing zone every document opens with|F308]]'s breadcrumb census.

| Shape | Marker | Downward expression | Live example | Made-up | Pages |
|---|---|---|---|---|---|
| **Breadcrumb** | *(none)* | nothing — this page is a leaf | [[LUMEN Nudge]] · [[HA Config]] · [[MUX Testing]] | [[Harbor Latency Budget]] | 1,266 |
| **Grouped** | `...` | children sorted under a few **plain labels**; the catchall sweeps the rest | [[Rolodex]] · [[MY Stuff]] | [[Harbor Runbooks]] | 223 |
| **Two-level** | `...` + `+` | labels that are **themselves pages**, each with its own spine | [[SKA]] · [[SV]] · [[OBU]] | [[Devtools]] | 13 |
| **List** | `---` | the machine writes **one row per child**, alphabetical, each with its description | [[Disk]] · [[Career]] | [[Harbor Hops]] | 231 |
| **Stream** | `^^^` | the same, reversed, so **dated** children read newest-first | [[VOX]] · [[EOC Log]] · [[Trips]] | [[Harbor Releases]] | 23 |

A grouped spine with **zero** labels is a bare `...` catchall — the commonest shape in the vault at **577 pages**, and the right default for a folder whose children need no sentence and form no natural clusters. It is grouped with the knob at zero, not a sixth shape.

**`...` and `---` are not the same list written twice.** `...` collapses every unlisted child into **one compact row**; `---` gives each child **its own row with room for a sentence**. That per-child sentence is the only reason to choose `---`, which is why a `---` page with no children below the marker is a defect rather than a style — and 94 of the 231 are exactly that. A page whose per-child rows are *hand-written above* a `...` is a grouped spine with unusually long labels, not a list spine.

**A hub is normally the anchor page of its own folder** — `Harbor Hops/Harbor Hops.md` with a `.anchor` beside it — and that is what makes the machine's enumeration trustworthy: it is reading the folder, not a list someone maintained. Pages that dispatch children they do not contain exist and are not yet specified here.

### Grouped is the preferred hub shape

Given a folder of fifteen children, a flat list of fifteen rows and three named groups of five carry the same links — but the three groups are the ones a reader can hold in their head. [[Rolodex]] is the worked case: **Corporate**, **Professional**, **Personal**, and the reader understands the whole contact system at a glance. The same page as a fifteen-row list would be complete and unreadable.

**Prefer grouped whenever natural groups exist.** Reach for a list spine when they don't, or when the per-child *description* is the point — the one thing grouping costs you, since a group row spends its right-hand cell on links rather than prose. [[Disk]] is where that trade is visibly worth paying: each drive gets its own row and its own sentence.

### Grouped and two-level are different structures, not different sizes

The distinction is **what the label is**, and it is easy to miss because the two render almost identically.

- In a **grouped** spine the labels are *plain text*. `Incident`, `Routine`, `Recovery` name nothing you can open; every child already sits in this one folder, and the label only tells you which one you want.
- In a **two-level** spine each label is *a link to a page* carrying its own spine and its own children, marked `+`. The members shown beside it are a hand-pinned preview, not the list.

So grouped is one folder wearing headings; two-level is a node in a tree of containers. Read [[Harbor Runbooks]] and [[Devtools]] side by side — they are built to be that pair. Two-level is the **rarest** shape at 13 pages and earns its keep only past roughly fifteen children, when a preview genuinely beats a list; below that it adds a hop for nothing.

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

`+++` (alphabetical with grandchildren) and `!!!` (clip) each occur in exactly one file vault-wide — the same file, the spec that defines them. Under the standing rule that *a shape with no live exemplar is a shape you invented*, both stay out.

`+` is the exception that earned promotion. It is written per-row rather than as a terminal marker, so it looked like a régime layered on the other shapes — but what it marks is a *structural* difference (the label is a page, not a word), and that difference changes how a reader navigates. It is a shape.

## Breadcrumb spine — the line order is fixed

Five lines, in this order, immediately after frontmatter:

| Line | Content |
|---|---|
| 1 | `:>> [[kmr]] → [[SYS]] → … → [Name](hook://p/Name)` — the breadcrumb, first body line |
| 2 | `# Name` — the H1, with **no blank line** between it and the breadcrumb |
| 3 | One sentence saying what this document is |
| 4 | *(blank)* |
| 5 | **The heart** — the one main thing the document exists to hold |

Line 5 is the load-bearing one and the one most often got wrong. A document about one thing has one *main* thing in it — a table, a figure, a checklist. **That goes first, directly under the summary**, before any prose explaining it. If a reader must scroll past three paragraphs to reach the table the page exists for, the spine has failed even though lines 1–4 are perfect.

[[LUMEN Nudge]] is the exemplar: breadcrumb, H1, one sentence, then immediately the table of what is coming up — the entire reason the page exists.

## The heart

**The spine is everything above the H1. The heart is what sits directly below it.** They divide cleanly by what they talk about: the spine talks about *other pages* — what this one hangs under and what hangs beneath it; the heart talks about *this page's own substance*.

The order is fixed and the reason is the fold: **H1 → one sentence → heart**, with no blank line between the H1 and the sentence, so the heart lands on screen without scrolling. If a reader must scroll past three paragraphs to reach the table the page exists for, the page has failed even when every line above is perfect.

**A heart is usually a table, sometimes a figure with a table beneath it.** Its range is wide and both ends are legitimate:

- **The heart *is* the page.** [[Disk]]'s table of drives is the entire reason that page exists; the prose below it only explains what the table is.
- **The heart merely orients.** A table of contents, or a table of the page's key ideas, summarizes what follows rather than carrying it.

**The heart never routes to children.** If the element under the H1 is handing the reader other pages, that is spine work wearing a different hat — and a page whose spine and content are the same table simply has no heart. [[Harbor Hops]] is that case, deliberately: a pure index's spine is its content. [[Devtools]] is the contrast, carrying both a masthead that routes and a pipeline table that does not.

**Authored or derived, the heart is equally untouchable.** [[Disk]]'s table is hand-written and load-bearing. A table-of-contents heart is generated from the page's own headings. Same slot, opposite ownership — so a derived heart is regenerated like an electric zone and must not be hand-edited, while an authored one must not be regenerated.

Supporting detail — a second table for bookkeeping, the reasoning, the caveats — goes *below* the heart, never above it.

*(The heart may eventually earn its own discipline page. It is documented here because the two zones are only comprehensible as a pair, and because the spine examples cannot be authored correctly without it.)*

## Dispatch spine

The row vocabulary, the identity cell, and the fixed row order are [[DAS Dispatch Table]]'s; the automation semantics are summarized above but owned there. Do not restate either here.

**This page carries no marker deliberately** — `disciplines/DAS spine.md` fronts no folder, so a catchall would sweep nothing. Its rows are hand-picked and stay that way. By the rule above that is correct, not an omission.

### Where the examples live, and why not in a folder here

The instinct is to make this discipline an anchor **folder** with the shapes' examples inside it. The house pattern says otherwise, for two reasons that pull in opposite directions and settle in the same place.

**Live pages, for the real shapes.** Every exemplar in the table above is a real document doing that shape for real reasons — an example is a real instance, never a copy, because a copied exemplar rots the moment the vault moves on and cannot be clicked to see the shape behave under HookAnchor.

**Made-up pages, for the teaching gallery.** Real vault content in a published repo leaks the vault, so the synthetic Harbor world ([[Harbor Runbooks]], [[Harbor Hops]], [[Harbor Releases]], gathered by [[FEX Spine Examples]]) is deliberately invented — coherent fictional instances rather than real ones.

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

The user's reframing replaced the old selector ("does this document organize other files?") with **position in the structure, up and down** — which explains why the identity row contains a breadcrumb, a fact the two-forms framing could not account for. Naming follows the user's spine-family vocabulary (breadcrumb / grouped / list / stream). The apparent collision with the house's old "list dispatch" naming — a *manual* flat list ending `...`, where a list spine is *machine* rows below `---` — was resolved by keeping the name for `---` only; the manual form is a grouped spine with long labels.

Exemplars replaced in the same pass: `PKM Discussion` → [[LUMEN Nudge]] (the user asked for a breadcrumb page whose primary entity is a table; `PKM Discussion` has no primary entity and is arguably a stream), and `DAS WP Design` → [[Disk]] (the old one had zero child rows below its `---`, a degenerate list — 94 of 231 list spines share that defect).

**Still open:** whether the `(See …)` redirect line (86 pages) is a spine at all. Carried as [[TINK308 - Spine: the routing zone every document opens with|F308]] Q5.

**2026-08-09 (later) — four shapes became five, and the heart got its name.** A second round with the user, all of it correction:

- **`+` was promoted from régime to shape.** Grouped and two-level render almost identically and are structurally different: a grouped label is a *word*, a two-level label is a *page*. Naming them the same hid the distinction. Two-level is the rarest hub shape at 13 pages.
- **`...` and `---` had been conflated.** `Bridges` was cited as the list exemplar, but its per-child rows are *hand-written above a `...`* — a grouped spine with long labels. A list spine is `---`, where the machine writes one row per child. Replaced with [[Harbor Hops]], built as a real folder anchor so the enumeration is genuine.
- **The heart was named** (user, this session) and specified as the zone directly below the H1, with the spine now defined as *everything above* it. The split is what each zone talks about: the spine talks about other pages, the heart about this page's own substance. The architecture case — figure plus a table of children — is spine work wearing a picture, not a heart, and stays [[FEX Figure Page]]'s.
- **The made-up examples were renamed to their in-world names**, so the identity cell and the H1 always agree. `FEX Two Level Spine` and the old `FEX List Dispatch` were deleted outright: each duplicated an existing page ([[Devtools]], `Bridges`) rather than adding one, which is the single-source-of-truth failure the gallery is supposed to model. Only the gallery itself keeps an `FEX` name.
- **Identity cells were flipped to description-first** (`: summary<br>→ breadcrumb`), 192 of them across this repo, per the user's standing preference. The vault-side sweep and the [[R-dispatch-table]] amendment that would make it binding are not done.
