---
description: Rules for applications using ~/.config/ (XDG Base Directory) conventions
applies-when: Project stores configuration, state, or cache in ~/.config/, ~/.local/, or ~/.cache/
---

# XDG Config — Configuration Directory Rules

Standard rules for applications that follow XDG Base Directory conventions for configuration, state, and cache storage.

### R-XDG01 — Use XDG Base Directories
RULE: Configuration goes in `~/.config/<app>/`, state in `~/.local/state/<app>/`, cache in `~/.cache/<app>/`. Never store config directly in `~/` as a dotfile.

### R-XDG02 — Config File is YAML
RULE: The primary configuration file must be `config.yaml`. Not JSON, not TOML, not INI. YAML is the standard across the skills system.

### R-XDG03 — State File is Separate from Config
RULE: Runtime state (last-run timestamps, active project lists, counters) goes in a `state.yaml` file, not in `config.yaml`. Config is what the user sets; state is what the system tracks.

### R-XDG04 — Config Has Documented Defaults
RULE: Every config key must have a default value in the code. The config file only needs to contain values that differ from defaults. Missing keys are never errors.

### R-XDG05 — Paths in Config Are Expandable
RULE: All path values in config must support `~` expansion and relative paths (resolved relative to a documented base). Absolute paths are also accepted. The code must call `os.path.expanduser()` on every path read from config.

### R-XDG06 — No Secrets in Config
RULE: Credentials, API keys, and tokens must never appear in config.yaml. Use a separate credentials file with restricted permissions, or reference an environment variable. Config files may be committed or shared; secrets must not leak.

### R-XDG07 — Config is Human-Editable
RULE: The config file must be readable and editable by hand in a text editor. No binary formats, no encoded values, no machine-generated IDs that humans can't interpret. Comments are encouraged.

### R-XDG08 — Create Directories on First Use
RULE: The application must create its `~/.config/<app>/` directory (and subdirectories) on first use if they don't exist. Never fail because a directory is missing. Use `os.makedirs(path, exist_ok=True)`.

### R-XDG09 — Cache is Deletable
RULE: Everything in `~/.cache/<app>/` must be safely deletable at any time. The application must regenerate cached data on demand. Deleting the cache directory must never cause data loss or require reconfiguration.

### R-XDG10 — Config Changes Take Effect Without Restart
RULE: The application should re-read config.yaml when needed rather than caching values at startup. If caching is necessary for performance, provide a reload mechanism.

### R-XDG11 — Respect XDG Environment Variables
RULE: If `XDG_CONFIG_HOME` is set, use it instead of `~/.config`. Similarly for `XDG_STATE_HOME`, `XDG_CACHE_HOME`, and `XDG_DATA_HOME`. Fall back to the standard defaults only when the environment variable is not set.
