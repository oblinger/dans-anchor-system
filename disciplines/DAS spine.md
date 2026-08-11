---
name: spine
description: "Slot facet. The spine is everything above the H1 — the page's position in the structure, in whichever shape its children call for; the heart is what comes directly below."
user_invocable: false
---

| -[[DAS spine]]- | : Slot facet. The spine is everything above the H1 — the page's position in the structure, in whichever shape its children call for; the heart is what comes directly below.<br>→ [[DAS]] → [[disciplines]] → [DAS spine](hook://p/DAS%20spine)  |
| --- | --- |
| Related | [[DAS Dispatch Table]],  [[DAS progressive-disclosure]],  [[DAS Disciplines\|Disciplines]],  [[DAS\|dans-anchor-system]],   |
| Rules | [[R-spine]],  [[R-dispatch-table]],  [[R-exception-discipline]],   |
| Shapes | [[LUMEN Nudge\|breadcrumb]],  [[Rolodex\|grouped]],  [[SKA\|two-level]],  [[Disk\|list]],  [[VOX\|stream]],   |
| Examples | [[FEX Spine Examples\|made-up gallery]],  [[Harbor Runbooks]],  [[Devtools]],  [[Harbor Hops]],  [[Harbor Releases]],   |

# Spine Discipline
Everything above the H1 says where the page sits; the heart directly below says what it is about. One question picks the shape — does this page have children? — and one marker names it.

