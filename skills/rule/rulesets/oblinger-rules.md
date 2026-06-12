# Oblinger's Rules

Universal rules that apply to all projects. Appended to every project's rules file during `/rule create` and synced via `/rule sync`.

## Data Centralization

### OB-R01 — All config access goes through the data singleton
RULE: All configuration reads and writes must go through the centralized config/settings object. No component may read config from environment variables, files, or command-line args directly. No component may write config except through the singleton's save operation.

**Pattern:** Config is loaded into the in-memory singleton during initialization. During execution, all components read config from this object. Config changes update the in-memory object, then call save. No direct `env::var()`, no direct file reads, no hardcoded paths to config files.

**Check:** Search for `env::var`, `std::env`, `process.env`, `os.environ`, file reads of `.yaml`/`.json`/`.toml` config files outside the singleton's load function. Each is a violation.

### OB-R02 — All state access goes through the data singleton
RULE: All application state reads and writes must go through the centralized state object. No component may maintain its own shadow copy of shared state. No component may read or write state except through the singleton.

**Pattern:** State is loaded into the in-memory singleton during initialization. During execution, all components read and write state through this object. State changes update the in-memory object, then call save. No local caches, no "I'll keep my own copy," no direct file writes to state files.

**Check:** Search for components that store values also found in the state singleton. Search for direct reads/writes to state files outside the singleton's load/save functions. Each is a violation.

### OB-R03 — No hardcoded values that belong in config
RULE: Values that a user might want to change, or that differ between environments, must be in the config system. Hardcoded constants are only acceptable for values that are intrinsic to the algorithm (e.g., mathematical constants, protocol-defined values).

**Check:** Search for numeric literals, string literals, and timeout values in source code. For each, ask: "would someone ever want this to be different?" If yes, it belongs in config.

## Error Handling

### OB-R05 — No silent fallbacks
RULE: When a fallible operation fails, the failure must be (a) propagated to the caller as `Err` / exception, OR (b) logged with enough context to diagnose. Silently substituting a default, discarding the error, or proceeding with empty state is a violation. Every silent-fallback site must either be fixed or listed in the project's `R05 Exceptions` table with a grade + justification.

**Pattern:** A fallible call (`Result<T, E>` in Rust, `Promise` rejection in TS, `try`/`except` in Python, etc.) yields one of three outcomes: success (use the value), known-recoverable failure (substitute a documented default AND log the substitution), or propagate. Silent fallback is the case where the third option's documented-substitute step is missing.

**Check (Rust):** Search for these silent-fallback shapes — each is a violation unless logged or graded as an exception:
- `.unwrap_or(<default>)` and `.unwrap_or_default()` — the fallback is silent unless the call site emits a warning when the Err case fires.
- `.unwrap_or_else(|_| <default>)` — same; the closure usually drops the error.
- `.ok()` on `Result` followed by `unwrap_or_default()` or `if let Some(...)` — the Err is silently converted to None and the failure mode disappears.
- `let _ = fallible_call()` — return value (including `Result`) is explicitly ignored. If the function is documented as best-effort, the discard is OK provided the function itself logs on failure.
- `if let Ok(v) = ... { ... }` with no `else` branch — Err case is a no-op; sometimes correct, often a silent skip.
- `match ... { Ok(v) => ..., Err(_) => <default> }` — same shape as unwrap_or_else.
- `unwrap_or_default()` on `Option<T>` deep in a parse path where None means "config file malformed" — caller can't distinguish "field absent" from "file broken."

**Check (TS/JS):** `catch (_) { return default }`, `.catch(() => default)`, `try { ... } catch { /* nothing */ }`, optional-chaining `?.` that swallows undefined when the property is expected.

**Check (Python):** `except: pass`, `except Exception: pass`, `.get(key, default)` when the key is supposed to be present, `try/except` blocks that don't log.

**Grading (per finding):**
- **High** — the silent fallback masks a bug the user would want to see (config parse error, IPC failure, file-not-found when the file is required). Fix: log a warning and either propagate or use a documented-recoverable default.
- **Medium** — the fallback hides a less-impactful failure but still loses information. Fix: add a log line; the default value can stay.
- **Low** — defensible exception: the function is documented as best-effort AND logs internally; OR the fallback is provably safe (e.g., test fixtures, optional fields where None has a documented semantic).

**Per-project audit:** scan source tree, classify each finding, append/update `{NAME} Rules/R05 Exceptions.md` with grade + one-line justification (same convention as the existing `MUX-R04 Exceptions.md`). On `/audit rules`, re-run the scan and fail if any High or Medium finding has appeared since the last audit without an exception.
