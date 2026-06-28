---
description: "facet spec for the code repository association declared in an anchor's `.anchor` file"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Anchor]] → [FCT Code Repository](hook://p/FCT%20Code%20Repository)

# FCT Code Repository
Facet spec for how an anchor declares and resolves its associated code repository — linked (separate path) or inline — via the `code:` key in `.anchor`.

**Related:** [[FCT Anchor Page]],  [[TRT]],  [[FCT Facet]],  [[FCT Manifest]]
**Examples:** [[OBU\|linked-absolute]],  [[HA\|linked-relative]]

**TLDR** — An anchor with a `code` trait declares its repo via `code:` in `.anchor` (absolute, relative, or `.` for inline). No symlink, no `.git/`-probing fallback. Doc folders sync one-way vault → repo via `sync-push`. **Cardinality: one** — one code repo association per anchor.

An anchor may optionally have an associated code repository. The anchor
declares that association with a `code:` key in its `.anchor` file. The
value is the path to the repository — absolute, or relative to the anchor
root.

The presence of the `code:` key *is* the declaration that code belongs to
this anchor; no `Code` symlink is used.

```yaml
# .anchor at the anchor root
slug: CAE
traits:
  - code
code: ../../proj/CAE/cae-example   # relative to anchor root
# or:
# code: /Users/oblinger/ob/proj/CAE/cae-example   # absolute
# or:
# code: .                                         # inline (repo at anchor root)
```

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

The anchor folder in the vault:

```
CAE example/                         Anchor folder (in vault)
├── .anchor                          YAML config (declares code: path)
├── CAE example.md                   Marker file
├── CAE.md                           Anchor page
├── CAE Docs/                        Planning & published docs
└── CLAUDE.md                        Claude Code config
```

The code repository (outside the vault), reached via `.anchor`'s `code:` key:

```
~/ob/proj/CAE/cae-example/           Code repository (referenced by .anchor)
├── .git/
├── pyproject.toml
├── justfile                         Standard task recipes
├── README.md
├── src/taskrunner/
├── tests/
└── docs/                            Sync-pushed from CAE Docs/
    ├── user/                        ← from CAE User/
    └── dev/                         ← from CAE Dev/
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

Anchors live in the vault under `~/ob/kmr/` in grouping folders like
`prj/`, `prj/binproj/`, `prj/PP/`, `SV/`. Code repositories live under
`~/ob/proj/`, nominally mirroring the grouping:

```
Vault (anchors)                   Repos
~/ob/kmr/prj/ClaudiMux/          ~/ob/proj/ClaudiMux/
~/ob/kmr/prj/binproj/ctrl code/  ~/ob/proj/ctrl code/
~/ob/kmr/SV/CVT/                  ~/ob/proj/CVT/
```

The parallel structure is **nominal** — grouping folders don't always
match exactly. The `code:` key in `.anchor` is always the authoritative
way to find the repo; never rely on path conventions alone.

## Path resolution

Scripts and skills read `.anchor` and resolve the `code:` value as follows:

- **Absolute path** — used as-is.
- **Relative path** — resolved against the **anchor root** (the folder
  containing `.anchor`), not the caller's current working directory.
- `code: .` — the anchor root itself is the repository (**inline mode**).
  In this case `.git/` sits alongside `.anchor`.

There is no implicit fallback. If an anchor has the `code` trait but no
`code:` key, scripts must error. No probing for `.git/` at the anchor
root, no legacy `Code` symlink lookup.

## Inline vs linked

Both modes declare the association with `code:` in `.anchor`.

| Mode     | `code:` value     | Repo location          | When to use |
| -------- | ----------------- | ---------------------- | ----------- |
| Linked   | path to repo dir  | outside the vault      | Normal case — keeps vault and repo separate |
| Inline   | `.`               | same folder as anchor  | Small projects where planning docs live with the code |

## Doc Sync with sync-push

When an anchor has `{NAME} User/` and/or `{NAME} Dev/` doc folders and a
code repository, the docs are pushed to the repo using `sync-push`. The
repo receives them in lowercase folders:

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

Add a pre-commit hook in the repository to automatically sync docs
before each commit. In `{repo}/.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Sync docs from vault before committing
sync-push "/path/to/{NAME} Docs/{NAME} User" 2>/dev/null
sync-push "/path/to/{NAME} Docs/{NAME} Dev" 2>/dev/null
```

This ensures the repo always has the latest docs from the vault without
manual sync steps.

## Edits Flow One Way

Documentation is authored in the vault (`{NAME} User/`, `{NAME} Dev/`)
and pushed to the repo. Do not edit the `docs/user/` or `docs/dev/`
folders in the repo directly — `sync-push` will detect conflicts and
refuse to overwrite if target files have been modified.

# RULESET R-code-repository
include::
where:: file:{ANCHOR}/.anchor
description:: how an anchor declares & resolves its associated code repository

What `/audit` checks on a `code`-trait anchor's repository association. Format of this set: [[FCT Ruleset]].

### RULE R-code-repository-01 — A `code`-trait anchor declares `code:` in `.anchor` (checked)
check:: anchor_has code

An anchor with the `code` trait carries a `code:` key in its `.anchor`; its presence *is* the declaration that code belongs to this anchor.

**Check pattern:** if `traits` contains `code`, assert a non-empty `code:` key in `.anchor`.

**Why:** the `code:` key is the single source of truth — there is no `Code` symlink and no path-convention fallback.

### RULE R-code-repository-02 — No implicit fallback when `code:` is absent (checked)
check:: no_git_probe_fallback

A `code`-trait anchor with no `code:` key is an error — scripts must fail, never probe for `.git/` at the anchor root or look up a legacy `Code` symlink.

**Check pattern:** resolver errors (does not silently locate a repo) when the trait is present but `code:` is missing.

**Why:** silent fallbacks hide misconfiguration; the spec forbids them generally.

### RULE R-code-repository-03 — Relative `code:` resolves against the anchor root (stated)

An absolute `code:` value is used as-is; a relative value resolves against the **anchor root** (the folder holding `.anchor`), not the caller's cwd; `code: .` is inline mode (repo == anchor root, `.git/` beside `.anchor`).

### RULE R-code-repository-04 — Doc sync flows one way, vault → repo (stated)

`{NAME} User/` and `{NAME} Dev/` doc folders are sync-pushed into the repo's lowercase `docs/user/` and `docs/dev/`; the repo copies are never hand-edited — `sync-push` refuses to overwrite a modified target.

**Why:** docs are authored in the vault; a reverse path would create two sources of truth.

# BRIEF

- **This is a CAB facet spec, not a per-anchor record.** Rules here describe how *any* anchor with the `code` trait declares and resolves its repository — never inline a specific anchor's `code:` value or repo path as canonical content; use [[CAE example]] (or similar) as a worked reference instead.
- **The `code:` key is the single source of truth** — no `Code` symlink, no `.git/`-probing fallback, no path-convention guessing. If you find yourself describing a fallback, stop: this spec forbids them (see § Path resolution) and the surrounding facet rules forbid silent fallbacks generally.
- **Inclusion test for additions:** content belongs here only if it concerns the vault↔repo *association mechanism* (declaration, resolution, inline vs linked, doc sync direction). Repo-internal conventions (justfile shape, test layout, language choices) live in `<App> Dev/` or the repo's own docs — not here.
- **Doc-sync is one-way, vault → repo.** Any edit to this spec that softens that invariant or adds a reverse path is load-bearing — flag it explicitly and update [[FCT Facets]] / related facet specs in the same pass.
- **Don't pile cross-facet rules here.** Trait-wide rules (every `code`-trait anchor) belong in `CAB code.md` (the trait spec); markdown-rendering rules in [[R-markdown]]; project-wide policy in `CLAUDE.md`. This file is scoped to the *code repository association* facet only.
- **Reference example is illustrative, not normative.** The `CAE example/` tree and minimal justfile are condensed for orientation; don't grow them into a full template — point readers at the live anchor instead.
