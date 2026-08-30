---
description: "the kinds catalog"
group: file
---

| -[[DAS Anchor Page]]- | → [[DAS]] → [[FCT]] → [DAS Anchor Page](hook://p/DAS%20Anchor%20Page)  |
| --- | --- |
| Related | [[DAS Facets]],  [[DAS Dispatch Table]],  [[DAS progressive-disclosure]],  [[FEX]],   |
| Rules | [[R-anchor]],  [[R-anchor-page]],   |
| Examples | [[HBR\|HBR anchor page]],  [[OBU\|OBU anchor page]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS At Entity]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Proj]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Anchor Page
The entry page every anchor opens with — its `{slug}.md`.

Design
**Examples:** [[HBR\|Code project]],  [[DAS Anchor Page\|facet]],  [[DAS progressive-disclosure\|discipline]],  [[DAS Mint\|skill-doc]],  [[DAS Skills\|Container · grouped]],  [[SKA Access\|Container · list]],  [[HBR Log\|Container · chronological]],  [[Life\|Topic]]
Rulesets
**OLD Examples:** [[FEX]] — ~~[[Snapper Dapper\|skill]]~~,  [[Espresso\|list]],  ~~[[Harbor Components\|grouped]]~~,  [[Glossary\|facet]],  ~~[[Harbor\|project]]~~,  ~~[[Harbor Ingest\|sub-folder]]~~

