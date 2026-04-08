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
