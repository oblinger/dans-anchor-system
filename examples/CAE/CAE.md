---
description: Common Anchor Example — reference anchor — a fully-wired example of the canonical CAB structure
---
# CAE — Common Anchor Example

CAE is a self-contained reference anchor that demonstrates the canonical CAB structure by showing exactly what each file type looks like in a fully-wired Code-trait project.

| -[[CAE]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [CAE](hook://p/CAE)<br>: Common Anchor Example — reference anchor — a fully-wired example of the canonical CAB structure |
| --- | --- |
| Related | [[CAB]],  [[SKA]],   |
| [[CAE Design\|Design]] | [[CAE PRD\|PRD]],  [[CAE Architecture\|Architecture]],  [[CAE Decisions\|Decisions]],  [[CAE UX Design\|UX Design]],  [[CAE CLI\|CLI]],  [[CAE API\|API]],  [[CAE Roadmap\|Roadmap]],  [[CAE Testing\|Testing]],  [[CAE Features\|Features]],   |
| [[CAE Track\|Track]] | [[CAE Backlog\|Backlog]],   |
| [[CAE User Docs\|User Docs]] | [[CAE Guide\|Guide]],   |
| [[CAE Dev Docs\|Dev Docs]] | [[CAE Files\|Files]],  [[CAE-Scheduler\|Scheduler]],   |

**Examples** — CAE doubles as the dispatch-form gallery (member zone):

| [[CAE Facet\|Facet]] | [[CAE Skill\|Skill]] | [[CAE Project Root\|Project Root]] | [[CAE Grouped Dispatch\|Grouped Dispatch]] | [[CAE List Dispatch\|List Dispatch]] |
| --- | --- | --- | --- | --- |
| [[CAE Figure Page\|Figure Page]] | [[CAE Dispatch Examples\|Dispatch Examples]] | [[CAE Minimal Facet\|Minimal Facet]] | [[CAE Minimal Skill\|Minimal Skill]] |   |



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
[[CAE Track|Track]] — work tracking + planning
[[CAE User Docs|User Docs]] — curated, synthesis-level docs for any human audience
