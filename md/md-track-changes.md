# Track Changes

Present edits to markdown text as visible tracked changes in a standalone HTML document. The HTML uses `<del>` for deletions, `<ins>` for additions, and comment divs to explain each change.


## HTML Format

Every track changes document uses this structure:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{TITLE} - Track Changes</title>
  <style>
    body { font-family: Georgia, serif; max-width: 850px; margin: 40px auto; padding: 20px; line-height: 1.7; color: #333; }
    h1, h2, h3 { color: #1a1a1a; }
    del { background-color: #fdd; color: #900; text-decoration: line-through; }
    ins { background-color: #dfd; color: #060; text-decoration: none; }
    .comment { background-color: #fffde7; border-left: 3px solid #ffc107; padding: 10px 14px; margin: 12px 0; font-size: 0.9em; color: #555; }
    .comment::before { content: "💬 "; }
    .legend { background: #f5f5f5; padding: 12px 15px; border-radius: 5px; margin-bottom: 20px; font-size: 0.9em; }
  </style>
</head>
<body>
<h1>{TITLE}</h1>
<p><strong>Base:</strong> {old version} → <strong>Target:</strong> {new version}</p>
<div class="legend">
  <del>Deleted</del> | <ins>Added</ins> | <span class="comment" style="display:inline; margin:0; padding:2px 8px;">Comment</span>
</div>
<hr>

<!-- Body: original text with inline <del>/<ins> markup and .comment divs -->

</body>
</html>
```

### Rules
- **Deletions**: `<del>` — red background, strikethrough
- **Insertions**: `<ins>` — green background, no underline
- **Comments**: `.comment` divs after each change or group, explaining the reasoning
- **Formatting**: render markdown as HTML (bold, italic, lists, headings) — the reader sees formatted prose, not raw markdown
- **Granularity**: mark changes at the word/phrase level, not whole paragraphs
- **Placement**: HTML file lives in the same folder as the markdown source


## Workflow 1: Inline Edit Review

The user provides markdown text and asks for changes (tighten, restructure, simplify, etc.). Produce three outputs:

1. The **original text** — unchanged markdown, preserved as-is
2. A **track changes HTML** — the diff rendered using the format above
3. A **revised text** — new markdown with all changes applied, preceded by a link to the HTML:

```markdown
**Track changes**: [[{NAME} track-changes.html|view changes]]

(revised text follows...)
```

Place the HTML in the same folder as the markdown file. If no folder context, use the current working directory.


## Workflow 2: Versioned Paper Flow

For long documents edited across multiple revision cycles. The document's anchor page maintains a **version table**:

```markdown
| Version            | Markup                                            | Notes         |
| ------------------ | ------------------------------------------------- | ------------- |
| [[ABP 2026-01-15]] | [[ABIO s1.html|s1]]✓ [[ABIO s2.html|s2]]✓ ...    | section index |
| [[ABP 2025-07-08]] | (original)                                        |               |
```

- **Left column** — wiki-link to that version's full markdown text
- **Middle column** — links to per-section track changes HTML files
- **Right column** — section index or notes

### Process
1. The latest version is always the **top row**
2. Track changes are split by **section** — one HTML file per section
3. Each section HTML shows `Base: {old version} → Target: {new version}`
4. Checkmarks (✓) are added as the user reviews and accepts/rejects changes for each section
5. After all sections are reviewed, accepted changes produce a new version
6. The new version gets a new row at the top; the cycle repeats

### Section HTML Naming
```
{RID} {DATE} s{N}.html
```
Example: `ABIO 2026-01-15 s1.html`, `ABIO 2026-01-15 s2.html`

Section HTML files live alongside the markdown versions in the same folder.
