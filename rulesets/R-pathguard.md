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
    p = Path(target)
    name = p.name
    if name.endswith(" Backlog.md"):
        # A backlog STORE, not merely a file whose name ends in " Backlog.md".
        # Two independent signals, either one sufficient: the `state:backlog`
        # stamp `state` writes into every store it manages, and the canonical
        # `{slug} Track/` home. They agree on all 42 vault instances; the OR
        # keeps a store guarded when one signal is missing.
        in_track = p.parent.name.endswith(" Track")
        stamped = False
        try:
            stamped = "state:backlog" in p.read_text(errors="replace")[:800]
        except OSError:
            stamped = True   # unreadable — guard rather than wave through
        if in_track or stamped:
            # Scoped to ROW writes (2026-08-28, reported by Presti on SVAR
            # Backlog): `state` owns the rows and the H2s, and has no verb for
            # the prose outside them — the R-spine-02 orientation line under the
            # stamp above all. An Edit that touches no bullet and no heading in
            # either its old or its new text is that prose, and passes. A Write
            # (no old/new strings) still denies: it replaces rows wholesale.
            inp = getattr(ev, "input", None) or {}
            if "old_string" in inp or "new_string" in inp:
                import re
                touched = (inp.get("old_string") or "") + "\n" + (inp.get("new_string") or "")
                if not re.search(r"^[ \t]*(?:[-*+] |#{1,6} )", touched, re.M):
                    return []
            return ["DENY: " + name + " is owned by `state <define|set|resolve|remove> "
                    "<anchor> Backlog <label>` — never Edit backlog rows directly "
                    "(~/.claude/skills/workflow/scripts/state). Prose outside the "
                    "rows and headings (the orientation line under the stamp) is "
                    "yours: an Edit touching no bullet and no heading passes."]
    if name.endswith(" queries.md") or name == "Q.md":
        return ["DENY: " + name + " is mechanically rendered by queries-render.py — "
                "edit the backlog rows / feature-doc Open Questions it renders from, not the page."]
    return []
```

The backlog and queries pages are projections of `state`-managed rows; a direct Edit silently diverges them from the state the scripts maintain (and the next render clobbers it).

`Q.md` is matched by exact name, not by the `" queries.md"` suffix — the cross-anchor dashboard is called `Q.md` and matched neither suffix, so the one page the user actually reads was the only projection an agent could edit freely. Closed 2026-07-29.

**A backlog STORE is matched, not every file whose name ends in `" Backlog.md"`** *(narrowed 2026-08-07)*. The suffix alone caught six namesakes, and one of them was [[DAS Backlog]] — **the facet that defines the backlog format**, a prose document with no rows, unreachable through the very tool the DENY redirects to. `state` has no verb for editing a facet, so the guard made its own specification unmaintainable: the only way to correct the state table was to route around the rule entirely, which is the outcome a guard exists to prevent. The other five are the `exp` docs checklist and four Warden Corpus fixtures — specimens whose whole purpose is to be hand-authored.

Two signals decide it, and **either one is sufficient**: the `state:backlog` stamp that `state` writes into every store it manages, and the canonical `{slug} Track/` home. Measured across all 42 vault instances the two partition identically — 36 stores carry both, 6 namesakes carry neither — so the `or` is not a widening of the accept set but insurance: a store that loses its stamp is still guarded by its location, and a store living outside a Track folder is still guarded by its stamp. An unreadable file is guarded on the Edit path (the safe branch), and on the Write path the stamp is additionally sought in the content being written, since the file may not exist yet.

Both rules moved together. Narrowing `-01` alone would have taught the failure mode a new verb — the `-03` lesson, recorded below.

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
    # Three feature-doc filename forms, all permanent — older docs are never
    # renamed: `F<n> — Title.md` (legacy), `{slug} F<n> — Title.md` (F298),
    # `{SLUG}<n> - Title.md` (F300, current — no `F`, ASCII hyphen). Canonical
    # copy of this grammar lives at `backlog_edit.feature_number`; rule bodies
    # are exec'd in isolation and cannot import, so it is repeated here.
    if not re.match(r"(?:(?:[A-Za-z][A-Za-z0-9]*\s+)?F\d+\s+—|[A-Za-z]+\d+\s+-\s)",
                    Path(target).name):
        return []
    inp = getattr(ev, "input", None) or {}
    old = inp.get("old_string") or ""
    new = inp.get("new_string") or ""
    # `## Resolved` was here until F291 and is now [[R-state-region]]'s (warn).
    # F305: `## Open Items` is the canonical heading; `## Open Questions` is
    # the legacy spelling, accepted forever (the writer renames on touch).
    heads = ("## Open Items", "## Open Questions")
    # Location-based, NOT substring-based (T045 defect 2): fire only when the
    # edit touches a REAL managed heading LINE — prose
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
    return ["DENY: the open-items block (`## Open Items` / legacy `## Open Questions`) in a feature doc is owned by "
            "`state <define|set|resolve|remove> <anchor> <doc> <Q<n>|Q+>` — do not Edit the region directly."]
