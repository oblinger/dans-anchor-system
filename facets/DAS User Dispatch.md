---
description: user-facing docs dispatch page — curated, synthesis-level human-authored docs for any audience
---

# DAS User Dispatch
Facet spec for the `{slug} User Docs.md` dispatch page that catalogs an anchor's end-user / consumer-facing documentation (Guide, Installation, CLI, FAQ, Cards).

| -[[DAS User Dispatch]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS User Dispatch](hook://p/DAS%20User%20Dispatch) |
| --- | --- |
| Related | [[DAS Design Dispatch]],  [[DAS Dev Dispatch]],  [[DAS Track Dispatch]],  [[DAS Dispatch]],   |
| Examples | [[HBR User Docs\|minimal (code anchor)]],  [[HBR User Docs\|fuller (server anchor)]],   |
| Rules | [[R-fct-user-dispatch]],   |

**TLDR** — `{slug} User Docs.md` is the dispatch page for end-user / consumer-facing documentation (Guide, Installation, CLI, FAQ, Cards). It lives in the root-level `{slug} User Docs/` folder. Cardinality: **one per anchor**. Scope boundary: user-task docs only; system-spec docs (Interface, Architecture) live elsewhere — Interface in [[DAS Design Dispatch|Design]], the Architecture story in `{slug} Design/`.

The `{slug} User Docs.md` dispatch page inside the root-level `{slug} User Docs/` folder. Lists **end-user / consumer-facing documentation** for the anchor — Guide, Installation, CLI reference, FAQ, Cards.

Per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] Q3=A (2026-06-01), the User Docs folder scope is **end-user / consumer documentation only**. System-spec docs (Interface, UX Design, Data Model, Principles) live in [[DAS Design Dispatch|Design]], and the system-architecture story lives in `{slug} Design/` — even when their content is "public-facing," because they describe the system's contract, not an end-user task.

## Audience — end users and consumers

The User folder is for **anyone reading the docs to *use* the system as a consumer**, not to understand or evolve its design. Specifically:

- **End users** read the Guide for getting started.
- **Operators** read Installation for setup.
- **CLI users** read the CLI reference for exact syntax.
- **Anyone** reads the FAQ for quick answers.

System-level audiences (integrators-above-the-layer, architects, designers) read [[DAS Design Dispatch|Design]] (the Interface layer contract) and the `{slug} Architecture` doc in `{slug} Design/` (the system structure) instead.

The defining property is **what the content describes**: User docs describe *user tasks*; Design docs describe *system shape*. Compare with [[DAS Dev Dispatch]] which holds **audit-tied, machine-checkable reference** (Files tree, per-module docs).

**Cardinality: one per anchor.** Every anchor has exactly one root-level `{slug} User Docs/` folder with one `{slug} User Docs.md` dispatch page.

**Working example:** `HBR User Docs/HBR User Docs.md` — User Docs dispatch.

# Reference Example
---

# CAE User Docs

| -[[HBR User Docs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Dispatch]] → [DAS User Dispatch](hook://p/DAS%20User%20Dispatch)<br>: end-user / consumer documentation |
| --- | --- |
| [[HBR Guide\|Guide]] | getting started and usage |
| [[CAE Installation\|Installation]] | installation instructions (when applicable) |
| [[HBR CLI\|CLI]] | CLI command reference (when applicable) |
| [[CAE FAQ\|FAQ]] | frequently asked questions (when applicable) |
| [[CAE Cards\|Cards]] | cheat sheets and flashcards |

---

# Format Specification

## Location

`{slug} User Docs.md` lives inside the root-level `{slug} User Docs/` folder.

## Structure (per F060)

- **YAML frontmatter** — optional.
- **H1** — `# {slug} User Docs`. Blank line after.
-[[{slug} User Docs]]-`, top-right is `><br>: user-facing documentation` (or `+>` legacy shorthand).
- **Body rows** — one row per user-facing document.
- **Auto-management separator** — a `---` row enables auto-listing of remaining children.

## Filename convention — `{slug} Guide.md`, not `{slug} User Guide.md`

The folder context (`{slug} User Docs/`) already supplies "user-facing" — putting "User" in the filename too is redundant. Use `{slug} Guide.md` as the basename for the primary user-facing guide.

The H1 *inside* the file may still be `# {slug} User Guide` if the verbose title reads better at the top of the document — the file basename is for the index/wiki-link surface; the H1 is for the reader. Either is fine.

For multi-guide anchors (rare), variants are `{slug} {Topic} Guide.md` — e.g., `CAE Setup Guide.md`, `CAE Migration Guide.md`. The bare `{slug} Guide.md` is the canonical top-level entry point.

## Contents

Typical entries include:

| Document | Description |
|----------|-------------|
| `{slug} Guide.md` | Getting started, installation, usage (the primary user-facing guide) |
| `{slug} Installation.md` | Installation instructions (when applicable) |
| `{slug} CLI.md` | CLI command reference (when applicable) |
| `{slug} FAQ.md` | User-facing FAQs (when applicable) |
| `{slug} Cards.md` | Cheat sheets and flashcards |
| `{slug} {Topic} Guide.md` | Topic-specific guides for specialized workflows |

All rows are optional except the primary Guide, and are listed only when those docs exist. The system-spec docs (Interface, Architecture) are **not** User Docs — Interface lives in `{slug} Design/` (`/audit docs` flags its absence on a code anchor as `missing-interface`), and the Architecture story lives in `{slug} Design/`.

## Migration note

Anchors that still have `{slug} User Guide.md` continue to resolve correctly (wiki-links by basename). The rename to `{slug} Guide.md` happens organically when an anchor is touched. Don't bulk-rename retroactively.

Anchors that still have `{slug} Rollup.md` (the predecessor to Interface — see F062) continue to resolve correctly for now, but should be renamed to `{slug} Interface.md` when the anchor is next touched. The semantic shift (Rollup was a loose summarization pattern; Interface is a tightened layer contract with a user-validation gate) usually warrants a content review at rename time. Migration is forward-only; no bulk pass.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + RULESET R-fct-user-dispatch above.)*

- **Keep the Reference Example, Format Specification, and the working example (`HBR User Docs/HBR User Docs.md`) in sync** — edits here change every anchor's User Docs dispatch; if the example and the spec disagree, fix one, don't leave them drifted.
- **Don't inline sibling-dispatch rules here** — Design / Dev Docs / Track facet specifics live in their own DAS facet files; this file owns only the User Docs dispatch rules. Cross-link, don't duplicate.
