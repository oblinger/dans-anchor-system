---
description: product requirements document
---
# CAB PRD

The PRD (`{NAME} PRD.md`) defines what the product does: goals, user stories, scope, and constraints. It is the starting point for the design workflow and links to all other design documents.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

# TSK PRD

| TOC |  |
| --- | --- |
| 1 | Overview |
| 2 | Design Workflow |
| 3 | Goals & Non-Goals |
| 4 | User Stories |



## 1 Overview

Task Runner is a CLI tool for scheduling and running deferred shell tasks with priority queuing and retry semantics. It replaces ad-hoc cron jobs and shell scripts with a unified, testable scheduling engine.



## 2 Design Workflow

| Step | Document | Purpose |
|------|----------|---------|
| 1 | TSK PRD.md | Clarify requirements and scope |
| 2 | [[TSK Open Questions]] | Surface and resolve unknowns |
| 3 | [[TSK UX Design]] | Design CLI interface and output formats |
| 4 | [[TSK System Design]] | Design technical architecture |



## 3 Goals & Non-Goals

### Goals
- Schedule tasks with deadlines and priority ordering
- Retry failed tasks with configurable backoff
- Provide clear CLI output for task status and history

### Non-Goals
- GUI interface (CLI only for v1)
- Distributed scheduling across multiple machines
- Sub-second task granularity



## 4 User Stories

### US-1: Schedule a Task
As a developer, I want to schedule a shell command to run at a specific time so that I can defer work to off-peak hours.

### US-2: Monitor Task Status
As a developer, I want to see which tasks are pending, running, and completed so that I can track progress.

### US-3: Retry Failed Tasks
As a developer, I want failed tasks to automatically retry with backoff so that transient failures don't require manual intervention.

---



# Format Specification

## Location

`{NAME} PRD.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Document Structure

### TOC
A table of contents at the top linking to major sections by number.

### Overview
1-2 paragraphs explaining what the product is and why it exists.

### Design Workflow
A table linking to the other design documents in sequence: PRD → Open Questions → UX Design → System Design. Steps are iterative — resolving questions may require revisiting earlier docs.

### Goals & Non-Goals
Two subsections listing what the product will and will not do. Keeps scope focused.

### User Stories
H3 entries with the pattern `### US-N: Title`. Each story follows "As a {role}, I want {capability} so that {benefit}." Stories are numbered sequentially and not reordered after creation.

## Lifecycle

- **Create** at project inception — this is the first design document written
- **Update** when requirements change, adding new user stories with the next available number
- **The PRD is a living spec** — it reflects current requirements, not historical ones
