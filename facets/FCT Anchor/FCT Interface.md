---
description: top-level human-authored layer contract — complete vocabulary for using the layer, hides everything below
---

# FCT Interface

The facet spec for `{NAME} Interface.md` — the top-level human-authored layer contract on a code anchor, defining the complete caller-facing vocabulary while hiding the implementation below.

**Location:** `{NAME} Docs/{NAME} Design/{NAME} Interface.md`

(Relocated from `{NAME} User/` per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] Q3=A — 2026-06-01. Interface describes a *system contract callers consume*, not an end-user task; it belongs in [[FCT Design Dispatch|Design]] alongside Architecture + UX Design + Data Model + Principles, not in [[FCT User Dispatch|User]].)

`{NAME} Interface.md` is the **top-level human-authored layer contract** for a code anchor — the complete vocabulary a caller needs to use the layer, written explicitly enough that the caller does not have to descend into the layer below.

## Defining Properties

An Interface document is defined by four invariants:

1. **Layer-completeness.** It describes everything a caller above the layer needs to use the layer — types, operations, invariants, error modes, lifecycle, conceptual model. A reader using this layer should not need to read the layer below it.
2. **Hiding.** Within the constraint of completeness, the Interface hides as much as it can. Implementation details that are not part of the contract are not surfaced. The Interface is the *contract*, not the *implementation*.
3. **Human-authored.** Drafts may be scaffolded (`rewire` creates an empty scaffold when missing), but every Interface ships through human review and editing. Interfaces are designed.
4. **Human-audited.** New Interface docs and significant modifications go through a user-validation gate (see [[SKA workflow]] § Interface-validation gate). The user reads and approves; the agent drafts and proposes.

These four invariants distinguish Interface from related facets:

- **Module Docs** are auto-generated ground-truth reference for one module in isolation — complete *for that module*, not for the layer as a whole. Module docs are great for code-level lookup but bad for understanding a layer's contract.
- **Architecture** describes how the system is structured internally (component diagrams, thread model, data flow) — it's the *how*, not the *what-callers-see*.
- **Guide** is task-oriented teaching ("how do I do X with this?") — useful, but not constrained by the completeness invariant; a Guide is allowed to be partial.

The Interface is the *what callers see, completely*. That property is unique to this facet.

## Trait Applicability

**Required** for anchors with the `code` trait — every code anchor MUST have a top-level Interface doc.

Other traits (`simple`, `topic`, `paper`) typically don't have an Interface — they don't expose a programmable surface. Exception: a `topic` anchor that documents a logical layer (e.g. a cross-system protocol) may have one.

## Sub-Interfaces — Nested Layers

A code anchor often has internal layers worth documenting separately — an internal library, a subsystem with its own API, a protocol stack. Each such layer gets its own `{NAME} {LayerName} Interface.md` alongside the top-level one. Sub-Interfaces sit one level below the top-level Interface in the User dispatch (or in a layer-specific subfolder for deep nestings).

Example shapes:

- Single Interface — small codebase, one layer worth describing.
  - `OBU Interface.md`
