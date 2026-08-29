# RULESET R-code-mirror
include::
confirm:: user
description:: Two-Way Doc Mirror wrong-side-edit protection (F188, protection layer 3 of [[SKA Code-Docs Design]]) — deny the agent's Edit/Write on the repo-side copy of a mirrored doc route and redirect to the vault original. Routes come from the `mirror-routes.json` index that `code sync` regenerates from `.anchor` `mirror:` declarations. Rides the anchor base — fires vault-wide.

> [!info] Provenance
> Per [[SKA Code-Docs Design]] § Protection layers: the asymmetry rule quarantines wrong-side edits after the fact, the read-only stamp blocks shell writes, and this rule blocks the agent's tool writes *before* they land — the deny names the vault path to edit instead. `pull`-direction routes are exempt (the repo side is the source there). User direct edits are unaffected: rules fire only on the agent's tool calls.

### RULE R-code-mirror-01 — repo-side mirror copies are vault-owned on Edit (when:: tool:pre:Edit)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    import json
    from pathlib import Path
    idx = Path.home() / ".config/anchor-system/mirror-routes.json"
    if not idx.is_file():
        return []
    try:
        routes = json.loads(idx.read_text()).get("routes", [])
    except Exception:
        return []
    try:
        t = Path(target).resolve()
    except OSError:
        t = Path(target)
    for e in routes:
        if e.get("direction") == "pull":
            continue  # repo side is the source on pull routes
        there = Path(e.get("there", ""))
        if t == there or there in t.parents:
            return ["DENY: " + str(target) + " is the repo-side copy of a Two-Way "
                    "Doc Mirror route — edit the vault original under "
                    + e.get("here", "?") + " instead; `code sync` transports it "
                    "(mirror declared in " + e.get("anchor", "?") + ")."]
    return []
```

The repo working-tree copy is a sync artifact: a direct edit there is quarantined by the asymmetry rule at the next sync and never reaches the vault — the work would be silently stranded.

**Why:** per the Two-Way Doc Mirror design, all authoring happens on the vault side; the deny lands the agent on the editable original instead of a copy whose edits die in quarantine.

### RULE R-code-mirror-02 — repo-side mirror copies are vault-owned on Write (when:: tool:pre:Write)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    import json
    from pathlib import Path
    idx = Path.home() / ".config/anchor-system/mirror-routes.json"
    if not idx.is_file():
        return []
    try:
        routes = json.loads(idx.read_text()).get("routes", [])
    except Exception:
        return []
    try:
        t = Path(target).resolve()
    except OSError:
        t = Path(target)
    for e in routes:
        if e.get("direction") == "pull":
            continue
        there = Path(e.get("there", ""))
        if t == there or there in t.parents:
            return ["DENY: " + str(target) + " sits inside a Two-Way Doc Mirror's "
                    "repo-side route — create/overwrite the file under "
                    + e.get("here", "?") + " in the vault instead; `code sync` "
                    "transports it (mirror declared in " + e.get("anchor", "?") + ")."]
    return []
```

The Write-tool bypass of rule 01: new files created on the repo side are equally stranded — the mirror's forward pass never saw them in the vault, and the backward pass quarantines them as uncommitted dirt.

**Why:** closing the loophole structurally (the R-pathguard-03 lesson) — guarding Edit alone just teaches the failure mode a new verb.
