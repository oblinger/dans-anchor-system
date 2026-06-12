---
name: heading-spacing
severity: warning
---

# Heading spacing

ATX headings (`#`, `##`, `###`, …) should have a blank line both **before** and **after**. Many markdown renderers tolerate missing blanks, but the lack of them defeats outline navigation in Obsidian and breaks the visual scan pattern of the file.

Exception: a heading on line 1 (with no preceding content) and a heading immediately after frontmatter (lines `---` … `---`) don't need a blank line *before* — the document or frontmatter terminator implicitly separates them.

```python
HEADING_RE = re.compile(r"^#{1,6}\s+\S")


def check(file_path):
    findings = []
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return findings
    # Detect end of frontmatter (if any): the second `---` line
    fm_end = -1
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm_end = i
                break
    for i, line in enumerate(lines):
        if not HEADING_RE.match(line):
            continue
        # Check blank-before (skip if line 0 or immediately after frontmatter end)
        if i > 0 and i != fm_end + 1:
            if lines[i - 1].strip() != "":
                findings.append({
                    "line": i + 1,
                    "message": f"heading needs blank line before: {line[:60].rstrip()}",
                })
        # Check blank-after (skip if last line of file)
        if i < len(lines) - 1:
            if lines[i + 1].strip() != "":
                findings.append({
                    "line": i + 1,
                    "message": f"heading needs blank line after: {line[:60].rstrip()}",
                })
    return findings
```
