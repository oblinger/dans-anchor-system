# RULESET R-dispatch-guard
include::
confirm:: user
description:: **SUSPENDED 2026-08-29 pending the spine→heart migration (TINK T623) — every body returns before judging.** The `tool:pre` veto twin of [[R-dispatch-table]]-06 — a Write/Edit (and, best-effort, a Bash heredoc) that would put more than 2 words in a row in a masthead RIGHT cell is **denied** before the bytes land, not advised after. Rides `anchor-base`. Touch means clean (ratchet removed 2026-08-22): any write that emits or changes a spine must leave the WHOLE spine legal, legacy cells included; only body-only Edits pass on a dirty doc.

> [!info] Provenance
> Commissioned by Dan 2026-08-22: *"let's just change the rule so that you cannot write a table with more than 2 words … ideally 0 words. But if modifiers are critical, you can add them, but it can't be more than two words. Let's just see what happens when the system is forced to do that."* The doc-rule flip (`warn`→`fail` on R-dispatch-table-06) the same day only produced a post-write advisory the writing agent could ignore — "cannot write" requires the F131 veto path (`tool:pre` + `DENY: `), which is this ruleset. Same relationship as [[R-pathguard]] (deny) to [[R-state-region]] (advisory): the doc-rule names the law, this ruleset blocks the act.
>
> **The criterion is a flat word-run cap, hardened 2026-08-22.** Dan, declining the F594 adaptive-tuning path for this rule: *"I was happy to just have a hard rule that says you can't write a spine that has more than 2 words in a row in it … it's just gonna be harsh on that point at this stage."* Links and code spans break a run and count zero; any third consecutive word — parenthesized or not — is a violation.
>
> **One definition of a violating cell, shared.** All three bodies call `audit-plan.masthead_narrative_offenders(text, stem)` — the exact function `chk_dispatch_cell_narrative` (the R-dispatch-table-06 checker) formats its verdict from — via the daemon-resident `warden_docfire.ap` binding, which `refresh_audit_plan()` keeps current. The deny and the audit can therefore never disagree about what a violation is.
>
> **Touch means clean — the ratchet is gone.** The original ship kept a ratchet (only a NEW offending cell denied) so the 361 legacy docs stayed editable. It lasted hours: Atticus added a clean links-only row to [[ATT]]'s spine while two illegal cells stood beside it, and the guard waved it through — Dan, same day: *"Atticus can edit his spine even though it's completely illegal. I don't understand how you can think this is fixed."* The rule now: **-01 Write** denies whenever the proposed bytes carry any offending cell (a Write emits the whole masthead — legacy prose rides along and is refused with it; body-only work belongs in Edit); **-02 Edit** denies when the result carries any offender AND the edit changed the masthead region — a body-only edit on a dirty doc still passes; **-03 Bash** (full-masthead writes only) denies on any offender, even a byte-identical re-emit. A dirty legacy doc is therefore body-editable via Edit, and its spine is cleanable — but its spine cannot be modified without being fully cleaned.
>
> **The escape is the exception table** ([[R-exception-discipline]], grades A–C suppress), consulted against `R-dispatch-table-06` first (the law being enforced) and this ruleset's own rule id second — a row that suppresses the audit also unlocks the write, one record for both surfaces.
>
> **Fail-open, everywhere.** Every body is wrapped so any error returns no steer: a guard bug on this hot path (15+ live sessions) must never block an unrelated write. The costs of that choice are the residues listed on -03.

### RULE R-dispatch-guard-01 — a Write proposing a narrative masthead cell is denied (when:: tool:pre:Write)

