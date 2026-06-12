---
name: final-newline
severity: warning
---

# Missing final newline

Markdown files should end with a single `\n`. POSIX defines a "line" as ending with a newline; files missing the trailing newline confuse `cat`, `wc -l`, and naive text processors. Most editors auto-add it; if it's missing, a non-conforming editor touched the file.

```python
def check(file_path):
    try:
        # Read raw bytes to preserve the final character exactly
        data = file_path.read_bytes()
    except OSError:
        return []
    if not data:
        return []  # empty file: vacuous pass
    if data[-1:] != b"\n":
        # Compute the line number of the last line for the report
        line_count = data.count(b"\n") + 1
        return [{
            "line": line_count,
            "message": "file does not end with newline",
        }]
    return []
```
