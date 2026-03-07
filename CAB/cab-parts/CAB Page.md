# CAB Page

The primary entry point for an anchor: `{NAME}.md`. Contains the heading, a one-line description property, and a link table pointing to all related docs.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

# TSK — Task Runner

desc:: CLI tool for scheduling and running deferred shell tasks

| [[TSK Docs]]    | --------------------------------                |
| ---------------- | ----------------------------------------------- |
| External         | [Repo](https://github.com/oblinger/task-runner) |
| [[TSK Docs]]     | [[TSK PRD]], [[TSK Features]], [[TSK Notes]]    |
| User Docs        | [[TSK User Guide]]                              |
| - Execution      | [[TSK Todo]], [[TSK Roadmap]]                   |

---



# Format Specification

## Naming

An anchor has a **name** — the identifier used for its files and references:

- **TLC** (optional) — A short uppercase code like `CLF`, `DMUX`, `HA`. Used when brevity matters.
- **Full Name** — The complete name in Title Case (e.g., "Claudifier", "2026 Daves Finances"). Always present.

If a TLC exists, it is the `{NAME}` used for file naming (`{TLC}.md`, `{TLC} Docs/`). If no TLC, the full name is used.

**Every markdown file and folder inside an anchor is prefixed with `{NAME}`** to avoid collisions in the shared Obsidian namespace. This applies to files, folders, and nested files alike (see [[CAB Naming Conventions]] for the full rule):
- `{NAME} PRD.md`, `{NAME} Todo.md`, `{NAME} Roadmap.md`
- `{NAME} Docs/`, `{NAME} Dev/`, `{NAME} bio/`
- `{NAME} bio/{NAME} Chemistry.md` — nested files still carry the prefix

## Format

```
{TLC} — {Full Name}              ← H1 heading

desc:: One-line description of the anchor

| {NAME} Docs   | --------------------------------              |
| -------------- | --------------------------------------------- |
| ...            | ...                                           |
```

## Heading

- **With TLC**: `CLF — Claudifier` (as H1 heading)
- **Without TLC**: `2026 Daves Finances` (as H1 heading)

## Description Property

The `desc::` line appears immediately after the heading. This is a machine-readable property that can be synced bidirectionally with the TLC index via `scan_tlc.py sync`.

```markdown
desc:: macOS enhancements to speed the use of Claude Code
```

## Link Table

The link table organizes references to related pages. It uses a markdown table with two columns:

| Row | Purpose |
|-----|---------|
| **External** | Links to external resources (GitHub repos, websites, etc.) |
| **Research** | Research pages and references |
| **{NAME} Docs** | Links to planning docs (PRD, Features, Notes) |
| **User Docs** | Links to user-facing documentation (User Guide, Architecture) |
| **Execution** | Links to execution docs (Todo, Roadmap) |

Not all rows are required — use what's appropriate for the anchor. Simple anchors may have no link table at all.

**Example (with TLC):**
```markdown
| [[CLF Docs]]     | --------------------------------               |
| ---------------- | ---------------------------------------------- |
| External         | [Repo](https://github.com/oblinger/claudifier) |
| [[CLF Docs]]     | [[CLF PRD]], [[CLF Features]], [[CLF Notes]]   |
| User Docs        | [[CLF User Guide]], [[CLF Architecture]]       |
| - Execution      | [[CLF Todo]], [[CLF Roadmap]]                  |
```
