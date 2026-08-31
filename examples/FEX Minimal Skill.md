---
description: "the leanest complete file set for a skill, with a live instance"
---

| -[[FEX Minimal Skill]]- | : the leanest complete file set for a skill, with a live instance<br>→ [[DAS]] → [[FEX]] → [FEX Minimal Skill](hook://p/FEX%20Minimal%20Skill)  |
| --- | --- |
| Anchor | [[HBR]] (reference anchor) |
| Related | [[FEX Minimal Facet\|Minimal Facet]],  [[DAS Skills]],  [[granularity]],   |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[BRDG]],  [[Clarifier]],  [[CSE]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DVT]],  [[ESP]],  [[Espresso]],  [[FEX Agenda\|Agenda]],  [[FEX API\|API]],  [[FEX API Design\|API Design]],  [[FEX Architecture\|Architecture]],  [[FEX At Entity\|At Entity]],  [[FEX Claude\|Claude]],  [[FEX Completed Roadmap\|Completed Roadmap]],  [[FEX CSE\|CSE]],  [[FEX Decisions\|Decisions]],  [[FEX Decisions Details\|Decisions Details]],  [[FEX Dispatch Examples\|Dispatch Examples]],  [[FEX Empty\|Empty]],  [[FEX Facet\|Facet]],  [[FEX Figure Page\|Figure Page]],  [[FEX Files\|Files]],  [[FEX Icebox\|Icebox]],  [[FEX Inbox\|Inbox]],  [[FEX Project Root\|Project Root]],  [[FEX Repo\|Repo]],  [[FEX Roadmap\|Roadmap]],  [[FEX Rules\|Rules]],  [[FEX Scheduler\|Scheduler]],  [[FEX Skill\|Skill]],  [[FEX Spine Examples\|Spine Examples]],  [[FEX Stories\|Stories]],  [[FEX System Design\|System Design]],  [[Forum Stories]],  [[Harbor Account Northwind]],  [[Harbor Integrations]],  [[Harbor Latency Budget]],  [[Harbor Releases]],  [[Harbor Tenancy Model]],  [[Harbor Upgrade Guide]],  [[HBR PRD User Stories]],  [[HHOP]],  [[HRUN]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

# FEX Minimal Skill


The **minimal-skill capsule**: the smallest file set that fully captures a skill *and its design thinking*, with **nothing empty**. Same lazy discipline as [[FEX Minimal Facet]] — uniform structure, files exist only when they carry content. The one structural difference from a facet: a skill's **spec is its runbook, and the runbook lives in the published repo** ([[DAS Skills]] / `dans-anchor-system` on GitHub), so the design thinking is kept *out* of the published repo and lives in the parallel design-home tree.

## The capsule

| File | Where it lives | Role | When it exists |
|---|---|---|---|
| `{name}/SKILL.md` | **published repo** (`~/.claude/skills/`, symlinked from [[DAS Skills]]) | **Spec / runbook** — *what* the skill does + how to run it. | Always. |
| `{Name}.md` | **design-home tree** (e.g. `Utility/{design-home} {name}/`) | **Design-home anchor page** — masthead: Spec (→ the runbook) / Design / Features. | Always (the design home). |
| `{Name} Design.md` | design-home tree | **Design** — *why*: standing decisions + index of the feature docs that shaped it. | Lazily — when the first real decision lands. |
| `{Name} Story.md` | design-home tree | one representative **user story**, if it illuminates intent. | Optional, only when it adds something. |
| (shared) `{Anchor} Features/F<n> …` | design-home tree | **Features** — chronological detail; the Design doc **links** them, never copies. | Already exist from `/feature`. |

**Not in the capsule:** no Backlog, no UX, no prd/principles/architecture stubs. The published runbook stays clean (spec + any helper code only); all rationale lives in the design-home tree.

## Why the split matters

The published `SKILL.md` is consumed by anyone who installs the skill — it must stay a clean runbook. The *why we built it this way* (rejected alternatives, standing decisions) would be noise there, but is exactly what keeps the system from relitigating itself. So it lives one tree over, in `{design-home}/{name}/`, linked from the runbook's `Related`. Single source of truth ([[atlas]] § routing-not-duplication): the Design doc references the runbook; it never restates it.

## Live instance

A simple single-runbook skill such as [[snip]] is the shape: its spec is `skills/snip/SKILL.md` (published); its design home is `{design-home} snip` in the design-home tree, where a `{design-home} snip Design.md` is added the first time a real decision needs recording. Most skills are at the "spec only" stage today — the Design doc is the lazy piece the per-skill migration fills in *as decisions happen*, not up front. The facet side is already fully worked: see [[FEX Minimal Facet]] → [[DAS Dispatch Table]].
