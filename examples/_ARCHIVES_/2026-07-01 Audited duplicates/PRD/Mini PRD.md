---
description: "product requirements — what Mini does and the one story it must deliver"
---
# Mini PRD
What Mini is and the single thing its first version must do.

| Outline                         |                                              |
| ------------------------------- | -------------------------------------------- |
| [[#Overview\|Overview]]         | what Mini is                                 |
| [[#Goals\|Goals]]               | what v1 must deliver                         |
| [[#Non-Goals\|Non-Goals]]       | what v1 defers                               |
| [[Mini PRD#User Stories\|Mini Stories]] | one user story (inline; US-MINI-1)   |

## Overview

Mini is a one-command line counter: point it at a text file and it prints the number of lines. It is the smallest possible CLI — a single binary, no config, no state — and exists only as the minimal worked example of the Design-Docs facets.

## Design Workflow

| Step | Document | Purpose |
|------|----------|---------|
| 1 | [[Mini PRD]] | Clarify requirements and scope |
| 2 | [[Mini Architecture]] | System architecture (read → count → print) |
| 3 | [[Mini Testing]] | Testing strategy + proposed tests |
| 4 | [[Mini Decisions]] | Load-bearing decisions citing rules |

## Goals

- **Count lines** — given a file path, print the integer line count and exit 0.
- **Fail clearly** — given a missing or unreadable path, print one error line and exit non-zero.

## Non-Goals

- **Word / character counts** — out of scope for v1; line count only.
- **Reading from stdin** — v1 takes a path argument only; pipes are a later nicety.

## User Stories

### US-MINI-1 — Count the lines in a file
As a **user**, I want to point Mini at a file and get its line count, so that I can check a file's size without opening it.
**Acceptance:** `mini <path>` prints the line count and exits 0 for a readable file; prints one error line and exits non-zero for a missing path.
