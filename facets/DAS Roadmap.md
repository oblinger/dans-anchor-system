---
description: "facet spec for the project sequencing-design doc — milestones, shapes, and numbering"
---

# Roadmap Facet
The Roadmap facet — the project's sequencing-design doc, organized as named milestones with sub-numbering.

| -[[DAS Roadmap]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Roadmap](hook://p/DAS%20Roadmap) |
| --- | --- |
| Related | [[templates/roadmap.md\|roadmap template]],  [[DAS Features]],  [[DAS Completed Roadmap]],  [[DAS Status]],  [[DAS Design Folder]],   |
| Examples | [[FEX Roadmap\|Shape A named-milestone]],  [[HBR Roadmap\|Shape B legacy-numbered]],   |
| Rules | [[R-roadmap]],   |
|  |  |
| **Table of Contents** |  |
| [[#Location]] |  |
| [[#Two roadmap shapes — pick one per project]] |  |
| [[#Numbering grammar]] |  |
| [[#Feature naming when commissioned from a roadmap]] |  |
| [[#Roadmap is future + present only; completed milestones migrate]] |  |
| [[#Status-tracking conventions — three layered axes]] |  |
| #\[x\] M1.5 — Spec Language Module |  |
| [[#Reference-block convention]] |  |
| #\[x\] M1.8 — Spec Evaluation Implementation |  |
| [[#Section separator — `### .`]] |  |
| [[#Deferred items — paired cross-references]] |  |
| #\[~\] M1.11 - Documentation Sync (Deferred - see M3.14) |  |
| [[#Open Questions on the roadmap]] |  |
| [[#Open Questions]] |  |
| [[#Preface zone]] |  |
| [[#Trait applicability]] |  |
| [[#Audit]] |  |
| [[#See also]] |  |
| **[[#BRIEF]]** |  |

The Roadmap facet specifies the `{slug} Roadmap.md` file — the project's **sequencing-design**. It declares what ships in what order, organized as milestones (M1, M2, M3 …) with sub-numbering for finer detail. Open questions at the sequencing/dependency/gating level live as `## Open Questions` H2 on this file per [[DAS ask-format]].

**Relocated to Design 2026-06-10** — previously lived at `{slug} Track/{slug} Roadmap.md` (per F094) and pre-F094 at `{slug} Docs/{slug} Plan/{slug} Roadmap.md`. Moved into Design alongside [[DAS Features]] because milestones ARE design — the plan, not the execution. Existing anchors stay at the old location until next `/design roadmap` touch repositions them (F142).

## Location

`{slug} Design/{slug} Roadmap.md`.

## Two roadmap shapes — pick one per project

A roadmap is structurally one of two shapes. Both are legal; the project picks based on how work is delegated.

### Shape A — Milestone-as-feature-group

Each milestone is a group of feature docs (from [[DAS Features]]) that ship together. The milestone heading carries a checkbox (`## [ ] M-<Name> — <Title>`); its body opens with a one-line milestone summary, then lists the constituent features as `- [ ] [[F<NNN> — …]]` wiki-link bullets, then a bolded `**Acceptance:**` line naming the end-to-end behavior and the e2e test (in `{slug} Testing`) that covers the milestone.

Use when: the project organizes via feature docs and delegates implementation per-feature (the canonical `/feature` workflow). Milestone progress = feature-doc progress. See [[FEX Roadmap]] for a worked Shape A instance.

### Shape B — Milestone-as-task-checklist

Each milestone is a hand-curated checklist of atomic tasks, often multi-level. No per-task feature doc; the roadmap IS the spec. The milestone heading carries a checkbox; its body is a run of H3-checkbox sub-tasks (`### [x] <task>`, including `### [x] Test: …` rows), closed by the `### .` separator before the next milestone.

Use when: the project organizes around evolving research/code where every task is too small to warrant its own feature doc. Milestone progress = checkbox progress. See [[ABIO Roadmap]] for a worked Shape B instance — ~3000 lines across M1-M3 with multi-level numbering (M1.8 → M1.8a → M1.8a.1), Status-line summaries, and deferral cross-refs.

**Mix is not allowed.** Pick one shape per project. (A project can transition between shapes — e.g., starting Shape B and migrating to Shape A as feature docs become useful — but transitions are explicit, not gradual mixing within the same milestone.)

## Numbering grammar

**Top-level milestones are NAMED, not numbered** (per the 2026-06-10 convention codified in [[F144 — Completed Roadmap + named milestones]]). Sub-numbering within a named milestone is numeric.

```
M-<Name>                       ← top-level milestone, named with short acronym/word (M-Auth, M-WAL, M-Core)
M-<Name>.<m>                   ← milestone point (M-Auth.1, M-Auth.2)
M-<Name>.<m>.<k>               ← sub-point (M-Auth.3.5, M-Auth.3.6)
M-<Name>.<m>-<suffix>          ← hyphenated suffix for related grouping (M-Auth.8-tests)
```

**Name conventions:**

- **Short acronym or word** — 3-8 chars typically. Alphanumeric only; no internal hyphens or spaces (the `M-` prefix's hyphen is the only one).
- **Examples that work:** `M-Auth`, `M-WAL`, `M-Onboarding`, `M-Payments`, `M-DataMig`, `M-Core`
- **Avoid:** pure numbers (loses the renumbering-escape benefit), long words (`M-Authentication-Flow` is fatiguing), single letters (cryptic), spaces inside name (kills grep), hyphens inside name (collides with `M-` prefix).

**Why named over numbered (provenance — kept inline pending the 'pull provenance out of rules' refactor):**

Long-running roadmaps accumulate dozens of milestones and inserting a new mid-sequence milestone forces renumbering of everything after it. ABIO Roadmap hit this pain (3000+ lines, M1.0 through M3.7+). Named milestones don't have ordering at the top level — `M-Auth` and `M-WAL` exist independently; you can add `M-Notifications` anywhere without renumbering. The name carries semantic meaning a number doesn't; `grep "M-Auth"` is meaningful (finds all the auth work), `grep "M3"` finds noise.

**Why sub-numbering stays numeric:** within a milestone, sub-points DO have meaningful local ordering ("first I do M-Auth.1, then M-Auth.2 …"). Numbers are right for that.

**Why sub-numbering is renumberable but top-level names aren't:**

Sub-items within a milestone are easy to renumber on insertion because they're scoped — grep `M-Auth.` finds all of them and you mechanically renumber. Top-level milestones in a long roadmap aren't — they touch every cross-reference everywhere, plus features whose titles encode the old position (see § Feature naming below).

### Names are identity; order is document position (never a stored number)

A milestone's **identity is its name** (`M-Scaffolding`) — never an ordinal. Its **order is its position in this file**: milestones are listed top-to-bottom in execution order, so the sequence is inherent in the document. There is deliberately **no stored top-level milestone number**. If a display ordinal is wanted, it is **computed from position** ("3 · Scaffolding") by the reader or tooling — never written into the heading and never referenced by anything.

This is what makes insertion cheap: dropping a new milestone between two others shifts everyone's *position* automatically, with **nothing to renumber** and **no reference to update** — because every reference (sub-entries, backlog `R` tasks, done-logs, cross-links) is keyed on the **name**, not a number. Only **renaming** a milestone touches references, and renames are rare. A reorder/reflow script, if ever built, is pure convenience for moving H1 blocks around — never required for correctness, because identity is name-based.

**Names must be unique within a roadmap** — the scheme rests on the name being an unambiguous key (enforced by R-roadmap-12).

*(Provenance: designed 2026-07-05. The alternative — a stored ordinal on each milestone — was rejected: it forces a full-roadmap renumber on every insert and leaves external references stale. Making the ordinal a computed *position* rather than stored data eliminates both problems: nothing to renumber, nothing to drift.)*

### Referencing a roadmap entry as backlog work (`R` tasks)

When a roadmap entry is pulled onto a backlog as work-to-do, its backlog handle is **`R` + the entry's name-path — word-only, no number**:

- `R-Scaffolding.5.2` — a **leaf** sub-entry ("do this item", the usual case).
- `R-Scaffolding` — a **non-leaf** entry: a commitment to do the *whole subtree* under it.

The reference is **flat** (it names one entry) and **name-keyed**, so an `R` task parked on a backlog survives any reordering of the roadmap — only a rename would touch it. `R` is the roadmap counterpart of the backlog `T` task; both are executable work-items (see [[DAS Backlog]] § Numbering for the full `F`/`T`/`M`/`R` model).

### Legacy numeric form (for migration only)

Some existing roadmaps use `M1`, `M2`, `M1.8a` per the pre-2026-06-10 convention (e.g., ABIO). The legacy grammar:

```
M<n>                  ← top-level milestone (M1, M2, M3 …)
M<n>.<m>              ← milestone point (M1.0, M1.1, … M1.14)
M<n>.<m><letter>      ← sibling point added later (M1.6b, M1.8a, M1.8b)
M<n>.<m><letter>.<k>  ← sub-point within a sub-milestone (M2.1a.1, M2.1a.2)
M<n>.<m>-<suffix>     ← hyphenated suffix for related grouping (M1.8a-tests)
```

Existing legacy roadmaps don't need to migrate immediately; new roadmaps use the named-milestone form.

**Letter suffix** marks a sibling added after the initial sequence — `M1.6b` after `M1.6` was already written. New parallel work that doesn't deserve a fresh point-number.

**Sub-letter (M1.8a etc.)** marks substantial sub-milestones within a single point. Each `M1.8a` / `M1.8b` is itself a substantial chunk of work, typically with its own Status line and inline checkboxes.

**Numbers are monotonic-forever within a level.** Don't recycle M1.4 if it was deprecated; mark it `[~]` deferred or `~~M1.4~~` struck through, and let new work take M1.15.

## Feature naming when commissioned from a roadmap

When a roadmap milestone sub-item gets commissioned as its own feature doc (i.e., earns a `## Roadmap`-section-worthy chunk of work), the feature's filename and title encode the milestone position. This gives bi-directional traceability without renames.

**Title format:**

```
F<NNN> — M-<Name>.<position>: <Title from Roadmap entry>
```

**Worked example:** Roadmap entry says:

```markdown
### [ ] M-CLI — Command-Line Interface
- [ ] M-CLI.3.5 — Implement CLI Core Statements
```

When commissioned, the feature gets the next F-number (say F118) and the title:

```
F118 — M-CLI.3.5: Implement CLI Core Statements
```

The roadmap entry stays as `M-CLI.3.5 — Implement CLI Core Statements`. A small `[F118]` marker is added after the bullet (or `[[F118 — M-CLI.3.5: Implement CLI Core Statements|F118]]` as a wiki-link) so the roadmap reader can click through to the feature doc.

**Bi-directional discoverability:**

- **Roadmap → feature:** click the `[F118]` marker (or wiki-link).
- **Feature → roadmap:** look at the feature title — `M-CLI.3.5` tells you exactly which milestone position it implements. Grep `M-CLI` to find the milestone heading.

**Why this format (provenance — discussed in [[F144 — Completed Roadmap + named milestones]] Q1):**

User initially proposed M-numbers replacing F-numbers when promoted. Rejected because F-numbers are monotonic-forever, never renamed — renaming on promotion would break commit messages, e2e test exercises lines, and every cross-reference. Agent counter-proposed M-names for groupings, F-numbers for features. User refined: titles encode M-position so the feature doc itself shows its roadmap origin. Both agreed: F-numbers don't claim to encode order; they're unique handles. The title's M-prefix carries the position information.

**For features NOT commissioned from a roadmap** (the common case — features filed straight to backlog): no M-prefix. Title is just `F<NNN> — <Title>` (e.g., `F042 — Add retry budget cap`). The absence of an M-prefix in a feature title is itself a signal: this feature was filed independently, not as part of a milestone commitment.

**For sub-items within a milestone that don't earn their own feature doc:** the `M-<Name>.<n>` identifier exists only in the roadmap. No F-number, no feature doc. These are inline checklist items.

**Renumbering within a milestone:** legal but adds cost when features have already been commissioned. Grep by `M-<Name>.<old>` finds the feature doc; rename the file (Obsidian propagates wiki-links). Commit history references stay frozen with the old position — accept this as the cost of renumbering. Renumbering should be rare; usually new sub-items append at the end.

## Roadmap is future + present only; completed milestones migrate

The roadmap is **forward-looking** — it shows what's planned and what's in progress. Completed milestones do NOT accumulate in the roadmap doc; they migrate to a companion **Completed Roadmap** doc at `{slug} Design/{slug} Completed Roadmap.md` (per [[DAS Completed Roadmap]]).

**Why future-only (provenance — discussed in [[F144 — Completed Roadmap + named milestones]]):**

Long-running roadmaps that retain completed work become hard to navigate — "where are we now?" requires scrolling past completed milestones to find the current one. ABIO Roadmap demonstrates the pain (3000+ lines mostly completed). User explicitly framed this: "you can always jump to the roadmap document, and kind of see what's up and coming, what's happening now, is right inside the roadmap."

**Migration unit is the whole milestone.** When a milestone reaches "all sub-items checked, parent milestone `[x]`," the entire milestone (heading + sub-items + Status line + reference block) moves as a unit from Roadmap to Completed Roadmap. Individual completed sub-items inside a still-in-flight milestone stay in the roadmap (the milestone hasn't fully completed yet).

**Migration is currently manual** (F145 will ship the automation: `state roadmap migrate M-<Name>`).

**Within an in-flight milestone:** sub-items CAN be `[x]` checked while parent milestone is still `[ ]`. This shows partial progress. The milestone's `**Status:**` line tracks the overall state ("Core complete — 3/5 sub-items done").

## Status-tracking conventions — three layered axes

Roadmap status uses three complementary mechanisms simultaneously. None alone is enough; together they let a reader graze at any depth.

### Axis 1 — Checkbox in heading

Every milestone-level heading carries a checkbox in its title:

- `## [x] M1.0 — Done`
- `## [ ] M2.3 — Not started or in progress`
- `## [~] M1.11 — Deferred (see M3.14)`

H1 (top milestones), H2 (points), H3 (sub-points) all carry checkboxes. H4 typically doesn't (it's labeling a section within a sub-point).

**Vocabulary:**

| Checkbox | Meaning |
|---|---|
| `[x]` | Complete |
| `[ ]` | Not started or in progress (disambiguate via Status line) |
| `[~]` | Deferred — must include `(Deferred - see M<n>.<m>)` reference + matching revisit milestone |

### Axis 2 — `**Status**:` line under each milestone

A free-form summary line directly after the milestone heading (and after any reference block):

```markdown
## [x] M1.5 — Spec Language Module

Implement spec_lang module with YAML tags, decorators, Bio class.

**Status**: Complete — 83 tests passing, 3 skipped.
```

**Status vocabulary** (extracted from observed practice):

| Status | Meaning |
|---|---|
| `Complete — <summary>` | Milestone fully done. Summary may carry quantitative anchor (PR refs, test counts). |
| `Core complete — <summary>` | Primary work done; minor items pending or deferred. |
| `In progress — <what's done, what's not>` | Active work; partial progress. |
| `Not started` | Default; usually omitted (absence implies). |
| `Deferred — see M<n>.<m>` | Postponed to a future milestone; paired with revisit ref. |
| `Blocked — <reason>` | External dependency; usually with `[[wiki-link]]` to blocker. |

**Quantitative anchors** are encouraged in the summary — *"339 tests passing"*, *"PR #58 merged"*, *"15 tests passing, 2 skipped"*. These give the reader a concrete handle on what "Complete" actually means.

### Axis 3 — Per-item checkboxes within milestone body

Atomic work items inside a milestone use inline markdown checkboxes (or H3-level checkboxes for substantial sub-tasks):

```markdown
- [x] Implement priority queue
- [x] Implement worker thread pool
- [ ] Retry logic with exponential backoff
```

Or, for substantial sub-tasks:

```markdown
### [x] M1.8a — Write Comprehensive Tests First
### [x] M1.8b — Placeholder Classes
### [ ] M1.8c — Hydrate Implementation
```

Inline-list checkboxes and H3 checkboxes are equivalent in semantics — H3 for things that earn their own heading, inline for everything else.

## Reference-block convention

Many milestones carry a block of `**<Label>**:` lines right after the Status line:

```markdown
## [x] M1.8 — Spec Evaluation Implementation

**Status**: Complete — All subtasks done.

**Reference Docs**: [[Spec Evaluation]], [[Spec Language]]
**Tests**: tests/unit/test_spec_eval.py (149 tests)
**Discussion**: [[ABIO Notes#2026-01-14 M1.14 Agent Interface]]

**Design Summary**:
- `!_` tag → preserve expression unchanged
- `!ev` tag → evaluate Python at instantiation
```

Reference-block labels are free-form (`Reference`, `Tests`, `Discussion`, `Design Summary`, `Acceptance` …). Convention: each label is a bolded run-in (`**Label**: …`), one per line, in the block immediately after Status.

## Section separator — `### .`

A literal `### .` H3 with just a dot serves as a visual closer between milestones. Lets a reader scrolling through visually identify where one milestone ends and the next begins, without the closer competing with content for attention.

Use after the last item of each milestone (after the last `- [x]` bullet or `### [x] M1.8j — Integration` sub-point), before the next `## ` H2 starts.

## Deferred items — paired cross-references

When an item or milestone is deferred, both ends carry cross-references:

**Original entry** (marked deferred):

```markdown
## [~] M1.11 - Documentation Sync (Deferred - see M3.14)

**Deferred**: Documentation tasks postponed to focus on feature development. See M3.14 for revisit.
```

**Revisit entry** (in the target milestone):

```markdown
### [ ] M3.14 - Revisit: M1.11 Documentation Sync

Address the documentation backlog deferred from M1.11.
```

Both directions linked so neither end is lost. A validation pass (per CAB Validation below) checks that every `[~]` has a matching revisit entry and vice versa.

## Open Questions on the roadmap

Roadmap-level open questions (sequencing, dependency, gating) — questions whose answer changes the milestone shape rather than a single feature doc — live as `## Open Questions` H2 directly above the file's H1, per [[DAS ask-format]]:

```markdown
# {slug} Roadmap

## Open Questions

- **Q1 — Should M2 ship before or after the Q4 freeze?** Context: M2 includes risky data-layer migration; shipping it before freeze means longer bake time, but the M1 → M2 dependency means delay shifts M3 too. **Recommendation:** Lean ship-after — bake risk is real. Block ID: ^q1
```

Questions tied to specific features live on the feature doc, not here. Use `/ask --doc {slug} Roadmap.md "<question>"` to file roadmap-level Qs.

## Preface zone

Per [[DAS progressive-disclosure]]:

- **Dispatch table** — Required.
- **TLDR** — Optional. Roadmaps often benefit from a 3-5 bullet TLDR naming the milestone count + current state ("M1 done, M2 in progress, M3+ planned").
- **Figure** — Optional. A timeline diagram or dependency graph can help on roadmaps with cross-milestone dependencies; skip for linear roadmaps.

## Trait applicability

Any anchor with a `{slug} Design/` folder per [[DAS Design Folder]] that's planning more than 1-2 milestones of work. Single-milestone projects don't need the roadmap.

## Audit

`/audit roadmap` (future) would flag the rules captured in `R-roadmap` below — checkbox-in-heading shape, Status-line presence on each milestone, deferral cross-ref pairs, multi-level numbering compliance, mixed-shape violations.

## See also

- [[DAS Design Folder]] — parent facet (Roadmap is a Recommended child of the Design folder)
- [[DAS Features]] — feature docs that Shape A roadmaps group into milestones
- [[DAS Stories]] — user stories that milestones implement (cited from milestone Acceptance lines)
- [[DAS Status]] — `{slug} Status.md` carries the design-phase tier for `roadmap::` (separate from per-milestone progress)
- [[DAS ask-format]] — open-questions discipline
- [[design-roadmap]] — authoring sub-skill for `/design roadmap`
- [[ABIO Roadmap]] — worked example of Shape B (task-checklist; multi-level numbering; deferral cross-refs)
- [[FEX Roadmap]] — worked example (currently Shape A skeleton; expansion landing alongside CAE refresh)

# BRIEF

*(Maintainer note — what belongs in this spec and what doesn't.)*

- **Inclusion test + boundary:** a rule belongs only if it constrains the shape / numbering / status / deferral convention of *every* `{slug} Roadmap.md`. Roadmap *content* lives in per-anchor files; *how* features ship is [[DAS Features]]; the design-phase tier is [[DAS Status]]'s `roadmap::`.
- **Don't collapse the two shapes** (A milestone-as-feature-group / B milestone-as-task-checklist) "for simplicity" — both are load-bearing; mixing is forbidden, transitioning allowed.
- **`R-roadmap` is co-located** (per [[F133]]); don't split it out. Rule numbering is monotonic-forever — **R-roadmap-09/-10/-11/-12 are out-of-sequence by intent** (authoring order, not narrative). R-roadmap-12 (unique milestone name) is the invariant the name-is-identity / computed-position scheme depends on — added 2026-07-05.
- **Don't delete the legacy numeric section** — named-milestone `M-<Name>` is the convention ([[F144]]); legacy `M1`/`M2` is migration-only and stays documented.
- **Cross-refs to keep live on edit:** [[DAS Completed Roadmap]], [[DAS Features]], [[DAS Status]], [[design-roadmap]], [[DAS ask-format]].
