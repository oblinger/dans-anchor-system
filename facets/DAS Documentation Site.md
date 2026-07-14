---
description: "published web presence for an anchor — Jekyll project page or MkDocs full documentation site"
---

# DAS Documentation Site
Published web presence for an anchor. Two levels: a simple project page (Jekyll) or a full documentation site (MkDocs).

| -[[DAS Documentation Site]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Documentation Site](hook://p/DAS%20Documentation%20Site) |
| --- | --- |
| Related | [[DAS Output]],  [[DAS Track]],  [[DAS Code]],  [[code-publish]],   |
| Rules | [[R-documentation-site]],   |
| Examples | [[ABIO\|fuller (project page + full MkDocs site)]],  [[DCP\|minimal (project page only)]],   |
|  |  |
| **Table of Contents** |  |
| [[#What it is]] |  |
| [[#Project Page]] |  |
| [[#Documentation Site]] |  |
| [[#Stack]] |  |
| [[#Setup Recipe]] |  |
| [[#Three Output Format Pattern]] |  |
| [[#Deployment Options]] |  |
| [[#Applicability]] |  |
| **[[#BRIEF]]** |  |

**TLDR** — One per anchor. Two tiers: a lightweight Jekyll project page (`website/`) for anchors that need a splash, and a full MkDocs documentation site (`docs/` + `mkdocs.yml`) for anchors with substantial reference material. The stack is MkDocs Material + mkdocstrings + mkdocs-jupyter + mkdocs-roamlinks. Deployment is via `just docs-deploy` (copy to website repo) or `mkdocs gh-deploy` (gh-pages branch). See [[code-publish]] for the publishing workflow.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

**Project page** (simple splash):

```
CAE example/
└── website/
    ├── index.md              Jekyll front matter, cayman layout
    └── deploy.sh             Copy to oblinger.github.io repo
```

**Full documentation site** (MkDocs):

```
cae-example/                  (code repository)
├── mkdocs.yml
├── docs/
│   ├── index.md
│   ├── user/
│   │   └── guide.md
│   └── dev/
│       ├── architecture.md
│       └── modules/
│           └── scheduler.md
└── justfile                  just docs / just docs-serve
```

Published at `oblinger.github.io/gitproj/cae-example/`.

---

## What it is

**Cardinality: one per anchor.** An anchor adopts at most one Documentation Site facet — either a project page or a full documentation site, not both simultaneously. Detection is folder-existence: presence of `website/` (project page tier) or `docs/mkdocs.yml` (documentation site tier) within the anchor's code repository.

## Project Page

A lightweight splash page on the personal website (oblinger.github.io). Built via `/code publish`.

- Lives in `website/` inside the anchor (vault side)
- Uses Jekyll with `jekyll-theme-cayman`
- Published to `oblinger.github.io/gitproj/{slug}/`
- Added to the projects hub at `/gitproj/`

```
website/
├── index.md              # Splash page with Jekyll front matter
├── [additional .md]      # Extra pages (if any)
├── [assets/]             # Images, PDFs (if any)
└── deploy.sh             # Copy to website repo and push
```

See [[code-publish]] for the full workflow and questions checklist.

## Documentation Site

A full documentation website for anchors with enough content to warrant a browsable, searchable site.

### When to Use

- Any anchor with a code repository that has public or team-facing docs
- Anchors with architecture docs, user guides, API reference, or demo galleries
- Non-repo anchors with substantial reference material (serve from `docs/` folder)

## Stack

| Component | Package | Purpose |
|-----------|---------|---------|
| Site generator | MkDocs + Material | Static site with navigation, search, dark mode |
| API docs | mkdocstrings[python] | Auto-generated from docstrings |
| Notebooks | mkdocs-jupyter | Render pre-executed `.ipynb` inline |
| Wikilinks | mkdocs-roamlinks-plugin | Convert `[[wikilinks]]` to standard links |

## Setup Recipe

### pyproject.toml

Add to `[project.optional-dependencies]` and/or `[dependency-groups]`:

```toml
[project.optional-dependencies]
dev = [
    "mkdocs-material>=9.0",
    "mkdocstrings[python]>=0.24",
    "mkdocs-roamlinks-plugin>=0.3",
    "mkdocs-jupyter>=0.25",
]
```

### mkdocs.yml

```yaml
site_name: Project Name
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - content.code.copy

plugins:
  - search
  - roamlinks
  - mkdocs-jupyter:
      include_source: true
      execute: false   # use pre-executed notebooks
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            show_source: true
            docstring_style: google
```

### justfile

```just
# Build documentation site
docs:
    uv run mkdocs build

# Serve documentation locally with live reload
docs-serve:
    uv run mkdocs serve

# Deploy to website repo
docs-deploy: docs
    rm -rf /path/to/website-repo/project-docs
    cp -r site /path/to/website-repo/project-docs
    cd /path/to/website-repo && git add project-docs && git commit -m "Update docs" && git push
```

## Three Output Format Pattern

For projects with demos or tutorials, publish in three synchronized formats from a single source:

1. **MkDocs pages** — rendered notebooks inline in the doc site
2. **Jupyter notebooks** — downloadable `.ipynb` for interactive use
3. **Standalone scripts** — runnable `.py` files for headless/CI use

### Implementation

Extract shared logic into a `demos/_core.py` module with pure functions (no I/O, no `matplotlib.use()`, no `save_or_show()`):

```
demos/
├── _shared.py          # builders, agents, helpers
├── _core.py            # pure functions returning figures/data
├── scripts/            # thin wrappers: use("Agg") + _core + save_or_show
├── notebooks/
│   ├── _build_notebooks.py   # generates .ipynb from _core calls
│   └── *.ipynb               # pre-executed notebooks
└── output/             # saved PNGs for gallery previews
```

The gallery page (`docs/demos/index.md`) uses symlinks to reference notebooks, scripts, and output without copying:

```
docs/demos/
├── index.md              # gallery hub with preview images
├── notebooks/ → ../../demos/notebooks/
├── output/   → ../../demos/output/
└── scripts/  → ../../demos/scripts/
```

## Deployment Options

- **Website repo copy** — `just docs-deploy` copies `site/` to a GitHub Pages repo
- **gh-pages branch** — `mkdocs gh-deploy` pushes directly to `gh-pages` branch
- **Local only** — `just docs-serve` for private anchors

## Applicability

- **Public repos** — full deployment to GitHub Pages or similar
- **Private repos** — deploy to internal hosting or serve locally
- **Non-repo anchors** — create a `docs/` folder with `mkdocs.yml`, serve with `mkdocs serve`

# BRIEF

*(Maintainer note — this is the facet spec for the Documentation Site facet; edits here change the contract for every anchor that adopts it. Don't collapse the two tiers or add a third without a clear use case — the choice point is the spec's main value. Inclusion test: content belongs here only if it applies across multiple anchors (stack choice, layout convention, deployment pattern); per-anchor config, credentials, and any real `mkdocs.yml` live in the anchor's own `website/` / `docs/`. The Stack table and Setup Recipe are the canonical reference downstream anchors copy from — update them here first, and keep the Reference Example block in sync with the Project Page / Documentation Site sections when layouts change.)*
