# RULESET R-stone-guard
include::
confirm:: user
description:: a Write or Edit that puts a stone line over `stone_line_max` (global.yaml) into a stone file's `line::` or a control file is denied at `tool:pre`, line and rendered length named — the veto behind [[R-stone]]-13, which only reports after the bytes land

> [!info] Provenance
> Commissioned by Dan 2026-09-03 from `Atticus P0004`, whose line rendered at 104 characters on a list with a budget of 84: *"the agent did a word wrap… it should just reject if the agent tries to create a stone whose title line is gonna cause a word wrap."* `stone new` already refuses; the hole was every other write path. Same relationship as [[R-fence-guard]] to R-markdown-17: the doc-rule names the law, this ruleset blocks the act.
>
> **One measure, shared.** Both bodies call `audit-plan.stone_overbudget_lines(text)` — the function `chk_stone_line_budget` reports from — and the budget is `stone_line_max` in ~/.config/anchor-system/global.yaml, the same key `stone new` reads. Widths are config, never constants (Dan, same day).
>
> **Deny only NEW over-budget lines.** A file that already holds one stays editable elsewhere and can be repaired one line at a time.
>
> **Fail-open, everywhere.**

### RULE R-stone-guard-01 — a Write that adds an over-budget stone line is denied (when:: tool:pre:Write)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    fp = inp.get("file_path") or ""
    if not fp.lower().endswith((".md", ".markdown")):
        return []
    proposed = inp.get("content")
    if not isinstance(proposed, str) or ("line::" not in proposed and "|-]]" not in proposed):
        return []
    try:
        from pathlib import Path
        import warden_docfire as wdf
        wdf.refresh_audit_plan()
        ap = wdf.ap
        p = Path(fp)
        after = ap.stone_overbudget_lines(proposed)
        if not after:
            return []
        before_set = set()
        if p.is_file():
            before_set = {h[2] for h in ap.stone_overbudget_lines(p.read_text(encoding="utf-8"))}
        new = [h for h in after if h[2] not in before_set]
        if not new:
            return []
        anchor = next((d for d in [p.parent, *p.parent.parents]
                       if (d / ".anchor").is_file()), None)
        if anchor is not None:
            excs, _, _ = ap.load_exceptions(anchor)
            if excs and (ap._exception_for(excs, "R-stone-13", p, anchor)
                         or ap._exception_for(excs, "R-stone-guard-01", p, anchor)):
                return []
        shown = "; ".join(f"line {ln} renders at {n}" for ln, n, _ in new[:3])
        return [f"DENY: {len(new)} stone line(s) render over the {ap.stone_line_max()}-"
                f"character budget — {shown}. A stone's line must fit on ONE line "
                "of the reading view (`stone_line_max` in global.yaml); a longer one "
                "word-wraps and the list is unreadable. Shorten the line; the "
                "detail belongs in the stone's body. Measured as Obsidian shows it: "
                "`- ` plus the text with links collapsed to their alias (R-stone-13; "
                "Dan 2026-08-30 / 2026-09-03). Deliberate deviation → a graded row "
                "(A–C) in the anchor's `{slug} Exceptions.md`."]
    except Exception:
        return []  # fail-open: a guard bug must never block a write
```

Denies a `Write` whose content carries a stone line over the budget that the file on disk does not already hold.

### RULE R-stone-guard-02 — an Edit that adds an over-budget stone line is denied (when:: tool:pre:Edit)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    fp = inp.get("file_path") or ""
    if not fp.lower().endswith((".md", ".markdown")):
        return []
    old = inp.get("old_string") or ""
    new_s = inp.get("new_string") or ""
    if not old or ("line::" not in new_s and "|-]]" not in new_s):
        return []
    try:
        from pathlib import Path
        p = Path(fp)
        if not p.is_file():
            return []
        text = p.read_text(encoding="utf-8")
        if old not in text:
            return []
        proposed = (text.replace(old, new_s) if inp.get("replace_all")
                    else text.replace(old, new_s, 1))
        import warden_docfire as wdf
        wdf.refresh_audit_plan()
        ap = wdf.ap
        after = ap.stone_overbudget_lines(proposed)
        if not after:
            return []
        before_set = {h[2] for h in ap.stone_overbudget_lines(text)}
        new = [h for h in after if h[2] not in before_set]
        if not new:
            return []
        anchor = next((d for d in [p.parent, *p.parent.parents]
                       if (d / ".anchor").is_file()), None)
        if anchor is not None:
            excs, _, _ = ap.load_exceptions(anchor)
            if excs and (ap._exception_for(excs, "R-stone-13", p, anchor)
                         or ap._exception_for(excs, "R-stone-guard-02", p, anchor)):
                return []
        shown = "; ".join(f"line {ln} renders at {n}" for ln, n, _ in new[:3])
        return [f"DENY: {len(new)} stone line(s) render over the {ap.stone_line_max()}-"
                f"character budget — {shown}. A stone's line must fit on ONE line "
                "of the reading view (`stone_line_max` in global.yaml); a longer one "
                "word-wraps and the list is unreadable. Shorten the line; the "
                "detail belongs in the stone's body. Measured as Obsidian shows it: "
                "`- ` plus the text with links collapsed to their alias (R-stone-13; "
                "Dan 2026-08-30 / 2026-09-03). Deliberate deviation → a graded row "
                "(A–C) in the anchor's `{slug} Exceptions.md`."]
    except Exception:
        return []  # fail-open: a guard bug must never block a write
```

Applies the Edit in memory and denies iff the RESULT carries a stone line over the budget that the current file does not already hold.
