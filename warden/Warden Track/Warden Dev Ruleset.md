---
description: "R-warden-dev — the first REAL Warden rule fired live (F220 dogfood): orients any agent working in the Warden anchor to its dev disciplines"
---

# [[Warden]] · Warden Dev Ruleset

The **first real Warden rule** fired live in the system (the [[F220 — Live hook install + kill switch|F220]] dogfood — moving past the steer-only pilot to a genuinely-useful rule). Keyed by the `warden-dev` trait, which the Warden anchor (`warden/.anchor`) adopts, so it fires for any agent that starts a session inside the Warden tree — orienting it to the anchor's dev disciplines before it touches anything. It is a **steer, never a deny** (non-blocking), and `warden off` disables it (and all of Warden) instantly, everywhere.

This is Warden auditing its own workflow with its own engine: the discipline it enforces is exactly the one the Warden dev loop must follow.

# RULESET R-warden-dev
description:: dev-discipline orientation for the Warden anchor

### RULE R-warden-dev-01 — orient on session start (when:: session:start)
when:: session:start

```python
def body(ctx):
    return (
        "[warden] You are in the Warden anchor. Dev disciplines here: "
        "(1) Commit mode — commit at logical boundaries without asking, never amend, "
        "pathspec-limit so you never sweep another agent's in-flight files. "
        "(2) Before committing engine changes, run the unit suites "
        "(warden/engine/test_warden_*.py) AND the golden corpus "
        "(warden/Warden Corpus/harness/run-corpus.py, default + --engine warden); "
        "keep the Rust↔Python differential (test_warden_rust.py) green. "
        "(3) `warden off` disables Warden globally if anything here misfires."
    )
```

### RULE R-warden-dev-02 — trait-reachability self-audit (when:: session:start)
when:: session:start

The [[F219 — Activation self-audit rules — base-trait + ruleset-reachability|F219]] integrity backstop — the rule engine guarding its own wiring. `warden compile` stamps the vault's declared anchor traits into the IR (`declared_traits`); this rule checks every trait that keys a *moment* rule against that snapshot (doc-rules fire by `where::` glob on the audit path and need no trait). A moment-rule trait no `.anchor` declares is **dead wiring** — authored, compiled, and unable to ever fire — exactly how `query` was found undeclared on 2026-07-05. `warden-selftest` is exempt: it is the hermetic test-fixture trait, declared only by test-scratch anchors outside the vault.

```python
def body(ctx):
    import json
    import os
    from pathlib import Path
    home = Path(os.environ.get("WARDEN_HOME", str(Path.home() / ".warden")))
    try:
        ir = json.loads((home / "rules-ir.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    declared = set(ir.get("declared_traits") or [])
    if not declared:
        return []          # pre-F219 IR — no wiring snapshot to audit against
    exempt = {"warden-selftest"}   # hermetic test-fixture trait
    moment_rules = {rid for ids in ir.get("moments", {}).values() for rid in ids}
    dead = sorted(
        t for t, ids in ir.get("traits", {}).items()
        if t not in declared and t not in exempt
        and any(r in moment_rules for r in ids))
    if not dead:
        return []
    return [
        "[warden trait-reachability] dead wiring — moment rules keyed by trait(s) "
        + ", ".join(dead)
        + " which no .anchor in the vault declares, so they can never fire live. "
          "Adopt the trait on an anchor that wants those rules, or retire the ruleset."
    ]
```
