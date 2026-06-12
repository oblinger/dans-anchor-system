# CAB Roadmap
description:: facet spec (TBD — user authoring)

The Roadmap facet specifies the `{NAME} Roadmap.md` file — the project's **sequencing-design**. It declares what ships in what order, organized as milestones (M1, M2, M3 …) with sub-numbering for finer detail. Open questions at the sequencing/dependency/gating level live as `## Open Questions` H2 on this file per [[ask-format]].

**Relocated to Design 2026-06-10** — previously lived at `{NAME} Track/{NAME} Roadmap.md` (per F094) and pre-F094 at `{NAME} Docs/{NAME} Plan/{NAME} Roadmap.md`. Moved into Design alongside [[CAB Features]] because milestones ARE design — the plan, not the execution. Existing anchors stay at the old location until next `/design roadmap` touch repositions them (F142).

## Location

`{NAME} Design/{NAME} Roadmap.md`.

## Two roadmap shapes — pick one per project

A roadmap is structurally one of two shapes. Both are legal; the project picks based on how work is delegated.

### Shape A — Milestone-as-feature-group

Each milestone is a group of feature docs (from [[CAB Features]]) that ship together. Milestone body lists the F-numbered features as wiki-links, plus an acceptance summary.

```markdown
## [ ] M1 — Core Scheduler

Initial scheduler + persistence. Ships when all three features land.

- [ ] [[F001 — Priority queue implementation]]
- [ ] [[F002 — Worker thread pool]]
- [ ] [[F003 — Retry logic with exponential backoff]]

**Acceptance:** `cae schedule` and `cae status` work end-to-end with `priority` + `at` flags; one e2e test in [[CAE Testing]] covers the milestone.
```

Use when: the project organizes via feature docs and delegates implementation per-feature (the canonical `/feature` workflow). Milestone progress = feature-doc progress.

### Shape B — Milestone-as-task-checklist

Each milestone is a hand-curated checklist of atomic tasks, often multi-level. No per-task feature doc; the roadmap IS the spec.

```markdown
## [x] M1.0 — Environment Setup

### [x] Create repo structure
### [x] Initialize uv environment
### [x] Configure pytest for tests/
### [x] Test: `just test` passes with empty suite

### .

## [x] M1.1 — Infrastructure Operators

Top-level operations for the system. See [[Architecture]] for details.

### [x] Implement do(name) — resolve dotted names
### [x] Implement create(spec) — instantiate from prototype
### [x] Test: do("fixtures.X") resolves
```

Use when: the project organizes around evolving research/code where every task is too small to warrant its own feature doc. Milestone progress = checkbox progress.

**Worked example of Shape B:** [[ABIO Roadmap]] — ~3000 lines across M1-M3 with multi-level numbering (M1.8 → M1.8a → M1.8a.1), Status-line summaries, deferral cross-refs.

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

The roadmap is **forward-looking** — it shows what's planned and what's in progress. Completed milestones do NOT accumulate in the roadmap doc; they migrate to a companion **Completed Roadmap** doc at `{NAME} Design/{NAME} Completed Roadmap.md` (per [[CAB Completed Roadmap]]).

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

Roadmap-level open questions (sequencing, dependency, gating) — questions whose answer changes the milestone shape rather than a single feature doc — live as `## Open Questions` H2 directly below the file's H1, per [[ask-format]]:

```markdown
# {NAME} Roadmap

## Open Questions

- **Q1 — Should M2 ship before or after the Q4 freeze?** Context: M2 includes risky data-layer migration; shipping it before freeze means longer bake time, but the M1 → M2 dependency means delay shifts M3 too. **Recommendation:** Lean ship-after — bake risk is real. Block ID: ^q1
```

Questions tied to specific features live on the feature doc, not here. Use `/ask --doc {NAME} Roadmap.md "<question>"` to file roadmap-level Qs.

## Preface zone

Per [[progressive-disclosure]]:

- **Dispatch table** — Required.
- **TLDR** — Optional. Roadmaps often benefit from a 3-5 bullet TLDR naming the milestone count + current state ("M1 done, M2 in progress, M3+ planned").
- **Figure** — Optional. A timeline diagram or dependency graph can help on roadmaps with cross-milestone dependencies; skip for linear roadmaps.

## Trait applicability

Any anchor with a `{NAME} Design/` folder per [[CAB Design]] that's planning more than 1-2 milestones of work. Single-milestone projects don't need the roadmap.

## Audit

`/audit roadmap` (future) would flag the rules captured in `R-roadmap` below — checkbox-in-heading shape, Status-line presence on each milestone, deferral cross-ref pairs, multi-level numbering compliance, mixed-shape violations.

## See also

