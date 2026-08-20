---
name: diagramming
description: >
  Discipline for figures — the judgement half of making pictures, as distinct
  from the mechanics of producing them. When a picture earns its place at all,
  shipping the editable source beside the export, and recording stated intent
  so the next agent does not re-introduce what the reader already rejected.
  Not user-invocable; cited by /viz, /imgen, and any skill that emits a figure.
user_invocable: false
---

# Diagramming Discipline
requires:: vault
subsystem:: [[DAS Doc Design]] — the Doc group's subsystem profile

**This set is judgement, not mechanism, and the split is deliberate.** [[R-diagram]] already holds the checkable half thoroughly — 22 rules across seven sub-sets covering geometry, graph aesthetics, C4 semantics, contrast, typography, data-ink and SVG hygiene. Every one of them asks *is this diagram correct* and presupposes the diagram exists. **Not one asks whether it should.** That is what lives here.

The tools live elsewhere too: [[DAS Viz]] holds the capability matrix — which renderer round-trips in Obsidian, which survives export with clickable regions. That is a snapshot of what today's renderers do, and it stays with the tool docs because it goes stale with the tooling. This file holds what outlives any of them.

> **A note on what `R-diagram` currently does.** The umbrella is **inert** — the rules are written and not armed. Cite them as the checkable half that *exists*, not as enforcement that *fires*. A figure that satisfies everything below can still be geometrically broken, and nothing will say so automatically yet.

## 1 — A picture earns its place, or it does not get made

The default is prose. A figure is worth its cost when it carries something the prose cannot, and the test is not whether a diagram *could* be drawn but whether the reader learns something from the drawing that the sentence beside it fails to deliver.

**A figure earns its place when it shows a relation the reader must hold several of at once** — a topology, a flow with branches, a containment hierarchy, a before-and-after. Prose serialises; those are the cases where serialising is the loss.

**A figure does not earn its place when it re-states a list.** Four boxes in a row with arrows between them, where the arrows mean "then", is a numbered list that costs a build step, a source file, an export, and a maintenance obligation every time the list changes. The tell is that you can read the figure aloud as a sentence without losing anything.

**Cost is the argument, and it is ongoing rather than one-time.** A figure has to be re-rendered when it changes, re-audited when it moves, and re-read by whoever inherits it. A figure that is *wrong* is worse than absent, because a picture reads as authoritative in a way a sentence does not — a reader who spots a contradiction between prose and figure will usually believe the figure.

**When the answer is no, say so where the question will be asked again.** A doc that deliberately carries no diagram is indistinguishable from one nobody got around to illustrating. One sentence — *"deliberately no figure: the relation here is a sequence, and § X states it"* — costs nothing and stops the next agent re-litigating it.

## 2 — Ship the editable source beside the export

**Every figure ships with the thing it was made from, next to the thing it renders to:** `.d2` / `.excalidraw` / `.py` beside the `.svg` / `.png`. For a generated image the **prompt is the source**, and the rule applies unchanged.

**The reason is that an export is a dead end.** An SVG can be hand-patched once, and after that nobody knows whether the source or the export is authoritative — the two drift, and the drift is silent because both still render. Shipping the source makes the answer structural: the source is canonical, the export is derived, and regenerating is always available.

**The practice was already universal before it was written down**, which is the strongest evidence it is right: eight `.d2` sources sit beside their SVGs across the vault's architecture figures. What it lacked was a statement — it was cited in [[DAS Doc Design]] and in the `/imgen` runbook as settled policy while being written down nowhere, which is how this discipline came to exist.

## 3 — Record stated intent, not just the picture

**A figure ships with a `{base}.desc.md` sidecar** capturing what the figure is *for*: what it must convey, what is deliberately included, what is deliberately **omitted**, layout and style decisions, and any audit-posture relaxation taken on purpose.

**The omissions are the load-bearing half.** What a figure leaves out is invisible in the figure, so without the sidecar the next agent to touch it is one plausible improvement away from re-introducing something the reader already rejected — *"I already said no examples in the boxes"*, *"we agreed no caption"*. The SVG cannot record a decision not to draw something.

Three habits make it work, and all three are what stop it decaying into a changelog:

- **Author it in the same turn as the first export.** A minimal first version beats none; it grows with the rounds.
- **Edit in place — it is a living summary, never a log.** Superseded preferences are *removed*, not struck through or stacked. Git history is the chronological record; the sidecar answers only *what does the reader want right now*.
- **Read it before any later edit**, and treat it as authoritative for what the figure must convey and must avoid.

*(Mechanics — the sidecar's skeleton and the per-tool workflow — are in `/viz`'s `viz-diagram` runbook. This section is the part that survives the tool.)*

## Where the boundary sits

| the question | where it is answered |
|---|---|
| should this figure exist? | **here**, § 1 |
| does the export have its source beside it? | **here**, § 2 |
| what did the reader already reject? | **here**, § 3 — and the figure's own `.desc.md` |
| do the boxes overlap; is the contrast sufficient? | [[R-diagram]] — 22 rules, currently inert |
| which renderer should I use? | [[DAS Viz]] § Capability matrix |
| how do I actually produce it? | `/viz diagram`, `/viz d2`, `/viz excalidraw`, `/imgen` |

**The line that sorts them: does the judgement survive the tool being replaced?** *"Use Excalidraw for a hand-drawn architecture sketch"* dies with `/viz`. *"A picture earns its place only when it says something the prose cannot"* does not. Where the test comes out close — the capability matrix is arguably about formats rather than about `/viz` — **volatility breaks the tie**, and content that goes stale with the tooling stays with the tool docs rather than taking the most permanent-looking home in the family.

# BRIEF

*(Maintainer note — the audience here is the agent editing this discipline.)*

- **Do not migrate `R-diagram`'s rules into this file.** They are the checkable half and they already have a home; a second copy is a second thing to drift. This file cites them and states what they do not cover.
- **Do not absorb [[DAS Viz]]'s capability matrix**, even though it passes the line test on a strict reading. § Where the boundary sits records why, and the reason is volatility rather than kind — re-deriving that argument is the failure this note exists to prevent.
- **§ 2 is the reason this discipline was written.** The source-alongside-output rule was cited as settled policy in two published files and written down in none; both citations pointed at a private memory slug that did not exist. If a future edit is tempted to compress § 2 back to a cross-reference, that is exactly the state it was rescued from.
- **Provenance.** Commissioned by [[TINK Backlog#^T566|T566]] from Dan's 2026-08-02 observation that the accumulated judgement about drawing pictures was *"different than the skill itself, which is kind of very mechanical"* and *"going to get published to other people."* [[TINK Backlog#^T558|T558]] established that the slot for that content is a discipline rather than a new per-skill file.
