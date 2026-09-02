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
| `enrolled::` | the anchors this stone was **pushed** to by a deliberate act ([[DAS Stone]] § Placement), comma-separated by slug; present only while there is one | no | `stone push` / `recall`, machine-written |

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
| `due::` | the moment by which an outcome in the world must have happened — the field that makes a pebble **timed**, and so the shape that needs a watcher | no | none — an ordinary pebble has priority but no timing |
| `done::` | the observable outcome in the world that ends the watch — *"he replies"*, *"the drive is unplugged"*, *"the row leaves `[Questions]`"* | no; **required by any anchor whose `.anchor` says `accepts: due, done, importance`** | none |
| `importance::` | `low` / `nominal` / `high` / `critical` — how much it matters, crudely; the watcher picks the rung from this, the owner does not | no; required where `accepts:` names it | none |

**`due::`, `done::` and `importance::` arrived 2026-08-29 with placement ([[Tink626 - Stone placement an explicit push verb, so enrolling a watch cannot|TINK T626]]).** The date field is `due::` — not `ends`, not `deadline` — because it is what a date field is called everywhere else. There is deliberately no `spark` kind: a pebble carrying a `due::` *is* one, and Dan rejected the name on collision grounds (*"file a spark for Sparks"* is one sibilant from ambiguous, spoken to a watch). They pass the arrangement test because no position in a control file can express a clock. None is required at the mint; all three are required at the **push** into an anchor that declares them, which is where a missing one can still be fixed by the agent who knows the answer. T626's draft named the third key `then::` — *what to do if it does not land* — and it was dropped before shipping: [[ASTR Comms]] § The handoff contract (take two, same day) moved that decision to the watcher, so asking the owner for it would ask for a rung it should not be choosing.

**Only `tempo::` is required**, and the reasoning generalises to every kind: everything else has a defensible default, and *a required field with a sensible default is a field that gets filled in wrong.*

**The `tempo::` grammar, carried verbatim from the Nudge register when M5 retired it (2026-08-13).** This table is now the canonical spec — the register's `# BRIEF` no longer exists, and `nudge-check.py --selftest` pins every form. A tempo answers two questions in one value — *when do I raise this next*, and *how often after that* (Dan, 2026-08-06: *"it's just telling you when is the time that you should bother me again and how often should you bother me?"*):

| `tempo::` | Means |
|---|---|
| `2026-08-07 07:00` | one moment, then the pebble is done |
| `2026-08-10` | one day, no particular hour |
| `daily` | every morning until it moves |
| `weekly` | once midweek, and again at Friday's close |
| `2026-08-07 07:00 → daily` | first at that moment, every day after at that time |
| `2026-08-06 10:00 → weekly` | first at that moment, same weekday and time after |
| `every 3 hours` / `hourly` | sub-day repeat |
| `waiting` | blocked on a person or an event — no clock |

