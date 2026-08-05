---
name: anchor-system
description: Internal helper — reads + writes the unified `~/.config/anchor-system/` namespace (per F080) for skill configuration, runtime state, and accumulated data. Not user-invocable; consumed by other skills via the `anchor-system config` / `anchor-system path` CLI.
user_invocable: false
---

# anchor-system
requires:: vault

The `anchor-system` folder hosts the **unified skill namespace** that every skill in this suite reads + writes against. Not a user-facing skill — its job is to be the canonical entry point to `~/.config/anchor-system/`.

Per [[F080 — Skill config — unified namespace YAML]] (supersedes F072).

## The namespace

```
~/.config/anchor-system/
├── global.yaml                  # cross-skill preferences (vault_root, etc.)
├── <skill>/
│   ├── config.yaml              # skill's overrides for its hardcoded defaults
│   ├── data/                    # user-accumulated structured content
│   ├── state/                   # tool-managed runtime state
│   ├── cache/                   # ephemera (backup-skippable)
│   └── logs/                    # optional
└── <other-skill>/ …
```

Inside `<skill>/`, the skill picks its own internal layout. Simple skills (cook, snip) have just `config.yaml`. Complex skills (fleet) use multiple files + nested folders.

**Backup-friendly conventions** (per [[F080 — Skill config — unified namespace YAML|F080]] § 1):
- `cache/` subfolder anywhere → safe to delete; backup tools may skip
- `state/` → tool-managed runtime data; semi-durable
- `data/` → user-accumulated structured content

## Documented globals (in `global.yaml`)

Seeded on first run. Skills add new keys as they need them.

| Key | Default | What it is |
|---|---|---|
| `vault_root` | `~/ob/kmr` | Obsidian vault root. Audit / hygiene / link-uniqueness scripts walk this. Per [[SKA System Design]] § Per-user parameters. |
| `kmr_root` | `~/ob/kmr` | Synonym in practice; kept distinct in schema in case they diverge. |
| `skill_data_root` | `~/ob/kmr/SYS/anchor-system` | Default vault-side root for skill-owned persistent data (per F071). |
| `default_agent_mode` | `drive` | Default operating mode for new anchors. Per-anchor `.anchor` files override via `agent_modes:`. |
| `scratch_root` | (no hardcoded default — must be set in `global.yaml`; this user has it at `~/ob/kmr/SYS/Bureau/Scratch`) | Inside-vault anchor for skill working files the user may want to browse in Obsidian (viz/diagram drafts, intermediate exports, preview artifacts). Distinct from `cache/` (under `~/.config/anchor-system/<skill>/cache/` — hidden, backup-skippable). Skills typically scope further into a sub-folder named after themselves (e.g. `{scratch_root}/viz/`). |

## Read tier (high to low)

```
1. env var (ANCHOR_SYSTEM_<KEY> or ANCHOR_SYSTEM_<SKILL>_<KEY>)
2. ~/.config/anchor-system/<skill>/config.yaml (per-skill)
3. ~/.config/anchor-system/global.yaml          (cross-skill)
4. ~/.claude/anchor-system.md                   (legacy F072 — being retired)
5. --default <value>                        (caller's safe fallback)
```

Higher tiers override lower. Skills NEVER fail for missing config — `--default` is always safe.

## Usage from another skill's SKILL.md

```bash
# Read a global parameter
VAULT="$(~/.claude/skills/anchor-system/scripts/anchor-system config vault_root --default ~/ob/kmr)"

# Read a per-skill parameter
ALLOWLIST="$(~/.claude/skills/anchor-system/scripts/anchor-system config dupes allowlist --default "$DEFAULT_PATH")"

# Get + ensure a per-skill namespace path (creates dir if absent)
SKILL_DIR="$(~/.claude/skills/anchor-system/scripts/anchor-system path fleet)"
echo "remotes:" >> "$SKILL_DIR/remotes.yaml"
```

From Python, skip the bash wrapper and read YAML directly — it's two lines:

```python
import yaml
data = yaml.safe_load(open(Path.home() / ".config/anchor-system/global.yaml")) or {}
vault_root = data.get("vault_root", "~/ob/kmr")
```

## CLI surface

- **`anchor-system config <key> [--default <v>]`** — global read. Dotted keys traverse nested YAML maps. Falls back to F072 legacy file for backward compat with un-migrated keys.
- **`anchor-system config <skill> <key> [--default <v>]`** — per-skill read.
- **`anchor-system path <skill>`** — print + ensure the per-skill namespace path. Use to anchor write paths.
- **`anchor-system help`** — usage.

## Migration from F072

F072's `~/.claude/anchor-system.md` (custom `key :: value` markdown) is **read as a fallback** during migration, so existing consumer skills don't break. New writes always go to the YAML namespace.

To migrate a specific key:
1. Move the value from `~/.claude/anchor-system.md` into the right YAML file:
   - `skill_data.root` → `~/.config/anchor-system/global.yaml` `skill_data_root:`
   - `skill_data.per_skill.<skill>.<key>` → `~/.config/anchor-system/<skill>/config.yaml` `<key>:`
2. Delete the F072 line.
3. Verify with `anchor-system config <key> --default MISSING` — should print the new value, not MISSING.

When all keys are migrated and the F072 file is empty, delete it. The bash script will silently skip the missing file.

## Cross-references

- [[F080 — Skill config — unified namespace YAML]] — full design.
- [[F071 — Standard skill-data location convention]] — vault-side data root convention.
- [[F072 — Skills config file (~_.claude_skills.md)]] — superseded; read-fallback retained for migration window.
- [[SKA System Design]] § Per-user parameters — vault-wide-scope rule and the documented-globals table.
