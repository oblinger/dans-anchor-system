---
description: system design — PRD, UX Design, Testing
---
# DAS Bridge Design
System design for the bridge skill — PRD and design docs.

| -[[DAS Bridge Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [design](hook://design) → [DAS Bridge Design](hook://p/DAS%20Bridge%20Design)<br>: system design — PRD, UX Design, Testing |
| --- | --- |
| [[DAS Bridge PRD\|PRD]]  | what bridge produces; the three kinds of bridging (control / sync / claude); mechanism-vs-goal; config-is-the-recipe |
| [[DAS Bridge UX Design\|UX Design]]  | the subskill command surface — every verb, its arguments, output shape, confirmation gates |
| [[DAS Bridge Testing\|Testing]]  | testing strategy + proposed integration tests, grouped by bridge kind |
| --- | |

See ~~[[DAS Design Dispatch]]~~ for the canonical Design-dispatch shape. The live runbook is `~/.claude/skills/bridge/SKILL.md` (~~[[DAS Bridge|bridge]]~~); this design hierarchy is the *what/why*, the SKILL.md is the *how*.

## Provenance

Commissioned + built 2026-06-11 as [[F150 — Rename mux-bridge → bridge — umbrella with mux_sync_claude sub-bridges + environment manifest|F150]] (renamed from `mux-bridge`). Sync mechanism designed in [[F122 — mux-bridge file-sync extension (Syncthing + NFS-via-symlink + rsync future)|F122]]; defaults/manifest layer in [[F146 — mux-bridge sync defaults + interactive setup|F146]]. Design relocated from the SKA-level `SKA Bridge` anchor into this repo 2026-07-18 (F263, per SKA D13); `SKA Bridge` dissolved.
