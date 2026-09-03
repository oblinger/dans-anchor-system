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

### RULE R-markdown-03 — No wiki-links or headings inside fenced code blocks (retired)

**Retired 2026-08-11 ([[Tink Backlog#^T349|T349]]), superseded by `R-markdown-11`** — same subject, and `-11` states it with the exemption this one lacks. Both read `(checked)` with no `check::`, so this set has been asking an LLM the same question twice on every markdown file it sees, and getting **contradictory** answers by construction: a `python` fence containing `[[` in a regex fails `-03` (which scopes to *any* fenced block) and passes `-11` (which exempts language-tagged fences as literal source). Two verdicts, one file, one subject — and the wrong one is the one this rule gives.

The retirement is the half that could be decided mechanically. `-11` carries the user's own framing (*show live markdown, or link a real instance*), the language-tag exemption that keeps real code out of scope, and now `check:: md_fence_no_markdown` — so retiring this rule loses no coverage and removes a judgment call that was being billed against every `.md` file in the anchor.

The superseded rule follows, for anyone tracing a historical finding.

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
check:: md_fence_no_markdown

**Check pattern:** an unlabeled or `markdown`/`md`-tagged fence containing markdown meant to be read as markdown.

A fenced code block (unlabeled or `markdown`/`md`-tagged) contains markdown meant to be *read as markdown* — `[[wiki-links]]` go inert and headings, tables, and emphasis don't render. Show the example as **live markdown** (its own `# H1`, with commentary BEFORE it so it can't bleed in) or link a real worked instance. Language-tagged fences (`python`, `bash`, `json`, …) are literal source and are not flagged.

**Why:** the whole point of an example is to show the *rendered* form. The user has corrected this repeatedly; it is absolute.

### RULE R-markdown-12 — Figures are embedded images; never mermaid, never text-based diagrams (checked)
description:: A figure is an exported image embedded with a width hint; mermaid blocks and ASCII box-art are forbidden.

**Check pattern:** a `mermaid` fence, or runs of box-drawing characters / `+---+` art used as a figure.

This doc draws a diagram as a `mermaid` block or ASCII box-art (`┌ ─ │ └ → ╮` runs, `+---+` character art used as a figure). A figure must be a real editable artifact — an Excalidraw / D2 / matplotlib export embedded with a page-fill width hint (`![[name.svg|2400]]`), source kept alongside. Redraw it that way.

### RULE R-markdown-13 — No stray `<tag>`-like angle brackets (checked)
description:: A bare `<identifier>` glued to a tag-name character is parsed as an unknown HTML element and eats text up to the next `>`.
check:: md_stray_angle_tag
A stray `<identifier>` (a `<` glued to a tag-name character, e.g. `<Name>` or `List<int>`) is read as an unknown HTML element and silently eats the text up to the next `>`. Fix it with intent — backtick it, escape as `&lt;`/`&gt;` or `\<`, add spaces (`a < b`), or restructure. Inline code, real HTML constructs, and whitespace-surrounded comparisons are fine; `.html` files are skipped.

**Single-letter placeholders are NOT exempt** — Q002, 2026-08-01. This rule granted `F<n>` an exemption until 2026-08-11 ([[Tink Backlog#^T349|T349]]) despite the ruling that revoked it: the feared storm was 25 occurrences in 15 files, mostly *shipped* DAS templates and skill docs where a bare `<n>` vanishes from the page a newcomer reads first, and T084 swept every site. The checker has never implemented the exemption, so for ten days the rule text and its docstring both offered an author a way to argue with a true finding. Stated here rather than left implicit because the exemption is the thing a reader will remember.

**Check pattern:** in the code-masked text, no `</?NAME …>` span survives whose `NAME` is outside the allowed-tag set. Two things are load-bearing. Matching the *closing* `>` is what keeps `a < b` out of scope without enumerating exceptions. Admitting **anything between the name and that `>`** is what brings `Box<dyn Error>` and `<the actual question, in prose>` into scope — the generic this rule's own text names, and the multi-word placeholder that is the commonest form of the fault; a matcher requiring `<WORD>` with nothing after the word passed both. A backslash-escaped `\<` is exempt on either end, because it is one of the fixes offered above.

**This rule had two implementations, and the second is deleted.** `md_angle_brackets_html_or_spaced` sat registered and called by nothing — the older design, which flags any surviving `<` followed by `[A-Za-z!/]` and masks a *curated* tag list of its own rather than reading `_HTML_ALLOW`. Measured over the 910 DAS-repo docs before deletion: it failed 20 to the wired checker's 15, and of the five extra, **three were false** — the regex lookbehind `(?<!` in this repo's own `R-query` check pattern, and `<span style="…">` in two `md` skill docs (`span` is real HTML the wired allow-list admits and the curated one omits). The other two, `<the actual question>` and `<full name>`, were true — and are exactly what the widening above now catches. So it is fully subsumed: everything it found correctly the wired checker finds, and the rest it found wrongly. Keeping a second implementation of one rule is how a corpus acquires two answers to one question.

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

Sits under [[R-doc]] (cross-cutting documentation conventions umbrella).

**`R-md` — the predecessor set — is deleted, 2026-08-11 ([[Tink Backlog#^T349|T349]]), finishing the fold F139 declared.** It had been marked *superseded by R-markdown* since 2026-06-09 and left on disk for two months, during which all three of its rules acquired live successors here: `R-md-02` (tables need blank lines) was a literal duplicate of `R-markdown-02` **sharing the same `md_table_blank_lines` implementation**, and `R-md-01` / `R-md-03` (angle brackets) are both subsumed by `R-markdown-13`. Nothing `include::`d it, so it fired on nothing and no finding is lost.

**What kept it alive was its last rule's `check::`, and that ref is why the deletion is the fix rather than a tidy-up.** `R-md-03` read `(checked)` and declared `check:: md_angle_brackets_backtick_only` — a checker **deliberately reverted** on 2026-08-01 (T071) after it measured **2,514 of 7,425 files**, 34% of the vault, the same unactionable-corpus signature [[R-naming]]-01 records at 39%. So the corpus held a `(checked)` rule pointing at a name registered nowhere: the sole surviving entry in `test-f289-checker-registration.py`'s `KNOWN_GHOSTS` ratchet and the sole surviving `registered by no imported module` warning from the live warden compile — carried, named and re-explained across four separate backlog rows (T071, T156, T172, T175), each of which had to stop and say *that one is known, pre-existing and out of scope*. A frozen exception is a cost paid on every future reading. With the set gone the ratchet is **empty** and the corpus compiles with **zero** resolution warnings, so the next ghost fails the suite instead of joining a list.

## Adoption

Applies to every markdown doc in the vault — no explicit `include:: [[R-markdown]]` required in `{slug} Decisions.md`. (Listed in the catalog for completeness; vault-wide rules don't need per-anchor opt-in.)

## See also

- [[DAS markdown]] — discipline spec this ruleset enforces.
- [[R-doc]] — cross-cutting documentation conventions umbrella.
- [[DAS progressive-disclosure]] — sibling discipline; its rules live separately (preface zone, dispatch patterns, figure placement).
- [[DAS Rulesets]] — top-level catalog.

### RULE R-markdown-17 — Fenced code lines fit without wrapping (checked)
description:: No line inside a fenced code block exceeds `fence_line_max` (global.yaml, 72 here); a longer line soft-wraps at render time and the fence's alignment is destroyed.
check:: md_fence_width
A code fence is the one place markdown promises fixed geometry — a `--help` figure, a file tree, an aligned `# comment` column. Obsidian soft-wraps a fenced line that is wider than the pane, and a wrapped line silently breaks that geometry: the comment column lands under the command, a tree's branches float free. Break the line, put the comment on its own line above the command, or render the figure as an SVG per [[DAS CLI]] (R-cli-04). **No exemption for URLs or paths** — a fenced URL that wraps is as unreadable as anything else; put it in prose.

**Check pattern:** every line inside a ``` or `~~~` fence (opener and closer excluded) is at most `fence_line_max` characters — a config key in `~/.config/anchor-system/global.yaml` beside `stone_line_max` (72 in this vault; 0/absent turns the rule off). Prose lines are unconstrained — prose is meant to wrap.

**Why:** Dan, 2026-09-03, on the rendered `DAS Stone CLI` figure whose every command wrapped at 72–73 characters: *"forbid writing into markdown with word wrap inside of a text section… a hard fail if you try to write a document that word wraps."* The refusal half is [[R-fence-guard]]; this rule is the law it enforces, and what audit-on-write reports for a Bash-written file the tool guard never saw. (Tier: checked)
