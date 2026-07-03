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
