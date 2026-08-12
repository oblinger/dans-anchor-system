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
