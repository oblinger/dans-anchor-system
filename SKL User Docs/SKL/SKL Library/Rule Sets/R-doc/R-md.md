# RULESET R-md
description:: Markdown rules — files render correctly across CommonMark renderers, with attention to Obsidian-specific gotchas. Adopt when authoring any .md file.
includes::

### R-md-01 — Angle brackets need surrounding whitespace (checked)

Raw angle brackets in prose (`<word>`) get interpreted as HTML tag attempts and silently swallow content in Obsidian and several other renderers. Acceptable forms: `<verb>` inside backticks, `< verb >` with whitespace on both sides, or `&lt;verb&gt;` escaped.

**Why:** observed breakage in past docs where `<foo>` placeholders disappeared from the rendered view with no visible error.

**Check pattern:** grep for `\S<[A-Za-z_]` or `[A-Za-z_]>\S` outside code fences. Both are leading/trailing-whitespace-less angle brackets and fail.

### R-md-02 — Tables need blank lines before and after (checked)

Markdown tables (pipe syntax) require a blank line above the header row and a blank line below the last row. Without surrounding blank lines, the table parser merges the table into adjacent paragraphs and renders broken or as raw text.

**Why:** Obsidian's table parser (and CommonMark's table extension) require blank-line delimiters; without them, the pipe-syntax bleeds into surrounding prose.

**Check pattern:** for every table (line starting with `|` followed by another line starting with `|---`), verify the line immediately before the header is blank AND the line immediately after the table-end is blank.
