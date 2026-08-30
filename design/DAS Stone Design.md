---
description: the architecture of the stone system — the four surfaces, the one line that is both an ordering decision and a machine reference, and the propagation pass over the feed DAG
---

| -[[DAS Stone Design]]- | → [[DAS]] → [design](hook://design) → [DAS Stone Design](hook://p/DAS%20Stone%20Design)  |
| --- | --- |
| Keys | [[DAS Stone Keys]],   |
| Facet | [[DAS Stone]],   |
| Rules | [[R-stone]],   |
| ... | [[DAS Anchor Design]],  [[DAS Anchor Toolkit Design]],  [[DAS Architect Design]],  [[DAS Architect PRD]],  [[DAS Atlas Design]],  [[DAS Audit API Design]],  [[DAS Audit Architecture]],  [[DAS Audit Completed Roadmap]],  [[DAS Audit Decisions]],  [[DAS Audit Design]],  [[DAS Audit Files Architecture]],  [[DAS Audit PRD]],  [[DAS Audit Roadmap]],  [[DAS Audit Rules Redesign]],  [[DAS Audit Stories]],  [[DAS Audit System Design]],  [[DAS Audit Testing]],  [[DAS Audit UX Design]],  [[DAS Bridge Design]],  [[DAS Bridge PRD]],  [[DAS Bridge Testing]],  [[DAS Bridge UX Design]],  [[DAS Code Design]],  [[DAS Code Skill Design]],  [[DAS Cook Design]],  [[DAS Crank Design]],  [[DAS Crank PRD]],  [[DAS Create Design]],  [[DAS Ctrl Design]],  [[DAS Daybreak Design]],  [[DAS Daybreak PRD]],  [[design/DAS Decisions]],  [[DAS Design]],  [[DAS Design Design]],  [[DAS Doc Design]],  [[DAS Drive Design]],  [[DAS Dupes Design]],  [[DAS Exp Design]],  [[DAS Feature Design]],  [[DAS Feature PRD]],  [[DAS Finalize Design]],  [[DAS Finalize PRD]],  [[DAS Find Design]],  [[DAS Fix Design]],  [[DAS Fortify Design]],  [[DAS Fortify PRD]],  [[DAS Groom Design]],  [[DAS Groom PRD]],  [[DAS Hygiene Design]],  [[DAS Install Design]],  [[DAS Land Design]],  [[DAS Land PRD]],  [[DAS Maintain Design]],  [[DAS MD Design]],  [[DAS Migrate Design]],  [[DAS Mint Design]],  [[DAS Mint PRD]],  [[DAS Move Design]],  [[DAS MUSE Architecture]],  [[DAS Parley Design]],  [[DAS Pilot Flow Design]],  [[DAS PR Flow Design]],  [[DAS Profile Design]],  [[DAS Publish Design]],  [[DAS Purchase Design]],  [[DAS Rewire Design]],  [[DAS Search Design]],  [[DAS Slug Scan Design]],  [[DAS Snip Design]],  [[DAS Streams Design]],  [[DAS Survey Design]],  [[DAS Tidy Design]],  [[DAS Tracking Design]],  [[DAS Utility Design]],  [[DAS Viz Design]],  [[DAS WP Design]],  [[DAS Yore Design]],  [[Query PRD]],  [[Template Examples]],   |

# DAS Stone Design
The architecture behind [[DAS Stone]]: what the pieces are, which of them the human owns, which the machine owns, and why the seam between them is a single line of markdown.

## The architecture in one picture

Four surfaces, and every one of them is a plain markdown file a human can open:

| Surface | Owner | What it holds |
|---|---|---|
| **stone file** — `{slug} R0001` | agents | one unit of work: keys at the top, prose below |
| **control file** — `{slug} Rock` | **the user** | the ordering, the grouping, and what is published |
| **`feeds:` in `.anchor`** | the user | which anchors this one draws from |
| **`stone` CLI** | the machine | keeps the first two consistent and moves lines along the third |

The inversion is deliberate and is the whole design: **agents write the content, the human writes the arrangement.** Everywhere else in this system the machine renders and the human must not touch the output — an electric zone. Here it is the opposite, and it has to be, because *priority is not derivable*. No agent can compute which of four rocks matters most this quarter; that is the one thing only the user knows, so it is the one surface the machine may not rewrite.

## The seam: one line, two readers

Everything above works because of a single representation choice.

    [[Vector R0001|VEC:]] decide Aria

A human reads `VEC: decide Aria` — a Vector item about deciding Aria. A machine reads a link to `VEC R0001` followed by that stone's `line::`. **The same bytes carry the human's ordering decision and the machine's reference**, with the machine's half hidden inside the link where it does not muddy the human's view.

Three properties fall out, and each of them is load-bearing:

- **It survives cut and paste.** The user rearranges by moving lines. Nothing needs re-resolving because the reference travels inside the text.
- **It survives crossing anchors.** Pasted into Lumen's control file, the line still resolves to Vector's stone and still says it came from Vector. Propagation is therefore *line-copying*, not rendering — which is what lets a downstream file remain hand-editable.
- **It degrades gracefully.** If `stone` never runs again, every control file is still a readable, clickable document. Nothing is generated, so nothing rots into a stale block.

## Identity by link target, not by appearance

A **header** is any line whose *first* link targets a control file. That single rule does two jobs: pointing at this file's own control file marks the **self-section**, and pointing at another anchor's marks that anchor's **import site**.

Because identity lives in the target, the *display* forms are free to be terse and even to collide — `VEC:` for a stone, `-VEC-` for a header, both aliased. The renderer still distinguishes them for free: punctuation **inside** the link is painted as link text, punctuation **outside** it is not. So `[[Vector Rock|-VEC-]]` and `[[VEC]]:` are visibly different in reading view without opening the source.

This is why **the control-file name is configuration rather than convention** — nothing downstream depends on what it is called, only on what points at it.

## The propagation pass

`stone update` reconciles, in this order:

1. **Scan** each stone folder for files, and each control file for lines.
2. **Reconcile locally** — a new stone gets a line at the top; a deleted stone loses its line; a changed `line::` is rewritten in place. Existing lines keep their position, always.
3. **Collect published stones** — those below each anchor's self-section.
4. **Walk the `feeds:` DAG** and, for each downstream anchor, insert at its header for that source (block form, or inline comma-separated if the header carries a trailing colon), else at the top.

Three invariants govern the walk, inherited from [[DAS Feed]]: **acyclicity**, reported as a path rather than a boolean; **resolvability**, failing loudly on an edge naming no anchor; and **no silent empty**, because a pass that propagates nothing must say so rather than exit clean.

## The checker cannot see this facet yet

**[[R-stone]]'s rules are all `stated`, not `checked`, and shipping them that way is a deliberate refusal.**

A stone group is a *folder*, and a folder-shaped facet carries its own `.anchor`. The audit scopes to one anchor without descending into sub-anchors, while these rulesets write their selector from the parent's point of view — `{anchor}/**/* Rocks/**` — which is unsatisfiable from both ends: from the parent the folder is out of scope, and from the folder itself the pattern demands a nested copy of itself. Measured 2026-08-08: **zero `R-rocks-*` rules fire on either live Rocks group, at any scope**, while five other rulesets fire normally on the same runs. The same holds for `R-wp` and `R-fct-outputs`.

Arming `R-stone` today would produce rules that read `(checked)`, an audit that reports no failures, and nothing enforced — the shape that has already produced three false clean bills in two days. The rules convert to `checked` in the same pass that fixes the selector, and the acceptance test is that they **fire** on a real group.

## What is deliberately not here

- **No status vocabulary.** Completion is a *location* (an archived sibling), not a value.
- **No priority field.** Priority is position — see [[DAS Stone Keys]] § The test for whether something is a key at all.
- **No generated blocks.** Every surface stays hand-editable; the machine only ever adds, removes, or rewrites individual lines.
