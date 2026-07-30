---
description: "work queue"
---
# HBR Backlog
<!-- state:backlog w9 -->
Harbor's work queue — horizon H2s, one row per item, status in brackets.

| -[[HBR Backlog]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[examples]] → [[HBR]] → [[HBR Track]] → [HBR Backlog](hook://p/HBR%20Backlog)<br>: work queue |
| --- | --- |
| Anchor | [[HBR Track]] (parent) |
| Related | [[HBR Features]],  [[HBR Roadmap]],   |
| ... | [[HBR Messages]],  [[HBR queries]],  [[HBR Status]],   |

## Ready

- **B-QFix — QFix** [Ready] — audit q findings routed by --fix; each sub-bullet is a residual on HBR's tree needing the 100%-fix discipline (per the audit skill's Governing principle). ^B-QFix
  - **Next:** Fix the next residual below at its source (repoint a renamed link, de-link a retired one, correct the flagged doc), then re-run `/audit q` to clear it — per the 100%-fix discipline.
  - **C14** SYS/Bespoke/Skill Agent/dans-anchor-system/examples/HBR/HBR Track/HBR Backlog.md:14 — row 'F002' has [] bracket under ## Active H2 — workflow-state H2 must match bracket; needs /groom body-reading
  - **C25** SYS/Bespoke/Skill Agent/dans-anchor-system/examples/HBR/HBR Track/HBR Backlog.md:17 — bullet row 'F003' [Designing] has no justification — per F102 every [Designing] row must carry **Designing** + next-action (in linked doc's ## Status H2, or inline `- **Status:** Designing — <next-action>` sub-bullet).

## Active
- **F002 — Direct-play streaming** `[Active]` — byte-range session for already-playable files. → [[HBR Features]] 

## Now
- **F003 — Transcode fallback** `[Designing]` — choose the output codec when direct play fails; needs a codec-priority ruling.

## Next
- **B1 — Cache eviction** `[Ready]` — evict hot segments least-recently-used once the cache dir passes its cap.

## Later
- **B2 — Watched-root hot reload** `[ ]` — re-scan when a watched root changes, without a restart.
