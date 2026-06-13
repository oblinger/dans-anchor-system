---
description: published project overview page
---
# FCT Project Page

A lightweight public-facing splash page for an anchor, published to the personal website (oblinger.github.io). Built via the `/code publish` skill.

A project page is a `website/` folder inside the anchor holding an `index.md` (Jekyll/cayman splash with front matter), optional extra pages/assets, and a `deploy.sh` that copies the folder to the website repo and pushes. The shape, location, front matter, and publish path are specified in the sections below.

## When to Use

- Any anchor with a code repository that should have a public presence
- Projects that need a landing page but don't warrant a full documentation site
- Open source projects, portfolio pieces, tools shared with others

## Location

The project page lives in a `website/` directory inside the anchor (vault side, not repo side):

```
{CAB Folder}/
├── {NAME}.md
├── CLAUDE.md
├── .anchor                       declares `code:` key pointing at the repo (absolute, or relative to this folder; `.` for inline)
├── {NAME} Docs/
└── website/                      project page source
    ├── index.md                  splash page with Jekyll front matter
    ├── [additional .md]          extra pages (if any)
    ├── [assets/]                 images, PDFs (if any)
    └── deploy.sh                 copy to website repo and push
```

## F060 — not applicable

The Project Page is a published static-website artifact (Jekyll + cayman theme on `oblinger.github.io`), not a CAB facet doc inside the anchor's documentation tree. The F060 top-of-doc rule (H1 + CAB dispatch-table placeholder) does **not** apply — the Jekyll layout in the front matter shapes the rendered page instead.

## Jekyll Front Matter

Each `.md` file uses the cayman layout:

```yaml
---
layout: cayman
title: {PROJECT NAME}
description: {ONE-LINER}
permalink: /gitproj/{SLUG}/
---
```

## Publishing

Published to `oblinger.github.io/gitproj/{SLUG}/` and linked from the projects hub at `/gitproj/`. See [[code-publish]] for the full workflow, questions checklist, and deploy steps.

## Dispatch Table Entry

The project page URL appears in the **External** row of the anchor's dispatch table:

```markdown
| External | [Repo](https://github.com/oblinger/{repo}), [Project Page](https://oblinger.github.io/gitproj/{SLUG}/) |
```

## Relationship to Documentation Site

- **Project Page** — simple splash, one or a few pages, Jekyll/cayman
- **[[FCT Documentation Site]]** — full doc site with navigation, search, API docs (MkDocs/Material)

An anchor can have both: a project page for the public landing, and a documentation site for detailed reference.

# BRIEF

- **This is the facet spec for the published Project Page artifact** — a Jekyll/cayman splash page living in `{NAME}/website/` and deployed to `oblinger.github.io/gitproj/{SLUG}/`. Edits here change the rule, not any one anchor's page.
- **F060 explicitly does NOT apply** to this facet — the Project Page is a static-website artifact (Jekyll front matter shapes it), not an in-anchor doc with a CAB dispatch-table placeholder. Don't add an H1+placeholder to the structure described above.
- **Inclusion test for new content here**: does it describe the *shape, location, front matter, or publish path* of a project page across all anchors? If yes, add. If it's anchor-specific or deploy-tooling-specific, route to [[code-publish]] (workflow) or that anchor's own `website/` folder.
- **No inline reference example** — the page describes the project-page shape in prose/outline (§ Location, § Jekyll Front Matter); a facet spec must not embed a sample instance. TODO: link a worked example (a real anchor's `website/` folder) once one exists.
- **Cross-references to keep aligned**: [[code-publish]] (the workflow that builds + deploys), [[FCT Documentation Site]] (sibling facet for full doc sites), and the anchor's dispatch-table `External` row format shown in § Dispatch Table Entry. If any of those names change, update here.
- **Permalink and dispatch-table-row formats are load-bearing**: `permalink: /gitproj/{SLUG}/` and the `External` row `[Project Page](https://oblinger.github.io/gitproj/{SLUG}/)` must stay in sync — both are consumed by the projects hub at `/gitproj/`.
