---
name: feed
description: "Discipline — the second DAG over anchors. `feeds:` in `.anchor` names the anchors that feed into this one; out-edges are computed by inversion. A feed facet materializes as a folder of one-file-per-item with a roster on top, each item carrying `key::` parameters and a `line::` rendering. The top group of a roster is the export set, and it propagates to every anchor declaring this one as a source. Members: Rocks, and the item register. DRAFT — the facet-side naming is pending TINK F312 Q1."
tools: Read
user_invocable: false
group: discipline
---

# DAS Feeds

**Feed is an information flow discipline for aggregating information across anchors.** An anchor holds its own planning surfaces; a feed is the declaration that another anchor draws from them, and the machinery that carries what one anchor publishes into the next.

**Live since 2026-08-09**, implemented by `stone` ([[Tink313 - Stone: one script for every kind of stone, its control file, and the feeds between them|TINK F313]]). Eight `.anchor` files declare `feeds:` today. Commissioned in [[Tink312 - Feed: a second DAG over anchors, and the facets that travel it|TINK F312]] and drafted 2026-08-06 ahead of its open questions; § What the implementation changed records where the draft was overtaken.

## The second DAG

[[DAS anchor-dag]] describes the vault's **containment** graph: every anchor has a place, a breadcrumb up, dispatch links down. Feed is a **different graph over the same nodes** — supply rather than containment — and the two must never be merged.

The proof they are different is the case that motivated feeds at all: [[Vector]] sits at the top of the rocks feed and [[Lumen|Lumen]] at the top of the pebble feed, and **neither is the parent of the anchors that feed them.** [[MED]] lives under `Topic/`. Reusing `parents:` for feed would either relocate MED or make its breadcrumb lie.

`anchor-dag` names itself a *global, corpus-level* discipline — a property of all the anchors together, verified by walking the whole graph rather than by authoring any one artifact — and explicitly opens a shelf for siblings of that shape. **Feed is the first genuine sibling**: same nodes, different edges, its own invariants.

## Declaring an edge — `feeds:` in `.anchor`

An anchor names the anchors it draws from. Nothing declares the other direction; consumers are computed by inverting the graph. Registered as a field in [[DAS Dot Anchor]]; enforced by [[R-feed]]-01.

- On [[Vector]]'s `.anchor` — `feeds: MED, CMX, NJ, SV, AIS`
- On `MED`'s `.anchor` — nothing

**The edge is declared by the consumer**, which has two consequences worth stating because they shape the tooling:

- **A leaf needs no configuration.** Creating an anchor never requires editing it to join the graph; it requires editing whoever should draw from it. New anchors cost one line, in one file, at the place that actually made the decision.
- **"Where does my work go?" needs an index.** It is not answerable by reading your own `.anchor`. That is a tooling job — invert the graph on read — and **not** a reason to also declare out-edges. Two declared directions is two things that drift apart, and the drift is silent.

**The prepositions carry the direction, and they are part of the vocabulary** (Dan, 2026-08-06). The noun takes *for* — **the feeds for Vector are MED, CMX, NJ**. The verb takes *into* — **MED feeds into Vector**. Both are needed: a bare *"MED feeds Vector"* is the one phrasing that could invert, and *into* closes it.

The plural noun is what makes `feeds:` safe as a key where `flows:` was not. *Your* feeds are what you subscribe to, not what you nourish — the subscriber reading is the dominant one in ordinary use, and a colon followed by a list cues it unambiguously.

## What travels — and what this discipline does not own

What moves along a feed edge is a **stone**: one unit of work-worth-naming, held one-file-per-item in a folder, ordered by a hand-arranged **control file**. Its folder, its numbering, its keys, its control file and its display forms all belong to [[DAS Stone]] and are **not restated here**.

That boundary is not where the original design put it, and the move is the single most useful thing [[Tink313 - Stone: one script for every kind of stone, its control file, and the feeds between them|F313]] settled. F312 proposed *feed as a discipline with two member facets*, Rocks and Pebbles, sharing storage machinery the discipline would own. What shipped is **one facet parameterised by kind** — pebble and rock are kinds in a JSON config, not facets — so the shared machinery has a single home in [[DAS Stone]] rather than a home in a discipline plus two facets that must not diverge from it.

