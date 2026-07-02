---
description: "product requirements for the CAE Example CLI scheduler"
---
# CAE PRD
Product requirements for the CAE Example CLI scheduler.

| -[[CAE PRD]]- | : Product requirements for the CAE Example CLI scheduler.<br>→ [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [[CAE Design]] → [CAE PRD](hook://p/CAE%20PRD) |
| --- | --- |
| [[CAE Stories]] | three user stories — index for US-CAE-1..3 (folder-form per [[FCT Stories]]) |
| [[CAE UX Design]] | CLI command surface, output shapes, error voice |
| [[CAE Architecture]] | system-architecture story (peer Design facet) |
| [[CAE Testing]] | testing strategy + proposed-tests overview |
| [[CAE Decisions]] | load-bearing decisions citing rules |
| --- | |

## Overview

CAE Example is a CLI tool for scheduling and running deferred shell tasks with priority queuing and retry semantics. It replaces ad-hoc cron jobs and shell scripts with a unified, testable scheduling engine.

## Design Workflow

| Step | Document | Purpose |
|------|----------|---------|
| 1 | [[CAE PRD]] | Clarify requirements and scope |
| 2 | [[CAE UX Design]] | Design the user-facing CLI surface (commands, output shape, error voice) |
| 3 | [[CAE Architecture]] | Design the technical architecture (subsystems, data flow, thread model) |
| 4 | [[CAE Testing]] | Strategy + proposed-tests overview consistent with architecture |
| 5 | [[CAE Decisions]] | Encode load-bearing decisions citing R-rules |
| 6 | [[CAE Track]] | Roadmap + features that implement the user stories |

Steps are iterative — open questions arising in any step land inline as `## Open Questions` H2 (per [[DSC ask-format]]) and resolve back into the originating section.

## Goals

- Schedule tasks with deadlines and priority ordering
- Retry failed tasks with configurable backoff
- Provide clear CLI output for task status and history

## Non-Goals

- GUI interface (CLI only for v1)
- Distributed scheduling across multiple machines
- Sub-second task granularity

## User Stories

See [[CAE Stories]] for the index. Three stories in folder-form per [[FCT Stories]]:

- [[US-CAE-1 — Schedule a Task|US-CAE-1: Schedule a Task]]
- [[US-CAE-2 — Monitor Task Status|US-CAE-2: Monitor Task Status]]
- [[US-CAE-3 — Retry Failed Tasks|US-CAE-3: Retry Failed Tasks]]

## See also

- [[FCT PRD]] — facet spec
- [[FCT Stories]] — stories sub-facet (active here in folder form)
- [[CAE UX Design]], [[CAE Architecture]], [[CAE Testing]], [[CAE Decisions]] — peer Design facets
- [[CAE Track]] — features and roadmap implementing these stories
