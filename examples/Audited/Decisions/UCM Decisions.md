---
description: "architectural and implementation decisions for UCM"
---
# UCM Decisions
include::

Architectural and implementation decisions for the UCM project. Each is a D-record: the choice, the rationale, and the downstream commitments.

## D01 — Implement the parser in Rust using nom (checked)
**Ratified:** 2026-01-08

**Choice.** Implement the UCM parser in **Rust using nom** (parser combinators), with a runtime-configurable grammar:

- **Grammar rules** written in readable PEG-like notation in an associated markdown/text file.
- **Token table** runtime-configurable via a grammar-definition string (like the original Python parser): token precedence, types, modifiers; scaffolding rewrites (paren unwrap, head pulling, separator removal); semantic rewrite rules (if/elif/else chains, decorator merging). No performance penalty for runtime configuration (one-time init cost only).
- **Delivery form factors:** Rust library (core), Python library via PyO3 (`pip install ucm`), standalone CLI binary, WASM (future).

**Why.** Rust + nom provides speed, safety, and flexibility, with escape hatches for complex parsing (precedence, indentation). PyO3 gives Python users native speed with a simple API. A runtime-configurable grammar enables domain-specific customization, and a single Rust codebase serves all delivery targets — no parallel implementations to drift.

**Consequences.**
- One Rust core; all bindings (Python / CLI / WASM) build on it.
- The grammar definition is data, not code — customization needs no recompile.

## Related Documents
- [[UCM Parse Rules]] - Token table and PEG-style behavior rules
- [[UCM Notes]] - Performance analysis and trade-off discussion
- [[UCM Test Cases]] - Test suite to validate implementation
