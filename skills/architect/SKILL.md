---
name: architect
description: >
  Create and maintain the top-level architecture document for an anchor.
  Architecture lives in `{NAME} Design/` — a single `{NAME} Architecture.md`
  by default, upgraded to a `{NAME} Architecture/` folder-doc once it grows
  subsystems. Decomposes the system into one or more subsystems (each with
  a dispatch table + mandatory summary table + optional figure + module list).
  Both the top-level doc and each subsystem are single-file by default and
  upgrade to a folder-doc when they grow discussion that won't fit in one
  file; the same-named index keeps the upgrade link-transparent. Bidirectional `module ↔ arch` linking via an `Arch` row
  in every module doc's dispatch table. Reads module docs as ground truth
  (with a commit-log staleness precondition); source-dip on demand for specific
  module questions. Conservative-edit posture: proposes additions/refinements,
  never wipes user-authored prose. Use when the user says "architect",
  "/architect", "build the architecture", "update the architecture", or any
  variant about working on the system-level design view.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Architect — Maintain `{NAME} Architecture/`

The `/architect` skill — creates and maintains the top-level system-architecture document for an anchor as a subsystem decomposition rooted in `{NAME} Design/` (a single `{NAME} Architecture.md`, upgraded to a `{NAME} Architecture/` folder-doc once it grows subsystems).

`/architect` creates and maintains the top-level system-architecture document for an anchor. The doc lives in `{NAME} Design/` — as `{NAME} Architecture.md` by default, upgrading to `{NAME} Architecture/{NAME} Architecture.md` (folder-doc form) once it grows subsystems (see § Folder layout). It decomposes the system into **subsystems** — each subsystem has a dispatch table, a **mandatory summary table** linking to its parts, an **optional figure**, and a **modules table** linking to the relevant module docs.

Feature spec: `[[F074 — Architect skill — Architecture as anchor folder with subsystems]]`. Companion specs: `[[FCT Architecture]]` (the facet), `[[FCT Module Doc]]` (defines the `Arch` row in module-doc dispatch tables). **F074 Q4=a (kept-System-Design-parallel) REVERSED 2026-05-26 per user direction**: Architecture is the sole architectural-synthesis facet; legacy `{NAME} System Design/` folders (pre-F074 anchors only) are absorbed during `/architect` runs — pull their `### Architectural Commitments` content into `{NAME} Architecture/{NAME} Architecture.md § Architectural Commitments`, archive the folder under `{NAME} Postmortems/legacy System Design/`. New anchors never create one.

## Sub-actions

(Per [[F084 — Architect redesign]] — `/architect` is being split into a family of sub-skills. Sub-action runbooks live alongside this SKILL.md.)

| Sub-action | File | Description |
|---|---|---|
| `/architect drift` | [[architect-drift]] | Read-only arch-vs-code drift report. Categorizes findings (Aligned / Orphan in code / Ghost in arch / Diverged); writes report to `Versions/{date} Drift Report.md`; never modifies arch or code. |
| `/architect new` | [[architect-new]] | Greenfield architecture draft from features/PRD only. No anchoring bias from existing code/arch. Writes to `Versions/{date} Architecture (greenfield).md`. |
| `/architect update` | [[architect-update]] | Snapshot current arch → integrate new ideas in-place → `## Changes since [[snapshot]]` at bottom. **Bare `/architect` routes here** per F084. |
| `/architect changes` | [[architect-changes]] | Re-derive `## Changes since` section from structural diff (recovery tool). Shares arch-doc parser + semantic-diff engine with `/architect update`. |
| `/architect overview` | [[architect-overview]] | **Portable bare-project mode (per F184).** Produces an `Architecture Overview.md` + embedded hand-drawn SVG (via `/viz svg`) for a codebase with **no** CAB scaffolding (no `.anchor`, no module docs, no vault). Requires a subject: `/architect overview <subject>` — names what to architect; asks *"what do you want me to architect?"* if none is given, never no-ops. Skips all CAB preconditions and vault post-conditions; runs anywhere. |

