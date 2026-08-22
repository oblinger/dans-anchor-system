# RULESET R-dispatch-guard
include::
description:: The `tool:pre` veto twin of [[R-dispatch-table]]-06 — a Write/Edit (and, best-effort, a Bash heredoc) that would put narrative prose in a masthead RIGHT cell is **denied** before the bytes land, not advised after. Rides `anchor-base`. Ratcheted: only a NEW offending cell denies, so the 1,374-cell legacy corpus stays editable and cleanable.

> [!info] Provenance
> Commissioned by Dan 2026-08-22: *"let's just change the rule so that you cannot write a table with more than 2 words … ideally 0 words. But if modifiers are critical, you can add them, but it can't be more than two words. Let's just see what happens when the system is forced to do that."* The doc-rule flip (`warn`→`fail` on R-dispatch-table-06) the same day only produced a post-write advisory the writing agent could ignore — "cannot write" requires the F131 veto path (`tool:pre` + `DENY: `), which is this ruleset. Same relationship as [[R-pathguard]] (deny) to [[R-state-region]] (advisory): the doc-rule names the law, this ruleset blocks the act.
>
> **One definition of "narrative cell", shared.** All three bodies call `audit-plan.masthead_narrative_offenders(text, stem)` — the exact function `chk_dispatch_cell_narrative` (the R-dispatch-table-06 checker) formats its verdict from — via the daemon-resident `warden_docfire.ap` binding, which `refresh_audit_plan()` keeps current. The deny and the audit can therefore never disagree about what a violation is.
>
> **The ratchet.** Deny only when the PROPOSED content contains an offending `(left label, right cell)` pair the CURRENT file does not. An edit elsewhere in a legacy-violating doc passes; deleting or trimming prose passes; only introducing (or rewording — a reword is a fresh chance to obey) a prose cell is refused. Without this, every one of the 361 legacy docs would be frozen — uneditable AND uncleanable.
>
> **The escape is the exception table** ([[R-exception-discipline]], grades A–C suppress), consulted against `R-dispatch-table-06` first (the law being enforced) and this ruleset's own rule id second — a row that suppresses the audit also unlocks the write, one record for both surfaces.
>
> **Fail-open, everywhere.** Every body is wrapped so any error returns no steer: a guard bug on this hot path (15+ live sessions) must never block an unrelated write. The costs of that choice are the residues listed on -03.

### RULE R-dispatch-guard-01 — a Write proposing a narrative masthead cell is denied (when:: tool:pre:Write)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    fp = inp.get("file_path") or ""
    if not fp.lower().endswith((".md", ".markdown")):
        return []
    proposed = inp.get("content")
    # Cheap gate: no identity cell, no masthead, no fire.
    if not isinstance(proposed, str) or "-[[" not in proposed:
        return []
    try:
        from pathlib import Path
        import warden_docfire as wdf
        wdf.refresh_audit_plan()
        ap = wdf.ap
        p = Path(fp)
        after = ap.masthead_narrative_offenders(proposed, p.stem)
        if not after:
            return []
        before = []
        if p.is_file():
            try:
                before = ap.masthead_narrative_offenders(
                    p.read_text(encoding="utf-8"), p.stem)
            except OSError:
                before = []
        new = [o for o in after if o not in before]
        if not new:
            return []  # ratchet: no NEW offense — legacy docs stay editable
        anchor = next((d for d in [p.parent, *p.parent.parents]
                       if (d / ".anchor").is_file()), None)
        if anchor is not None:
            excs, _, _ = ap.load_exceptions(anchor)
            if excs and (ap._exception_for(excs, "R-dispatch-table-06", p, anchor)
                         or ap._exception_for(excs, "R-dispatch-guard-01", p, anchor)):
                return []
        rows = "; ".join(f"{lbl} row: {right[:70]!r}" for lbl, right in new[:3])
        return ["DENY: this write puts prose in a dispatch-table RIGHT cell — "
                + rows + ". A masthead right cell is links plus at most a 2-word "
                "parenthetical (R-dispatch-table-06; Dan 2026-08-22: 'you cannot "
                "write a table with more than 2 words'). Move the sentence to the "
                "destination page's own head/description or this doc's ## Overview "
                "(`warden mend R-dispatch-table-06`), then rewrite the row as pure "
                "links. Deliberate deviation → a graded row (A–C) in the anchor's "
                "`{slug} Exceptions.md`."]
    except Exception:
        return []  # fail-open: a guard bug must never block a write
