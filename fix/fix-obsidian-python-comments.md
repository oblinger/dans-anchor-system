# Fix: Python Comments in Obsidian Code Blocks

Obsidian's folding engine treats `#` at line start inside code blocks as markdown headers, breaking the fold structure of the document.

## Runbook

### 1. Identify the problem

When a markdown file in Obsidian has Python code blocks with `#` comments, the heading outline gets polluted with fake headings from inside the code block. Folding becomes unpredictable.

### 2. Apply the fix

Replace standard `#` with Unicode fullwidth number sign `＃` (U+FF03) for Python comments inside code blocks:

```python
def activate(entity):
    ＃ Check energy threshold before activation
    if entity.energy > MIN_ENERGY:
        entity.state = "active"
```

### 3. Scope

This only applies to:
- Python comments inside fenced code blocks in **Obsidian markdown files**
- It does NOT apply to actual `.py` source files
- It does NOT apply to markdown rendered outside Obsidian

## Why This Happens

Obsidian's markdown parser does not fully isolate code blocks from its heading detection. Any line starting with `#` inside a code fence is treated as a heading candidate for folding purposes.
