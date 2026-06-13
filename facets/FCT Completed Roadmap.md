# CAB Completed Roadmap
description:: facet spec this doc follows

The Completed Roadmap is the **migration target** for whole milestones that reach completion. Roadmap stays forward-looking; this doc captures everything that's shipped — preserving the milestone structure that the project used to plan it.

**Name choice — provenance:** discussed in [[F144 — Completed Roadmap + named milestones]]. *History* was rejected because it implies temporal precision (which we don't claim). *Completed Roadmap* describes what the doc actually contains: preserved milestone structure with rough chronology. If precise temporal order is ever wanted, a separate `History` doc can hold it; the Completed Roadmap is not that.

## Location

`{NAME} Design/{NAME} Completed Roadmap.md` — sibling of `{NAME} Roadmap.md`.

## Structure — newest at top

The Completed Roadmap reads top-to-bottom as **newest to oldest by migration date**. Two kinds of section alternate:

1. **Standalone-completed-features groupings** — `## Completed standalone features (since <last-migration>)`. These accumulate as features reach Done that aren't part of any milestone (the common case for backlog-pulled features). The grouping at the top of the doc is the *current* one; new completions append here. When the next milestone migrates in, this grouping is "sealed" (no more entries added) and a fresh one starts at the top.

2. **Migrated milestone sections** — `## [x] M-<Name> — <Milestone Title> (migrated <YYYY-MM-DD>)`. Inserted below the most recent standalone-features grouping at migration time. The milestone keeps its full structure: sub-items, Status line, reference block.

### Example structure

```markdown
# {NAME} Completed Roadmap

## Completed standalone features (since 2026-06-01)

- [x] [[F042 — Add retry budget cap]] — (Done 2026-06-08)
- [x] [[F045 — Verbose status output]] — (Done 2026-06-05)
- [x] [[F046 — Cancel-by-prefix matching]] — (Done 2026-06-04)

## [x] M-Store — Persistence Layer (migrated 2026-06-01)

**Status:** Complete — WAL + SQLite + recovery loader all merged. F049 spun out + deferred.

**Tests:** 24 unit + 6 integration tests added; CI green.

- [x] [[F050 — M-Store.1: SQLite schema + migrations]]
- [x] [[F052 — M-Store.2: WAL append path]]
- [x] [[F055 — M-Store.3: Recovery loader]]
- [~] M-Store.4 — Snapshot rotation (deferred — see M-Polish)

## Completed standalone features (between M-Store and M-Core)

- [x] [[F020 — Status output color]] — (Done 2026-05-22)

## [x] M-Core — Core Scheduler Engine (migrated 2026-05-15)

**Status:** Complete — priority queue + worker pool + retry + drain shipped. 8 of 8 sub-items.

- [x] [[F003 — M-Core.1: Priority queue implementation]]
- [x] [[F006 — M-Core.2: Worker thread pool]]
- [x] [[F009 — M-Core.3: Retry logic with exponential backoff]]
- [x] [[F011 — M-Core.4: Cancellation and drain]]
- (and so on)
```

**Why this structure (provenance — discussed in [[F144]]):**

Top-to-bottom = newer-to-older gives rough chronology without claiming temporal precision. Standalone-features groupings between milestones capture "things that got done between milestone shipments" without forcing them into a fake milestone. Partial milestone work that got done before the milestone was abandoned can land in the standalone grouping at migration time (no forced grouping).

## What migrates and when

**Migration unit is the whole milestone.** Trigger: every sub-item is `[x]`, parent milestone heading is `[x]`. Migration moves:

- The milestone H2 heading (with its `[x]` checkbox)
- The Status line + reference block
- All sub-items (in current state — `[x]` for done, `[~]` for deferred, etc.)
- Any per-sub-item Reference block content

Migration is **append at top below current standalone grouping, then seal the standalone grouping**. The standalone grouping reads "since X" — where X is the previous milestone migration. After the new milestone gets inserted, a fresh empty standalone grouping is created at the very top with the new "since" date.

**Migration is currently manual.** F145 will ship `state roadmap migrate M-<Name>` to automate this.

## When a milestone is abandoned, not completed

If a milestone is being dropped (not all sub-items will land), the user has a choice:

- **Drop entirely** — delete the milestone from the roadmap; do not migrate to Completed Roadmap. Lost.
- **Salvage completed sub-items** — at migration time, transfer the `[x]` sub-items from the abandoned milestone into the current standalone-completed-features grouping. The milestone heading itself is dropped. The completed work survives as standalone features.

This handles the "we did some of M-Auth's sub-items before realizing we wanted to scope it down" case.

## Trait applicability

Any anchor that uses CAB Roadmap. Activated as soon as the first milestone migrates.

## Preface zone

Per [[DSC progressive-disclosure]]:

- **Dispatch table** — Required.
- **TLDR** — Optional. May summarize: "N milestones migrated, latest M-X on YYYY-MM-DD."
- **Figure** — N/A.

## See also

- [[FCT Roadmap]] — parent facet; the forward-looking roadmap is the migration source
- [[FCT Features]] — feature docs; the M-position is encoded in their titles per R-roadmap-10
- [[FCT Design]] — Completed Roadmap is an OPTIONAL child of {NAME} Design/; activated when the first milestone migrates
- [[F144 — Completed Roadmap + named milestones]] — the feature that landed this convention
- F145 (future) — `state roadmap migrate` script automation


# RULESET R-completed-roadmap
include::
description:: Structural rules for {NAME} Completed Roadmap.md — sibling of CAB Roadmap; preserves migrated milestones in newest-on-top order.

Embedded rule set for the Completed Roadmap facet, co-located with the spec above per [[F133 — Rule sets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella.

### RULE R-completed-roadmap-01 — Location is `{NAME} Design/{NAME} Completed Roadmap.md` (checked)

The doc lives at `{NAME} Design/{NAME} Completed Roadmap.md` — sibling of `{NAME} Roadmap.md`.

**Check pattern:** when one or more milestones have migrated, `ls "{anchor}/{NAME} Design/{NAME} Completed Roadmap.md"` exists. When zero migrations have occurred, the file may be absent — it's created on first migration.

**Why:** companion location keeps the forward and the completed views adjacent.

### RULE R-completed-roadmap-02 — Body-only, no YAML frontmatter (checked)

First non-blank line is `# {NAME} Completed Roadmap` (H1). No `---` block precedes.

**Why:** matches the vault-wide body-only convention.

### RULE R-completed-roadmap-03 — Top-to-bottom order is newest-to-oldest (sampled)

Migrated milestone H2 sections appear in reverse-chronological order by migration date. The migration date is in the heading: `## [x] M-<Name> — <Title> (migrated YYYY-MM-DD)`.

**Check pattern:** parse migrated milestone H2s; extract dates; assert monotonically non-increasing top-to-bottom.

**Why:** the reader's primary query is "what shipped most recently?" Reverse-chrono gives that answer first.

### RULE R-completed-roadmap-04 — Standalone groupings interleave with migrated milestones (sampled)

Standalone-completed-features groupings (H2s named `## Completed standalone features (since <date>)`) appear between migrated milestone sections, capturing features that completed in that window. At most one "current" standalone grouping exists at the top.

**Check pattern:** parse H2 headings; classify each as `migrated milestone` or `standalone grouping`; assert structure alternates plausibly (standalone groupings between or above milestones, never below all milestones).

**Why:** standalone-feature completions get a coherent home that's still rough-chronological without forcing them into fake milestones.

### RULE R-completed-roadmap-05 — Migrated milestones preserve their full structure (stated)

A migrated milestone retains its Status line, reference block, and all sub-items (in their final `[x]` / `[~]` / abandoned state) exactly as they were in the Roadmap at migration time.

**Check pattern:** sample migrated milestones; assert presence of Status line and sub-items.

**Why:** migration is structural, not summarizing. Preserves the project's reasoning about what shipped together.

### RULE R-completed-roadmap-06 — Migrated milestones never come back (stated)

Once a milestone migrates to Completed Roadmap, it stays. Reactivation of work in the same domain creates a new milestone (e.g., `M-Auth-V2`), not a revival of the old one.

**Check pattern:** git history — assert no roadmap entry uses an M-name that already appears in Completed Roadmap.

**Why:** keeps the historical record honest. Reopened work is genuinely a new milestone with new scope.

# BRIEF

- **This file is the facet spec for `{NAME} Completed Roadmap.md`** — it defines what the completed-roadmap doc must look like in any anchor that uses CAB Roadmap. Edits here change the contract for every consumer.
- **Spec content + embedded RULESET only.** Keep the spec body (location, structure, migration semantics, trait applicability) and the embedded `R-completed-roadmap` RULESET aligned — when the spec changes a structural rule, mirror it in the matching R-rule and bump the check pattern.
- **Do NOT put per-anchor completed-roadmap content here.** Actual migrated milestones live in `{ANCHOR}/{NAME} Design/{NAME} Completed Roadmap.md`; this file holds rules and example shapes only.
- **The inclusion test for a new rule:** it constrains the *structure* of the completed-roadmap doc (location, order, preservation, naming) — not the forward-looking Roadmap (that's [[FCT Roadmap]]) and not feature-doc shape (that's [[FCT Features]]).
- **Provenance lives in [[F144]].** When questions arise about "why this name?" or "why newest-on-top?", point to the F144 discussion rather than re-litigating in this spec.
- **Cross-reference integrity is load-bearing:** the See also links to [[FCT Roadmap]], [[FCT Features]], [[FCT Design]], and F144/F145 wire this facet into the larger CAB graph — don't drop them when refactoring.
- **Sibling-doc invariant:** Completed Roadmap is always a sibling of Roadmap under `{NAME} Design/` — never relocate, never nest. R-completed-roadmap-01 enforces this.