```python
def body(ctx):
    # SUSPENDED 2026-08-29 (Dan, TINK T623): the deny is destroying content — a
    # spine holding the page's own facts (the SV fact cards, person summaries)
    # has nowhere legal to put them until those pages have a heart. Re-arm by
    # deleting this return once the spine→heart migration ([[DAS heart]] § Fact
    # card) has run; R-dispatch-table-06 reads `warn` meanwhile.
    return []
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
        # NO ratchet (removed 2026-08-22, the ATT.md escape): a Write emits the
        # whole masthead, so legacy prose rides along in the proposed bytes and
        # is refused with it — touch means clean. Body-only work belongs in
        # the Edit tool, which passes when the spine region is untouched.
        new = after
        anchor = next((d for d in [p.parent, *p.parent.parents]
                       if (d / ".anchor").is_file()), None)
        if anchor is not None:
            excs, _, _ = ap.load_exceptions(anchor)
            if excs and (ap._exception_for(excs, "R-dispatch-table-06", p, anchor)
                         or ap._exception_for(excs, "R-dispatch-guard-01", p, anchor)):
                return []
        rows = "; ".join(f"{lbl} row: {right[:70]!r}" for lbl, right in new[:3])
        return ["DENY: this write emits a spine carrying more than 2 words in a "
                "row — " + rows + ". Touch means clean: every offending cell "
                "must be legal in the same write, legacy ones included "
                "(R-dispatch-table-06; Dan 2026-08-22: 'a hard rule that says you "
                "can't write a spine that has more than 2 words in a row'). "
                "Move each sentence to the destination page's own head/description "
                "or this doc's ## Overview (`warden mend R-dispatch-table-06`), "
                "then rewrite the rows as pure links — or use the Edit tool for "
                "body-only changes, which passes when the spine is untouched. "
                "Deliberate deviation → a graded row (A–C) in the anchor's "
                "`{slug} Exceptions.md`."]
    except Exception:
        return []  # fail-open: a guard bug must never block a write
```

Denies a `Write` whose proposed content carries a masthead right cell with prose that the file on disk does not already carry. A new file with a clean masthead, a rewrite that only removes prose, and any file without an identity cell all pass untouched.

**Why:** the post-write advisory arrives after the bytes land, addressed to an agent already past the moment of choice — measured 2026-08-22: eight days of the doc-rule at `warn` changed nothing, and the flip to `fail` still let the write stand. Only a refusal at `tool:pre` makes "cannot write" literally true.

### RULE R-dispatch-guard-02 — an Edit producing a narrative masthead cell is denied (when:: tool:pre:Edit)

```python
def body(ctx):
    # SUSPENDED 2026-08-29 (Dan, TINK T623): the deny is destroying content — a
    # spine holding the page's own facts (the SV fact cards, person summaries)
    # has nowhere legal to put them until those pages have a heart. Re-arm by
    # deleting this return once the spine→heart migration ([[DAS heart]] § Fact
    # card) has run; R-dispatch-table-06 reads `warn` meanwhile.
    return []
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
        # NO per-cell ratchet (removed 2026-08-22, the ATT.md escape: adding a
        # clean row beside two legacy-illegal cells sailed through). The gate
        # is now the masthead REGION: a body-only edit leaves the spine's rows
        # byte-identical and passes even on a dirty doc — the moment the edit
        # changes any spine row, the whole spine must come out legal.
        if ap._masthead_rows(proposed, p.stem) == ap._masthead_rows(text, p.stem):
            return []
        new = after
        anchor = next((d for d in [p.parent, *p.parent.parents]
                       if (d / ".anchor").is_file()), None)
        if anchor is not None:
            excs, _, _ = ap.load_exceptions(anchor)
            if excs and (ap._exception_for(excs, "R-dispatch-table-06", p, anchor)
                         or ap._exception_for(excs, "R-dispatch-guard-02", p, anchor)):
                return []
        rows = "; ".join(f"{lbl} row: {right[:70]!r}" for lbl, right in new[:3])
        return ["DENY: this edit touches a spine that carries more than 2 words "
                "in a row — " + rows + ". Touch means clean: an edit that "
                "changes any spine row must leave the WHOLE spine legal, legacy "
                "cells included (R-dispatch-table-06; Dan 2026-08-22: 'a hard "
                "rule that says you can't write a spine that has more than 2 "
                "words in a row'). Clean the offending cells in this same edit — "
                "move each sentence to the destination page's own head/description "
                "or this doc's ## Overview (`warden mend R-dispatch-table-06`) and "
                "leave pure links. Deliberate deviation → a graded row (A–C) in "
                "the anchor's `{slug} Exceptions.md`."]
    except Exception:
        return []  # fail-open: a guard bug must never block an edit
```

Applies the Edit's own `old_string → new_string` replacement to the current file in memory and denies iff the RESULT carries any offending cell AND the masthead region changed. Body-only edits pass on a dirty doc; any edit that changes a spine row — adding a clean one included — must leave the whole spine legal.

**Why:** same as -01; Edit is the tool that actually rewrote `OBS Setup.md`'s table three times on 2026-08-22 with zero pushback at the moment of writing.