```

Denies a `Write` whose proposed content carries a masthead right cell with prose that the file on disk does not already carry. A new file with a clean masthead, a rewrite that only removes prose, and any file without an identity cell all pass untouched.

**Why:** the post-write advisory arrives after the bytes land, addressed to an agent already past the moment of choice — measured 2026-08-22: eight days of the doc-rule at `warn` changed nothing, and the flip to `fail` still let the write stand. Only a refusal at `tool:pre` makes "cannot write" literally true.

### RULE R-dispatch-guard-02 — an Edit producing a narrative masthead cell is denied (when:: tool:pre:Edit)

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
        # Cheap gate: masthead identity cell in neither the file nor the
        # insertion → this edit cannot mint a masthead cell.
        if "-[[" not in text and "-[[" not in new_s:
            return []
        if old not in text:
            return []  # the Edit tool will reject this call itself
        proposed = (text.replace(old, new_s) if inp.get("replace_all")
                    else text.replace(old, new_s, 1))
        import warden_docfire as wdf
        wdf.refresh_audit_plan()
        ap = wdf.ap
        after = ap.masthead_narrative_offenders(proposed, p.stem)
        if not after:
            return []
        before = ap.masthead_narrative_offenders(text, p.stem)
        new = [o for o in after if o not in before]
        if not new:
            return []  # ratchet: untouched legacy prose never blocks the edit
        anchor = next((d for d in [p.parent, *p.parent.parents]
                       if (d / ".anchor").is_file()), None)
        if anchor is not None:
            excs, _, _ = ap.load_exceptions(anchor)
            if excs and (ap._exception_for(excs, "R-dispatch-table-06", p, anchor)
                         or ap._exception_for(excs, "R-dispatch-guard-02", p, anchor)):
                return []
        rows = "; ".join(f"{lbl} row: {right[:70]!r}" for lbl, right in new[:3])
        return ["DENY: this edit puts prose in a dispatch-table RIGHT cell — "
                + rows + ". A masthead right cell is links plus at most a 2-word "
                "parenthetical (R-dispatch-table-06; Dan 2026-08-22: 'you cannot "
                "write a table with more than 2 words'). Move the sentence to the "
                "destination page's own head/description or this doc's ## Overview "
                "(`warden mend R-dispatch-table-06`), then rewrite the row as pure "
                "links. Deliberate deviation → a graded row (A–C) in the anchor's "
                "`{slug} Exceptions.md`."]
    except Exception:
        return []  # fail-open: a guard bug must never block an edit
```

Applies the Edit's own `old_string → new_string` replacement to the current file in memory and denies iff the RESULT carries a masthead-prose cell the current file does not. The comparison is against the whole-file outcome, so an edit that merely moves existing prose rows around without adding one passes, and an edit that rewords a prose cell is denied — a reword is a fresh chance to obey the rule.

**Why:** same as -01; Edit is the tool that actually rewrote `OBS Setup.md`'s table three times on 2026-08-22 with zero pushback at the moment of writing.

