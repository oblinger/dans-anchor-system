# RULESET R-agenda
include::
where:: `file:{anchor}/**/* Agenda.md, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog (a `DAS <Name>.md` is the SPEC for the facet, not an instance; specs are governed by [[R-facet-spec]]). Standalone `FEX <Name>.md` teaching artifacts under `examples/` satisfy the content rules but are exempt from the location rules R-agenda-02 / R-agenda-09 — they belong to no project world and so have no Track folder or dispatch page (per [[DAS Facet]] § Examples of a facet).
description:: Structural rules for the {slug} Agenda.md facet doc; enforces location, the five required H2s and their order, the stated-interval Cadence, and the no-work-rows discipline.

Ruleset for the Agenda facet — spec: [[DAS Agenda]]. Adopted via the `R-facet` umbrella. Sibling of [[R-backlog]] / [[R-status]] in the Tracking group.

### RULE R-agenda-01 — File name `{slug} Agenda.md` (checked)
check:: agenda_filename_valid

The agenda file is named `{slug} Agenda.md` — anchor slug + space + `Agenda.md`. No qualifier suffix.

**Check pattern:** the file's basename matches `^{slug} Agenda\.md$`; no alternate `Strategy.md` / `Plan.md` / `{slug} Agenda 2026.md` alongside.

**Why:** the Track-dispatch wiring, the audit, and any future `/create facet agenda` all assume this exact name. Aliases make the facet undetectable.

### RULE R-agenda-02 — Lives under `{slug} Track/` (checked)
check:: agenda_in_track_folder

The Agenda file lives inside the Track folder, NOT the Design folder, NOT the anchor root.

**Check pattern:** path matches `{anchor}/{slug} Track/{slug} Agenda.md`, or the folder-doc form `{anchor}/{slug} Track/{slug} Agenda/{slug} Agenda.md`.

**Why:** Agenda is tracking metadata about the *activity* — strategy the tactical layers execute — not design content about the artifact. Placing it in Design collapses the Track ⟺ Design boundary that [[DAS Track]] establishes.

### RULE R-agenda-03 — Cardinality 0-or-1 per anchor (checked)
check:: agenda_single_per_anchor

At most one Agenda exists under any one anchor. No sub-Agendas for sub-activities.

**Check pattern:** count files matching `* Agenda.md` under the anchor root (excluding nested anchors); assert ≤ 1.

**Why:** a second Agenda means two competing theories of victory for one activity, with nothing to say which governs. When a big-chunk activity splits, the sub-activities get their own anchors — and each of those gets its own single Agenda.

### RULE R-agenda-04 — The five required H2s are present (checked)
check:: agenda_required_h2s

The file contains all five required H2 headers: `## Purpose`, `## Success — what "won" looks like`, `## Approach`, `## Constraints`, `## Cadence`.

**Check pattern:** grep for each of the five `^## ` headers; all five must match. `## Success` matches on its `Purpose`-style prefix (`^## Success`), tolerating a reworded tail.

**Why:** the five sections are the facet's whole content contract — why / what winning is / how / what limits us / when we revisit. A file missing one of them is a note about an activity, not an Agenda.

### RULE R-agenda-05 — Required H2s appear in declared order (checked)
check:: agenda_h2_order

The five required H2s appear in this order: Purpose → Success → Approach → Constraints → Cadence. Optional H2s (`## Open Questions`, `## History`, `## Links down`) follow them.

**Check pattern:** extract `^## ` headers in file order; the subsequence of required headers matches the declared order.

**Why:** the order is an argument — purpose motivates the success definition, which the approach targets, which the constraints bound, which the cadence maintains. Shuffling it makes the document read as a list of headings rather than a case.

### RULE R-agenda-06 — `## Cadence` names an interval (sampled)
check:: agenda_cadence_stated

The `## Cadence` section body names a revisit interval (weekly / monthly / quarterly / annually, or an explicit period) and who performs the revisit.

**Check pattern:** the section body matches an interval token (`weekly|monthly|quarterly|annual|every \d+ (day|week|month)s?`).

**Why:** an Agenda has no execution forcing-function — nothing pings it the way a Backlog gets pinged by work. The stated interval is the only thing that keeps it from silently rotting into a misleading document.

### RULE R-agenda-07 — No workflow rows (checked)
check:: agenda_no_work_rows

The Agenda contains no bracketed workflow rows and no work-item block anchors.

**Check pattern:** absent — `\[(Ready|Active|Blocked|Verify|Done|Questions|Waiting|Watching|Designing|Implementing)\]` and `\^[FT]\d{3}`.

**Why:** Agenda is strategy; the work queue is the [[DAS Backlog|Backlog]]. Rows here would be invisible to `state`, absent from `Q.md`, and unreachable by `/groom` and `/crank` — work that looks tracked but is not.

### RULE R-agenda-08 — Frontmatter `description:` plus `# {slug} Agenda` H1 (checked)
check:: agenda_header_shape

The file opens with YAML frontmatter carrying a `description:` key, followed by an H1 of the form `# {slug} Agenda`.

**Check pattern:** first line is `---`; the block contains `^description: `; the first `^# ` header matches `^# {slug} Agenda$`.

**Why:** ordinary [[DAS Doc Structure]] shape — the description drives search and dispatch-table rendering, and the slug-matched H1 keeps the file identifiable when opened out of context.

### RULE R-agenda-09 — Track dispatch links to the Agenda file (checked)
check:: agenda_track_dispatch_linked

`{slug} Track.md` contains a dispatch-table row whose link target is `[[{slug} Agenda]]`.

**Check pattern:** grep `{slug} Track.md` for `\[\[{slug} Agenda`.

**Why:** an elective facet that nothing links to is a file the next agent will never open. The Track dispatch page is the one surface guaranteed to be read.

### RULE R-agenda-10 — Elective; never scaffolded by default (stated)

`/create anchor` does not create an Agenda. The facet is added deliberately, when the § When appropriate gates in [[DAS Agenda]] are met.

**Check pattern:** none mechanized — this constrains the scaffolding tools, not the instance. Audit would flag an anchor tree where every anchor carries an empty template-shaped Agenda.

**Why:** the standing failure mode for a new facet is universal adoption by scaffolding, which converts a meaningful signal ("this activity has a strategy worth writing") into boilerplate noise on every anchor.

### RULE R-agenda-11 — Approach carries theory, not milestones (stated)

`## Approach` states the theory of victory. Sequenced milestones belong in [[DAS Roadmap]]; individual steps belong in [[DAS Backlog]].

**Check pattern:** none mechanized — a sampled read flags an `## Approach` section that is a numbered milestone list with dates.

**Why:** this is the observed drift direction between the two facets. Once milestones live in the Agenda, the Roadmap becomes redundant and the strategy becomes invisible — the exact collapse the facet exists to prevent.
