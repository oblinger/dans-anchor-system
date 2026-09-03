# RULESET R-stacked-guard
include::
confirm:: user
description:: a Write or Edit that leaves a `[=]`-declared stacked table WORSE than it found it is denied at `tool:pre`, with row, column and cell named — the veto behind [[R-stacked-table]]-01, which only reports after the bytes land

> [!info] Provenance
> Commissioned by Dan 2026-09-01 on [[DAS stacked-table]], relayed by Atticus: the checked rule shipped and tested that day reports per-cell violations through audit-on-write, a steer the writing agent can ignore; the intended end state is stronger — *"the thing won't even let it write."* Same relationship as [[R-dispatch-guard]] (deny) to R-dispatch-table-06 (advisory): the doc-rule names the law, this ruleset blocks the act. Tracked as [[Tink650 - Warden denies a Write or Edit that produces a nonconforming stacked table|TINK F650]].
>
> **One definition of a violation, shared.** Both bodies call `audit-plan.stacked_table_problems(text)` — the exact function `chk_stacked_table` formats its verdict from — via the daemon-resident `warden_docfire.ap` binding, which `refresh_audit_plan()` keeps current. The deny and the audit can therefore never disagree about what a violation is.
>
> **Deny only on INCREASE.** Each body counts violations in the file's current text and in the proposed text and denies only when the count rises. A partially broken table can be repaired one cell at a time, and an edit elsewhere in a file that carries a broken table is never held hostage by it — the save-refusal-deadlocks-on-pre-existing-state gotcha, designed out rather than discovered. This is deliberately NOT R-dispatch-guard's touch-means-clean: a dispatch masthead is rewritten whole, a stacked table is edited by the cell.
>
> **The escape is the exception table** ([[R-exception-discipline]], grades A–C suppress), consulted against `R-stacked-table-01` first (the law being enforced) and then against this ruleset's own rule id.
>
> **Fail-open, everywhere.** Every body is wrapped so any error returns no steer: a guard bug on this hot path must never block an unrelated write.

### RULE R-stacked-guard-01 — a Write that raises a stacked table's violation count is denied (when:: tool:pre:Write)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    fp = inp.get("file_path") or ""
    if not fp.lower().endswith((".md", ".markdown")):
        return []
    proposed = inp.get("content")
    # Cheap gate: no corner marker, no stacked table, no fire.
    if not isinstance(proposed, str) or "[=]" not in proposed:
        return []
    try:
        from pathlib import Path
        import warden_docfire as wdf
        wdf.refresh_audit_plan()
        ap = wdf.ap
        p = Path(fp)
        after = ap.stacked_table_problems(proposed)
        if not after:
            return []
        before = ap.stacked_table_problems(p.read_text(encoding="utf-8")) if p.is_file() else []
        if len(after) <= len(before):
            return []  # repair or no-worse: a broken table stays editable
        anchor = next((d for d in [p.parent, *p.parent.parents]
                       if (d / ".anchor").is_file()), None)
        if anchor is not None:
            excs, _, _ = ap.load_exceptions(anchor)
            if excs and (ap._exception_for(excs, "R-stacked-table-01", p, anchor)
                         or ap._exception_for(excs, "R-stacked-guard-01", p, anchor)):
                return []
        new = [x for x in after if x not in before] or after
        return ["DENY: this write leaves a `[=]` stacked table with more violations than "
                f"the file has now ({len(before)} → {len(after)}) — " + "; ".join(new[:3])
                + ". The corner cell draws the stack and its line count is the arity for "
                "every cell; a missing sub-value is an em-dash, never empty; `[=]` belongs "
                "only in the header's corner (R-stacked-table-01; Dan 2026-09-01: 'the "
                "thing won't even let it write'). Fix the named cells in this same write. "
                "See [[DAS stacked-table]]. Deliberate deviation → a graded row (A–C) in "
                "the anchor's `{slug} Exceptions.md`."]
    except Exception:
        return []  # fail-open: a guard bug must never block a write
```

Denies a `Write` whose proposed content carries more stacked-table violations than the file on disk already does. A new file with a clean table, a rewrite that repairs cells, and any content without a `[=]` corner all pass untouched.

**Why:** the post-write advisory arrives after the bytes land, addressed to an agent already past the moment of choice; a wrong arity shears sub-values into the wrong sub-row and the corruption renders plausibly, so it is read as the wrong value off the wrong line. Only a refusal at `tool:pre` makes "cannot write" literally true.

### RULE R-stacked-guard-02 — an Edit that raises a stacked table's violation count is denied (when:: tool:pre:Edit)

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
        # Cheap gate: no corner marker in the file or the insertion → this
        # edit cannot touch a stacked table.
        if "[=]" not in text and "[=]" not in new_s:
            return []
        if old not in text:
            return []  # the Edit tool will reject this call itself
        proposed = (text.replace(old, new_s) if inp.get("replace_all")
                    else text.replace(old, new_s, 1))
        import warden_docfire as wdf
        wdf.refresh_audit_plan()
        ap = wdf.ap
        after = ap.stacked_table_problems(proposed)
        if not after:
            return []
        before = ap.stacked_table_problems(text)
        if len(after) <= len(before):
            return []  # repair or no-worse: a broken table stays editable
        anchor = next((d for d in [p.parent, *p.parent.parents]
                       if (d / ".anchor").is_file()), None)
        if anchor is not None:
            excs, _, _ = ap.load_exceptions(anchor)
            if excs and (ap._exception_for(excs, "R-stacked-table-01", p, anchor)
                         or ap._exception_for(excs, "R-stacked-guard-02", p, anchor)):
                return []
        new = [x for x in after if x not in before] or after
        return ["DENY: this edit leaves a `[=]` stacked table with more violations than "
                f"the file has now ({len(before)} → {len(after)}) — " + "; ".join(new[:3])
                + ". The corner cell draws the stack and its line count is the arity for "
                "every cell; a missing sub-value is an em-dash, never empty; `[=]` belongs "
                "only in the header's corner (R-stacked-table-01; Dan 2026-09-01: 'the "
                "thing won't even let it write'). Fix the named cells in this same edit. "
                "See [[DAS stacked-table]]. Deliberate deviation → a graded row (A–C) in "
                "the anchor's `{slug} Exceptions.md`."]
    except Exception:
        return []  # fail-open: a guard bug must never block an edit
```

Applies the Edit's own `old_string → new_string` replacement to the current file in memory and denies iff the RESULT carries more stacked-table violations than the file does now. Repairs, edits outside the table, and edits to a file with no `[=]` corner all pass.

**Why:** same as -01; Edit is the tool that writes a table cell by cell, which is exactly where a sub-value count drifts.