```

Matches an Edit that touches the heading LINE or whose `old_string` sits inside the heading's section (between it and the next H2). It does **not** fire on prose that merely quotes the heading string inline — the T045 false positive that refused a `## Recovery note` edit for containing the managed heading as literal text.

The scope is the **open block alone**. `## Resolved` was covered here until F291 and now carries only [[R-state-region]]'s advisory, on the rule *deny where desync is possible, detect where it is not*. Three facts make uniform machine-ownership of the resolved section incoherent: half of it (F068 auto-decisions) is written straight in as un-numbered H3s that no `state <verb> <anchor> <doc> Q<n>` call can ever address, so a blanket deny forbids the mechanism that populates it; there is no live state left to desynchronize once an entry is archived (it is not rendered, not counted, gates nothing); and the vault is committed continuously, so tamper-evidence already exists at the commit layer. Denying there bought prevention where evidence already existed, at the cost of making legitimate edits illegal — superseded-stamps, link repairs, hindsight added years later. It also produced the [[TINK Backlog#^T488|T488]] deadlock: a lint demanding a fix inside a region every write path forbade.

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
    p = Path(target)
    name = p.name
    if name.endswith(" queries.md") or name == "Q.md":
        return ["DENY: " + name + " is script-owned (`state <verb> <anchor> Backlog ...` / queries-render.py) — "
                "a wholesale Write bypasses the same discipline Edit is denied for."]
    if name.endswith(" Backlog.md"):
        # Same store-vs-namesake test as R-pathguard-01, with the third signal a
        # Write needs: the file may not exist yet, so the stamp is also looked
        # for in the content being written.
        in_track = p.parent.name.endswith(" Track")
        stamped = False
        try:
            stamped = "state:backlog" in p.read_text(errors="replace")[:800]
        except OSError:
            pass
        if not stamped:
            inp = getattr(ev, "input", None) or {}
            stamped = "state:backlog" in (inp.get("content") or "")[:800]
        if in_track or stamped:
            return ["DENY: " + name + " is script-owned (`state <verb> <anchor> Backlog ...`) — "
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
    # Legacy / F298 slug-prefixed / F300 fused — see R-pathguard-02.
    if not re.match(r"(?:(?:[A-Za-z][A-Za-z0-9]*\s+)?F\d+\s+—|[A-Za-z]+\d+\s+-\s)",
                    p.name):
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
        # Open block only since F291 — `## Resolved` is R-state-region's now.
        # F305: both spellings — `## Open Items` canonical, `## Open
        # Questions` legacy (the writer renames on touch).
        for m in re.finditer(r"^(## Open (?:Items|Questions))[ \t]*$", text, re.M):
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
    return ["DENY: the open-items block (`## Open Items` / legacy `## Open Questions`) in a feature doc is owned by "
            "`state <define|set|resolve|remove> <anchor> <doc> <Q<n>|Q+>` — this Write changes or drops "
            "the managed region. Preserve it verbatim (rewrite prose only) and route question "
            "edits through `state`."]
```

The Write-tool sibling of rule 02: rule 02 denies the Edit path into an existing feature doc's question region, this one denies the whole-file Write path. Doc *creation* is exempt by construction — the rule fires only when the target already exists (`p.is_file()`), so the `/feature` flow authoring a new doc's initial `## Open Questions` block never triggers it (the same exemption R-state-region-02 uses). It compares the incoming managed region against the on-disk one (T045) and fires **only when they differ** — a whole-file Write that preserves the region verbatim (a legitimate prose rewrite) passes, while a Write that mutates or drops the region is denied. Blunt "content mentions the heading" would have blocked every prose rewrite and false-positived on docs that only quote the heading.

**Why:** guarding Edit alone just teaches the failure mode a new verb (the rule-03 lesson) — the whole reason rule 03 exists for the backlog surface. The feature-doc question region needs the identical Write cover so `state`'s ask-format / numbering / lifecycle gates can't be bypassed by overwriting the file.
