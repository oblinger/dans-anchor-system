# RULESET R-markdown
include::
import:: skills/audit/scripts/audit-plan.py
where:: `**/*.md`
description:: Mechanical + authoring rules for every markdown document; cited by every facet and skill that produces markdown.

Embedded ruleset for the markdown discipline. Adoption is implicit — every markdown doc in the vault is subject to these rules, no explicit include:: needed in {slug} Decisions.md. (The catalog still lists R-markdown as a child of the R-facet umbrella for completeness.) Checked rules with a `check::` reference execute mechanically through the audit-plan checker registry (and auto-heal via `fix::` on the on-write doc-fire); checked rules without one are agent-judged at /audit against their **Check pattern**.

### RULE R-markdown-01 — Escape pipes inside wiki-links inside tables (checked)
description:: A wiki-link in a table cell escapes its alias pipe — [[Target\|alias]] — so the cell doesn't terminate early.
check:: md_table_pipe_escape
fix:: md_table_pipe_escape
A wiki-link in a table cell has an unescaped `|` — write it `\|` so the cell keeps its column count.

**Check pattern:** on each line whose **code-masked** form starts with `|`, every `[[…]]` span is free of an unescaped `|`. Masking is length-preserving, so a fenced example of a table row is not a table row and the reported line numbers still point at the real file.

**Why:** the table breaks visibly — column counts go wrong, content disappears.

### RULE R-markdown-02 — Tables have blank line before and after (checked)
description:: A markdown table is preceded and followed by a blank line so Obsidian renders it.
check:: md_table_blank_lines
fix:: md_table_blank_lines
A table is touching the line above or below it — add a blank line on each side so Obsidian doesn't merge it into the surrounding paragraph.

**Check pattern:** a table is a `|`-leading line followed by a `|---|` delimiter row, outside any fence. The line before the header and the line after the last `|`-leading row are both blank (or the file boundary).

### RULE R-markdown-03 — No wiki-links or headings inside fenced code blocks (checked)
description:: A fenced block holding renderable markdown ([[links]], headings, tables) the reader expects to click is a smell.

**Check pattern:** a fenced code block contains a `[[wiki-link]]`, heading, or table the reader would expect to click or navigate.

A fenced code block contains a `[[wiki-link]]`, heading, or table the reader would expect to click or navigate — they render as inert literal text. If you're quoting syntax for illustration, use single backticks; if the reader should click it, move it outside the fence.

**Why:** a link-shaped string with no link is worse than no string at all.

### RULE R-markdown-04 — References to vault documents use wiki-links, not backticks (checked)
description:: A reference to a vault doc / anchor / page is a [[wiki-link]]; backticks are reserved for code identifiers.

**Check pattern:** a backtick-wrapped `*.md` name or `SLUG Title`-shaped string that a reader could open in Obsidian.

A backtick-wrapped string looks like a reference to a vault document. If a reader could open it in Obsidian, make it a [[wiki-link]] — backticks are for code identifiers (source paths, function names, CLI flags, config keys), which rot silently when used for vault references.

### RULE R-markdown-05 — Em-dash is the real character U+2014, never double-hyphen (checked)
description:: Definition lists and prose use the em-dash character; double-hyphen does not auto-convert in Obsidian.
check:: md_em_dash
fix:: md_em_dash
A definition-list bullet (or prose) uses a spaced ` -- ` where it wants an em-dash — replace it with ` — ` so it reads right in Obsidian's reading view. `--flag` and `---` rules are untouched.

**Check pattern:** no line of the code-masked text contains the space-delimited ` -- `. Only the *spaced* form is flagged, which is what leaves `--flag` and a `---` rule alone without listing them as exceptions.

### RULE R-markdown-06 — Dataview inline fields have no `::` in the value (checked)
description:: For any key:: value line, the value carries no further :: token, which would collide with the Dataview parser.
check:: md_inline_field_value
A `key:: value` inline field has a second `::` in its value — Dataview will misparse it (the value truncates or the next field is eaten). Move any mention of a field name into a regular paragraph below the field line.

**Check pattern:** for every line matching `^<key>:: <value>`, the `<value>` contains no further `::` token.

### RULE R-markdown-07 — Body-only preferred for vault docs (checked)
description:: Vault docs are body-only with description:: inline as the second line; YAML frontmatter is reserved for SKILL.md.

**Check pattern:** the doc opens with `---` YAML frontmatter and is not a SKILL.md.

