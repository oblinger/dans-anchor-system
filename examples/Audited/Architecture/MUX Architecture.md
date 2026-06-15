---
description: top-level architecture facet — subsystem decomposition with bidirectional module links
architect_run: 2026-05-26
---
# MUX Architecture
Top-level architectural view of MuxUX — the Tauri overlay for tmux session management.

| -[[MUX Architecture]]- | → [[_]] → [[prj]] → [[ClaudiMux]] → [[MUX]] → [[MUX Docs]] → [[MUX Design]] → [MUX Architecture](hook://p/MUX%20Architecture)<br>: top-level architecture facet |
| --- | --- |
| Related | [[MUX Decisions]],  [[MUX Rules]],   |

## Overview

MuxUX decomposes into **11 subsystems** that reflect its runtime architectural commitments (single-dispatcher, event-as-universal-type, sensors-engines-effectors separation), plus the cross-cutting concerns that don't fit any one runtime stage (logging, native bridge, frontend, dev tools). The commitments are documented inline below (§ Architectural Commitments); each subsystem's Arch doc elaborates the commitments specific to it.

## Architecture diagram

![[MUX Architecture v2.svg|800]]

*Source: `MUX Architecture v2.svg`.* Boxes are the runtime subsystems; arrows trace event flow through the single dispatcher from sensors to engines to effectors.

## Subsystems

| SUBSYSTEMS              | Description                                                                  |
| ----------------------- | --------------------------------------------------------------------------- |
| [[MUX-Launcher]]        | Process supervisor — long-running shim that owns the DictaMux family's process lifecycle. Sole spawner of brain-bearing children; "exactly one brain alive" is a structural property, not a runtime mutex. |
| [[MUX-Dispatcher]]      | `Sys` central event dispatcher — single match-statement routing, synchronous, pane-level serialization. AppState integrates dispatcher into the Tauri shell. |
| [[MUX-Sensors]]         | Input event producers — global hotkey (CGEventTap), right-click overlay, snapshot timer, socket-CLI ingress. Stateless: produce events, forget. |
| [[MUX-Engines]]         | Domain-logic processors — layout realization, capture pipeline, parts expansion. Emit events back through dispatcher rather than side-effecting directly. |
| [[MUX-Effectors]]       | I/O boundary adapters — tmux command execution, window manipulation, preflight checks, session lifecycle, OS Window menu. Trait-pluggable (Shell vs Mock). |
| [[MUX-Data]]            | Pure data types — Layout/Expr trees, Parts catalog, MuxSettings/State/Tile/Agent. No I/O. JSON-serializable. |
| [[MUX-Native-Bridge]]   | macOS / AppKit / Cocoa interop — NSWindow observers, AX trust polling, DictaMUXKit.framework dlopen + callback registration. |
| [[MUX-Frontend]]        | TypeScript / HTML webview layer — overlay UI, xterm.js terminal, submenu panels, preferences screen, quick-open dialog. |
| [[MUX-Logging]]         | Cross-cutting structured-log infrastructure — async logsink + 8 channel-organized logline catalogs. Thin wrapper over `ob_utils::logging::structured`. |
| [[MUX-Reference]]       | Dev tools, audit scripts, CLI surface, justfile recipes, top-of-tree indices. Not part of the runtime — supports development + ops. |
| [[MUX-Permissions]]     | macOS TCC permissions architecture for the MUX + DMUX two-app bundle pattern. Gotcha catalog, recovery procedures, one-bundle migration proposal. |

## Platform & Tech Stack

- **Tauri 2 + Rust + system WebView.** Small binary (~10–20 MB, no bundled Chromium); native menu bar + tray; OS-level global hotkey registration; first-class macOS interop via `objc msg_send!`. Cross-platform by design; Mac-only in MVP.
- **Three crates + frontend** at `/Users/oblinger/ob/proj/ClaudiMux/muxux/`: `core/` (pure domain logic — Sys, Event, Layout, Parts, types), `tauri/` (app shell — IPC, AppState, Cocoa hooks, effectors, sensors), `cli/` (`mux` socket client), `frontend/` (TypeScript + xterm.js webview).
- **External dependencies surfaced at the boundary:** `ob-utils` (structured logging + socket service primitives — see [[MUX-Logging]]); `DictaMUXKit.framework` loaded via `dlopen` at runtime (see [[MUX-Native-Bridge]]).
- **Standalone, not part of an orchestrator.** MuxUX is its own app with its own settings at `~/.config/muxux/`.

## Architectural Commitments

Migrated 2026-06-08 to [[MUX Decisions]] as numbered D-records, per the rules-vs-decisions vocabulary split. The subsystem decomposition above is the structural realization of these commitments.

- **Dispatcher** — D05 (single dispatcher), D06 (synchronous), D07 (hardcoded dispatch), D08 (pane-level serialization).
- **Events** — D09 (everything is an event), D10 (JSON-serializable), D11 (unified event log).
- **Sensors** — D12 (CLI as universal external), D13 (internal use IPC), D14 (stateless).
- **Engines** — D15 (emit events not side effects), D16 (own domain logic), D17 (testable independently).
- **Effectors** — D18 (pluggable backends), D19 (operations fast), D20 (fire-and-forget for content).
- **Data** — D21 (layout is pure data structure), D22 (single namespace).
- **System singleton (Sys)** — D23–D27.
- **Tauri layer** — D28–D31.
- **Launcher / process model** — D01–D04.

## See Also

- [[MUX Architecture Versions]] — diagram revision history + edit workflow.
- [[MUX Layout Format]] — file-format spec for serialized layout expressions.
- [[MUX Decisions]] — durable anchor-wide rulings.
- [[MUX Files]] — file-tree index of the source repo.
