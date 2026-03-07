# CAB Code

An anchor may optionally have an associated code repository. The repository lives outside the vault and is connected to the anchor via a `Code` symlink.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

The anchor folder in the vault:

```
Task Runner/                         Anchor folder (in vault)
├── Task Runner.md                   Marker file
├── TSK.md                           Anchor page
├── TSK Docs/                        Planning & published docs
├── CLAUDE.md                        Claude Code config
└── Code -> ~/ob/proj/TSK/task-runner   Symlink to repo
```

The code repository (outside the vault):

```
~/ob/proj/TSK/task-runner/           Code repository
├── .git/
├── pyproject.toml
├── justfile                         Standard task recipes
├── README.md
├── src/taskrunner/
├── tests/
└── docs/                            Sync-pushed from TSK Docs/
    ├── user/                        ← from TSK User/
    └── dev/                         ← from TSK Dev/
```

A minimal justfile for this project:

```just
# Default recipe — show available recipes
default:
    @just --list

# Incremental build
build:
    python -m build

# Run the test suite
test:
    pytest tests/

# Run all checks (lint + test)
check:
    ruff check src/ tests/
    pytest tests/

# Install in development mode
dev:
    pip install -e ".[dev]"
```

---



# Format Specification

## Location

Anchors live in the vault under `~/ob/kmr/` in grouping folders like `prj/`, `prj/binproj/`, `prj/PP/`, `SV/`. Code repositories live under `~/ob/proj/`, nominally mirroring the grouping:

```
Vault (anchors)                   Repos
~/ob/kmr/prj/ClaudiMux/          ~/ob/proj/ClaudiMux/
~/ob/kmr/prj/binproj/ctrl code/  ~/ob/proj/ctrl code/
~/ob/kmr/SV/CVT/                  ~/ob/proj/CVT/
```

The parallel structure is **nominal** — grouping folders don't always match exactly. The `Code` symlink in the anchor is always the authoritative way to find the repo; never rely on path conventions alone.

```
{CAB Folder}/
├── {NAME}.md
├── {NAME} Docs/
└── Code -> ~/ob/proj/{project}/{repo}
```

The symlink is always named `Code` regardless of the repository's actual name.

## Doc Sync with sync-push

When an anchor has both `{NAME} User/` and/or `{NAME} Dev/` doc folders and a code repository, the docs are pushed to the repo using `sync-push`. The repo receives them in lowercase folders:

```
{repo}/docs/
├── user/    ← sync-pushed from {NAME} Docs/{NAME} User/
└── dev/     ← sync-pushed from {NAME} Docs/{NAME} Dev/
```

### Setup

Register sync-push targets for each doc folder that should be pushed:

```bash
sync-push "{NAME} Docs/{NAME} User" --add code "{repo}/docs/user"
sync-push "{NAME} Docs/{NAME} Dev"  --add code "{repo}/docs/dev"
```

### Git Pre-Commit Hook

Add a pre-commit hook in the repository to automatically sync docs before each commit. In `{repo}/.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Sync docs from vault before committing
sync-push "/path/to/{NAME} Docs/{NAME} User" 2>/dev/null
sync-push "/path/to/{NAME} Docs/{NAME} Dev" 2>/dev/null
```

This ensures the repo always has the latest docs from the vault without manual sync steps.

## Edits Flow One Way

Documentation is authored in the vault (`{NAME} User/`, `{NAME} Dev/`) and pushed to the repo. Do not edit the `docs/user/` or `docs/dev/` folders in the repo directly — `sync-push` will detect conflicts and refuse to overwrite if target files have been modified.
