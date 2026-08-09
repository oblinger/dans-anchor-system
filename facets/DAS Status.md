---
description: "status facet — one {slug} Status.md per anchor tracking design-phase completeness via a tier ladder"
---

# DAS Status
One file per anchor that tracks design-phase completeness, one dataview line per design facet, using a monotonic tier ladder read/written by the state script.

| -[[DAS Status]]- | → [[DAS]] → [[FCT]] → [DAS Status](hook://p/DAS%20Status)  |
| --- | --- |
| Related | [[templates/status.md\|status template]],  [[DAS Backlog]],  [[DAS Roadmap]],  [[design]],  [[workflow]],   |
| Examples | [[HBR Status\|example]],   |
| Rules | [[R-status]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Rocks]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — One `{slug} Status.md` per anchor (cardinality: **one**), body-only (no YAML frontmatter), with a `description::` line followed by exactly five `<facet>::` dataview lines in declared order (`prd`, `ux`, `architecture`, `testing`, `roadmap`). Each cell is one of `none < MVP-agent < MVP-user < Full-agent < Full-user`. Reads/writes are mediated by the `state` script; the picker walks the ladder bottom-up; promotion is monotonic.

The Status facet specifies the format of `{slug} Status.md` — the per-anchor file that tracks **design-phase completeness**. One row per design facet (`prd` / `ux` / `architecture` / `testing` / `roadmap`), each carrying a tier value, a grading-actor, a date, and a one-line rationale. The file is read by `/design`'s picker (bare `/design` dispatches to the lowest-tier facet) and by `/mint`'s pre-implementation gate.

Body-only — no YAML frontmatter. The first content line is the `# {slug} Status` H1; the second is the `description::` dataview inline field above; everything else is plain markdown. (Same body-only discipline as [[DAS Ruleset]].)

## Location

`{slug} Track/{slug} Status.md` — single file per anchor, in the Track folder alongside Backlog and Roadmap. Reachable from `{slug} Track.md`'s dispatch table via a `[[{slug} Status]]` row.

## Distinction — workflow state vs Status cell

These are orthogonal vocabularies; they describe different things and are not interchangeable:

| | [[workflow]] state graph | Status cell |
|---|---|---|
| Vocabulary | `[Designing] / [Ready] / [Active] / [Verify] / [Done] / [Questions] / [Blocked] / [Waiting] / [Watching]` | `none < MVP-agent < MVP-user < Full-agent < Full-user` |
| Answers | "where is this unit of work in its lifecycle?" | "how complete is this design facet, and who graded it?" |
| Applies to | Backlog rows, roadmap rows, feature-doc Status fields, PRDs | Per-facet design-completeness grading only |
| Cited by | Backlog, Features, /groom, /mint, /finalize | The state script + `/design` picker only |

A facet can be `[Ready]` in workflow terms AND `MVP-agent` in Status terms simultaneously — meaning different things. Do not conflate.

## File shape

```markdown
# {slug} Status
description:: status facet — one `{slug} Status.md` per anchor tracking design-phase completeness via a tier ladder

prd::          MVP-user  (2026-06-08) — covers golden path; edge cases unspecified
ux::           MVP-agent (2026-06-07) — three screens sketched; flow validated
architecture:: MVP-user  (2026-06-08) — subsystems, data flow, thread model
testing::      MVP-agent (2026-06-09) — strategy + 18 proposed tests, awaits user review
roadmap::      none
```

**Required lines, positional:**

- **Line 1:** `# {slug} Status` H1 — the file's H1 matches the anchor.
- **Line 2:** `description::` dataview inline field — one-line tagline.
- **Lines 4+:** one `<facet>::` dataview line per design facet, in declared order: `prd`, `ux`, `architecture`, `testing`, `roadmap`. The order is load-bearing — `/design`'s picker walks them in this order for tie-breaks.

## Cell format

Each facet line follows this shape:

```
<facet>:: <cell> (<YYYY-MM-DD>) — <one-line note>
```

- **`<facet>`** — one of `prd` / `ux` / `architecture` / `testing` / `roadmap` (v1 hardcoded; per-anchor extension is Phase 2).
- **`<cell>`** — one of `none` / `MVP-agent` / `MVP-user` / `Full-agent` / `Full-user`. Strictly ordered low → high; the picker treats this ladder as monotonic. Other values invalid.
- **`(<YYYY-MM-DD>)`** — ISO date the cell was set. Required for non-`none` cells; absent when cell is `none`.
- **`<one-line note>`** — short rationale (~ 5-15 words). Required for `*-user` cells (user must say WHY they're confirming); recommended for `*-agent`. Absent when cell is `none`.

## Cell semantics — when each tier applies

| Cell | Meaning | Set by |
|---|---|---|
| `none` | Facet not yet started | Default at file creation |
| `MVP-agent` | Agent has written the doc to "MVP" depth; awaits user review | Sub-skill self-promote at completion |
| `MVP-user` | User has reviewed and approved the MVP-depth doc | User in natural language ("PRD looks good") |
| `Full-agent` | Agent has fleshed it out to "Full" depth; awaits user review | Sub-skill self-promote on second-pass authoring |
| `Full-user` | User has reviewed and approved the Full-depth doc | User in natural language ("PRD is complete") |

**Promotion is monotonic.** Cells only move up the ladder (or reset to `none` deliberately on a major scope change). The state script enforces this.

## State script

Reads and writes `{slug} Status.md` are mediated by `~/.claude/skills/workflow/scripts/state`. The script lives in the [[workflow]] discipline's scripts folder (parallel to `backlog-edit.py` which mediates [[DAS Backlog]]'s file). Hand-editing the Status file is discouraged but not forbidden — the script just validates and rewrites on next access.

Key invocations:

```bash
state status {slug} show              # Print all facets one per line
state status {slug} set <facet> <cell> --note "<reason>"  # Promote one facet
state status {slug} get <facet>       # Print one facet
```

On first `set`, the script auto-creates `{slug} Status.md` with all 5 facets at `none`.

## Track dispatch wiring

The Track folder's dispatch page (`{slug} Track.md`) MUST include a row pointing at the Status file:

```markdown
| [[{slug} Status]] | design-phase completeness per facet; consumed by /design picker |
```

That makes the Status reachable in one click from the anchor's main Track surface.

## Trait applicability

Available to any anchor with a `{slug} Design/` folder per [[DAS Design Folder]]. v1 facet list (`prd`, `ux`, `architecture`, `testing`, `roadmap`) matches the canonical `/design` phase set; per-trait facet-list customization is Phase 2.

## Audit

`/audit status` (future) would flag:
- **missing-file** — anchor has `/design` activity (Backlog mentions design work, Design folder has artifacts) but no Status file.
- **invalid-cell** — a facet line has a cell value not in the ladder.
- **non-monotonic** — a `set` operation tried to downgrade a cell (script-side; recorded for audit).
- **missing-note-on-user** — `*-user` tier line has no `— <note>`.
- **missing-date** — non-`none` cell has no `(YYYY-MM-DD)`.
- **wrong-location** — file lives anywhere other than `{slug} Track/`.
- **frontmatter-present** — YAML frontmatter on the file (should be body-only).
- **dispatch-unlinked** — `{slug} Track.md` doesn't have a row linking to `[[{slug} Status]]`.

## See also

- [[workflow]] — the state-graph discipline; orthogonal vocabulary, not interchangeable.
- [[DAS Backlog]] — sibling Track-folder facet; same pattern (file format + script-mediated writes).
- [[DAS Testing]] — peer Design facet whose `status:: accepted` is consumed by `/design`'s gate.
- [[design]] — picker consumer; reads Status to pick next facet.
- [[F130 — Planning Status facet — per-facet tier+approver; plan picker; pre-impl gate]] — the feature that introduced this facet.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above + the extracted [[R-status]] ruleset.)*

