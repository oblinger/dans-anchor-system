# Silent Fallbacks — Rust

Rust-specific silent fallback patterns. Semgrep catches the mechanical ones; agent reasoning catches the rest.

## Semgrep Patterns (mechanical — already caught by rust rules in all-fallbacks.yaml)

- `unwrap_or_default()` — silently uses Default::default() on error
- `unwrap_or(...)` — silently uses a hardcoded value on error
- `.ok()` — converts Result to Option, discarding the error
- `let _ = ...` — explicitly ignoring a Result
- `match ... { Err(_) => {} }` — empty error arm

## Agent Reasoning (Rust-specific)

**`if let Ok(x) = ... { }` without else:**
The Err case is silently ignored. Check if the Err contains information the caller needs.

**`unwrap_or_else(|_| default)` with ignored error:**
The closure ignores the error value. If the error has context (e.g., IO error with path), it's lost.

**`.unwrap_or(vec![])` / `.unwrap_or(String::new())`:**
Returns empty collection on error. The caller can't distinguish "no results" from "query failed."

**`Option::unwrap_or_default()` on config values:**
```rust
let port = config.port.unwrap_or(8080);
```
Is 8080 always correct, or does it mask a missing config?

**`map_err(|_| ...)` dropping the original error:**
```rust
file.read().map_err(|_| MyError::ReadFailed)
```
The original IO error (permission denied? file not found?) is lost.

**`impl Default` that hides construction failures:**
If `Default::default()` is used as a fallback for a type that should require initialization parameters, the default may be silently wrong.
