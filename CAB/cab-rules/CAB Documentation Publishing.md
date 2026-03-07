# CAB Documentation Publishing

Documentation is split between private docs (anchor level) and published user docs (repository level). See also [[CAB Documentation Site]].

## Private Docs vs User Docs

- **PRIVATE DOCS** — Located in `{NAME} Docs/` folder at anchor level. Contains planning, design decisions, internal discussions, rough ideas. NOT published.
- **USER DOCS** — Published, located in repository under `docs/`. Contains polished documentation for end users and developers.

## docs/ Folder Structure

All repositories with documentation should organize `docs/` as follows:

```
docs/
├── index.md              # Documentation home page (entry point)
├── user-guide/           # Task-oriented tutorials and how-tos
│   ├── getting-started.md
│   ├── installation.md
│   └── ...
├── architecture/         # System design and technical reference
│   ├── overview.md
│   ├── config-reference.md
│   └── ...
└── api/                  # Generated API reference (auto-generated)
    └── ...
```

## Documentation Types

- **INDEX.MD** — Entry point linking to all documentation sections
- **USER-GUIDE/** — Task-oriented tutorials, getting started guides, how-tos. Written for end users.
- **ARCHITECTURE/** — System design docs, configuration reference, technical specifications. Written for developers.
- **API/** — Auto-generated from source code. Do not edit manually.

## Documentation Generators

Choose the appropriate generator for your project type:

- **PYTHON** — MkDocs with mkdocstrings for API docs
- **SWIFT** — swift-docc or Jazzy for API docs
- **TYPESCRIPT/JS** — TypeDoc for API docs
- **GENERAL** — MkDocs, Docusaurus, or similar static site generator

## MkDocs Setup (Python Projects)

```
repo/
├── mkdocs.yml            # MkDocs configuration
├── docs/                 # Documentation source
└── site/                 # Generated site (gitignored)
```

Key files:
- **MKDOCS.YML** — Configuration file in repo root
- **SITE/** — Generated documentation folder (gitignored, deployed to GitHub Pages)

## Documentation Workflow

1. Write user guides and architecture docs by hand in `docs/`
2. API docs are auto-generated from source code docstrings
3. Build docs locally: `mkdocs build` (or equivalent)
4. Preview locally: `mkdocs serve` (or equivalent)
5. Deploy to GitHub Pages: `mkdocs gh-deploy` (or equivalent)

## Documenting Code Interfaces

**Show return types** — Always annotate the return type so readers know what they're getting:
```python
run: dict = bio.fetch("data/experiments/run_001")
```

**Inline comments on same line** — Put explanatory comments on the same line as the code:
```python
run: dict = bio.fetch("data/experiments/run_001")              # data directory — run results
scenario: Scenario = bio.fetch("catalog.scenarios.mutualism")  # source tree — template
```

**Align comment markers** — Line up the `#` symbols for readability when showing multiple related calls.
