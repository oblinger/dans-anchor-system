---
description: user-facing docs dispatch page — curated, synthesis-level human-authored docs for any audience
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT User Dispatch](hook://p/FCT%20User%20Dispatch)

# FCT User Dispatch
Facet spec for the `{NAME} User Docs.md` dispatch page that catalogs an anchor's end-user / consumer-facing documentation (Guide, Installation, CLI, FAQ, Cards).

**Related:** [[FCT Design Dispatch]],  [[FCT Dev Dispatch]],  [[FCT Track Dispatch]],  [[FCT Dispatch]]
**Examples:** [[CAE User Docs\|minimal (code anchor)]],  [[HBR User Docs\|fuller (server anchor)]]

**TLDR** — `{NAME} User Docs.md` is the dispatch page for end-user / consumer-facing documentation (Guide, Installation, CLI, FAQ, Cards). It lives in the root-level `{NAME} User Docs/` folder. Cardinality: **one per anchor**. Scope boundary: user-task docs only; system-spec docs (Interface, Architecture) live elsewhere — Interface in [[FCT Design Dispatch|Design]], the Architecture story in `{NAME} Design/`.

The `{NAME} User Docs.md` dispatch page inside the root-level `{NAME} User Docs/` folder. Lists **end-user / consumer-facing documentation** for the anchor — Guide, Installation, CLI reference, FAQ, Cards.

Per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] Q3=A (2026-06-01), the User Docs folder scope is **end-user / consumer documentation only**. System-spec docs (Interface, UX Design, Data Model, Principles) live in [[FCT Design Dispatch|Design]], and the system-architecture story lives in `{NAME} Design/` — even when their content is "public-facing," because they describe the system's contract, not an end-user task.

## Audience — end users and consumers

The User folder is for **anyone reading the docs to *use* the system as a consumer**, not to understand or evolve its design. Specifically:

- **End users** read the Guide for getting started.
- **Operators** read Installation for setup.
- **CLI users** read the CLI reference for exact syntax.
- **Anyone** reads the FAQ for quick answers.

System-level audiences (integrators-above-the-layer, architects, designers) read [[FCT Design Dispatch|Design]] (the Interface layer contract) and the `{NAME} Architecture` doc in `{NAME} Design/` (the system structure) instead.

The defining property is **what the content describes**: User docs describe *user tasks*; Design docs describe *system shape*. Compare with [[FCT Dev Dispatch]] which holds **audit-tied, machine-checkable reference** (Files tree, per-module docs).

**Cardinality: one per anchor.** Every anchor has exactly one root-level `{NAME} User Docs/` folder with one `{NAME} User Docs.md` dispatch page.

**Working example:** `HBR User Docs/HBR User Docs.md` — User Docs dispatch.

# Reference Example
---

# CAE User Docs