**Bare `/architect`** (no sub-action) routes to `/architect update` — the most common action. The legacy single-pass behavior documented below is superseded by the sub-skill family ([[architect-new]] / [[architect-update]] / [[architect-drift]] / [[architect-changes]] / [[architect-overview]]); retained inline for historical reference and may be removed in a follow-up cleanup.

**Off-vault / non-CAB codebases use `/architect overview <subject>`** ([[architect-overview]], per F184) — the portable bare-project path. The full runbook below assumes a CAB anchor (`.anchor`, module docs, `{NAME} Docs/…` layout); when none of that is present, `overview` is the entry point. It still **requires an explicit subject** — a bare architect with nothing to architect must ask what to architect, not no-op.


## When to Use

- User says `/architect`, `architect`, "update the architecture", "build the system view", "refresh the architecture diagram".
- After significant module-doc changes (new modules, removed modules, renames) so the architecture stays in sync.
- During design discussions where the user wants a high-level view of how subsystems relate.
- Periodically as part of vault maintenance — staleness precondition (per § 4.1) reports drift quietly.

**Don't** invoke `/architect` for module-level rewriting. That's `/audit docs` (and its downstream module-doc refresh skill). Architect operates *above* module docs — it's rollup-of-rollup.


## Folder layout — Architecture file-by-default, folder-doc when it grows

```
{NAME} Design/
├── {NAME} Architecture.md                 ← DEFAULT: a single file (most anchors stop here)
└── {NAME} Architecture/                   ← UPGRADED to a folder-doc once it grows subsystems
    ├── {NAME} Architecture.md             ← the index (same basename as the folder)
    ├── {NAME} Foo Arch.md                 ← simple subsystem: single file
    └── {NAME} Bar Arch/                   ← complex subsystem: itself a folder-doc
        ├── {NAME} Bar Arch.md             ← folder-doc index
        ├── {NAME} <Module-1> Arch.md      ← per-module arch doc (only when needed)
        └── {NAME} <Module-2> Arch.md
```

The two top rows are the same artifact in its two states — a one-document architecture is **just `{NAME} Architecture.md`** in `{NAME} Design/`; the `{NAME} Architecture/` folder is created only on upgrade. Don't pre-create the folder.

**File-by-default, folder-doc when it grows — at every level.** Both the top-level architecture and each subsystem start as a single file and upgrade to a folder-doc only when they accumulate more than one document's worth of discussion (the top-level grows *subsystems*; a subsystem grows *per-module arch docs*). The upgrade is **mechanical and link-transparent**: a folder-doc is a folder plus an index file of the *same basename*, so `[[{NAME} Architecture]]` resolves whether it is a file or a folder-doc — **no reference breaks across the upgrade**. Because nothing breaks, upgrade *timing* is a tidiness call, not a correctness one: `/architect` performs it when it detects a second document is warranted, and it is reversible.

A project's value statements (formerly `{NAME} Principles.md`) now live as D-records in `{NAME} Decisions.md` per `[[FCT Decisions]]` — the Principles facet was retired and absorbed into Decisions (F113). Architecture cross-links to those decisions; it doesn't absorb them.


## Top-level `{NAME} Architecture.md`

Standard top-of-doc per F060 (YAML frontmatter + H1 + dispatch-table placeholder). The dispatch table links to every subsystem doc and to `{NAME} Principles.md`. Below the dispatch:

- **Single-document systems** — the architecture is just `{NAME} Architecture.md` (a single file in `{NAME} Design/`); there is **no** `{NAME} Architecture/` folder until subsystems appear. Don't pre-create it — the file→folder upgrade is link-transparent (§ Folder layout), so wait until a second document is actually warranted.
- **Multi-subsystem systems** — the body is **a figure showing the relationships between subsystems and other major components** (third-party services, external systems, persistence boundary, etc.) followed by a **summary table** of subsystems (one row per subsystem, linking to its Arch doc, with a one-line description). Build the figure with the **SVG-in-MD** sub-pattern (see `[[SKA viz]]` § SVG in Markdown): an `![[…svg]]` embed + a `↗ Clickable | Index | ✎ Edit` link row, with an **Index** table that mirrors the figure.

