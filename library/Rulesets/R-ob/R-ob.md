---
description: Umbrella folder-file for Ob's rulesets — applies to every project Dan owns regardless of trait. Children listed in the dispatch table below and rolled up via `includes::`. Commit-discipline and em-dash rules pending capture as separate rulesets.
applies-when: every project Dan owns (cross-cutting, not trait-scoped).
set-id: OB
---

| -[[R-ob]]- |  |
| --- | --- |
| [[R-ob-cmd-proc]] | Ob's opinionated take on the command-processor / event-driven architecture pattern — single dispatcher routes events from sensors through engines to effectors. Use this set for applications with a clear input→process→output flow that benefits from a central routing layer, unified event log, and clean concurrency story. Other architectures (direct calls, async tasks, actor model, CQRS) work fine for different problems; this set captures Dan's specific approach when the dispatcher pattern fits. |
| [[R-ob-observability]] | Ob's opinionated take on observability — failures don't disappear silently, and every OS-bridge call is instrumented. Reflects a "log everything, gate by tier" philosophy; other schools prefer minimal logging and richer error context. This set captures Dan's specific approach. |
| [[R-ob-state-mgt]] | Ob's opinionated take on state management — centralize config and state behind a single data singleton, and refuse to hardcode values that could vary. Not universal (other architectures use repository pattern, CQRS, event sourcing, functional state passing); this set captures Dan's specific approach. |
| --- | |

# RULESET R-ob
description:: Umbrella folder-file for Ob's rulesets — applies to every anchor Dan owns. Children rolled up via `includes::` below. The markdown rule formerly here (D-OB01) moved to [[R-md]] under [[R-doc]] (2026-06-09) since it's not Ob-specific. Commit-discipline and em-dash rules pending capture as their own rulesets.
includes:: [[R-ob-cmd-proc]], [[R-ob-observability]], [[R-ob-state-mgt]]


# Notes

A small canonical set of rules Dan applies to *every* project he owns. Not trait-scoped (a personal-Code-anchor and a personal-Skill-anchor both pull this in); not domain-scoped (applies to docs, code, configs alike). Naming "ob" mirrors the `ob-` prefix used elsewhere in Dan's tooling (`ob-skills`, `ob-utils`, vault root `~/ob/`). Rename if a better umbrella name surfaces later.