This vault doc opens with YAML frontmatter — prefer the body-only form with a visible `description::` inline as the second non-blank line. Frontmatter is invisible in Obsidian read view and drifts silently; only SKILL.md (read by Claude Code) needs it.

### RULE R-markdown-08 — Wiki-link form for code identifiers is forbidden (checked)
description:: Source paths, function names, CLI commands, and config keys go in backticks, never wiki-links.

**Check pattern:** a `[[wiki-link]]` whose target is a source path, extension-bearing file, or `fn()`-shaped identifier.

A `[[wiki-link]]` names a code identifier (a source path, a function, a CLI command) — that fabricates a link and pollutes the vault graph. Put code identifiers in backticks; keep wiki-links for vault-internal navigation.

### RULE R-markdown-09 — Definition list format for naming-natured content (stated)
description:: A list of named things uses the bolded-handle + em-dash + single-line-description form; procedural lists are exempt.
The lists in this doc whose items are *named things* (each has a recognizable handle or concept name) should use the definition-list form — a bolded 2–3 word handle, an em-dash, then a one-line description. Plain procedural lists ("first X, then Y") are exempt. Point out any naming-natured list that isn't in this form.

### RULE R-markdown-10 — Per-anchor docs don't restate facet-level rules (stated)
description:: A per-anchor doc does not restate rules that live in a facet spec; the facet is the single source of truth.
where:: `{anchor}/**/{slug} *.md`
This per-anchor doc looks like it restates universal format rules that belong in a facet (a Log's format rules live in [[DAS Log]], a PRD's in [[DAS PRD]]) — restated rules drift when the facet evolves. Drop the restatement and rely on the facet's embedded ruleset.

### RULE R-markdown-11 — Never put markdown inside a fenced code block (checked)
description:: A fence meant to show rendered markdown ([[links]], headings, tables) defeats itself; show live markdown or link a real instance.

**Check pattern:** an unlabeled or `markdown`/`md`-tagged fence containing markdown meant to be read as markdown.

A fenced code block (unlabeled or `markdown`/`md`-tagged) contains markdown meant to be *read as markdown* — `[[wiki-links]]` go inert and headings, tables, and emphasis don't render. Show the example as **live markdown** (its own `# H1`, with commentary BEFORE it so it can't bleed in) or link a real worked instance. Language-tagged fences (`python`, `bash`, `json`, …) are literal source and are not flagged.

**Why:** the whole point of an example is to show the *rendered* form. The user has corrected this repeatedly; it is absolute.

### RULE R-markdown-12 — Figures are embedded images; never mermaid, never text-based diagrams (checked)
description:: A figure is an exported image embedded with a width hint; mermaid blocks and ASCII box-art are forbidden.

**Check pattern:** a `mermaid` fence, or runs of box-drawing characters / `+---+` art used as a figure.

This doc draws a diagram as a `mermaid` block or ASCII box-art (`┌ ─ │ └ → ╮` runs, `+---+` character art used as a figure). A figure must be a real editable artifact — an Excalidraw / D2 / matplotlib export embedded with a page-fill width hint (`![[name.svg|2400]]`), source kept alongside. Redraw it that way.

### RULE R-markdown-13 — No stray `<tag>`-like angle brackets (checked)
description:: A bare <identifier> glued to a tag-name character is parsed as an unknown HTML element and eats text up to the next >.
check:: md_stray_angle_tag
A stray `<identifier>` (a `<` glued to a tag-name character, e.g. `<Name>` or `List<int>`) is read as an unknown HTML element and silently eats the text up to the next `>`. Fix it with intent — backtick it, escape as `&lt;`/`&gt;`, add spaces (`a < b`), or restructure. Inline code, real HTML constructs, single-letter placeholders (`F<n>`), and whitespace-surrounded comparisons are fine; `.html` files are skipped.

**Check pattern:** in the code-masked text, no `</?NAME>` span survives whose `NAME` is outside the allowed-tag set. Matching the *closing* `>` is what keeps `a < b` and `F<n>` out of scope without enumerating them.

### RULE R-markdown-14 — No trailing whitespace (checked)
description:: A line must not end in spaces or tabs; stripping trailing whitespace never removes content, so it is safe to normalize. One space after a terminal link is the R-markdown-16 pad and is exempt.
check:: md_trailing_ws
fix:: md_trailing_ws
A line ends in trailing whitespace — invisible noise that pollutes diffs and can create accidental hard-breaks. Strip it.

