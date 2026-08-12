---
name: electric-zone
description: "Slot facet. The electric zone is everything below a dispatch table's separator — a region defined by position and ownership alone, whose content has no shape of its own because the machine recomputes it."
user_invocable: false
group: slot
---

| -[[DAS electric-zone]]- | : Slot facet. The electric zone is everything below a dispatch table's separator — a region defined by position and ownership alone, whose content has no shape of its own because the machine recomputes it.<br>→ [[DAS]] → [[disciplines]] → [DAS electric-zone](hook://p/DAS%20electric-zone)  |
| --- | --- |
| Related | [[DAS Dispatch Table]],  [[DAS spine]],  [[DAS Facet]] (§ Facet groups),  [[DAS Disciplines\|Disciplines]],  [[DAS\|dans-anchor-system]], |
| Rules | [[R-dispatch-table]],  [[R-spine]],   |
| Examples | [[Harbor Hops\|list zone]],  [[Harbor Releases\|stream zone]],  [[Bridges\|near-empty catchall]],   |

# Electric-zone Discipline
Everything below a dispatch table's separator belongs to the machine — a region identified by position and ownership alone, never by anything it contains.

| | Above the separator | **Below it — the electric zone** |
|---|---|---|
| **Owner** | the author | **HookAnchor** |
| **Source of truth** | the row as written | **the command store** |
| **Lifetime of an edit** | permanent | **~30 seconds** |
| **Shape** | the row vocabulary | **none — whatever the store computes** |

**Cardinality: many** — any number of pages carry one, and a page carries one per dispatch table.

This is the one slot in the family whose specification is almost entirely about **custody**. The spine has shapes, the heart has two forms, the orientation line has a role; the electric zone has no shape at all, and asking what belongs in it is the wrong question. What belongs in it is *whatever the machine last computed*, and the only authorable thing about it is the separator that opens it.

## Position and ownership are the whole definition
A **separator row** — `...`, `| --- | |`, or the `+++` / `^^^` / `!!!` variants — divides the table. Rows above it are the author's. Everything below is recomputed from the command store on every rebuild, about 30 seconds after the page stops changing. The marker vocabulary and what each one renders belong to [[DAS Dispatch Table]] § Electric zones; **this page deliberately does not restate them**, because a second copy of a marker list is exactly how the two would drift.

Two consequences follow from custody alone, and both are counter-intuitive enough that they are the reason this facet is worth writing down:

- **Anything typed into the zone is discarded** — not merged, not flagged, silently overwritten on the next rebuild.
- **A link missing from a `...` catchall is not damage.** The catchall deliberately omits any child the page already links *anywhere in its text, prose included* — F081 body-mention suppression. [[WIRE]]'s intro names `[[WIRE Muse]]` in a sentence, so `WIRE Muse` is correctly absent from its catchall row.

## The failure this facet exists to prevent
**Restoring a "missing" link is the trap, and it has caught three separate agents.** The hand-added link appears to work, then vanishes about thirty seconds later with nothing running and no explanation. That reads exactly like corruption, and it has produced **three wrong bug reports from three different agents** — filed variously as a Warden bug, an Obsidian stale-buffer bug, and a daemon-cache bug. It was none of those. It was the zone doing its job. Confirmed as correct behaviour by the user, 2026-08-05.

That history is the whole argument for a spec. The mechanism is simple and the *symptom* is indistinguishable from a serious defect, so an agent reasoning from first principles at the moment it happens will reliably reach the wrong conclusion — three did. What stops it is knowing beforehand that the zone is not yours.

**To change what appears, change the source** — the file's location, its command, or a row *above* the separator. Never the zone itself.

**The rule is deliberately duplicated at `~/ob/kmr/CLAUDE.md`**, so every agent working anywhere in the vault loads it whether or not they ever read this facet or [[DAS Dispatch Table]]. That duplication is a considered exception to single-source-of-truth: the cost of a stale copy is a wording drift, and the cost of *not* loading it is a wrong bug report against three different subsystems.

## How it is checked
No ruleset of its own. [[R-dispatch-table]] owns the table's interior — which markers are legal, where the separator may sit, what each zone renders — and [[R-spine]] owns whether a folder-fronting page owes a marker at all (`S07`, `S08`, `S09`). Splitting custody further would put two authorities over one region, which [[DAS heart]] gives the general argument against.

**The zone's own correctness is not checkable from the document**, and that is structural rather than a gap: the zone is correct exactly when it matches what the command store computes, so the document cannot be graded against itself. Every check in this area is therefore about the *frame* — is there a separator, does the page owe one, is anything above it that should be below. HookAnchor logs each suppression it applies (`DISPATCH catchall on '<anchor>': N child(ren) omitted`) to `~/.config/hookanchor/hookanchor-<date>.jsonl`, and that log — not the rendered table — is where a suspected omission is confirmed or refuted.

## Why this is a slot facet
It is a **region inside a file**, with a start (the separator) and an end (the table's end), appearing in documents of many kinds. That is the slot group's definition ([[DAS Facet]] § Facet groups).

It reads as a discipline in the `where::` grammar for the same reason [[DAS spine]], [[DAS heart]] and [[DAS orientation-line]] do — the grammar cannot express a **positional** region, so the governing rulesets fall back to `` `always` `` and the group is carried by this declaration instead. The file sits in `disciplines/` beside its siblings; the folder is not the taxonomy.

**It is the one member of that family with no template**, which is worth stating because the template test is what usually separates a slot from a discipline. The absence here is not a missing artifact: a template describes what an author should write, and nobody authors this zone. What it has instead — a defined extent and a named owner — is enough, and the group turns on the extent rather than on the template.

# BRIEF

*(Maintainer note — cautions for editing this spec.)*

- **Never demonstrate the zone by editing one.** The obvious way to check a claim here is to add a row and watch — which silently reverts thirty seconds later and teaches the wrong lesson to whoever reads the file next. Confirm against the HookAnchor log instead.
- **Do not restate the marker vocabulary.** [[DAS Dispatch Table]] § Electric zones owns which markers exist and what each renders; this page owns position and custody. A marker list copied here is the drift this split exists to prevent.
- **Do not mint `R-electric-zone`.** The frame checks already live in [[R-dispatch-table]] and [[R-spine]], and the zone's contents are not gradable from the document at all — a ruleset would have nothing to check that is not already checked.
- **The `CLAUDE.md` duplicate is intentional.** If this page's wording changes materially, update `~/ob/kmr/CLAUDE.md` in the same pass; do not "fix" the duplication by deleting one side.
