# RULESET R-pathguard
include::
description:: Veto-path protection for state-managed file regions (F131) — deny the agent's Edit/Write on surfaces owned by a script (`state`, `/atlas`, the queries renderer) and redirect to the owning tool. Fires at `tool:pre:*` through the live dispatcher. Rides the anchor base — fires vault-wide (F264, 2026-07-18; formerly opt-in via the `pathguard` trait, which no anchor adopted, so the DENY never fired — only the softer [[R-state-region]] advisory rode the base). The two are twins on the same surfaces: this one blocks the edit, the advisory only reminds.

> [!info] Provenance
> The first consumer of the F131 veto path (per [[F131 — Hooks — fast inner-loop check substrate (path-rule alerts first)|F131]] — realized on the Warden substrate rather than a separate hook binary). User direct edits are unaffected: the rules fire only on the agent's tool calls. A denied call carries the redirect message, so the agent lands on the owning script instead.

### RULE R-pathguard-01 — backlog and queries files are script-owned on Edit (when:: tool:pre:Edit)
mend:: state-owns-the-edit

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    from pathlib import Path
    name = Path(target).name
    if name.endswith(" Backlog.md"):
        return ["DENY: " + name + " is owned by `state Backlog <F<n>|T<n>|F+|T+> "
                "<define|set|resolve|remove>` — never Edit backlog rows directly "
                "(~/.claude/skills/workflow/scripts/state)."]
    if name.endswith(" queries.md") or name == "Q.md":
        return ["DENY: " + name + " is mechanically rendered by queries-render.py — "
                "edit the backlog rows / feature-doc Open Questions it renders from, not the page."]
    return []
```

The backlog and queries pages are projections of `state`-managed rows; a direct Edit silently diverges them from the state the scripts maintain (and the next render clobbers it).

`Q.md` is matched by exact name, not by the `" queries.md"` suffix — the cross-anchor dashboard is called `Q.md` and matched neither suffix, so the one page the user actually reads was the only projection an agent could edit freely. Closed 2026-07-29.

**Why:** per [[SKA workflow]] mutation discipline and the standing feedback rule — never hand-edit backlog/Q surfaces; `state` refreshes Q.md as part of the write.

### RULE R-pathguard-02 — feature-doc question regions are `state`-owned (when:: tool:pre:Edit)
mend:: state-owns-the-edit

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    import re
    from pathlib import Path
    if not re.match(r"F\d+\s+—", Path(target).name):
        return []
    inp = getattr(ev, "input", None) or {}
    old = inp.get("old_string") or ""
    new = inp.get("new_string") or ""
    heads = ("## Open Questions", "## Resolved")
    # Location-based, NOT substring-based (T045 defect 2): fire only when the
    # edit touches a REAL managed heading LINE (`^## Open Questions$`) — prose
    # that merely quotes the heading string inline (e.g. a `## Recovery note`
    # that mentions the managed region) must pass.
    head_re = re.compile(r"^(?:" + "|".join(re.escape(h) for h in heads) + r")[ \t]*$", re.M)
    hit = bool(head_re.search(old) or head_re.search(new))
    if not hit and old:
        try:
            text = Path(target).read_text(encoding="utf-8")
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
            pass
    if not hit:
        return []
    return ["DENY: `## Open Questions` / `## Resolved` in a feature doc are owned by "
            "`state <doc> <Q<n>|Q+> <define|resolve|remove>` — do not Edit the region directly."]
```

Matches an Edit that touches either heading LINE or whose `old_string` sits inside the heading's section (between it and the next H2). It does **not** fire on prose that merely quotes the heading string inline — the T045 false positive that refused a `## Recovery note` edit for containing the managed headings as literal text.

**Why:** the F130 lesson — Q blocks edited by hand bypass the block-ID / numbering / lifecycle discipline `state q` enforces.