- [[CAB Design]] — parent facet (Roadmap is a Recommended child of the Design folder)
- [[CAB Features]] — feature docs that Shape A roadmaps group into milestones
- [[CAB Stories]] — user stories that milestones implement (cited from milestone Acceptance lines)
- [[CAB Status]] — `{NAME} Status.md` carries the design-phase tier for `roadmap::` (separate from per-milestone progress)
- [[ask-format]] — open-questions discipline
- [[design-roadmap]] — authoring sub-skill for `/design roadmap`
- [[ABIO Roadmap]] — worked example of Shape B (task-checklist; multi-level numbering; deferral cross-refs)
- [[CAE Roadmap]] — worked example (currently Shape A skeleton; expansion landing alongside CAE refresh)


# RULESET R-roadmap
include::
description:: Structural rules for the {NAME} Roadmap.md facet — milestone numbering, checkbox states, Status-line presence, deferral cross-ref, shape consistency.

Embedded rule set for the Roadmap facet, co-located with the facet spec above per [[F133 — Rule sets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella.

### RULE R-roadmap-01 — Location is `{NAME} Design/{NAME} Roadmap.md` (checked)

The roadmap lives at `{NAME} Design/{NAME} Roadmap.md`. Not under Track (legacy), not at anchor root.

**Check pattern:** `ls "{anchor}/{NAME} Design/{NAME} Roadmap.md"` exists; no `{NAME} Track/{NAME} Roadmap.md` lingers alongside.

**Why:** Roadmap is sequencing-design; lives with the design facets. The 2026-06-10 restructure moved it from Track.

### RULE R-roadmap-02 — Body-only, no YAML frontmatter (checked)

The first non-blank line is `# {NAME} Roadmap` (H1). No `---` YAML block precedes.

**Check pattern:** first non-blank line starts with `# `; does not start with `---`.

**Why:** matches the vault-wide body-only convention. Frontmatter is invisible in Obsidian read view and drifts silently.

### RULE R-roadmap-03 — Every milestone heading carries a checkbox in its title (checked)

Every H1 marked as a top milestone, H2 marked as a milestone point, and H3 marked as a sub-point carries `[x]`, `[ ]`, or `[~]` in the heading text immediately after the H-marker.

**Check pattern:** for headings matching `^# Milestone \d+` (H1), `^## M\d+\.\d+` (H2), `^### M\d+\.\d+\w?` (H3), assert the heading text starts with `[x] `, `[ ] `, or `[~] `.

**Why:** the checkbox is the grazer's primary read of milestone state. Missing checkbox = milestone state is invisible to a quick scan.

### RULE R-roadmap-04 — Milestones with checkbox `[x]` or `[ ]` carry a `**Status**:` line (sampled)

Within ~5 lines of the milestone heading, a `**Status**:` line summarizes the state — *"Complete — N tests passing"* / *"Core complete — …"* / *"In progress — …"*. Required for `[x]` and `[~]`; recommended for `[ ]` once work begins.

**Check pattern:** for each `[x]` or `[~]` milestone H1/H2, scan the next 10 lines for `^\*\*Status\*\*:`; flag if absent.

**Why:** the checkbox gives binary state; the Status line gives the narrative + quantitative anchor (test counts, PR refs) that makes "Complete" mean something specific.

### RULE R-roadmap-05 — Deferred items (`[~]`) have matching revisit cross-references (checked)

Every `[~]` milestone or item includes `(Deferred - see M<n>.<m>)` in its heading or first body line. The referenced milestone in turn contains a `Revisit: M<source>` entry.

**Check pattern:** for each `[~]` milestone, extract the cited revisit target; verify the target exists and contains a Revisit entry pointing back at the source.

**Why:** one-way deferral pointers rot — the deferred item disappears from view because the revisit milestone doesn't surface it. Paired cross-refs keep both ends discoverable.

### RULE R-roadmap-06 — Shape is consistent across the file (stated)

Within a single roadmap file, all milestones use the same shape (Shape A — milestone-as-feature-group OR Shape B — milestone-as-task-checklist). Don't mix `[[F<NNN>]]` wiki-link bullets in one milestone with raw checkbox tasks in the next.

**Check pattern:** scan the body of each milestone; classify as Shape A (predominantly `[[F\d+`-prefixed bullets) or Shape B (predominantly raw checkbox tasks); assert all classifications match.

**Why:** mixed shapes confuse the reader about how to interpret milestone progress (is it "all features done" or "all tasks checked"?). Pick one shape per project; transitions between shapes are explicit (a marker note), not gradual mixing.

### RULE R-roadmap-07 — Milestone numbers are monotonic-forever (stated)

Milestone numbers are never recycled within a level. A deprecated `M1.4` stays at M1.4 (struck through or `[~]` deferred); new work takes the next unused number (`M1.15`, `M1.4b`, etc.).

**Check pattern:** git history — flag instances where a milestone-number heading was deleted and the same number reappears later with different content.

**Why:** stable identifiers across cross-references (e.g., "see M1.11", "Deferred - see M3.14") and external citations (commit messages, feature docs). Recycling breaks every back-reference silently.

### RULE R-roadmap-09 — Milestones use `M-<Name>` form, not pure numbers (checked)

Top-level milestones are named with a short acronym or word: `M-Auth`, `M-WAL`, `M-Core`. Pure-number forms (`M1`, `M2`) are legacy-only — accepted in existing roadmaps but new milestones use named form.

**Check pattern:** for each H2/H3 milestone heading, assert the milestone identifier matches `^M-[A-Za-z][A-Za-z0-9]{2,}(\.[0-9]+)*(-\w+)?$` (named form). Pure-numbered forms accepted only if the roadmap file carries a `<!-- legacy-numbered-milestones -->` marker comment.

**Why (provenance):** numbering long-running roadmaps creates renumbering nightmare on insertion. Named milestones don't have top-level ordering; you can add `M-Notifications` anywhere without touching anything else. Names are grep-able semantic anchors. Discussed and agreed in [[F144 — Completed Roadmap + named milestones]].

### RULE R-roadmap-10 — Feature title encodes M-position when commissioned from roadmap (checked)

When a feature is commissioned from a roadmap milestone sub-item, the feature doc's filename and title use:

```
F<NNN> — M-<Name>.<position>: <Title from Roadmap entry>
```

Example: `F118 — M-CLI.3.5: Implement CLI Core Statements.md`. The roadmap entry gets a `[F118]` marker (or full wiki-link) added after the bullet to point at the feature doc.

**Check pattern:** for each feature doc filename matching `F\d+ — M-`, assert the format matches `F\d+ — M-[A-Za-z][A-Za-z0-9]+(\.\d+)*: .+\.md`. For each roadmap sub-item that has a `[F\d+]` marker, assert a matching feature doc exists.

**Why (provenance):** F-numbers stay universal (monotonic-forever, never renamed). Encoding M-position in the title gives bi-directional discoverability without rename-cost. A reader on the feature doc sees `M-CLI.3.5` in the title and knows the roadmap origin; a reader on the roadmap clicks `[F118]` to reach the feature doc. Discussed and agreed in [[F144 — Completed Roadmap + named milestones]] Q1.

### RULE R-roadmap-11 — Roadmap is future + present only; completed milestones migrate to Completed Roadmap (stated)

The roadmap holds forward-looking work. Whole milestones — when `[x]` complete — migrate as units to `{NAME} Design/{NAME} Completed Roadmap.md` (per [[CAB Completed Roadmap]]).

**Check pattern:** roadmap should have at most one or two `[x]` top-level milestones at any time (they're awaiting migration). Stale `[x]` milestones accumulating in the roadmap = drift; flag for migration.

**Why (provenance):** long roadmaps mostly composed of completed work become hard to navigate. "Where are we now?" should be answerable by glancing at the top of the roadmap. ABIO Roadmap demonstrates the pain at scale. F145 will ship automation; until then, migration is manual.

### RULE R-roadmap-08 — Section separator `### .` is used between milestones (stated)

After the last body item of each milestone, before the next `## ` H2, a `### .` (H3 with literal dot) serves as a visual closer.

**Check pattern:** for each H2 milestone, check that the preceding H2's body ends with a `### .` line within ~3 lines of the next H2.

**Why:** scrolling readers benefit from the visual closer to identify milestone boundaries without parsing content. Optional for very short milestones (one or two items) but encouraged.

# BRIEF

- **This is the facet spec for `{NAME} Roadmap.md`** — it defines structure, numbering, status-tracking, and shape rules for the project sequencing-design doc. Edits here change the rule, not any one project's roadmap.
- **NOT for** roadmap *content* (those live in per-anchor `{NAME} Roadmap.md` files), NOT for execution-time rules about *how* features ship (that's [[CAB Features]]), NOT for the design-phase tier marker (that's [[CAB Status]]'s `roadmap::` field).
- **Inclusion test:** a rule belongs here only if it constrains the shape, numbering, status convention, deferral pattern, or shape consistency of every `{NAME} Roadmap.md` across anchors. Project-specific milestone naming or content never belongs here.
- **Two shapes (A — milestone-as-feature-group; B — milestone-as-task-checklist) are load-bearing** — keep both documented; mixing within a project is forbidden but transitioning is allowed. Don't collapse into one shape "for simplicity."
- **R-roadmap RULESET is co-located** in this same file per [[F133]] (embedded rule set adopted via the `R-facet` umbrella). Don't split it into a separate file; keep rule numbering monotonic-forever (R-roadmap-09, -10, -11 are out-of-sequence by intent — order reflects authoring history, not narrative).
- **Named-milestone form (`M-<Name>`) is the new convention** per [[F144]]; legacy numeric (`M1`, `M2`) is migration-only. When updating examples or rules, prefer the named form; keep the legacy section as a documented fallback, don't delete it.
- **Cross-refs to maintain on edit:** [[CAB Completed Roadmap]] (the migration target), [[CAB Features]] (Shape A milestone bullets are F-numbered wiki-links), [[CAB Status]] (`roadmap::` field), [[design-roadmap]] (authoring skill), [[ask-format]] (Open Questions convention).
