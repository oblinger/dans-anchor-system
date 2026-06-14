---
description: "published web presence for an anchor — Jekyll project page or MkDocs full documentation site"
---
# FCT Documentation Site
Published web presence for an anchor. Two levels: a simple project page (Jekyll) or a full documentation site (MkDocs).

| -[[FCT Documentation Site]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Output]] → [FCT Documentation Site](hook://p/FCT%20Documentation%20Site)<br>: published web presence for an anchor — Jekyll project page or MkDocs full documentation site |
| --- | --- |
| Related | [[FCT Output]],  [[FCT Track]],  [[FCT Code]],  [[code-publish]],   |
| Examples | [[ABIO\|fuller (project page + full MkDocs site)]],  [[DCP\|minimal (project page only)]],   |

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
- Published to `oblinger.github.io/gitproj/{SLUG}/`
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

- **This is the facet spec for the Documentation Site facet** — the authoritative rule for how an anchor publishes a web presence (Jekyll project page or MkDocs full site). Edits here change the contract for every anchor that adopts the facet.
- **Two-tier scope is load-bearing**: keep the Project Page (lightweight Jekyll splash) and Documentation Site (full MkDocs) tiers distinct. Don't collapse them, don't add a third tier without a clear use case — the choice point ("which tier does this anchor need?") is the spec's main value.
- **Not for**: per-anchor publishing config, deploy credentials, site content, or the actual `mkdocs.yml` of any real anchor — those live in the anchor's own `website/` or `docs/` folder. Keep this file as the reference shape; instance-specific tuning belongs in the anchor.
- **Inclusion test for new content**: a rule belongs here only if it applies across multiple anchors adopting the facet (stack choice, file layout convention, deployment pattern). One-off recipes for a single anchor go in that anchor's docs.
- **Stack table and Setup Recipe are the canonical reference** — when MkDocs plugins, the justfile shape, or the three-output-format pattern change, update them here first; downstream anchors copy from this spec.
- **Cite, don't duplicate**: workflow mechanics (the `/code publish` questions checklist, etc.) live in [[code-publish]]; link from here rather than re-inlining. Markdown rendering rules live in [[R-markdown]] — never duplicate them inside this facet.
- **Keep the Reference Example block in sync** with the Project Page and Documentation Site sections below it — the condensed file tree at the top is the at-a-glance summary; if the detailed layout changes, the example must change too.
