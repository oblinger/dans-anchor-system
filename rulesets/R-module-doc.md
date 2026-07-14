# RULESET R-module-doc
include::
where:: `file:{anchor}/**/{slug} Dev/**/{slug} *.md`
description:: per-module source documentation — one doc per source module under `{slug} Dev/`

What `/audit module-doc` checks on a module doc. Cardinality: many — one per source module, mirroring the repo tree. Format of this set: [[DAS Ruleset]].

### RULE R-module-doc-01 — Doc tree mirrors the source tree under `{slug} Dev/` (checked)

Every source directory gets a parallel `{slug} {dir}/` folder under `{slug} Dev/`; every source file with public API gets a `{slug} {ClassName}.md` named after its **primary class**, not the filename. All files/folders carry the `{slug}` prefix.

**Check pattern:** for each module doc, a corresponding source module exists at the mirrored path; the doc name matches the primary class.

### RULE R-module-doc-02 — Two zones: Overview then Class Method Details (checked)

A module doc has an Overview zone (frontmatter, H1+brief, SECTIONS table, per-class overview sections with class tables — no method-body prose) and a `# Class Method Details` zone (per-class deep-dive H2s with concept H3s and per-method H3s).

**Check pattern:** the doc has exactly two H1s — `# {slug} {ModuleName}` and `# Class Method Details`; no method-body prose appears in the overview zone.

### RULE R-module-doc-03 — SECTIONS table indexes each section with a typed block-ID link (checked)

After the file overview, a 2-column `SECTIONS` table (header literally `SECTIONS`, not `CLASSES`) lists each section: column 1 is a block-ID wiki-link plus a trailing lowercase type word (`class`, `enum`, `topic`, …); column 2 is a one-line role.

**Check pattern:** the index table's header is `SECTIONS`; each row's first cell is `[[#^id\|Name]] <type>`.

### RULE R-module-doc-04 — Method links bold-wrap the link with the tail as a separate code span (checked)

Class-table method rows use `**[[#^Class-method\|method]]**\`(args) -> Return\`` — bold wraps the wiki-link, the alias is plain text (NO backticks inside the alias), the signature tail is a separate code span. Method block-IDs are `^ClassName-methodname`.

**Check pattern:** no method-row link puts backticks inside the alias; every method block-ID is class-prefixed.

**Why:** backticks inside a wiki-link alias do not render in Obsidian — the literal asterisks and backticks show.

### RULE R-module-doc-05 — Figures are SVG only, authored via `[[viz-excalidraw]]` (checked)

The top-of-doc figure is an SVG co-located with the doc (`{slug} {ModuleName}.svg`), embedded `![[{slug} {ModuleName}.svg]]`, authored from a sibling `.excalidraw` source via the viz workflow. Mermaid and ASCII-art-in-fences are forbidden.

**Check pattern:** any embedded figure is `.svg` (not mermaid, not an ASCII fence); an `.excalidraw` source sits beside it.

### RULE R-module-doc-06 — Module doc is linked into Dev + Files dispatch before authoring (stated)

Before writing a module doc, add its row to `{slug} Dev.md` (Dev dispatch) and to `{slug} Files.md` (Files tree). An unlinked module doc is invisible.
