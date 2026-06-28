---
description: Change log — date-stamped record of CAB structure changes; doubles as the rewire spec source when migrations propagate format changes across anchors.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAB]] → [CAB Log](hook://p/CAB%20Log)

# CAB Log

Chronological record of changes to the Common Anchor Blueprint. Reverse-chronological (newest entries at the top). Each entry is dated, names the change, and carries enough detail to act on it.

Two concurrent audiences:

- **Future agents / readers** answering *"when did X become Y?"* — skim the H2 headings.
- **The eventual rewire script** (or hand migration) propagating CAB changes to existing anchors — reads the structured body of each entry: `From:` / `To:` / `Affects:` / `Rationale:`.

Renames, relocations, facet introductions, trait additions, deprecations — all CAB-shape changes belong here.

## Entry format

Each entry is one dated H2 with a structured body:

- **`## YYYY-MM-DD — <one-line summary>`** — the entry heading: ISO date, em-dash, one-line summary.
- **`**Change:**`** — one or two sentences naming the change.
- **`**From:**`** / **`**To:**`** — old then new path / shape / convention (each in back-ticks).
- **`**Affects:**`** — all anchors using `<X>`; how the rewire pass walks `<Y>` and applies `<Z>`.
- **`**Rationale:**`** — why; references prior decisions / F-numbers / commit hashes as relevant.

Empty when no field applies; trim freely. The `From` / `To` / `Affects` block is the data the rewire script consumes; the prose surrounding it is for human readers.

---

## 2026-06-08 — Rules vs Decisions vocabulary split; CAB Rules re-activated; R-NN compound naming

**Change:** The unified "Decisions" vocabulary from F113 is refined into two distinct concepts that travel separately. **Rules** are portable, audit-checkable constraints, defined in ruleset files under `Rulesets/` (catalog) or `{NAME} Rules.md` (anchor-local, rare). **Decisions** are anchor-specific applied choices with rationale, recorded in `{NAME} Decisions.md`, citing rules. Audit walks decisions → collects cited rules → verifies each.

**Rules:**

- Catalog folder renamed: `Decision Sets/` → `Rulesets/`. Folder layout (Arch / Diagram / Doc / Git / Process / Test / Ob etc.) unchanged.
- Ruleset naming: `R-<kebab-slug>.md` (e.g., `R-diagram.md`, `R-mac-app.md`). For well-known external methodologies, use the methodology name directly (`R-sugiyama`, `R-c4`).
- Rule-within-set naming: `R-<slug>-<NN>` (e.g., `R-diagram-04`); NN monotonic-forever within its source set; never recycled.
- Composition does NOT renumber. When `R-diagram` includes `R-sugiyama`, Sugiyama's rules retain `R-sugiyama-NN` identity.
- Ruleset file shape: body-only markdown (no YAML frontmatter). H1 = set name; optional `> [!info] Ruleset` callout; `## Includes` H2 with wiki-links; `## Rules` H2 with H3 per rule.
- CAB Rules facet **re-activated** (was deprecated post-F113); specs the format above. CAB Decisions facet stays for `{NAME} Decisions.md`.
- Decisions cite rules via a `**Cites:** [[R-…]]` line in the decision body.

**Affects:** Every anchor that uses or will use rules. Rewire pass:
1. Anchor's `{NAME} Decisions.md` continues to record applied choices, now ending each with `**Cites:** [[R-…]]`.
2. Anchor MAY have a `{NAME} Rules.md` for anchor-local rules; most won't.
3. Ruleset catalog migration: existing `Ob/ob.md` etc. need their `D-OB01` → `R-OB-01` renaming and frontmatter removal. Deferred (only the Diagram set has been fully migrated to the new format).
4. `/audit decisions` → `/audit rules` rename. Defer until the audit script is updated.

**Rationale:** F113 unified Principles + Rules into Decisions because the Principle/Rule distinction wasn't useful. But the unified term was *Decisions* — and that turned out to be a poor fit at the catalog level, where the constraints are reusable rules independent of any specific application. User feedback 2026-06-08: *"most places that we use it, it's more natural to call this thing a rule, rather than a decision."* The honest semantic distinction: a rule is a standing constraint; a decision is a specific applied choice (the choice to apply rule X here, with rationale Y). Both terms now have a clear home.

**Worked examples landed in this commit:** `R-diagram.md` (22 rules in 5 zones, extracted from the 2026-06-08 diagram-auditing-methodologies survey), `CAE Rules.md` (anchor-local example adopting R-diagram), `CAE Decisions.md` D11 (decision citing R-diagram rules), `CAB Rules` facet re-activated with the new spec.

---

## 2026-06-08 — Subsystem doc kebab-form naming — `{NAME}-{Subsystem}.md`

**Change:** Subsystem doc filenames inside `{NAME} Architecture/` adopt **kebab form**: `{NAME}-{Subsystem}.md` (anchor slug joined to subsystem name with a hyphen, no spaces around it). Multi-word subsystem names use internal hyphens. The qualifier suffixes "Arch" and "Subsystem" are dropped — kebab itself disambiguates from any same-name module doc elsewhere in the anchor.

**Rules:**

- Single-word subsystem: `CAE-Scheduler.md`, `MUX-Data.md`, `MUX-Dispatcher.md`
- Multi-word subsystem: `MUX-Native-Bridge.md` (not `MUX-Native Bridge.md`)
- Folder-form subsystem (when subsystem decomposes further): folder is `MUX-Foo/`, dispatch page is `MUX-Foo/MUX-Foo.md`
- Asset files alongside: `MUX-Foo.excalidraw`, `MUX-Foo.svg`, `MUX-Foo.png` — same kebab form

**From:** `{NAME} {Subsystem} Arch.md` (with spaces + "Arch" suffix), e.g., `MUX Data Arch.md`, `MUX Native Bridge Arch.md`
**To:** `{NAME}-{Subsystem}.md` (kebab), e.g., `MUX-Data.md`, `MUX-Native-Bridge.md`

**Affects:** Every architecture-folder subsystem doc across every anchor. Rewire pass per anchor:
1. Rename every `{NAME} <Words> Arch.md` to `{NAME}-<Words-joined-with-hyphens>.md` (plus matching `.excalidraw` / `.svg` / `.png` siblings).
2. Update H1 inside each renamed doc to match the new name.
3. Vault-wide sweep: `[[{NAME} <Words> Arch]]` → `[[{NAME}-<Words>]]` (with display aliases preserved where present).
4. Sweep breadcrumb refs + hook URIs that mentioned the old paths.

**Rationale:** "Arch" suffix was visually ugly when the architecture folder filled up with `MUX Foo Arch.md` / `MUX Bar Arch.md` / etc. — the tech-shorthand tag cluttered every filename. Underscores were considered as a minimal alternative but ruled out because `_word_` is markdown italic syntax and risks rendering glitches inside wiki-links. Kebab adds only one character vs the bare anchor-prefixed name (`MUX-Data` vs `MUX Data`), has zero markdown collision, and produces a distinctive basename that doesn't conflict with same-name docs elsewhere in the anchor. Worked examples: CAE (1 subsystem renamed) + MUX (11 subsystems renamed) in this commit.

## 2026-06-08 — CAB Architecture facet — standard section order + visual-diagram-only + subsystem link convention

**Change:** The [[CAB Architecture]] facet spec gains a load-bearing **section-order invariant** for the entry-point doc, a **forbid-ASCII** rule on all in-architecture diagrams, a **subsystem dispatch table** with an explicit link convention, and an explicit **what-does-NOT-belong** list. The Public API surface (modules, classes, functions, schemas) is moved off the entry-point page into a dedicated `{NAME} API.md` sub-doc inside `{NAME} Architecture/`.

**Rules:**

- **Standard section order (first four are load-bearing).** Entry-point Architecture doc spine: (1) top-of-doc per F060 → (2) `## Overview` (one paragraph) → (3) `## Architecture diagram` (Excalidraw image embed + one paragraph max) → (4) `## Subsystems` (dispatch table). Sections after 4 are flexible.
- **Visual-diagram-only.** Every diagram in any architecture doc — top-level component figure, thread layout, data flow, etc. — is authored in Excalidraw and embedded as `![[Name.png]]`. ASCII art is forbidden (per durable feedback).
- **Subsystem dispatch link convention.** Real subsystems use `[[double-bracket]]` wiki-links; placeholder/future subsystems use `[single-bracket]` plain text (no link, no broken wiki-link).
- **Architecture page is a conceptual map, not a reference.** Per-module class/function tables, schemas, error types, CLI surfaces do NOT belong on the entry-point page. They go in `{NAME} API.md` (sub-doc) or the relevant subsystem doc.
- **Architecture diagram requires arrows.** Boxes without arrows are a list, not a diagram.

**Affects:** Every anchor with an existing Architecture doc. Rewire pass per anchor:
1. Reorder sections to put `## Overview` → `## Architecture diagram` → `## Subsystems` first (in that order).
2. If the architecture doc has ASCII art, replace with Excalidraw + image embed.
3. If per-module API content lives on the architecture page, split it out to `{NAME} API.md` and/or the relevant subsystem doc.
4. Build the `## Subsystems` dispatch table with the link convention (real = `[[X]]`, placeholder = `[X]`).
5. `/audit architecture` (extended with the new flags: `ascii-diagram`, `api-content-on-arch-page`, `section-order`, `orphan-subsystem`, `missing-subsystem-doc`) catches drift.

**Rationale:** The Architecture spec said "no fixed section order" — that turned out to be too permissive; the first four sections are exactly the spine a reader needs to orient. The Public API content kept landing on the architecture page because there wasn't a documented home for it; now the rule is explicit. The ASCII-art ban codifies durable user feedback (2026-06-08). The single-bracket placeholder convention lets the CAE worked example demonstrate a *partially-authored* architecture honestly without polluting Obsidian's link graph with broken double-bracket wiki-links.

## 2026-06-08 — Architecture becomes a folder anchor; fold Rollup + System Design

**Change:** Architecture transitions from a single `{NAME} Architecture.md` file inside `{NAME} Design/` into its own folder anchor `{NAME} Architecture/` at the anchor root. **[Reversed 2026-06-27 — Architecture moved back into `{NAME} Design/`; see FCT Architecture / FCT Design.]** The folder contains a top-level `{NAME} Architecture.md` entry point plus one child per subsystem (a single `.md` file OR a sub-folder, depending on the subsystem's complexity). `{NAME} Rollup.md` and `{NAME} System Design.md` are folded in.

**Rules:**

- `{NAME} Design/{NAME} Architecture.md` → `{NAME} Architecture/{NAME} Architecture.md` (single doc becomes folder + entry-point)
- `{NAME} Design/{NAME} Rollup.md` → prepended to the top of `{NAME} Architecture/{NAME} Architecture.md` as the opening summary/TLDR section; standalone Rollup file deleted
- `{NAME} Design/{NAME} System Design.md` → folded into `{NAME} Architecture/{NAME} Architecture.md` (whole-system content) OR migrated to a subsystem `.md` / sub-folder inside `{NAME} Architecture/` (subsystem-level content); standalone System Design file deleted
- Each subsystem within Architecture is a single `.md` (when one file suffices) OR a sub-folder with its own dispatch page (when the subsystem decomposes further). Subsystems linked from `{NAME} Architecture.md`'s body.

**Affects:** Every anchor with `{NAME} Architecture.md` and/or `{NAME} Rollup.md` and/or `{NAME} System Design.md`. Rewire pass per anchor:
1. Create `{NAME} Architecture/` folder at root with `.anchor`.
2. Move `{NAME} Architecture.md` into it.
3. Read `{NAME} Rollup.md`; prepend its content as a summary section at the top of `{NAME} Architecture.md`; delete Rollup file.
4. Read `{NAME} System Design.md`; judge whole-system vs subsystem; either merge into `{NAME} Architecture.md` or break out as a subsystem child.
5. Identify any existing module docs that are subsystems (e.g., docs currently in `{NAME} Dev Docs/`); move them into `{NAME} Architecture/` as subsystem children.
6. Link every subsystem from `{NAME} Architecture.md`.
7. Sweep wiki-links across the vault: `[[{NAME} Rollup]]` and `[[{NAME} System Design]]` now resolve to anchor sections inside `{NAME} Architecture.md`.

**Rationale:** Single-file architecture forced everything into one document, making subsystems hard to navigate or revise independently. Rollup + System Design + Architecture were three docs covering overlapping ground; the consolidation removes the "which file is the canonical entry?" ambiguity. Folder-anchor pattern lets subsystems be first-class docs while keeping a clear top-level entry point.

---

## 2026-06-08 — CAE migrated as worked example (applied above rule)

**Change:** Applied the wrapper-elimination rule to CAE. Renames: `CAE User/` → `CAE User Docs/`; `CAE Dev/` → `CAE Dev Docs/`. (`CAE Track/` already existed; `CAE Design/` untouched — neither was inside a Docs wrapper.) Dispatch pages renamed in lockstep (`CAE User.md` → `CAE User Docs.md` etc.) with H1 + breadcrumb updates.

**From:** `CAE/CAE User/`, `CAE/CAE Dev/` (with dispatch pages `CAE User.md`, `CAE Dev.md`)
**To:** `CAE/CAE User Docs/`, `CAE/CAE Dev Docs/` (with dispatch pages `CAE User Docs.md`, `CAE Dev Docs.md`)

**Affects:** CAE only. Worked example confirms the rule above is applicable; serves as the visual reference for the rewire pass.

**Rationale:** User direction — see [[CAE-Scheduler]] discussion context. Establishes CAE as the worked-example anchor for the new shape.

## 2026-06-08 — Eliminate `{NAME} Docs/` wrapper; promote children to root (one rename)

**Change:** The `{NAME} Docs/` parent folder is removed. Its three children are promoted to anchor-root siblings. One child is also renamed in the move (`Plan` → `Track`).

**Rules:**

- `{NAME} Docs/{NAME} User/` → `{NAME} User Docs/` (promote, rename)
- `{NAME} Docs/{NAME} Dev/` → `{NAME} Dev Docs/` (promote, rename)
- `{NAME} Docs/{NAME} Plan/` → `{NAME} Track/` (promote, rename)

**Affects:** Every anchor with a `{NAME} Docs/` wrapper. Rewire pass for each anchor: detect `{NAME} Docs/`; for each of its children apply the matching rule above; delete the now-empty `{NAME} Docs/`; rewrite any wiki-link or breadcrumb that routed through `{NAME} Docs/`, `{NAME} User/`, `{NAME} Dev/`, or `{NAME} Plan/` to use the new path/name. Note that `Plan` → `Track` is a rename, so links like `[[{NAME} Plan]]` need rewriting beyond just the parent move.

**Rationale:** The wrapper added a layer without semantic value — the three categories are independently meaningful and frequently cross-referenced; the extra parent forced longer paths and harder skimming. `Plan` → `Track` aligns the workflow vocabulary with the doc category (rows / features / roadmap are *tracked* over time, not just *planned*). F113 names the elimination: *"`{NAME} Docs/` parent and `Plan/` subfolder eliminated vault-wide."*
