---
description: "published project overview page for an anchor"
---

# DAS Project Page
A lightweight public-facing splash page for an anchor, published to the personal website (oblinger.github.io). Built via the `/code publish` skill.

| -[[DAS Project Page]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Project Page](hook://p/DAS%20Project%20Page) |
| --- | --- |
| Related | [[DAS Documentation Site]],  [[code-publish]],  [[DAS Anchor Page]],  [[DAS Dispatch]],   |
| Rules | [[R-project-page]],   |
| Examples | [[ABIO\|fuller (index + deploy.sh)]],  [[DCP\|minimal (index only)]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[facets/DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Disciplines Brief]],  [[DAS Discussion]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Plan Dispatch]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS TSK User Guide]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

A project page is a `website/` folder inside the anchor holding an `index.md` (Jekyll/cayman splash with front matter), optional extra pages/assets, and a `deploy.sh` that copies the folder to the website repo and pushes. The shape, location, front matter, and publish path are specified in the sections below.

**Cardinality: one per anchor** — an anchor has at most one project page (one `website/` folder, one splash page deployed to `oblinger.github.io/gitproj/{slug}/`).

## When to Use

- Any anchor with a code repository that should have a public presence
- Projects that need a landing page but don't warrant a full documentation site
- Open source projects, portfolio pieces, tools shared with others

## Location

The project page lives in a `website/` directory inside the anchor (vault side, not repo side):

```
{CAB Folder}/
├── {slug}.md
├── CLAUDE.md
├── .anchor                       declares `code:` key pointing at the repo (absolute, or relative to this folder; `.` for inline)
├── {slug} Docs/
└── website/                      project page source
    ├── index.md                  splash page with Jekyll front matter
    ├── [additional .md]          extra pages (if any)
    ├── [assets/]                 images, PDFs (if any)
    └── deploy.sh                 copy to website repo and push
```

## F060 — not applicable

The Project Page is a published static-website artifact (Jekyll + cayman theme on `oblinger.github.io`), not a DAS facet doc inside the anchor's documentation tree. The F060 top-of-doc rule (H1 + CAB dispatch-table placeholder) does **not** apply — the Jekyll layout in the front matter shapes the rendered page instead.

## Jekyll Front Matter

Each `.md` file uses the cayman layout:

```yaml
---
layout: cayman
title: {PROJECT NAME}
description: {ONE-LINER}
permalink: /gitproj/{slug}/
---
```

## Publishing

Published to `oblinger.github.io/gitproj/{slug}/` and linked from the projects hub at `/gitproj/`. See [[code-publish]] for the full workflow, questions checklist, and deploy steps.

## Dispatch Table Entry

The repo + project-page URLs live in the **Related** row of the anchor's dispatch table (the first optional row; there is no separate `External` row — see [[DAS Dispatch Table]] R-08):

```markdown
| Related | [Repo](https://github.com/oblinger/{repo}),  [Project Page](https://oblinger.github.io/gitproj/{slug}/) |
```

## Relationship to Documentation Site

- **Project Page** — simple splash, one or a few pages, Jekyll/cayman
- **[[DAS Documentation Site]]** — full doc site with navigation, search, API docs (MkDocs/Material)

An anchor can have both: a project page for the public landing, and a documentation site for detailed reference.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above plus the `# RULESET R-project-page` block; the deploy workflow is [[code-publish]].)*

- **Inclusion test** — content belongs here only if it describes the *shape, location, front matter, or publish path* of a project page across all anchors. Anchor-specific or deploy-tooling detail routes to [[code-publish]] or that anchor's own `website/` folder.
- **Cross-references to keep aligned** — [[code-publish]] (builds + deploys), [[DAS Documentation Site]] (sibling facet), and the § Dispatch Table Entry `Related`-row format. Update here if any of those names change.
