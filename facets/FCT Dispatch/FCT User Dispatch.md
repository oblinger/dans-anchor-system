---
description: user-facing docs dispatch page — curated, synthesis-level human-authored docs for any audience
---
# FCT User Dispatch

Facet spec for the `{NAME} User.md` dispatch page that catalogs an anchor's end-user / consumer-facing documentation (Guide, Installation, CLI, FAQ, Cards).

**Location:** `{NAME} Docs/{NAME} User/{NAME} User.md`


The `{NAME} User.md` dispatch page inside the `{NAME} User/` folder. Lists **end-user / consumer-facing documentation** for the anchor — Guide, Installation, CLI reference, FAQ, Cards.

Per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] Q3=A (2026-06-01), the User folder scope tightens to **end-user / consumer documentation only**. System-spec docs (Interface, Architecture, UX Design, Data Model, Principles) live in [[FCT Design Dispatch|Design]] instead — even when their content is "public-facing," because they describe the system's contract, not an end-user task.

## Audience — end users and consumers

The User folder is for **anyone reading the docs to *use* the system as a consumer**, not to understand or evolve its design. Specifically:

- **End users** read the Guide for getting started.
- **Operators** read Installation for setup.
- **CLI users** read the CLI reference for exact syntax.
- **Anyone** reads the FAQ for quick answers.

System-level audiences (integrators-above-the-layer, architects, designers) read [[FCT Design Dispatch|Design]] instead — that's where Interface (the layer contract) and Architecture (the system structure) now live per F094.

The defining property is **what the content describes**: User docs describe *user tasks*; Design docs describe *system shape*. Compare with [[FCT Dev Dispatch]] which holds **audit-tied, machine-checkable reference** (Files tree, per-module docs).

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE User/CAE User.md` — User dispatch.

# Reference Example
---


# CAE User

| -[[CAE User]]- | ><br>: end-user / consumer documentation |
| --- | --- |
| [[CAE Guide\|Guide]] | getting started and usage |
| [[CAE Installation\|Installation]] | installation instructions (when applicable) |
| [[CAE CLI\|CLI]] | CLI command reference (when applicable) |
| [[CAE FAQ\|FAQ]] | frequently asked questions (when applicable) |
| [[CAE Cards\|Cards]] | cheat sheets and flashcards |

---



# Format Specification

## Location

`{NAME} User.md` lives inside `{NAME} Docs/{NAME} User/`.

## Structure (per F060)

- **YAML frontmatter** — optional.
- **H1** — `# {NAME} User`. Blank line after.
- **Dispatch table** — top-left cell is `-[[{NAME} User]]-`, top-right is `><br>: user-facing documentation` (or `+>` legacy shorthand).
- **Body rows** — one row per user-facing document.
- **Auto-management separator** — a `---` row enables auto-listing of remaining children.

## Filename convention — `{NAME} Guide.md`, not `{NAME} User Guide.md`

The folder context (`{NAME} User/`) already supplies "user-facing" — putting "User" in the filename too is redundant. Use `{NAME} Guide.md` as the basename for the primary user-facing guide.

The H1 *inside* the file may still be `# {NAME} User Guide` if the verbose title reads better at the top of the document — the file basename is for the index/wiki-link surface; the H1 is for the reader. Either is fine.

For multi-guide anchors (rare), variants are `{NAME} {Topic} Guide.md` — e.g., `CAE Setup Guide.md`, `CAE Migration Guide.md`. The bare `{NAME} Guide.md` is the canonical top-level entry point.

## Contents

Typical entries include:

| Document | Description |
|----------|-------------|
| `{NAME} Guide.md` | Getting started, installation, usage (the primary user-facing guide) |
| `{NAME} Interface.md` | Top-level layer contract — see [[FCT Interface]] (required for code anchors) |
| `{NAME} Architecture.md` | System-level architecture overview |
| `{NAME} Cards.md` | Cheat sheets and flashcards |
| `{NAME} {Topic} Guide.md` | Topic-specific guides for specialized workflows |

For code anchors, the Interface is **required** (`/audit docs` flags absence as `missing-interface`); the other rows are optional and listed only when those docs exist. For non-code anchors (`simple`, `topic`, `paper`), Interface and Architecture are typically absent.

## Migration note

Anchors that still have `{NAME} User Guide.md` continue to resolve correctly (wiki-links by basename). The rename to `{NAME} Guide.md` happens organically when an anchor is touched. Don't bulk-rename retroactively.

Anchors that still have `{NAME} Rollup.md` (the predecessor to Interface — see F062) continue to resolve correctly for now, but should be renamed to `{NAME} Interface.md` when the anchor is next touched. The semantic shift (Rollup was a loose summarization pattern; Interface is a tightened layer contract with a user-validation gate) usually warrants a content review at rename time. Migration is forward-only; no bulk pass.

# BRIEF

- **This is the facet spec for the User dispatch page** — `{NAME} User.md` inside `{NAME} Docs/{NAME} User/`. Edits here change how every anchor's User dispatch is structured; cross-check the Reference Example and Format Specification stay in sync.
- **In-scope content is consumer/end-user task documentation only** — Guide, Installation, CLI, FAQ, Cards. Per F094 Q3=A (2026-06-01), system-spec docs (Interface, Architecture, UX Design, Data Model, Principles) belong in [[FCT Design Dispatch|Design]], even when public-facing — don't drift them back here.
- **Inclusion test** — ask "does this doc describe a *user task*, or does it describe the *system's shape/contract*?" Task-shaped → User. Shape-shaped → Design. Machine-checkable per-module reference → [[FCT Dev Dispatch|Dev]].
- **Filename convention is load-bearing** — `{NAME} Guide.md` (not `{NAME} User Guide.md`); the folder context already supplies "user-facing." H1 inside the file may still spell out "User Guide" if it reads better. Don't bulk-rename legacy `{NAME} User Guide.md` or `{NAME} Rollup.md` — migration is forward-only when the anchor is next touched.
- **Dispatch table header is fixed** — top-left `-[[{NAME} User]]-`, top-right `><br>: end-user / consumer documentation` (legacy `+>` shorthand still accepted). A `---` separator row enables auto-listing of remaining children — preserve it when present.
- **Don't pile facet-shape rules from sibling dispatches here** — Design / Dev / Track facet specifics live in their own CAB facet files. This file owns only the User dispatch rules; cross-link, don't inline.
- **Working example is canonical** — `~/.claude/skills/CAE/CAE Docs/CAE User/CAE User.md`. If the example and the spec disagree, fix one or the other; don't leave them drifted.
