# CAB PRD

Facet spec for `{NAME} PRD.md` — the first doc in an anchor's Design folder, defining what the product does (goals, non-goals, user stories) for every downstream design phase to consume.

description:: PRD facet — `{NAME} PRD.md` defines what the product does; goals, non-goals, user stories. First doc in the Design folder; consumed by every downstream design phase.

The PRD (`{NAME} PRD.md`) is the **what** of the product — what it does, who it serves, what's in and out of scope, and the user stories that downstream work realizes. It is the first document written during `/design`, and every downstream phase (UX, Architecture, Testing, Roadmap, Features) reads it as authoritative input.

PRDs are deliberately not the place for technical decisions, principles, rules, or implementation detail — those live in [[CAB Decisions]], [[CAB Rules]], [[CAB Architecture]], and per-module docs respectively. The PRD's job is to define the contract that lets everything downstream argue from the same shared understanding of what the product is.

## Location

`{NAME} Design/{NAME} PRD.md` (single-file form) **or** `{NAME} Design/{NAME} PRD/{NAME} PRD.md` (folder form, when user stories migrate to the [[CAB Stories|Stories sub-facet]]).

**File location moved 2026-06-01 per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]]** — legacy path `{NAME} Docs/{NAME} Plan/{NAME} PRD.md` is superseded. Existing legacy locations migrate during normal anchor work.

## Two forms — single-file (default) and folder (when stories extract)

### Single-file form (default)

```
{NAME} Design/{NAME} PRD.md
```

User stories live inline under `## User Stories` as bullets. Right for most PRDs.

### Folder form (when stories grow to need their own pages)

```
{NAME} Design/{NAME} PRD/
├── {NAME} PRD.md           ← this file, anchor file (matches folder name)
├── {NAME} Stories.md       ← stories dispatch index
├── US-<RID>-1 — <Title>.md ← individual story files
└── ...
```

Per [[CAB Stories]]. The PRD's `## User Stories` section then links to `[[{NAME} Stories]]` instead of carrying inline bullets. Migration is one-way; mixing inline and extracted stories in the same PRD is forbidden.

## Standard section order

| # | Section | Purpose |
|---|---|---|
| 1 | Top of doc | Body-only — no YAML frontmatter. `# {NAME} PRD` H1 + `description::` inline + dispatch table per [[progressive-disclosure]]. |
| 2 | `## Overview` | One to two paragraphs — what the product *is*, who it's for, why it needs to exist. Reader leaves knowing the shape of the thing. |
| 3 | `## Design Workflow` | Table listing the design phases downstream of this PRD with wiki-links: PRD → Architecture → Testing → Decisions → Track (Roadmap + Features). The sequence may be revisited iteratively as questions surface. |
| 4 | `## Goals` | Concrete, verifiable outcomes — what the product will accomplish. Bulleted; outcome-shaped (not feature-shaped). |
| 5 | `## Non-Goals` | What the product explicitly will NOT do. Each non-goal is one of: (a) deferred to a future version, (b) out of scope by design, (c) constraint from the environment. Keeps scope conversation honest. |
| 6 | `## User Stories` | Either inline bullets (`US-<RID>-<N>` per [[CAB Stories]]) or a wiki-link to `[[{NAME} Stories]]` if folder form. Each story is "As a `<role>`, I want `<capability>` so that `<reason>`." |
| 7 | `## Open Questions` (optional) | Pending decisions surfaced via [[ask-format]]. Lives below the H1 only while pending Qs exist; deletes entirely once all resolve. |
| 8 | `## Resolved` (optional) | Bottom-of-doc archive of resolved questions and decisions, H3 per resolution. Populated as questions resolve; never deleted. |
| 9 | `## See also` (optional) | Links to peer Design facets (Architecture, Testing, Decisions). |

The spine is `Overview → Design Workflow → Goals → Non-Goals → User Stories`. Sections 7-9 appear as needed.

**Working example:** [[CAE PRD]] — single-file form; three inline stories.

## Preface zone requirements

Per [[progressive-disclosure]] § Per-facet preface requirements:

- **Dispatch table** — **Required**.
- **TLDR** — **Explicitly NOT required**. PRDs are too heterogeneous to compress meaningfully into 3-8 bullets without filler; forcing one degrades the doc. The `## Overview` section serves the grazer-altitude need.
- **Figure** — Optional. A product-shape mockup or context diagram can help on visual products; skip for CLI / library / pure-data projects.

## User stories — naming and lifecycle

- **Identifier:** `US-<RID>-<N>` per [[CAB Stories]] § Naming convention. Monotonic-forever within the anchor; never recycled.
- **Inline shape:** H3 heading `### US-<RID>-<N>: <Title>` followed by the canonical "As a `<role>`, I want `<goal>` so that `<reason>`" sentence on the next line.
- **When stories grow:** migrate to [[CAB Stories]] folder form. The PRD's `## User Stories` section then reads "See [[{NAME} Stories]] for the story index" + (optionally) a wiki-list of the top-level stories.

### Dispatch-row pointer to stories — required in both forms

The PRD's top-of-doc dispatch table carries a row pointing at stories. The link target depends on the form, but the **display alias is always `{NAME} Stories`** (the proper anchor-prefixed name, matching the convention used by sibling rows like `[[{NAME} Architecture]]`, `[[{NAME} Testing]]`):

- **Single-file PRD (inline stories):** `[[{NAME} PRD#User Stories\|{NAME} Stories]]` — section-deep wiki-link into this same doc's `## User Stories` H2, displayed as `{NAME} Stories`. The description names the story count: *"three user stories (inline-bullet form per [[CAB Stories]]; US-{RID}-1..N)"*.
- **Folder-form PRD (extracted stories):** `[[{NAME} Stories]]` — wiki-link to the sibling dispatch index; display defaults to the page name (`{NAME} Stories`). The description names the count: *"N user stories — index at [[{NAME} Stories]]"*.

The row is required in both forms so a reader landing on the PRD has a one-click jump to "what does this product DO for users" without scrolling. The proper-name display keeps the row consistent with its peers in the dispatch table. Worked example: [[CAE PRD]] § dispatch table.

## Open questions — handled by `/ask`

PRD discussions surface questions throughout. The PRD does NOT carry a separate `{NAME} Open Questions.md` file (legacy pattern, deprecated). Instead:

- **Active questions** live as `## Open Questions` H2 directly below the H1, per [[ask-format]].
- **Resolved questions** move to `## Resolved` at the bottom of the doc when answered. Never deleted.
- **The `/ask --doc` workflow** is the way to add or resolve questions on a PRD; it handles the formatting, the lifecycle transitions, and the Q.md update.

## Status tracking

Design-phase completeness for the PRD is tracked in `{NAME} Track/{NAME} Status.md` per [[CAB Status]], on the `prd::` line. The PRD file itself does NOT carry a `status::` dataview field — the centralized Status facet is the single source of truth. Legacy per-doc `status::` is acceptable as a fallback when the Status file doesn't exist yet.

## Trait applicability

Any anchor that has a `{NAME} Design/` folder per [[CAB Design]]. Initially supports anchors with code-shaped artifacts; broader applicability (Paper / Topic / Simple traits) covered as those traits land.

## Audit

`/audit prd` (future) would flag the rules captured in `R-prd` below — body-only shape, required-section presence, US-<RID>-<N> story numbering, no legacy Open Questions file, etc.

## See also

- [[CAB Stories]] — sub-facet activated when user stories grow beyond inline-bullet form
- [[CAB Architecture]] — peer Design facet (system-architecture story)
- [[CAB Testing]] — peer Design facet (testing strategy + proposed-tests overview)
- [[CAB Decisions]] — peer Design facet (load-bearing decisions citing rules)
- [[CAB Status]] — `{NAME} Status.md` carries the PRD's design-phase tier
- [[ask-format]] — open-questions formatting discipline
- [[progressive-disclosure]] — preface-zone requirements
- [[design-prd]] — authoring sub-skill for `/design prd`
- [[CAE PRD]] — worked example (single-file form, three inline stories)


# RULESET R-prd
include::
description:: Structural rules for the {NAME} PRD facet — location, body-only shape, required sections, user-story numbering, modern Open-Questions handling.

