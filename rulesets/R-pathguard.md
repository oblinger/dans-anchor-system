# RULESET R-pathguard
include::
description:: Veto-path protection for state-managed file regions (F131) — deny the agent's Edit/Write on surfaces owned by a script (`state task`, `state q`, `/atlas`, the queries renderer) and redirect to the owning tool. Fires at `tool:pre:*` through the live dispatcher; adopt via the `pathguard` trait.

> [!info] Provenance
> The first consumer of the F131 veto path (per [[F131 — Hooks — fast inner-loop check substrate (path-rule alerts first)|F131]] — realized on the Warden substrate rather than a separate hook binary). User direct edits are unaffected: the rules fire only on the agent's tool calls. A denied call carries the redirect message, so the agent lands on the owning script instead.

### RULE R-pathguard-01 — backlog and queries files are script-owned on Edit (when:: tool:pre:Edit)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    from pathlib import Path
    name = Path(target).name
    if name.endswith(" Backlog.md"):
        return ["DENY: " + name + " is owned by `state task` (create | update | delete) — "
                "never Edit backlog rows directly (~/.claude/skills/workflow/scripts/state)."]
    if name.endswith(" queries.md"):
        return ["DENY: " + name + " is mechanically rendered by queries-render.py — "
                "edit the backlog rows / feature-doc Open Questions it renders from, not the page."]
    return []
```

The backlog and queries pages are projections of `state`-managed rows; a direct Edit silently diverges them from the state the scripts maintain (and the next render clobbers it).

**Why:** per [[SKA workflow]] mutation discipline and the standing feedback rule — never hand-edit backlog/Q surfaces; `state` refreshes Q.md as part of the write.

### RULE R-pathguard-02 — feature-doc question regions are `state q`-owned (when:: tool:pre:Edit)

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
    hit = any(h in old or h in new for h in heads)
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
            "`state q` (add | answer | remove | rewrite) — do not Edit the region directly."]
```

Matches an Edit that names either heading or whose `old_string` sits inside the heading's section (between it and the next H2).

**Why:** the F130 lesson — Q blocks edited by hand bypass the block-ID / numbering / lifecycle discipline `state q` enforces.

### RULE R-pathguard-03 — script-owned files are protected wholesale on Write (when:: tool:pre:Write)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    from pathlib import Path
    name = Path(target).name
    if name.endswith(" Backlog.md") or name.endswith(" queries.md"):
        return ["DENY: " + name + " is script-owned (`state task` / queries-render.py) — "
                "a wholesale Write bypasses the same discipline Edit is denied for."]
    return []
```

The Write-tool bypass of rule 01: overwriting the whole file is the same violation at larger blast radius.

**Why:** closing the loophole structurally (per the round-trip-loophole feedback rule) — guarding Edit alone just teaches the failure mode a new verb.

### RULE R-pathguard-04 — Atlas is `/atlas`-owned (when:: tool:pre:Edit)

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
                "direct writes break its alphabetical-order and ATL Slugs.md-sync disciplines."]
    return []
```

**Why:** the vault has ONE Atlas and one maintenance path (per the one-Atlas feedback rule); a hand edit silently breaks the slug-sync invariants the skill enforces.
