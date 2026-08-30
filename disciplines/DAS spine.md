---
name: spine
description: "Slot facet. The spine is everything above the H1 — the page's position in the structure, in whichever shape its children call for; the heart is what comes directly below."
user_invocable: false
group: slot
---

| -[[DAS spine]]- | : Slot facet. The spine is everything above the H1 — the page's position in the structure, in whichever shape its children call for; the heart is what comes directly below.<br>→ [[DAS]] → [[disciplines]] → [DAS spine](hook://p/DAS%20spine)  |
| --- | --- |
| Related | [[DAS Dispatch Table]],  [[DAS progressive-disclosure]],  [[DAS Disciplines\|Disciplines]],  [[DAS\|dans-anchor-system]],   |
| Rules | [[R-spine]],  [[R-dispatch-table]],  [[R-exception-discipline]],   |
| Shapes | [[Lumen Nudge\|breadcrumb]],  [[Rolodex\|custom]],  [[Disk\|list]],  [[VOX\|stream]],  [[AI Safety\|exception]],   |
| Examples | [[FEX Spine Examples\|made-up gallery]],  [[Harbor Runbooks]],  [[Devtools]],  [[Harbor Hops]],  [[Harbor Releases]],   |

# Spine Discipline
Everything above the H1 says where the page sits; the heart directly below says what it is about. One question picks the shape — does this page have children? — and one marker names it.

