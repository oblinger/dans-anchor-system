---
description: "numbered, graded accepted deviations from the rulesets the Warden anchor adopts (R-exception-discipline) — a violation neither fixed nor listed here is an open finding"
---

# [[Warden]] · Warden Exceptions

Accepted rule-violations against the anchor's adopted rulesets ([[R-arch]], [[R-process]], plus the base), per [[R-exception-discipline]]: numbered EX-handles (monotonic, never recycled), each graded A–F with a one-line justification for not taking the strict fix. Created 2026-07-06 when the Warden anchor became the first adopter of the F218 catalog and the adoption audit produced its first accepted deviations.

| EX | Rule(s) | Grade | Deviation + justification |
| --- | --- | --- | --- |
| EX001 | R-one-path-01, R-one-path-03 | A | **Two dispatcher implementations maintained in parallel** (Python `warden_hook` + Rust `hook.rs`, incl. mirrored helpers like `effective_traits`). Deliberate reference-implementation architecture: the Python engine is the behavioral oracle, Rust the installed hot path; the sync mechanism is two standing differential gates in CI (zero-divergence required) — the labeled-derived-mirror shape R-single-source-of-truth-02 sanctions. |
| EX002 | R-interfaces-folder-01/-02, R-factory-pegboard-01/-02/-03 | B | **No `interfaces/` package, no factory-pegboard.** The engine is a small procedural pipeline (9 modules, few classes); its real contracts are data schemas — `rules-ir.json`, the daemon IPC protocol, the hook JSON — not abstract types. The one genuine implementation swap (Python ↔ Rust dispatcher) already goes through a registration-style switch (`warden install --rust`), not call-site edits. Revisit if the engine grows a second implementation of any internal component. |
| EX003 | R-stable-ids-03 | C | **Roadmap milestones numbered sequentially (M1–M8), and the M4a insertion happened** — exactly what gap numbering prevents. Renumbering a substantially-complete roadmap would break historical references, which stable-ids itself forbids; accepted as-is. Future Warden roadmaps gap-number from the start. |
