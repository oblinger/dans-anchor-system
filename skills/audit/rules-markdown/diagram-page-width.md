---
name: diagram-page-width
severity: warning
---

# Diagram embeds must carry a page-fill width hint

A diagram embedded with no width hint — bare `![[figure.svg]]` — renders in Obsidian as a tiny fit-to-column thumbnail, not the page-wide figure that is the default requirement for architecture and module diagrams (see [[FCT Architecture]] § Architecture diagram requirements and [[DSC markdown]]). The fix is a large width hint the reading pane caps to itself, e.g. `![[figure.svg|2400]]`.

This rule flags **bare** image embeds (`.svg` / `.png` / `.excalidraw`) that carry no `|<width>`. An embed that *does* carry a width — page-fill (`|2400`) or a deliberately small inline width (`|400`) — is the author's explicit choice and passes: the rule enforces "make a sizing decision," not a specific number. Embeds inside fenced code blocks (skill templates / examples) are skipped.

```python
EMBED_RE = re.compile(r"!\[\[[^\]|]*\.(?:svg|png|excalidraw)\]\]", re.IGNORECASE)
# Build the backtick fence marker via chr() so this rule's own fence isn't cut short.
TRIPLE_BACKTICK = chr(96) * 3


def check(file_path):
    findings = []
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return findings
    in_fence = False
    for line_num, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith(TRIPLE_BACKTICK) or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in EMBED_RE.finditer(line):
            findings.append({
                "line": line_num,
                "message": (
                    f"diagram embed {m.group(0)} has no width hint — renders as a tiny "
                    f"thumbnail; add a page-fill width like |2400 (or a small width for "
                    f"an explicit inline figure)"
                ),
            })
    return findings
```
