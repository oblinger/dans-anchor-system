# RULESET R-md
description:: Markdown rules — files render correctly across CommonMark renderers, with attention to Obsidian-specific gotchas. Adopt when authoring any .md file.
includes::

### RULE R-md-01 — Angle brackets need surrounding whitespace (checked)

Raw angle brackets in prose (`<word>`) get interpreted as HTML tag attempts and silently swallow content in Obsidian and several other renderers. Acceptable forms: `<verb>` inside backticks, `< verb >` with whitespace on both sides, or `&lt;verb&gt;` escaped.

**Why:** observed breakage in past docs where `<foo>` placeholders disappeared from the rendered view with no visible error.

**Check pattern:** grep for `\S<[A-Za-z_]` or `[A-Za-z_]>\S` outside code fences. Both are leading/trailing-whitespace-less angle brackets and fail.

### RULE R-md-02 — Tables need blank lines before and after (checked)

Markdown tables (pipe syntax) require a blank line above the header row and a blank line below the last row. Without surrounding blank lines, the table parser merges the table into adjacent paragraphs and renders broken or as raw text.

**Why:** Obsidian's table parser (and CommonMark's table extension) require blank-line delimiters; without them, the pipe-syntax bleeds into surrounding prose.

**Check pattern:** for every table (line starting with `|` followed by another line starting with `|---`), verify the line immediately before the header is blank AND the line immediately after the table-end is blank.

### RULE R-md-03 — Angle brackets only inside backticks (checked)
check:: md_angle_brackets_backtick_only

A literal `<` or `>` may appear **only** inside an inline code span or a fenced code block. Everywhere else — prose, tables, headings — it must be backticked (`` `<NAME>` ``) or HTML-escaped (`&lt;` / `&gt;`). This tightens R-md-01: the whitespace-padded form `< x >` is **no longer** acceptable, because it still renders as a stray bracket and several renderers still try to parse it as a tag.

**Sanctioned exceptions** (the checker drops these before scanning): the masthead line-break `<br>` (and `<br/>` / `<br />`), which the CAB breadcrumb dispatch-table cell embeds; and the leading `>` of a Markdown blockquote or Obsidian callout (`> text`, `> [!info] …`, nested `> >`) — that `>` is structural, not a content angle bracket (only the *leading* marker is exempt; a stray `<`/`>` inside the quoted text still fails).

**Why:** raw angle brackets outside code silently become (broken) HTML in Obsidian + CommonMark — a `<NAME>` placeholder vanishes from the rendered view with no error. Forcing backticks makes every such token both render-safe and visibly code.

**Check pattern:** `md_angle_brackets_backtick_only` — mask fenced code blocks and inline code spans, drop sanctioned `<br>` variants, then assert no `<` or `>` survives.
