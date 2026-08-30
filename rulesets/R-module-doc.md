# RULESET R-module-doc
include::
where:: `file:{anchor}/**/{slug} Dev/**/{slug} *.md`
description:: per-module source documentation — one doc per source module under `{slug} Dev/`

What `/audit module-doc` checks on a module doc. Cardinality: many — one per source module, mirroring the repo tree. Format of this set: [[DAS Ruleset]].

> **Not armed 2026-08-11 ([[Tink Backlog#^T349|T349]]), and the blocker is three independent unsatisfiabilities stacked on one selector.** Measured against the real corpus — **443 module docs across 14 anchors**, the largest single population any dormant ruleset claims.
>
> **(1) The folder name is a generation stale.** The selector says `{slug} Dev/`; the corpus and [[DAS Dev Dispatch]] both say `{slug} Dev Docs/` (*"root-level folder, Gen-3"*). Zero folders in the vault are named `* Dev` — 14 are named `* Dev Docs`. [[R-dev-dispatch]] already spells it the current way; this set was never updated with it.
>
> **(2) Every one of those 14 folders carries its own `.anchor`**, so `sub_anchor_roots` drops the entire folder from the parent anchor's scope. The selector is written from the parent's point of view (`{anchor}/**/{slug} Dev Docs/**`) and is therefore unsatisfiable from **both** ends at once — out of scope from the parent, and from the folder itself `{anchor}` *is* the Dev Docs folder, so the pattern demands a second one nested inside. This is [[Tink Backlog#^T522|T522]]'s folder-shaped-facet defect exactly; `_match_file_glob`'s own-directory-name candidate was added for it, and does not reach this case, because —
>
> **(3) `{slug}` resolves to the wrong slug there.** None of the 14 `.anchor` files declares `slug:`, so `_anchor_name` falls back to the basename and `{slug}` expands to `DKT Dev Docs`, not `DKT`. The pattern becomes `DKT Dev Docs *.md` while every real file is `DKT Something.md`. Verified on DKT, OBU and DMUX: **0 targets, from every direction tried.**
>
> Fixing (1) alone would look like a repair and change nothing — which is what makes this worth writing down rather than patching. The set is blocked on a decision it cannot make for itself: either the Dev Docs folders declare their parent's slug, or folder-shaped facets get a selector form that names the parent. [[R-dev-dispatch]], [[R-all-files]] and [[R-code-surface]] sit behind the same three, and are counted separately in T212's 37 only because they are separate files.

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
