---
aliases: ["Harbor Runbooks"]
description: canonical grouped-spine exemplar — direct children sorted under plain labels
---

| -[[HRUN]]- | : Harbor Runbooks — canonical grouped-spine exemplar — direct children sorted under plain labels<br>→ [[DAS]] → [[FEX]] → [HRUN](hook://p/HRUN)  |
| --- | --- |
| Related | [[FEX Spine Examples]],  [[DVT\|Devtools]],  [[DAS spine]],  [[DAS progressive-disclosure]],   |
| **Incident** | [[Harbor Runbook Egress Stall]],  [[Harbor Runbook Auth Storm]],  [[Harbor Runbook Cert Expiry]],   |
| **Routine** | [[Harbor Runbook Weekly Rotate]],  [[Harbor Runbook Cache Warm]],  [[Harbor Runbook Quota Review]],   |
| **Recovery** | [[Harbor Runbook Replay Queue]],  [[Harbor Runbook Rebuild Index]],   |
| ... |  |

# HRUN
Every Harbor runbook, sorted by when you reach for it — eight procedures in three situations.

| Severity | Who is paged | Response target | Runbook opens with |
|---|---|---|---|
| **S1** — traffic stopped | on-call + secondary, immediately | 5 min to acknowledge | the rollback step, before diagnosis |
| **S2** — degraded, still serving | on-call only | 15 min | the measurement that confirms degradation |
| **S3** — single hop over budget | next business morning | 1 day | the [[Harbor Latency Budget\|latency budget]] row it breached |
| **S4** — scheduled work | nobody; it is on the calendar | the window itself | a precondition checklist |

**S1 runbooks open with the rollback, not the diagnosis** — the one convention worth stating here, because it is the one people get wrong under pressure. Understanding why the egress stalled is an S2 activity; at S1 the job is to stop serving errors, and the reasoning goes in the postmortem.

> [!note] Canonical grouped spine
> A hub whose children **all live in this one folder**, sorted under a few plain-text labels. Compare it to a [[DVT|two-level spine]] side by side — that is the distinction this page exists to draw:
> - **The group labels are not links.** `Incident`, `Routine`, `Recovery` are headings, not destinations. There is no `Harbor Runbooks Incident` page, and there should not be: the eight runbooks are siblings in one folder, and the labels only tell you which one you want.
> - **No `+` marker**, because no row expands. `+` means "this label is itself a container"; here nothing is.
> - **Three groups beat eight rows.** The reader holds *when do I reach for this* — an incident, a chore, a cleanup — rather than eight filenames. That is the whole argument for grouping, and it is why grouped is the preferred hub shape whenever natural groups exist.
> - **The `...` is load-bearing.** A ninth runbook dropped into this folder appears there automatically. Without it the page would look complete while being wrong — the failure that is currently 16 pages deep in the live vault.
>
> The live counterpart is [[Rolodex]]: **Corporate**, **Professional**, **Personal** over contact groups that all sit under one folder, ending `...`.
