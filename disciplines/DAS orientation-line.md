---
name: orientation-line
description: "Slot facet. The orientation line is the one sentence directly under the H1 — a place with a role and no fixed form, saying what this file is before anything says what it contains."
user_invocable: false
group: slot
---

| -[[DAS orientation-line]]- | : Slot facet. The orientation line is the one sentence directly under the H1 — a place with a role and no fixed form, saying what this file is before anything says what it contains.<br>→ [[DAS]] → [[disciplines]] → [DAS orientation-line](hook://p/DAS%20orientation-line)  |
| --- | --- |
| Related | [[DAS spine]],  [[DAS heart]],  [[DAS progressive-disclosure]],  [[DAS Facet]] (§ Facet groups),  [[DAS Disciplines\|Disciplines]],  [[DAS\|dans-anchor-system]], |
| Rules | [[R-spine]],  [[R-doc-structure]],   |
| Examples | [[Lumen Nudge]],  [[Briefs]],  [[Stones]],   |

# Orientation-line Discipline
One sentence, directly under the H1, saying what this file is — the hinge between the spine that says where the page sits and the heart that shows what it holds.

| | Spine | **Orientation line** | Heart |
|---|---|---|---|
| **Where** | above the H1 | directly under the H1 | directly under the orientation line |
| **Subject** | other pages | **what this file is** | this page's own substance |
| **Owed by** | every page | **every page with an H1** | only a page with substance to lead with |
| **Form** | seven shapes | **none — a place, not a shape** | two — bare or labelled |

**Cardinality: one** — exactly one per document, under the head H1; a second sentence there is body, not a second orientation line.

It is the third layer of [[DAS progressive-disclosure]]: the title names the thing, the orientation line says what the thing *is*, and only then does the page say what it contains. A reader who stops after this line should still be able to say what they just opened.

## A place with a role and no fixed form
Every other slot in this family is recognizable by its shape — a spine by its marker, a heart by being a table or figure. **The orientation line is recognizable only by where it sits.** It is one line of ordinary prose in whatever words the subject needs, and the discipline deliberately specifies no template, no opening formula, and no length.

What it *does* specify is exactly three things, and each exists because its absence has a cost:

- **It is prose.** A heading, table, list, figure or fence there means the page jumped from its title straight to its contents — the reader learns what is inside before learning what it is.
- **It is one line.** No embedded newline. The line is read at a glance and often rendered alone; a sentence that wraps into a second prose line has become a paragraph, and a paragraph is body.
- **It adjoins the H1.** No blank line between them, so the heart lands on screen without scrolling (see [[DAS spine]] § The heart for the fold argument). This is `S05`, and `spine fix` actively closes that gap.

**Non-prose lines between the H1 and the line are skipped, not counted against it.** Inline `key:: value` fields (skill pages carry `requires::` / `subsystem::`) and the machine-written `<!-- state:backlog XX -->` / `<!-- state:q XX -->` stamps sit exactly there. The stamps are written by `state` rather than by the author, so counting them would make a state-managed doc **structurally unable** to satisfy the rule — found on the [[HBR]] reference anchor, and the same trap caught `md-toc.py`, which consumed the stamp *as* the orientation line and inserted the TOC above the real one.

## Where it is not owed
Four exemptions, each a document class whose head is a different convention rather than a defective version of this one:

- **Rendered query surfaces** — `Q.md` and `{slug} queries.md` carry a banner-only head owned by [[R-query]], on the user's ruling that those pages carry no meta prose.
- **`# RULESET` specs** — a machine-read class whose head is `# RULESET <id>` followed by `where::` / `include::` / `description::`, not breadcrumb → H1 → orientation (T051).
- **Simple-facet form** — a slug-prefixed facet page whose H1 fuses the breadcrumb into the title (`# [[{slug}]] {Facet}`). The wiki-link *is* the breadcrumb and the head is self-describing, so the file's essence may follow the H1 directly.
- **Pages with no H1 at all** — out of scope here; whether a page owes an H1 is [[R-doc-structure]]'s business, and one rule per question.

## How it is checked
No ruleset of its own — [[R-spine]] owns the zone, for the reason [[DAS heart]] gives: a page's opening is graded once, not once per line of it. Two checkers, one per property:

- **`doc_head_orientation_line`** — the line is present and is a single line of prose. Its two failure texts are deliberately different: *"no orientation line under the H1"* and *"orientation line … runs into the next line"* are different defects with different repairs.
- **`orientation_line_adjoins_h1`** (`S05`, grade `fail`) — no blank line between the H1 and the line.

Both resolve the H1 through the `_head_h1` primitive, which reads the **head** H1 rather than the first `# ` it finds — any heading of any level before the first H1 means there is no head H1. Spelling that scan by hand is how a checker ends up blaming a file's `# BRIEF` for a defect in its head; sixteen sites were consolidated onto the primitive, and a seventeenth in `spine.py` was still hand-spelling it as late as 2026-08-11 (T198), handing 215 pages an H1 that does not exist.

**Measured 2026-08-11 across the vault: 6,195 pages satisfy the rule and 2,096 do not.** That is a large enough population that it describes the corpus rather than a defect list, and it is why this page specifies the *place* and leaves the sentence to the author — a migration that also dictated wording would be unfinishable.

**One live contradiction, since removed at the root.** The F081 markdown rule `heading-spacing` demanded a blank line after every heading, which is exactly the blank line `S05` reports and `spine fix` deletes: conforming to one guaranteed a finding from the other, on 1,787 pages carrying the mandated shape, fired through a Stop hook in normal use. Reported by [[ATT|Atticus]] 2026-08-11 and patched the same day by exempting an H1 followed directly by prose. **That patch treated a symptom.** The residual 19,245 findings were the same contradiction one heading level down — Dan's standing instruction puts a heading's content on the very next line at *every* level — so on his answer to [[Tink Backlog#^T537|T537]] Q1 the blank-after check was deleted outright rather than narrowed a third time. There is now no second authority over this line at all, which is a stronger resolution than agreement between two checkers.

## Why this is a slot facet
It is a **region inside a file** — one line, with a start and an end — appearing in documents of many kinds, and it has a role a template could be written against. That is the slot group's definition ([[DAS Facet]] § Facet groups).

Like [[DAS spine]] and [[DAS heart]], it reads as a discipline in the `where::` grammar only because that grammar cannot express a **positional** region: `sentinel:` matches a region that announces itself with a marker, and this one is defined purely by sitting under the H1. [[R-spine]] therefore falls back to `` `always` ``, and the group is carried by this declaration instead. The file lives in `disciplines/` beside its two siblings for the same reason — the folder is not the taxonomy.

# BRIEF

*(Maintainer note — cautions for editing this spec.)*

- **Do not add a template, an opening formula, or a length bound.** The absence is the specification: this facet fixes a *place* and a *role*, and 2,096 non-conforming pages is a migration that stays finishable only because the sentence is the author's. A worked example belongs in the Examples row, never as a shape to copy.
- **Do not mint `R-orientation-line`.** The checks belong to [[R-spine]] on purpose, exactly as [[DAS heart]]'s do — a second authority over one zone is what produced the `S05` / `heading-spacing` contradiction in the first place.
- **Skip-lists are load-bearing and grow.** Anything machine-written that lands between the H1 and this line (today: `key::` fields, `state` stamps) must be skipped, or a doc whose stamp is not the author's becomes permanently unable to conform. Add to the skip list; never relax the prose test to accommodate one.
- **The exemptions are document classes, not escapes.** Each names a head convention that is complete on its own terms. A page that merely lacks an orientation line is not thereby a new class.
