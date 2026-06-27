---
description: CAE Design — high-level system spec for the CAB Example anchor (PRD, System Design, Architecture, Principles, legacy Rollup). Created per F094 — 2026-06-01.
---

# CAE Design

| -[[CAE Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [CAE Design](hook://p/CAE%20Design)<br>: design — system spec, architecture, principles |
| --- | --- |
| [[CAE PRD\|PRD]] | product requirements (folder form — contains [[CAE Stories]] + per-story files) |
| [[CAE UX Design\|UX Design]] | user-facing CLI surface — commands, output shape, error voice |
| [[CAE Architecture\|Architecture]] | system-architecture story (peer Design facet) |
| [[CAE Testing\|Testing]] | testing strategy + proposed-tests overview (worked example of [[CAB Testing]]) |
| [[CAE Decisions\|Decisions]] | load-bearing decisions citing rules |
| [[CAE Roadmap\|Roadmap]] | sequencing-design — milestones + ordering (moved from Track 2026-06-10) |
| [[CAE Features\|Features]] | per-feature design docs `F<NNN> — <Title>.md` (moved from Track 2026-06-10) |
| --- | |
| [[CAE API Design]] | programmatic surface of the `cae` Rust crate — types, signatures, error envelope, stability + compatibility commitments. Sibling to |
| [[CAE CLI]] | command reference — every command, flag, exit code |
| [[CAE Completed Roadmap]] | companion to CAE Roadmap; preserved migrated milestones with their structure; newest-on-top. |
| [[CAE Decisions Details]] |  |
| [[CAE Rules]] | CAE's anchor-local ruleset — rules truly specific to this example anchor |

Per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] (2026-06-01) — Design is the umbrella for system-spec content. Architecture (relocated from CAE User), PRD, System Design, Principles, and the legacy Rollup all live here. See [[CAB Design Dispatch]] for the canonical Design-dispatch shape.

(CAE has the legacy `Rollup.md` rather than an `Interface.md`; per [[F062]] the Rollup → Interface migration happens during normal anchor work.)
