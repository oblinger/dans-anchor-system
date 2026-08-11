---
description: "the rocks facet — an optional {slug} Rocks/ folder per anchor holding the big chunks that anchor is trying to move; rocks form a tree and promotion up the tree is the main action"
---

| -[[DAS Rocks]]- | → [[DAS]] → [[FCT]] → [DAS Rocks](hook://p/DAS%20Rocks)  |
| --- | --- |
| Related | [[Rocks]],  [[DAS Agenda]],  [[DAS Roadmap]],  [[DAS Backlog]],  [[VEC Mandate]],   |
| Examples | [[HBR Rocks\|worked instance]],  [[Rocks\|the root aggregator]] (differently shaped — see § The root is not an instance) |
| Rules | [[R-rocks]],   |

# DAS Rocks
The big chunks an anchor is trying to move — an optional `{slug} Rocks/` folder holding one file per rock, ranked by a hand-arranged control file beside it, forming one node of a vault-wide tree whose root is the global [[Rocks]].

**TLDR** — a **rock** is a multi-week-to-quarter chunk of work an anchor is trying to move. Rocks are the `rock` kind of [[DAS Stone|stone]], so the folder, the numbering, the control file and propagation along the feed DAG are that facet's and are not restated here; this page holds what is true of **rocks specifically**. The facet materializes as a folder, `{slug} Track/{slug} Rocks/`, holding one numbered file per rock, ranked by the control file `{slug} Rock.md` beside it. **Cardinality: one** — at most one Rocks folder per anchor, and elective, so 0-or-1 in practice. Rocks form a **tree** — each rocks folder is a node, and **promotion** up the tree is the main action, ending at the global [[Rocks]]. Every rock is **owned by an anchor**; the global list never holds an unowned one. Tier vocabulary inside the control file is deliberately unspecified.

## Location

`{anchor}/{slug} Track/{slug} Rocks/` — inside the Track folder, beside [[DAS Agenda|Agenda]] and [[DAS Backlog|Backlog]].

Track, not Design: a rock is metadata about *the activity*, not design content about the artifact. Putting it in Design would collapse the Track ⟺ Design boundary [[DAS Track]] establishes, and would sit it next to [[DAS Roadmap|Roadmap]] — the neighbour it is most often confused with.

The anchor's `{slug} Track.md` dispatch table links the folder (`R-rocks-08`).

## Why this is a separate facet

Four rungs of the planning ladder, coarse to fine. Each exists because the one above it cannot express something:

| Facet | Grain | What it answers |
|---|---|---|
| [[DAS Agenda\|Agenda]] | the whole anchor | why this anchor exists and where it is going |
| **Rocks** | weeks → a quarter | the big chunks worth naming, ranked by **commitment** |
| [[DAS Roadmap\|Roadmap]] | ordered milestones | what happens in what **sequence** |
| [[DAS Backlog\|Backlog]] | a work item | what is being done **now** |

The rung Rocks occupies is the one where **a chunk can be named without being committed to**. A Roadmap milestone is a promise about order; a Backlog row is a promise about now. Neither can hold *"this is real, it matters, and nobody has agreed to do it."* That state is most of what long-range planning actually consists of, and Rocks is where it lives.

## Rock names are numbers

A rock file is named `{slug} R{NNNN}.md` — the anchor slug, then a monotonic number that is **never recycled**. `HBR R0001`, and what it stands for is the file's own H1 (*Historical retrospective*).

**This supersedes the abbreviation scheme** (`HBR HR`), which named rocks by a one-word acronym expanded inside the file. The abbreviation read better in a line, and that was a real advantage — but the name was also the identifier, so improving a rock's name silently re-pointed every line that cited it, including copies already propagated into other anchors. Numbering separates the two: the number is an opaque handle nothing has to keep in sync, and the readable half moved into the control line's display text.

Rocks are cited from the documents that organize execution, in a line of this form:

- `[[HBR R0001|HBR:]] gather stats` — which renders as `HBR: gather stats`

Link, colon, then a few words naming *the slice being worked right now*. Almost never is a whole rock in flight; what enters an execution list is a piece of one, and the words after the colon are the only part carrying today's information. The display half names the **source anchor** rather than the rock, so the same line reads correctly after it is copied downstream — which is what makes propagation line-copying instead of rendering.

The governing rule is now `R-stone-02` in [[DAS Stone]]; `R-rocks-04` is retired.

## The two files

A rock group is two things, and keeping them apart is the point:

1. **`{slug} Rocks.md`** — the folder's anchor page, with a dispatch table and a `...` catch-all, so a rock file dropped into the folder is surfaced without being hand-listed (`R-rocks-09`).
2. **`{slug} Rock.md`** — the **control file**, in `{slug} Track/` beside the folder, holding the ranked list grouped by how committed the anchor is.

**The ranking used to live on the folder page and no longer can.** An anchor page's top is machine-maintained, and the ranking is the one thing that must stay hand-arranged — so they are separate files. [[HBR Rocks]] and [[HBR Rock]] are the normative pair.

The tier vocabulary and layout are **deliberately unspecified here**, and differ by anchor and by level. What the spec does pin is that grouping expresses **commitment, not sequence** (`R-rocks-11`) — the moment tier lines grow dates and dependency arrows, the anchor has quietly acquired a second Roadmap.

The catch-all is load-bearing: it is what lets `R-rocks-05` *warn* about an unranked rock rather than erroring on a lost one.

## What a rock file holds

A plain markdown file. Typical shape — `## What` / `## Why now` / `## Shape` / `## Status` — but the facet does not mandate headings. What it does require:

- **The H1 says what the rock is**, since the filename is a number and carries no meaning of its own (`R-stone-02`). This replaces the retired expand-the-abbreviation requirement, which existed only because the name used to *be* the identifier.
- **No work rows** (`R-rocks-07`). A rock is not a backlog. When a slice of it becomes actual work, that work is a `{slug} Backlog` row; the rock file explains the chunk, it does not track it.

## The tree, and promotion

Each rocks folder is one **node**. The structure above it:

- **The global [[Rocks]] at `LST/Rocks.md` is the root** — [[Vector]] + Dan territory.
- **Life-area anchors** ([[MED]], [[CMX]], [[NJ]], [[SV]], …) are mid-level nodes when they do their own rock-level planning.
- **Sub-project anchors** may be lower nodes that roll up into a life-area node before reaching the root.

**Promotion is the main action** — deliberately moving a rock *up* the tree when it deserves a larger share of attention than its own level can allocate. Promotion is always **traceable**: the promoted row wiki-links back to the source, and the source entry is marked with where it went (`R-rocks-12`, `R-rocks-13`). That round-trip is what makes the tree navigable rather than merely nested.

**Demotion** is the inverse and is not a deletion. A rock that comes off the global list stays in its owning anchor's folder as an uncommitted rock — which is exactly the state this facet exists to hold.

**Every rock is owned by an anchor** (`R-rocks-12`). If a rock does not obviously belong anywhere, place it in the most plausible anchor; never leave it orphaned at the root.

### The root is not an instance

`LST/Rocks.md` is the top of the same tree but is **not** an instance of this facet and is not governed by [[R-rocks]]. It is a flat cross-anchor file, one row per life-area, with no owning `{slug} Track/`; its own Brief governs its format, which is load-bearing for [[DAS Daybreak|Daybreak]]'s focus-cut parse. The tree has a differently-shaped root on purpose — a per-anchor folder answers *"what are this anchor's big chunks"*, and the root answers *"what is the one thing in focus per life-area"*. Those are different questions and want different shapes.

## When appropriate

**An anchor gets a Rocks folder when** there are three or more multi-week-to-quarter chunks worth naming together, **and** conversations about which to commit to happen (or should happen) at this level.

**It does not when** there is one obvious chunk (promote it straight to the root, sourced from the anchor page), or the anchor is small enough that its whole future fits in the Agenda or Backlog, or creating it would produce an empty planning artifact.

**Bias to too-few over too-many.** Too many rocks facets means planning overhead and coverage loss — work lost among planning documents. Too few means the interplay between chunks stays hidden. The facet is elective and is never scaffolded (`R-rocks-10`, [[feedback_lazy_file_creation]]).

## Ownership

- **[[Vector]]** owns the root and coordinates promotion across the tree — see [[VEC Mandate]] § Manage the rocks tree.
- **The anchor's agent** owns rock detail within its own folder.
- **The user** is the final authority on what gets promoted, at every level.

## Relationship to other facets

- **[[DAS Roadmap|Roadmap]]** — sequence. A rock may become a milestone; a milestone is never a rock.
- **[[DAS Backlog|Backlog]]** — the now. Slices of an active rock become backlog rows; the rock file does not hold them.
- **[[DAS Discussion|Discussion]]** — a rock file commonly grows one as deliberation accumulates. Nothing here requires it; the [[DAS stream|stream]] forms apply as they do to any document.

## Audit

[[R-rocks]] — folder name and location, cardinality, tier-line integrity in the control file, no-work-rows, dispatch linkage, the catch-all, and the two tree rules (ownership, traceable promotion). Naming and numbering are [[R-stone]]'s.

# BRIEF

- **What this is** — the `rock` kind of [[DAS Stone]], specified where it differs. Elective, folder-form, one numbered file per rock, a hand-arranged control file, one node of a promotion tree. Anything true of every stone belongs in [[DAS Stone]]; only what is true of rocks belongs here.
- **This BRIEF used to tell you to defend `R-rocks-04`, and that instruction was wrong** — kept here because a maintainer note that defends a superseded decision is worse than a stale one: it reads as a warning and gets obeyed. The short-name rule was retired **on purpose** (superseded by `R-stone-02`), because the readable name was also the identifier, so improving a rock's name silently re-pointed every line citing it — including copies already propagated downstream. What survives is the narrower true thing: what gets read in a narrow line is the **display text** (`[[HBR R0001|HBR:]] gather stats`), and *that* must stay short. The filename is a number and is not meant to be read at all.
- **The tier structure is intentionally unspecified.** [[HBR Rock]] is normative about layout where this page is not. Do not promote the example's tier names into this spec.
- **The ranking lives in the control file, and a checker forgot once already.** `R-rocks-06` kept reading the folder-note after the Stone migration and judged **0 tier lines where 12 existed**, passing on every group in the vault for the wrong reason (fixed 2026-08-11). Any new rule about the ranked list reads `{slug} Rock.md` with a folder-note fallback — and gets a fire test, because on this facet a green rule has three times meant a blind one.
- **A discussion at the foot of a rock file is expected practice, not a requirement.** Mentioned once under § Relationship to other facets and deliberately not turned into a rule.
- **Merged from two parallel designs, 2026-08-06.** A [[TINK]] session built the folder shape from Dan's dictation ([[TINK309 - Rocks: the per-anchor facet for big chunks of work|F309]]); a [[Vector]] session the same day independently wrote a flat-file version with the tree/promotion/ownership model ([[VEC Journal]] 2026-08-06) and overwrote this file without knowledge of the first. Neither was wrong — each held half. **Folder shape** is Dan's explicit and twice-repeated instruction, and the Vector journal records that his rejection of a folder was about the *root* (`LST/Rocks/`), noting "not because folder-per-rock is bad." **Tree, promotion, ownership, and the no-orphan rule** are the Vector session's, and they fill the compile-into-a-global-plan hole the first design left open. Vector's embedded `# RULESET R-rocks` was dropped in favor of the standalone [[R-rocks]] — the repo default since 2026-07-13 (`R-facet-spec` § companion ruleset).