| Spine shape                           | Marker | What it says about the children                                  | Live                              | Made-up                                          | Pages |
| ------------------------------------- | ------ | ---------------------------------------------------------------- | --------------------------------- | ------------------------------------------------ | ----- |
| **[[#Breadcrumb spine\|Breadcrumb]]** | `:>>`  | there are none — this page is a leaf                             | [[Lumen Nudge]]                   | [[Harbor Latency Budget]]                        | 1,266 |
| **[[#Custom spine\|Custom]]**         | `...`  | named by hand, one row each, in whatever arrangement suits them  | [[Legal]] · [[Rolodex]] · [[SKA]] | [[Bridges]] · [[Harbor Runbooks]] · [[Devtools]] | 814   |
| **[[#List spine\|List]]**             | `---`  | the machine writes one row each, alphabetical, with descriptions | [[Disk]]                          | [[Harbor Hops]]                                  | 231   |
| **[[#Stream spine\|Stream]]**         | `^^^`  | the same, reversed, so dated children read newest-first          | [[VOX]]                           | [[Harbor Releases]]                              | 23    |
| *[[#Exceptions\|Exception]]*          | *n/a*  | *not a spine — see § Exceptions*                                 | [[AI Safety]]                     | —                                                | 102   |

**Four shapes and one exception list. The question is who writes the rows** — you, or the machine. Custom is the author's: every row hand-written above a `...`, arranged however the material wants (flat, under plain-text group labels, or with `+` handing a group's members to the machine). List and stream are the machine's: it writes one row per child below the marker, alphabetical or reversed. Breadcrumb is the leaf case, where there are no rows because there are no children.

**Anything that is not one of the four is an exception, enumerated by name** rather than derived from a rule — the redirect page is the only known kind, and § Exceptions holds it. Dan, 2026-08-12, on the redirect: *"it's not really a spine, but redirect files are a valid exception case… for the exception cases, we should probably just list them out."*

Counts are a vault scan of 1,234 masthead pages plus [[Tink308 - Spine: the routing zone every document opens with|F308]]'s breadcrumb census; custom is the `...` population entire, which is why it absorbs the three figures the earlier cut split it into (578 + 223 + 13). Each shape is specified in its own section below; the examples illustrate those specs and do not replace them.

## What a spine is

**A spine states the page's position in the structure.** That is the whole definition, and it has two directions:

- **Upward — what this page hangs under.** The breadcrumb: `kmr → SYS → Staff → LUMEN → LUMEN Nudge`. Every page owes this.
- **Downward — what hangs under this page.** The dispatch rows. Only a page with children owes this.

Those are not two competing forms to choose between; they are the two halves of one job. **A dispatch table already contains its breadcrumb** — folded into the identity row, right of the `-[[Name]]-` cell — so a masthead is a breadcrumb that also points down. That is why no page carries both: the table *is* the breadcrumb, extended.

So the question a page faces is not "which opening?" but **"do I have children?"** No children — a leaf, upward only. Children — a hub, both directions. It is a question about the document's *position*, not its length, importance, or how much work went into it: a long, central, carefully-written document at the bottom of the tree takes a breadcrumb.

**The failure this exists to stop is a leaf wearing a dispatch table.** A masthead announces "I route you onward"; when the page routes nowhere, every row is empty or invented, and the reader's first impression is of a hub that turns out to be a leaf. The pull is that a masthead *looks* more finished. It isn't — it is a promise the page cannot keep.

## The shapes, specified

**One question picks the shape: who writes the rows?** No children — breadcrumb. You write them — custom, in whichever of its three arrangements suits the material. The machine writes them — list, or stream when the children are dated. Layout is the author's business *inside* the custom shape and does not select between shapes; that was the mistake the seven-shape cut made, splitting one shape into three by how its rows happened to be arranged.

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

Line 5 is load-bearing and the one most often got wrong: the main thing goes **directly under the summary**, before any prose explaining it. [[Lumen Nudge]] is the exemplar — breadcrumb, H1, one sentence, then the table of what is coming up.

**A data table on a leaf is not a dispatch table.** This is the distinction a reader must make on sight, and the reason [[Harbor Latency Budget]] exists: it carries a substantial table and is still a leaf, because the table describes the page's own subject rather than routing anywhere.

### Custom spine

**Marker:** `...`, always. **Use when:** you are naming the children yourself.

Every entry gets its own hand-written row above the marker, and the machine sweeps whatever is left into the zone below. **Every dispatch spine has hand-written rows** — everything above the marker is always the author's; what makes *this* shape custom is that those rows carry essentially all the content, with automation demoted to a backstop.

**The `...` is mandatory even when your rows already name every child.** Dan, 2026-08-12: *"you always put the dot, dot, dot at the end, because you wanna make sure that you see all the files. So even if you have a custom entry and you cover every one of them, you still want the dot, dot, dot, just so that if somebody adds one, it's not going to get lost."* A complete list is complete *today*; the marker is what keeps it complete tomorrow. So completeness is never a reason to omit it, and on a well-kept custom page the electric zone is nearly empty — that is the point, not a sign the marker is doing nothing. § The catchall is not optional carries the measured cost of leaving it off.

**Three arrangements, one shape.** How the rows are laid out is the author's business and does not change what the page is:

- **Flat** — a row per child, no grouping. The honest shape for a hodgepodge: [[Legal]] hand-lists about a hundred contracts, invoices and disclosures that genuinely do not sort into three tidy piles, and forcing groups onto that would invent structure the material does not have. With **zero** rows and nothing but the marker it is a *bare catchall* — the vault's commonest shape at 577 pages, and the right default when the children need no sentence and form no natural clusters.
- **Grouped** — the rows sit under a few plain-text labels. `Incident`, `Routine`, `Recovery` name nothing you can open; every child is already in this one folder, so the label only tells the reader which one they want. Fifteen children as fifteen rows and as three named groups of five carry the same links, but three groups are what a reader can hold in their head. [[Rolodex]] is the worked case — **Corporate**, **Professional**, **Personal**, and the whole contact system legible at a glance. Prefer it whenever the groups are real; fall back to flat when they are not, rather than inventing them. **A group label may carry a gloss** — `| **Registers** | *entity-keyed: you arrive knowing an identity and look it up* |` on [[kmr]] — written entirely in italics in the right cell, so a reader knows which group to open before opening any. It is exempt from the two-word cap only in that exact shape ([[R-dispatch-table]]-06), because the worry is abuse: prose outside the italics is narrative. Keep it to one line; that is a preference, not a rule (Dan, 2026-08-29).
- **Two-level** — the label is itself **a page**, marked `+`, carrying its own spine and its own children. The members shown beside it are a hand-pinned *preview*, not the list; the list lives on the group's page. Reach for it when the groups are large enough to deserve pages of their own — roughly past fifteen children; below that it adds a hop for nothing, which is why it is the rarest arrangement at 13 pages.

**A custom spine whose rows leave the folder is still a custom spine.** Dan, 2026-08-12, on [[STARTUPPER]]: *"why is startupper an exception spine? Why isn't that a custom spine."* It is. The rows are hand-written, so the selector answers the same way it does for every other custom page, and what the rows happen to *point at* was never the axis. [[STARTUPPER]] gathers thirty `@Name` pages that sit all over `AT/` because they are startup-affiliated rather than because they share a directory.

**Pointing outward is a property of the rows; the mandatory marker turns on the folder.** Those are two different questions, and collapsing them is what briefly made this look like a shape of its own. The marker rule was always *every masthead **over a folder** needs one* — so a page that fronts no folder has nothing to sweep and owes no marker; 121 pages sit there legitimately.

**[[STARTUPPER]] is the live warning, because it fronts no folder and carries a `...` anyway.** `spine_check` grades that `S09` — *carries a marker but fronts no folder, so it can only sweep siblings* — and the damage is visible in the rendered zone: its catchall has swept [[CONSULTANT]], [[DEVSHOP]], [[TECH]], [[PE FIRM]] and `FAANG Notes`, which are the *other* rolodex groups, not startuppers. An electric marker can only compute the folder it sits in, so on a page whose rows deliberately leave that folder it computes the wrong set — adding nothing to the hand-written list while sweeping in unrelated neighbours.

**The cost of pointing outward is that nothing can verify the rows.** Every page whose children are in its folder can be diffed against that folder; one whose rows leave it cannot. Reach for it only when the grouping really is by property.


**Grouped and two-level render almost identically and are not the same thing.** Grouped is one folder wearing headings; two-level is a node in a tree of containers. Read [[Harbor Runbooks]] and [[Devtools]] side by side — they are built to be that pair. The distinction is real and worth teaching, but it is a distinction *within* the custom spine rather than two more shapes: in all three arrangements the author writes the rows, the marker is `...`, and the machine sweeps the remainder.

### List spine

**Marker:** `---` **Use when:** each child needs its own sentence.

The machine writes **one row per child**, alphabetically, each carrying that child's own description. Nothing below the marker is hand-written.

**`...` and `---` are not the same list written twice.** `...` collapses every unplaced child into one compact row; `---` gives each child a line with room for a sentence. That per-child sentence is the only reason to choose `---` — which is why **a `---` page with no rows below the marker is a defect, not a style, and 94 of the 231 are exactly that.** Conversely, a page whose per-child rows are *hand-written above* a `...` is a custom spine with unusually long labels, not a list spine.

[[Disk]] is where the trade is visibly worth paying: two hand-written rows, then `---`, then a row per drive with real descriptions.

**Special children may be pulled above the marker, and described there by hand.** A list usually has a few members that matter more than the rest — on [[Disk]] the master drive and its two backups. Those rows move above `---`, under a bold group label (`**DISKS**`), in the same shape the machine would give them below it: the child's link in the left cell, its one-sentence description in the right. That sentence is a *description of the link beside it*, not narrative about some other page, so [[R-dispatch-table]]-06's two-word cap does not apply — the checker skips any row whose left cell is a wiki-link (Dan, 2026-08-29: *"it's totally legal for there to be a sentence there. It's expected"*). The children that stay below the marker are still written by the machine.

### Stream spine

**Marker:** `^^^` **Use when:** the children are date-named.

Identical to a list spine except reversed, so reverse-alphabetical *is* reverse-chronological.

**The marker follows the children, not the topic.** A page of dated children takes `^^^` whether it is a release log, a trip list, or a set of dated applications — which is why the live `^^^` pages include `Apply`, `Find`, `Guide`, `Profile`, `Survey` and `Trips` alongside `EOC Log` and `MED Log`.

**A stream is not automatically a stream spine.** [[DAS stream]] is an *ordering* principle and applies at two granularities: entries as H2s **inside one file** (no children to enumerate — the page ends `...`, which is what [[DAS Log]] and the `{slug} Log` template do), or **one dated file per entry**, which is where the stream spine appears. Same ordering, different object.

## Exceptions

**A page that is none of the four shapes is an exception, and exceptions are listed by name.** Dan, 2026-08-12: *"for the exception cases, we should probably just list them out."* This is deliberately a roster rather than a rule — the four shapes are meant to cover everything an authored page does, so a fifth kind should have to be written down and looked at, not derived from a definition loose enough to admit it quietly.

**One kind is known.** The roster was briefly two: the *external masthead* was listed here for a day, on the reasoning that it must carry no marker and so cannot obey the mandatory `...`. Dan refused it the same day by pointing at the exemplar: *"why is startupper an exception spine? Why isn't that a custom spine?"* It is one — its rows are hand-written, which is the whole selector. What made it look like an exception was a *condition* (fronting no folder) that § The catchall is not optional had always carried its own clause for. See § Custom spine, which also records that [[STARTUPPER]] carries a marker it does not owe and is sweeping four unrelated sibling pages as a result.

### Redirect page

**A single `(See …)` line below the H1, and no table.** The page organizes nothing and owes two or three named destinations — or *is* a slug marker standing in for its anchor page. Live: [[AI Safety]], [[MED Food]], [[@Peter Hui]], [[Flashcards]], [[Self Attention]]; the slug-marker sub-form is [[VEC]], [[FCT]], [[CFO]], [[ANC]].

**It is not a spine, and the sharp edge is where it sits.** Every shape above sits at or above the H1; a redirect sits *below* it, which is body content's position. Dan, 2026-08-12: *"it's kind of an exception… it's not really a spine, but I think redirect files are a valid exception case."* Ruled as [[Tink308 - Spine: the routing zone every document opens with|F308]] Q5, which had carried it as a seventh shape (S2) through three census passes.

**86 pages, plus 16 more riding alongside a breadcrumb.** They are exceptions, not defects: a page that exists to hand the reader onward and nothing else is a real thing the vault does, and giving it a masthead would be a promise it cannot keep.

## Rules that cut across every shape

### The catchall is not optional

**Every hub ends in an electric marker.** Not because the page needs it today, but because of what happens tomorrow: someone adds a file to the folder and does not update the masthead. With a catchall the new child appears automatically — unsorted, but *visible*. Without one it is invisible, and nothing ever tells you.

That is a measured failure, and the size of it is **16 pages hiding 44 children** (2026-08-11) — pages that front a folder, carry no marker, and hold at least one member they link nowhere. The worst is [[Ember Log]] at 14 of 14; then [[Atticus]] (6 of 7), [[SV Track]] (4), [[Warden Corpus]] (3 of 3). Treat the figure as a snapshot: three passes over the same afternoon read 39, 37 and 37 pages as the corpus moved under them.

**The figure this section used to carry — 36 pages, with `ASIO` (33) and `META` (14) as its worked examples — was wrong, and wrong in a way worth keeping.** `S07` fired on folder *size* and reported it as hidden, never asking whether the page already linked its members. Re-measured 2026-08-11 (by [[ATT|Atticus]], then independently here): **37 pages / 230 children** as the rule was written, **16 / 44** once the already-linked filter `S08` had used all along is applied — and **21 of the 37 hid nothing whatsoever.** `ASIO` has 33 members and 0 unlinked; `META` 14 and 0. Both hand-write one masthead row per child, which is a custom spine doing exactly its job.

The remedy this section prescribes could not have helped them either: [[DAS Dispatch Table]]'s F081 body-mention suppression omits every child the page already links, so the `...` they were told to add would have rendered an **empty zone** — the fix would have looked like it silently failed. A rule whose message asserts children are invisible, about children linked three rows above the marker it demands, teaches a reader to discount the checker; that is why the correction went into `S07` (`test-s07-already-linked.py` pins both directions) rather than into this prose.

**A page that fronts no folder has nothing to sweep**, and correctly carries no marker — 121 pages sit there legitimately. The rule is not "every masthead needs a marker"; it is **"every masthead over a folder needs one."**

**Stated as three clauses (Dan, 2026-08-29):** an **anchor page** — the page fronting its folder — *must* have a spine, and that spine *must* end in an electric section, because otherwise nothing anywhere lists the folder's files. Any **other page** *must not* carry an electric section — it owns no files, so the marker lists another page's children (seen live on [[DAS ask-format]], whose `...` filled with every `disciplines/` sibling within twenty minutes) — and *may or may not* have a spine at all: a breadcrumb is enough, and a full masthead is also fine when the related work is worth routing to, ending at its last hand row while [[disciplines]] carries the `...` for the folder. The marker follows ownership, never the masthead.

**A hub is normally the anchor page of its own folder** — `Harbor Hops/Harbor Hops.md` with a `.anchor` beside it — and that is what makes the enumeration trustworthy: the machine is reading the folder, not a list someone maintained. Pages that dispatch children they do not contain exist and are not yet specified here.

**Never hand-author the zone below the marker** — it is recomputed, and anything typed there is silently discarded on the next rebuild. See the vault's `CLAUDE.md`.

### Two markers are deliberately not shapes

`+++` (alphabetical with grandchildren) and `!!!` (clip) each occur in exactly one file vault-wide — the same file, the spec that defines them. Under the standing rule that *a shape with no live exemplar is a shape you invented*, both stay out.

**`+` is not a shape either, and it was one for three days.** It is written per-row rather than as a marker, and on 2026-08-09 it was promoted out of régime and into its own shape (*two-level*) on the argument that the label being a page rather than a word is a structural difference. That argument still holds and the distinction is still taught — but it distinguishes two *arrangements of a custom spine*, not two shapes, because the thing that selects a shape is who writes the rows and `+` does not change the answer. Demoted 2026-08-12 with the rest of the re-cut; see § Custom spine.

## The heart

**The spine is everything above the H1. The heart is what sits directly below it.** They divide by what they talk about: the spine talks about *other pages* — what this one hangs under and what hangs beneath it; the heart talks about *this page's own substance*.

The order is fixed and the reason is the fold: **H1 → one sentence → heart**, with no blank line between the H1 and the sentence, so the heart lands on screen without scrolling. If a reader must scroll past three paragraphs to reach the table the page exists for, the page has failed even when every line above is perfect.

**The heart is specified at [[DAS heart]]** — its two forms (bare and labelled), its range from carries-the-page to merely-orients, why a page may legitimately have none, and how `H01` checks it. It earned its own page 2026-08-11, having been documented here only because the two zones are comprehensible as a pair. **Keep this section a pointer:** detail restated here is detail that drifts.

One rule stays, because the spine examples cannot be authored correctly without it. **The heart never routes to children.** If the element under the H1 is handing the reader other pages, that is spine work wearing a different hat — and a page whose spine and content are the same table simply has no heart. [[Harbor Hops]] is that case deliberately; [[Devtools]] is the contrast, carrying a masthead that routes and a pipeline table that does not.

## Dispatch spine

The row vocabulary, the identity cell, and the fixed row order are [[DAS Dispatch Table]]'s; the automation semantics are summarized above but owned there. Do not restate either here.

**This page is itself a [[#Custom spine|custom spine]] that fronts no folder** — its rows point at [[Lumen Nudge]], [[Rolodex]], [[Disk]], [[VOX]] and the Harbor examples, 93% of them outside `disciplines/`, so there is nothing to sweep and carrying no marker is correct rather than an omission.

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

**2026-08-12 — seven shapes became four and an exception list, and the shape set stopped living in two places.** Dan resolved [[Tink308 - Spine: the routing zone every document opens with|F308]] Q5 and Q6, and the ruling was larger than either question asked.

- **Curated, grouped and two-level are one shape, `custom`.** All three are hand-authored rows above a `...`; what separated them was how those rows happened to be arranged, which is the author's business and not a property of the page. Both distinctions are kept and taught inside § Custom spine — they were worth writing down, they were just not shapes.
- **`+` was demoted back to a régime**, three days after this page promoted it. Recorded rather than quietly reverted, because the argument that promoted it was sound and is still in the text.
- **The `...` is mandatory, and completeness is not an excuse.** Dan: *"even if you have a custom entry and you cover every one of them, you still want the dot, dot, dot, just so that if somebody adds one, it's not going to get lost."*
- **The redirect page is an exception, listed by name** in a new § Exceptions at the end. It had been carried as a seventh shape through three census passes of F308 and appeared nowhere on this page.
- **The external masthead was listed beside it for one day and Dan refused it the same day**, by opening the exemplar: *"why is startupper an exception spine? Why isn't that a custom spine."* Its rows are hand-written, which is the whole selector; what looked like a shape defined by carrying no marker was a *condition* (fronting no folder) that § The catchall is not optional had always had its own clause for. There is no external shape and no external exception. Worth keeping because the same mistake is available again: **pointing outward is a property of the rows, and the marker rule turns on the folder** — and because the first attempt at writing this entry asserted that [[STARTUPPER]] carries its `...` *because it fronts a folder*, which the checker refuted in one call. It fronts none, the marker is an `S09`, and its catchall has swept four unrelated rolodex groups.
- **Scope and rollout settled (Q6):** every markdown file under an anchor owes a spine — 7,644 of 7,651 — with liberal exceptions allowed and no exceptions table built yet. The rollout is **lazy**: a page gets its spine when an agent saves it. Dan: *"we're not gonna scan through the whole repository, we're just gonna do this as the agent modifies a file. Later, we'll do the whole thing."* So the 5,088 spineless pages are a backlog depth, not a migration to schedule.

**And the shape set now lives here alone.** Dan: *"we're getting multiple sources of truth here… what we should be doing is not doing this in the feature document, but actually putting the exemplars into the DAS documentation."* F308 had been carrying its own six-shape table while this page carried a different seven, and neither knew about the other. F308's table becomes a pointer; [[Tink326 - Spine Update|F326]] is where the work is tracked, and F308 closes when Dan agrees with this page and [[FEX Spine Examples]].

**2026-08-09 — the six shapes became four, and the axis was wrong.** The first cut of this page keyed six shapes (S1–S6) on "the terminal separator," which was wrong in three ways the user caught by reading the exemplars:

- **The marker is not terminal.** For `---` and `^^^` it sits in the *middle*, with machine-written child rows below it. Only `...` happens to be last, because its electric zone is a single sweeping row. The marker is a **boundary**, which is what the vault `CLAUDE.md` says; "terminal" was this page's invention.
- **`Rolodex` was cited as "masthead-only, no separator." It ends `...`.** It is the vault's best *grouped* spine, and citing it for the absence of the thing it has inverted its lesson.
- **"S3 — no separator" was not a shape but a bug class.** 36 folder-fronting pages carry no marker and hide their children, `SKA Features` worst at 189. Folded into § The catchall is not optional. *(Both figures were retracted 2026-08-11 — the checker was counting folder size, not hidden children. The true contemporaneous count was 16 pages / 44 children; see that section.)*

The user's reframing replaced the old selector ("does this document organize other files?") with **position in the structure, up and down** — which explains why the identity row contains a breadcrumb, a fact the two-forms framing could not account for. Naming follows the user's spine-family vocabulary (breadcrumb / grouped / list / stream). The apparent collision with the house's old "list dispatch" naming — a *manual* flat list ending `...`, where a list spine is *machine* rows below `---` — was resolved by keeping the name for `---` only; the manual form is a grouped spine with long labels.

Exemplars replaced in the same pass: `PKM Discussion` → [[Lumen Nudge]] (the user asked for a breadcrumb page whose primary entity is a table; `PKM Discussion` has no primary entity and is arguably a stream), and `DAS WP Design` → [[Disk]] (the old one had zero child rows below its `---`, a degenerate list — 94 of 231 list spines share that defect).

**Still open:** whether the `(See …)` redirect line (86 pages) is a spine at all. Carried as [[Tink308 - Spine: the routing zone every document opens with|F308]] Q5.

**2026-08-09 (later) — four shapes became five, and the heart got its name.** A second round with the user, all of it correction:

- **`+` was promoted from régime to shape.** Grouped and two-level render almost identically and are structurally different: a grouped label is a *word*, a two-level label is a *page*. Naming them the same hid the distinction. Two-level is the rarest hub shape at 13 pages.
- **`...` and `---` had been conflated.** `Bridges` was cited as the list exemplar, but its per-child rows are *hand-written above a `...`* — a grouped spine with long labels. A list spine is `---`, where the machine writes one row per child. Replaced with [[Harbor Hops]], built as a real folder anchor so the enumeration is genuine.
- **The heart was named** (user, this session) and specified as the zone directly below the H1, with the spine now defined as *everything above* it. The split is what each zone talks about: the spine talks about other pages, the heart about this page's own substance. The architecture case — figure plus a table of children — is spine work wearing a picture, not a heart, and stays [[FEX Figure Page]]'s.
- **The made-up examples were renamed to their in-world names**, so the identity cell and the H1 always agree. `FEX Two Level Spine` and the old `FEX List Dispatch` were deleted outright: each duplicated an existing page ([[Devtools]], `Bridges`) rather than adding one, which is the single-source-of-truth failure the gallery is supposed to model. Only the gallery itself keeps an `FEX` name.
- **Identity cells were flipped to description-first** (`: summary<br>→ breadcrumb`), 192 of them across this repo, per the user's standing preference. The vault-side sweep and the [[R-dispatch-table]] amendment that would make it binding are not done.
