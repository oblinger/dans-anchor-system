---
description: "the rule engine — declarative rules fired at agent moments, validated against whole-file format specs, with agent-steering feedback"
---

| -[[Warden]]- | : the rule engine — declarative rules fired at agent moments, validated against whole-file format specs, with agent-steering feedback<br>→ [[DAS]] → [Warden](hook://p/Warden)  |
| --- | --- |
| [[Warden Design\|Design]]  | [[Warden PRD\|PRD]],  [[Warden Architecture\|Architecture]],  [[Warden Interface\|Interface]],  [[Warden Rule\|Rule]],  [[Warden Semantics\|Semantics]],  [[Warden Events\|Events]],  [[Warden Runtime\|Runtime]],  [[Warden Roadmap\|Roadmap]],   |
| [[Warden User Docs\|User Docs]]  | [[Warden Examples\|Examples]],  [[Warden Examples Extended\|Examples Extended]],   |
| [[Warden Corpus\|Corpus]]  | the golden test corpus — rule × fixture × expected-verdict cases, the drift oracle for every Warden engine |
| [[Warden Track\|Track]]  | [[Warden Backlog\|Backlog]],  [[Warden Features\|Features]],   |
| ... |  |

# Warden


## Overview

**Warden** is the rule engine for the anchor system. Author a declarative rule once — `where` (the files) ∧ `when` (the agent moment) ∧ `if` (a Python test) — and Warden fires it at the right moment (or audits it), validates the whole resulting file against its format spec, and feeds a corrective `tell` back to the agent (or blocks the action with `deny`). It is the under-served capability the prior-art survey identified: whole-resulting-file validation against a rich multi-rule format spec, with per-violation agent feedback, on top of the standard Claude Code hook plumbing.

Warden is **consumed by** the `/rule` and `/audit` skills and underpins the [[DAS Ruleset]] facet — those reference Warden as their engine rather than re-implementing it.

The full design is [[Warden Design]]; the build sequence is [[Warden Roadmap]].

## Which copy runs — `~/ob/grove/warden`, always

Warden's engine exists at two paths, and **only one of them executes anything**. Measured 2026-08-02 (T097):

| | path | what it is |
|---|---|---|
| **Live** | `~/ob/grove/warden/engine/` | `~/bin/warden` is a symlink to `engine/warden`, so every `warden compile` / `warden off` you run is this copy |
| **Live** | `~/ob/grove/warden/rs/target/release/warden-rs` | the Rust engine the `settings.json` hooks invoke — this is what fires on every file write |
| **Inert** | `dans-anchor-system/warden/engine/` | a vendored mirror; nothing loads it |

**Edit the proj copy. A fix landed in the mirror runs nowhere.** The roadmap's Phase 1 extraction did happen ([[TINK Backlog#^T008|T008]]), but the intended `git subtree` vendor-back did not — the mirror is a plain copy that has since drifted, so the single-source-of-truth guarantee the subtree was meant to provide is not in force.

**The drift is one-directional, which is the useful part.** Ten source files differ (`warden`, `warden_compile.py`, `warden_fire.py`, `warden_hook.py`, `warden_scan.py`, and five `test_warden_*.py`), plus `conftest.py` exists only in proj. That is **403 proj-only lines against 41 mirror-only**, and every one of the 41 was checked: none is content the mirror uniquely holds. They are refactors — proj split `read_anchor_traits` into `_read_trait_list` + `read_anchor_traits`, and the `py_kinds` line simply gained a `"mend"` key beside it. So proj is a strict superset in substance, and **the mirror can be replaced wholesale whenever someone decides to; nothing needs rescuing from it first.**

**The trap this creates is diagnostic, not functional.** A directory copy carried `__pycache__` across, so during [[TINK Backlog#^T500|T500]] pytest ran from the proj repo while every traceback's `co_filename` pointed at the *mirror*. A debugging session that trusts those paths edits the copy that is not running — and the edit appears to do nothing, for reasons the traceback actively conceals.
