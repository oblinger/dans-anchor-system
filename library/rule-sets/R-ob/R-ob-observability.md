# RULESET R-ob-observability
include::
description:: Ob's opinionated take on observability — failures don't disappear silently, and every OS-bridge call is instrumented. Reflects a "log everything, gate by tier" philosophy; other schools prefer minimal logging and richer error context. This set captures Dan's specific approach.

### RULE R-ob-observability-01 — No silent fallbacks (checked)

When a fallible operation fails, the failure is (a) propagated to the caller as `Err` / exception, OR (b) logged with enough context to diagnose. Silently substituting a default, discarding the error, or proceeding with empty state is a violation. Every silent-fallback site is either fixed or listed in an Exceptions table with a grade + justification.

**Why:** silent fallbacks mask bugs. A `.unwrap_or_default()` on a config parse turns a config-syntax error into a silent revert-to-defaults that the user discovers weeks later when behavior is wrong. Either propagate the error (forces the caller to handle it explicitly) or log it (preserves the diagnostic trail). Defaulting silently is the only option that destroys information.

**Check pattern (Rust):** search for these silent-fallback shapes — each is a violation unless logged or graded as an exception:
- `.unwrap_or(<default>)` and `.unwrap_or_default()`
- `.unwrap_or_else(|_| <default>)`
- `.ok()` on `Result` followed by `unwrap_or_default()` or `if let Some(...)`
- `let _ = fallible_call()` (where the function isn't documented as best-effort + self-logging)
- `if let Ok(v) = ... { ... }` with no `else` branch
- `match ... { Ok(v) => ..., Err(_) => <default> }`

**Check pattern (TS/JS):** `catch (_) { return default }`, `.catch(() => default)`, `try { ... } catch { /* nothing */ }`.

**Grading per finding:**
- **High** — silent fallback masks a bug the user would want to see (config parse error, IPC failure, missing-required-file). Fix: log warning + propagate or use documented default.
- **Medium** — fallback hides a less-impactful failure but loses information. Fix: add log line; default value can stay.
- **Low** — defensible exception (best-effort function that logs internally; optional field with documented None semantic; test fixture).

### RULE R-ob-observability-02 — 100% OS-bridge logging coverage (checked)

Every line of application code that bridges to the operating system emits a log entry within ~10 lines, OR is listed in an audit exception table with a graded justification. Both **egress** (calls the application makes into the OS — FFI, process spawn, file I/O, dynamic library loading) and **ingress** (notification streams the application could observe — system event sources, observer callbacks) are in scope.

**Why:** OS-level operations are the most common source of "the app froze and I don't know why" bugs. Without logging, you have to reproduce the freeze under a debugger; with a `trace_high`-equivalent instrumentation tier gated by an env var, you can capture the log from the user's failed session and read it back. The cost of an unused gated log line is ~1ns; the cost of an absent one is a multi-hour debug session.

The default disposition is **log it**. Exceptions are only valid when adding a log emit would cause measurable damage (perf cliff in a sub-microsecond hot loop, recursive-logging risk, log-bandwidth ratio exceeding policy thresholds). The fact that a log line is "noisy" is NOT a valid exception — if the logging system gates trace-high emits at the macro level with near-zero cost when off, noise is free to add and selectively enable.

**Check pattern:** scan the application's source for these OS-bridging sites:
- Direct OS API calls (Rust `msg_send!`, `extern "C"` blocks, `std::fs::*`, `std::process::Command::*`, `dlopen` / `dlsym`, `dispatch_*`)
- Observer registrations (`NSNotificationCenter`, distributed notifications, `CGDisplay*` callbacks)
- IPC boundaries (socket reads/writes, file-IPC writes)
- Missing observer coverage: every notification name in {NSWindow / NSApplication / NSWorkspace / NSScreen / CGDisplay / distributed notifications} that the adopter doesn't subscribe to must appear in the exception table

For each found site: pass if a logger emit is within ±10 lines; otherwise add to the adopter's exception table with grade — **Low** (clear exception OK), **Medium** (should add log but no harm in deferring), **High** (must add log, the missing instrumentation is actively costing round-trips).
