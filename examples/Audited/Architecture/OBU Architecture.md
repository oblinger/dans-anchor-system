---
description: "system architecture"
---
# OBU Architecture
How ob-utils is built: a small synchronous Rust crate of independent subsystems — a Unix-socket client/service stack plus a standalone logging stack.

## Overview

ob-utils is a dependency-light Rust crate (`serde`, `serde_json`, `libc`; no async runtime, no crypto, no network beyond Unix-domain sockets + `flock`). Consumer apps (MuxUX, SKD, …) pull only the subsystems they need: the framed client/service/watch stack for IPC, an opt-in heavier `protocol` upgrade path, and a logging subsystem that has no dependency on the rest. Every module is either a pure state machine or synchronous I/O, so the crate compiles fast and tests run without external services.

## Architecture diagram

![[OBU Architecture.svg|800]]

*Source: `OBU Architecture.svg` (hand-written SVG).* Consumer apps call into Client / Service / Watch, which share framing + the JSON `Response` payload; `protocol` is an opt-in upgrade path below them. Logging is an independent subsystem consumed directly by apps.

## Subsystems

| SUBSYSTEMS         | Description                                                                  |
| ------------------ | --------------------------------------------------------------------------- |
| [[OBU-Client]]     | Socket client — framed I/O, locks, single-instance, daemon spawn             |
| [[OBU-Service]]    | Unix-domain socket listener with framed JSON I/O                             |
| [[OBU-Watch]]      | Long-poll registry extending Service with live-update semantics              |
| [[OBU-Response]]   | Shared `Response` / `Direction` / `Action` payload types                     |
| [[OBU-Protocol]]   | Opt-in heavier stack — binary frames, codec, streams, multiplex, auth, router |
| [[OBU-Logging]]    | Independent logging subsystem — structured, buffer, filter, audit            |

## Module grouping

- **Logging** has no dependencies on the protocol/client/service stack. Any crate can take it alone.
- **Client** and **Service** are peers — same framing, same `Response` payload. A library using both is a daemon that also makes outbound calls.
- **Watch** extends Service with long-poll semantics. A service can offer both `send_and_receive` and `watch`.
- **Protocol** is the opt-in heavier stack (binary frames, streaming, auth). Nothing in logging/response requires it.
- **Response** is the universal return type — keep it string-payloaded so the wire is schema-agnostic; put JSON inside the string for structured data.

## Process model

In-process library, single-threaded by default. A `Service` owns one Unix-domain socket and serves clients synchronously; `Watch` adds long-poll registry semantics on top. No daemon fan-out — the consumer app decides whether to spawn a daemon (Client provides the single-instance + spawn helpers).

## Versioning

The crate version lives in `rs/Cargo.toml`. Wire-level protocol versioning lives separately in `protocol::codec::ProtocolVersion` (semver, major-match required). Consumers can pin on the former; peers negotiate the latter.

## See also

- [[OBU PRD]] — what ob-utils is for.
- [[OBU Decisions]] — durable crate-wide rulings.