### RULE R-dispatch-guard-03 — a Bash full-file markdown write with a narrative masthead cell is denied, best-effort (when:: tool:pre:Bash)

```python
def body(ctx):
    # SUSPENDED 2026-08-29 (Dan, TINK T623): the deny is destroying content — a
    # spine holding the page's own facts (the SV fact cards, person summaries)
    # has nowhere legal to put them until those pages have a heart. Re-arm by
    # deleting this return once the spine→heart migration ([[DAS heart]] § Fact
    # card) has run; R-dispatch-table-06 reads `warn` meanwhile.
    return []
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
            t = os.path.expanduser(os.path.expandvars(t))
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
            # NO ratchet (removed 2026-08-22): this leg only sees full-masthead
            # writes, and writing the whole spine while any cell is illegal is
            # the violation itself — even a byte-identical re-emit of legacy
            # prose. Touch means clean.
            new = after
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
                    "cell of " + p.name + " — " + rows + ". A spine right cell "
                    "never carries more than 2 words in a row — links, code "
                    "spans, and <=2-word tags only (R-dispatch-table-06). "
                    "Move the sentence to the destination "
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

### RULE R-dispatch-guard-04 — an opaque Bash write aimed at a dirty spine is denied (when:: tool:pre:Bash)

```python
def body(ctx):
    # SUSPENDED 2026-08-29 (Dan, TINK T623): the deny is destroying content — a
    # spine holding the page's own facts (the SV fact cards, person summaries)
    # has nowhere legal to put them until those pages have a heart. Re-arm by
    # deleting this return once the spine→heart migration ([[DAS heart]] § Fact
    # card) has run; R-dispatch-table-06 reads `warn` meanwhile.
    return []
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    if ".md" not in cmd:
        return []
    # Judge the write MECHANISM on the command with quoted spans blanked, so
    # prose naming a path or an arrow is not read as shell (T605). Two shapes
    # were denying pure reads: `2>&1` -- the commonest suffix in the corpus --
    # matched a bare `">" in cmd` even though duplicating a file descriptor
    # writes no file at all, and `" cp "` matched those letters inside a
    # `state drop` body. Reproduced 2026-08-28: `grep -c foo <page>` passed and
    # the same command with `2>&1` denied.
    # Sanctioned generators (state, md-toc, audit-dispatch, queries-render)
    # pass naturally — their command lines name a script, not a write call.
    try:
        import warden_fire as _wf
        ops = _wf.mask_quoted(cmd)
        writes = bool(_wf.REDIRECT_RE.search(ops) or _wf.MOVE_COPY_RE.search(ops))
    except Exception:
        ops, writes = cmd, (">" in cmd)      # deny-side conservative
    inds = ("write_text(", ".write(", "writelines", "sed -i", "perl -i",
            "tee ", "shutil.", "os.rename", "os.replace")
    if not writes and not any(i in ops for i in inds):
        return []
    try:
        from pathlib import Path
        import os
        import re
        # Quoted spans are scanned ANYWHERE in the command — not only at
        # whitespace boundaries — because the escape this rule closes names
        # its target as pathlib.Path('OBS Setup.md'): a greedy \S+ token walk
        # eats straight through those quotes and never sees the filename.
        cands = []
        for pat in (r"'([^']+\.(?:md|markdown))'",
                    r'"([^"]+\.(?:md|markdown))"'):
            for t in re.findall(pat, cmd, re.I):
                if t not in cands:
                    cands.append(t)
        for t in re.findall(r"(\S+)", cmd):
            t = t.strip("<>|;&()`,:='\"")
            if t.lower().endswith((".md", ".markdown")) and t not in cands:
                cands.append(t)
        if not cands:
            return []
        import warden_docfire as wdf
        wdf.refresh_audit_plan()
        ap = wdf.ap
        sess = getattr(getattr(ctx, "agent", None), "_session", None) or {}
        sess_cwd = sess.get("cwd") or ""
        # Follow `cd` inside the command (the R-ob-commons lesson, 7882d729):
        # the escape's real shape is `cd '<dir>'; python3 - <<PY ...
        # Path('OBS Setup.md')` — relative to the cd target, NOT the session
        # cwd, and resolving against the session cwd finds nothing and
        # fail-opens. Best-effort: the LAST cd before the write wins.
        eff_cwd = sess_cwd
        cds = re.findall(r"(?:^|[;&|]|&&|\|\|)\s*cd\s+(?:'([^']+)'"
                         r"|\"([^\"]+)\"|([^\s;&|]+))", cmd)
        if cds:
            a, b, c = cds[-1]
            # expandvars first (R-ob-commons 7882d729's other half): the
            # live escape wrote `cd "$HOME/ob/..."` — a literal $HOME that
            # expanduser alone never resolves.
            d = os.path.expanduser(os.path.expandvars(a or b or c))
            if not os.path.isabs(d) and eff_cwd:
                d = os.path.join(eff_cwd, d)
            if os.path.isdir(d):
                eff_cwd = d
        for t in cands:
            t = os.path.expanduser(os.path.expandvars(t))
            p = Path(t)
            if not p.is_absolute():
                # Try the cd-derived cwd first, then the session cwd.
                resolved = None
                for base in (eff_cwd, sess_cwd):
                    if base and (Path(base) / p).is_file():
                        resolved = Path(base) / p
                        break
                if resolved is None:
                    continue
                p = resolved
            if not p.is_file():
                continue
            try:
                disk = p.read_text(encoding="utf-8")
            except OSError:
                continue
            # Only spine-bearing pages, and only while the DISK spine is
            # already illegal. A write mechanism aimed at such a page cannot
            # be inspected pre-hoc (the content is computed at run time), so
            # while the spine is dirty the opaque channel is closed entirely.
            offenders = ap.masthead_narrative_offenders(disk, p.stem)
            if not offenders:
                continue
            # A genuinely read-only naming of the file beside an unrelated
            # redirect is the accepted false-positive cost; the deny message
            # names the clean escape (Edit/Write) in one line.
            anchor = next((d for d in [p.parent, *p.parent.parents]
                           if (d / ".anchor").is_file()), None)
            if anchor is not None:
                excs, _, _ = ap.load_exceptions(anchor)
                if excs and (ap._exception_for(excs, "R-dispatch-table-06", p, anchor)
                             or ap._exception_for(excs, "R-dispatch-guard-04", p, anchor)):
                    continue
            rows = "; ".join(f"{lbl} row: {right[:60]!r}"
                             for lbl, right in offenders[:2])
            return ["DENY: " + p.name + " carries an ILLEGAL spine (more than 2 "
                    "words in a row — " + rows + "), and this command writes it "
                    "through a channel the guard cannot inspect (inline python / "
                    "sed -i / redirect / mv). While the spine is dirty, opaque "
                    "writes to the page are refused outright — this is the exact "
                    "channel Atticus used to keep editing an illegal spine on "
                    "2026-08-22. Clean the spine FIRST via the Edit tool (move "
                    "each sentence to the destination page's own head/description "
                    "or this doc's ## Overview — `warden mend R-dispatch-table-06` "
                    "— leaving pure links), then the page is writable again. "
                    "Deliberate deviation → a graded row (A–C) in the anchor's "
                    "`{slug} Exceptions.md`."]
        return []
    except Exception:
        return []  # fail-open: a guard bug must never block a command
