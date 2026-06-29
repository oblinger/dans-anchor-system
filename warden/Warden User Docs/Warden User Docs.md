---
description: Warden user documentation — the manual for writing and running rules
---
# Warden User Docs

| -[[Warden User Docs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[Warden]] → [Warden User Docs](hook://p/Warden%20User%20Docs)<br>: the manual — how to write and run Warden rules |
| --- | --- |
| [[Warden Examples]] | worked examples of every rule-execution mode (start here) |

**Warden** lets you state a rule once — *when* a moment happens, *where* (which file), and optionally *if* a condition holds — and have it enforced automatically, with a corrective message fed back to the agent. This is the user-facing manual: how to author rules and what they can do.

> [!note] Where the precise specs live
> This manual is task-oriented (*how do I…*). The authoritative formats are the reference specs: the rule/ruleset file format is [[Warden Rule]], the `when::` moment vocabulary is [[Warden Events]], and `where::` is [[FCT Ruleset]] § Where clause. New here? **[[Warden Examples]]** is the fastest way in.

## Contents

- **[[Warden Examples]]** — one worked ruleset, ten complete rules: a prose `tell`, a Python test, an LLM judgment, a script-assisted judgment, an `edit`, a `deny`, a shell (`sh`) condition, a Python `run`, a shell `run`, and sensing `agent` state.
- *Getting started, the importer (Vale/Hookify), and the CLI — to come as Warden is built (see [[Warden Roadmap]]).*
