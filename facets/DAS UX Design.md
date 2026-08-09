---
description: "facet spec for `{slug} UX Design.md` — the human user-facing surface (CLI commands, screens, organization, naming, output shapes, error voice)"
---

# DAS UX Design
Facet spec for `{slug} UX Design.md` — the *human* user-facing surface: CLI commands, screens, organization, naming, output shapes, error voice.

| -[[DAS UX Design]]- | → [[DAS]] → [[FCT]] → [DAS UX Design](hook://p/DAS%20UX%20Design)  |
| --- | --- |
| Related | [[DAS API Design]],  [[DAS CLI]],  [[DAS Decisions]],  [[DAS Architecture]],   |
| Examples | [[HBR UX Design\|minimal (CLI surface)]],  [[HBR UX Design\|fuller (multi-surface)]],   |
| Rules | [[R-ux]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR**
- **One per anchor** — a single `{slug} UX Design.md` captures all human-facing surface intent for the anchor.
- Covers CLI command sets, screen flows, slash-command surfaces, output shapes, and error voice.
- Sibling to [[DAS API Design]] (programmatic surface); the cut is *who the consumer is* (human vs code).
- Preface zone of each instance requires TLDR + representative figure before body H2s.
- See [[HBR UX Design]] for the canonical worked example.

UX Design specifies the **human user surface** of the anchor — how a person discovers, invokes, reads, and recovers from errors. It is sibling to [[DAS API Design]] (the *programmatic* user surface). The cut between them is **who the consumer is**, not where the surface lives: UX = human reading or invoking; API Design = code calling.

**Cardinality: one per anchor** — a single `{slug} UX Design.md` file per anchor captures the full human-facing surface intent. If the anchor has no human consumer, mark this facet `none` in [[DAS Status]] and omit the file.

> [!info] Scope guard
> "UX" here is the broad sense — *user-facing surface* — not narrowly "visual interface." For a CLI scheduler the UX is the command set, output shapes, and error voice. For a GUI app it is screens + flows. For a skill repository (no pixels) it is the slash-command surface and organization. If the anchor has no human consumer, this facet is N/A; mark it `none` in [[DAS Status]] and omit the file.

The UX Design doc is the **current spec** — what the surface looks like today, not what alternatives were considered. Rationale lives in [[DAS Decisions]] or in the document's own `D-UX<n>` design-decision rows (see [[R-ux]]). Exhaustive flag/option reference for CLIs lives in the sibling [[DAS CLI]] doc; UX Design captures the *intent* (what commands exist, what they mean, what output they produce), CLI doc is the *reference* (every flag, every exit code).

## Location

`{slug} Design/{slug} UX Design.md` — single-file form. Upgrade to anchor-folder form `{slug} UX Design/` only when sub-surfaces grow beyond what one file holds cleanly (rare; almost always single-file).

Peer of [[DAS Architecture]] and [[DAS API Design]] under [[DAS Design Dispatch|Design]].

## Preface zone

Per [[DAS progressive-disclosure]]:

- **TLDR** required — 3–8 short bullets covering: audience, the surface's spine (commands / screens / affordances), output-shape posture, error voice.
- **Figure** required — a representative visual of the surface. For a CLI: an annotated session transcript (one or two real commands with their output). For a GUI: a screen mockup. For a slash-command surface: a typed example with its inline result. SVG preferred; PNG acceptable.

## Required section spine

| H2 | What it carries |
|---|---|
| `## Audience` | One paragraph: who the human consumer is, what context they're in (terminal? Obsidian? browser?), what they know going in, what their goal is. Sets the frame for every following decision. |
| `## Entry-points` | The spine table. Every command / screen / affordance listed once with: name, one-line purpose, source story (`US-<slug>-<N>`). For CLIs: command name + one-line synopsis. For GUIs: screen name + one-line purpose. |
| `## Output shapes` | Both forms named explicitly: human-readable default (what the user sees with their eyes) AND structured opt-in (`--json`, machine-readable export, copyable payload). Realistic example for each. |
| `## Error voice` | The named error situations + the exact (or templated) message + exit code (CLI) or alert pattern (GUI). Tone is declared at the top (terse / friendly / verbose). |
| `## Discovery` | How the human finds the entry-points: `--help` text, dispatch table in `{slug}.md`, hotkey hints, banner copy. Names the signal the user follows on first encounter. |
| `## Design decisions` | `D-UX<n>` rows: each load-bearing UX choice with rationale (why this and not the obvious alternative). Bridge to [[DAS Decisions]] for decisions that cite a ruleset. |

Other H2s (e.g., `## Affordances`, `## Accessibility`, `## Telemetry`) join when applicable.

## Reference example

See [[HBR UX Design]] — the CAE scheduler shows the canonical shape for a CLI-shaped human surface. For a slash-command surface example see the future SKL UX Design (in progress).

## See also

- [[DAS API Design]] — sibling facet covering the programmatic surface.
- [[DAS CLI]] — exhaustive flag/exit-code reference (downstream of UX Design's *intent*).
- [[DAS Decisions]] — load-bearing decisions citing rules; bridge from D-UX rows.
- [[DAS Architecture]] — internal organization; UX entry-points typically map to architecture components.
- [[DAS progressive-disclosure]] — preface zone discipline.
- [[DAS markdown]] — markdown authoring discipline.

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative spec is the body above; the embedded [[R-ux]] ruleset is its auditable form.)*

- **Inclusion test** — a change belongs here only if it is a structural rule, required section, or load-bearing definition that applies to *every* `{slug} UX Design.md` across anchors. Concrete commands, screens, error messages, and worked examples belong in each anchor's own doc or in [[HBR UX Design]] (canonical exemplar) — never inline them here.
- **Preserve the facet-cut boundaries** — UX Design owns human-facing intent; [[DAS API Design]] owns the programmatic surface, [[DAS CLI]] the exhaustive flag reference, [[DAS Architecture]] internal organization. R-ux-08 is the load-bearing guard; don't let this spec absorb sibling content.
- **Ruleset is co-located** — the `# RULESET R-ux` H1 is part of this file per [[F133 — Rulesets folder convention + facet embedding|F133]]; revise rules in place, never split into a sibling file or duplicate in [[DAS Ruleset]]. And this is the rulebook, not an instance — R-ux-01 mandates TLDR + figure for each instance; don't import a figure or transcript into this spec.
- **Cross-references that must stay live** — [[DAS API Design]], [[DAS CLI]], [[DAS Decisions]], [[DAS Architecture]], [[DAS progressive-disclosure]], [[HBR UX Design]]; renaming or moving any requires updating the wiki-links here.
