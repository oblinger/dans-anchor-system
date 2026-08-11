# RULESET R-status
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file:{anchor}/**/* Status.md`
description:: Structural rules for the {slug} Status.md facet doc; enforces the per-facet dataview-line shape and cell ladder.

Ruleset for the Status facet — spec: [[DAS Status]] (extracted from the spec 2026-07-12). Armed by [[R-anchor]]'s `include::` — the umbrella `/audit anchor` resolves. Being named by [[R-facet]] is catalog membership, not adoption — that umbrella sits outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so an `include::` there arms nothing ([[TINK Backlog#^T208|T208]]).

### RULE R-status-01 — File name `{slug} Status.md` (checked)
check:: status_filename_valid

The status file is named `{slug} Status.md` — anchor slug + space + `Status.md`. No qualifier suffix.

**Check pattern:** `ls "{anchor}/{slug} Track/{slug} Status.md"` exists; no alternate `Status Tracking.md` / `Plan Status.md` etc. alongside.

**Why:** the picker, the state script, and the Track-dispatch wiring all assume this exact name. Aliases break all three.

### RULE R-status-02 — Lives under `{slug} Track/` (checked)
check:: status_in_track_folder

The Status file lives inside the Track folder, NOT the Design folder, NOT the anchor root.

**Check pattern:** path matches `{anchor}/{slug} Track/{slug} Status.md`.

**Why:** Status is a Track-folder facet (sibling of Backlog/Roadmap) — it tracks design *progress*, not design *content*. Design-folder content is what gets graded; Status is the grade book.

### RULE R-status-03 — Body-only, no YAML frontmatter (checked)
check:: regex_absent ^---$

The first non-blank line of the file is `# {slug} Status` (H1). No `---` YAML block precedes it.

**Check pattern:** first non-blank line starts with `# `; does not start with `---`.

**Why:** body-only matches the broader vault discipline ([[DAS Ruleset]], [[DAS Backlog]] are also body-only). Frontmatter is invisible in normal Obsidian read view and easy to drift.

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

`{slug} Track.md` contains a dispatch-table row whose link target is `[[{slug} Status]]`.

**Check pattern:** grep `{slug} Track.md` for `\[\[{slug} Status\]\]`.

**Why:** the Status file should be one click away from the anchor's main Track surface. Otherwise users (and the agent) don't discover it.

### RULE R-status-10 — Cell promotion is monotonic up the ladder (stated)

The state script's `set` operation does not allow downgrading a cell (e.g., `MVP-user` → `MVP-agent`). Resetting to `none` IS allowed but requires an explicit `--reset` flag (script-side; not user-facing).

**Check pattern:** state script enforces; audit would inspect git history for downgrade-without-reset moves.

**Why:** progress is one-way; if scope changes enough to warrant a downgrade, the user should explicitly reset and re-grade rather than silently downgrade.