| Kind | FEX examples | Description and external examples |
| --- | --- | --- |
| Topic ([[Topic Anchor]]) | [[Knots]] | Domain-of-life hub folder that routes to the pages within it; masthead = breadcrumb + optional Related + a `...` auto-summary member zone. *Ext:* [[Life]], [[Food]], [[Legal]] |
| Project | *(abstract)* | Active-work anchor that moves through states; splits by output kind into Code vs Paper. |
| - Code project ([[Code Anchor]]) | [[HBR]] | Software project (`traits: [code]`); switchboard masthead (Design iff a design folder, Track iff a track folder), full design+track scaffold once a `Status` doc exists. *Ext:* [[HA]], [[MUX]], [[DMUX]] |
| - Paper project ([[Paper Anchor]]) | [[HWP]] | Long-form writeup (`traits: [paper]`) through revision cycles; signature is a `## Version history` table with per-section `s1, s2, …` track-changes markup. *Ext:* [[ABP]], [[AUP]] |
| - SKA sub-project | [[FEX Repo]] | A skill-ecosystem spec page that owns its own design but no tracking or status (the ecosystem's tracking is elsewhere — [[DAS Track]] § Who owns a Track folder). Three flavors below. |
| - - skill | [[FEX Snapshot]] | The documentation page for a skill (the skill-doc — **not** the `SKILL.md` runbook). *Ext:* [[DAS Mint]] |
| - - facet | [[FEX Manifest]] | A reusable document-shape spec — the format a recurring kind of doc must follow. *Ext:* [[DAS Anchor Page]], [[DAS Naming]] |
| - - discipline | [[FEX Retention]] | A cross-cutting principle or practice applied across many anchors. *Ext:* [[DAS progressive-disclosure]], [[DAS verification]] |
| Container ([[Collection]]) | *(abstract)* | A [[Collection]] anchor whose body enumerates homogeneous members; required member zone in one of three structural shapes. |
| - Grouped Container ([[Collection]]) | [[HBR Components]] | Each row is a group holding many members (often `+`-expandable); chosen once a flat list outgrows ~15. *Ext:* [[Log]], [[DAS Facets]], [[DAS Skills]] |
| - List Container ([[Collection]]) | [[Espresso]] | One row per member (an auto-list separator emits one row per child); count-independent. *Ext:* [[SV]], [[RR]], [[Roots]], [[SKA Access]] |
| - Chronological Container ([[Collection]]) | [[HBR Log]] | Reverse-dated entry stream; newest-first, ISO-prefixed member names. *Ext:* [[Journal]], [[HBR Log]] |

## Worked example sets — five real vault instances per kind

Real anchor pages found in the vault and brought to conformance, so the spec can be judged against actual instances (not the gallery). Five per kind:

### Topic
- [[Life]]
- [[Courses]]
- [[Food]]
- [[Legal]]
- [[SRCH]]

### Code project
- [[HA]]
- [[SKD]]
- [[MUX]]
- [[CMP]]
- [[DMUX]]

### Paper project
- [[ABP]] *(Alien Biology Paper — the canonical paper project)*
- [[AUP]] *(Alignment Under Pressure — legacy-formatted, version table TBD)*

*(Only ~1–2 genuine paper projects exist in the vault. The giveaway is a `## Version history` **version table** with `s1, s2, s3 …` per-section markup (per [[Paper Anchor]]) — NOT promotable from research reports or paper collections.)*

### SKA sub-project
- [[DAS Code Repository]]
- [[DAS Naming]]
- [[DAS verification]]
- [[DAS Linked Mode]]
- [[SKL Doc]]

### Container
- [[Log]] *(grouped — many entries per row)*
- [[SV]] *(list — `---` auto-generates one row per entry)*
- [[RR]] *(list — `---` auto, one row per entry)*
- [[Roots]] *(list)*
- [[Journal]] *(chronological)*

**TLDR** — **Cardinality: one per anchor.** Every anchor has exactly one `{slug}.md` entry page. It opens with YAML `description:` frontmatter, then H1 → one-line summary → optional figure → dispatch table (breadcrumb + Related + kind-specific rows). The embedded `R-anchor-page` ruleset (23 shared rules + five kind deltas — Topic / Code / Paper / SKA sub-project / Container) is the auditable contract; `/audit anchor` and `/create anchor` cite it. Member groups appear only on Container anchors; a Topic carries a `...` auto-summary of its contents.

## Anchor Page Template

An anchor is **two files**: the `.anchor` spec (what makes the folder an anchor) and the `{slug}.md` entry page that renders inside it.

**`.anchor`** — the anchor spec (YAML; consumed by HookAnchor):

```yaml
slug: {slug}
title: {Full Name}
traits: [Code]
```

**`{slug}.md`** — opens with YAML frontmatter…

```yaml
description: one-line description of the anchor
traits: [Code]
```

…then the body, which renders **live** (markdown is never shown in back-ticks — it does not render there):

# {slug} - {Full Name}
{one-sentence summary — the essence: what the page is/does at its core, not incidental detail; NO blank line above this line}

| -{slug}- | → [[kmr]] → … → [{Full Name}](hook://p/{slug})<br>: short description |
| --- | --- |
| Related | … |
| {structural / member rows} | … |
| ... |  |

## Anchor Page Parts

- **Frontmatter** — `description:` (one line) + `traits:` (the anchor kind). Inline `desc::` is deprecated; migrate to `description:` in YAML.
- **H1** — `{slug} - {Full Name}`: the slug leads (the jump-key), the readable name follows. Bare-name anchors use just the name.
- **Summary** — one sentence on the **very next line** (no blank after the H1); states the **essence** — what the page *is* or *does* at its core, not incidental detail (per R-anchor-page-06). More goes in an optional `## Overview` later, never above the dispatch table.
- **Figure** — optional; embedded right after the summary with **no heading above it** — the big-picture visual before the navigation.
- **Dispatch table** — the masthead (+ a member zone for a [[Collection]] anchor). The table's *form* is [[DAS Dispatch Table]]; its row *placement* is [[R-anchor-page]]-12/-13/-14.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above: the `.anchor` + page template, the parts, and the `R-anchor-page` ruleset.)*

- **Consumers cite this file as the format authority** — `/create anchor`, `/rewire`, `/tidy`, `/audit anchor`, and the audit scripts.
- **Link, don't duplicate** — dispatch-table *mechanics* stay in [[DAS Dispatch Table]], row *placement / order* in [[R-anchor-page]]-12/-13/-14, the naming prefix in [[DAS Naming]]; sub-folder dispatch pages have their own facets. Don't inline them here.
- **Examples are never instantiated here** — they live in the `examples/` gallery ([[FEX]]); the masthead `Examples` row links to them by kind. If the spec changes, fix the examples — never retrofit the spec to a stale copy.
