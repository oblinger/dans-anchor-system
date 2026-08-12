---
description: Umbrella folder-file for Ob's rulesets — applies to every project Dan owns regardless of trait. Children listed in the dispatch table below and rolled up via `include::`. Commit-discipline and em-dash rules pending capture as separate rulesets.
applies-when: every project Dan owns (cross-cutting, not trait-scoped).
set-id: OB
---

| -[[R-ob]]- | : Umbrella folder-file for Ob's rulesets — applies to every project Dan owns regardless of trait. Children listed in the dispatch table below and rolled up via `include::`. Commit-discipline and em-dash rules pending capture as separate rulesets.<br>→ [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [R-ob](hook://p/R-ob) |
| --- | --- |
| [[R-ob-cmd-proc]] | Ob's opinionated take on the command-processor / event-driven architecture pattern — single dispatcher routes events from sensors through engines to effectors. Use this set for applications with a clear input→process→output flow that benefits from a central routing layer, unified event log, and clean concurrency story. Other architectures (direct calls, async tasks, actor model, CQRS) work fine for different problems; this set captures Dan's specific approach when the dispatcher pattern fits. |
| [[R-ob-observability]] | Ob's opinionated take on observability — failures don't disappear silently, and every OS-bridge call is instrumented. Reflects a "log everything, gate by tier" philosophy; other schools prefer minimal logging and richer error context. This set captures Dan's specific approach. |
| [[R-ob-remote-ops]] | Ob's remote-ops hygiene — remote machines are driven through the sanctioned control planes (`bridge` persistent tmux, `exp`), never one-shot SSH remote-control. First member: the F183 bridge-guard (`tool:pre:Bash` deny, rides `anchor-base`). |
| [[R-ob-state-mgt]] | Ob's opinionated take on state management — centralize config and state behind a single data singleton, and refuse to hardcode values that could vary. Not universal (other architectures use repository pattern, CQRS, event sourcing, functional state passing); this set captures Dan's specific approach. |
| --- | |

# RULESET R-ob
description:: Umbrella folder-file for Ob's rulesets — applies to every anchor Dan owns. Children rolled up via `include::` below. The markdown rule formerly here (D-OB01) moved out in 2026-06-09 since it's not Ob-specific; it now lives in [[R-markdown]] under [[R-doc]] (via the interim `R-md`, deleted 2026-08-11). Commit-discipline and em-dash rules pending capture as their own rulesets.
include:: [[R-ob-cmd-proc]], [[R-ob-observability]], [[R-ob-state-mgt]], [[R-ob-remote-ops]] 


# Notes

> **`R-ob-observability` and `R-ob-state-mgt` gained a selector 2026-08-11 ([[TINK Backlog#^T212|T212]]), and the obvious one would have been wrong.** Both declared no `where::`, so they inherited `always` — every file in every anchor. The reflex fix is to copy the sibling: [[R-ob-cmd-proc]] declares `file:{anchor}/**/*.rs`. **Reading the rules refuses it.** `R-ob-observability-01` writes out three Check patterns under three headings — *(Rust)*, *(TS/JS)* and *(Python)*, naming `except: pass` and `.catch(() => default)` explicitly — and `R-ob-state-mgt-01` names `env::var`, `process.env` and `os.environ` in a single line. These sets are deliberately multi-language, and the sibling's selector would have silently discarded two thirds of what they say.
>
> **The measurement is the argument.** Across the vault, `.rs` reaches **6** source files; `{rs,py,ts,js}` reaches **347** — so the reflex fix would have scoped a *"no silent fallbacks"* rule to under 2% of the code it was written about, and reported green over the rest. That is the same defect shape as [[R-wcag-contrast]]'s `file:*.svg` (69 of 127 diagrams, found the same day): a selector narrower than its rules, which cannot announce itself because a narrow scope is clean by construction. Both now carry `file:{anchor}/**/*.{rs,py,ts,js}`.
>
> **[[R-ob-cmd-proc]]'s own `.rs` scope is left as found and is not obviously wrong** — its rules turn on Rust-specific machinery (`-05` JSON-serializable events, `-11` trait-pluggable backends), so narrow may be right there. It is flagged only because a family whose three members disagree about their own language scope is worth one reader noticing.
>
> Selectors are a precondition, not arming: this umbrella is still inert ([[TINK Backlog#^T208|T208]]), and all five rules across the two sets read `(checked)` while resolving to no checker — the layer T212 takes up next.

A small canonical set of rules Dan applies to *every* project he owns. Not trait-scoped (a personal-Code-anchor and a personal-Skill-anchor both pull this in); not domain-scoped (applies to docs, code, configs alike). Naming "ob" mirrors the `ob-` prefix used elsewhere in Dan's tooling (`dans-anchor-system`, `ob-utils`, vault root `~/ob/`). Rename if a better umbrella name surfaces later.