**Check pattern:** no line ends in a space or tab, **except** a line ending in a terminal link, which carries exactly one (the R-markdown-16 pad). Two or more spaces after a terminal link still fail — that is the hard-break form, not the pad.

**One exemption:** exactly one space following a *terminal link* is the canonical pad required by [[#RULE R-markdown-16 — Terminal links carry one trailing space (checked)|R-markdown-16]], not noise. Without the carve-out the two rules fight each other on every write — 16 appends the space, 14 strips it back — so the fixer collapses two-or-more trailing spaces after a link down to the canonical one rather than removing them all.

### RULE R-markdown-16 — Terminal links carry one trailing space (checked)
description:: A prose line whose last token is a wiki-link or markdown link ends with exactly one space, the canonical form shared with ha, so Obsidian does not expand the link to source when the line is clicked.
check:: md_terminal_link_pad
fix:: md_terminal_link_pad
In Obsidian, clicking a line whose last token is a link expands that link to its source form. One trailing space gives the click a non-link target and stops the expansion. It is invisible in reading view, live preview, and rendered HTML — pure ergonomics.

Exactly one space, never two: two trailing spaces are a markdown `<br>` hard break. The pad is only appended to a line that has none, so re-applying the rule is a no-op. A trailing `^block-anchor` or punctuation after the link means the link is not terminal and the rule does not fire. Struck links (`~~[[X]]~~`) are padded too — strikethrough is applied after padding, so refusing the struck form would strand the space and oscillate.

**Table rows are out of scope.** A padded cell's canonical form is two spaces before the closing `|` — one from ordinary `| cell |` spacing, one from the pad — so deciding whether a cell is already padded means inferring that table's baseline spacing, and column-aligned tables use padding for source readability that a normalizer would destroy. `ha` generates those cells and already pads them.

**Check pattern:** every prose line whose last token is a wiki-link or a markdown link ends in exactly one space. Table rows are out of scope; a line ending in a `^block-anchor` or in punctuation after the link is not terminal and does not fire.

**Why:** `ha` stamps this same form on the content it generates (HA F135). Two tools that rewrite the same lines must share ONE canonical form; if they disagree, each strips the other's space on every pass and the file churns forever. The checker is a direct port of HA's `ends_with_terminal_link` for exactly this reason — a re-derived predicate is how the two drift apart.

### RULE R-markdown-15 — SVG figure embeds carry an explicit width hint (checked)
description:: Every ![[name.svg]] embed carries a |width hint — |3000 for page-wide figures (the default), a smaller value only for a deliberately-inline thumbnail.
check:: md_svg_embed_width
fix:: md_svg_embed_width
A bare `![[x.svg]]` embed renders as a tiny fit-to-column thumbnail — the recurring mistake the viz doctrine exists to kill. The auto-fix appends the page-wide default `|3000` (Obsidian caps the hint to the pane, so a large value costs nothing; the file is byte-identical at any display width). A smaller hint is legitimate only for a deliberately-inline figure — set it explicitly and the rule stays satisfied. Scope is `.svg` only: raster embeds (screenshots, photos) often legitimately render at intrinsic size. Doctrine: viz skill § page-width default.

**Check pattern:** every `![[….svg]]` embed carries a `|<width>` hint. Scope is `.svg` only — raster embeds are untouched, since a screenshot at intrinsic size is usually right.

**Why:** authored figures are made to be read; fit-to-column shrink makes every diagram illegible by default and the author never notices until a reader does.

## Position in the catalog

Sits under [[R-doc]] (cross-cutting documentation conventions umbrella). [[R-md]] (the older "markdown rendering" ruleset under R-doc) is **superseded** by R-markdown — F139 sweeps remaining `[[R-md]]` citations.

## Adoption

Applies to every markdown doc in the vault — no explicit `include:: [[R-markdown]]` required in `{slug} Decisions.md`. (Listed in the catalog for completeness; vault-wide rules don't need per-anchor opt-in.)

## See also

- [[DAS markdown]] — discipline spec this ruleset enforces.
- [[R-doc]] — cross-cutting documentation conventions umbrella.
- [[R-md]] — predecessor; superseded by R-markdown per F139.
- [[DAS progressive-disclosure]] — sibling discipline; its rules live separately (preface zone, dispatch patterns, figure placement).
- [[DAS Rulesets]] — top-level catalog.
