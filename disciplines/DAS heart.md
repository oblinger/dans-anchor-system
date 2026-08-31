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
| Examples | [[2026-08-19 Legacy Athletics\|fact card]],  [[Stones\|fact card, bare]],  [[Lumen Data Sources\|register]],  [[DAS ask-format\|definition list]],  [[DAS Code Design\|figure]],  [[Briefs\|roster]],  [[Harbor Hops\|deliberately none]],   |

# Heart Discipline
The spine is everything above the H1; the heart is what sits directly below it. They divide by what they talk about — the spine talks about *other pages*, the heart talks about *this page's own substance*.

| Heart kind | What it holds | Shape | Live | Made-up |
|---|---|---|---|---|
| **[[#Fact card\|Fact card]]** | the key facts *about this page's subject* — a status card, a who-feeds-whom map, whatever facts matter most | a table of facts, any shape | [[2026-08-19 Legacy Athletics]] · [[2025-11-07 TeamSnap Data Partnership]] · [[@Henna Dattani]] · [[STONE\|Stones]] · [[IDEA Template]] (a template's card) | [[Harbor Account Northwind]] · [[@Marguerite Vale]] |
| **[[#Definition list\|Definition list]]** | the page's key facts as a definition list — `**Term:** body` — when the facts are sentences rather than cells | a bulleted definition list, one term per bullet | [[DAS ask-format]] · [[META Register]] | [[Harbor Tenancy Model]] |
| **[[#Register\|Register]]** | the heart *is* the page: one row per thing the page exists to track; the prose below only explains it | data table, hand-written, load-bearing | [[Eli Bedtime Audio]] · [[Lumen Data Sources]] | [[Harbor Latency Budget]] |
| **[[#Figure\|Figure]]** | the thing the page defines, drawn | an image or diagram, no title, table beneath | [[DAS Code Design]] | [[FEX Figure Page]] · [[FEX Architecture]] |
| **[[#Types table\|Types table]]** | the mutually exclusive subtypes of the thing the page specifies, one row each, with an example | a fact table whose rows partition the type — like this one | [[DAS spine]] · this page | [[FEX Dispatch Examples]] § The four kinds |
| **[[#Table of contents\|Table of contents]]** | the page's own sections, so a long page is navigable before it is read | derived from the headings, regenerated | [[DAS ask-format]] · [[DAS progressive-disclosure]] | [[Harbor Upgrade Guide]] |
| **[[#Roster\|Roster]]** | the members of a set this page fronts — usually things elsewhere in the vault, sometimes this folder's own children | index table with a row per member | [[Briefs]] | [[Harbor Integrations]] |

**Live** is a real vault page; **Made-up** is a [[FEX]] specimen that exists only to show the shape; every row has one as of 2026-08-29. The table is deliberately open — a kind earns a row when a real page exhibits it, exactly as the [[DAS spine]] shapes table grew. One thing every row shares: the heart is *inward-facing*. It talks about this page's subject; the spine above it talks about other pages (Dan, 2026-08-29).

## The order — spine, H1, one-liner, heart, overview
Memorialized 2026-08-29 (Dan, on [[2026-08-19 Legacy Athletics]]). A page with a heart opens in exactly this order, and each slot has one job:

| # | Slot | Job | Rule |
|---|---|---|---|
| 1 | **Spine** | where this page sits among *other* pages — up and down | everything above the H1; specified at [[DAS spine]] |
| 2 | **H1** | names the thing | the file's base name, verbatim; **no blank line** between it and the one-liner |
| 3 | **One-liner** | says what the thing *is* | one simple sentence — a definition, not a fact; specified at [[DAS orientation-line]] |
| 4 | **Heart** | the page's own substance | one of the kinds above, bare or labelled; lands on screen without scrolling |
| 5 | **`## Overview`** | the most important things to say about it | typical, not required; its first line is the salient fact |

**The one-liner is a definition, not a headline.** The line under the H1 answers *what is this?* — a league operator, a camera vendor, a tool, a register — so a reader who stops there can say what they just opened. It is not the most important fact about the thing; that fact is the natural opener of `## Overview`. The misplacement is common enough to name: Legacy Athletics opened with *"The clearest example in the tree of hardware being the thing that closes a software deal"* — true, and the most important sentence on the page, and useless for telling you whether Legacy Athletics is a camera company or a basketball league. Dan: *"that's really what that first line should be. It just orients the reader to what the thing is."* Its one-liner now reads *"Legacy Athletics is a Canadian operator of youth sports leagues — a returning SportsVisio customer …"*, and the headline opens the Overview. **Move a misplaced salient fact down; never cut it.**

**The fold is the reason the order is fixed.** H1, one-liner, heart, with nothing between them, so the heart is on screen before any scrolling. If a reader must scroll past three paragraphs to reach the table the page exists for, the page has failed even when every line above it is perfect.

## Bare or labelled
Every kind comes in two shapes, and **both are correct** — the choice is whether the element needs a name.

**Bare** — the element sits directly under the one-liner, with no heading of its own. [[Briefs]] is the worked example: H1, one sentence, then the `Area | Files carrying a # BRIEF` table. Take this when the one-liner already says what the table is, so a heading would only repeat it.

**Labelled** — an H2 names the element, and the element follows immediately. [[STONE|Stones]] was the worked example until 2026-08-29, when Dan removed its `## The map — what flows into what` heading to make the example proper: the one-liner should carry what the table is, and when it cannot, a header *row* inside the table ([[2026-08-19 Legacy Athletics]]'s `Card`) names it without opening a section. Take this when the element benefits from a name the one-liner cannot carry, or when the page has several substantial sections and the heart needs to be findable by heading.

**The labelled form is a heart, not a section.** The heading leads *straight* into the table — nothing between them. A heading that opens with prose is an ordinary section, and the zone has ended; the checker draws exactly that line, and got it wrong until 2026-08-10 (see § How it is checked).

## Fact card
**What it is.** A two-column table whose left cells are labels and whose right cells are the page's own facts — `Status`, `Counterparty`, `Their people`, `Value`, `Volume`, `Dates`, `Waiting on`, `Tech owes`, `Next` on an engagement page; `Role`, `Where met`, `Last contact`, `Owes / owed` on a person page. Inward-facing by construction: every cell is about *this* page's subject. It may *contain* links, but no row of it exists to send the reader elsewhere.

**Live:** [[2026-08-19 Legacy Athletics]] — eleven rows under a `Card` header, moved out of the spine 2026-08-29 as the first spine→heart migration; and [[STONE|Stones]] — the who-feeds-whom table, a fact card of a different shape. **Made-up:** [[Harbor Account Northwind]].

**There is no taxonomy of fact tables, on purpose.** A "map" of what flows into what was briefly its own kind here; Dan folded it back 2026-08-29: *"it's a set of facts — probably the most important facts about stones. There's probably a million different kinds of fact tables you could put in there; I'm not sure there's a clear categorization."* So the fact card is one kind with any shape: a label/value column pair, a matrix, a who-feeds-whom grid. What makes it a fact card is only that every cell is about the page's own subject.

**Where it had been living, and why that was wrong.** The [[SV Proj Template]] put the card in the masthead position, and six days of R-dispatch-table-06 at `fail` measured 434 mastheads carrying prose — the worst of them precisely these cards and the `@` person summaries. Dan, looking at Legacy Athletics: *"the spine indexes a page in the context of other pages — it is always outward-facing. The heart is always inward-facing: the meat, the summary, the most important content of a page."* The cap was right that the spine must be links-only; it had nowhere to send the words because the pages had no heart.

**The migration rule — a spine cell that talks about this page moves to the heart; one that explains another page moves to that page.** For a masthead row whose right cell fails the cap:

1. A **fact about this page's subject** (a status, a counterparty, a value, a date, a next step) becomes a row of the fact card. The spine row is dropped, or kept links-only if it also pointed somewhere.
2. An **explanation of a destination** ("~~[[X]]~~ — the tool that does Y") goes onto X's own top line (H1 + one-liner, `description:` frontmatter); the spine row keeps the link and at most a two-word tag.
3. **Anything else** — commentary, history, a caveat — goes into the body below the heart, never above it.

Nothing is deleted in the move; the cap becomes satisfiable *without loss*, which is the condition for re-arming it (the migration ran 2026-08-29 — 434 → 0 offending mastheads — and R-dispatch-table-06 is `fail` again with [[R-dispatch-guard]] armed). **One row that is not a fact card:** a child pulled above a list spine's `---` and described beside its link ([[Disk]]'s 10T / 8T / BLACK) is *spine*, and correctly so — the sentence describes another page. See [[DAS spine]] § List spine.

## Definition list
**What it is.** A fact heart that is not a table: the page's key facts written as a **definition list** — each bullet opens with a short bold naming phrase **ending in a colon**, then the body: `- **Term:** body` (Dan, 2026-08-29, on [[META Register]]: a colon after the term reads better here than the em-dash the vault's prose definition lists use). Mirrors HTML `<dl>`. Take it when the facts are sentences that would not survive being squeezed into cells — five properties that each need a clause, not a value. It is inward-facing like every fact heart: every term is about this page's subject. Named 2026-08-29 (Dan, on [[DAS ask-format]]: *"a different kind of fact heart, but one that isn't expressed as a table"*).

**Live:** [[META Register]] — six terms under the one-liner; [[DAS ask-format]] — the five things that distinguish a conformant ask surface (block-IDs, labeled alternatives, recommendation strength, numbered headers, acceptance phrasing), directly under the one-liner. **Made-up:** [[Harbor Tenancy Model]] — five terms (tenant, tier, depot, pool, quota), each a clause that would not survive a cell.

**A hybrid heart is legal.** Two elements can share the slot when they carry different halves of the substance — [[Agent Memory]] has a definition list (what the thing *is* and its rules) directly over a one-row register (the store itself), and Dan kept both (2026-08-29): *"it's okay to have a hybrid heart."* The test is still the fold: both must land before scrolling, and the prose that explains either goes into `## Overview` beneath, not between them.

**When a page has two candidates.** ask-format also carries a table of contents. Either could be the heart; the definition list wins because it is the page's substance and the TOC only orients — so the list sits first and the TOC follows it. That ordering is the general rule when a carrying heart and an orienting one meet on the same page.

## Register
**What it is.** The heart *is* the page: one row per thing the page exists to track, and the prose below only explains the table. Hand-written and load-bearing — an authored register must never be regenerated.

**Live:** [[Eli Bedtime Audio]] — the options survey *is* the page (Dan, 2026-08-29: *"the whole document is about that information; the rest is just detail explaining the heart table"*); [[Lumen Data Sources]] — H1, one sentence, then `Source | Where | Reach for it when`, one row per source. **Made-up:** [[Harbor Latency Budget]] — the per-hop budget table. ([[Disk]] was the earlier example and is retired here: its drive table is one of several, and the page's spine — a list spine with three drives pulled above the marker — is the more instructive thing about it.)

## Figure
**What it is.** The thing the page defines, drawn — an architecture diagram, a flow — **plus the parts table beneath it**: one row per piece the figure draws, linking out to the page that describes that piece. The figure carries no clickable links, so the table is the way from the picture to the parts; a figure with no table under it is a picture, not a heart (Dan, 2026-08-29). The figure sits directly under the one-liner with **no title**. In FEX, parts that are not built out link to [[FEX Empty]] so a click mints nothing.

**Live:** [[DAS Code Design]] — the subsystem figure, then the skills table. **Made-up:** [[FEX Figure Page]], [[FEX Architecture]].

## Types table
**What it is.** A specification page's own catalog of the **mutually exclusive subtypes** of the thing it specifies — one row per subtype, with what it is, its shape, and a live and a made-up example. It is still a fact table (every row is about this page's subject), but a particular category of fact worth its own name: the rows *partition* the type, so a reader sees the whole space and knows each instance falls in exactly one row before reading any one entry. Named 2026-08-29 (Dan: *"it's still a fact table, but it is an interesting category of fact — a mutually exclusive list of subtypes of this data type"*); it was briefly "kinds table".

**Live:** [[DAS spine]]'s shapes table, and the table at the top of this page. **Made-up:** [[FEX Dispatch Examples]] § The four kinds.

## Table of contents
**What it is.** The page's own sections, so a long page is navigable before it is read. Derived from the headings and regenerated (`md-toc.py`), so — like an electric zone — never hand-edited. It orients rather than carries. **It exists only on a long page**: `md-toc.py` inserts it above the 1,500-word floor and *removes* it below (`toc_table_iff_long`), so a short page cannot have this heart — the floor is the rule, not a suggestion, and a specimen had to be long to earn one.

**Live:** [[DAS ask-format]], [[DAS progressive-disclosure]]. **Made-up:** [[Harbor Upgrade Guide]] — eight steps, 1,600 words, the TOC directly under the one-liner.

## Roster
**What it is.** The members of a set this page fronts, one row per member, usually grouped by area. Most rosters list things that live *elsewhere* — [[Briefs]] lists every file in the vault carrying a `# BRIEF`, none of them its children — and that is the clean case: the rows are facts about the set, and routing to them is incidental.

**A roster of this folder's own children is also legal — even though the spine could carry them.** Ruled by Dan 2026-08-29. The dispatch table is the normal home for a page's children, and stays valid for them; but when the spine is already complex — structural rows, related links, pinned members — *and* the roster is big, the page is cleaner with the children split out as its heart: a links-only spine above the H1, the full roster with a sentence per member below it. The test is legibility of the page, not a rule about where children may appear. The one thing that does not change: a roster in the heart is written by the author, so it does not get a `---` marker and the machine never rewrites it — a roster that should be machine-maintained is a list spine ([[DAS spine]] § List spine), and belongs above the H1.

**Live:** [[Briefs]] — `Area | Files carrying a # BRIEF`, a roster of files elsewhere. **Made-up:** [[Harbor Integrations]] — the children case: five integration pages in the folder, rostered below the H1 with a sentence each because the spine above already carries six rows of structure; the `...` stays empty because the body links every child.

## What a heart is not
**A heart's job is never routing.** If the only reason an element sits under the H1 is to hand the reader other pages, that is spine work wearing a different hat — and a page whose spine and content are the same table simply has no heart. [[HHOP|Harbor Hops]] is that case deliberately; [[DVT|Devtools]] is the contrast, carrying a masthead that routes and a pipeline table that does not. A **roster** of the page's own children is the one sanctioned exception (§ Roster, 2026-08-29): it may live in the heart when the spine is already complex and the roster big, because there its rows are read as *the membership* — a sentence per member — not as a jump table.

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

**The detector was blind to the labelled form until 2026-08-10.** `heart_candidate()` ended its zone at the first H2, so [[STONE|Stones]] — put forward as the exemplar of what a page with a heart should look like — read as having no heart at all, along with 39 other pages. The cost was not cosmetic: `H01` protects a heart from being buried *later*, so a heart the detector cannot see has no protection at all, which was confirmed by pushing prose above Stones' map table and watching the check stay silent. Widening the zone took `H01` from 6 hits to 16 vault-wide with no other change; the regression test is `test-f319-labelled-heart.py`, whose six cases pin both directions — a labelled heart at the top must be found *and* not reported, the same heart buried must be reported, and a heading that opens a prose section must still end the zone.

## Why this is a slot facet
A heart is a **region inside a file** with a start and an end, appearing in documents of many different kinds, with a template on each of its two forms. That is the slot group's definition ([[DAS Facet]] § Facet groups), and it is what separates the heart from a true discipline like [[DAS markdown]], which selects nothing of its own and has no template.

It reads as a discipline in the `where::` grammar only because that grammar cannot express a **positional** region — `sentinel:` matches a region that announces itself with a marker, and the heart is defined by where it sits rather than by anything it says. So [[R-spine]] falls back to `` `always` ``, and the group is carried by this declaration instead. The file lives in `disciplines/` beside its sibling for the same reason: the folder is not the taxonomy.

# BRIEF

*(Maintainer note — cautions for editing this spec.)*

- **The spine doc is the pair, not the parent.** [[DAS spine]] § The heart is a pointer to this page; keep it a pointer. Detail added there instead of here will drift, which is how the heart ended up documented inside the spine spec in the first place.
- **Do not mint `R-heart`.** The checks belong to [[R-spine]] on purpose — a page's opening is graded once. A second ruleset would put two authorities over one zone, which is the same mistake [[R-dispatch-table]] is deliberately kept out of.
- **`H01`'s condition 4 is `body_weight() >= 200`.** Any test fixture shorter than that is never nominated regardless of how its heart sits, so a short fixture silently tests nothing. The first draft of `test-f319-labelled-heart.py` did exactly that and read as two failures in the code rather than in itself.
