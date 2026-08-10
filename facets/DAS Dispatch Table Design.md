---
description: "Design rationale + standing decisions for the Dispatch Table discipline — the why behind the spec, so it isn't relitigated."
---

| -[[DAS Dispatch Table Design]]- | → [[DAS]] → [[FCT]] → [DAS Dispatch Table Design](hook://p/DAS%20Dispatch%20Table%20Design)  |
| --- | --- |
| Related | [[DAS Dispatch Table]],  [[Collection]],  [[DAS progressive-disclosure]],  [[audit-dispatch\|/audit dispatch]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Dispatch]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Dispatch Table Design


The **design-flow** companion to [[DAS Dispatch Table]]: it holds the *why* — the standing decisions, what was considered and rejected — so future work doesn't relitigate them. The spec is the *what*; this is the *why*. It's also the first worked instance of the **minimal-facet capsule** ([[FEX Minimal Facet]]).

## Standing decisions

Each entry: what was decided, what was considered, why. Append-only; this is the record.

### Masthead is a small fixed switchboard — at most three standard rows
**Decided 2026-06-11.** The masthead is breadcrumb (identity) + **Anchor** (general dispatch) + **Design** (design-flow, only if the anchor has one) + **Related**. Not a directory of everything — a switchboard.
**Considered & rejected:** an open-ended set of category rows (the prior "structural rows + curated links" framing). It let mastheads sprawl and blurred the line between the fixed switchboard and the variable contents. The three-row cap keeps every anchor's masthead uniform and scannable.

### Enumerable content is the Member zone, never a masthead row
**Decided 2026-06-11.** Anything you'd *list* — members, sub-items, worked examples — drops below the masthead into the Member zone. "Examples are outside the masthead" turned out to be the same statement as "examples are the member zone."
**Considered & rejected:** an `Examples` row *inside* the masthead (built first, then reverted). It conflated the fixed switchboard with variable-length content; the member zone already exists to hold exactly that.

### Promotion scope = minimal capsule, not a full project anchor (F156 Q1)
**Decided 2026-06-11.** Dispatch Table stays a discipline doc with the new masthead + member zone + this Design doc — a **minimal-facet capsule**, not a folder with PRD / Backlog / Architecture / UX. Per [[F156 — Dispatch-table rollout pilot + Dispatch Table anchor promotion|F156]] Q1, option (A/C).
**Considered & rejected:** (B) a full anchor with a design scaffold — it re-creates the empty-stub bloat the vault is currently *deleting* (the legacy `{name} plan/` dozen-doc scaffold; see [[SYS]] F005). Wiki-links resolve by filename regardless of folder, so a later promotion stays link-safe — low lock-in is *why* we start minimal.

### Classification: a discipline (the form), not a doc facet
**Decided earlier; reaffirmed.** The dispatch table is the *form* of a switchboard (derived navigation), distinct from content-container doc facets like [[DAS Brief]] / [[DAS Discussion]]. The reopenable alternative — folding it into [[DAS Anchor Page]] — is parked in the spec's § Alternative formulation.

### No markdown inside backticks
**Decided 2026-06-11.** Wiki-links inside inline code spans mangle on render (the linter rewrites them). Use bare wiki-links in prose; reserve backticks for literal tokens (`---`, `...`, `+`, paths, commands). Fenced blocks may show literal row *syntax* (placeholders render as plain text), but never as a stand-in for a real page — link to the live instance instead.

## Features that shaped this

- [[F155 — Dispatch-table structure spec + CAE worked examples|F155]] — established the Masthead + Member-zone model and the live CAE example gallery.
- [[F156 — Dispatch-table rollout pilot + Dispatch Table anchor promotion|F156]] — the promotion-scope decision (minimal capsule) and the audit-dispatch rollout pilot.
