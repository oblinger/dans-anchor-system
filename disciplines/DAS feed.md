---
name: feed
description: >
  Discipline — the second DAG over anchors. `feeds:` in `.anchor` names the
  anchors that feed into this one; out-edges are computed by inversion. A feed
  facet materializes as a folder of one-file-per-item with a roster on top,
  each item carrying `key::` parameters and a `line::` rendering. The top group
  of a roster is the export set, and it propagates to every anchor declaring
  this one as a source. Members: Rocks, and the item register. DRAFT — the
  facet-side naming is pending TINK F312 Q1.
tools: Read
user_invocable: false
---

# Feed

**Feed is how work becomes visible somewhere other than where it is owned.** An anchor holds its own planning surfaces; a feed is the declaration that another anchor draws from them, and the machinery that carries the top of one roster into the next.

**DRAFT, 2026-08-06.** Commissioned in [[TINK312 - Feed: a second DAG over anchors, and the facets that travel it|TINK F312]] and written ahead of its open questions. The naming landed 2026-08-06 (F312 Q5): the concept is **Feed** and the key is `feeds:`. What remains unwritten is the second member facet — that page is deliberately unwritten until F312 Q1 lands, because its filename and every one of its rule IDs depend on the answer.

## The second DAG

[[DAS anchor-dag]] describes the vault's **containment** graph: every anchor has a place, a breadcrumb up, dispatch links down. Feed is a **different graph over the same nodes** — supply rather than containment — and the two must never be merged.

The proof they are different is the case that motivated feeds at all: [[Vector]] sits at the top of the rocks feed and [[LUMEN|Lumen]] at the top of the item feed, and **neither is the parent of the anchors that feed them.** [[MED]] lives under `Topic/`. Reusing `parents:` for feed would either relocate MED or make its breadcrumb lie.

`anchor-dag` names itself a *global, corpus-level* discipline — a property of all the anchors together, verified by walking the whole graph rather than by authoring any one artifact — and explicitly opens a shelf for siblings of that shape. **Feed is the first genuine sibling**: same nodes, different edges, its own invariants (acyclic, every named source resolves, every item owned).

## Declaring an edge — `feeds:` in `.anchor`

An anchor names the anchors it draws from. Nothing declares the other direction; consumers are computed by inverting the graph.

- On [[Vector]]'s `.anchor` — `feeds: MED, CMX, NJ, SV, AIS`
- On `MED`'s `.anchor` — nothing

**The edge is declared by the consumer**, which has two consequences worth stating because they shape the tooling:

- **A leaf needs no configuration.** Creating an anchor never requires editing it to join the graph; it requires editing whoever should draw from it. New anchors cost one line, in one file, at the place that actually made the decision.
- **"Where does my work go?" needs an index.** It is not answerable by reading your own `.anchor`. That is a tooling job — invert the graph on read — and **not** a reason to also declare out-edges. Two declared directions is two things that drift apart, and the drift is silent.

**The prepositions carry the direction, and they are part of the vocabulary** (Dan, 2026-08-06). The noun takes *for* — **the feeds for Vector are MED, CMX, NJ**. The verb takes *into* — **MED feeds into Vector**. Both are needed: a bare *"MED feeds Vector"* is the one phrasing that could invert, and *into* closes it.

The plural noun is what makes `feeds:` safe as a key where `flows:` was not. *Your* feeds are what you subscribe to, not what you nourish — the subscriber reading is the dominant one in ordinary use, and a colon followed by a list cues it unambiguously.

## What a feed facet looks like

Every feed facet materializes the same way. This is the whole of what the discipline owns:

- **A folder** at `{anchor}/{slug} Track/{slug} {Facet}s/`, elective, cardinality 0-or-1.
- **One file per item**, plain markdown, named by the facet's own identity scheme.
- **`key:: value` parameters** in each item file — the double-colon form used throughout this repo, which works anywhere in the file rather than only in a frontmatter block.
- **`line::`** — the item's canonical one-line rendering, stored on the item. This is what every roster displays, so editing it changes the item everywhere it appears.
- **A roster** carrying a `...` catch-all so no item is ever lost, and grouped lines below it. **The top group is the export set**: those items, and only those, travel the outbound edges.
- **A link at the head of every roster line**, so the item is one click away. What the link is *named* and how it *renders* belongs to the facet, not here — see § What the facet declares.

