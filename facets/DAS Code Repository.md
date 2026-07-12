---
description: "facet spec for the code repository association and doc-mirror routes declared in an anchor's `.anchor` file"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Code Repository](hook://p/DAS%20Code%20Repository)
# FCT Code Repository
Facet spec for how an anchor declares and resolves its associated code repository — linked (separate path) or inline — via the `code:` key in `.anchor`.

**Related:** [[DAS Anchor Page]],  [[DAS Traits]],  [[DAS Facet]],  [[FCT Manifest]]
**Examples:** [[OBU\|linked-absolute]],  [[HA\|linked-relative]]

| Table of Contents |  |
|---|---|
| **[[#Location]]** |  |
| **[[#Path resolution]]** |  |
| **[[#Inline vs linked]]** |  |
| **[[#Doc Mirror (`mirror:`)]]** |  |
|    [[#Mirror engine (`code sync`)]] |  |
|    [[#The there side is not an authoring surface]] |  |
|    [[#RULE R-code-repository-01 — A `code`-trait anchor declares `code:` in `.anchor` (checked)]] |  |
|    [[#RULE R-code-repository-02 — No implicit fallback when `code:` is absent (checked)]] |  |
|    [[#RULE R-code-repository-03 — Relative `code:` resolves against the anchor root (stated)]] |  |
|    [[#RULE R-code-repository-04 — Doc mirroring is declared via `mirror:` in `.anchor` (stated)]] |  |
|    [[#RULE R-code-repository-05 — The there side is never an authoring surface (stated)]] |  |

**TLDR** — An anchor with a `code` trait declares its repo via `code:` in `.anchor` (absolute, relative, or `.` for inline). No symlink, no `.git/`-probing fallback. Docs that ship with the repo are kept in sync by the **`mirror:`** key — a local two-folder sync (`here:` in the anchor tree ↔ `there:` anywhere on disk), two-way by default, fully independent of `code:`. **Cardinality: one** — one code repo association per anchor.

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
└── docs/                            Mirrored from CAE Docs/ (two-way)
    ├── user/                        ← mirrors CAE User/
    └── dev/                         ← mirrors CAE Dev/
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

## Doc Mirror (`mirror:`)

When the repo ships the anchor's hand-authored docs (the normal case for
public repos), `.anchor` declares **mirror routes**. `mirror:` is a
**sync-layer** key, fully independent of `code:` (the association layer):
each entry keeps two local folders in sync — nothing more. A `there:`
path that happens to sit inside the code tree is composition, not
coupling.

```yaml
mirror:
  - here: CAE Docs                                # route relative to the anchor root
    there: ~/ob/proj/CAE/cae-example/docs         # absolute path — any local tree
  - here: CAE Schemas
    there: ~/ob/proj/CAE/cae-example/docs/schemas
    direction: push                                # publish-only route
```

- **`here:`** — route relative to the anchor root. **`there:`** — absolute
  (or `~`) path; never resolved against `code:`.
- **`direction:`** — `two-way` (default, omitted) | `push` (here→there
  only; there-side changes are flagged as drift, never ingested) | `pull`
  (there→here only; for ingesting repo-generated artifacts, e.g. a
  CI-built changelog).
- **No `mirror:` key = Separated Docs** — docs exist only at the anchor;
  the repo ships without them. Normal for private repos.

### Mirror engine (`code sync`)

Three-way sync per file: the here copy, the there copy, and a
last-synced hash manifest (kept in the enclosing repo's `.git/`,
local-only by construction). Forward (here→there) transfers freely; the
mirrored change then rides the next code commit — code + docs commit
atomically in the one clone. **Backward (there→here) transfers only
changes that arrived via git history**: the engine discovers any repo
enclosing `there:` by walking up; a there-side change on a *clean* path
(arrived by commit/pull) syncs back, while an *uncommitted* there-side
edit is **quarantined and flagged, never transported**. Both-sides-changed
is a conflict — flagged, resolved on the here side, then explicitly
taken. No auto-merge, ever. With no enclosing repo, the engine degrades
to plain three-way folder sync with conflict flags.

### The there side is not an authoring surface

Docs are authored at the anchor (here side) by user and agents alike.
Three guards keep edits off the there side: the sync stamps there-side
files **read-only**; a Warden rule denies agent writes into declared
there-paths (the deny message names the here-side original); the repo's
`CLAUDE.md` states the routes and points home. Even a guard-evading edit
only reaches the quarantine flag — it cannot silently enter the anchor.

Design rationale, alternatives considered, and the trade-off matrix:
[[SKA Code-Docs Design]] (dev-side). Predecessor mechanisms — one-way
`sync-push` (retired) and sparse-checkout-into-the-anchor
([[Anchor Remotes]], rejected) — are superseded by this section.

# RULESET R-code-repository
include::
where:: `file:{anchor}/.anchor`
description:: how an anchor declares & resolves its associated code repository

What `/audit` checks on a `code`-trait anchor's repository association. Format of this set: [[DAS Ruleset]].

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

### RULE R-code-repository-04 — Doc mirroring is declared via `mirror:` in `.anchor` (stated)

Each route carries `here:` (anchor-root-relative) + `there:` (absolute path) + optional `direction:` (`two-way` default | `push` | `pull`). `mirror:` is independent of `code:` — it syncs two local folders; `there:` is never resolved against the code checkout.

**Why:** association ("where is the code") and sync ("what mirrors where") are different layers; coupling them was the old spec's hidden dependency.

### RULE R-code-repository-05 — The there side is never an authoring surface (stated)

Backward transport happens only for changes that arrived via git commits; uncommitted there-side edits are quarantined and flagged. The sync stamps there-side copies read-only.

**Why:** the here side is where user and agents co-author; silent backward flow would collide with live edits.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. This is a CAB facet spec, never a per-anchor record — don't inline a specific anchor's `code:` value or repo path as canonical content; use [[CAE example]] (or similar) as a worked reference. The normative spec is the body above.)*

- **Inclusion test** — content belongs here only if it concerns the vault↔repo *association mechanism* (declaration, resolution, inline vs linked, doc-sync direction). Repo-internal conventions (justfile shape, test layout, language choices) live in `<App> Dev/` or the repo's own docs; trait-wide rules in `CAB code.md`; markdown-rendering rules in [[R-markdown]]; project-wide policy in `CLAUDE.md`.
- **Two load-bearing invariants — don't soften them:** the `code:` key is the single source of truth (no symlink / `.git/`-probing / path-convention fallback), and the mirror's backward leg transports **only committed changes** (uncommitted there-side edits quarantine — the there side is never an authoring surface). Any edit weakening either must be flagged explicitly, with [[FCT Facets]] / related facet specs updated in the same pass.
- **Reference example stays condensed** — the `CAE example/` tree and minimal justfile are illustrative orientation, not normative; don't grow them into a full template — point readers at the live anchor.
