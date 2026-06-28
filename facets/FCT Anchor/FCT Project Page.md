---
description: "published project overview page for an anchor"
---
# FCT Project Page
A lightweight public-facing splash page for an anchor, published to the personal website (oblinger.github.io). Built via the `/code publish` skill.

| -[[FCT Project Page]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Anchor]] → [FCT Project Page](hook://p/FCT%20Project%20Page)<br>: published project overview page for an anchor |
| --- | --- |
| Related | [[FCT Documentation Site]],  [[code-publish]],  [[FCT Anchor Page]],  [[FCT Dispatch]],   |
| Examples | [[ABIO\|fuller (index + deploy.sh)]],  [[DCP\|minimal (index only)]],   |

A project page is a `website/` folder inside the anchor holding an `index.md` (Jekyll/cayman splash with front matter), optional extra pages/assets, and a `deploy.sh` that copies the folder to the website repo and pushes. The shape, location, front matter, and publish path are specified in the sections below.

**Cardinality: one per anchor** — an anchor has at most one project page (one `website/` folder, one splash page deployed to `oblinger.github.io/gitproj/{SLUG}/`).

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

The repo + project-page URLs live in the **Related** row of the anchor's dispatch table (the first optional row; there is no separate `External` row — see [[FCT Dispatch Table]] R-08):

```markdown
| Related | [Repo](https://github.com/oblinger/{repo}),  [Project Page](https://oblinger.github.io/gitproj/{SLUG}/) |
```

## Relationship to Documentation Site

- **Project Page** — simple splash, one or a few pages, Jekyll/cayman
- **[[FCT Documentation Site]]** — full doc site with navigation, search, API docs (MkDocs/Material)

An anchor can have both: a project page for the public landing, and a documentation site for detailed reference.

# RULESET R-project-page
include::
where:: file: **/website/index.md
description:: Rules every Project Page instance must satisfy — presence of a `website/` folder, the Jekyll cayman front matter, and the deploy script.

### RULE R-project-page-01 — `website/` folder present (checked)
The anchor contains a `website/` subdirectory with at minimum an `index.md` and a `deploy.sh`.
**Check pattern:** `website/index.md` and `website/deploy.sh` exist inside the anchor folder.
**Tier:** checked
**Why:** the `website/` folder is how the project page is detected; missing it means the facet is absent, not malformed.

### RULE R-project-page-02 — Jekyll cayman front matter (checked)
`website/index.md` opens with YAML frontmatter including `layout: cayman`, a non-empty `title:`, a non-empty `description:`, and a `permalink: /gitproj/{SLUG}/`.
**Check pattern:** frontmatter block contains `layout: cayman`, `title:`, `description:`, and `permalink:` matching `/gitproj/`.
**Tier:** checked
**Why:** the cayman layout and permalink are what Jekyll needs to render and route the page; missing fields produce a broken or invisible page.

### RULE R-project-page-03 — Dispatch-table Related row carries the published URLs (sampled)
The anchor's dispatch table (root `{NAME}.md`) includes a `Related` row carrying both the GitHub repo link and the project page URL `https://oblinger.github.io/gitproj/{SLUG}/` (repo/site links live in Related, not a separate External row).
**Check pattern:** the anchor page has a `| Related |` row containing `oblinger.github.io/gitproj/`.
**Tier:** sampled
**Why:** the Related row is how readers discover the published page; without it the deployment is silent to navigators.

### RULE R-project-page-04 — Permalink and dispatch-table URL stay in sync (stated)
The `permalink:` value in `website/index.md` frontmatter and the URL in the anchor's `Related` dispatch row must use the same `{SLUG}` — they cannot drift.
**Check pattern:** extract `{SLUG}` from frontmatter `permalink:`; verify the same path appears in the `Related` row.
**Tier:** stated
**Why:** mismatched slugs cause the dispatch row to link a 404; the projects hub `/gitproj/` lists all pages by permalink.

# BRIEF

- **This is the facet spec for the published Project Page artifact** — a Jekyll/cayman splash page living in `{NAME}/website/` and deployed to `oblinger.github.io/gitproj/{SLUG}/`. Edits here change the rule, not any one anchor's page.
- **F060 explicitly does NOT apply** to this facet — the Project Page is a static-website artifact (Jekyll front matter shapes it), not an in-anchor doc with a CAB dispatch-table placeholder. Don't add an H1+placeholder to the structure described above.
- **Inclusion test for new content here**: does it describe the *shape, location, front matter, or publish path* of a project page across all anchors? If yes, add. If it's anchor-specific or deploy-tooling-specific, route to [[code-publish]] (workflow) or that anchor's own `website/` folder.
- **No inline reference example** — the page describes the project-page shape in prose/outline (§ Location, § Jekyll Front Matter); a facet spec must not embed a sample instance. TODO: link a worked example (a real anchor's `website/` folder) once one exists.
- **Cross-references to keep aligned**: [[code-publish]] (the workflow that builds + deploys), [[FCT Documentation Site]] (sibling facet for full doc sites), and the anchor's dispatch-table `Related` row format shown in § Dispatch Table Entry. If any of those names change, update here.
- **Permalink and dispatch-table-row formats are load-bearing**: `permalink: /gitproj/{SLUG}/` and the `Related` row `[Project Page](https://oblinger.github.io/gitproj/{SLUG}/)` must stay in sync — both are consumed by the projects hub at `/gitproj/`.
