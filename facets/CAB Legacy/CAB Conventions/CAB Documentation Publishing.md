# CAB Documentation Publishing

Convention spec defining how an anchor's documentation is split between private planning docs and the published `docs/` tree that becomes the user-facing site.

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

# BRIEF

- **This file is the publishing-layout spec** — it defines the split between private `{NAME} Docs/` (planning/internal) and the published repo-level `docs/` tree (user guides, architecture, API). Edits here change what every code anchor's published documentation should look like.
- **NOT a generator manual.** Keep generator-specific runbooks (full MkDocs/TypeDoc/swift-docc configs, theme tuning, plugin wiring) out of this file — record only the chooser-level "use X for Python, Y for Swift" mapping. Detailed generator setup belongs in a per-anchor brief or the generator's own docs.
- **Inclusion test** — a thing belongs here only if it is a *cross-anchor convention* about where docs live, how they're categorized (user-guide / architecture / api), or how the workflow flows (write → build → preview → deploy). Per-anchor specifics, code samples beyond illustrative snippets, and project-specific deploy pipelines do not.
- **Sibling-spec boundaries** — site structure / hosting / theming is [[CAB Documentation Site]]; private planning docs are governed by the `{NAME} Docs/` folder rules in the relevant CAB facet. Link sideways rather than inlining their content here.
- **Load-bearing folder names** — `docs/`, `user-guide/`, `architecture/`, `api/`, `site/`, `{NAME} Docs/` are referenced by tooling, hooks, and other CAB specs. Do not rename them without sweeping every CAB facet and generator config that depends on them.
- **Code-interface examples are illustrative only.** The `## Documenting Code Interfaces` snippets show the discipline shape (return-type annotation, aligned inline comments); do not let this section grow into a full code-style guide — that belongs in language-specific rule files, not the publishing spec.