**Figure rule: NO title text inside the figure.** The H2 section heading immediately above the embed names the figure (e.g. `## DictaMux Permissions Architecture`); the figure shows it. Duplicating a title inside the SVG wastes pixels, drifts when one is renamed without the other, and makes the figure less reusable when embedded elsewhere. The H2 + a focused figure is the canonical form. Same rule applies to subsystem-doc optional figures (§ Subsystem doc shape).


## Subsystem doc shape — file by default, folder when complex

Each subsystem is a **single markdown file** by default: `{NAME} Architecture/{NAME} <Subsystem> Arch.md`. When one or more modules within a subsystem grow architecture-level discussion that won't fit in a modules-table cell, **the subsystem is upgraded to a folder doc** — the single file is moved into a folder of the same anchor-name, and per-module arch docs become siblings inside it. The upgrade is reversible.

Subsystem doc shape (same for file and folder-doc forms), top-of-doc per F060, then in strict order:

1. **Mandatory summary table** — links out to every relevant part of the subsystem. One row per linked-to artifact (a module's destination, a decision row, an external service, etc.). Link in column 1; one-line description in column 2.
2. **Optional figure** — built with the **SVG-in-MD** pattern (default; see `[[SKA viz]]` § SVG in Markdown) showing the subsystem's internals; excalidraw / mermaid serve only as bootstrappers that export the SVG. *Below* the summary table per the spec: the table is the synthesis (must-have); the figure is illustrative (nice-to-have).
3. **Modules table** — every module in the subsystem with a wiki-link and an architecture-level one-line description. The wiki-link points to the **most-specific** destination: the per-module arch doc if one exists, otherwise the module doc itself.
4. **Optional H2 sections** — narrative on Thread Model, Data Flow, Boundaries, etc.

Single-subsystem systems use exactly this format inside `{NAME} Architecture.md` itself — no separate subsystem file.


## Module-to-subsystem invariant

**Every module belongs to exactly one subsystem.** Hard invariant.

- **Single-subsystem systems** use an implicit "root subsystem" — every module lives there.
- **Multi-subsystem systems** partition modules across the named subsystems: no module appears in two subsystem modules-tables; no module is absent from all of them.

`/architect` enforces this during its comparison step (per § 4.4) — **orphans** (in `{NAME} Dev/` but in no subsystem modules-table) and **duplicates** (in two) surface as proposals to the user.


## Bidirectional cross-linking

Architecture-to-modules links live in each subsystem's **modules table** (above). The reverse — module-to-architecture — lives in the **module doc's dispatch table** at the top:

```

| -[[{NAME} <Module>]]- | |
| --- | --- |
| Arch | [[{NAME} <Subsystem> Arch]] |       ← architect-managed row
| --- | |

```

The `Arch` row points to the **most-specific** architecture destination:
- If a per-module arch doc exists → link to it.
- Else if a subsystem arch doc exists → link to it.
- Else (single-subsystem systems) → link to the top-level `{NAME} Architecture.md`.

**Every module doc has exactly one `Arch` row.** Both directions are maintained by `/architect`: each run reconciles the dispatch-table `Arch` rows and the modules-table links so they always point at each other (or surfaces the disagreement as a proposal). `[[FCT Module Doc]]`'s dispatch-table spec reserves the `Arch` row name.


## Runbook

### 1. Staleness precondition (commit-log check)

Before reading module docs as ground truth, verify they're current with the source code.

Procedure:

1. Walk up from `cwd` to find `.anchor`. If none, say "No anchor found from `{cwd}` upward." and stop.
2. Read `{NAME} Dev.md` frontmatter and extract the `module_docs_audited:` date field (written by `/audit docs` at the end of every audit pass — see `[[audit-docs]]`).
3. Run `git log --oneline <audited-date>..HEAD -- <source-tree>` to count commits in source since the audit. Also `git diff --shortstat <audited-date>..HEAD -- <source-tree>` for line-change magnitude.
   - Wall-clock cost: ~1 second typical; up to ~3s on large repos. Sequential, no parallelism needed.
4. Branch on the result:
   - **Zero commits** → module docs are current. Proceed silently to step 2.
   - **Non-zero but small** (≤ 3 commits / 100 lines): announce the count via the Drive-mode assume-and-announce pattern (`**Assuming module docs are current enough — N commits, M lines since audit. Proceeding.**`), then proceed. Small staleness is reversible if the architecture pass is re-run later.
   - **Non-zero and large** (> 3 commits / 100 lines): surface to the user — offer to refresh module docs first (run `/audit docs`) before architecting, or proceed with explicit stale-input acknowledgement.
   - **No `module_docs_audited:` field exists** in `{NAME} Dev.md` frontmatter: module docs have never been audited under this discipline — recommend a docs refresh.

### 2. Read existing state

Read (in this order, each at most once per run):
1. `{NAME} Architecture/{NAME} Architecture.md` (if exists) + every `{NAME} <Subsystem> Arch.md` sibling.
2. `{NAME} Principles.md` (for cross-link continuity).
3. The index of `{NAME} Dev/` module docs — `find` for `{NAME} <Module>.md` files; do NOT read each one yet.

### 3. Analyze the codebase via module docs

Build the architecture-level mental model **using only module-doc content**. Do NOT read source files at this step.

For each module doc, extract:
- The module's role (the brief paragraph after the dispatch table).
- Its primary class(es) and their responsibilities (from the CLASSES table).
- Its dependencies (from the `## See Also` section if present, plus inferred dependencies from class signatures).

Group modules into subsystems by responsibility cluster, dependency proximity, and any existing subsystem-doc structure.

### 4. Compare to existing architecture

Diff the proposed structure against what's already documented. Categorize each delta:

- **Missing** — subsystem not currently documented; propose adding.
- **Stale** — subsystem documented but no longer matches code; propose updating.
- **Phantom** — subsystem documented but no longer present in code; propose removal *as a question*, not autonomously.
- **Orphan** — module exists in `{NAME} Dev/` but appears in no subsystem modules-table (per § Module-to-subsystem invariant); propose assignment to a subsystem.
- **Duplicate** — module appears in two subsystem modules-tables; propose deduplication.

### 5. Reconcile bidirectional links

For every module doc: ensure exactly one `Arch` row exists in the top-of-doc dispatch table, pointing at the most-specific architecture destination (per § Bidirectional cross-linking). Fix or propose-to-fix any mismatch. Reverse direction is enforced by the modules-table content.

### 6. Surface proposals via `/query`

Each significant delta becomes a Q on the architecture doc. Trivial deltas can be made silently in Drive mode under the assume-and-announce gates:
- **Trivial — silent**: adding a new module to an existing modules-table; correcting an `Arch` row; updating a one-line module description in the modules table.
- **Substantive — `/query`**: creating a new subsystem; promoting a subsystem from file to folder; removing a phantom subsystem; reassigning a module to a different subsystem.

`/query` parks Qs in the architecture doc's `## Open Questions` H2 per `[[SKA queries]]`. **If `/query` isn't installed** (a minimal clone), degrade to asking the proposal inline in chat instead — never skip the user's decision just because the parking surface is absent.

### 7. Source dip on demand

If the user asks a question about a specific module (or `/architect` detects an ambiguity in the module doc), read that one source file. **Never default to "read all source."** The whole skill operates on module docs; source dip is the exception, not the rule.

### 8. Q.md update post-condition (per F075)

**Skip-if-absent (portability, per F184).** This post-condition is vault-coupled. Perform it **only when `~/ob/kmr/Q.md` exists**. On a machine without the kmr vault (a colleague's clone), skip it silently with a one-line note — the architecture is still written and committed; only the dashboard refresh is skipped. The `/architect overview` (bare-project) path always skips it.

When `~/ob/kmr/Q.md` is present: after the architecture pass commits, regenerate the anchor's per-anchor section in `~/ob/kmr/Q.md` per `[[SKA triage]]` § 6 — walk the backlog, compute the section, remove any existing section for this anchor, insert at the top of Q.md's body (bubble-to-top). The backlog file is NOT reordered.

### 8a. `/audit architecture` post-condition (per F092)

**Skip-if-absent (portability, per F184).** Run this **only when `~/.claude/skills/audit/scripts/audit-architecture.py` is reachable**. On a minimal clone that ships `viz` + `architect` but not the `audit` skill, skip it with a one-line note — the architecture is still written; it just isn't post-audited. The `/architect overview` (bare-project) path skips it by default.

When the script is present, invoke the architecture audit on the touched anchor's reachability set:

```bash
~/.claude/skills/audit/scripts/audit-architecture.py --scope anchor --anchor <NAME>
```

The audit checks two structural rules over the anchor's Arch docs: (R1) diagram-at-top + component-table-immediately-after, and (R2) wiki-link integrity on every module reference in component tables. Non-zero findings are **surfaced inline but do NOT block the mint** — they're reported, and (when the violation is the agent's own work this turn) addressed in the same pass; or filed as a backlog row for downstream cleanup. Pass `--fix` to apply A3 wrap-in-brackets auto-fixes when the basename match is unambiguous. Full rule reference: `[[F015 — Audit architecture]]`; runbook: `[[audit-architecture]]`.

### 9. Commit on transition

Per the standard commit discipline. The architecture pass is one logical change unit — commit when the run finishes (subsystem additions, modules-table updates, `Arch` row reconciliations all bundle).


## Conservative-edit posture

The skill presumes the user is the original author of the design. Every `/architect` write either:

- **(a) Structural-only** (creating an empty subsystem doc, regenerating a dispatch table, fixing a broken link) — silent in Drive mode.
- **(b) Tightens an existing description** (one-line update flagged in the commit message) — silent in Drive mode.
- **(c) Adds substantive new prose** (new subsystem rationale, narrative section) — requires user agreement via `/query`.

**Never wipe user-authored content.** If `/architect` would replace a paragraph the user wrote, it surfaces the change as a Q and waits.


## Out of scope (v1)

- Auto-generating subsystem groupings from module-import graphs. v1 takes the user's manual groupings; future versions might propose groupings algorithmically.
- Hand-illustrating the inter-subsystem figure. The figure is produced with the **SVG-in-MD** sub-pattern from the viz skill (`[[SKA viz]]` § SVG in Markdown) — a source `.svg` (edit in Inkscape) embedded via `![[svg]]`, a `Clickable | Index | Edit` link row, and a figure-mirroring **Index** table. v1 may drop a placeholder SVG and refine it later.
- Cross-anchor architecture (e.g., SYS-level "how all my projects fit together"). Out of scope; per-anchor only.
- Rewriting module docs. Module-doc maintenance is `/audit docs`'s domain.


## Cross-references

- `[[FCT Architecture]]` — the facet spec for `{NAME} Architecture/` and subsystem docs.
- **Legacy `{NAME} System Design/`** — `[[FCT System Design]]` was kept as a parallel facet per F074 Q4=a, but that was reversed 2026-05-26. New anchors never create a System Design folder. Legacy ones (currently only MUX) get absorbed: `### Architectural Commitments` migrates into Architecture; the rest of the System Design content moves to `{NAME} Postmortems/legacy System Design/` as preserved historical reference.
- `[[FCT Module Doc]]` — defines the `Arch` row in module-doc dispatch tables and the `module_docs_audited:` frontmatter contract.
- `[[FCT Decisions]]` — value statements (formerly Principles, now retired) live here as D-records; Architecture cross-links to them, doesn't absorb them.
- `[[audit-docs]]` — writes `module_docs_audited:` to `{NAME} Dev.md` frontmatter at the end of every audit pass; the source of truth `/architect`'s staleness precondition reads.
- `[[SKA queries]]` — universal Q-parking subroutine.
- `[[SKA triage]]` — provides the Q.md regen helper that `/architect` calls as its post-condition.
- `[[F074 — Architect skill — Architecture as anchor folder with subsystems]]` — design doc.
