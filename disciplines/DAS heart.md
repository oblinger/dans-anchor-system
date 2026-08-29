---
name: heart
description: "Slot facet. The heart is what sits directly below the H1 — the page's own substance, on screen without scrolling, where the spine above it says only where the page sits."
user_invocable: false
group: slot
---

| -[[DAS heart]]- | : Slot facet. The heart is what sits directly below the H1 — the page's own substance, on screen without scrolling, where the spine above it says only where the page sits.<br>→ [[DAS]] → [[disciplines]] → [DAS heart](hook://p/DAS%20heart)  |
| --- | --- |
| Related | [[DAS spine]],  [[DAS progressive-disclosure]],  [[DAS Facet]] (§ Facet groups),  [[DAS Disciplines\|Disciplines]],  [[DAS\|dans-anchor-system]], |
| Rules | [[R-spine]],   |
| Examples | [[Stones\|labelled form]],  [[Briefs\|bare form]],  [[Disk\|the heart IS the page]],  [[Harbor Hops\|deliberately none]],   |

# Heart Discipline
The spine is everything above the H1; the heart is what sits directly below it. They divide by what they talk about — the spine talks about *other pages*, the heart talks about *this page's own substance*.

| Heart kind | What it holds | Shape | Live | Made-up |
|---|---|---|---|---|
| **[[#The fact card — the third form, and where a spine's prose goes\|Fact card]]** | the key facts *about this page's subject* — status, counterparty, value, dates, waiting-on, next | label / value table, 5–12 rows | [[2026-08-19 Legacy Athletics]] *(still in its spine — the migration specimen)* | — |
| **Register** | the heart *is* the page: one row per thing the page exists to track | data table, hand-written, load-bearing | [[Disk]] | [[Harbor Latency Budget]] |
| **Map** | how the page's parts relate — what flows into what | labelled table under an H2 | [[Stones]] | — |
| **Figure** | the thing the page defines, drawn | an image or diagram, no title, table beneath | [[DAS Code Design]] | [[FEX Figure Page]] · [[FEX Architecture]] |
| **Kinds table** | the variants of the thing the page specifies, each with an example | a table like this one | [[DAS spine]] · this page | [[FEX Dispatch Examples]] § The four kinds |
| **Table of contents** | the page's own sections, so a long page is navigable before it is read | derived from the headings, regenerated | [[DAS ask-format]] · [[DAS progressive-disclosure]] | — |
| **Roster** | the members a collection page fronts, by area | index table — orients, does not route | [[Briefs]] | — |

**Live** is a real vault page; **Made-up** is a [[FEX]] specimen that exists only to show the shape. A dash means the specimen is still to be minted. The table is deliberately open — a kind earns a row when a real page exhibits it, exactly as the [[DAS spine]] shapes table grew. One thing every row shares: the heart is *inward-facing*. It talks about this page's subject; the spine above it talks about other pages (Dan, 2026-08-29).

| | Spine | Heart |
|---|---|---|
| **Where** | above the H1 | directly below the H1 |
| **Subject** | other pages — what this hangs under, what hangs beneath | this page's own substance |
| **Owed by** | every page | only a page that has substance to lead with |
| **Shapes** | seven, [[DAS spine\|specified]] | two — bare, or labelled |

The order is fixed and the reason is the fold: **H1 → one sentence → heart**, with no blank line between the H1 and the sentence, so the heart lands on screen without scrolling. If a reader must scroll past three paragraphs to reach the table the page exists for, the page has failed even when every line above it is perfect.

## The two forms
A heart is usually a table, sometimes a figure with a table beneath it. It comes in two shapes, and **both are correct** — the choice is whether the element needs a name.

**Bare** — the element sits directly under the orientation line, with no heading of its own. [[Briefs]] is the worked example: H1, one sentence, then the `Area | Files carrying a # BRIEF` table. Take this when the orientation line already says what the table is, so a heading would only repeat it.

**Labelled** — an H2 names the element, and the element follows immediately. [[Stones]] is the worked example: `## The map — what flows into what` directly over the feed table. Take this when the element benefits from a name the orientation line cannot carry, or when the page has several substantial sections and the heart needs to be findable by heading.

**The labelled form is a heart, not a section.** The heading leads *straight* into the table — nothing between them. A heading that opens with prose is an ordinary section, and the zone has ended; the checker draws exactly that line, and got it wrong until 2026-08-10 (see § How it is checked).

## The fact card — the third form, and where a spine's prose goes
Ruled by Dan 2026-08-29 on [[2026-08-19 Legacy Athletics]] ([[TINK623 - R-dispatch-table-06 six days on 434 of 1,604 mastheads (27%) violate|TINK T623]]): *"the spine indexes a page in the context of other pages — it is always outward-facing. The heart is always inward-facing: the meat, the summary, the most important content of a page."* That sentence is the whole discriminator, and it settles a case the two forms above did not name.

**A fact card is a heart.** A two-column table whose left cells are labels and whose right cells are the page's own facts — `Status`, `Counterparty`, `Their people`, `Value`, `Volume`, `Dates`, `Waiting on`, `Tech owes`, `Next` on an engagement page; `Role`, `Where met`, `Last contact`, `Owes / owed` on a person page — is inward-facing by construction: every cell is about *this* page's subject. It carries the page the way [[Disk]]'s drive table does, and it takes either shape — **bare** under the orientation line, or **labelled** under an H2 such as `## Card`. Nothing changes about the rule that a heart never routes: a fact card may *contain* links, but no row of it exists to send the reader elsewhere.

**It had been living in the spine, which is why the 2-word cap read it as narrative.** The [[SV Proj Template]] put the card in the masthead position, and six days of R-dispatch-table-06 at `fail` measured 434 mastheads carrying prose — the worst of them precisely these cards and the `@` person summaries. The cap was right that the spine must be links-only; it was wrong about what to do with the words, and had nowhere to send them because the pages had no heart. Dan, looking at Legacy Athletics: *"definitely it does not belong in the spine of the page. But this document doesn't have a heart — and it deserves to have a heart."*

**The migration rule — a spine cell that talks about this page moves to the heart; one that explains another page moves to that page.** Concretely, for a masthead row whose right cell fails the cap:

1. If the row is a **fact about this page's subject** (a status, a counterparty, a value, a date, a next step) — it becomes a row of the fact card, directly below the H1's orientation line. The spine row is dropped, or kept as a links-only row if it also pointed somewhere.
2. If the row **explains a destination** ("[[X]] — the tool that does Y") — the explanation goes onto X's own top line (H1 + first sentence, `description:` frontmatter), and the spine row keeps only the link and at most a two-word tag.
3. If the row is **neither** — commentary, history, a caveat — it goes into the body below the heart, never above it.

Nothing is deleted in the move; the cap becomes satisfiable *without loss*, which is the condition for re-arming it (R-dispatch-table-06 sits at `warn` and [[R-dispatch-guard]] returns early until this migration has run over the pages it would otherwise destroy).

**A template follows.** The fact card is a shape with an extent, so it gets a template beside the bare and labelled ones — the `SV Proj Template` card, moved below the H1, is the first specimen; minting it is the next step of T623, not this paragraph.

## What a heart is not
**A heart never routes to children.** If the element under the H1 is handing the reader other pages, that is spine work wearing a different hat — and a page whose spine and content are the same table simply has no heart. [[Harbor Hops]] is that case deliberately; [[Devtools]] is the contrast, carrying a masthead that routes and a pipeline table that does not.

**A page may legitimately have none, and most do.** A page that is genuinely an argument, a narrative, or a log has no element to lead with, and inventing one to satisfy a checker makes it worse. The heart is an opportunity a page either has or hasn't — never a slot to be filled.

## Range — the heart carries or the heart orients
Both ends are legitimate and the span between them is wide:

- **The heart *is* the page.** [[Disk]]'s table of drives is the entire reason that page exists; the prose below only explains it.
- **The heart merely orients.** A table of contents, or a table of the page's key ideas, summarizes what follows rather than carrying it.

**Authored or derived, the heart is equally untouchable.** [[Disk]]'s table is hand-written and load-bearing; a table-of-contents heart is generated from the page's own headings. Same slot, opposite ownership — a derived heart is regenerated like an electric zone and must not be hand-edited, while an authored one must not be regenerated.

Supporting detail — a second table for bookkeeping, the reasoning, the caveats — goes *below* the heart, never above it.

## Never ask about a heart in the abstract
The agent does not walk up to a page and ask *"could this page have a heart?"* That question has no answer a user can give without re-reading the whole page, and asked page-by-page it is pure noise.

**Ask only with a candidate in hand.** The shape that earns a question is a page carrying **a table that is not at the top** — there is a concrete element, it is buried, and the question becomes answerable in one glance: *"should `## The map` be this page's heart?"* No candidate, no question.

This is the difference between a check that fires 100 times and a check that fires 16 (§ How it is checked). It is also why `H01` nominates a specific element rather than reporting an absence: **an absent heart is not a finding.**

## How it is checked
The heart has no ruleset of its own — [[R-spine]] owns it and `spine_check.py` implements it, because the two zones are only comprehensible as a pair and a page's opening is graded once, not twice.

`H01` fires on a **buried heart**: an element that qualifies, sitting below prose that should be below *it*. Its four conditions, all required — a candidate element exists; the page has real body weight (≥ 200); at least two paragraphs of prose already precede it; and it sits more than two lines past the orientation line. A heart at the top is *found and not reported* — being correctly placed, it has nothing to nominate.

**The detector was blind to the labelled form until 2026-08-10.** `heart_candidate()` ended its zone at the first H2, so [[Stones]] — put forward as the exemplar of what a page with a heart should look like — read as having no heart at all, along with 39 other pages. The cost was not cosmetic: `H01` protects a heart from being buried *later*, so a heart the detector cannot see has no protection at all, which was confirmed by pushing prose above Stones' map table and watching the check stay silent. Widening the zone took `H01` from 6 hits to 16 vault-wide with no other change; the regression test is `test-f319-labelled-heart.py`, whose six cases pin both directions — a labelled heart at the top must be found *and* not reported, the same heart buried must be reported, and a heading that opens a prose section must still end the zone.

## Why this is a slot facet
A heart is a **region inside a file** with a start and an end, appearing in documents of many different kinds, with a template on each of its two forms. That is the slot group's definition ([[DAS Facet]] § Facet groups), and it is what separates the heart from a true discipline like [[DAS markdown]], which selects nothing of its own and has no template.

It reads as a discipline in the `where::` grammar only because that grammar cannot express a **positional** region — `sentinel:` matches a region that announces itself with a marker, and the heart is defined by where it sits rather than by anything it says. So [[R-spine]] falls back to `` `always` ``, and the group is carried by this declaration instead. The file lives in `disciplines/` beside its sibling for the same reason: the folder is not the taxonomy.

# BRIEF

*(Maintainer note — cautions for editing this spec.)*

- **The spine doc is the pair, not the parent.** [[DAS spine]] § The heart is a pointer to this page; keep it a pointer. Detail added there instead of here will drift, which is how the heart ended up documented inside the spine spec in the first place.
- **Do not mint `R-heart`.** The checks belong to [[R-spine]] on purpose — a page's opening is graded once. A second ruleset would put two authorities over one zone, which is the same mistake [[R-dispatch-table]] is deliberately kept out of.
- **`H01`'s condition 4 is `body_weight() >= 200`.** Any test fixture shorter than that is never nominated regardless of how its heart sits, so a short fixture silently tests nothing. The first draft of `test-f319-labelled-heart.py` did exactly that and read as two failures in the code rather than in itself.