- **This is the Status-facet spec, not a Status file** — don't paste live status entries here as if it were a status surface; sample entries stay in fenced code blocks illustrating the format.
- **Keep the two vocabularies separate** — workflow state (`[Ready]/[Active]/…`, in [[workflow]]) and the Status-cell ladder are orthogonal; § Distinction is the canonical place that contrast lives — don't merge, alias, or cross-reference them elsewhere.
- **Inclusion test for new rules / sections** — the rule must constrain the *file format, location, or promotion semantics* of `{slug} Status.md` itself; picker behavior, `/mint`-gate logic, and per-facet authoring belong in [[design]] or the relevant `CAB <Facet>.md`, not here.
- **Cell ladder + facet names are load-bearing** — changing the five ladder values or their order, or the five facet names or their declared order, requires coordinated updates to the `state` script, `/design`'s picker, and every adopting anchor's Status file.
- **`R-status` was extracted to a sibling ruleset (2026-07-12 tracking-group pass)** — keep the spec body and [[R-status]] in sync (a format change requires the matching `R-status-NN` change); keep the `(checked)` / `(sampled)` / `(stated)` markers honest — they tell the audit script which rules it can mechanize.
- **Keep the two views in sync** — when the format changes, update the § File shape example AND the corresponding `RULE R-status-NN` in the same pass; they must not drift.
