---
description: CLI command surface — a compressed, `--help`-style command reference, progressively disclosed; a design-pipeline doc downstream of UX Design
---

| **FCT CLI**<br>Anchor Page | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Design Docs]] → [FCT CLI](hook://p/FCT%20CLI)<br>: compressed `--help` command-surface facet |
| --- | --- |
| Related | [[FCT UX Design\|UX Design]],  [[FCT API Design\|API Design]],  [[FCT Design\|Design]],  [[CAB User Guide\|User Guide]] |
| Examples | [[CAE CLI\|minimal]],  [[HBR CLI\|fuller]] |

# FCT CLI
Facet spec for `{NAME} CLI.md` — the compressed, `--help`-style command surface for an anchor that ships a CLI, authored in the design pipeline (downstream of UX Design) and disclosed progressively.

**Table of Contents**

| Section |  |
| --- | --- |
| [[#The Help Block — READ THIS\|Help block — READ THIS]] | the fenced `--help` block — the doc's central figure |
| [[#Progressive disclosure — the drill-down\|Progressive disclosure]] | optional per-command drill-down |
| [[#Location — a migrating reference\|Location]] | Design/ (authored) → User Docs/ (graduated) |
| [[#Optional Sections\|Optional Sections]] | env vars / config / exit codes / output modes |
| [[#Linking\|Linking]] | where the CLI doc is linked from |
| [[#When to Create\|When to Create]] | create iff the anchor ships a CLI |
| [[#BRIEF\|BRIEF]] | maintainer notes |

**TLDR** — `{NAME} CLI.md` presents an anchor's command-line surface the way a well-written UNIX tool's `--help` does: a one-line summary under the H1, then the fenced **help block as the doc's central figure** (every command, one line, aligned trailing `# comment`), then — **only** for the commands that need more than their one-liner — light per-command drill-down. **Progressive disclosure is the whole ethic:** the help block IS the doc; detail is added a command at a time, never an exhaustive man-page up front. **Cardinality: one per anchor**, only when it ships a CLI. **Home:** authored at `{NAME} Design/{NAME} CLI.md` (a design-pipeline doc, downstream of UX Design); as a *migrating reference* it graduates to `{NAME} User Docs/` once the CLI stabilizes.

`{NAME} CLI.md` is the **command surface** of an application that ships a command-line interface — presented compactly, the way you'd read `tool --help` piped through a pager. It is **not** an exhaustive man page: you do not write a Flags table and an Exit-codes table for every command up front. You write the help block that shows the whole surface at a glance, then disclose the detail of a command *only when that command's one-line entry can't carry it*.

**Only create this file when the anchor actually has a CLI.** It is optional. GUI-only, library-only, or daemon-only anchors have no CLI doc — a library's surface is [[FCT API Design]], a GUI's is [[FCT UX Design]].

## Relationship to the other design docs

- [[FCT UX Design]] — the CLI doc is **downstream of UX Design**: UX Design decides *that* there is a CLI and its command shape (verbs, grouping, the interaction model); `{NAME} CLI.md` is the concrete `--help` realization of that decision.
- [[FCT API Design]] — sibling programmatic surface. An anchor with both a CLI and a library form carries both (e.g. [[CAE]]).
- [[CAB User Guide]] / `{NAME} User Guide.md` — the **tutorial** (narrative, teaches the few commands a newcomer needs). The CLI doc is the **reference** (the whole surface, look-up-oriented). Guide links to CLI for "full surface"; CLI links back to Guide for "getting started."

# Reference Example

The whole doc, in the compressed form (a `{NAME} CLI.md` for a task-scheduler `tool`):

````markdown
---
description: "command surface — every command, compressed --help form"
---

:>> [[{NAME}]] → [[{NAME} Design]]

# {NAME} CLI
Command surface of `{tool}` — every command in one screen; the fenced help block below is this doc's central figure.

```
{tool} --help                                       # Show this help text
{tool} --version                                    # Print version
{tool} submit --deadline <t> [--retry N] -- <cmd>   # Enqueue a task at the deadline
{tool} status [--json] [--filter <state>]           # Show task states and queue depth
{tool} cancel <task-id>                             # Cancel a pending task
{tool} drain [--timeout <sec>]                      # Wait for all pending tasks to finish
```

For a tutorial introduction, see [[{NAME} User Guide]]. Commands that need more than their one-line entry are detailed below; the rest are self-explanatory from the block.

## Notes

- **submit** — `--deadline` (ISO-8601) is required; `--retry N` defaults to 3; `--priority 0–9` defaults to 5. The command to enqueue follows a literal `--`. Exits non-zero (2) if the scheduler is unreachable.
- **status** — `--filter` takes one of `pending | running | done | failed`; `--json` emits machine-readable output for scripts.
````

*(Six commands; only the two with non-obvious flags get a note. `cancel`, `drain`, `--version`, `--help` carry no section — their one-line entry says everything. That restraint IS the progressive-disclosure ethic.)*

# Format Specification

## The Help Block — READ THIS

**The help block is this doc's central figure.** Per the universal opening format ([[FCT Doc Structure]] / [[DSC progressive-disclosure]]): `:>>` breadcrumb → `# {NAME} CLI` H1 → **one-line summary** → **help block**. The block sits directly after the summary line — no `## Synopsis` wrapper, no second intro paragraph between the summary and the fence. (An optional one-line install/usage note may follow the block.)

Inside the fence: every command the CLI exposes, **one per line**, each with a trailing `# comment` giving its one-line purpose, comments **column-aligned**. It reads exactly like the `--help` output of a well-written UNIX tool — it is the reader's single-screen map of the whole surface.

**Rules for the block:**

- **Fenced code block, not 4-space indent.** The fence is the first content under the H1.
- **Complete.** Every command the binary exposes appears here, including `--help` and `--version`. The block *is* the command inventory.
- **One line per command.** No multi-line invocations inside the block; a rare corner case goes to its drill-down note.
- **Summary flag form.** `[--json]`, `[--filter <state>]`, `<task-id>` — just enough to know what the command takes. `<required>` in angle brackets, `[--optional]` in square brackets.
- **Aligned trailing `# comment` on every line** — the one-line purpose (same alignment discipline as [[FCT All Files]]).
- **No wiki-links inside the block** — code fences don't render them; navigation links go on the line immediately after the block.
- **Mirror `{tool} --help`.** If the binary supports `--help`, this block is a faithful rendering of that output.

## Progressive disclosure — the drill-down

After the help block, disclose per-command detail **only for the commands that need more than their one-line entry**. This is the core difference from an exhaustive man page: most commands are fully specified by their help-block line and get **no section at all**.

Two forms, lightest first:

- **A `## Notes` bullet** (default) — one bullet per command that needs it: the non-obvious flags (name, default, required-ness), the payload convention, and any surprising exit behaviour, in a sentence or two. Enough for the large majority of commands.
- **A full `## <command>` H2** (only when a command is genuinely complex) — one-line description, a `**Usage:**` block, and — *if they carry real information* — a flags table and/or a worked `**Example:**`. Reserve this for commands with many flags or subtle semantics.

**Do not** write a Flags table + Exit-codes table + Example for a command whose help-block line already says everything. Exhaustiveness is the anti-pattern this facet exists to prevent — the shipped `--help` is the contract; the doc mirrors it and annotates only the sharp edges.

## Location — a migrating reference

The CLI doc is a **migrating reference** (per [[FCT Design]] § Reference is a migrating role):

- **Authored** at `{NAME} Design/{NAME} CLI.md` — a design-pipeline doc, downstream of UX Design, written while the command surface is still being decided.
- **Graduates** to `{NAME} User Docs/{NAME} CLI.md` once the CLI stabilizes and end users consult it as a look-up reference.

Either home is valid; which one it sits in reflects how settled the CLI is. Both are `{NAME} CLI.md` — the basename never changes, so links survive the move.

## Optional Sections

Include only when they carry real information (never as boilerplate):

| Section | When to include |
|---------|-----------------|
| **Environment variables** | The CLI respects any (`{TOOL}_CONFIG`, `NO_COLOR`, …) |
| **Config file** | The CLI reads a config file — show the format |
| **Exit codes (global)** | Exit codes are non-obvious and shared across commands |
| **Output modes** | The CLI has `--json` / `--quiet` / `--verbose` conventions |

## Linking

The CLI doc is linked from:

1. Its home dispatch page — `{NAME} Design.md` (while authored) or `{NAME} User Docs.md` (once graduated) — as a row: `| [[{NAME} CLI\|CLI]] | command surface |`.
2. **`{NAME}.md` anchor page** — on the relevant row: `… [[{NAME} CLI\|CLI]] …`.

`/audit docs` flags a missing CLI doc on anchors whose UX Design spec calls for a CLI.

## When to Create

Create `{NAME} CLI.md` when the anchor ships an executable (Rust `[[bin]]`, Python entry point, shell script) whose command surface is worth showing at a glance — more than a single one-shot invocation. A one-shot `tool --input FILE --output FILE` can be documented inline in `{NAME} User Guide.md` without a separate CLI doc.

# RULESET R-cli
include::
where:: `file:{ANCHOR}/**/{NAME} CLI.md`
description:: the `{NAME} CLI.md` compressed command-surface format

What `/audit docs` checks on a CLI doc. Optional — only an anchor that ships a CLI carries one. Format of this set: [[FCT Ruleset]].

### RULE R-cli-01 — Lives at `{NAME} Design/` (authored) or `{NAME} User Docs/` (graduated) (checked)

The CLI doc is a migrating reference: its basename is `{slug} CLI.md` and its parent chain includes either `{slug} Design` or `{slug} User Docs`.

**Check pattern:** basename is `{slug} CLI.md` and an ancestor folder is `{slug} Design` or `{slug} User Docs`.

**Why:** authored in the design pipeline downstream of UX Design; graduates to User Docs once stable (§ Location).

### RULE R-cli-02 — Help block is the doc's central figure, right after the one-line summary (checked)

The doc follows the universal opening format ([[FCT Doc Structure]] / [[DSC progressive-disclosure]]): `:>>` breadcrumb → `# {NAME} CLI` H1 → **one-line summary** (on the line directly under the H1, no blank line) → the fenced **help block as the doc's central figure**. Nothing else sits between the summary and the fence — no `## Synopsis` wrapper, no second intro paragraph. (An optional one-line install/usage note may follow the block.)

**Check pattern:** the H1 is followed by a single summary line, then a fenced code block as the first figure/table-level element — the help block is not buried under `##` prose sections.

**Why:** the help block is the CLI's "overview picture" — the reader's single-screen map of the whole surface — and in the progressive-disclosure opening the figure sits right after the summary; extra preamble buries it (§ The Help Block).

### RULE R-cli-03 — Help block is complete, one line per command, aligned trailing `# comment` (checked)

Inside the fence: every command the binary exposes (including `--help` and `--version`), one per line, each with a column-aligned trailing `# comment` stating its one-line purpose. No multi-line invocations in the block.

**Check pattern:** every non-blank line in the help fence is a single command with a `#` comment; comments are column-aligned.

### RULE R-cli-04 — No wiki-links inside the help block (checked)

The help fence carries no `[[…]]` links — code fences don't render them; navigation links go on the line immediately after the block.

**Check pattern:** no `[[…]]` token appears between the help fence's open and close.

### RULE R-cli-05 — Per-command drill-down is optional and progressive, never exhaustive (stated)

Detail below the help block is disclosed **only** for commands whose one-line entry can't carry it — as a `## Notes` bullet (default) or, for a genuinely complex command, a `## <command>` H2. A command fully specified by its help-block line gets **no section**. Do not emit a Flags table + Exit-codes table + Example for every command; the shipped `--help` is the contract and the doc annotates only the sharp edges.

**Why:** progressive disclosure is the facet's reason to exist — an exhaustive man-page is the anti-pattern it replaces.

### RULE R-cli-06 — Optional sections carry real information, never boilerplate (stated)

Environment-variable, config-file, global-exit-code, and output-mode sections appear only when the CLI actually has them. Absent behaviour is never documented as "none."

### RULE R-cli-07 — Help block reads like real `--help`: public surface only, no internal references (checked)

Inside the fence: the **public command surface as a user sees it**. No internal tracking references (feature / ticket numbers like `F023`), no design-status annotations (`(shipped)` / `(wire-up)` / `(new)`), no wiki-link or design-doc cross-refs. Grouping is optional and light — for a small surface a flat command list ("boom, boom, boom") is preferred over category headers; never annotate a group header with a tracking number. A complex command gets a **compact one-line entry** in the block plus a drill-down below (§ Progressive disclosure — the drill-down) — never a multi-line, flag-stretched entry inside the block.

**Check pattern:** no `F\d+`, no `(shipped|wire-up|new)` marker, and no `[[…]]` token appears between the help fence's open and close; each command occupies exactly one line.

**Why:** the block mirrors `tool --help` — a user-facing contract. Feature numbers, build-status markers, and multi-line flag dumps are design-doc bookkeeping that make it stop reading like a help screen (the exact drift this facet exists to prevent).

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + ruleset R-cli above; § The Help Block and § Progressive disclosure are the canonical sources.)*

- **Keep instance content out** — this is the spec, not a CLI doc; a real binary's commands belong in the linked working examples ([[CAE CLI]], [[HBR CLI]]).
- **Progressive disclosure is the load-bearing idea** — the reshape (2026-07-02) that made per-command detail *optional* is the whole point; do not let R-cli-05 drift back toward mandatory exhaustive tables.
- **Help block is the figure, right after the one-line summary** — R-cli-02: breadcrumb → H1 → summary → block; no `## Synopsis` wrapper, no second intro paragraph. The block reads like real `--help` (R-cli-07): no feature numbers, no status markers, no stretched multi-line entries.
- **Migrating home, not a fixed one** — the doc lives in `{NAME} Design/` while authored and `{NAME} User Docs/` once graduated (§ Location); R-cli-01's `where::` matches both. Don't re-pin it to a single folder.
- **Cross-cite rather than inline** — tutorial/narrative content belongs in [[CAB User Guide]], CLI-*shape* design in [[FCT UX Design]], markdown rendering rules in [[R-markdown]]; if a rule drifts toward one of those, move or link rather than duplicate.