Embedded rule set for the PRD facet, co-located with the facet spec above per [[F133 — Rule sets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella.

### RULE R-prd-01 — Location is `{NAME} Design/{NAME} PRD.md` or folder form (checked)

The PRD lives at `{NAME} Design/{NAME} PRD.md` (single-file form) or `{NAME} Design/{NAME} PRD/{NAME} PRD.md` (folder form). Not under `{NAME} Docs/`, not under `{NAME} Plan/`, not at the anchor root.

**Check pattern:** path matches one of the two canonical locations.

**Why:** F094 moved Design docs out of the legacy `{NAME} Plan/` folder; surfacing stale paths breaks `/design`'s anchor-detection.

### RULE R-prd-02 — Body-only, no YAML frontmatter (checked)

The first non-blank line of `{NAME} PRD.md` is `# {NAME} PRD` (H1). No `---` YAML block precedes it.

**Check pattern:** first non-blank line starts with `# `; does not start with `---`.

**Why:** body-only matches the broader vault discipline (CAB Rules, CAB Status, CAB Log, CAB Stories all body-only). Frontmatter is invisible in Obsidian read view and drifts silently.

### RULE R-prd-03 — `description::` is the second non-blank line (checked)

Immediately after the H1, the next non-blank line is a `description::` dataview inline field with a one-line tagline.

**Check pattern:** second non-blank line matches `^description:: .+$` and contains no `::` tokens inside its value.

**Why:** Dataview discoverability; consistency with sibling facet specs.

### RULE R-prd-04 — Required sections present in order (checked)

The PRD contains H2s `## Overview`, `## Design Workflow`, `## Goals`, `## Non-Goals`, `## User Stories` (in that order). Optional H2s (`## Open Questions`, `## Resolved`, `## See also`) may follow.

**Check pattern:** parse H2 headers; assert the five required ones appear in declared order.

**Why:** downstream design phases read the PRD assuming this section spine. Missing sections force the reader to hunt for what they expect to find in a known location.

### RULE R-prd-05 — User stories use `US-<RID>-<N>` numbering (checked)

Every user-story H3 (inline form) matches `^### US-{RID}-\d+: .+` where `{RID}` is the anchor's RID. Folder-form PRDs link to `[[{NAME} Stories]]` instead of inline H3s and this rule defers to [[CAB Stories#RULESET R-stories|R-stories]].

**Check pattern:** for inline-form PRDs, enumerate H3s under `## User Stories`; assert each matches the pattern.

**Why:** `US-<RID>-<N>` is the load-bearing identifier referenced by feature docs (`Realizes: US-<RID>-<N>`), e2e tests (`Exercises: US-<RID>-<N>`), and Stories sub-facet files. Old `US-<N>` form (no RID) collides across anchors and breaks cross-anchor references.

### RULE R-prd-06 — No legacy `{NAME} Open Questions.md` file (checked)

No file named `{NAME} Open Questions.md` exists alongside the PRD. Open questions live as `## Open Questions` H2 directly inside the PRD per [[ask-format]].

**Check pattern:** `ls "{NAME} Design/{NAME} Open Questions.md"` returns no-such-file.

**Why:** the file-based Open Questions pattern was deprecated when `/ask` became the universal asking surface. Linger of the old file produces ambiguity about where to look.

### RULE R-prd-07 — Design Workflow references modern phase names (checked)

The `## Design Workflow` table references `[[{NAME} Architecture]]` (not "System Design"), `[[{NAME} Testing]]` (not "Testing Strategy"), and `[[{NAME} Decisions]]` (not "Principles").

**Check pattern:** parse the Design Workflow table; assert the wiki-link targets are in the modern naming set.

**Why:** F094 (Architecture vs System Design), F113 (Decisions vs Principles), and the 2026-06-10 CAB Testing facet rename (`Testing.md`, not `Testing Strategy.md`) all renamed canonical phase names. References to old names produce broken wiki-links.

### RULE R-prd-08 — Status tracked centrally, not per-doc (stated)

The PRD file does NOT carry a top-of-doc `status::` dataview field. PRD design-phase completeness is tracked in `{NAME} Track/{NAME} Status.md` per [[CAB Status]] on the `prd::` line.

**Check pattern:** grep `{NAME} PRD.md` for `^status::`; expect zero matches when `{NAME} Track/{NAME} Status.md` exists.

**Why:** dual-source-of-truth is the failure mode. F130 made `{NAME} Status.md` authoritative; per-doc `status::` is a legacy fallback that should fade as anchors land Status.md files.

### RULE R-prd-09 — No `## Design Constraints` (DC-N) section (stated)

The PRD does NOT contain a `## Design Constraints` H2 with DC-numbered entries. Architectural / technical constraints belong in [[CAB Decisions]] (`D<N>`) and [[CAB Rules]] (`R-<slug>-<NN>`); business / environmental constraints live in `## Non-Goals` or `## Overview`.

**Check pattern:** grep for `^## Design Constraints` or `^### DC-\d+`; expect zero matches.

**Why:** the pre-F113 DC-N pattern conflated business and architectural constraints, and downstream readers couldn't tell which discipline owned which constraint. Splitting Decisions / Rules / Non-Goals gives each constraint a clear home.

### RULE R-prd-10 — Dispatch table carries a Stories row with proper-name display (checked)

The PRD's top-of-doc dispatch table contains a row whose wiki-link target points at the stories — either `[[{NAME} PRD#User Stories\|{NAME} Stories]]` (single-file form) or `[[{NAME} Stories]]` (folder form). The displayed text is always the proper anchor-prefixed name `{NAME} Stories`, matching the display convention used by sibling dispatch rows (`{NAME} Architecture`, `{NAME} Testing`, etc.).

**Check pattern:** parse the PRD's dispatch table; assert at least one row's link target matches one of the two canonical forms AND the row's displayed text is `{NAME} Stories`.

**Why:** Stories are the "what does this product DO for users" of the PRD — readers landing on the PRD need a one-click jump to them without scrolling through Overview / Design Workflow / Goals first. Proper-name display keeps the dispatch table internally consistent; bare "Stories" loses the anchor prefix that every other row carries.

# BRIEF

- **This file is the PRD facet spec** — the authoritative shape, location, section spine, and lifecycle rules for every `{NAME} PRD.md` in the vault. Editors of this file are amending that contract; treat changes as load-bearing for `/design prd`, every downstream design phase, and the embedded `R-prd` rule set.
- **NOT a PRD instance, and NOT a meta-discussion of product management** — don't pile authoring tips, prose about writing good user stories, or example PRDs into the body. Worked examples are cited by wiki-link ([[CAE PRD]]); rationale for one-off prescriptions lives in the rule's **Why** block, not in narrative.
- **Inclusion test for new content:** does it specify the SHAPE of `{NAME} PRD.md` (where it lives, what sections it must carry, what fields it must declare, how it's surfaced from sibling docs, how its lifecycle interacts with `/ask` and `{NAME} Status.md`)? If yes, it belongs. If it's about technical decisions, principles, or implementation, route to [[CAB Decisions]] / [[CAB Rules]] / [[CAB Architecture]] instead — the body already says PRDs are not that.
- **Two co-located zones — keep them aligned:** the facet-spec prose above and the embedded `# RULESET R-prd` below must agree. When a section-order rule, naming convention, or location prescription changes in the prose, update the matching `### RULE R-prd-NN` block (and its **Check pattern** / **Why**) in the same edit. Drift between the two is the failure mode this file is built to avoid.
- **Rule numbering is monotonic-forever** — `R-prd-NN` IDs are never recycled. New rules append at the next integer; deprecated rules are marked but their numbers stay reserved. Renumbering breaks every `cites:` link from `{NAME} Decisions.md` files that adopted this ruleset.
- **Wiki-link targets are load-bearing** — references to [[CAB Stories]], [[CAB Decisions]], [[CAB Architecture]], [[CAB Testing]], [[CAB Status]], [[ask-format]], [[progressive-disclosure]], and the worked example [[CAE PRD]] are the spec's external dependencies. If any of those is renamed, the rename must propagate here in the same commit.
- **The `## Standard section order` table is the spine** — its row order is the order rule `R-prd-04` enforces. Don't reorder rows for stylistic reasons; downstream readers and the audit script both depend on the declared sequence.
