# Multi-Path — Redundant Code Paths

Two or more implementations of the same behavior exist in the codebase. This creates maintenance burden, behavior divergence, and makes it unclear which path is "correct."

Multi-path is almost entirely agent reasoning — Semgrep can't detect semantic duplication.

## Agent Reasoning

### Parallel Implementations
Look for two functions or methods that do the same thing with different approaches:
- `send_via_keystroke()` and `send_via_pasteboard()` — are both needed, or is one legacy?
- `load_config_json()` and `load_config_yaml()` — does the system actually support both formats?
- `parse_v1()` and `parse_v2()` — is v1 still called anywhere?

Ask: "Do both paths serve a current purpose, or is one a leftover from before the other existed?"

### Branching Where There Should Be One Path
Look for conditional logic that creates two distinct behavior modes when one would suffice:
```
if use_new_engine {
    new_engine.start()
} else {
    old_engine.start()  // Is this branch ever taken?
}
```

Ask: "Is the else branch reachable in production? If not, delete it."

### Duplicate Logic Across Modules
Look for the same algorithm or business logic implemented in two places:
- Two modules both computing layout positions
- Two functions both validating user input with slightly different rules
- Copy-pasted error handling blocks that diverged over time

Ask: "If I fix a bug in one copy, would the other copy also need the fix? If yes, consolidate."

### Configuration vs Code Duplication
Look for values that appear both as configuration and as hardcoded constants:
- `DEFAULT_PORT = 8080` in code AND `port: 8080` in config
- Timeout values defined in multiple places
- Feature flag defaults that duplicate config defaults

Ask: "Where is the single source of truth for this value?"

### Protocol/Interface with Multiple Conformances
Look for interfaces where two implementations exist but only one is used:
- A protocol with a "real" and "mock" implementation where the mock is used in production too
- An abstract class with two subclasses where one is dead
- A strategy pattern where one strategy is never selected

Ask: "Are all implementations actively used? Which ones can be removed?"

### Platform-Conditional Code That's Not Conditional
Look for `#[cfg(target_os)]` or `#if os(macOS)` blocks where only one platform is actually supported:
- macOS-only app with `#[cfg(not(target_os = "macos"))]` stubs that compile but never run
- Cross-platform abstractions for a single-platform project

Ask: "Does this project actually run on multiple platforms? If not, remove the dead platform branches."

## How to Report

| Finding | Issue | Fix |
|---------|-------|-----|
| **1.** src/send.rs + src/paste.rs<br>`parallel-impl` | Both `send_keystroke()` and `send_pasteboard()` send text to target — `send_pasteboard` is legacy, only used when `USE_PASTE=true` which is never set | Delete `send_pasteboard()` and `USE_PASTE` flag |
| **2.** src/config.rs:30 + src/main.rs:15<br>`duplicate-constant` | `DEFAULT_TIMEOUT` defined as 30s in config.rs and hardcoded as 30000ms in main.rs | Use `config::DEFAULT_TIMEOUT` in both places |
| **3.** src/engine.rs:100-150<br>`dead-branch` | `if use_legacy_engine { ... }` — `use_legacy_engine` is always `false` since v2.0 | Delete the legacy branch and the flag |

## Severity Guide

- **High** — two implementations that have already diverged in behavior (bugs hiding in the difference)
- **Medium** — redundant code that works but creates maintenance burden
- **Low** — platform stubs or defensive code that's harmless but adds noise