### RULE R-dispatch-guard-03 — a Bash full-file markdown write with a narrative masthead cell is denied, best-effort (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    # Cheap gates: a command that names no .md file, or carries no masthead
    # identity cell in its payload, cannot be a masthead write we can see.
    if ".md" not in cmd or "-[[" not in cmd or "|" not in cmd:
        return []
    try:
        from pathlib import Path
        import os
        import re
        # .md target tokens, quoted-aware (vault paths carry spaces).
        toks = re.findall(r"'([^']+)'|\"([^\"]+)\"|(\S+)", cmd)
        cands = []
        for a, b, c in toks:
            t = (a or b or c).strip("<>|;&()`,:=")
            if t.lower().endswith((".md", ".markdown")) and t not in cands:
                cands.append(t)
        if not cands:
            return []
        import warden_docfire as wdf
        wdf.refresh_audit_plan()
        ap = wdf.ap
        # The session's cwd, for relative targets. os.getcwd() would be the
        # DAEMON's cwd (the ATT T183 lesson: daemon-process state is never the
        # caller's); the event's session mapping carries the right one.
        sess = getattr(getattr(ctx, "agent", None), "_session", None) or {}
        sess_cwd = sess.get("cwd") or ""
        for t in cands:
            if t.startswith("~/"):
                t = os.path.expanduser(t)
            p = Path(t)
            if not p.is_absolute():
                if not sess_cwd:
                    continue  # cannot resolve a relative target — leave it to
                              # the post-hoc doc-fire rather than guess
                p = Path(sess_cwd) / p
            stem = p.stem
            # Only a payload carrying THIS file's own identity cell is testable
            # — i.e. a full-masthead write (heredoc / echo of a whole table).
            if f"-[[{stem}" not in cmd and f"-[[ {stem}" not in cmd:
                continue
            after = ap.masthead_narrative_offenders(cmd, stem)
            if not after:
                continue
            before = []
            if p.is_file():
                try:
                    before = ap.masthead_narrative_offenders(
                        p.read_text(encoding="utf-8"), stem)
                except OSError:
                    before = []
            new = [o for o in after if o not in before]
            if not new:
                continue
            base = p.parent  # p is absolute by here (relative targets skipped)
            anchor = next((d for d in [base, *base.parents]
                           if (d / ".anchor").is_file()), None)
            if anchor is not None:
                excs, _, _ = ap.load_exceptions(anchor)
                if excs and (ap._exception_for(excs, "R-dispatch-table-06", p, anchor)
                             or ap._exception_for(excs, "R-dispatch-guard-03", p, anchor)):
                    continue
            rows = "; ".join(f"{lbl} row: {right[:70]!r}" for lbl, right in new[:3])
            return ["DENY: this command writes prose into a dispatch-table RIGHT "
                    "cell of " + p.name + " — " + rows + ". A masthead right cell "
                    "is links plus at most a 2-word parenthetical "
                    "(R-dispatch-table-06). Move the sentence to the destination "
                    "page's own head/description or the doc's ## Overview "
                    "(`warden mend R-dispatch-table-06`), then write the row as "
                    "pure links — and prefer the Edit/Write tools over shell "
                    "redirection for markdown. Deliberate deviation → a graded "
                    "row (A–C) in the anchor's `{slug} Exceptions.md`."]
        return []
    except Exception:
        return []  # fail-open: a guard bug must never block a command
```

Best-effort by construction — the command string is all a Bash pre-hook has. **What it catches:** a heredoc or quoted-payload command whose text contains the target file's own identity cell (`-[[stem…]]-`) plus offending rows — the full-masthead rewrite, which is the form the measured misses actually took. **Stated residue, deliberately accepted:** (1) a script that *computes* the content (`python3 gen.py`) is invisible pre-hoc — it is caught post-hoc by the F297 leg-3 doc-fire steer instead; (2) a `sed -i`/append of a single row without the identity cell in the command falls through to the same post-hoc steer; (3) a `<<-`-style tab-indented heredoc misses the line-anchored row regex. Tightening any of these means denying commands whose effect cannot be seen, which fails the fail-open bar.

**Why:** without this leg, "cannot write" would be true of the polite tools only — and the same day's measurement showed one agent at 768 Bash calls against 10 Edit/Write.
