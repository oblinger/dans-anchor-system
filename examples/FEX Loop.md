---
description: worked example of a loop — a stone on its owner's list, the Cigna refill workflow it runs, and the ## Log a cycle leaves behind
---

| -[[FEX Loop]]- | → [[DAS]] → [[FEX]] → [FEX Loop](hook://p/FEX%20Loop)  |
| --- | --- |
| Facet | [[DAS Loop]],   |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[BRDG]],  [[Clarifier]],  [[CSE]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DVT]],  [[ESP]],  [[Espresso]],  [[FEX Agenda\|Agenda]],  [[FEX API\|API]],  [[FEX API Design\|API Design]],  [[FEX Architecture\|Architecture]],  [[FEX At Entity\|At Entity]],  [[FEX Claude\|Claude]],  [[FEX Completed Roadmap\|Completed Roadmap]],  [[FEX CSE\|CSE]],  [[FEX Decisions\|Decisions]],  [[FEX Decisions Details\|Decisions Details]],  [[FEX Dispatch Examples\|Dispatch Examples]],  [[FEX Empty\|Empty]],  [[FEX Facet\|Facet]],  [[FEX Figure Page\|Figure Page]],  [[FEX Files\|Files]],  [[FEX Icebox\|Icebox]],  [[FEX Inbox\|Inbox]],  [[FEX Minimal Facet\|Minimal Facet]],  [[FEX Minimal Skill\|Minimal Skill]],  [[FEX Project Root\|Project Root]],  [[FEX Repo\|Repo]],  [[FEX Roadmap\|Roadmap]],  [[FEX Rules\|Rules]],  [[FEX Scheduler\|Scheduler]],  [[FEX Skill\|Skill]],  [[FEX Spine Examples\|Spine Examples]],  [[FEX Stories\|Stories]],  [[FEX System Design\|System Design]],  [[Forum Stories]],  [[Harbor Account Northwind]],  [[Harbor Integrations]],  [[Harbor Latency Budget]],  [[Harbor Releases]],  [[Harbor Tenancy Model]],  [[Harbor Upgrade Guide]],  [[HBR]],  [[HBR PRD User Stories]],  [[HHOP]],  [[HRUN]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

# FEX Loop
One loop from mint to close, as the files actually read. The workflow lives on a template; the stone carries the bindings, the handoff keys and the step; the watch list holds a reference.

## The workflow template — `MED Cigna Refill.md`

The section the `workflow::` link resolves to:

## Workflow

requires:: window-open, run-out
raise:: daily

| step | when | probe | hit | miss |
|---|---|---|---|---|
| open | `window-open` | `key: ordered` | confirm | press |
| press | `+7d` · importance high | `key: ordered` | confirm | dan |
| confirm | `ordered+3d` | `portal: [[@Cigna]] — Orders and Balances shows the order` | arrive | open · importance critical |
| arrive | `run-out-3d` | `mail: from:express-scripts subject:delivered` · `key: arrived` | close | dan |

## The stone — `MED P0007.md`, after `loop start` and one scan

line:: September Cigna order — Eliquis + Atorvastatin
appears:: MED, TRAFFIC
workflow:: [[MED Cigna Refill]]
channel:: [[@Cigna]]
window-open:: 2026-09-12
run-out:: 2026-10-01
due:: 2026-10-01
done:: the supply is on the shelf
importance:: high
lapses:: Eliquis runs out 2026-10-01
step:: press
entered:: 2026-09-13
tempo:: daily
enrolled:: TRAFFIC

Body prose is the owner's. Then:

## Log

- 2026-09-10 — started at `open` on [[MED Cigna Refill]]
- 2026-09-13 — open → press — scan: key: `ordered::` not set

## The commands that produced it

```
stone new MED --line "September Cigna order — Eliquis + Atorvastatin"
loop start MED P0007 --workflow "[[MED Cigna Refill]]" --channel "[[@Cigna]]" \
    --set window-open=2026-09-12 --set run-out=2026-10-01 \
    --set due=2026-10-01 --set "done=the supply is on the shelf" \
    --set importance=nominal --set "lapses=Eliquis runs out 2026-10-01"
loop scan --apply            # hourly, from sparks-watch
loop advance MED P0007 --to arrive --evidence "portal shows order 4471"
loop close MED P0007 --evidence "bottles on the shelf"
```

The line on `TRAFFIC Pebbles.md` reads `[[MED P0007|MED:]] September Cigna order — Eliquis + Atorvastatin` and is gone after `close`.
