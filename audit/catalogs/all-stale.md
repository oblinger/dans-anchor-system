# Stale — Dead Code, Legacy Remnants, Cleanup Debt

Code that should have been removed or updated. Every item here represents cognitive load for developers and potential confusion for agents.

## Semgrep-Detectable

### TODO/FIXME/HACK Comments
- `TODO` without a ticket reference or owner
- `FIXME` older than 30 days (check via `git blame`)
- `HACK` or `XXX` — temporary workarounds that became permanent

**Acceptable:** `// TODO(#123): implement retry logic` — linked to a ticket, specific
**Flagged:** `// TODO: fix this later` — no ticket, no context, no owner

### Commented-Out Code
- Blocks of 3+ lines that are commented out
- `#if 0` / `#endif` blocks (C/Rust cfg)
- Functions or methods entirely inside comments

### Dead Imports
- `use` / `import` statements not referenced in the file
- Wildcard imports (`use foo::*`) that could be narrowed

### Large Files
- Source files over 500 lines — may indicate a module that should be split

## Agent Reasoning

### Deprecated Functions Still Called
Look for patterns where a newer version exists alongside an older one:
- Functions with `_old`, `_legacy`, `_v1`, `_deprecated` suffixes
- Two functions with similar names doing similar things (`send_text` and `send_text_new`)
- Comments saying "deprecated" or "will be removed" on functions that are still called

Ask: "Is there a newer version of this? If so, why is the old one still here?"

### Dead Feature Flags
Look for boolean flags or config values that are always the same:
- `if USE_OLD_ENGINE { ... }` where `USE_OLD_ENGINE` is always false
- `cfg` attributes for features that are never enabled
- Environment variables checked but never set

Ask: "Is this flag ever toggled? If not, delete the dead branch."

### Orphan Files
Source files that exist but are not imported, included, or referenced anywhere:
- `.rs` files not listed in `mod.rs` or `lib.rs`
- `.swift` files not in the Xcode project
- `.py` files not imported by any other module

### Stale Constants and Config
- Constants defined but never referenced
- Config keys read but no code path uses the value
- Default values that were temporary but became permanent

## How to Report

| Finding | Issue | Fix |
|---------|-------|-----|
| **1.** src/old_sync.rs:1<br>`deprecated-function` | `sync_legacy()` still called from 3 places — `sync_v2()` exists | Replace 3 call sites with `sync_v2()`, delete `sync_legacy()` |
| **2.** src/main.rs:42<br>`stale-todo` | `// TODO: fix this` — no ticket, added 2025-06-12 | Create ticket or fix it; remove if no longer relevant |
| **3.** src/utils/old_helper.rs<br>`orphan-file` | Not imported anywhere — last modified 4 months ago | Delete or add to exclusions if intentionally kept |