## Propagation, and who may write

An item that sits in the export group of anchor `A`'s roster appears in the roster of every anchor whose `.anchor` lists `A` among its feeds.

**An item is written where it is owned, and read everywhere else.** The roster in the item's own anchor is the write surface — edit a line there and the next pass stores it back to `line::`. Every roster downstream of a `feeds:` edge is a **rendered copy**, machine-owned in the sense [[DAS Dispatch Table]]'s electric zones already establish: hand-edits are discarded on the next pass, and the zone says so.

This is not a restriction chosen for safety; it falls out of the structure. Each item has exactly one owning anchor, so exactly one roster can hold an authoritative edit. The alternative — reconciling edits made to the same line in two anchors — is the merge problem feed exists to remove, reintroduced one layer down.

## What the facet declares

The discipline is deliberately silent on four things, because its two known members disagree on all of them and each is right for itself:

| The facet declares | Why it cannot be shared |
|---|---|
| **Its parameter vocabulary** — which `key::`s are legal, which required | A rock has commitment; an item has tempo and a last-raised time. No overlap worth unifying. |
| **Its identity scheme** | [[DAS Rocks\|Rocks]] uses a human abbreviation (`HBR HR`) *because the link text is read in a narrow line* — `R-rocks-04`. Items want a short opaque ID because they are numerous and tracked as they move. |
| **Its presentation** | A rock's link text is the information: `[[HBR HR]]: gather stats`. An item hides its ID behind a star so the roster reads as a plain bullet. Applying either uniformly breaks the other. |
| **What the export group means** | For Rocks it is a commitment level; for items it is likely tempo or urgency. |

**The identity and presentation rows are the two places the members genuinely diverge**, and both are load-bearing. A discipline that fixed either would kill a shipped rule.

## Members

| Facet | Item | Root of its feed |
|---|---|---|
| [[DAS Rocks]] | a multi-week-to-quarter chunk of work | [[Vector]] — the global [[Rocks]] |
| *(pending F312 Q1)* | a small thing the user owes | [[LUMEN\|Lumen]] |

The roots are **convention, not mechanism** — nothing in this discipline privileges Vector or Lumen. They are the anchors that happen to declare everyone else as a source, and either could be replaced by editing one `.anchor`.

## Relationship to other disciplines

- **[[DAS anchor-dag]]** — the containment graph. Same nodes, different edges; see § The second DAG.
- **[[DAS stream]]** — the other multi-facet mechanism discipline, and the model this one follows: shared machinery here, per-facet specifics declared by the member. A feed facet's items may each carry a stream.
- **[[DAS file-association]]** — owns the general folder-attaches-to-a-parent placement; a feed folder is one shape of it, specialized by having a roster and an export semantics.

# BRIEF

- **What this is** — the discipline owning the feed DAG (`feeds:` in `.anchor`) and the shared shape of a feed facet: folder, one file per item, `key::` parameters, `line::`, a roster whose top group exports.
- **Status: DRAFT.** Written 2026-08-06 alongside [[TINK312 - Feed: a second DAG over anchors, and the facets that travel it|TINK F312]], ahead of its remaining questions. Q3 could split the roster out of the folder-note; Q4 could change the identity scheme. None of those change the shape above, which is why it was safe to write.
- **The second member facet is deliberately unwritten.** Its name is F312 Q1, and the name is its filename, its folder name, and every one of its rule IDs. Scaffolding it now would mean rewriting all three — [[feedback_lazy_file_creation]] applies exactly.
- **The two asymmetries are the part most likely to be lost.** A later reader will want to hoist identity and presentation up into this discipline for uniformity. Doing so deletes `R-rocks-04`, which exists because the wiki-link is read in a narrow line. § What the facet declares says why, and should survive any rewrite.
- **No ruleset yet.** `R-feed` is M1 of F312 and waits on Q3, since half its rules would assert the file count. The key name is settled.
