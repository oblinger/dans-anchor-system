---
description: Warden user documentation — the manual for writing and running rules
---
# Warden User Docs

| -[[Warden User Docs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[Warden]] → [Warden User Docs](hook://p/Warden%20User%20Docs)<br>: the manual — how to write and run Warden rules |
| --- | --- |
| [[Warden Examples]] | worked examples of every rule-execution mode (start here) |

**Warden** lets you state a rule once — *when* a moment happens, *where* (which file), and optionally *if* a condition holds — and have it enforced automatically, with a corrective message fed back to the agent. This is the user-facing manual: how to author rules and what they can do.

> [!note] Where the precise specs live
> This manual is task-oriented (*how do I…*). The authoritative formats are the reference specs: the rule/ruleset file format is [[Warden Rule]], the `when::` moment vocabulary is [[Warden Trigger Taxonomy]], and `where::` is [[FCT Ruleset]] § Where clause. New here? **[[Warden Examples]]** is the fastest way in.

## Contents

- **[[Warden Examples]]** — a single worked ruleset showing each kind of rule: a mechanical (script) check, an LLM-judged rule, a script-assisted LLM rule, and an expensive rule gated to re-run only on *significant* edits.
- *Getting started, the importer (Vale/Hookify), and the CLI — to come as Warden is built (see [[Warden Roadmap]]).*