```

The closing of the measured escape: -03 inspects a command's *payload* and therefore only sees full-masthead heredocs, so a `python3 - <<'PY'` that reads the file, rearranges lines, and `write_text`s the result was invisible — and that is precisely how Atticus reordered [[OBS Setup]]'s spine four times on 2026-08-22 while its `Related` row stood illegal (transcript `d375418e`, 19:58:48 among others; zero warden events, because the pre-hook had nothing to test and the file field of a Bash event is empty). This rule does not try to compute the result; it refuses the *channel*: a command that names a spine-bearing `.md` whose ON-DISK masthead is already illegal, and that carries a raw write mechanism (`write_text` / `.write(` / `sed -i` / `perl -i` / `tee` / redirect / `mv`/`cp` onto it), is denied until the spine is cleaned through an inspectable tool. A clean spine reopens the opaque channel (sanctioned generators and ordinary scripting keep working); re-dirtying through it is the stated remaining residue, caught post-hoc by the F297 doc-fire and re-frozen at the next touch.

**Why:** Dan, on finding the escape: *"I don't care what happened. I care that it's still not fixed … I would like you to try to reorder the spine in this document and find yourself blocked for it."* The acceptance test for this rule is exactly that — an Edit-tool reorder of a dirty spine is refused by -02, and the python-heredoc replay of Atticus's own command shape is refused here.