| Spine shape | Marker | What it says about the children | Live | Made-up | Pages |
|---|---|---|---|---|---|
| **[[#Breadcrumb spine\|Breadcrumb]]** | `:>>` | there are none — this page is a leaf | [[LUMEN Nudge]] | [[Harbor Latency Budget]] | 1,266 |
| **[[#Curated spine\|Curated]]** | `...` | listed by hand, one row each; the catchall is a safety valve | [[Legal]] | [[Bridges]] | 578 |
| **[[#Grouped spine\|Grouped]]** | `...` | curated, but the rows form cohesive named groups | [[Rolodex]] | [[Harbor Runbooks]] | 223 |
| **[[#Two-level spine\|Two-level]]** | `...` `+` | grouped, but each label is itself a page with its own spine | [[SKA]] | [[Devtools]] | 13 |
| **[[#List spine\|List]]** | `---` | the machine writes one row each, alphabetical, with descriptions | [[Disk]] | [[Harbor Hops]] | 231 |
| **[[#Stream spine\|Stream]]** | `^^^` | the same, reversed, so dated children read newest-first | [[VOX]] | [[Harbor Releases]] | 23 |
| **[[#External spine\|External]]** | none | they are not in this folder at all — the rows point outside | [[STARTUPPER]] | ~~[[Harbor Retrospectives]]~~ | 22+ |

**The middle four are a refinement ladder, not four unrelated options:** curated ⊃ grouped ⊃ two-level, each adding one constraint to the one above; list is what you take instead when no grouping exists *and* each child needs its own sentence. External sits outside the ladder entirely, because it is the one shape whose rows leave the folder. Counts are a vault scan of 1,234 masthead pages plus [[TINK308 - Spine: the routing zone every document opens with|F308]]'s breadcrumb census; the curated/bare-catchall boundary is a judgement, so that row's figure is the `...` population net of grouped and two-level. Each shape is specified in its own section below; the examples illustrate those specs and do not replace them.

## What a spine is

**A spine states the page's position in the structure.** That is the whole definition, and it has two directions:

- **Upward — what this page hangs under.** The breadcrumb: `kmr → SYS → Staff → LUMEN → LUMEN Nudge`. Every page owes this.
- **Downward — what hangs under this page.** The dispatch rows. Only a page with children owes this.

Those are not two competing forms to choose between; they are the two halves of one job. **A dispatch table already contains its breadcrumb** — folded into the identity row, right of the `-[[Name]]-` cell — so a masthead is a breadcrumb that also points down. That is why no page carries both: the table *is* the breadcrumb, extended.

So the question a page faces is not "which opening?" but **"do I have children?"** No children — a leaf, upward only. Children — a hub, both directions. It is a question about the document's *position*, not its length, importance, or how much work went into it: a long, central, carefully-written document at the bottom of the tree takes a breadcrumb.

**The failure this exists to stop is a leaf wearing a dispatch table.** A masthead announces "I route you onward"; when the page routes nowhere, every row is empty or invented, and the reader's first impression is of a hub that turns out to be a leaf. The pull is that a masthead *looks* more finished. It isn't — it is a promise the page cannot keep.

## The shapes, specified

Two independent questions pick the shape. **Layout** — are the children named under labels, or given a row each? **Automation** — does the author write the rows above the marker, or the machine below it? Layout is the interesting axis; automation follows from it.

### Breadcrumb spine

**Marker:** none — there is no table at all. **Use when:** the page has no children.

The whole spine is one line, and the lines around it are fixed:

| Line | Content |
|---|---|
| 1 | `:>> [[kmr]] → [[SYS]] → … → [Name](hook://p/Name)` — the breadcrumb, first body line |
| 2 | `# Name` — the H1, with **no blank line** between it and the breadcrumb |
| 3 | One sentence saying what this document is |
| 4 | *(blank)* |
| 5 | **The heart** — the one main thing the document exists to hold |

Line 5 is load-bearing and the one most often got wrong: the main thing goes **directly under the summary**, before any prose explaining it. [[LUMEN Nudge]] is the exemplar — breadcrumb, H1, one sentence, then the table of what is coming up.

**A data table on a leaf is not a dispatch table.** This is the distinction a reader must make on sight, and the reason [[Harbor Latency Budget]] exists: it carries a substantial table and is still a leaf, because the table describes the page's own subject rather than routing anywhere.

### Curated spine

**Marker:** `...` **Use when:** you are listing the children by hand and no grouping suggests itself.

Every entry gets its own hand-written row above the marker. **The `...` is a safety valve, not the content** — it exists so a child you forgot, or one added later, still surfaces rather than vanishing. On a well-kept curated page it is nearly empty, and that is the point.

This is the honest shape for a hodgepodge. [[Legal]] is the live case: about a hundred hand-listed contracts, invoices and disclosures that genuinely do not sort into three tidy piles. Forcing groups onto that would invent structure the material does not have.

**Every dispatch spine has curated rows** — everything above the marker is always the author's. What makes *this* shape curated is that those rows carry essentially all the content, with automation demoted to a backstop.

### Grouped spine

**Marker:** `...` **Use when:** the children live in this folder and fall into a few natural groups.

The labels are **plain text** — `Incident`, `Routine`, `Recovery` name nothing you can open. Every child is already in this one folder; the label only tells the reader which one they want. Below the labelled rows, the `...` sweeps up whatever has not been placed.

**Grouped is a special case of curated** — the case where cohesive groupings exist. Fifteen children as fifteen rows and as three named groups of five carry the same links, but three groups are what a reader can hold in their head. [[Rolodex]] is the worked case — **Corporate**, **Professional**, **Personal**, and the whole contact system is legible at a glance. Prefer grouped whenever the groups are real, and fall back to curated when they are not, rather than inventing them.

**A grouped spine with zero labels is a bare catchall** — 577 pages, the vault's commonest shape, and the right default when the children need no sentence and form no natural clusters. That is grouped with the knob at zero, not a separate shape.

### Two-level spine

**Marker:** `...` with `+` on the group rows. **Use when:** the groups are large enough to deserve pages of their own — roughly past fifteen children.

Each label is **a link to a page** carrying its own spine and its own children, marked `+`. The members shown beside it are a hand-pinned *preview*, not the list; the list lives on the group's page.

**This is the distinction that is easy to miss**, because grouped and two-level render almost identically. Grouped is one folder wearing headings; two-level is a node in a tree of containers. Read [[Harbor Runbooks]] and [[Devtools]] side by side — they are built to be that pair. At 13 pages it is the rarest shape, and below the fifteen-child threshold it adds a hop for nothing.

### List spine

**Marker:** `---` **Use when:** each child needs its own sentence.

The machine writes **one row per child**, alphabetically, each carrying that child's own description. Nothing below the marker is hand-written.

**`...` and `---` are not the same list written twice.** `...` collapses every unplaced child into one compact row; `---` gives each child a line with room for a sentence. That per-child sentence is the only reason to choose `---` — which is why **a `---` page with no rows below the marker is a defect, not a style, and 94 of the 231 are exactly that.** Conversely, a page whose per-child rows are *hand-written above* a `...` is a grouped spine with unusually long labels, not a list spine.

[[Disk]] is where the trade is visibly worth paying: two curated rows, then `---`, then a row per drive with real descriptions.

### Stream spine

**Marker:** `^^^` **Use when:** the children are date-named.

Identical to a list spine except reversed, so reverse-alphabetical *is* reverse-chronological.

**The marker follows the children, not the topic.** A page of dated children takes `^^^` whether it is a release log, a trip list, or a set of dated applications — which is why the live `^^^` pages include `Apply`, `Find`, `Guide`, `Profile`, `Survey` and `Trips` alongside `EOC Log` and `MED Log`.

**A stream is not automatically a stream spine.** [[DAS stream]] is an *ordering* principle and applies at two granularities: entries as H2s **inside one file** (no children to enumerate — the page ends `...`, which is what [[DAS Log]] and the `{slug} Log` template do), or **one dated file per entry**, which is where the stream spine appears. Same ordering, different object.

### External spine

**Marker:** none, and that is load-bearing. **Use when:** the pages this one organizes are deliberately not in its folder.

Every other shape describes children the file tree already holds. An external spine points at material that lives elsewhere — because it is grouped by a *property* rather than by a place. [[STARTUPPER]] is the live case: thirty members whose `@Name` pages sit all over `AT/`, gathered here because they are startup-affiliated, not because they share a directory.

**It must carry no marker at all.** An electric marker can only ever compute the folder, so on a page whose rows deliberately leave the folder it would compute the wrong set — sweeping in unrelated neighbours while adding nothing to the curated list. This is the one shape where the absence of automation is part of the definition rather than an omission, and the general rule already covers why: *a page that fronts no folder has nothing to sweep.*

**The rows are therefore fully manual, and nothing can verify them.** Every other shape can be diffed against its folder; this one cannot, because there is no folder to diff against. That is the cost of the shape, and the reason to reach for it only when the grouping really is by property.

An external spine can otherwise be laid out however suits it — [[STARTUPPER]] happens to be grouped (**People**, **Companies**, **Related pages**). Layout and externality are independent.

**This page is an external spine.** `disciplines/DAS spine.md` fronts no folder, and its rows point at [[LUMEN Nudge]], [[Rolodex]], [[Disk]], [[VOX]] and the Harbor examples — 93% of them outside `disciplines/`. It carries no marker, correctly.

## Rules that cut across every shape

### The catchall is not optional

**Every hub ends in an electric marker.** Not because the page needs it today, but because of what happens tomorrow: someone adds a file to the folder and does not update the masthead. With a catchall the new child appears automatically — unsorted, but *visible*. Without one it is invisible, and nothing ever tells you.

That is a measured failure, and the size of it is **16 pages hiding 44 children** (2026-08-11) — pages that front a folder, carry no marker, and hold at least one member they link nowhere. The worst is [[EMBER Log]] at 14 of 14; then [[Atticus]] (6 of 7), [[SV Track]] (4), [[Warden Corpus]] (3 of 3). Treat the figure as a snapshot: three passes over the same afternoon read 39, 37 and 37 pages as the corpus moved under them.

**The figure this section used to carry — 36 pages, with `ASIO` (33) and `META` (14) as its worked examples — was wrong, and wrong in a way worth keeping.** `S07` fired on folder *size* and reported it as hidden, never asking whether the page already linked its members. Re-measured 2026-08-11 (by [[ATT|Atticus]], then independently here): **37 pages / 230 children** as the rule was written, **16 / 44** once the already-linked filter `S08` had used all along is applied — and **21 of the 37 hid nothing whatsoever.** `ASIO` has 33 members and 0 unlinked; `META` 14 and 0. Both hand-write one masthead row per child, which is a curated spine doing exactly its job.

The remedy this section prescribes could not have helped them either: [[DAS Dispatch Table]]'s F081 body-mention suppression omits every child the page already links, so the `...` they were told to add would have rendered an **empty zone** — the fix would have looked like it silently failed. A rule whose message asserts children are invisible, about children linked three rows above the marker it demands, teaches a reader to discount the checker; that is why the correction went into `S07` (`test-s07-already-linked.py` pins both directions) rather than into this prose.

**A page that fronts no folder has nothing to sweep**, and correctly carries no marker — 121 pages sit there legitimately. The rule is not "every masthead needs a marker"; it is **"every masthead over a folder needs one."**

**A hub is normally the anchor page of its own folder** — `Harbor Hops/Harbor Hops.md` with a `.anchor` beside it — and that is what makes the enumeration trustworthy: the machine is reading the folder, not a list someone maintained. Pages that dispatch children they do not contain exist and are not yet specified here.

**Never hand-author the zone below the marker** — it is recomputed, and anything typed there is silently discarded on the next rebuild. See the vault's `CLAUDE.md`.

### Two markers are deliberately not shapes

`+++` (alphabetical with grandchildren) and `!!!` (clip) each occur in exactly one file vault-wide — the same file, the spec that defines them. Under the standing rule that *a shape with no live exemplar is a shape you invented*, both stay out.

`+` is the exception that earned promotion. It is written per-row rather than as a terminal marker, so it looked like a régime layered over the other shapes — but what it marks is a *structural* difference (the label is a page, not a word), and that difference changes how a reader navigates.

## The heart

**The spine is everything above the H1. The heart is what sits directly below it.** They divide by what they talk about: the spine talks about *other pages* — what this one hangs under and what hangs beneath it; the heart talks about *this page's own substance*.

The order is fixed and the reason is the fold: **H1 → one sentence → heart**, with no blank line between the H1 and the sentence, so the heart lands on screen without scrolling. If a reader must scroll past three paragraphs to reach the table the page exists for, the page has failed even when every line above is perfect.

**The heart is specified at [[DAS heart]]** — its two forms (bare and labelled), its range from carries-the-page to merely-orients, why a page may legitimately have none, and how `H01` checks it. It earned its own page 2026-08-11, having been documented here only because the two zones are comprehensible as a pair. **Keep this section a pointer:** detail restated here is detail that drifts.

One rule stays, because the spine examples cannot be authored correctly without it. **The heart never routes to children.** If the element under the H1 is handing the reader other pages, that is spine work wearing a different hat — and a page whose spine and content are the same table simply has no heart. [[Harbor Hops]] is that case deliberately; [[Devtools]] is the contrast, carrying a masthead that routes and a pipeline table that does not.

## Dispatch spine

The row vocabulary, the identity cell, and the fixed row order are [[DAS Dispatch Table]]'s; the automation semantics are summarized above but owned there. Do not restate either here.

**This page is itself an [[#External spine|external spine]]** — see that section; it fronts no folder and its rows point outward, so carrying no marker is correct rather than an omission.

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

## Why this is a slot facet
A spine is a **region inside a file** — everything above the H1 — with a start, an end, and a template on each of its shapes. That is the slot group's definition ([[DAS Facet]] § Facet groups).

**The earlier reading on this page was that a spine "cannot be owned by any facet, because it governs every kind of document."** That rested on a definition of *facet* which has since been sharpened (2026-08-11): a **file** facet describes one kind of document, a **slot** facet describes one region *in* documents of any kind. Applying to everything was never disqualifying — it is precisely what makes the spine a slot rather than a file. What the old reading got right stands: the rules could not be owned by any one document kind, which is how they ended up scattered across `R-progressive` and `R-dispatch-table` with no single home.

It still reads as a discipline in the `where::` grammar, because that grammar cannot express a **positional** region — `sentinel:` matches a region announcing itself with a marker, and a spine is defined by where it sits. So [[R-spine]] falls back to `` `always` ``, and the group is carried by this declaration instead. The file stays in `disciplines/` beside [[DAS heart]]; the folder is not the taxonomy.

**[[R-spine]] is the home those rules needed, extracted 2026-08-08 (F308 M2).** It owns the choice of opening — `R-spine-01` (never both forms), `-02` (breadcrumb → H1 → orientation line), `-03` (an index doc fronting a folder carries a dispatch table) — and `R-progressive` now mentions routing nowhere. [[R-dispatch-table]] keeps the masthead's internals and is deliberately not folded in: those rules govern the *content* of one spine form, not which form a page gets, and merging them would put two authorities over one table.

# Log

**2026-08-09 — the six shapes became four, and the axis was wrong.** The first cut of this page keyed six shapes (S1–S6) on "the terminal separator," which was wrong in three ways the user caught by reading the exemplars:

- **The marker is not terminal.** For `---` and `^^^` it sits in the *middle*, with machine-written child rows below it. Only `...` happens to be last, because its electric zone is a single sweeping row. The marker is a **boundary**, which is what the vault `CLAUDE.md` says; "terminal" was this page's invention.
- **`Rolodex` was cited as "masthead-only, no separator." It ends `...`.** It is the vault's best *grouped* spine, and citing it for the absence of the thing it has inverted its lesson.
- **"S3 — no separator" was not a shape but a bug class.** 36 folder-fronting pages carry no marker and hide their children, `SKA Features` worst at 189. Folded into § The catchall is not optional. *(Both figures were retracted 2026-08-11 — the checker was counting folder size, not hidden children. The true contemporaneous count was 16 pages / 44 children; see that section.)*

The user's reframing replaced the old selector ("does this document organize other files?") with **position in the structure, up and down** — which explains why the identity row contains a breadcrumb, a fact the two-forms framing could not account for. Naming follows the user's spine-family vocabulary (breadcrumb / grouped / list / stream). The apparent collision with the house's old "list dispatch" naming — a *manual* flat list ending `...`, where a list spine is *machine* rows below `---` — was resolved by keeping the name for `---` only; the manual form is a grouped spine with long labels.

Exemplars replaced in the same pass: `PKM Discussion` → [[LUMEN Nudge]] (the user asked for a breadcrumb page whose primary entity is a table; `PKM Discussion` has no primary entity and is arguably a stream), and `DAS WP Design` → [[Disk]] (the old one had zero child rows below its `---`, a degenerate list — 94 of 231 list spines share that defect).

**Still open:** whether the `(See …)` redirect line (86 pages) is a spine at all. Carried as [[TINK308 - Spine: the routing zone every document opens with|F308]] Q5.

**2026-08-09 (later) — four shapes became five, and the heart got its name.** A second round with the user, all of it correction:

- **`+` was promoted from régime to shape.** Grouped and two-level render almost identically and are structurally different: a grouped label is a *word*, a two-level label is a *page*. Naming them the same hid the distinction. Two-level is the rarest hub shape at 13 pages.
- **`...` and `---` had been conflated.** `Bridges` was cited as the list exemplar, but its per-child rows are *hand-written above a `...`* — a grouped spine with long labels. A list spine is `---`, where the machine writes one row per child. Replaced with [[Harbor Hops]], built as a real folder anchor so the enumeration is genuine.
- **The heart was named** (user, this session) and specified as the zone directly below the H1, with the spine now defined as *everything above* it. The split is what each zone talks about: the spine talks about other pages, the heart about this page's own substance. The architecture case — figure plus a table of children — is spine work wearing a picture, not a heart, and stays [[FEX Figure Page]]'s.
- **The made-up examples were renamed to their in-world names**, so the identity cell and the H1 always agree. `FEX Two Level Spine` and the old `FEX List Dispatch` were deleted outright: each duplicated an existing page ([[Devtools]], `Bridges`) rather than adding one, which is the single-source-of-truth failure the gallery is supposed to model. Only the gallery itself keeps an `FEX` name.
- **Identity cells were flipped to description-first** (`: summary<br>→ breadcrumb`), 192 of them across this repo, per the user's standing preference. The vault-side sweep and the [[R-dispatch-table]] amendment that would make it binding are not done.
