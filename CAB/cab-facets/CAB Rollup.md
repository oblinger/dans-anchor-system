---
description: whole-system API rollup — standalone overview from subsystems down to classes
---

# CAB Rollup

**Location:** `{NAME} Docs/{NAME} Dev/{NAME} Rollup.md`


`{NAME} Rollup.md` is a single-page standalone overview of the entire codebase's public surface. It groups modules into semantic subsystems, then for each subsystem shows per-class tables with the key types, functions, and signatures. A reader can read the rollup end-to-end and understand how the system is put together — without opening any individual module doc.

**Why a separate facet (distinct from Architecture and Module Docs):**

- **Module docs** describe one module in isolation. They're accurate but atomized — a reader has to hold many in working memory to see the whole picture, and modules whose meaning depends on a neighbor (e.g. `response.rs` alongside `client.rs`) don't make sense alone.
- **Architecture** describes system-level flow (thread model, component diagrams, data flow). It stops above the class level.
- **Rollup** lives in between: it groups modules into subsystems (what Architecture gives you) and shows per-class tables (what Module Docs give you), in one document. The goal is "read this once, understand the API surface."

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Dev/CAE Rollup.md` — the canonical shape.

Real-world example the facet was extracted from: `ob-utils/OBU Docs/OBU Dev/OBU Rollup.md` (an API rollup for a Rust crate).


# Reference Example
---

```markdown
---
description: Crate-wide public surface — everything {repo-name} re-exports
---

# {NAME} Rollup

Entry point ({source path of root module}). Re-exports the N public modules so consumers can write `use {pkg}::... ` without chasing the source tree.

This page is also the **canonical whole-codebase overview** — every public type and top-level function appears in a table below. For per-module prose, drill into the module docs linked in each section.

Source: `{absolute path to root module}`

## Public Modules

| Module           | Description                  |
| ---------------- | ---------------------------- |
| [[{NAME} logging]] | Structured log entries …    |
| [[{NAME} protocol]] | Wire protocol stack …       |
| [[{NAME} Response]] | Shared RPC types …          |
...

## How They Group

The N modules fall into M semantically coherent groups. Consumers typically pick one or two groups — not every app needs everything.

### Group 1 — {name} ({one-line role})

{2–4 sentences: what this group does, why it's grouped, when to use.}

| Module           | Role                                             |
| ---------------- | ------------------------------------------------ |
| [[{NAME} Response]] | The canonical payload — every call carries one |
| [[{NAME} Client]]   | Outbound side: connect, send, receive          |
...

### Group 2 — {name} ({one-line role})

{Same pattern.}

---

## {module} — {one-line tagline}

See [[{NAME} {ModuleDoc}]] for detail.

| CLASSES        | Description                                     |
| -------------- | ----------------------------------------------- |
| `Response`     | Enum — `Ok{output}` or `Error{message}`         |
| `Direction`    | Enum — `Horizontal`, `Vertical`                 |

| FUNCTIONS      | Signature                                    | Purpose                         |
| -------------- | -------------------------------------------- | ------------------------------- |
| `write_frame`  | `(stream, payload) -> Result<()>`            | Length-prefixed frame           |

---

## {next module} — {tagline}

{Same pattern, one `## {module}` section per module.}

---

## See Also

- [[{NAME} Architecture]] — module dependency graph and flow
- [[{NAME} Files]] — source tree with per-file links
```

---



# Format Specification

## Location

`{NAME} Rollup.md` lives inside `{NAME} Docs/{NAME} Dev/` alongside `{NAME} Architecture.md` and `{NAME} Files.md`.

## Trait Applicability

Only anchors with the `code` trait have a Rollup. Other traits (`simple`, `topic`, `paper`) don't have a code surface to summarize.

## Size Limit — Split When Too Large

Keep `{NAME} Rollup.md` under **~10 printed pages** (roughly 500 lines). When a codebase grows past that:

1. Split into per-subsystem rollups: `{NAME} {Subsystem} Rollup.md` (e.g., `OBU logging Rollup.md`, `OBU protocol Rollup.md`).
2. The top `{NAME} Rollup.md` shrinks to a **subsystem index** — one section per subsystem with its summary table and a link to the subsystem rollup.
3. Each subsystem rollup takes on the per-class tables for its area.

The goal is that every rollup file is standalone and fits in one reading. A reader opens the top rollup, gets the system shape, and drills into subsystem rollups only for the area they care about.

## Required Links

The Rollup must be reachable from two places — this is what `/audit docs` checks:

1. **`{NAME} Files.md` repo-root row (first row)** — the row for the repo root directory ends with `→ [[{NAME} Rollup]]`. This is the entry point for anyone reading the file tree: "start here for the API overview."
2. **`{NAME} Dev.md` dispatch page** — the Rollup appears at the top of the dispatch table, typically as a "**Start here**" row.

## Document Structure

| Section | Purpose |
|---------|---------|
| H1 `# {NAME} Rollup` | Title |
| Brief paragraph | What this rollup covers (codebase, root module, scope) |
| "canonical whole-codebase overview" line | Explicit statement that this is THE top-level rollup |
| Source line | Absolute path to the root module |
| `## Public Modules` | One table listing every top-level public module with a one-line description |
| `## How They Group` | Groupings, one H3 per group, each with a table of member modules and roles |
| `---` separator | |
| `## {module}` sections | One per module. Brief tagline + `See [[{NAME} {Module}]] for detail.` + per-class CLASSES and FUNCTIONS tables |
| `## See Also` | Links to Architecture, Files, any subsystem-level rollups |

## Class Tables — Same Shape as Module Docs

The class tables inside a rollup use the same format as in [[CAB Module Doc]] — CLASSES column, descriptions, and for structs/classes with methods a FUNCTIONS table with signatures. Keeping the shape aligned means a reader moves from rollup to module doc without mental translation.

Skip the deep per-method discussion sections that full module docs have — the rollup is a surface, not a reference. Readers who need method details follow the wiki-link to the module doc.

## Lifecycle

- **Create** as soon as the codebase has more than one module
- **Update** when a public module is added, renamed, or restructured — otherwise it goes stale fast
- **Split** when the top rollup crosses ~500 lines
- `/audit docs` flags missing or stale rollups; `/rule check` for structural rules (e.g., "every code anchor has a rollup") can catch absence

## Relationship to the Root-Module Doc

In languages with a single entry-point module (Rust `lib.rs`, Python `__init__.py`, TypeScript `index.ts`), the Rollup often replaces the module doc for that root. The root module is usually pure re-exports, so its "module doc" would be a de facto rollup anyway. Renaming `{NAME} Lib.md` → `{NAME} Rollup.md` makes the role explicit.

In codebases without a clear single root (multi-binary Rust workspaces, multi-package monorepos), the Rollup is authored as a standalone synthesis over the whole codebase.
