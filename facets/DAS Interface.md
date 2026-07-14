---
description: top-level human-authored layer contract — complete vocabulary for using the layer, hides everything below
---

# FCT Interface
The facet spec for `{slug} Interface.md` — the top-level human-authored layer contract on a code anchor, defining the complete caller-facing vocabulary while hiding the implementation below.

| -[[DAS Interface]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Interface](hook://p/DAS%20Interface) |
| --- | --- |
| Related | [[DAS Architecture]],  [[DAS Module Doc]],  [[DAS User Dispatch]],  [[DAS All Files]],   |
| Examples | [[HA Interface\|minimal — CLI tool, one caller surface]],  [[MUX Interface\|fuller — app with multiple caller surfaces + sub-Interfaces]],   |
| Rules | [[DAS Interface#RULESET R-fct-interface\|R-fct-interface]],   |
|  |  |
| **Table of Contents** |  |
| [[#Defining Properties]] |  |
| [[#Trait Applicability]] |  |
| [[#Sub-Interfaces — Nested Layers]] |  |
| [[#Required Links]] |  |
| [[#Document Structure]] |  |
| [[#The Hiding Invariant]] |  |
| [[#Lifecycle]] |  |
| [[#Relationship to the Root-Module Doc]] |  |
| [[#Audit Categories]] |  |
| [[#Cross-references]] |  |
| **[[#BRIEF]]** |  |

**TLDR** — `{slug} Interface.md` is the **one** doc a caller reads to fully use a code anchor's layer — layer-complete, hiding, human-authored, and human-audited. Required on every `code`-trait anchor. **Cardinality: one per anchor** (plus optional named sub-Interfaces for internal layers). Audited by `/audit docs` under `§ 1.8`; scaffolded by `rewire`.

**Location:** `{slug} Docs/{slug} Design/{slug} Interface.md`

(Relocated from `{slug} User/` per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] Q3=A — 2026-06-01. Interface describes a *system contract callers consume*, not an end-user task; it belongs in [[DAS Design Dispatch|Design]] alongside Architecture + UX Design + Data Model + Principles, not in [[DAS User Dispatch|User]].)

`{slug} Interface.md` is the **top-level human-authored layer contract** for a code anchor — the complete vocabulary a caller needs to use the layer, written explicitly enough that the caller does not have to descend into the layer below.

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

A code anchor often has internal layers worth documenting separately — an internal library, a subsystem with its own API, a protocol stack. Each such layer gets its own `{slug} {LayerName} Interface.md` alongside the top-level one. Sub-Interfaces sit one level below the top-level Interface in the User dispatch (or in a layer-specific subfolder for deep nestings).

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

1. **`{slug} Files.md` row 1** (the repo-root row) ends with `→ [[{slug} Interface]]`. The wiki-link resolves by basename. This is the entry point for anyone reading the file tree: "start here for the layer contract."
2. **`{slug} User.md` dispatch page** lists `[[{slug} Interface]]` as a top entry, alongside Guide / Architecture / Cards.

## Document Structure

An Interface composes from canonical section types. Pick the ones that apply; not every layer has all of them.

| Section | When to include | Purpose |
|---------|-----------------|---------|
| H1 `# {slug} Interface` | always | Title |
| -[[{slug} Interface]]- |  |
| --- | --- |
| --- | |

> ⚠️ **Recovery note (2026-06-14):** this `## Document Structure` table was truncated during recovery. A runaway edit ballooned the file to 19 MB (~38 K lines of one corrupted table cell full of escaped `\|` separators) and was hanging Obsidian's indexer on every launch. Only the first two clean rows survived; the remaining canonical-section rows were lost (the file was untracked — no git or backup copy existed). The full corrupted original is preserved beside this file as `.FCT Interface.CORRUPT-19MB-20260614.md` (dot-prefixed, so Obsidian ignores it). Rebuild the row list from a sibling facet such as [[DAS All Files]] when convenient.

## The Hiding Invariant

A common drift is for Interface docs to "leak" — they start as a layer contract and grow to describe internal mechanics. Resist this. When tempted to add a section, ask: *would a caller above this layer need this to use the layer correctly?*

- If yes → it's Interface material.
- If no → it belongs in Architecture (for design rationale), in a Module Doc (for implementation detail), or nowhere (for things not worth documenting).

The `## What's Hidden` section is a self-documenting check: writing "callers do not need to know about X, Y, Z" forces the author to name the hiding boundary explicitly, and prevents future agents from drifting the doc across it.

## Lifecycle

- **Create** — `rewire` scaffolds the file when missing on a code anchor; the scaffold is empty (TODOs in each section). Rewire also files a backlog row `## Now [Designing] — F<n> Author top-level Interface for {slug}` to surface the missing-content work.
- **Author** — the user collaborates with the agent to fill in the scaffold. This is design-bearing work; goes through `[Designing]` → `[Ready]` only after user agreement on the layer contract.
- **Validate** — promotion to `[Done]` requires user verification that the Interface accurately describes the layer. See [[SKA workflow]] § Interface-validation gate.
- **Maintain** — Interface drifts when callers see surface changes. Significant API additions, removals, renames, or conceptual-model changes go through the validation gate again. Cosmetic edits don't.
- **Split** — when a top-level Interface crosses ~500 lines, introduce sub-Interfaces for the internal layers; the top shrinks to a layer-index + the cross-cutting contract pieces.

## Relationship to the Root-Module Doc

In languages with a single entry-point module (Rust `lib.rs`, Python `__init__.py`, TypeScript `index.ts`), the Interface often *replaces* the module doc for that root. The root module is usually pure re-exports, so its "module doc" would be a de facto Interface anyway. Renaming `{slug} Lib.md` → `{slug} Interface.md` makes the role explicit.

In codebases without a clear single root (multi-binary workspaces, monorepos), the Interface is a standalone synthesis over the whole codebase.

## Audit Categories

`/audit docs` checks (see [[audit-docs]] § 1.8):

- `missing-interface` — no `{slug} Interface.md` exists on a code anchor.
- `interface-not-linked-from-files` — `{slug} Files.md` row 1 doesn't end with `→ [[{slug} Interface]]`.
- `interface-not-linked-from-dispatch` — `{slug} User.md` doesn't list `[[{slug} Interface]]`.
- `interface-incomplete-structure` — required sections (`## Public Modules` and at least one of: `## How They Group`, `## {module}`, `## Schemas`, `## CLI Surface`) are absent.
- `interface-module-missing` — Interface omits a public module that exists in source.
- `interface-too-large` — Interface exceeds ~500 lines (suggest splitting into sub-Interfaces).

## Cross-references

- **[[DAS All Files]]** — the audit-tied tree; Interface is linked from row 1.
- **[[DAS Module Doc]]** — auto-generated per-module reference; Interface is the human-authored layer contract that groups modules into a vocabulary.
- **[[DAS Architecture]]** — the *how* (internal structure, flow, design rationale); Interface is the *what callers see*.
- **[[DAS User Dispatch]]** — Interface lives here.
- **[[SKA workflow]]** § Interface-validation gate — user-collaboration gate for new and significantly-modified Interfaces.
- **[[SKA rewire]]** — creates the scaffold and files the backlog row when an Interface is missing.

# RULESET R-fct-interface
include::
where:: `file: **/{slug} Interface.md, **/{slug} * Interface.md`
description:: The rules every `{slug} Interface.md` (and sub-Interface) must satisfy — layer-completeness, hiding discipline, required structural links, and lifecycle gates.

### RULE R-fct-interface-01 — Layer-completeness: required sections present (checked)
Every top-level Interface doc contains at minimum a brief paragraph naming the layer + what callers gain, and at least one of: `## Public Modules`, `## Schemas`, `## CLI Surface`. Sub-Interfaces follow the same rule for their own layer.
**Check pattern:** the file has a non-empty H1-summary paragraph and at least one of the listed sections.
**Why:** an Interface that omits the caller vocabulary fails its core completeness invariant — a caller cannot use the layer from it.

### RULE R-fct-interface-02 — Required link from Files.md row 1 (checked)
`{slug} Files.md` row 1 (the repo-root row) ends with `→ [[{slug} Interface]]`.
**Check pattern:** `{slug} Files.md` row 1 ends with the Interface wiki-link.
**Why:** the Files entry point must direct readers to the layer contract first; a missing link makes the Interface invisible to file-tree navigation.

### RULE R-fct-interface-03 — Required link from User/Design dispatch (checked)
`{slug} User.md` (or `{slug} Design.md` if the anchor uses the Design dispatch) lists `[[{slug} Interface]]` as a top-level entry.
**Check pattern:** the dispatch page includes a `[[{slug} Interface]]` link.
**Why:** the dispatch page is the caller's entry; an Interface not listed there cannot be discovered without knowing to search for it.

### RULE R-fct-interface-04 — Human-review gate before Done (stated)
An Interface transitions to `[Done]` only after user verification that it accurately describes the layer contract (per [[SKA workflow]] § Interface-validation gate). Auto-generated or agent-only drafts are `[Designing]` until reviewed.
**Check pattern:** status on the backlog row is not `[Done]` unless the Interface has passed user review.
**Why:** layer-completeness and correctness can only be confirmed by a caller-perspective review; agent drafts are starting points, not finished contracts.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative contract is the body above. Per-anchor Interface content lives in each anchor's own `{slug} Interface.md`, never here; scaffold, validation, and audit mechanics live in [[SKA rewire]] / [[SKA workflow]] / [[audit-docs]] — link to those rather than restating them.)*

- **Inclusion test** — a change belongs here only if it alters the contract every Interface doc must satisfy (invariants, required sections, required links, lifecycle gates, audit checks).
- **Audit category names are consumed by tooling** — the identifiers under § Audit Categories are cited by `/audit docs`; don't rename or drop them (or the two Required Links contracts) without updating callers.
- **Don't regress the section menu to a checklist** — § Document Structure lists canonical sections as a menu; don't mark optional rows "always required" or remove rows because some anchor doesn't use them.
- **Cross-spec consistency** — keep aligned with [[DAS All Files]] (row 1 link contract), [[DAS Module Doc]] (auto-generated vs. human-authored split), [[DAS Architecture]] (*how* vs. *what callers see*), [[DAS User Dispatch]] (location/listing), and [[SKA workflow]] (validation gate); a drift here propagates to all of them.
