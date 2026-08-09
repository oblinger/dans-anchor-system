---
description: the `key:: value` vocabulary a stone file carries — what is shared by every kind, what each kind declares, and the test for whether something is a key at all
---

# DAS Stone Keys
The parameter vocabulary of a stone file: `key:: value` lines at the **top** of the document, above the prose, with the shared keys owned by the Stone discipline and the rest declared per kind.

| -[[DAS Stone Keys]]- | → [[DAS]] → [design](hook://design) → [DAS Stone Keys](hook://p/DAS%20Stone%20Keys)  |
| --- | --- |
| Parent | [[DAS Stone Design]],   |
| Facet | [[DAS Stone]],   |
| Related | [[DAS Rocks]],  [[DAS Pebble]],   |
| ... | [[DAS Anchor Design]],  [[DAS Anchor Toolkit Design]],  [[DAS Architect Design]],  [[DAS Architect PRD]],  [[DAS Atlas Design]],  [[DAS Audit API Design]],  [[DAS Audit Architecture]],  [[DAS Audit Completed Roadmap]],  [[DAS Audit Decisions]],  [[DAS Audit Design]],  [[DAS Audit Files Architecture]],  [[DAS Audit PRD]],  [[DAS Audit Roadmap]],  [[DAS Audit Rules Redesign]],  [[DAS Audit Stories]],  [[DAS Audit System Design]],  [[DAS Audit Testing]],  [[DAS Audit UX Design]],  [[DAS Bridge Design]],  [[DAS Bridge PRD]],  [[DAS Bridge Testing]],  [[DAS Bridge UX Design]],  [[DAS Code Design]],  [[DAS Code Skill Design]],  [[DAS Cook Design]],  [[DAS Crank Design]],  [[DAS Crank PRD]],  [[DAS Create Design]],  [[DAS Ctrl Design]],  [[DAS Daybreak Design]],  [[DAS Daybreak PRD]],  [[design/DAS Decisions]],  [[DAS Design]],  [[DAS Design Design]],  [[DAS Doc Design]],  [[DAS Drive Design]],  [[DAS Dupes Design]],  [[DAS Exp Design]],  [[DAS Feature Design]],  [[DAS Feature PRD]],  [[DAS Finalize Design]],  [[DAS Finalize PRD]],  [[DAS Find Design]],  [[DAS Fix Design]],  [[DAS Fortify Design]],  [[DAS Fortify PRD]],  [[DAS Groom Design]],  [[DAS Groom PRD]],  [[DAS Hygiene Design]],  [[DAS Install Design]],  [[DAS Land Design]],  [[DAS Land PRD]],  [[DAS Maintain Design]],  [[DAS MD Design]],  [[DAS Migrate Design]],  [[DAS Mint Design]],  [[DAS Mint PRD]],  [[DAS Move Design]],  [[DAS MUSE Architecture]],  [[DAS Parley Design]],  [[DAS Pilot Flow Design]],  [[DAS PR Flow Design]],  [[DAS Profile Design]],  [[DAS Publish Design]],  [[DAS Purchase Design]],  [[DAS Rewire Design]],  [[DAS Search Design]],  [[DAS Slug Scan Design]],  [[DAS Snip Design]],  [[DAS Streams Design]],  [[DAS Survey Design]],  [[DAS Tidy Design]],  [[DAS Tracking Design]],  [[DAS Utility Design]],  [[DAS Viz Design]],  [[DAS WP Design]],  [[DAS Yore Design]],  [[Query PRD]],  [[Template Examples]],   |

## The test for whether something is a key at all

**Anything the user expresses by *arranging* is not a key.** The control file is the arrangement, and it already carries order, grouping, tier, and publication — position *is* the data. So none of those become fields:

| The user expresses… | by | not by |
|---|---|---|
| priority / tier | position in the control file, under a caps label | a `tier::` key |
| which anchor sourced it | the link target and the folder path | an `anchor::` key |
| whether it is published | being below the self-section | a `public::` key |
| grouping | adjacency under a header | a `group::` key |

A key earns its place only when the machine needs a fact the arrangement cannot express — a cadence, a date, a flag. That test is what keeps the block short enough to sit above the prose without burying it.

## Format and position

`key:: value`, one per line, **at the top of the file, above the body**.

**Double-colon, not frontmatter, and not by accident.** `::` is the vault's own convention, it works anywhere in the file rather than only in a header block, and — the deciding reason — **frontmatter is not visible by default.** A rock is a document a human reads often, and these keys carry real meaning about the stone; hiding them behind a fold makes the reader's model of the stone depend on a view setting. Dan, 2026-08-08: *"I don't think it's so good that they're not visible to the user."*

**Top rather than bottom, and this was genuinely close.** The argument for the bottom is that a rock is a long human-read document and a boilerplate block at the top is noise before the content. The argument that won: a reader who needs the cadence or the state should not have to scroll a long document to find it, and the block stays small precisely because of the arrangement test above. Recorded as a reversal-in-progress — Dan moved bottom → top mid-sentence — so if the block grows past a handful of lines, the bottom becomes right again and this is the paragraph to revisit.

## The shared key — every stone, every kind

| Key | Meaning | Required | Owner |
|---|---|---|---|
| `line::` | the canonical one-line rendering, which is what a control-file line displays after its provenance label | **yes** | Stone discipline |

`line::` is the only universal key, and it is universal because it is what makes propagation line-copying: every control file anywhere in the feed DAG renders a stone from this one string, so a stone reads identically wherever it appears.

## Pebble's keys

Declared by [[DAS Pebble]] on top of the shared key. Carried over from the Nudge register, whose grammar is shipped and self-tested.

| Key | Meaning | Required | Default |
|---|---|---|---|
| `tempo::` | the Nudge cadence grammar — how often this may be raised | **yes** | none |
| `last-raised::` | when it was last surfaced | no | empty = never raised |
| `alert::` | whether it earns a full-screen interrupt rather than a quiet listing | no | off |
| `created::` | mint date, so *"this has been ignored for six weeks"* becomes answerable | no | the file's own birth |
| `state::` | `open` or `declined` | no | `open` |

**Only `tempo::` is required**, and the reasoning generalises to every kind: everything else has a defensible default, and *a required field with a sensible default is a field that gets filled in wrong.*

`state::` is narrowed to two values on purpose. *Done* is not a value — a completed pebble is **archived to a `done/` sibling**, so completion is a location. Only *declined* still needs recording in the file, because a declined pebble stays where it is and must not be re-raised.

## Rock's keys

**None yet beyond the shared `line::`**, and that is a finding rather than an omission. Everything [[DAS Rocks]] needed turned out to be positional: the ranked order and the caps tier labels live in the control file, which is the arrangement, and the rock's expansion — what `HR` stood for — is now simply the document's H1, because stones are numbered and no longer carry meaning in the filename.

If a rock key is proposed later, run it through the arrangement test first.

## Retired keys

| Key | Why it died |
|---|---|
| `anchor::` | It restated the path. A pebble lives in `{slug} Pebbles/` and is named `{slug} P0001`, so the owning anchor is in the folder *and* the filename. **A field that restates the path is a field that can disagree with it** — and when it does, nothing says which is right. |

## Where the vocabulary is enforced

Nowhere yet, and deliberately so — see [[DAS Stone]] § Rules. `R-stone-06` fixes the position of the block as a `stated` rule; the per-kind vocabularies are declared by [[DAS Pebble]] and [[DAS Rocks]] and become checkable in the same pass that fixes the folder-facet selector.
