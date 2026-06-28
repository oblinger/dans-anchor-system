---
description: "status facet — one {NAME} Status.md per anchor tracking design-phase completeness via a tier ladder"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Track]] → [FCT Status](hook://p/FCT%20Status)

# FCT Status
One file per anchor that tracks design-phase completeness, one dataview line per design facet, using a monotonic tier ladder read/written by the state script.

**Related:** [[FCT Backlog]],  [[FCT Roadmap]],  [[design]],  [[workflow]]
**Examples:** [[HBR Status\|example]]

| Table of Contents |  |
|---|---|
| [[#Location]] |  |
| [[#Distinction — workflow state vs Status cell]] |  |
| [[#File shape]] |  |
| [[#Cell format]] |  |
| [[#Cell semantics — when each tier applies]] |  |
| [[#State script]] |  |
| [[#Track dispatch wiring]] |  |
| [[#Trait applicability]] |  |
| [[#Audit]] |  |
| [[#See also]] |  |
| **[[#BRIEF]]** |  |

**TLDR** — One `{NAME} Status.md` per anchor (cardinality: **one**), body-only (no YAML frontmatter), with a `description::` line followed by exactly five `<facet>::` dataview lines in declared order (`prd`, `ux`, `architecture`, `testing`, `roadmap`). Each cell is one of `none < MVP-agent < MVP-user < Full-agent < Full-user`. Reads/writes are mediated by the `state` script; the picker walks the ladder bottom-up; promotion is monotonic.

The Status facet specifies the format of `{NAME} Status.md` — the per-anchor file that tracks **design-phase completeness**. One row per design facet (`prd` / `ux` / `architecture` / `testing` / `roadmap`), each carrying a tier value, a grading-actor, a date, and a one-line rationale. The file is read by `/design`'s picker (bare `/design` dispatches to the lowest-tier facet) and by `/mint`'s pre-implementation gate.

Body-only — no YAML frontmatter. The first content line is the `# CAB Status` H1; the second is the `description::` dataview inline field above; everything else is plain markdown. (Same body-only discipline as [[FCT Ruleset]].)

## Location

`{NAME} Track/{NAME} Status.md` — single file per anchor, in the Track folder alongside Backlog and Roadmap. Reachable from `{NAME} Track.md`'s dispatch table via a `[[{NAME} Status]]` row.

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
# {NAME} Status
description:: status facet — one `{NAME} Status.md` per anchor tracking design-phase completeness via a tier ladder

prd::          MVP-user  (2026-06-08) — covers golden path; edge cases unspecified
ux::           MVP-agent (2026-06-07) — three screens sketched; flow validated
architecture:: MVP-user  (2026-06-08) — subsystems, data flow, thread model
testing::      MVP-agent (2026-06-09) — strategy + 18 proposed tests, awaits user review
roadmap::      none
```

**Required lines, positional:**

- **Line 1:** `# CAB Status` H1 — wait, in the concrete file: `# {NAME} Status` (the file's H1 matches the anchor).
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

Reads and writes `{NAME} Status.md` are mediated by `~/.claude/skills/workflow/scripts/state`. The script lives in the [[workflow]] discipline's scripts folder (parallel to `backlog-edit.py` which mediates [[CAB Backlog]]'s file). Hand-editing the Status file is discouraged but not forbidden — the script just validates and rewrites on next access.

Key invocations:

```bash
state --anchor {NAME} status show              # Print all facets one per line
state --anchor {NAME} status set <facet> <cell> --note "<reason>"  # Promote one facet
state --anchor {NAME} status get <facet>       # Print one facet
```

On first `set`, the script auto-creates `{NAME} Status.md` with all 5 facets at `none`.

## Track dispatch wiring

The Track folder's dispatch page (`{NAME} Track.md`) MUST include a row pointing at the Status file:

```markdown
| [[{NAME} Status]] | design-phase completeness per facet; consumed by /design picker |
```

That makes the Status reachable in one click from the anchor's main Track surface.

## Trait applicability

Available to any anchor with a `{NAME} Design/` folder per [[FCT Design]]. v1 facet list (`prd`, `ux`, `architecture`, `testing`, `roadmap`) matches the canonical `/design` phase set; per-trait facet-list customization is Phase 2.

## Audit

`/audit status` (future) would flag:
- **missing-file** — anchor has `/design` activity (Backlog mentions design work, Design folder has artifacts) but no Status file.
- **invalid-cell** — a facet line has a cell value not in the ladder.
- **non-monotonic** — a `set` operation tried to downgrade a cell (script-side; recorded for audit).
- **missing-note-on-user** — `*-user` tier line has no `— <note>`.
- **missing-date** — non-`none` cell has no `(YYYY-MM-DD)`.
- **wrong-location** — file lives anywhere other than `{NAME} Track/`.
- **frontmatter-present** — YAML frontmatter on the file (should be body-only).
- **dispatch-unlinked** — `{NAME} Track.md` doesn't have a row linking to `[[{NAME} Status]]`.

## See also

- [[workflow]] — the state-graph discipline; orthogonal vocabulary, not interchangeable.
- [[CAB Backlog]] — sibling Track-folder facet; same pattern (file format + script-mediated writes).
- [[FCT Testing]] — peer Design facet whose `status:: accepted` is consumed by `/design`'s gate.
- [[design]] — picker consumer; reads Status to pick next facet.
- [[F130 — Planning Status facet — per-facet tier+approver; plan picker; pre-impl gate]] — the feature that introduced this facet.

# RULESET R-status
include::
where:: file:{ANCHOR}/**/* Status.md
description:: Structural rules for the {NAME} Status.md facet doc; enforces the per-facet dataview-line shape and cell ladder.

Embedded ruleset for the Status facet, co-located with the facet spec above per the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention. Adopted via `R-facet` umbrella.

### RULE R-status-01 — File name `{NAME} Status.md` (checked)
check:: status_filename_valid

The status file is named `{NAME} Status.md` — anchor slug + space + `Status.md`. No qualifier suffix.

**Check pattern:** `ls "{anchor}/{NAME} Track/{NAME} Status.md"` exists; no alternate `Status Tracking.md` / `Plan Status.md` etc. alongside.

**Why:** the picker, the state script, and the Track-dispatch wiring all assume this exact name. Aliases break all three.

### RULE R-status-02 — Lives under `{NAME} Track/` (checked)
check:: status_in_track_folder

The Status file lives inside the Track folder, NOT the Design folder, NOT the anchor root.

**Check pattern:** path matches `{anchor}/{NAME} Track/{NAME} Status.md`.

**Why:** Status is a Track-folder facet (sibling of Backlog/Roadmap) — it tracks design *progress*, not design *content*. Design-folder content is what gets graded; Status is the grade book.

### RULE R-status-03 — Body-only, no YAML frontmatter (checked)
check:: regex_absent ^---$

The first non-blank line of the file is `# {NAME} Status` (H1). No `---` YAML block precedes it.

**Check pattern:** first non-blank line starts with `# `; does not start with `---`.

**Why:** body-only matches the broader vault discipline ([[FCT Ruleset]], [[CAB Backlog]] are also body-only). Frontmatter is invisible in normal Obsidian read view and easy to drift.

### RULE R-status-04 — `description::` is line 2 (checked)
check:: description_field_line

The line immediately after the H1 is a `description::` dataview inline field with a one-line tagline.

**Check pattern:** second non-blank line matches `^description:: .+$` and has no `::` tokens inside the value.

**Why:** Dataview discoverability; the description is what shows up in queries that list facet files.

### RULE R-status-05 — One `<facet>::` line per design facet, declared order (checked)
check:: status_facets_ordered

Lines after `description::` contain exactly five facet lines in this order: `prd`, `ux`, `architecture`, `testing`, `roadmap`.

**Check pattern:** parse all `^<name>:: ...` lines; expect the 5 names in this exact order, no duplicates, no extras.

**Why:** `/design`'s picker walks them in declared order for lowest-tier tie-breaks. Re-ordering would silently change which facet gets dispatched.

### RULE R-status-06 — Cell value is in the ladder (checked)
check:: status_cell_values_valid

Each facet line's cell value is one of `none`, `MVP-agent`, `MVP-user`, `Full-agent`, `Full-user`.

**Check pattern:** parse the cell-value token (first whitespace-separated token after `::`); assert membership.

**Why:** the picker compares cells using the ladder ordering; off-ladder values break comparison.

### RULE R-status-07 — Non-`none` cells carry a `(YYYY-MM-DD)` date (sampled)
check:: status_nonone_cells_dated

For every non-`none` cell, the line includes a parenthesized ISO date after the cell value.

**Check pattern:** for cells != `none`, line matches `:: <cell> \(\d{4}-\d{2}-\d{2}\)`.

**Why:** dates let the user judge staleness ("is this MVP-user grade from 6 months ago still trustworthy?") and let `/audit` flag entries that haven't been re-graded after major doc edits.

### RULE R-status-08 — `*-user` cells require a `— <note>` (sampled)
check:: status_user_cells_noted

For every cell ending in `-user`, the line includes an em-dash followed by a short note.

**Check pattern:** for cells matching `MVP-user|Full-user`, line matches ` — .+`.

**Why:** the user is making an explicit graded judgment; the note captures the WHY for later audit and helps future-self remember the basis for the grade.

### RULE R-status-09 — Track dispatch links to the Status file (checked)
check:: status_track_dispatch_linked

`{NAME} Track.md` contains a dispatch-table row whose link target is `[[{NAME} Status]]`.

**Check pattern:** grep `{NAME} Track.md` for `\[\[{NAME} Status\]\]`.

**Why:** the Status file should be one click away from the anchor's main Track surface. Otherwise users (and the agent) don't discover it.

### RULE R-status-10 — Cell promotion is monotonic up the ladder (stated)

The state script's `set` operation does not allow downgrading a cell (e.g., `MVP-user` → `MVP-agent`). Resetting to `none` IS allowed but requires an explicit `--reset` flag (script-side; not user-facing).

**Check pattern:** state script enforces; audit would inspect git history for downgrade-without-reset moves.

**Why:** progress is one-way; if scope changes enough to warrant a downgrade, the user should explicitly reset and re-grade rather than silently downgrade.

# BRIEF

- **This file is the Status-facet spec, not a Status file.** It defines the format of `{NAME} Status.md`; do not paste sample status entries here as if it were a status surface. Examples belong in fenced code blocks illustrating the format.
- **NOT for workflow-state vocabulary.** The `[Ready]/[Active]/[Verify]/...` graph lives in [[workflow]]; the Status-cell ladder (`none < MVP-agent < MVP-user < Full-agent < Full-user`) is orthogonal. Don't merge, alias, or cross-reference the two vocabularies as if they were interchangeable — keep the § Distinction table the canonical place that contrast lives.
- **Inclusion test for new rules / sections:** the rule must constrain the *file format, location, or promotion semantics* of `{NAME} Status.md` itself. Picker behavior, `/mint` gate logic, and per-facet authoring belong in [[design]] or the relevant `CAB <Facet>.md`, not here.
- **Cell ladder is load-bearing — five values, this exact order.** `none < MVP-agent < MVP-user < Full-agent < Full-user`. Do not add tiers, rename them, or change their ordering without coordinated updates to the state script, `/design`'s picker, and every adopting anchor's Status file. Same for the five facet names (`prd`, `ux`, `architecture`, `testing`, `roadmap`) in declared order.
- **Embedded `# RULESET R-status` is part of this file per F133.** Don't split it into a sibling Rules file; the facet spec + its ruleset live co-located. When editing rules, keep `(checked)` / `(sampled)` / `(stated)` markers honest — they tell the audit script which rules it can mechanize.
- **Body-only discipline is itself a rule (R-status-03).** Do not add YAML frontmatter to this spec or to sample files shown here; the first content line is always the `# {NAME} Status` H1.
- **When the format changes,** update both the § File shape example AND the corresponding `RULE R-status-NN` simultaneously — they are two views of the same constraint and must not drift.
