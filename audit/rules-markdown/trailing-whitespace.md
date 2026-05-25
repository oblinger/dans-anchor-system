---
name: trailing-whitespace
severity: warning
---

# Trailing whitespace

Lines should not have trailing spaces or tabs. Editors strip them automatically; their presence usually means a hand-edit was made by a tool that didn't normalize, or a paste went sideways.

```python
TRAILING_RE = re.compile(r"[ \t]+$")


def check(file_path):
    findings = []
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return findings
    for line_num, line in enumerate(text.splitlines(), start=1):
        if TRAILING_RE.search(line):
            findings.append({
                "line": line_num,
                "message": f"trailing whitespace ({len(line) - len(line.rstrip())} chars)",
            })
    return findings
```
