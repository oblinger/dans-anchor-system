---
description: source file tree with descriptions (monospace)
---
# CAB Files

`{NAME} Files.md` maps the file tree of an anchor's code repository. Each line has a filename and a one-line description, aligned in fixed-width columns. It provides a single-page codebase overview for onboarding, planning, and AI context.

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Files.md`

The page uses Form 4 from `/md file-tree` — `cssclasses: monospace` frontmatter renders the entire page in fixed-width font. Wiki-links work inline because text is not inside code spans.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---
```
---
cssclasses:
  - monospace
---
```

\# TSK Files

File tree for the task-runner repository with descriptions.


task-runner/
├── Cargo.toml                         Workspace config + dependencies
├── Cargo.lock                         Dependency lockfile
├── justfile                           Build, test, check recipes        → [[CAB Repository Structure]]
├── [[CAB Claude|CLAUDE.md]]                          Claude Code configuration
│
├── src/                               Library crate
│   ├── [[TSK Lib|lib.rs]]                         Crate root, module exports
│   ├── [[TSK CLI|cli.rs]]                         CLI argument parsing (clap)
│   ├── [[TSK Scheduler|scheduler.rs]]                   Priority queue engine
│   ├── [[TSK Worker|worker.rs]]                      Thread pool lifecycle
│   ├── [[TSK Retry|retry.rs]]                       Exponential backoff logic
│   └── [[TSK Models|models.rs]]                      Task, TaskResult structs
│
└── tests/                             Integration tests
    ├── scheduler.rs                   Scheduler integration tests
    └── cli.rs                         CLI end-to-end tests

---



# Format Specification

## Structure
Every Files page has:
1. Frontmatter: `cssclasses: monospace` — renders the entire page in fixed-width font
2. H1 heading: `# {NAME} Files`
3. Description line: "File tree for the {repo-name} repository with descriptions."
4. Two blank lines before the tree
5. Tree starting with `{repo-name}/`

## Tree Format
- One line per file or directory
- Box-drawing characters for structure (`├──`, `└──`, `│`)
- Blank lines with `│` continuation to separate logical groups
- Directories end with `/` and may have descriptions
- See `/md file-tree` for full box-drawing and indentation rules

## Linking — Filenames ARE the Links

Every source file and directory that has a module doc is linked by making the filename itself a wiki-link. The filename in the tree doubles as the navigation link — there is no separate arrow or reference. This is the primary linking pattern in the Files tree.

**Format:** `[[{NAME} DocPage|filename.ext]]` — renders as `filename.ext` but links to the module doc.

| What | Format | Renders as |
|------|--------|------------|
| Source file | `[[TSK Scheduler\|scheduler.rs]]` | `scheduler.rs` (links to TSK Scheduler doc) |
| Directory | `[[TSK engine\|engine/]]` | `engine/` (links to module aggregator doc) |
| Standard file | `[[CAB Claude\|CLAUDE.md]]` | `CLAUDE.md` (links to CAB spec) |

Files without a module doc (tests, config files, etc.) use plain filenames — no link.

**Do NOT use `→ [[doc]]` arrows for source file doc links.** The `→` arrow pattern is only for non-source files that reference an external spec (e.g., `justfile → [[CAB Repository Structure]]`). Source files use the filename-as-link pattern instead.

## Alignment
- **Descriptions** — aligned at a consistent display column using regular spaces
- Pick columns that fit the project's longest filename and description; stay consistent within the file
- Alignment is based on **display width** — wiki-links like `[[TSK Scheduler|scheduler.rs]]` collapse to `scheduler.rs` when rendered, so padding must account for the shorter display width, not the raw markdown width
- Use Python to compute alignment when adding or modifying tree lines

## Maintenance
Update the Files page when the repository structure changes significantly — new modules added, packages reorganized, or major files renamed. It does not need to track every individual file change.