### RULE R-pathguard-03 — script-owned files are protected wholesale on Write (when:: tool:pre:Write)
mend:: state-owns-the-edit

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    from pathlib import Path
    name = Path(target).name
    if name.endswith(" Backlog.md") or name.endswith(" queries.md") or name == "Q.md":
        return ["DENY: " + name + " is script-owned (`state Backlog ...` / queries-render.py) — "
                "a wholesale Write bypasses the same discipline Edit is denied for."]
    return []
```

The Write-tool bypass of rule 01: overwriting the whole file is the same violation at larger blast radius.

**Why:** closing the loophole structurally (per the round-trip-loophole feedback rule) — guarding Edit alone just teaches the failure mode a new verb.

### RULE R-pathguard-04 — Atlas is `/atlas`-owned (when:: tool:pre:Edit)
mend:: atlas-owns-the-edit

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    from pathlib import Path
    p = Path(target)
    if p.name == "Atlas.md" and p.parent.name == "Atlas":
        return ["DENY: Atlas.md is owned by /atlas — use `/atlas add <name>` / `/atlas update <name>`; "
                "direct writes break its alphabetical-order and routing disciplines."]
    return []
```

**Why:** the vault has ONE Atlas and one maintenance path (per the one-Atlas feedback rule); a hand edit silently breaks the slug-sync invariants the skill enforces.

### RULE R-pathguard-05 — feature-doc question regions are `state`-owned on Write too (when:: tool:pre:Write)
mend:: state-owns-the-edit

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    import re
    from pathlib import Path
    p = Path(target)
    if not re.match(r"F\d+\s+—", p.name):
        return []
    # Doc creation is exempt — the /feature flow Writes a NEW doc's initial
    # Open Questions block. Fire only when the doc already exists on disk.
    if not p.is_file():
        return []
    inp = getattr(ev, "input", None) or {}
    content = inp.get("content") or ""

    # Region-diff, NOT a blunt "content mentions the heading" test (T045): a
    # whole-file Write that leaves the managed region byte-identical is a
    # legitimate prose rewrite and must pass; only a Write that CHANGES or
    # DROPS the region is the bypass (dropping it is exactly how Lumen F002
    # lost a pending Q2 + its resolved archive in 105094b4). A doc that merely
    # quotes the heading inline has no real region, so it never trips.
    def _regions(text):
        out = {}
        for m in re.finditer(r"^(## Open Questions|## Resolved)[ \t]*$", text, re.M):
            tail = text[m.end():]
            nxt = re.search(r"^## ", tail, re.M)
            out[m.group(1)] = tail[:nxt.start()] if nxt else tail
        return out

    try:
        on_disk = _regions(Path(target).read_text(encoding="utf-8"))
    except OSError:
        return []
    if not on_disk:            # nothing managed on disk → nothing to protect
        return []
    if _regions(content) == on_disk:   # region preserved verbatim → allow
        return []
    return ["DENY: `## Open Questions` / `## Resolved` in a feature doc are owned by "
            "`state <doc> <Q<n>|Q+> <define|resolve|remove>` — this Write changes or drops "
            "the managed region. Preserve it verbatim (rewrite prose only) and route question "
            "edits through `state`."]
```

The Write-tool sibling of rule 02: rule 02 denies the Edit path into an existing feature doc's question region, this one denies the whole-file Write path. Doc *creation* is exempt by construction — the rule fires only when the target already exists (`p.is_file()`), so the `/feature` flow authoring a new doc's initial `## Open Questions` block never triggers it (the same exemption R-state-region-02 uses). It compares the incoming managed region against the on-disk one (T045) and fires **only when they differ** — a whole-file Write that preserves the region verbatim (a legitimate prose rewrite) passes, while a Write that mutates or drops the region is denied. Blunt "content mentions the heading" would have blocked every prose rewrite and false-positived on docs that only quote the heading.

**Why:** guarding Edit alone just teaches the failure mode a new verb (the rule-03 lesson) — the whole reason rule 03 exists for the backlog surface. The feature-doc question region needs the identical Write cover so `state`'s ask-format / numbering / lifecycle gates can't be bypassed by overwriting the file.
