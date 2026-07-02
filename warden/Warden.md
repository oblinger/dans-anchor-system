---
description: Warden — the rule engine that powers /rule, /audit, and the ruleset facet
---
# Warden

| -[[Warden]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [Warden](hook://p/Warden)<br>: the rule engine — declarative rules fired at agent moments, validated against whole-file format specs, with agent-steering feedback |
| --- | --- |
| [[Warden Design\|Design]] | [[Warden PRD\|PRD]],  [[Warden Architecture\|Architecture]],  [[Warden Rule\|Rule]],  [[Warden Semantics\|Semantics]],  [[Warden Events\|Events]],  [[Warden Runtime\|Runtime]],  [[Warden Roadmap\|Roadmap]],   |
| [[Warden User Docs\|User Docs]] | [[Warden Examples\|Examples]],  [[Warden Examples Extended\|Examples Extended]],   |
| [[Warden Corpus\|Corpus]] | the golden test corpus — rule × fixture × expected-verdict cases, the drift oracle for every Warden engine |
| [[Warden Track\|Track]] | [[Warden Backlog\|Backlog]],  [[Warden Features\|Features]],   |

## Overview

**Warden** is the rule engine for the anchor system. Author a declarative rule once — `where` (the files) ∧ `when` (the agent moment) ∧ `if` (a Python test) — and Warden fires it at the right moment (or audits it), validates the whole resulting file against its format spec, and feeds a corrective `tell` back to the agent (or blocks the action with `deny`). It is the under-served capability the prior-art survey identified: whole-resulting-file validation against a rich multi-rule format spec, with per-violation agent feedback, on top of the standard Claude Code hook plumbing.

Warden is **consumed by** the `/rule` and `/audit` skills and underpins the [[FCT Ruleset]] facet — those reference Warden as their engine rather than re-implementing it.

The full design is [[Warden Design]]; the build sequence is [[Warden Roadmap]]. Warden currently lives inside the [[DAS]] (`ob-skills`) repo; Phase 1 of the roadmap extracts it to its own repository, after which it is vendored back into DAS via `git subtree` (single source of truth upstream, one-clone-loadable downstream).
