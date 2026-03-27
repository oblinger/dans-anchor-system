# CAB Documentation Site

Published web presence for an anchor. Two levels: a simple project page (Jekyll) or a full documentation site (MkDocs).

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

**Project page** (simple splash):

```
Task Runner/
└── website/
    ├── index.md              Jekyll front matter, cayman layout
    └── deploy.sh             Copy to oblinger.github.io repo
```

**Full documentation site** (MkDocs):

```
task-runner/                  (code repository)
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

Published at `oblinger.github.io/gitproj/task-runner/`.

---



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
