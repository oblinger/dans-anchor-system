# RULESET R-at-entity
include:: [[R-stream]] 
where:: `file:{anchor}/**/@*.md`
description:: the `@`-prefixed entity page — placement, forms, and which of three containers an entry belongs in
selector-note:: **This set is deliberately not armed.** It is named in no `include::` on [[R-anchor]] or [[R-doc]], so it enters no plan and fires on nothing — intentional while [[DAS At Entity]] § Unsettled is open, because arming it would meet a 655-page corpus with a wall of findings for a shape its owner has not ratified. The consequence is the one [[DAS Facet]] § names: a green audit is **not** evidence of at-entity conformance. Arm it by naming it in [[R-anchor]], and measure the blast radius in the same pass.

What `/audit` would check on an `@`-prefixed entity page. Spec: [[DAS At Entity]]. Cardinality: many per anchor. Format of this set: [[DAS Ruleset]].

**Scope boundary — placement and structure only.** The shape of a drafted *message* (the four blocks, the versioning, the no-markdown rule) belongs to [[AT Mail]], which states it as prose under a standing instruction not to hand-write a ruleset for it, because [[STEN|Stencil]] is meant to own the generate-and-check pair rather than have it stated twice. No rule below describes the inside of a `Drafted/` document.

### RULE R-at-entity-01 — An entity page is `@{Name}.md`, or `@{Name}/` with a namesake file (checked)

An at entity is detected by the leading `@` and takes one of two forms: a flat `@{Name}.md`, or a folder `@{Name}/` containing a namesake `@{Name}.md` of the identical name. Nothing else in the tree carries a leading `@`.

**Check pattern:** for each `@*` directory, a child file exists whose basename equals the directory name plus `.md`.

**Why:** the namesake rule ([[DAS file-association]]) is what makes flat→folder promotion link-safe — every existing `[[@{Name}]]` resolves unchanged.

### RULE R-at-entity-02 — Promotion to folder form is one-way (stated)

Once an entity is folder form it stays folder form; contents are never folded back into a flat file.

**Why:** folding back re-breaks the links the namesake rule protected, for no gain.

### RULE R-at-entity-03 — `Drafted/` and `Meet/` are spelled exactly, and only inside folder form (checked)

The two dated folders are named `Drafted` and `Meet` — title case, no slug prefix, no plural on `Meet`, no `Drafts` — and appear only as direct children of an `@{Name}/` folder.

**Check pattern:** no directory named `Drafts`, `Drafted`, `Meet`, `Meets`, `Meetings` appears under an at entity except the two sanctioned spellings, and neither appears outside an `@*/` parent.

**Why:** `Drafted` names provenance rather than state, which is what lets a sent message stay filed there; `Drafts` would make every sent item read as misfiled.

### RULE R-at-entity-04 — Entries in both folders use the dated stream filename (checked)

Every file directly under `Drafted/` or `Meet/` is named `YYYY-MM-DD — {topic}.{ext}`, per [[DAS stream]] § Dated entry-file naming (coarser `YYYY-MM — ` / `YYYY — ` forms allowed when precision is genuinely lower).

**Check pattern:** basename matches the stream date-prefix grammar with the em-dash separator.

### RULE R-at-entity-05 — One drafting thread per `Drafted/` document (stated)

A `Drafted/` file holds exactly one thread — the inbound message, the reasoning, every revision, and the final text of one back-and-forth — and a second thread with the same entity opens a second file.

**Why:** the thread is the unit a reader wants whole; splitting it across dated entries is the fragmentation this facet exists to end.

### RULE R-at-entity-06 — A `Drafted/` file is never renamed after creation (stated)

The date in the filename is the date the thread **opened**, and it stays that date however long the thread runs.

**Why:** renaming breaks every link into the document; the improved sort order is not worth that.

### RULE R-at-entity-07 — A meeting files under the meeting's main entity (stated)

A `Meet/` document lives under the one entity whose meeting it is — the person who called it, or the standing group that owns the recurrence — never duplicated across attendees. A recurrence with no single owning person gets a standing-group at entity of its own, `@`-prefixed like any other.

**Why:** a meeting has N attendees; without a main-entity rule it either gets copied N times or one attendee is elected arbitrarily.

### RULE R-at-entity-08 — Three containers, three exclusive tests (stated)

Every dated item on an at entity belongs to exactly one container, decided in order: drafted here → `Drafted/`; synchronous exchange → `Meet/`; otherwise → `# LOG`. A meeting's preparation, contemporaneous notes and after-notes all belong to that meeting's document.

**Why:** three containers with a fuzzy boundary cost more than one container, and the cost is paid on every new note.

### RULE R-at-entity-09 — `# LOG` is not emptied by the two folders (stated)

Migration must not assume `# LOG` becomes vestigial: relationship and status notes are the majority of the existing corpus (134 of 244 dated events measured 2026-08-20, against 29 correspondence and 56 meetings), and they stay. The migration selector is *"was this a drafting session?"*, which is strictly narrower than *"is this about email"* — a received message that was never drafted against does not move.

**Why:** stated as a rule because the wrong version of it is the natural assumption, and acting on it would move ~60% of the corpus into the wrong container.

### RULE R-at-entity-10 — The message format is not restated here (stated)

No rule in this set describes the interior of a `Drafted/` document. That shape lives in [[AT Mail]], singly.

**Why:** two statements of one shape is the drift both documents exist to avoid; see the scope boundary above.

### RULE R-at-entity-11 — A person page opens breadcrumb → identity H1 → card (checked)
check:: at_entity_person_opening
mend:: at-entity-opening

A flat person page (an `@*.md` that is not under `Corp/` directly and is not its folder's namesake) opens with a `:>>` breadcrumb — never a dispatch masthead, never a `...` — then an H1 of the form `# @{Name} — **[title](…) at [[@Org]]**`, then a `| Card |  |` table directly beneath carrying at least the **Contact** and **Rolodex** rows, and no `#pp` anywhere in the head. Specified at [[DAS At Entity]] § The opening; specimens [[@Henna Dattani]] and [[@Marguerite Vale]].

**Check pattern:** breadcrumb present and no identity-row masthead; H1 begins `# @{stem} —`; the first table under the H1 is headed `Card` and has `**Contact**` and `**Rolodex**` rows; no `#pp` token before the card → pass; each missing piece is named → **warn** (the register is mid-migration; promote when the sweep reads zero).

**Why:** 441 of 465 person pages carry the pre-2026-08-29 head line — tags, tab-aligned links, loose contact lines — which no checker could read and no reader could scan. The card is what makes a person page a page; this rule is what keeps 465 hand migrations honest.

### MEND at-entity-opening

Run `at-entity-migrate.py --dry <page>` to see what the migrator would write, then `--write`; hand-finish anything it reports as unparsed. The rows and their order: [[DAS At Entity]] § The opening.
