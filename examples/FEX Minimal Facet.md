---
description: "the leanest complete file set for a facet, with a live instance"
---

| -[[FEX Minimal Facet]]- | : the leanest complete file set for a facet, with a live instance<br>→ [[DAS]] → [[FEX]] → [FEX Minimal Facet](hook://p/FEX%20Minimal%20Facet)  |
| --- | --- |
| Anchor | [[HBR]] (reference anchor) |
| Related | [[FEX Minimal Skill\|Minimal Skill]],  [[DAS Facets]],   |
| [[DAS Dispatch Table]]  | the live instance |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[BRDG]],  [[Clarifier]],  [[CSE]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DVT]],  [[ESP]],  [[Espresso]],  [[FEX Agenda\|Agenda]],  [[FEX API\|API]],  [[FEX API Design\|API Design]],  [[FEX Architecture\|Architecture]],  [[FEX At Entity\|At Entity]],  [[FEX Claude\|Claude]],  [[FEX Completed Roadmap\|Completed Roadmap]],  [[FEX CSE\|CSE]],  [[FEX Decisions\|Decisions]],  [[FEX Decisions Details\|Decisions Details]],  [[FEX Dispatch Examples\|Dispatch Examples]],  [[FEX Empty\|Empty]],  [[FEX Facet\|Facet]],  [[FEX Figure Page\|Figure Page]],  [[FEX Files\|Files]],  [[FEX Icebox\|Icebox]],  [[FEX Inbox\|Inbox]],  [[FEX Project Root\|Project Root]],  [[FEX Repo\|Repo]],  [[FEX Roadmap\|Roadmap]],  [[FEX Rules\|Rules]],  [[FEX Scheduler\|Scheduler]],  [[FEX Skill\|Skill]],  [[FEX Spine Examples\|Spine Examples]],  [[FEX Stories\|Stories]],  [[FEX System Design\|System Design]],  [[Forum Stories]],  [[Harbor Account Northwind]],  [[Harbor Integrations]],  [[Harbor Latency Budget]],  [[Harbor Releases]],  [[Harbor Tenancy Model]],  [[Harbor Upgrade Guide]],  [[HBR PRD User Stories]],  [[HHOP]],  [[HRUN]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

# FEX Minimal Facet


The **minimal-facet capsule**: the smallest file set that fully captures a facet *and its design thinking*, with **nothing empty**. Every file below exists only when it carries real content — the structure is uniform (you always know where a piece *would* go), but a piece that has nothing to say is simply absent, not a stub. This is the antidote to the legacy dozen-doc scaffold (see [[DAS Dispatch Table Design]] § Standing decisions).

## The capsule

| File | Role | When it exists |
|---|---|---|
| `{Facet}.md` | **Spec** — *what* the facet is (the form, the rules). Carries the masthead + (if it enumerates anything) a member zone. | Always. |
| `{Facet} Design.md` | **Design** — *why* it's this way: standing decisions (decided X / considered Y / rejected because Z) + an index of the feature docs that shaped it. | Lazily — created the moment the first real decision lands. |
| (shared) `{Anchor} Features/F<n> …` | **Features** — the chronological design detail. Live in the anchor's shared Features pile; the Design doc **links** them, never copies. | Already exist from `/feature`. |

**Not in the capsule:** no Backlog, no UX, no PRD/principles/architecture stubs. A facet is a spec, not a project. If a facet ever genuinely needs a backlog, it has outgrown "facet" and should be reconsidered.

The Design doc is the *synthesis* (standing decisions, one place to look); the feature docs are the *detail* (chronological, per-decision). Same synthesis-vs-detail split as [[DAS Brief]] — linking, not duplication ([[atlas]] § routing-not-duplication is the same principle).

## Live instance — [[DAS Dispatch Table]]

The Dispatch Table facet is the worked example. Click through to see the capsule rendered:

| Piece | Where |
|---|---|
| Spec | [[DAS Dispatch Table]] — masthead (Anchor / Design / Related) + a member zone (its four live examples) |
| [[DAS Dispatch Table Design\|Design]] | five standing decisions + the F155 / F156 index |
| Features | [[F155 — Dispatch-table structure spec + CAE worked examples\|F155]], [[F156 — Dispatch-table rollout pilot + Dispatch Table anchor promotion\|F156]] (linked from the Design doc) |

That's the whole facet: **two files** + links to shared features. No stubs.
