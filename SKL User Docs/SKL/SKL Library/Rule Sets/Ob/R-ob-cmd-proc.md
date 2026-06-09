# RULESET R-ob-cmd-proc
include::
description:: Ob's opinionated take on the command-processor / event-driven architecture pattern — single dispatcher routes events from sensors through engines to effectors. Use this set for applications with a clear input→process→output flow that benefits from a central routing layer, unified event log, and clean concurrency story. Other architectures (direct calls, async tasks, actor model, CQRS) work fine for different problems; this set captures Dan's specific approach when the dispatcher pattern fits.

### R-ob-cmd-proc-01 — Single dispatcher (sampled)

Every operation flows through one dispatcher. No side channels, no direct backend calls, no bypass paths. Single ordering, single log, single place for cross-cutting concerns.

**Why:** multiple dispatchers (or any direct backend calls) destroy the global ordering property — bugs become reproducibility-dependent, the unified log loses entries, and adding cross-cutting concerns (auditing, rate-limiting, instrumentation) requires touching every bypass site. Funneling through one dispatcher gives you one place to instrument.

**Check pattern:** search for invocations of backend / engine methods from outside the dispatcher path. Each is a violation unless documented as an architectural exception.

### R-ob-cmd-proc-02 — Synchronous by default (sampled)

The dispatcher processes one event at a time, blocking until complete. No event queues, no async runtime in the dispatcher itself.

**Why:** async dispatchers add concurrency to a domain that usually doesn't need it (most commands are fast). The complexity costs — ordering bugs, race conditions, harder debugging — outweigh the throughput gains. UI responsiveness, when needed, is achieved by running the synchronous dispatcher on a background thread (see R-ob-cmd-proc-12), not by making the dispatcher itself async.

**Check pattern:** search for async / Promise / Future signatures on dispatch entry points. Each is a violation unless the dispatcher's interface explicitly supports both sync and async modes.

### R-ob-cmd-proc-03 — Hardcoded dispatch routing (sampled)

Event routing is a match statement (or equivalent compile-time switch), not dynamic subscription. Engines and effectors are known at compile time.

**Why:** dynamic subscription (observer pattern, pub/sub) hides the dispatch graph — you can't read the source and know what handles a given event. Compile-time routing makes the entire flow grep-able. Cost: adding a new event type requires editing the dispatcher; this is a feature, not a bug — every new event gets a routing review.

**Check pattern:** search for runtime registration patterns (`.subscribe(...)`, `addEventListener`, `.on(...)`, dynamic dispatch tables keyed by string). Each is a violation unless graded as an exception (e.g., framework-required hooks).

### R-ob-cmd-proc-04 — Events are the universal type (sampled)

Commands, backend actions, responses, and sense data all use the same `Event` type. One enum, one serialization format, one log format.

**Why:** a unified Event type means the dispatcher has one routing surface, the log has one format, and replay/testing replay through the dispatcher works without translation. Parallel hierarchies (Command + Event + Query + Response) duplicate routing logic and create gaps where types don't compose.

**Check pattern:** look for parallel type hierarchies (Command + Event + Query) flowing through the dispatcher. Consolidating to one Event enum is the fix.

### R-ob-cmd-proc-05 — Events are JSON-serializable (checked)

Every event can be serialized to JSON. Enables logging, replay, and future remote execution without changing types.

**Why:** non-serializable events (containing closures, raw handles, mutex guards) block logging, prevent replay from a log file, and force the dispatcher to hand-marshal cross-boundary events. Forcing JSON-serializability at the type level catches this at design time.

**Check pattern:** every Event variant carries a derive / annotation enforcing serialization (e.g., Rust `#[derive(Serialize, Deserialize)]`). Compile-time check.

### R-ob-cmd-proc-06 — Unified event log (sampled)

All events from all sources are logged to a single timestamped stream. The log is the source of truth for ordering and debugging.

**Why:** per-component logs make cross-component bugs unreproducible — you can't reconstruct the order in which sensors fired and effectors responded. A unified log is the single timeline; it's what you give a user when asking "what happened?"

