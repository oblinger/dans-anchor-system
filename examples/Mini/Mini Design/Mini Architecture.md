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

## See also

- [[Mini PRD]] — what Mini is for.
