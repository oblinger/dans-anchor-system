---
name: heading-spacing
severity: warning
---

# Heading spacing

ATX headings (`#`, `##`, `###`, …) should have a blank line **before** them. Many markdown renderers tolerate a missing blank, but its absence defeats outline navigation in Obsidian and breaks the visual scan pattern of the file.

Exception: a heading on line 1 (with no preceding content) and a heading immediately after frontmatter (lines `---` … `---`) don't need a blank line before — the document or frontmatter terminator implicitly separates them.

## There is no blank-line-**after** check, and there will not be one

Retired 2026-08-11 by Dan's answer to [[Tink Backlog#^T537|T537]] Q1: *"for number two, let's just lean A. We might change that later, but for now, A is good."* His standing instruction (2026-04-28, held as a durable agent memory) is that **a heading followed by prose, a list, or a table takes its content on the very next line** — no blank between them. This rule's blank-after half enforced the exact opposite, so every heading written the way he asked for earned a warning, and `audit-markdown` is Stop-hook wired (F081 Q3), so it fired in normal use.

**The count at retirement was 19,245**, and it had already survived one narrowing that failed to reach the cause. On 2026-08-11 [[Atticus|Atticus]] reported that `R-spine`'s `S05` and this rule demanded opposite things about the H1's orientation line — `spine fix` deletes the blank the rule then asks for — so an H1-followed-by-prose exception was added, taking 22,146 → 19,245. That exception was written up as *"a tight `##` against its body text is ordinary crowding and the rule should keep saying so"*, which contradicts the standing instruction and was calibrated against Atticus's finding count rather than against the standard. The residual was never leftover scope; it was the same contradiction one heading level down, which is why the fix is a deletion rather than a third narrowing.

**The corpus did not settle it and was not allowed to.** Measured across every markdown file in the vault: 22,456 headings are tight and 43,074 carry a blank — 66% against the stated preference, unevenly by level (H2 15% tight, H3 43%, H4 67%, H1 42%). Pointing the rule at the majority would have made the user's own house style the finding set. Option (B) — inverting the rule to *require* tight — was available and was not taken: it would have converted 43,074 conforming-by-accident headings into findings and forced a migration nobody asked for. **The rule now permits both shapes and polices neither.** The blank-*before* check is untouched: nothing in the preference concerns the line above a heading, and a heading glued to the previous paragraph is a genuine outline defect.

Do not re-add a blank-after check, in either direction, without a new answer from Dan on T205. The `S05` / `spine fix` contradiction the H1 exception existed to resolve is resolved a fortiori — the check it contradicted no longer exists.

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
        # Blank-BEFORE only. The blank-after check was deleted 2026-08-11 (T205
        # Q1 answer (A)) because it enforced the opposite of the user's stated
        # heading style, 19,245 times. Do not restore it; see the section above.
        if i > 0 and i != fm_end + 1:
            if lines[i - 1].strip() != "":
                findings.append({
                    "line": i + 1,
                    "message": f"heading needs blank line before: {line[:60].rstrip()}",
                })
    return findings
```
