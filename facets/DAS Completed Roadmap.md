---
description: "completed-roadmap facet — migrated milestones in newest-on-top order, sibling of the forward-looking Roadmap"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Completed Roadmap](hook://p/DAS%20Completed%20Roadmap)
# FCT Completed Roadmap
The migration target for completed milestones — preserves shipped milestone structure in newest-to-oldest order alongside the forward-looking Roadmap.

**Related:** [[DAS Roadmap]],  [[DAS Design Folder]],  [[DAS Features]],  [[DAS Design Docs]]
**Examples:** [[FEX Completed Roadmap\|example]]
**Rules:** [[#RULESET R-completed-roadmap|R-completed-roadmap]]

**TLDR** — One doc per anchor (when any milestone has migrated). Lives at `{slug} Design/{slug} Completed Roadmap.md`. Newest migrated milestone at top; standalone-completed-features groupings interleave between milestones. Cardinality: **one per anchor**.

The Completed Roadmap is the **migration target** for whole milestones that reach completion. Roadmap stays forward-looking; this doc captures everything that's shipped — preserving the milestone structure that the project used to plan it.

**Name choice — provenance:** discussed in [[F144 — Completed Roadmap + named milestones]]. *History* was rejected because it implies temporal precision (which we don't claim). *Completed Roadmap* describes what the doc actually contains: preserved milestone structure with rough chronology. If precise temporal order is ever wanted, a separate `History` doc can hold it; the Completed Roadmap is not that.

## Location

`{slug} Design/{slug} Completed Roadmap.md` — sibling of `{slug} Roadmap.md`.

## Structure — newest at top

The Completed Roadmap reads top-to-bottom as **newest to oldest by migration date**. Two kinds of section alternate:

1. **Standalone-completed-features groupings** — `## Completed standalone features (since <last-migration>)`. These accumulate as features reach Done that aren't part of any milestone (the common case for backlog-pulled features). The grouping at the top of the doc is the *current* one; new completions append here. When the next milestone migrates in, this grouping is "sealed" (no more entries added) and a fresh one starts at the top.

2. **Migrated milestone sections** — `## [x] M-<Name> — <Milestone Title> (migrated <YYYY-MM-DD>)`. Inserted below the most recent standalone-features grouping at migration time. The milestone keeps its full structure: sub-items, Status line, reference block.

### Section order, top to bottom

The two section kinds alternate down the page, newest first:

- **H1** — `# {slug} Completed Roadmap`.
- **Current standalone grouping** — `## Completed standalone features (since <date>)` at the very top, each line `- [x] [[F<NNN> — <Title>]] — (Done <date>)`.
- **Most-recent migrated milestone** — `## [x] M-<Name> — <Title> (migrated <date>)`, followed by its preserved `**Status:**` line, reference block (`**Tests:**`, …), and its `- [x] [[F<NNN> — M-<Name>.<n>: …]]` sub-item bullets (with any `[~]` deferred sub-items retained).
- **Interleaved standalone groupings** — `## Completed standalone features (between M-<X> and M-<Y>)` capturing features that completed in that window.
- **Older migrated milestones** — same shape as above, continuing down in reverse-chronological order.

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

Per [[DAS progressive-disclosure]]:

- **Dispatch table** — Required.
- **TLDR** — Optional. May summarize: "N milestones migrated, latest M-X on YYYY-MM-DD."
- **Figure** — N/A.

## See also

- [[DAS Roadmap]] — parent facet; the forward-looking roadmap is the migration source
- [[DAS Features]] — feature docs; the M-position is encoded in their titles per R-roadmap-10
- [[DAS Design Folder]] — Completed Roadmap is an OPTIONAL child of {slug} Design/; activated when the first milestone migrates
- [[F144 — Completed Roadmap + named milestones]] — the feature that landed this convention
- F145 (future) — `state roadmap migrate` script automation

# RULESET R-completed-roadmap
include::
where:: `file:{anchor}/**/* Completed Roadmap.md`
description:: completed-roadmap facet — migrated milestones in newest-on-top order, sibling of the forward-looking Roadmap

Embedded ruleset for the Completed Roadmap facet, co-located with the spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella.

### RULE R-completed-roadmap-01 — Location is `{slug} Design/{slug} Completed Roadmap.md` (checked)

The doc lives at `{slug} Design/{slug} Completed Roadmap.md` — sibling of `{slug} Roadmap.md`.

**Check pattern:** when one or more milestones have migrated, `ls "{anchor}/{slug} Design/{slug} Completed Roadmap.md"` exists. When zero migrations have occurred, the file may be absent — it's created on first migration.

**Why:** companion location keeps the forward and the completed views adjacent.

### RULE R-completed-roadmap-02 — Body-only, no YAML frontmatter (checked)
check:: h1_no_frontmatter

First non-blank line is `# {slug} Completed Roadmap` (H1). No `---` block precedes.

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

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + embedded `R-completed-roadmap` RULESET above; design rationale is [[F144 — Completed Roadmap + named milestones]].)*

- **TODO: link a worked example** — no real `{slug} Completed Roadmap.md` instance exists yet (the facet landed with F144; no milestone has migrated). When the first ships, add it to `## See also` and reference it from § Structure in place of the prose outline.
- **Keep spec ↔ embedded RULESET aligned** — when the spec body changes a structural rule (location, order, preservation, naming), mirror it in the matching `R-completed-roadmap` rule and bump the check pattern; never put per-anchor migrated-milestone content here (it lives in `{anchor}/{slug} Design/{slug} Completed Roadmap.md`).
- **Inclusion test for a new rule** — it constrains the *structure* of the completed-roadmap doc (location, order, preservation, naming), not the forward-looking Roadmap ([[DAS Roadmap]]) or feature-doc shape ([[DAS Features]]).
- **Cross-reference integrity is load-bearing** — the `## See also` links to [[DAS Roadmap]], [[DAS Features]], [[DAS Design Folder]], and F144/F145 wire this facet into the CAB graph; don't drop them when refactoring.
