---
description: "work queue"
---
# HBR Backlog
<!-- state:backlog 05 -->
Harbor's work queue — horizon H2s, one row per item, status in brackets.

| -[[HBR Backlog]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[examples]] → [[HBR]] → [[HBR Track]] → [HBR Backlog](hook://p/HBR%20Backlog)<br>: work queue |
| --- | --- |
| Anchor | [[HBR Track]] (parent) |
| Related | [[HBR Features]],  [[HBR Roadmap]],   |
| ... | [[HBR Messages]],  [[HBR queries]],  [[HBR Status]],   |

## Ready

- **B-QFix — QFix** [Ready] — audit q findings routed by --fix; each sub-bullet is a residual on HBR's tree needing the 100%-fix discipline (per the audit skill's Governing principle). ^B-QFix
  - **Next:** Fix the next residual below at its source (repoint a renamed link, de-link a retired one, correct the flagged doc), then re-run `/audit q` to clear it — per the 100%-fix discipline.
  - **C23** SYS/Bespoke/Skill Agent/dans-anchor-system/examples/HBR/HBR Track/HBR Backlog.md:27 — row 'F003' is [Designing] with zero pending Qs but has no `- **Next:**` — add a no-user next action and it becomes [Ready] (a [Ready] row needs a Next per F171), or move it to [Done]
  - **C33** SYS/Bespoke/Skill Agent/dans-anchor-system/examples/HBR/HBR Track/HBR Backlog.md:27 — row 'F003' [Designing] has no `→ [[F<n>]]` link to a feature doc — [Designing] implies active design work in a linked doc. If parked, use [Waiting]; if ready to implement, [Ready]; if Qs remain, [N Questions] + link to the feature doc holding them.

## Active

- **F002 — Direct-play streaming** [Active] — byte-range session for already-playable files. ^F002
  - **Next:** Wire the byte-range handler into the serve path, then measure seek latency on a 4K sample.
## Now

- **F003 — Transcode fallback** [Designing] — choose the output codec when direct play fails; needs a codec-priority ruling. ^F003
  - **Status:** Designing — next action is to rank the fallback codecs by decoder availability, then write the ladder into HBR Features.

## Next
- **B1 — Cache eviction** `[Ready]` — evict hot segments least-recently-used once the cache dir passes its cap.

## Later
- **B2 — Watched-root hot reload** `[ ]` — re-scan when a watched root changes, without a restart.
