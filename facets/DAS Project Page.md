---
description: "published project overview page for an anchor"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Anchor]] → [FCT Project Page](hook://p/DAS%20Project%20Page)
# FCT Project Page
A lightweight public-facing splash page for an anchor, published to the personal website (oblinger.github.io). Built via the `/code publish` skill.

**Related:** [[DAS Documentation Site]],  [[code-publish]],  [[DAS Anchor Page]],  [[DAS Dispatch]]
**Examples:** [[ABIO\|fuller (index + deploy.sh)]],  [[DCP\|minimal (index only)]]

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

The Project Page is a published static-website artifact (Jekyll + cayman theme on `oblinger.github.io`), not a CAB facet doc inside the anchor's documentation tree. The F060 top-of-doc rule (H1 + CAB dispatch-table placeholder) does **not** apply — the Jekyll layout in the front matter shapes the rendered page instead.

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

# RULESET R-project-page
include::
where:: `file: **/website/index.md`
description:: Rules every Project Page instance must satisfy — presence of a `website/` folder, the Jekyll cayman front matter, and the deploy script.

### RULE R-project-page-01 — `website/` folder present (checked)
The anchor contains a `website/` subdirectory with at minimum an `index.md` and a `deploy.sh`.
**Check pattern:** `website/index.md` and `website/deploy.sh` exist inside the anchor folder.
**Tier:** checked
**Why:** the `website/` folder is how the project page is detected; missing it means the facet is absent, not malformed.

### RULE R-project-page-02 — Jekyll cayman front matter (checked)
`website/index.md` opens with YAML frontmatter including `layout: cayman`, a non-empty `title:`, a non-empty `description:`, and a `permalink: /gitproj/{slug}/`.
**Check pattern:** frontmatter block contains `layout: cayman`, `title:`, `description:`, and `permalink:` matching `/gitproj/`.
**Tier:** checked
**Why:** the cayman layout and permalink are what Jekyll needs to render and route the page; missing fields produce a broken or invisible page.

### RULE R-project-page-03 — Dispatch-table Related row carries the published URLs (sampled)
The anchor's dispatch table (root `{slug}.md`) includes a `Related` row carrying both the GitHub repo link and the project page URL `https://oblinger.github.io/gitproj/{slug}/` (repo/site links live in Related, not a separate External row).
**Check pattern:** the anchor page has a `| Related |` row containing `oblinger.github.io/gitproj/`.
**Tier:** sampled
**Why:** the Related row is how readers discover the published page; without it the deployment is silent to navigators.

### RULE R-project-page-04 — Permalink and dispatch-table URL stay in sync (stated)
The `permalink:` value in `website/index.md` frontmatter and the URL in the anchor's `Related` dispatch row must use the same `{slug}` — they cannot drift.
**Check pattern:** extract `{slug}` from frontmatter `permalink:`; verify the same path appears in the `Related` row.
**Tier:** stated
**Why:** mismatched slugs cause the dispatch row to link a 404; the projects hub `/gitproj/` lists all pages by permalink.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above plus the `# RULESET R-project-page` block; the deploy workflow is [[code-publish]].)*

- **Inclusion test** — content belongs here only if it describes the *shape, location, front matter, or publish path* of a project page across all anchors. Anchor-specific or deploy-tooling detail routes to [[code-publish]] or that anchor's own `website/` folder.
- **Cross-references to keep aligned** — [[code-publish]] (builds + deploys), [[DAS Documentation Site]] (sibling facet), and the § Dispatch Table Entry `Related`-row format. Update here if any of those names change.
