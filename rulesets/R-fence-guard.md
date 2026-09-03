# RULESET R-fence-guard
include::
confirm:: user
description:: a Write or Edit that puts a line wider than `fence_line_max` (global.yaml) inside a fenced code block is denied at `tool:pre`, line and length named — the veto behind [[R-markdown]]-17, which only reports after the bytes land

> [!info] Provenance
> Commissioned by Dan 2026-09-03 from the rendered `DAS Stone CLI` figure, every command of which soft-wrapped in Obsidian at 72–73 characters: *"forbid writing into markdown with word wrap inside of a text section… the simplest is just a hard fail if you try to write a document that word wraps, with a reminder that you can't word wrap inside of a backtick section."* Same relationship as [[R-stacked-guard]] to R-stacked-table-01 and [[R-dispatch-guard]] to R-dispatch-table-06: the doc-rule names the law, this ruleset blocks the act.
>
> **One definition of over-width, shared.** Both bodies call `audit-plan.fence_overwidth_lines(text)` — the exact function `chk_md_fence_width` reports from — via the daemon-resident `warden_docfire.ap` binding, and read the width from `fence_line_max` in ~/.config/anchor-system/global.yaml through `audit-plan.fence_max_width()` (Dan: widths are config, not constants). The deny and the audit therefore cannot disagree.
>
> **Deny only NEW over-width lines.** Each body compares the over-width fenced lines of the proposed text against those already in the file and denies only when a line appears that the file does not already carry. An edit elsewhere in a file that already holds a wrapped figure is never held hostage by it, and a file can be repaired one line at a time — the save-refusal-deadlocks-on-pre-existing-state gotcha, designed out. Every line the agent itself types is held, including a whole-file Write that reproduces an old long line verbatim (that line is in `before`, so it passes; a retyped longer variant is not).
>
> **Fail-open, everywhere.** Any error in a body returns no steer: a guard bug on this hot path must never block an unrelated write.

### RULE R-fence-guard-01 — a Write that adds an over-width fenced line is denied (when:: tool:pre:Write)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    fp = inp.get("file_path") or ""
    if not fp.lower().endswith((".md", ".markdown")):
        return []
    proposed = inp.get("content")
    if not isinstance(proposed, str) or ("```" not in proposed and "~~~" not in proposed):
        return []
    try:
        from pathlib import Path
        import warden_docfire as wdf
        wdf.refresh_audit_plan()
        ap = wdf.ap
        p = Path(fp)
        after = ap.fence_overwidth_lines(proposed)
        if not after:
            return []
        before_set = set()
        if p.is_file():
            before_set = {h[2] for h in ap.fence_overwidth_lines(p.read_text(encoding="utf-8"))}
        new = [h for h in after if h[2] not in before_set]
        if not new:
            return []  # every over-width line already exists in the file: not this write's doing
        anchor = next((d for d in [p.parent, *p.parent.parents]
                       if (d / ".anchor").is_file()), None)
        if anchor is not None:
            excs, _, _ = ap.load_exceptions(anchor)
            if excs and (ap._exception_for(excs, "R-markdown-17", p, anchor)
                         or ap._exception_for(excs, "R-fence-guard-01", p, anchor)):
                return []
        shown = "; ".join(f"line {ln} is {n} chars" for ln, n, _ in new[:3])
        return [f"DENY: {len(new)} line(s) inside a code fence exceed "
                f"{ap.fence_max_width()} characters — {shown}. A fenced line cannot "
                "word-wrap: Obsidian soft-wraps it at the pane edge and the "
                "figure's alignment is destroyed. Break the line, move the "
                "`# comment` to its own line above the command, or render a "
                "help figure as SVG per [[DAS CLI]]. Prose lines are free to be "
                "long; only fenced lines are held (R-markdown-17; Dan "
                "2026-09-03). Deliberate deviation → a graded row (A–C) in the "
                "anchor's `{slug} Exceptions.md`."]
    except Exception:
        return []  # fail-open: a guard bug must never block a write
```

Denies a `Write` whose content carries a fenced line over the width that the file on disk does not already hold. A new file with a narrow fence, a rewrite that only shortens lines, and content with no fence at all pass untouched.

### RULE R-fence-guard-02 — an Edit that adds an over-width fenced line is denied (when:: tool:pre:Edit)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    fp = inp.get("file_path") or ""
    if not fp.lower().endswith((".md", ".markdown")):
        return []
    old = inp.get("old_string") or ""
    new_s = inp.get("new_string") or ""
    if not old:
        return []
    try:
        from pathlib import Path
        p = Path(fp)
        if not p.is_file():
            return []
        text = p.read_text(encoding="utf-8")
        if "```" not in text and "~~~" not in text and "```" not in new_s and "~~~" not in new_s:
            return []
        if old not in text:
            return []  # the Edit tool will reject this call itself
        proposed = (text.replace(old, new_s) if inp.get("replace_all")
                    else text.replace(old, new_s, 1))
        import warden_docfire as wdf
        wdf.refresh_audit_plan()
        ap = wdf.ap
        after = ap.fence_overwidth_lines(proposed)
        if not after:
            return []
        before_set = {h[2] for h in ap.fence_overwidth_lines(text)}
        new = [h for h in after if h[2] not in before_set]
        if not new:
            return []  # every over-width line already exists in the file: not this write's doing
        anchor = next((d for d in [p.parent, *p.parent.parents]
                       if (d / ".anchor").is_file()), None)
        if anchor is not None:
            excs, _, _ = ap.load_exceptions(anchor)
            if excs and (ap._exception_for(excs, "R-markdown-17", p, anchor)
                         or ap._exception_for(excs, "R-fence-guard-02", p, anchor)):
                return []
        shown = "; ".join(f"line {ln} is {n} chars" for ln, n, _ in new[:3])
        return [f"DENY: {len(new)} line(s) inside a code fence exceed "
                f"{ap.fence_max_width()} characters — {shown}. A fenced line cannot "
                "word-wrap: Obsidian soft-wraps it at the pane edge and the "
                "figure's alignment is destroyed. Break the line, move the "
                "`# comment` to its own line above the command, or render a "
                "help figure as SVG per [[DAS CLI]]. Prose lines are free to be "
                "long; only fenced lines are held (R-markdown-17; Dan "
                "2026-09-03). Deliberate deviation → a graded row (A–C) in the "
                "anchor's `{slug} Exceptions.md`."]
    except Exception:
        return []  # fail-open: a guard bug must never block a write
```

Applies the Edit's replacement in memory and denies iff the RESULT carries a fenced line over the width that the current file does not already hold. Repairs, edits outside fences, and edits to a file with no fence all pass.
