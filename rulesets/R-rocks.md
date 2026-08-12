# RULESET R-rocks
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file:{anchor}/**/* Rocks/**, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog (a `DAS <Name>.md` is the SPEC for the facet, not an instance; specs are governed by [[R-facet-spec]]). The vault-wide `LST/Rocks/` is **not** an instance of this facet — it is the top-level compilation surface across life-areas, has no owning `{slug} Track/`, and is governed by its own Brief; the `{anchor}/**/` prefix in the `where::` excludes it because its folder is not named `{slug} Rocks`.
description:: Structural rules for the Rocks facet folder; enforces location, folder-note presence, the catch-all, short abbreviation-style rock names with their expansions, tier-line integrity, and the no-work-rows discipline.

Ruleset for the Rocks facet — spec: [[DAS Rocks]]. Armed by [[R-anchor]]'s `include::` — the umbrella `/audit anchor` resolves. Being named by [[R-facet]] is catalog membership, not adoption — that umbrella sits outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so an `include::` there arms nothing ([[TINK Backlog#^T208|T208]]). Sibling of [[R-agenda]] / [[R-backlog]] / [[R-status]] in the Tracking group.

**Instance test.** The facet is elective (R-rocks-10), so a folder counts as an instance only when the anchor has evidently adopted it: a folder named `{slug} Rocks/` for its **owning** anchor, sitting under that anchor's `{slug} Track/`. Both halves are load-bearing — the name test is what lets R-rocks-02 fire on a `{slug} Design/{slug} Rocks/`, and the location test is what lets R-rocks-01 fire on a `{slug} Track/{slug} Big Rocks/`. Note that `{slug} Track/` carries its own `.anchor`, so the checkers resolve past the facet sub-anchor to the project that owns it before reading a slug.

### RULE R-rocks-01 — Folder name `{slug} Rocks/` with a folder-note of the same name (checked)
check:: rocks_folder_named

The facet materializes as a folder named `{slug} Rocks/` — anchor slug + space + `Rocks` — containing a folder-note `{slug} Rocks.md`. No qualifier suffix, no singular form, no flat `{slug} Rocks.md` sitting alone in Track.

**Check pattern:** the folder's basename matches `^{slug} Rocks$` and it contains a file named `{slug} Rocks.md`; no alternate `{slug} Big Rocks/` / `{slug} Rock/` / `{slug} Priorities/` alongside.

**Why:** the Track-dispatch wiring, the audit, and any future roll-up into the vault-wide [[Rocks]] all assume this exact name. The facet is a folder rather than a file because the ranked list and the per-rock explanations are different things at different sizes; a flat file collapses them.

### RULE R-rocks-02 — Lives under `{slug} Track/` (checked)
check:: rocks_in_track_folder

The Rocks folder sits inside the Track folder, NOT the Design folder, NOT the anchor root.

**Check pattern:** path matches `{anchor}/{slug} Track/{slug} Rocks/`.

**Why:** what the user is spending effort on is metadata about the *activity*, not design content about the artifact. Placing it in Design collapses the Track ⟺ Design boundary that [[DAS Track]] establishes — and would put it beside [[DAS Roadmap|Roadmap]], which is the neighbour it is most often confused with.

### RULE R-rocks-03 — Cardinality 0-or-1 per anchor (checked)
check:: rocks_single_per_anchor

At most one Rocks folder exists under any one anchor. No sub-Rocks for sub-activities.

**Check pattern:** count folders matching `* Rocks` under the anchor root (excluding nested anchors); assert ≤ 1.

**Why:** two ranked lists for one anchor means two answers to "what are the big chunks here" with nothing to say which governs. When an activity splits, the sub-activities get their own anchors, and each gets its own single Rocks folder.

### RULE R-rocks-04 — Rock names are short, and the abbreviation is expanded in the file (retired)

**Unwired 2026-08-11, on the trigger this note itself set.** The retirement below kept `check:: rock_name_short_and_expanded` attached, reasoning that it self-disables on a numbered name and still judged unmigrated groups. **Every group has now migrated** — measured 2026-08-11 across all four `* Rocks/` folders in the vault (`AIS` 3, `HBR` 3, `MED` 1, `VEC` 1): eight rock files, eight matching `{slug} R\d{4}`, zero abbreviation-named. So the checker had nothing left to judge, and leaving it wired was doing active harm rather than nothing — see below.

**Leaving it wired silently disabled `R-rocks-03`.** `_RULE_RE` admits exactly four tiers — `checked`, `sampled`, `stated`, `tracked` — and `(retired)` is not among them, so the parser skipped this heading and folded the `check::` line beneath it onto the previous rule. `R-rocks-03` (cardinality, `rocks_single_per_anchor`) therefore ran **this** rule's checker and reported *"name is 'R0001' — not an abbreviation, nothing to expand"* as its own verdict: green on every rock group, having never been evaluated. **This is the second time this exact fold has happened in this exact ruleset** — the T156 note in `audit-plan.py` records `RULE R-rocks-05` headed `(checked, warn)` folding onto rule 04 for the same reason. It recurs because a malformed tier makes a rule invisible to the very checks that would catch it, and because `R-ruleset-06` (*every rule has a tier annotation*) reads `(checked)` while carrying no `check::` line — its implementation `chk_all_rules_have_tier` exists, is registered, and is invoked by nothing. Reported to [[TINK|Tink]] 2026-08-11, who owns `R-ruleset` and the tier vocabulary; unwiring here is the half that is Stone's to fix.


**Retired 2026-08-10, superseded by `R-stone-02`** — a rock file is named `{slug} R{NNNN}.md`, monotonic and never recycled, and its expansion is simply the file's H1. The checker stays wired because it self-disables on a numbered name (*"not an abbreviation, nothing to expand"*) and still judges the abbreviated files that have not been migrated. It becomes genuinely inert once the last group converts, and should be unwired then rather than left reading as coverage.

The superseded rule follows, for the anchors still shaped that way.

A rock file is named `{slug} {ABBR}.md`, where `{ABBR}` is **at most two words** — normally one word, or an acronym when the rock's real name is multi-word. The expansion appears in the file's H1 orientation line or its `description:` frontmatter.

**Check pattern:** for each member file other than the folder-note, strip the `{slug} ` prefix and assert the remainder is ≤ 2 whitespace-separated words — an error. Then, when the remainder is all-caps or mixed-caps of ≤ 5 characters, assert the `description:` or the orientation line under the H1 **opens with a gloss** — a short phrase ahead of an em dash, saying something other than the rock's own name — and warn when it does not. Whether that phrase is the *correct* expansion is deliberately not mechanized: `HR` → *historical retrospective* is an acronym, but `TX` → *transcode*, `OBS` → *observability* and `LEX` → *life expectancy* are contractions, and no initials, prefix or subsequence test admits all four (`transcode` has no `x`). That half is a reader's judgment, and the warning is where it gets raised.

**Why:** the wiki-link is the reusable unit and it is reused in a narrow line — `[[HBR R0001|HBR:]] gather stats`, where the words after the colon carry the only current information. A long link crowds them out. The expansion requirement is the price of the abbreviation: a reader who does not recognize `HR` must be able to learn it by opening the file, and nowhere else.

### RULE R-rocks-05 — Every member appears on a tier line (checked)
check:: rocks_member_ranked

Every rock file in the folder is named on some line of the ranked list. Emitted as a **warning**, not an error.

**Where the ranked list is:** the **control file** `{slug} Rock.md`, in `{slug} Track/` beside the folder (per [[DAS Stone]]). It used to be the folder-note itself; the checker reads the control file when one exists and falls back to the folder-note for groups not yet migrated, so both shapes are judged correctly during the changeover.

**Check pattern:** collect member basenames; collect wiki-link targets in the control file (or, absent one, below the folder-note's dispatch table); assert every member is among them.

**Why:** a rock nobody has ranked is a real state and a transient one — the file lands first, the ranking follows. The warning is the cleanup pressure, not a gate. This is also why the folder-note carries a `...` catch-all: an unranked rock must still be reachable.

### RULE R-rocks-06 — No dead tier lines (checked)
check:: rocks_tier_links_resolve

Every tier line naming one of **this group's** rocks resolves to a file that exists.

**Where the ranked list is:** the **control file** `{slug} Rock.md`, exactly as in R-rocks-05 — read when present, falling back to the folder-note for groups not yet migrated.

**Check pattern:** for each tier line — a line opening with a wiki-link, the `[[HBR R0001|HBR:]] gather stats` form — assert that leading link's target resolves. Leading only, and this group's own only. Three shapes are deliberately not judged, each because a local resolver cannot see it: a promotion marker (`**Elevated to [[Rocks]]**`, R-rocks-13), a **header** whose leading link targets a control file (R-stone-04), and a line naming **another anchor's** stone, which under [[DAS feed]] is what a propagated line is.

**Why:** the ranked list is the surface people read and cite from; a link that goes nowhere makes the list untrustworthy at exactly the moment someone is trying to act on it. The vault-wide [[Rocks]] page carried five such rows for months, which is the failure this rule generalizes.

**This rule judged nothing at all between the Stone migration and 2026-08-11.** [[DAS Stone]] moved the ranking to the control file and R-rocks-05's checker moved with it; this one kept opening the folder-note, found **0 tier lines where 12 existed**, and reported pass on all four live groups. Green because it was reading the wrong file is indistinguishable from green because the links resolve — and it is the **third** silent stop in this ruleset, after the two parser folds R-rocks-04's note records. Fixed with a fire test, `test-f312-rocks-tier-control-file.py`, whose import-site case caught the fix's own landmine: judging propagated foreign lines would have traded a vacuous pass for a false failure on the first anchor to actually use the feed DAG.

### RULE R-rocks-07 — No work rows inside a rock file (checked)
check:: rocks_no_work_rows

Rock files carry no bracketed workflow rows (`[Ready]`, `[Active]`, `[Blocked]`, …), no `^F<n>` / `^T<n>` block anchors, and no minted F-numbers.

**Check pattern:** grep member files for the bracket grammar and for `^[FT]\d+` block anchors; assert none.

**Why:** a rock is a thinking surface, not a queue. When a rock becomes executable it spawns backlog rows and feature docs and links **to** them. Two surfaces both claiming to be the work queue is how a work queue rots — the same reason [[DAS Agenda]] forbids it.

### RULE R-rocks-08 — Dispatch linkage from `{slug} Track.md` (checked)
check:: rocks_dispatch_linked

`{slug} Track.md` carries a row linking `[[{slug} Rocks]]`.

**Check pattern:** grep the Track dispatch page for a wiki-link to the folder-note; assert present.

**Why:** the folder is elective, so nothing else guarantees it is reachable. An unlinked Rocks folder is invisible to anyone navigating the anchor and to the catch-all of any page above it.

### RULE R-rocks-09 — The folder-note carries a catch-all separator (checked)
check:: rocks_folder_note_catchall

The folder-note's dispatch table includes a `...` catch-all row, so a file dropped into the folder is surfaced without being hand-listed.

**Check pattern:** assert a `| ... |` separator row is present in `{slug} Rocks.md`.

**Why:** the catch-all is what makes R-rocks-05 a warning rather than an error — nothing is ever lost, only unranked. Without it, an unranked rock is genuinely invisible and the warning would have to become a gate.

### RULE R-rocks-10 — Elective; never scaffolded (stated)

No anchor is required to have a Rocks folder, and `/create anchor` never scaffolds one. It is created when an anchor actually has more than one big chunk worth naming.

**Check pattern:** stated; a Rocks folder containing only a folder-note and no rocks is a smell to flag.

**Why:** the failure mode of every new facet is universal adoption by scaffolding, which produces hundreds of empty folders and trains readers to skip the facet everywhere — including where it is real.

### RULE R-rocks-11 — Tier grouping expresses commitment, not sequence (stated)

The ranked list groups rocks by **commitment level**. Ordering within a group carries no promise, and the list is not a plan. The specific tier vocabulary and layout are deliberately unspecified — [[HBR Rock]] is the normative demonstration.

**Check pattern:** stated; dates, dependency arrows, or an explicit ordinal sequence appearing on tier lines are a smell to flag.

**Why:** the one property that makes Rocks its own facet is that a rock may be listed without being committed to. Sequencing belongs to [[DAS Roadmap]]; the moment tier lines acquire dates and dependency order, the anchor has grown a second Roadmap and lost the ability to name an uncommitted chunk.

### RULE R-rocks-12 — Every rock is owned by this anchor (stated)

Every rock file in this folder belongs to *this* folder's anchor. A rock that belongs to a sub-anchor lives in that sub-anchor's own Rocks folder, not here. A cross-cutting rock is placed in the most plausible anchor — never left unowned.

**Check pattern:** stated; a rock file whose subject is evidently another anchor's work is a smell to flag.

**Why:** the facet is one node of a tree whose root is the vault-wide [[Rocks]], and the root's whole discipline is that it never holds an unowned rock. Ownership has to be true at every node for the root's guarantee to mean anything. Ratified 2026-08-06 ([[VEC Journal]]).

### RULE R-rocks-13 — Promotion is marked in both directions (stated)

When a rock is promoted to a higher node — another anchor's Rocks folder, or the root [[Rocks]] — its entry here says so and links where it went, e.g. `**Elevated to [[Rocks]] 2026-08-06.**` The receiving row links back to this rock.

**Check pattern:** stated; a rock named on a higher node with no corresponding marker here is a smell to flag.

**Why:** round-trip traceability is the whole difference between a tree and a set of nested lists. Only the here-side of the round trip is in scope for this ruleset — the root is not an instance of this facet (see [[DAS Rocks]] § The root is not an instance), so the there-side is honored by whoever owns that node.
