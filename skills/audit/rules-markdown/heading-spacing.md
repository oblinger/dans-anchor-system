---
name: heading-spacing
severity: warning
---

# Heading spacing

ATX headings (`#`, `##`, `###`, …) should have a blank line both **before** and **after**. Many markdown renderers tolerate missing blanks, but the lack of them defeats outline navigation in Obsidian and breaks the visual scan pattern of the file.

Exception: a heading on line 1 (with no preceding content) and a heading immediately after frontmatter (lines `---` … `---`) don't need a blank line *before* — the document or frontmatter terminator implicitly separates them.

Exception: **an H1 followed directly by its orientation line** doesn't need a blank line *after*. [[DAS spine]] requires exactly that shape — *H1 → one sentence → heart, with no blank line between the H1 and the sentence, so the heart lands on screen without scrolling* — and `R-spine`'s `S05` reports the blank line as the defect, while `spine fix` actively deletes it. Without this exception the two checkers demand opposite things about the same line, and running `spine fix` is what *creates* this rule's warning: **1,787 pages** vault-wide carry the mandated shape and each earned one false finding. Since `audit-markdown` is Stop-hook wired (F081 Q3), that warning fired in normal use on pages that had just become correct — which trains agents to discount the checker. Reported by [[ATT|Atticus]] 2026-08-11 from the `Topic/MGR/Hire` spine pass; fixed the same day.

Scoped to **level-1 headings followed by prose**, deliberately, and to nothing wider. Two narrowings were measured rather than assumed:

- **Prose, not any follower.** A first cut exempted an H1 followed by anything non-heading and suppressed 3,254 findings against the ~1,787 the discipline mandates; the extra ~1,467 were H1s jammed against a table, list, fence or quote, which the spine promises nothing about. Narrowed to the same `_prose` predicate `chk_orientation_line` uses, so the two agree by construction.
- **`##` and deeper still report.** A tight `##` against its body text is ordinary crowding and the rule should keep saying so — verified on `## Why this is a slot facet` in [[DAS spine]], which still fires.

Measured effect: **22,146 → 19,245** `blank line after` findings vault-wide. That is ~2,901 rather than the 1,787 Atticus counted, and the gap is honest scope: the exception keys on *a* level-1 heading, not on *the head* H1, so a `# BRIEF` or `# Log` that opens a body section with prose is exempted too. Locating the head would mean reaching for the `_head_h1` primitive, which a standalone rule body cannot import. Left as-is: those are body-section heads whose following line is prose, which is the same shape for the same reason.

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
        # Check blank-after (skip if last line of file, or if this is an H1
        # followed directly by its orientation line — the shape [[DAS spine]]
        # mandates and `spine fix` produces. Without this the two checkers
        # contradict each other on 1,787 pages and conforming to one guarantees
        # a finding from the other. H1 only: the promise is about the head.)
        # PROSE only, matching `chk_orientation_line`'s own predicate. A first
        # cut skipped any non-heading follower and suppressed 3,254 findings
        # against the 1,787 the discipline actually mandates — the extra 1,467
        # were H1s jammed against a table, list, fence or quote, which the spine
        # promises nothing about and which is ordinary crowding.
        # NB: the fence marker is built with chr(96) rather than written out,
        # and must NEVER be written out even inside a comment. This rule's body
        # lives inside a fenced block, so a literal triple-backtick anywhere in
        # it closes the fence early. Both failure modes were hit while writing
        # this exception: cut mid-statement it fails to compile and the runner
        # drops to 3 rules; cut after the last append it still compiles, loses
        # `return findings`, returns None, and reports ZERO findings vault-wide
        # while looking perfectly healthy. The second is the dangerous one.
        NOT_PROSE = ("|", "#", "- ", "* ", "+ ", ">", "![", chr(96) * 3, ":>>")
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        is_head_orientation = (
            line.startswith("# ") and bool(nxt) and not nxt.startswith(NOT_PROSE)
        )
        if i < len(lines) - 1 and not is_head_orientation:
            if lines[i + 1].strip() != "":
                findings.append({
                    "line": i + 1,
                    "message": f"heading needs blank line after: {line[:60].rstrip()}",
                })
    return findings
```