**The discipline is therefore smaller than drafted, and correctly so.** What is left here is exactly what is a property of the *graph*: who declares an edge, what travels one, and the three invariants any pass over the graph must hold. Nothing in this page names a kind.

## Propagation is line-copying, not rendering

A stone that its owning anchor **publishes** appears in the control file of every anchor whose `.anchor` lists that owner among its feeds. Reach is **transitive** — if Vector declares `feeds: MED` and MED declares `feeds: X`, then X's stones reach Vector — while the **declaration is not**: only the direct edge is written, and reach is computed. A top that saw only its direct children would not be a top, and re-declaring the subtree at every intermediate anchor is the duplication § Declaring an edge rejects.

**The unit that travels is the control line itself, copied verbatim.** A control line opens with a link whose *target* is a numbered stone and whose *display* is a short provenance label — `[[Vector R0001|VEC:]] decide Aria`, reading `VEC: decide Aria`. Because the display carries the source anchor, that exact line is correct in any anchor and still resolves to the original stone, so it can simply be copied.

**This is what keeps a downstream control file hand-editable.** A rendered block would have to be machine-owned — an electric zone, hand-edits discarded — because a render has no way to accept an edit. A copied line has: it is ordinary text in an ordinary file, and the human who arranges the file arranges the imported lines along with their own. Where an import lands is the consumer's choice, expressed by writing a header for the source ([[R-stone]]-04).

## Who may write

**Every control file is a write surface, not only the owner's** — settled 2026-08-13 as [[Tink312 - Feed: a second DAG over anchors, and the facets that travel it|F312]] Q6 = (C), which supersedes F312's original single-owner resolution.

A control line differing from its stone is an **edit of the stone** wherever it is found: the edit travels up to the stone, and every projection is rewritten to match. Convergence is guaranteed — every projection equals its stone at the end of a pass. This is what keeps a downstream control file hand-editable, which single-owner would have cost: a rendered block has no way to accept an edit, so it would have to be an electric zone.

**Two projections of one stone edited to DIFFERENT values in one pass is a collision, and the pass refuses.** It names the stone and quotes every value in conflict, and nothing is written — the same before-any-write abort a cycle gets, because a half-reconciled tree is worse than an unreconciled one. Resolve by hand and re-run. Two projections edited to the *same* new text is not a collision and converges normally: taking one of two identical values discards nothing, so only genuine disagreement is reported.

**The ruling turned on silence, not on the trade-off it appeared to be about.** The choice was never hand-editability versus safety — it was hand-editability versus *silence*, and only the silence was load-bearing. Under the shipped last-writer-wins model a discarded edit was invisible by nature: the projections converge, every file looks right afterwards, and nothing anywhere records that a second edit ever existed. That is the failure shape this page's own invariant 3 names and `R-feed`-04 states as a rule, so keeping it would have left the discipline holding a no-silent-empty rule while its one implementation lost writes quietly. In practice the user arranges control files ([[DAS Stone]] § Who edits what) and agents write stone files, so the collision is rare rather than impossible — which argued that the report will almost never fire, not that it should not exist. Guard: case H in `test-f313-stone.py`, which also pins that agreeing edits still converge, so the check cannot pass by refusing every multi-file edit.

## The three invariants

Any pass that walks the feed DAG holds all three. They are stated as rules in [[R-feed]] and guard-tested in `test-f313-stone.py`.

- **Acyclic, reported as a path.** A cycle makes ownership circular, and ownership is what write-back rests on. Reported as `A → B → C → A` and the pass aborts before writing anything — never as a boolean, because a cycle you cannot locate is a cycle nobody fixes. (`R-feed`-02, case I.)
- **Every edge resolves.** A name matching no anchor is quoted and fails the pass — but drops only its own edge; the rest of the DAG still reconciles. This is the least visible of the three and the reason the others are not enough: an unresolvable source supplies zero stones and is *indistinguishable from a source that happens to be empty*, so a typo'd edge would otherwise stay invisible forever. The narrower blast radius is 2026-08-27 (T599): a whole-pass abort meant one retired slug in one `.anchor` took reconciliation offline vault-wide, and unlike a cycle a missing source poisons nothing downstream of itself. (`R-feed`-03, case N.)
- **No silent empty.** A pass reports its counts on a run with nothing to do exactly as on a busy one — a pass that prints nothing when it does nothing cannot be told apart from a pass that never ran. (`R-feed`-04, case O.)