**Check pattern:** every dispatcher entry point emits to the unified log. Branches that skip logging are violations.

### R-ob-cmd-proc-07 — Sensors are stateless (sampled)

Sensors produce events and forget. No callbacks, no waiting for responses, no held state beyond connection handles.

**Why:** stateful sensors are themselves engines — they encode "what to do" instead of "what happened." This violates separation of concerns and makes the sensor untestable (its outputs depend on its history). Pushing state to engines keeps sensors thin and replayable.

**Check pattern:** sensors have no mutable fields beyond connection handles. Any state field is suspect.

### R-ob-cmd-proc-08 — Engines emit events, not side effects (sampled)

Engines produce backend events that flow back through the dispatcher rather than calling backends directly. This keeps the log complete and the ordering visible.

**Why:** direct side effects from engines bypass the dispatcher's logging, ordering, and cross-cutting concerns. The pattern "engine emits event → dispatcher routes to effector" is what makes the architecture auditable. Direct backend calls reintroduce the routing tangle the dispatcher was supposed to eliminate.

**Check pattern:** search for engine methods that call backend methods directly. Each is a violation; engines should emit `BackendEvent` enum variants instead.

### R-ob-cmd-proc-09 — Engines own domain logic (sampled)

Each engine encapsulates one domain of business logic with a clear, bounded responsibility. Cross-engine logic flows through events, not direct calls.

**Why:** engines that call each other directly couple their lifecycles, break independent testability, and re-introduce the routing tangle the dispatcher was supposed to eliminate. Each engine should be self-contained against its inputs.

**Check pattern:** search for cross-engine direct imports. Each is a violation unless one engine owns the other as a strict sub-component.

### R-ob-cmd-proc-10 — Engines are testable independently (stated)

Each engine works with mock backends via the dispatcher. No real I/O needed for tests.

**Why:** if an engine requires real I/O to test, you've hidden a dependency that should be pluggable. The trait-pluggable backend pattern (R-ob-cmd-proc-11) means every engine has a mockable I/O boundary, which means every engine is testable in isolation.

**Check pattern:** test files for each engine exist and use mock backends. Engines without independent test files are a smell.

### R-ob-cmd-proc-11 — Backends are trait-pluggable (checked)

Each backend (storage, network, OS, etc.) implements a trait. Production uses real backends; tests use mocks.

**Why:** the trait boundary is the test seam. Without it, you can't unit-test engines without real I/O; you also can't swap backends (e.g., file-IPC → socket-IPC) without rewriting engines.

**Check pattern:** every I/O subsystem is named via a trait, not a concrete struct. Engines hold `Box<dyn Trait>` (or equivalent), not concrete instances.

### R-ob-cmd-proc-12 — Backend operations are fast OR off-thread (stated)

Backend operations on the dispatch path complete within the application's responsiveness budget (typically <50ms). Operations that don't fit run on a background thread, not on the dispatcher.

**Why:** the dispatcher is synchronous (R-ob-cmd-proc-02). A slow operation blocks every other event. The fast-operation invariant keeps the dispatcher responsive; the background-thread escape hatch handles the inevitable exceptions without violating the synchronous-dispatcher rule.

**Check pattern:** profile-based or manual review. Search for known long-running operations (`Command::output()` on slow programs, blocking network calls, file scans) inside the dispatch path. Each is a violation unless wrapped in spawn-background.

### R-ob-cmd-proc-13 — Domain data types are pure (sampled)

Domain data types (Layout, State, Config, etc.) are pure data structures. No I/O fields, no cached backends, no embedded mutexes. Methods that need I/O take the backend as a parameter.

**Why:** data types that hold backends are no longer data — they're objects with hidden behavior. They can't be serialized, can't be transmitted, can't be diffed, can't be unit-tested in isolation. Keeping them pure means they round-trip through JSON and stay testable.

**Check pattern:** domain types have no `Box<dyn Backend>`-like fields. Methods that perform I/O take a backend reference parameter.
