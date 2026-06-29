---
description: "system architecture"
---
# Mini Architecture
How Mini is built: a CLI front-end over a single key/value store.

## Overview

Mini is one small binary. The CLI parses a command, the Core applies it, and the Store persists the result to a single file on disk. There is no daemon, no network surface, and no concurrency — each invocation runs start to finish and exits.

## Architecture diagram

![[Mini Architecture.svg|520]]

*Source: `Mini Architecture.svg` (hand-written SVG).* Arrows are the request path: the CLI parses input into a Core call, and Core reads and writes through the Store.

## Subsystems

| SUBSYSTEMS      | Description                                                        |
| --------------- | ----------------------------------------------------------------- |
| [[Mini-Core]]   | command application logic — the submit/apply pipeline. Source: `src/core.rs`. |
| [Mini-Store]    | single-file key/value persistence; load/save (no doc yet)         |

## Decisions

Mini's **architecture** decisions live here, next to what they shape. (The cross-cutting *value* behind them — zero-setup — is a project-wide decision in [[Mini Decisions]].)

### D01 — Plain-text store, no database (checked)

**Choice.** Mini keeps its data in a single newline-delimited text file, not a database.

**Why.** A toy project should add no infrastructure a user must install or administer — a file the user can open in any editor beats a process they have to run. Serves the project-wide zero-setup value, [[Mini Decisions#D02|D02]].

**Consequences.** No concurrent writers and no query language — both fine at Mini's scale; revisit only if Mini grows past a single-user CLI.

## See also

- [[Mini PRD]] — what Mini is for.
