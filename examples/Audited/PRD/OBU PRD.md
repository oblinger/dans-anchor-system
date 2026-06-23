---
description: "product requirements — ob-utils shared utilities library, one spec across languages"
---
# OBU PRD
What ob-utils is and what it must deliver across its consumer languages.

| Outline                         |                                              |
| ------------------------------- | -------------------------------------------- |
| [[#Overview\|Overview]]         | what ob-utils is + who depends on it         |
| [[#Goals\|Goals]]               | what the library must deliver                |
| [[#Non-Goals\|Non-Goals]]       | what it deliberately is not                  |
| [[OBU PRD#User Stories\|OBU Stories]] | three user stories (inline; US-OBU-1..3) |
| [[#See also\|See also]]         | sibling design docs                          |

## Overview

`ob-utils` is a shared utilities library providing common infrastructure — structured logging, wire protocol, response types, socket client/service primitives, watch registry — that would otherwise be re-implemented per app. Apps depend on it instead of growing their own copies.

It is *specified once* in `OBU Dev/` (log format, wire protocol, response schema, heartbeat policy) and implemented *separately in each consumer language*. Rust is the master implementation; Swift and Python are planned siblings that implement against the spec. The goal is cross-language design *parity*, not binary interop: each language compiles independently against the spec, with no FFI bridge or shared dylib. Current consumers are MuxUX and SKD (both on the Rust crate); DMUX is slated to refactor onto the Swift port once it ships.

## Design Workflow

| Step | Document | Purpose |
|------|----------|---------|
| 1 | [[OBU PRD]] | Clarify requirements and scope |
| 2 | [[OBU Architecture]] | Module surface, wire protocol, response/log types |
| 3 | [[OBU Testing]] | Testing strategy + cross-language parity checks |
| 4 | [[OBU Decisions]] | Load-bearing decisions (master language, no-FFI, heartbeat policy) |
| 5 | [[OBU Track]] | Roadmap + features (incl. language ports) |

## Goals

- **One spec, many languages** — specify the library once in `OBU Dev/`; implement separately per language, Rust as master.
- **Cross-language design parity** — designers reference the same primitives (`LogEntry`, six-level `LogLevel`, `Compact` formatter `[TS] LEVEL module: message`, `hb:<subsystem>` heartbeat convention) and assume identical semantics on either side.
- **Heartbeat-discipline freeze diagnosis** — long-running threads emit `hb:<subsystem>` heartbeats; which ones keep ticking identifies a wedged subsystem, the same way in every consumer.
- **Replace per-app duplication** — apps with their own logging/protocol code (CMX Utils, ad-hoc loggers in DMUX/MuxUX) consolidate onto ob-utils over time.

## Non-Goals

- **Rust-Swift binary interop** — no FFI bridges, no shared dylib, no C ABI surface; each language's implementation is independent.
- **API innovation per language** — ports mirror the Rust API surface; idiom adjustments allowed, conceptual surface stays parallel.
- **Hot-path performance optimization** — ob-utils is general-purpose; apps with hard real-time constraints write their own.

## User Stories

### US-OBU-1 — Depend on shared logging
As an **app developer**, I want to pull structured logging from ob-utils instead of writing my own, so that my app's logs share the `[TS] LEVEL module: message` shape with every other app.
**Acceptance:** an app adds the ob-utils dependency, emits `LogEntry` values, and its output `grep`s uniformly with other consumers' logs.

### US-OBU-2 — Diagnose a freeze by heartbeat
As an **operator**, I want each long-running subsystem to emit `hb:<subsystem>` heartbeats, so that when the app wedges I can see which subsystem stopped ticking.
**Acceptance:** during a freeze, the heartbeat stream shows which `hb:<subsystem>` lines continue and which stop, isolating the wedged subsystem.

### US-OBU-3 — Add a language port against the spec
As a **library maintainer**, I want to implement a new language port against the language-agnostic spec, so that a new consumer language gets parity without reverse-engineering the Rust crate.
**Acceptance:** following the port process (baseline review → spec lift → parallel implementation → parallel docs), a new `<lang>/` implementation mirrors the master API surface module-by-module.

## See also

- [[OBU Architecture]] — module surface, wire protocol, response/log types
- [[OBU Decisions]] — master-language, no-FFI, and heartbeat-policy decisions
- [[OBU Track]] — roadmap incl. Swift/Python ports