| -[[CAE User Docs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT User Dispatch](hook://p/FCT%20User%20Dispatch)<br>: end-user / consumer documentation |
| --- | --- |
| [[CAE Guide\|Guide]] | getting started and usage |
| [[CAE Installation\|Installation]] | installation instructions (when applicable) |
| [[CAE CLI\|CLI]] | CLI command reference (when applicable) |
| [[CAE FAQ\|FAQ]] | frequently asked questions (when applicable) |
| [[CAE Cards\|Cards]] | cheat sheets and flashcards |

---

# Format Specification

## Location

`{NAME} User Docs.md` lives inside the root-level `{NAME} User Docs/` folder.

## Structure (per F060)

- **YAML frontmatter** — optional.
- **H1** — `# {NAME} User Docs`. Blank line after.
-[[{NAME} User Docs]]-`, top-right is `><br>: user-facing documentation` (or `+>` legacy shorthand).
- **Body rows** — one row per user-facing document.
- **Auto-management separator** — a `---` row enables auto-listing of remaining children.

## Filename convention — `{NAME} Guide.md`, not `{NAME} User Guide.md`

The folder context (`{NAME} User Docs/`) already supplies "user-facing" — putting "User" in the filename too is redundant. Use `{NAME} Guide.md` as the basename for the primary user-facing guide.

The H1 *inside* the file may still be `# {NAME} User Guide` if the verbose title reads better at the top of the document — the file basename is for the index/wiki-link surface; the H1 is for the reader. Either is fine.

For multi-guide anchors (rare), variants are `{NAME} {Topic} Guide.md` — e.g., `CAE Setup Guide.md`, `CAE Migration Guide.md`. The bare `{NAME} Guide.md` is the canonical top-level entry point.

## Contents

Typical entries include:

| Document | Description |
|----------|-------------|
| `{NAME} Guide.md` | Getting started, installation, usage (the primary user-facing guide) |
| `{NAME} Installation.md` | Installation instructions (when applicable) |
| `{NAME} CLI.md` | CLI command reference (when applicable) |
| `{NAME} FAQ.md` | User-facing FAQs (when applicable) |
| `{NAME} Cards.md` | Cheat sheets and flashcards |
| `{NAME} {Topic} Guide.md` | Topic-specific guides for specialized workflows |

All rows are optional except the primary Guide, and are listed only when those docs exist. The system-spec docs (Interface, Architecture) are **not** User Docs — Interface lives in `{NAME} Design/` (`/audit docs` flags its absence on a code anchor as `missing-interface`), and the Architecture story lives in `{NAME} Design/`.

## Migration note

Anchors that still have `{NAME} User Guide.md` continue to resolve correctly (wiki-links by basename). The rename to `{NAME} Guide.md` happens organically when an anchor is touched. Don't bulk-rename retroactively.

Anchors that still have `{NAME} Rollup.md` (the predecessor to Interface — see F062) continue to resolve correctly for now, but should be renamed to `{NAME} Interface.md` when the anchor is next touched. The semantic shift (Rollup was a loose summarization pattern; Interface is a tightened layer contract with a user-validation gate) usually warrants a content review at rename time. Migration is forward-only; no bulk pass.

# RULESET R-fct-user-dispatch
include::
where:: file: **/{NAME} User Docs/{NAME} User Docs.md
description:: Rules every `{NAME} User Docs.md` dispatch page must satisfy — the file must exist in the right location, open with the right dispatch-table header, and contain only user-task-shaped documentation (not system-spec docs).

### RULE R-fct-user-dispatch-01 — file lives at the correct path (checked)
The dispatch page is at `{NAME} User Docs/{NAME} User Docs.md` — a root-level folder.
**Check pattern:** path matches `{NAME} User Docs/{NAME} User Docs.md`.
**Why:** the folder context supplies the "User Docs" qualifier; a misfiled page is invisible to dispatch resolution.

### RULE R-fct-user-dispatch-02 — dispatch table top-left cell is the self-link (checked)
-[[{NAME} User Docs]]-` in the left cell and a brief description beginning with `>` or `+>` in the right cell.
**Check pattern:** first table row matches `-\[\[.+ User Docs\]\]-` in cell 1 and starts with `>` or `+>` in cell 2.
**Why:** the self-link is what makes the dispatch table navigable; wrong or absent cell breaks the anchor-page contract per F060.

### RULE R-fct-user-dispatch-03 — contains only user-task documentation (sampled)
Every body row links a doc that describes a *user task* (Guide, Installation, CLI, FAQ, Cards) — not a system-spec doc (Interface, Architecture, UX Design, Data Model, Principles), which belong in [[FCT Design Dispatch|Design]] per F094.
**Check pattern:** body rows do not link `{NAME} Interface.md`, `{NAME} Architecture.md`, `{NAME} Data Model.md`, `{NAME} Principles.md`, or `{NAME} UX Design.md`.
**Why:** scope leakage lets Design docs accumulate here; the F094 boundary is load-bearing for `/audit docs`.

### RULE R-fct-user-dispatch-04 — primary guide uses bare filename (stated)
The primary user-facing guide is `{NAME} Guide.md`, not `{NAME} User Guide.md`. The folder context already supplies "user-facing."
**Check pattern:** no file named `{NAME} User Guide.md` is linked as the primary row (legacy files may exist pending forward-migration).
**Why:** the filename convention prevents "User User Guide" redundancy and is the canonical form going forward.

# BRIEF

- **This is the facet spec for the User Docs dispatch page** — `{NAME} User Docs.md` inside the root-level `{NAME} User Docs/` folder. Edits here change how every anchor's User Docs dispatch is structured; cross-check the Reference Example and Format Specification stay in sync.
- **In-scope content is consumer/end-user task documentation only** — Guide, Installation, CLI, FAQ, Cards. System-spec docs (Interface, UX Design, Data Model, Principles) belong in [[FCT Design Dispatch|Design]] and the Architecture story in `{NAME} Design/`, even when public-facing — don't drift them back here.
- **Inclusion test** — ask "does this doc describe a *user task*, or does it describe the *system's shape/contract*?" Task-shaped → User Docs. Shape-shaped → Design (or the Architecture folder). Machine-checkable per-module reference → [[FCT Dev Dispatch|Dev Docs]].
- **Filename convention is load-bearing** — `{NAME} Guide.md` (not `{NAME} User Guide.md`); the folder context already supplies "user-facing." H1 inside the file may still spell out "User Guide" if it reads better. Don't bulk-rename legacy `{NAME} User Guide.md` or `{NAME} Rollup.md` — migration is forward-only when the anchor is next touched.
-[[{NAME} User Docs]]-`, top-right `><br>: end-user / consumer documentation` (legacy `+>` shorthand still accepted). A `---` separator row enables auto-listing of remaining children — preserve it when present.
- **Don't pile facet-shape rules from sibling dispatches here** — Design / Dev Docs / Track facet specifics live in their own CAB facet files. This file owns only the User Docs dispatch rules; cross-link, don't inline.
- **Working example is canonical** — `HBR User Docs/HBR User Docs.md`. If the example and the spec disagree, fix one or the other; don't leave them drifted.
