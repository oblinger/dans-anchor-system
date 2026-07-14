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
