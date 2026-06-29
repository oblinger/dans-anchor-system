---
description: "product requirements — what `/architect` produces and for whom"
---

# Architect PRD

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[Architect Design]] → PRD

## Overview

`/architect` creates and maintains the **top-level architecture document** for an anchor — the single page that decomposes a system into subsystems and shows how they fit together. Architecture lives in `{NAME} Design/`: a single `{NAME} Architecture.md` by default, upgraded to a `{NAME} Architecture/` folder-doc once it grows subsystems. The skill reads **module docs as ground truth**, rolls them up into a decomposition (subsystems → components → boundaries), and keeps a **bidirectional `module ↔ arch` link** (an `Arch` row in each module doc's dispatch table) so the architecture and the modules never drift apart.

Per [[SKA Decisions|D10]], `/architect` is the **behavioral core of the [[FCT Design]] facet**: an anchor's `{NAME} Design/` folder existing ⟺ the anchor has been *architected* — its design is the artifact `/architect` walks for completeness. (The asymmetry with Track/Workflow — Design→*skill*, Track→*discipline* — reflects periodic architecting vs. continuous tracking.)

## Goals

- **G1 — One canonical architecture per anchor.** Produce and maintain a single top-level architecture doc that decomposes the system into subsystems, each with a dispatch table, a mandatory summary table, an optional figure, and a module list.
- **G2 — Module docs are ground truth.** Roll the architecture up *from* module docs; never let the architecture assert a structure the modules contradict. Maintain the bidirectional `module ↔ arch` link.
- **G3 — Grow without breaking links.** Single-file by default; upgrade top-level doc or any subsystem to a same-named folder-doc when discussion outgrows one file, keeping every `[[...]]` link transparent across the upgrade.
- **G4 — Portable bare-project mode.** `/architect overview <subject>` produces a self-contained `Architecture/` folder (overview + hand-drawn SVG) for *any* codebase — no anchor, no vault required (per [[F184 — Skill portability — architect bare-project mode + environment gating|F184]]).

## Non-Goals

- **Not tracking.** Backlog/feature state is unified at SKA ([[SKA Decisions|D08]]); the architecture doc records *what is*, not *what's in flight*.
- **Not the design dispatch.** The Design-pipeline ordering and folder shape belong to [[FCT Design]] / [[FCT Design Docs]]; `/architect` maintains the Architecture artifact within that shape.
- **Not per-file documentation.** The output is an architecture-level decomposition (a handful of subsystems), not a per-file inventory.

## User Stories

- **US1 — Architect an anchor.** *As a maintainer, I run `/architect` on a CAB anchor and get a top-level architecture doc rolled up from its module docs, with bidirectional links back to each module.*
- **US2 — Keep it current.** *As a maintainer, after changing modules I run `/architect update` and the architecture reconciles to the new module reality (staleness precondition, `Arch`-row reconciliation).*
- **US3 — Overview any repo.** *As a colleague with only the cloned skills, I run `/architect overview .` on a plain codebase and get a diagrammed architecture overview, no vault or anchor needed.*

## Success criteria

The architecture doc decomposes the anchor into named subsystems; every module doc carries an `Arch` row resolving to it and vice versa; `/audit architecture` is clean on a vault anchor; and `/architect overview` runs to a written `Architecture/` folder on a bare repo with no vault-coupled step firing.

## Composition

`/architect` (full, vault/anchor) · `/architect update` (reconcile to module changes) · `/architect overview <subject>` (portable bare-project mode, [[F184 — Skill portability — architect bare-project mode + environment gating|F184]]). Sub-action docs: [[architect-new]], [[architect-update]], [[architect-changes]], [[architect-drift]], [[architect-overview]]. Full runbook: [[architect/SKILL|SKILL.md]]; user-facing docs: [[SKL Architect]].
