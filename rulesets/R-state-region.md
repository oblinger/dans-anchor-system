# RULESET R-state-region
include::
description:: The F236 advisory on state-managed doc regions — an agent Edit/Write touching `## Open Questions` / `## Resolved` / `## Status` on an existing doc that carries labeled items (Q/V bullets, resolved `### Q<n>` H3s) gets the use-`state` reminder; the edit stands. Rides the anchor base (adopted 2026-07-13, F236 M3) — fires vault-wide. Doc creation is exempt; the backlog / queries / feature-doc surfaces keep their harder [[R-pathguard]] DENY rules.

> [!info] Provenance
> Per [[F236 — state v2 — one address scheme — state doc label verb for rows, questions, and verifications|F236]] § Warden reminder rule (Q3 = advisory): warden's hook sees exactly the writes `state` doesn't make (agent hand-edits), so the two enforcement paths cover each other's blind side — `state`-side integrity via audit-q on every mutation, hand-edit-side via this advisory.

### RULE R-state-region-01 — state-managed regions of item-bearing docs get the `state` reminder on Edit (when:: tool:pre:Edit)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    import re
    from pathlib import Path
    p = Path(target)
    name = p.name
    if not name.endswith(".md"):
        return []
    # Surfaces owned by harder R-pathguard DENY rules are not re-advised here.
    if name.endswith(" Backlog.md") or name.endswith(" queries.md") \
            or re.match(r"F\d+\s+—", name):
        return []
    inp = getattr(ev, "input", None) or {}
    old = inp.get("old_string") or ""
    new = inp.get("new_string") or ""
    heads = ("## Open Questions", "## Resolved", "## Status")
    hit = any(h in old or h in new for h in heads)
    text = None
    if not hit and old:
        try:
            text = p.read_text(encoding="utf-8")
            for h in heads:
                m = re.search(r"^" + re.escape(h) + r"\s*$", text, re.M)
                if not m:
                    continue
                tail = text[m.end():]
                nxt = re.search(r"^## ", tail, re.M)
                if old in (tail[:nxt.start()] if nxt else tail):
                    hit = True
                    break
        except OSError:
            return []
    if not hit:
        return []
    if text is None:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            return []
    if not re.search(r"^\s*- \*\*[A-Z]+\d+ —|^### Q\d+\b", text, re.M):
        return []
    return ["state-managed region — `## Open Questions` / `## Resolved` / `## Status` on a "
            "doc carrying labeled items are maintained by `state <doc> <label> <verb>` "
            "(define | set | resolve | remove); prefer it over a direct edit so the doc, "
            "backlog, queries.md, and Q.md stay locked together."]
```

Fires only on an *existing* doc that already carries labeled items (`- **Q7 — …**` / `- **V3 — …**` bullets or resolved `### Q<n>` H3s), reminds, and lets the edit stand. Region detection matches an Edit that names one of the headings or whose `old_string` sits inside a heading's section (between it and the next H2).

**Why:** habit-drift catch without breaking legitimate authoring flows — the long tail of docs `state` can now address (PRDs, design docs, anything with Q/V items), where a hand edit silently skips the atomic propagation chain.

### RULE R-state-region-02 — same reminder on Write to an existing item-bearing doc (when:: tool:pre:Write)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    import re
    from pathlib import Path
    p = Path(target)
    name = p.name
    if not name.endswith(".md") or not p.is_file():
        return []
    if name.endswith(" Backlog.md") or name.endswith(" queries.md") \
            or re.match(r"F\d+\s+—", name):
        return []
    inp = getattr(ev, "input", None) or {}
    content = inp.get("content") or ""
    heads = ("## Open Questions", "## Resolved", "## Status")
    if not any(h in content for h in heads):
        return []
    if not re.search(r"^\s*- \*\*[A-Z]+\d+ —|^### Q\d+\b", content, re.M):
        return []
    return ["state-managed region — `## Open Questions` / `## Resolved` / `## Status` on a "
            "doc carrying labeled items are maintained by `state <doc> <label> <verb>` "
            "(define | set | resolve | remove); prefer it over a wholesale Write so the doc, "
            "backlog, queries.md, and Q.md stay locked together."]
```

The Write-tool sibling of rule 01. Doc *creation* is exempt by construction — the rule fires only when the target already exists on disk (`p.is_file()`), so authoring a new doc's initial `## Open Questions` block by hand (the `/feature` flow) never triggers it.

**Why:** guarding Edit alone just teaches the failure mode a new verb (the [[R-pathguard]]-03 lesson), and the advisory has to see the same blind side on both mutation tools.

### RULE R-state-region-03 — Open Questions integrity stamp must hash-match on write (when:: write:markdown)

```python
def body(ctx):
    # NB: the compiler marks a rule file-bearing (and the engine binds
    # ctx.file) only when the source contains a literal `file.` reference —
    # keep the direct ctx.file.* accesses below (F215).
    if getattr(ctx, "file", None) is None:
        return []
    if not ctx.file.name.endswith(".md") or not ctx.file.exists:
        return []
    import hashlib, re
    stamp_re = re.compile(r"^<!--\s*state:q\s+([0-9a-z]{2})\s*-->$")
    lines = ctx.file.lines
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "## Open Questions":
            start = i
            break
    if start is None:
        return []
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## ") or (lines[j].startswith("# ")
                                          and not lines[j].startswith("## ")):
            end = j
            break
    stored = None
    for k in range(start + 1, end):
        m = stamp_re.match(lines[k].strip())
        if m:
            stored = m.group(1)
            break
    if stored is None:
        return []  # grandfathered — stampless legacy block
    content = [ln.rstrip() for ln in lines[start:end]
               if not stamp_re.match(ln.strip())]
    digest = hashlib.sha1("\n".join(content).encode("utf-8")).hexdigest()
    n = int(digest, 16) % 1296
    b36 = "0123456789abcdefghijklmnopqrstuvwxyz"
    computed = b36[n // 36] + b36[n % 36]
    if computed == stored:
        return []
    return [f"`## Open Questions` integrity stamp mismatch (stored `{stored}`, "
            f"computed `{computed}`) — this block is maintained by "
            "`state <doc> <label> <verb>`; a hand-edit bypasses its ask-format "
            "gates. Re-issue the change through `state`, or run "
            "`state \"<doc>\" revalidate` to validate-then-restamp (F241)."]
```

The F241 tamper-evidence check. The state script re-stamps the block (a 2-char base-36 sha1 of the trailing-whitespace-normalized block text, heading through the next H2, stamp line excluded) on every write it makes — so a stamp that doesn't match means the block content changed through some other write path. The audit twin over backlog-linked docs is audit-q **C48**; recovery is `state <doc> revalidate` (validate-then-stamp — every pending Q re-runs the same ask-format gates as `Q+ define`; there is deliberately no blind re-bless flag). Hash algorithm mirrors `backlog-edit.py`'s `compute_q_stamp` — rule bodies are sandboxed standalone, so the four-line algorithm is inlined here; if it ever changes, change both.

**Why:** the point is not verifying the questions — it is making the script (whose write path enforces ask-format) the only quiet route to a green block. Rules 01/02 remind on the way in; this one catches what slipped through, including writes warden never saw as tool events.
