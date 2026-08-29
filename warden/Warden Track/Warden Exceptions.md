---
description: "numbered, graded accepted deviations from the rulesets the Warden anchor adopts (R-exception-discipline) — a violation neither fixed nor listed here is an open finding"
---

# [[Warden]] · Warden Exceptions
Accepted rule-violations against the anchor's adopted rulesets, each numbered, target-scoped, graded, and justified — the audit engine reads this table, so a row here is the only thing that suppresses a finding.

| EX | Rule | Target | Grade | Justification | Requester | Grader |
| --- | --- | --- | --- | --- | --- | --- |
| EX001 | R-one-path-01 | ** | A | **Two dispatcher implementations maintained in parallel** (Python `warden_hook` + Rust `hook.rs`, incl. mirrored helpers like `effective_traits`). Deliberate reference-implementation architecture: the Python engine is the behavioral oracle, Rust the installed hot path; the sync mechanism is two standing differential gates in CI (zero-divergence required) — the labeled-derived-mirror shape R-single-source-of-truth-02 sanctions.  Warden |  |
| EX002 | R-one-path-03 | ** | A | Same deliberate two-implementation architecture as EX001; split into its own row so each rule can be retired independently.  Warden |  |
| EX003 | R-interfaces-folder-01 | ** | B | **No `interfaces/` package.** The engine is a small procedural pipeline (9 modules, few classes); its real contracts are data schemas — `rules-ir.json`, the daemon IPC protocol, the hook JSON — not abstract types. Revisit if the engine grows a second implementation of any internal component.  Warden |  |
| EX004 | R-interfaces-folder-02 | ** | B | Same reasoning as EX003.  Warden |  |
| EX005 | R-factory-pegboard-01 | ** | B | **No factory-pegboard.** The one genuine implementation swap (Python ↔ Rust dispatcher) already goes through a registration-style switch (`warden install --rust`), not call-site edits.  Warden |  |
| EX006 | R-factory-pegboard-02 | ** | B | Same reasoning as EX005.  Warden |  |
| EX007 | R-factory-pegboard-03 | ** | B | Same reasoning as EX005.  Warden |  |
| EX008 | R-stable-ids-03 | Warden Track/Warden Roadmap.md | C | **Roadmap milestones numbered sequentially (M1–M8), and the M4a insertion happened** — exactly what gap numbering prevents. Renumbering a substantially-complete roadmap would break historical references, which stable-ids itself forbids; accepted as-is. Future Warden roadmaps gap-number from the start.  Warden |  |

## Log

**2026-08-28 — Requester/Grader columns added (F601).** All eight rows predate the columns: Requester is the anchor, Grader is blank — a legacy self-grade, honoured as before because none of these rules is `confirm:: user`.

**2026-08-08 — split to one rule per row, and every target made explicit.** The original three rows each named several rules at once (`R-interfaces-folder-01/-02, R-factory-pegboard-01/-02/-03` was a single cell), which meant no rule could be retired without editing a justification shared with four others. `EX001`–`EX003` became `EX001`–`EX008`, keeping the earlier handles on their first rule; retired numbers are never recycled, and none were. The `Target` column is new and is never blank — the two architectural exceptions are genuinely anchor-wide and now say so with `**` rather than leaving a reader to infer it.

**2026-07-06 — created**, when the Warden anchor became the first adopter of the F218 catalog and the adoption audit produced its first accepted deviations. For the month that followed it was the only exception table in the vault, and nothing read it; [[TINK314 - Exceptions: a graded, user-approved escape from any checked rule|F314]] made it live.
