# RULESET R-ob-state-mgt
include::
description:: Ob's opinionated take on state management — centralize config and state behind a single data singleton, and refuse to hardcode values that could vary. Not universal (other architectures use repository pattern, CQRS, event sourcing, functional state passing); this set captures Dan's specific approach.

### RULE R-ob-state-mgt-01 — Config access through the data singleton (checked)

All configuration reads and writes go through the centralized config/settings object. No component reads config from environment variables, files, or command-line args directly. No component writes config except through the singleton's save operation.

**Why:** scattered config access produces inconsistent behavior (one path reads `XDG_CONFIG_HOME`, another hardcodes `~/.config/foo`), invisible coupling (a refactor that moves a config file breaks N grepable call sites), and untestable code (every reader of `env::var(...)` needs its own mock). The singleton centralizes load semantics, applies validation once, and lets tests inject a populated singleton instead of stubbing the OS environment.

**Check pattern:** search for `env::var`, `std::env`, `process.env`, `os.environ`, and file reads of `.yaml` / `.json` / `.toml` config files outside the singleton's load function. Each is a violation.

### RULE R-ob-state-mgt-02 — State access through the data singleton (checked)

All application state reads and writes go through the centralized state object. No component maintains its own shadow copy of shared state. No component reads or writes state files except through the singleton.

**Why:** shadow state diverges. The moment two places hold "current layout" or "current settings" independently, they will get out of sync — and the bug presents as a state-doesn't-stick failure that's hard to trace because two writers exist. Centralizing through one object makes the writer visible in stack traces and tests.

**Check pattern:** search for components that store values also found in the state singleton. Search for direct reads/writes to state files outside the singleton's load/save functions. Each is a violation.

### RULE R-ob-state-mgt-03 — No hardcoded values that belong in config (checked)

Values that a user might want to change, or that differ between environments, are in the config system. Hardcoded constants are only acceptable for values intrinsic to the algorithm (mathematical constants, protocol-defined values, sentinels with no degrees of freedom).

**Why:** hardcoded "magic numbers" are the most common source of "I wish I could change this" friction. By the time a user reports they want timeout X different from the hardcoded 30s, the change is a code edit instead of a config tweak. Putting tunable values in config from the start costs almost nothing and pays back the first time someone wants to vary one.

**Check pattern:** search for numeric literals, string literals, and timeout values in source code. For each, ask "would someone ever want this to be different?" If yes, it belongs in config. Defensible hardcodes (mathematical constants, fixed protocol values like `\r\n`, sentinel strings the protocol mandates) pass.
