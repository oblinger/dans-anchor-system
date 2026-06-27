---
description: Common Anchor Example — reference anchor — a fully-wired example of the canonical CAB structure
---
# CAE — Common Anchor Example

CAE is a self-contained reference anchor that demonstrates the canonical CAB structure by showing exactly what each file type looks like in a fully-wired Code-trait project.

| -[[CAE]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [CAE](hook://p/CAE)<br>: Common Anchor Example — reference anchor — a fully-wired example of the canonical CAB structure |
| --- | --- |
| Related | [[CAB]],  [[SKA]],   |
| [[CAE Design\|Design]] | [[CAE PRD\|PRD]],  [[CAE UX Design\|UX Design]],  [[CAE CLI\|CLI]],  [[CAE API\|API]],  [[CAE Architecture\|Architecture]],  [[CAE Decisions\|Decisions]],  [[CAE Testing\|Testing]],  [[CAE Roadmap\|Roadmap]],  [[CAE Features\|Features]],   |
|  |  |
| Examples | [[CAE Facet\|Facet]],  [[CAE Skill\|Skill]],  [[CAE Project Root\|Project Root]],  [[CAE Grouped Dispatch\|Grouped Dispatch]],  [[CAE List Dispatch\|List Dispatch]],  [[CAE Figure Page\|Figure Page]],  [[CAE Dispatch Examples\|Dispatch Examples]],  [[CAE Minimal Facet\|Minimal Facet]],  [[CAE Minimal Skill\|Minimal Skill]],   |
| External |  |
|  | [[CAE-Scheduler\|Scheduler]],   |
| [[CAE User Docs\|User Docs]] | [[CAE Guide\|Guide]],   |
| [[CAE Dev Docs\|Dev Docs]] | [[CAE Files\|Files]],   |



## Overview

CAE is the **Common Anchor Example** — a self-contained reference anchor whose purpose is to demonstrate the canonical CAB structure. Every file here shows the correct format for its type. CAB specs (in `skills/CAB/cab-facets/`) describe *what each piece is and why*; CAE shows *exactly what the files look like*.

The content below the structural level is illustrative. CAE's fictional project is a simple CLI scheduler — enough domain to give the PRD, System Design, and module docs realistic content to demonstrate.

CAE shows a **Code-trait** anchor. For a worked example of a **Skill-trait** anchor — `SKILL.md` at the root, no code repo, user docs in the parallel SKL tree — see [[CSE]] (Common Skill Example).



## Design Principles

Canonical statements live in [[CAE Decisions\|CAE Decisions § Principles]]. This page names them for quick scanning.

- **[[CAE Decisions#D01 — One Queue, One Clock (sampled)\|D01]]** — one queue, one clock
- **[[CAE Decisions#D09 — Fail Loudly, No Silent Fallbacks (checked)\|D09]]** — fail loudly, no silent fallbacks
- **[[CAE Decisions#D03 — Deterministic Tests (sampled)\|D03]]** — deterministic tests

Writing the principle once (in Rules) and referencing it by ID everywhere else keeps the single source of truth and eliminates drift.

# BRIEF

- **This page is the CAE anchor head — a reference exemplar, not a real project.** Edits here demonstrate the canonical CAB anchor-page shape (dispatch table, Overview, Design Principles); they teach by example.
- **Scope is structural fidelity, not domain depth.** The fictional CLI-scheduler content exists only to give the dispatch rows realistic referents; do NOT expand the scheduler domain here — domain content belongs in the linked sub-docs ([[CAE PRD]], [[CAE Architecture]], etc.).
- **Inclusion test for a dispatch row:** the row must point at a file/folder that itself exemplifies a canonical CAB facet or zone (Design, Architecture, User Docs, Dev Docs, Track). Do not add rows for one-off content that wouldn't appear in a real anchor.
- **Mirror, don't invent.** When CAB facet specs change (in `Skill Agent/CAB/`), reflect the new shape here; do NOT pioneer new structural conventions in CAE — it follows CAB, never leads it. Cross-trait counterpart is [[CSE]] (Skill-trait); keep the two aligned in structure where applicable.
-[[CAE]]-	: Common Anchor Example — reference anchor — a fully-wired example of the canonical CAB structure
[[CAE Design|Design]] — design — system spec, architecture, principles
[[CAE Dev Docs|Dev Docs]] — source file tree and per-module reference for CAE (audit-tied implementation docs)
[[CAE Dispatch Examples|Dispatch Examples]] — Worked examples of the dispatch-table structure (Masthead + Member zone) — real, live anchor pages demonstrating each alternative. Per CAB Dispatch Table § Structure.
[[CAE Facet|Facet]] — Canonical facet exemplar — the structure every FCT facet page follows, worked with the Design facet. Roll this out to all facets.
[[CAE Figure Page|Figure Page]] — Worked example — an anchor page WITH a figure: the canonical progressive-disclosure ordering (H1 → one-liner → figure → dispatch table).
[[CAE Grouped Dispatch|Grouped Dispatch]] — Canonical grouped-dispatch exemplar — a Collection with > 15 members, grouped, each group row linking down to its own container page. Roll out to grouped anchors.
[[CAE List Dispatch|List Dispatch]] — Canonical list-dispatch exemplar — a small Collection (≤ 15 members), flat member list, one row per member. Roll out to small grouped anchors.
[[CAE Minimal Facet|Minimal Facet]] — The minimal-facet capsule — the leanest complete file set for a CAB facet, with a live worked instance. Lazy, no empty stubs.
[[CAE Minimal Skill|Minimal Skill]] — The minimal-skill capsule — the leanest complete file set for a skill, keeping design thinking out of the published repo. Lazy, no empty stubs.
[[CAE Project Root|Project Root]] — Canonical project-root exemplar — the {NAME}.md anchor page for a designed software project (masthead-only; structural rows, no member zone). Roll out to project anchors.
[[CAE Skill|Skill]] — Canonical skill exemplar (SKILL.md). Capture a screenshot, file it with a generated title, and drop a transcribed note beside it. Use when the user says '/snap', 'grab a screenshot', 'snap this'. Roll this structure out to all skills.
[[CAE Track|Track]] — work tracking + planning
[[CAE User Docs|User Docs]] — curated, synthesis-level docs for any human audience