## Members

| Kind | Item | Root of its feed |
|---|---|---|
| `rock` ([[DAS Rocks]]) | a multi-week-to-quarter chunk of work | [[Vector]] — the global [[Rocks]] |
| `pebble` | a small thing the user owes | [[Lumen\|Lumen]] |

Both are kinds of [[DAS Stone]], declared in the kind table in [[DAS Stone]]; a third needs no code. The roots are **convention, not mechanism** — nothing here privileges Vector or Lumen. They are the anchors that happen to declare everyone else as a source, and either could be replaced by editing one `.anchor`.

## What the implementation changed

Four things the 2026-08-06 draft asserted, and what 2026-08-09 shipped instead. Each is recorded rather than silently overwritten, because three of them were *resolved decisions* in F312 and one of them was a prediction this page made about itself.

- **Discipline-plus-two-facets → one facet, two kinds.** See § What travels. The shared machinery has one home instead of three.
- **A roster (the folder-note) → a separate control file.** F312 Q3 chose the one-file form and recorded a reservation: two files *"become genuinely safer once propagation writes downstream rosters."* The reservation fired, and the two-file form shipped — the ranking must stay hand-arranged and an anchor page's top is machine-maintained, so they cannot be the same file.
- **Rendering → line-copying**, and with it the write model. See § Who may write.
- **The two "measured asymmetries" collapsed.** This page argued that identity and presentation could never be shared between the members, and warned that "a discipline that fixed either would kill a shipped rule." A facet fixed **both** — every kind uses `{slug} {PREFIX}{NNNN}` and the same `{slug}:` display — and it did kill a shipped rule: `R-rocks-04` is retired. The prediction was right about the mechanism and wrong about the conclusion. The rule it protected existed because a rock's readable name was also its identifier, which turned out to be the defect: improving a name silently re-pointed every line citing it, including copies already propagated downstream. Numbering separates the two, and the readable half moved into the control line's display text, where it is still short and still read in a narrow line.

## Relationship to other disciplines

- **[[DAS anchor-dag]]** — the containment graph. Same nodes, different edges; see § The second DAG.
- **[[DAS stream]]** — the other multi-facet mechanism discipline, and the model this one was drafted after. The model turned out to fit Stream and not Feed: Stream's members genuinely differ in their entry skeletons, where Feed's turned out to differ in nothing structural at all, which is why they became kinds rather than facets.
- **[[DAS file-association]]** — owns the general folder-attaches-to-a-parent placement; a stone folder is one shape of it.

# BRIEF

- **What this is** — the discipline owning the feed DAG: the `feeds:` key, its consumer-only declaration, propagation by line-copy, and the three invariants. Ruleset: [[R-feed]].
- **This page is deliberately small, and shrinking it was the work.** Everything about how an item is *stored* belongs to [[DAS Stone]]. If you find yourself writing a folder name, a numbering scheme, a `key::` or a display alias into this page, it belongs there. The one test: this page names no kind.
- **§ Who may write was an open divergence until 2026-08-13 and is now a rule.** F312's § Resolved had said single-owner while `stone` implemented last-writer-wins; Q6 = (C) kept the implementation's write model and removed its silence. If you find a doc still describing single-owner, or a discarded edit that nothing reported, that is drift against a settled ruling — not the old divergence.
- **The three invariants are `stated`, not `checked`, and that is not a gap to close.** No `where::`-selected file can evidence "the graph is acyclic". They are enforced at run time in `stone` and held by named guard tests; arming them as `checked` would buy a coverage claim and no coverage — the failure [[DAS Stone]]'s BRIEF warns about at length.
- **Two of the three invariants shipped untested and were caught here.** Only acyclicity had a guard; resolvability and no-silent-empty were implemented, cited in the code by F312 invariant number, and asserted by nothing — added as cases N and O on 2026-08-11, before this ruleset was allowed to claim them.
