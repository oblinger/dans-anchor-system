---
description: "HookAnchor system architecture — top-level decomposition into subsystems."
---
# HA Architecture
HookAnchor system architecture — the top-level decomposition into subsystems, each owning a coherent slice of the codebase.

## Overview

The HookAnchor system decomposes into the subsystems below. Each subsystem owns a coherent slice of the codebase, has its own architecture doc, and lists the source modules under its responsibility. The "every module belongs to exactly one subsystem" invariant is enforced by [[architect]] — orphans and duplicates surface as proposals on re-run. This top-level doc points at each subsystem; the actual content lives in the subsystem docs.

## Architecture diagram

![[HA Architecture.svg|640]]

*Source: `HA Architecture.svg` (hand-written SVG).* The CLI / URL handlers drive Execution, which fans out to Scanner (file discovery) and Electric (dispatch-table rebuild); all of them read and write through the shared Data Model.

## Subsystems

| SUBSYSTEMS              | Description                                                                  |
| ----------------------- | --------------------------------------------------------------------------- |
| [[HA-Anchor]]           | Anchor data model — `.anchor` files, anchor detection, description metadata access (single getter/setter routing FM / inline / anchor file). |
| [HA-Electric]           | Dispatch-table rebuilder. Watches anchor-page changes, regenerates breadcrumbs / link lists / dispatch tables in-place. Two-tier quiescence. (no doc yet) |
| [HA-Scanner]            | File discovery + indexing. Vault scan, file_watcher events, storm protection, anchor-trigger detection. (no doc yet) |
| [HA-Data-Model]         | Commands singleton (`sys_data`), `commands.txt`, deferred-validate retry policy, percent-encoding primitive. (no doc yet) |
| [HA-Execution]          | Three-tier action dispatch (Rust → config.yaml → config.js), command worker (P01/P02/P03), IPC. (no doc yet) |
| [HA-Popup]              | egui-based popup window, AnchorSelector state machine, dialog flow. (no doc yet) |
| [HA-CLI]                | `ha` binary subcommands, daemon-first dispatch, URL handlers. (no doc yet)   |
| [HA-JS-Runtime]         | QuickJS-backed JS evaluation, `setup_*` builder pipeline, template expansion. (no doc yet) |
| [HA-Supervisor]         | Process lifecycle: HookAnchorSupervisor, popup_server, ha daemon. setsid + SIGHUP handling, respawn rate-limit. (no doc yet) |
| [HA-Utilities]          | Cross-cutting helpers: logging, error display, process-lock, subprocess, dialog2, build verification. (no doc yet) |

## Process model

Daemon-first. The `ha` CLI dispatches to a long-running daemon (spawned via setsid) that owns the Scanner watcher, the Electric rebuild loop, and the Data Model singleton; subcommands short-circuit to the daemon over IPC. The Supervisor subsystem manages process lifecycle and respawn.

## See also

- [[HA Rules]] § Design Principles (P01–P09) — operational invariants that constrain how subsystems interact.
- [[HA Interface]] — the layer-contract for what callers see from outside HookAnchor.
- [[HA Files]] — the file-tree index pointing at every module's per-module doc.