Two rules ride with the grammar, both learned the hard way in the register era. **An `alert:: 🔔` on a date-certain tempo must carry a TIME, or the bell is decorative** — only a time-bearing tempo fires from the daemon; a day-only date is Daybreak's to surface, and a 🔔 with no clock has no path to the user the day Daybreak doesn't run (that is how Eli's birthday bell went unfired on 2026-08-08). `waiting` is the one honest exception — a 🔔 there means *flag this loudly whenever it resolves*. And **choosing a tempo is a real decision**: `daily` is a promise to raise something every single morning and the fastest way to train the user to ignore the channel; `weekly` is the honest default for *"soon, but not today"*.

**`tempo::` was carried by none of the pre-M5 corpus — measured 2026-08-13 (F312 M3): 0 of 22 live pebbles.** That was unanimous, and under the template-vs-population method it would ordinarily mean the population wins and the requirement is wrong. It did not mean that here, and the distinction is worth stating because it is the one case the method has to allow for: **the population was unanimous because the migration that would create the field had not run.** M5 ran later the same day: the 17 [[Lumen Nudge]] rows are now pebbles carrying `tempo::` (and `alert::`/`last-raised::` where earned), so the corpus is 17-of-39 — every migrated pebble carries it, every pre-M5 mint still does not. **What now gates arming the requirement is the backfill of the pre-M5 pebbles**, which is a per-owner judgment call (what *is* the tempo of "sweep 390 person pages"?), not a mechanical fill.

**The spelling is `last-raised::` with a hyphen, settled 2026-08-13 by measuring the vault rather than by preference.** [[Tink311 - Pebble parameters: tempo, last-raised, and the Nudge migration|F311]] and [[Tink312 - Feed: a second DAG over anchors, and the facets that travel it|F312]] both wrote `last_raised::` with an underscore, and `stone`'s `_KEY_RE` accepts either (`^([A-Za-z][\w-]*)::`), so nothing would have caught the disagreement. The live corpus is decisive: **110 occurrences across 7 hyphenated keys** — `runtime-seconds::`, `exit-code::`, `exclusion-note::`, `success-metric::`, `cost-estimate::`, `where-note::`, `selector-note::` — against **6 occurrences across 4 underscored ones**. Hyphen is the convention; both feature docs were corrected to match this spec rather than the reverse. It was worth settling now because **no pebble carries the key yet**, so the choice is free today and becomes a 17-row rename the moment M5 runs.

`state::` is narrowed to two values on purpose. *Done* is not a value — a completed pebble is **archived to a `done/` sibling**, so completion is a location. Only *declined* still needs recording in the file, because a declined pebble stays where it is and must not be re-raised.

## Rock's keys

**None yet beyond the shared `line::`**, and that is a finding rather than an omission. Everything [[DAS Rocks]] needed turned out to be positional: the ranked order and the caps tier labels live in the control file, which is the arrangement, and the rock's expansion — what `HR` stood for — is now simply the document's H1, because stones are numbered and no longer carry meaning in the filename.

If a rock key is proposed later, run it through the arrangement test first.

## Loop's keys

A stone becomes a **loop** ([[DAS Loop]]) by carrying a workflow and a step. Every one of these passes the arrangement test: none can be expressed by position, and none restates the path.

| Key | Meaning | Required | Owner |
|---|---|---|---|
| `workflow::` | wiki-link; whatever it points to is the workflow (a template, a page with `## Workflow`, or the stone itself) | **yes** | owner at `loop start`; recorded even when `channel::`'s page supplied it |
| `step::` | the current step's name in the resolved workflow | **yes** | `loop`, machine-written — `advance` is the only way it changes |
| `entered::` | date `step::` was entered; every relative `when` counts from here | **yes** | `loop`, machine-written |
| `lapses::` | one honest clause on what is lost if the loop fails — the Traffic board's right column | **yes** | owner |
| `channel::` | wiki-link to the counterparty (`[[@Cigna]]`); its page may carry the default `workflow::` | no | owner |
| `closed::` | date the loop closed; `close` recalls the reference from the watch list | written by `loop close` | `loop` |
| bindings | whatever the workflow's `requires::` names (`window-open`, `run-out`, `return-id`, `ship-by`), plain `key:: value`; a `key:` probe reads any key (`ordered`, `tracking`, `arrived`) | per workflow | owner, or the agent recording Dan's act |

`tempo::` is written by the step from the workflow's `raise::`; `importance::` may be rewritten by a step's annotation. The Traffic spine's `raise` field has no key — it is the current step's evaluated `when`, recomputed each cycle so it cannot rot ([[Tink635 - Loop mechanism: a stone that carries a process, so Traffic can run it|TINK F635]] § Resolved).

## Retired keys

| Key | Why it died |
|---|---|
| `anchor::` | It restated the path. A pebble lives in `{slug} Pebbles/` and is named `{slug} P0001`, so the owning anchor is in the folder *and* the filename. **A field that restates the path is a field that can disagree with it** — and when it does, nothing says which is right. |

## Where the vocabulary is enforced

Nowhere yet — but **no longer for the reason this section used to give**. `R-stone-06` fixes the position of the block as a `stated` rule, and the per-kind vocabularies were said to *"become checkable in the same pass that fixes the folder-facet selector"*. **That selector was fixed on 2026-08-11** ([[DAS Stone]] § Rules: a sweep over `Topic/MED` now visits `MED Rocks` as its own anchor and emits verdicts), so the stated blocker is gone and the vocabulary is checkable today.

What replaces it is a sequencing fact rather than a technical one, measured 2026-08-13:

- **The shared keys are checkable now and would pass.** `line::` and `appears::` are on 30 of 30 stones. A rule asserting them measures something real and starts green — which, per this project's standing caution, means the fixture has to prove it *can* fail before the green means anything.
- **The pebble vocabulary is closer but still not armable — M5 ran 2026-08-13 and moved the count from 0 of 22 to 17 of 39.** Every migrated pebble carries `tempo::`; every pre-M5 mint still does not. Arming today would condemn the 22 legacy pebbles — smaller than the vacuous explosion this bullet used to describe, but still a rule that opens by firing on more than half its corpus. What remains is the **backfill**: each pre-M5 pebble needs a tempo its owner actually means, which is a judgment call per stone, not a mechanical fill. Arm in the pass that finishes the backfill.
- **`anchor::` is retired and stayed retired.** Nothing in the corpus carries it, so the retirement is complete rather than merely declared.

The order that follows: arm the shared keys with a deliberately-malformed fixture beside a clean twin, and arm the pebble vocabulary in the same pass as M5, never before it.