- Top + sub-Interfaces — larger codebase with internal layers.
  - `MUX Interface.md` (top — describes what the whole app exposes)
  - `MUX Protocol Interface.md` (sub — the wire protocol contract)
  - `MUX Storage Interface.md` (sub — the persistence layer's API)

Each sub-Interface satisfies the four invariants *for its own layer*. The top-level Interface points to sub-Interfaces in its `## See Also` section.

## Required Links

Two structural links every Interface must satisfy — `/audit docs` enforces these:

1. **`{NAME} Files.md` row 1** (the repo-root row) ends with `→ [[{NAME} Interface]]`. The wiki-link resolves by basename. This is the entry point for anyone reading the file tree: "start here for the layer contract."
2. **`{NAME} User.md` dispatch page** lists `[[{NAME} Interface]]` as a top entry, alongside Guide / Architecture / Cards.

## Document Structure

An Interface composes from canonical section types. Pick the ones that apply; not every layer has all of them.

| Section | When to include | Purpose |
|---------|-----------------|---------|
| H1 `# {NAME} Interface` | always | Title |
| Dispatch-table placeholder (per F060) | always | `\| -[[{NAME} Interface]]- \| \|` + standard separator; rewire fills in breadcrumb cell. |
| Brief paragraph | always | What layer this is + what callers above the layer gain access to |
| "Top-level layer contract" line | always (top-level Interface) | Explicit statement that this is THE top-level Interface for the anchor (or names which layer for a sub-Interface) |
| Source line | always (code anchors) | Absolute path to the root module / entry point |
| `## Public Modules` | when the layer has named modules | One table listing every module exposed by this layer with a one-line description |
| `## How They Group` | when modules cluster meaningfully | Groupings — the conceptual vocabulary a caller picks from |
| `## {module}` sections | when modules have classes/functions worth surfacing | One per module. Brief tagline + `See [[{NAME} {Module}]] for detail.` + per-class CLASSES and FUNCTIONS tables |
| `## Schemas` | when the layer produces or consumes typed data | Field-level tables; one H3 per schema |
| `## File Formats` | when the layer reads/writes files that are part of the contract | One H3 per file format |
| `## CLI Surface` | when the layer exposes a CLI | Table of commands with one-line purpose; exit codes |
| `## Error Types` | when callers see typed errors | Variant table — when each fires |
| `## Constants` | when published constants are part of the contract | Table of name / value / purpose |
| `## What's Hidden` | optional but recommended | Explicit note on what callers do NOT need to know — what the Interface is *protecting* the caller from. Naming the hiding helps maintain the discipline. |
| `## See Also` | always | Architecture, Files, sub-Interfaces, Principles |

The rule of thumb: **if a caller above the layer needs to know it to use the layer, it's Interface material. If they don't, it stays hidden.**

## The Hiding Invariant

A common drift is for Interface docs to "leak" — they start as a layer contract and grow to describe internal mechanics. Resist this. When tempted to add a section, ask: *would a caller above this layer need this to use the layer correctly?*

- If yes → it's Interface material.
- If no → it belongs in Architecture (for design rationale), in a Module Doc (for implementation detail), or nowhere (for things not worth documenting).

The `## What's Hidden` section is a self-documenting check: writing "callers do not need to know about X, Y, Z" forces the author to name the hiding boundary explicitly, and prevents future agents from drifting the doc across it.

## Lifecycle

- **Create** — `rewire` scaffolds the file when missing on a code anchor; the scaffold is empty (TODOs in each section). Rewire also files a backlog row `## Now [Designing] — F<n> Author top-level Interface for {NAME}` to surface the missing-content work.
- **Author** — the user collaborates with the agent to fill in the scaffold. This is design-bearing work; goes through `[Designing]` → `[Ready]` only after user agreement on the layer contract.
- **Validate** — promotion to `[Done]` requires user verification that the Interface accurately describes the layer. See [[SKA workflow]] § Interface-validation gate.
- **Maintain** — Interface drifts when callers see surface changes. Significant API additions, removals, renames, or conceptual-model changes go through the validation gate again. Cosmetic edits don't.
- **Split** — when a top-level Interface crosses ~500 lines, introduce sub-Interfaces for the internal layers; the top shrinks to a layer-index + the cross-cutting contract pieces.

## Relationship to the Root-Module Doc

In languages with a single entry-point module (Rust `lib.rs`, Python `__init__.py`, TypeScript `index.ts`), the Interface often *replaces* the module doc for that root. The root module is usually pure re-exports, so its "module doc" would be a de facto Interface anyway. Renaming `{NAME} Lib.md` → `{NAME} Interface.md` makes the role explicit.

In codebases without a clear single root (multi-binary workspaces, monorepos), the Interface is a standalone synthesis over the whole codebase.

## Audit Categories

`/audit docs` checks (see [[audit-docs]] § 1.8):

- `missing-interface` — no `{NAME} Interface.md` exists on a code anchor.
- `interface-not-linked-from-files` — `{NAME} Files.md` row 1 doesn't end with `→ [[{NAME} Interface]]`.
- `interface-not-linked-from-dispatch` — `{NAME} User.md` doesn't list `[[{NAME} Interface]]`.
- `interface-incomplete-structure` — required sections (`## Public Modules` and at least one of: `## How They Group`, `## {module}`, `## Schemas`, `## CLI Surface`) are absent.
- `interface-module-missing` — Interface omits a public module that exists in source.
- `interface-too-large` — Interface exceeds ~500 lines (suggest splitting into sub-Interfaces).

## Cross-references

- **[[FCT Files]]** — the audit-tied tree; Interface is linked from row 1.
- **[[FCT API Doc]]** — auto-generated per-module reference; Interface is the human-authored layer contract that groups modules into a vocabulary.
- **[[FCT Architecture]]** — the *how* (internal structure, flow, design rationale); Interface is the *what callers see*.
- **[[FCT User Dispatch]]** — Interface lives here.
- **[[SKA workflow]]** § Interface-validation gate — user-collaboration gate for new and significantly-modified Interfaces.
- **[[SKA rewire]]** — creates the scaffold and files the backlog row when an Interface is missing.

# BRIEF

- **This file is the CAB facet spec for Interface docs** — it defines the four invariants (layer-completeness, hiding, human-authored, human-audited), the trait applicability, the canonical section menu, the required links, and the audit categories that govern every `{NAME} Interface.md` in the vault.
- **NOT for per-anchor Interface content** — concrete Interface text for OBU, MUX, etc. lives in those anchors' own `{NAME} Interface.md`; this file holds only the rule, never an instance of the rule.
- **Inclusion test** — a change belongs here only if it alters the contract every Interface doc must satisfy (invariants, required sections, required links, lifecycle gates, audit checks). Anchor-specific guidance, scaffold templates, and rewire mechanics belong in [[SKA rewire]] or the anchor itself, not here.
- **Load-bearing constraints to preserve** — the four Defining Properties, the two Required Links (`{NAME} Files.md` row 1 ends with `→ [[{NAME} Interface]]`; `{NAME} User.md` lists it), the `## What's Hidden` self-check pattern, and the audit category names under § Audit Categories (those names are cited by `/audit docs`); do not rename or drop without updating callers.
- **Cross-spec consistency** — when editing, keep aligned with [[FCT Files]] (row 1 link contract), [[FCT API Doc]] (auto-generated vs. human-authored split), [[FCT Architecture]] (the *how* vs. *what callers see* distinction), [[FCT User Dispatch]] (location/listing), and [[SKA workflow]] (validation gate). A drift here propagates to all of them.
- **Section menu is a menu, not a checklist** — the `## Document Structure` table lists canonical sections; not every Interface uses all of them. Don't add "always required" to optional rows or remove rows because some anchor doesn't use them.
- **Hiding discipline applies to this spec too** — resist adding implementation-detail prose about how rewire scaffolds, how validation runs, or how audits execute; link to [[SKA rewire]] / [[SKA workflow]] / [[audit-docs]] and let those own the mechanics.
