---
description: the `key:: value` vocabulary a stone file carries — what is shared by every kind, what each kind declares, and the test for whether something is a key at all
---

| -[[DAS Stone Keys]]- | → [[DAS]] → [design](hook://design) → [DAS Stone Keys](hook://p/DAS%20Stone%20Keys)  |
| --- | --- |
| Parent | [[DAS Stone Design]],   |
| Facet | [[DAS Stone]],   |
| Related | [[DAS Rocks]],  [[DAS Pebble]],   |
| ... | [[DAS Anchor Design]],  [[DAS Anchor Toolkit Design]],  [[DAS Architect Design]],  [[DAS Architect PRD]],  [[DAS Atlas Design]],  [[DAS Audit API Design]],  [[DAS Audit Architecture]],  [[DAS Audit Completed Roadmap]],  [[DAS Audit Decisions]],  [[DAS Audit Design]],  [[DAS Audit Files Architecture]],  [[DAS Audit PRD]],  [[DAS Audit Roadmap]],  [[DAS Audit Rules Redesign]],  [[DAS Audit Stories]],  [[DAS Audit System Design]],  [[DAS Audit Testing]],  [[DAS Audit UX Design]],  [[DAS Bridge Design]],  [[DAS Bridge PRD]],  [[DAS Bridge Testing]],  [[DAS Bridge UX Design]],  [[DAS Code Design]],  [[DAS Code Skill Design]],  [[DAS Cook Design]],  [[DAS Crank Design]],  [[DAS Crank PRD]],  [[DAS Create Design]],  [[DAS Ctrl Design]],  [[DAS Daybreak Design]],  [[DAS Daybreak PRD]],  [[design/DAS Decisions]],  [[DAS Design]],  [[DAS Design Design]],  [[DAS Doc Design]],  [[DAS Drive Design]],  [[DAS Dupes Design]],  [[DAS Exp Design]],  [[DAS Feature Design]],  [[DAS Feature PRD]],  [[DAS Finalize Design]],  [[DAS Finalize PRD]],  [[DAS Find Design]],  [[DAS Fix Design]],  [[DAS Fortify Design]],  [[DAS Fortify PRD]],  [[DAS Groom Design]],  [[DAS Groom PRD]],  [[DAS Hygiene Design]],  [[DAS Install Design]],  [[DAS Land Design]],  [[DAS Land PRD]],  [[DAS Maintain Design]],  [[DAS MD Design]],  [[DAS Migrate Design]],  [[DAS Mint Design]],  [[DAS Mint PRD]],  [[DAS Move Design]],  [[DAS MUSE Architecture]],  [[DAS Parley Design]],  [[DAS Pilot Flow Design]],  [[DAS PR Flow Design]],  [[DAS Profile Design]],  [[DAS Publish Design]],  [[DAS Purchase Design]],  [[DAS Rewire Design]],  [[DAS Search Design]],  [[DAS Slug Scan Design]],  [[DAS Snip Design]],  [[DAS Streams Design]],  [[DAS Survey Design]],  [[DAS Tidy Design]],  [[DAS Tracking Design]],  [[DAS Utility Design]],  [[DAS Viz Design]],  [[DAS WP Design]],  [[DAS Yore Design]],  [[Query PRD]],  [[Template Examples]],   |

# DAS Stone Keys
The parameter vocabulary of a stone file: `key:: value` lines at the **top** of the document, above the prose, with the shared keys owned by the Stone discipline and the rest declared per kind.

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
| `appears::` | the control files this stone currently renders in, comma-separated by slug | **yes** | `stone`, machine-written |

`line::` is what makes propagation line-copying: every control file anywhere in the feed DAG renders a stone from this one string, so a stone reads identically wherever it appears.

**`appears::` was missing from this table until 2026-08-13 (F312 M3), and it is not a minor omission** — it is the second half of the propagation mechanism. `line::` says *what* renders; `appears::` says *where it currently does*, which is how `readback()` knows which projections to compare a stone against and how `cmd_update` knows what to withdraw when a stone stops being published. It is **machine-written**: `stone` rewrites it on every update (`_kv_set(st.keys, "appears", …)`), so hand-editing it is editing a cache. Measured over the live corpus the same day: **30 of 30 stones carry both keys and nothing else** — 22 pebbles and 8 rocks, the other four files under a `* Rocks/` folder being the folder-anchor pages rather than stones. A key on 100% of the corpus and absent from its own vocabulary is the two-engines hazard in miniature: the spec was not describing the thing.

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

**Required by this spec and carried by none of the corpus — measured 2026-08-13 (F312 M3): 0 of 22 live pebbles declare `tempo::`.** That is unanimous, and under the template-vs-population method it would ordinarily mean the population wins and the requirement is wrong. It does not mean that here, and the distinction is worth stating because it is the one case the method has to allow for: **the population is unanimous because the migration that would create the field has not run.** `tempo::` comes from [[LUMEN Nudge]]'s register, and moving those 17 rows in is **M5**, still open. Every existing pebble was minted by `stone new`, which writes `line::` and `appears::` and nothing else.

So `tempo::` is **required-after-M5, unenforced until then**, and this line is the record of that so a later reader does not mistake an empty column for a dead field. The practical consequence is the reason it matters: **arming a `tempo::`-required check today would fire on 100% of the corpus** — the vacuous-explosion shape, a rule whose first run condemns everything it looks at.

**The spelling is `last-raised::` with a hyphen, settled 2026-08-13 by measuring the vault rather than by preference.** [[TINK311 - Pebble parameters: tempo, last-raised, and the Nudge migration|F311]] and [[TINK312 - Feed: a second DAG over anchors, and the facets that travel it|F312]] both wrote `last_raised::` with an underscore, and `stone`'s `_KEY_RE` accepts either (`^([A-Za-z][\w-]*)::`), so nothing would have caught the disagreement. The live corpus is decisive: **110 occurrences across 7 hyphenated keys** — `runtime-seconds::`, `exit-code::`, `exclusion-note::`, `success-metric::`, `cost-estimate::`, `where-note::`, `selector-note::` — against **6 occurrences across 4 underscored ones**. Hyphen is the convention; both feature docs were corrected to match this spec rather than the reverse. It was worth settling now because **no pebble carries the key yet**, so the choice is free today and becomes a 17-row rename the moment M5 runs.

`state::` is narrowed to two values on purpose. *Done* is not a value — a completed pebble is **archived to a `done/` sibling**, so completion is a location. Only *declined* still needs recording in the file, because a declined pebble stays where it is and must not be re-raised.

## Rock's keys

**None yet beyond the shared `line::`**, and that is a finding rather than an omission. Everything [[DAS Rocks]] needed turned out to be positional: the ranked order and the caps tier labels live in the control file, which is the arrangement, and the rock's expansion — what `HR` stood for — is now simply the document's H1, because stones are numbered and no longer carry meaning in the filename.

If a rock key is proposed later, run it through the arrangement test first.

## Retired keys

| Key | Why it died |
|---|---|
| `anchor::` | It restated the path. A pebble lives in `{slug} Pebbles/` and is named `{slug} P0001`, so the owning anchor is in the folder *and* the filename. **A field that restates the path is a field that can disagree with it** — and when it does, nothing says which is right. |

## Where the vocabulary is enforced

Nowhere yet — but **no longer for the reason this section used to give**. `R-stone-06` fixes the position of the block as a `stated` rule, and the per-kind vocabularies were said to *"become checkable in the same pass that fixes the folder-facet selector"*. **That selector was fixed on 2026-08-11** ([[DAS Stone]] § Rules: a sweep over `Topic/MED` now visits `MED Rocks` as its own anchor and emits verdicts), so the stated blocker is gone and the vocabulary is checkable today.

What replaces it is a sequencing fact rather than a technical one, measured 2026-08-13:

- **The shared keys are checkable now and would pass.** `line::` and `appears::` are on 30 of 30 stones. A rule asserting them measures something real and starts green — which, per this project's standing caution, means the fixture has to prove it *can* fail before the green means anything.
- **The pebble vocabulary is not checkable yet, and arming it would be an explosion, not a finding.** `tempo::` is on 0 of 22. The rule would condemn the entire corpus on its first run, and a rule that fires everywhere gets turned off. It waits on **M5**, the [[LUMEN Nudge]] migration, which is what puts `tempo::` on a pebble in the first place.
- **`anchor::` is retired and stayed retired.** Nothing in the corpus carries it, so the retirement is complete rather than merely declared.

The order that follows: arm the shared keys with a deliberately-malformed fixture beside a clean twin, and arm the pebble vocabulary in the same pass as M5, never before it.
