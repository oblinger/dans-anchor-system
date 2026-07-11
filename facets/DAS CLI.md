---
description: The command-line specification facet — the full command surface for an anchor that ships a CLI, opened by a compressed `--help` figure (an SVG); a design-pipeline doc downstream of UX Design
---
# FCT CLI
Facet spec for `{slug} CLI.md` — the **command-line specification** for an anchor that ships a CLI: a compressed `--help` figure (an SVG) opens the doc, then the full command surface is specified below. Authored in the design pipeline, downstream of UX Design.

| **FCT CLI**                                                          | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Design Docs]] → [FCT CLI](hook://p/DAS%20CLI)<br>: command-line specification facet |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Related                                                              | [[DAS UX Design\|UX Design]],  [[DAS API Design\|API Design]],  [[DAS Design Folder\|Design]],  [[DAS TSK User Guide\|User Guide]]                           |
| Examples                                                             | [[HBR CLI\|worked example]]                                                                                                        |
|                                                                      |                                                                                                                                                   |
| **Table of Contents**                                                |                                                                                                                                                   |
| [[#The Help Block — READ THIS\|Help block — READ THIS]]              | the fenced `--help` block — the doc's central figure                                                                                              |
| [[#Progressive disclosure — the drill-down\|Progressive disclosure]] | optional per-command drill-down                                                                                                                   |
| [[#Location — a migrating reference\|Location]]                      | Design/ (authored) → User Docs/ (graduated)                                                                                                       |
| [[#Optional Sections\|Optional Sections]]                            | env vars / config / exit codes / output modes                                                                                                     |
| [[#Linking\|Linking]]                                                | where the CLI doc is linked from                                                                                                                  |
| [[#When to Create\|When to Create]]                                  | create iff the anchor ships a CLI                                                                                                                 |
| [[#BRIEF\|BRIEF]]                                                    | maintainer notes                                                                                                                                  |

**TLDR** — `{slug} CLI.md` is the **full command-line specification** of an anchor's CLI. It opens with a compressed `--help` **figure** — rendered as an **SVG** (from a `.txt` source via `cli-help-svg.py`, so aligned `# comments` never re-wrap) — that maps the whole surface at a glance; below it, each command is specified in full (flags, defaults, semantics, exit behaviour). The figure is compressed; the document is not. **Cardinality: one per anchor**, only when it ships a CLI. **Home:** authored at `{slug} Design/{slug} CLI.md`; as a *migrating reference* it graduates to `{slug} User Docs/` once the CLI stabilizes.

`{slug} CLI.md` is the **full specification** of an application's command-line surface. The compressed `--help` figure at the top is the overview — the whole surface on one screen; the body below is the complete reference, documenting each command's flags, defaults, semantics, and exit behaviour. The figure is compressed; the document is not.

**Only create this file when the anchor actually has a CLI.** It is optional. GUI-only, library-only, or daemon-only anchors have no CLI doc — a library's surface is [[DAS API Design]], a GUI's is [[DAS UX Design]].

## Relationship to the other design docs

- [[DAS UX Design]] — the CLI doc is **downstream of UX Design**: UX Design decides *that* there is a CLI and its command shape (verbs, grouping, the interaction model); `{slug} CLI.md` is the concrete `--help` realization of that decision.
- [[DAS API Design]] — sibling programmatic surface. An anchor with both a CLI and a library form carries both (e.g. [[HBR]]).
- [[DAS TSK User Guide]] / `{slug} User Guide.md` — the **tutorial** (narrative, teaches the few commands a newcomer needs). The CLI doc is the **reference** (the whole surface, look-up-oriented). Guide links to CLI for "full surface"; CLI links back to Guide for "getting started."

# Reference Example

The whole doc — a compressed help figure (SVG) over the full command spec (a `{slug} CLI.md` for a task-scheduler `tool`):

````markdown
---
description: "command-line specification — a compressed --help figure over the full command reference"
---

:>> [[{slug}]] → [[{slug} Design]]

# {slug} CLI
The command-line specification of `{tool}` — a compressed `--help` figure (below), then the full command reference.

![[{tool} CLI Help.svg|1100]]

For a tutorial introduction, see [[{slug} User Guide]]. Every command is specified below; a simple one gets a one-line note, a complex one its own section.

## Notes

- **submit** — `--deadline` (ISO-8601) is required; `--retry N` defaults to 3; `--priority 0–9` defaults to 5. The command to enqueue follows a literal `--`. Exits non-zero (2) if the scheduler is unreachable.
- **status** — `--filter` takes one of `pending | running | done | failed`; `--json` emits machine-readable output for scripts.
````

*(The figure is the compressed overview; the `## Notes` below specify the commands in full — `submit` / `status` carry their flag detail, `cancel` / `drain` are simple enough for a one-line note.)*

# Format Specification

## The Help Block — READ THIS

**The help block is this doc's central figure.** Per the universal opening format ([[DAS Doc Structure]] / [[DAS progressive-disclosure]]): `:>>` breadcrumb → `# {slug} CLI` H1 → **one-line summary** → **help block**. The block sits directly after the summary line — no `## Synopsis` wrapper, no second intro paragraph between the summary and the fence. (An optional one-line install/usage note may follow the block.)

Inside the figure: every command the CLI exposes, **one per line**, each with a trailing `# comment` giving its one-line purpose, comments **column-aligned**. It reads exactly like the `--help` output of a well-written UNIX tool — the reader's single-screen map of the whole surface.

**Rules for the help figure:**

- **An SVG figure, not a code fence.** The help block is rendered to `{slug} CLI Help.svg` from a plain-text `{slug} CLI Help.txt` source by `cli-help-svg.py` (alongside this facet). A code fence re-wraps long lines at the render width and destroys the aligned `# comments`; the SVG fixes the geometry so it reads correctly at any width. Embed near its natural pixel width (`![[{slug} CLI Help.svg|1100]]`) — sized so text stays readable, never a 3000px canvas shrunk to tiny type. The `.txt` is the source of truth; regenerate the `.svg` after editing it.
- **Complete.** Every command the binary exposes appears, including `--help` and `--version`. The figure *is* the command inventory.
- **One line per command.** No multi-line invocations; a rare corner case goes to its drill-down note below.
- **Summary flag form.** `[--json]`, `[--filter <state>]`, `<task-id>` — just enough to know what the command takes. `<required>` in angle brackets, `[--optional]` in square brackets.
- **Aligned trailing `# comment` on every line** — the one-line purpose (same alignment discipline as [[DAS All Files]]).
- **No wiki-links inside the figure** — it's an image; navigation links go on the line immediately after it.
- **Mirror `{tool} --help`.** If the binary supports `--help`, the figure is a faithful rendering of that output.

## Below the figure — the full command specification

After the help figure, specify the command surface **in full** — each command documented to the depth it needs. The figure is the compressed overview; this is the complete reference.

Two forms, by command complexity:

- **A `## Notes` bullet** — for a simple command: its non-obvious flags (name, default, required-ness), the payload convention, and any surprising exit behaviour, in a sentence or two.
- **A full `## <command>` H2** — for a complex command: a one-line description, a `**Usage:**` block, a flags table, and a worked `**Example:**`. Use this freely wherever a command's flags or semantics warrant it.

The only thing to avoid is **empty restatement** — a Flags table that merely repeats a self-evident one-flag command adds nothing. Completeness is the goal; padding is not.

## Location — a migrating reference

The CLI doc is a **migrating reference** (per [[DAS Design Folder]] § Reference is a migrating role):

- **Authored** at `{slug} Design/{slug} CLI.md` — a design-pipeline doc, downstream of UX Design, written while the command surface is still being decided.
- **Graduates** to `{slug} User Docs/{slug} CLI.md` once the CLI stabilizes and end users consult it as a look-up reference.

Either home is valid; which one it sits in reflects how settled the CLI is. Both are `{slug} CLI.md` — the basename never changes, so links survive the move.

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

1. Its home dispatch page — `{slug} Design.md` (while authored) or `{slug} User Docs.md` (once graduated) — as a row: `| [[{slug} CLI\|CLI]] | command surface |`.
2. **`{slug}.md` anchor page** — on the relevant row: `… [[{slug} CLI\|CLI]] …`.

`/audit docs` flags a missing CLI doc on anchors whose UX Design spec calls for a CLI.

## When to Create

Create `{slug} CLI.md` when the anchor ships an executable (Rust `[[bin]]`, Python entry point, shell script) whose command surface is worth showing at a glance — more than a single one-shot invocation. A one-shot `tool --input FILE --output FILE` can be documented inline in `{slug} User Guide.md` without a separate CLI doc.

# RULESET R-cli
include::
where:: `file:{anchor}/**/{slug} CLI.md`
description:: the `{slug} CLI.md` command-line specification format (a compressed SVG help figure over the full command reference)

What `/audit docs` checks on a CLI doc. Optional — only an anchor that ships a CLI carries one. Format of this set: [[DAS Ruleset]].

### RULE R-cli-01 — Lives at `{slug} Design/` (authored) or `{slug} User Docs/` (graduated) (checked)

The CLI doc is a migrating reference: its basename is `{slug} CLI.md` and its parent chain includes either `{slug} Design` or `{slug} User Docs`.

**Check pattern:** basename is `{slug} CLI.md` and an ancestor folder is `{slug} Design` or `{slug} User Docs`.

**Why:** authored in the design pipeline downstream of UX Design; graduates to User Docs once stable (§ Location).

### RULE R-cli-02 — Help figure is the doc's central figure, right after the one-line summary (checked)

The doc follows the universal opening format ([[DAS Doc Structure]] / [[DAS progressive-disclosure]]): breadcrumb → `# {slug} CLI` H1 → **one-line summary** → the **help figure** (the SVG `--help` render) as the doc's central figure. Nothing else sits between the summary and the figure — no `## Synopsis` wrapper, no second intro paragraph. (An optional one-line install/usage note may follow it.)

**Check pattern:** the H1 is followed by a single summary line, then the help-figure embed (`![[{slug} CLI Help.svg…]]`) as the first figure-level element — not buried under `##` prose sections.

**Why:** the help figure is the CLI's "overview picture" — the single-screen map of the whole surface — and in the progressive-disclosure opening the figure sits right after the summary; extra preamble buries it (§ The Help Block).

### RULE R-cli-03 — Help figure is complete, one line per command, aligned trailing `# comment` (checked)

In the `{slug} CLI Help.txt` source (rendered to the SVG figure): every command the binary exposes (including `--help` and `--version`), one per line, each with a column-aligned trailing `# comment` stating its one-line purpose. No multi-line invocations.

**Check pattern:** every non-blank line in the `.txt` source is a single command with a `#` comment; comments are column-aligned; a `{slug} CLI Help.svg` exists alongside.

### RULE R-cli-04 — Help figure is an SVG rendered from a `.txt` source (checked)

The help block is an SVG image (`{slug} CLI Help.svg`) rendered from `{slug} CLI Help.txt` by `cli-help-svg.py` — not a markdown code fence, which re-wraps at the render width and destroys the aligned comments. Navigation links go on the line after the embed, never inside the figure.

**Check pattern:** the help block is an `![[{slug} CLI Help.svg…]]` embed with a sibling `.txt` source; no fenced `--help` code block remains under the H1.

### RULE R-cli-05 — The body is the full command specification; the figure is its compressed overview (stated)

Below the help figure, the doc specifies the **full command surface** — each command's flags, defaults, semantics, and error/exit behaviour. The figure is the compressed one-screen overview; the body is the complete reference. Use a `## Notes` bullet for a simple command and a `## <command>` H2 for a complex one, but aim for **completeness**. The only thing to skip is genuinely self-evident restatement — a Flags table that merely repeats an obvious one-flag command adds nothing.

**Why:** the CLI doc is the command-line *specification*. Only the top figure is compressed; the document itself is the full reference.

### RULE R-cli-06 — Optional sections carry real information, never boilerplate (stated)

Environment-variable, config-file, global-exit-code, and output-mode sections appear only when the CLI actually has them. Absent behaviour is never documented as "none."

### RULE R-cli-07 — Help block reads like real `--help`: public surface only, no internal references (checked)

Inside the fence: the **public command surface as a user sees it**. No internal tracking references (feature / ticket numbers like `F023`), no design-status annotations (`(shipped)` / `(wire-up)` / `(new)`), no wiki-link or design-doc cross-refs. Grouping is optional and light — for a small surface a flat command list ("boom, boom, boom") is preferred over category headers; never annotate a group header with a tracking number. A complex command gets a **compact one-line entry** in the block plus a drill-down below (§ Progressive disclosure — the drill-down) — never a multi-line, flag-stretched entry inside the block.

**Check pattern:** no `F\d+`, no `(shipped|wire-up|new)` marker, and no `[[…]]` token appears between the help fence's open and close; each command occupies exactly one line.

**Why:** the block mirrors `tool --help` — a user-facing contract. Feature numbers, build-status markers, and multi-line flag dumps are design-doc bookkeeping that make it stop reading like a help screen (the exact drift this facet exists to prevent).

### RULE R-cli-08 — The CLI doc carries no implementation-status section (checked)

A `{slug} CLI.md` documents the command *interface*, not build progress. No `## Status` / "partly shipped" / "what's done" section, and no per-command build-state markers ((shipped) / (wire-up) / (new)) in the body. Implementation status lives in the anchor's tracking artifacts — [[DAS Status]] (`{slug} Status.md`), the Roadmap, the Backlog — never on the reference doc.

**Check pattern:** no `## Status` heading and no `(shipped|wire-up|new)`-style build-state markers in the doc body.

**Why:** a documentation page is a stable interface reference; interleaving progress state dates it instantly and duplicates the tracker (the single source of truth for status).

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + ruleset R-cli above; § The Help Block and § Progressive disclosure are the canonical sources.)*

- **Keep instance content out** — this is the spec, not a CLI doc; a real binary's commands belong in the linked working example ([[HBR CLI]]).
- **It's the command-line *specification* — only the top figure is compressed** — the doc gives the full command reference below the SVG help figure (R-cli-05). Don't reframe the whole doc as "compressed/minimal" (regressed and corrected 2026-07-02).
- **The help block is an SVG, not a code fence** — rendered from `{slug} CLI Help.txt` by `cli-help-svg.py` (R-cli-04) so aligned comments can't re-wrap. Edit the `.txt`, regenerate the `.svg`, embed near natural width (~1100px).
- **Help block is the figure, right after the one-line summary** — R-cli-02: breadcrumb → H1 → summary → block; no `## Synopsis` wrapper, no second intro paragraph. The block reads like real `--help` (R-cli-07): no feature numbers, no status markers, no stretched multi-line entries.
- **Migrating home, not a fixed one** — the doc lives in `{slug} Design/` while authored and `{slug} User Docs/` once graduated (§ Location); R-cli-01's `where::` matches both. Don't re-pin it to a single folder.
- **Cross-cite rather than inline** — tutorial/narrative content belongs in [[DAS TSK User Guide]], CLI-*shape* design in [[DAS UX Design]], markdown rendering rules in [[R-markdown]]; if a rule drifts toward one of those, move or link rather than duplicate.
