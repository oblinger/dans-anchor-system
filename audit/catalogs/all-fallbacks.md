# Silent Fallbacks — Generic Reasoning

A silent fallback is code that handles a failure by substituting a default value or silently continuing, without logging, propagating, or otherwise making the failure visible. This masks bugs and makes debugging extremely difficult.

Language-specific patterns are in `{language}-fallbacks.md`. This file contains reasoning checks that apply to ALL languages.

## Agent Reasoning Checks

For each error-handling or default-value site, ask these questions:

**Config fallbacks hiding missing dependencies:**
```
config.get("database_url", "localhost")
settings.port || 8080
```
Ask: "If this value is missing, would the application behave incorrectly without the user knowing?"

**Guard clauses with silent early return:**
```
if !feature_enabled { return }
guard let data = data else { return [] }
```
Ask: "Would the caller want to know this condition was triggered?"

**Optional chaining hiding failures:**
```
user?.profile?.settings?.theme
```
Ask: "If this chain returns nil, can the developer tell which link broke?"

**Error logging without propagation:**
```
log.error("Failed to sync"); return Ok(())
eprintln!("Warning: ..."); // continues executing
```
Ask: "Does the caller know this operation partially failed?"

**Default constructors masking initialization failures:**
```
let config = Config::load().unwrap_or_default()
```
Ask: "Is the default actually correct, or does it mask a setup problem?"

## How to Report

Group by severity (High first, then Medium, then Low). Use this table format:

```
| Finding | Issue | Fix |
|---------|-------|-----|
| **1.** src/config.rs:42<br>`config fallback` | `database_url` defaults to "localhost" — wrong DB in production | Return error if DB URL missing |
| **2.** src/sync.rs:88<br>`error-log-continue` | Logs sync failure but returns Ok — caller thinks sync succeeded | Propagate the error to caller |
```

Severity guide:
- **High** — will cause wrong behavior in production without any indication
- **Medium** — might cause wrong behavior, depends on context
- **Low** — technically a silent fallback but the default is probably correct
