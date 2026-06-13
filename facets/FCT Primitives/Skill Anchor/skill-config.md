---
description: skill-config — facet defining the per-machine mutable configuration of a Skill Anchor. Lives at ~/.config/ob-skills/<skill-name>/ per F080. YAML format. Defaults hardcoded in the skill; overrides centralized here.
applies-when-trait: Skill Anchor
location: ~/.config/ob-skills/<skill-name>/
---

# CAB skill-config

The skill-config facet specifies *where a Skill Anchor's per-machine mutable configuration lives — `~/.config/ob-skills/<skill-name>/config.yaml`, plus optional `~/.config/ob-skills/<skill-name>/data/` for accumulated user state.* What distinguishes skill-config from ad-hoc config files:

- **Two-namespace split per F080** — skill assets (canonical, version-controlled, agent-read at runtime) live under `~/.claude/skills/<name>/`; skill config + accumulated user data (mutable, per-machine) live under `~/.config/ob-skills/<name>/`. Never mix them.
- **YAML format** — single `config.yaml` at the namespace root; subdirectories under `data/` for accumulated content.
- **Defaults hardcoded in the skill; overrides centralized here** — every skill knows its defaults; users override via `~/.config/ob-skills/<name>/config.yaml`. No defaults file shipped with the skill.
- **`ob-skills` CLI is the canonical accessor** — per F080, scripts use `ob-skills config get <name> <key>` and `ob-skills path <name>` instead of hardcoding paths.
- **Per-machine, not synced** — `~/.config/` is not part of the kmr vault; settings stay local.

This is a CAB facet of the Skill trait. The config namespace lives outside both the anchor's filesystem folder AND the skill runtime folder — at the per-machine `~/.config/` location.


## Layout

```
~/.config/ob-skills/<skill-name>/
├── config.yaml          ← user-set configuration (overrides skill defaults)
└── data/                ← optional — accumulated user state (cache, history, etc.)
    ├── <category>/
    └── ...
```


## Conventions

- **YAML for config.yaml** — simple key/value structure; nested dicts when grouping by sub-feature.
- **Defaults hardcoded** — the skill's SKILL.md or scripts know their defaults. Reading a missing config key returns the default, not an error.
- **`ob-skills` CLI usage** — `ob-skills config get <skill> <key>`, `ob-skills config set <skill> <key> <value>`, `ob-skills path <skill>` (returns the config root).
- **No nested config files** — one config.yaml per skill; sub-config goes under nested YAML keys, not separate files.
- **Data folder is freeform** — `data/` subdirectories are skill-defined; agents browse them via `ob-skills path` + filesystem walks.


## Reference instances

- `~/.config/ob-skills/global.yaml` — the F080 global config (vault_root, etc.).
- (per-skill instances populate as skills opt into F080.)


## Conformance

A Skill Anchor carries this facet when it has any user-configurable behavior. Skills with no configuration (e.g., pure disciplines) MAY omit. The `ob-skills` CLI provides namespace creation on first access — skills don't need to pre-create their config folder.


## Migration note (F116)

Reserved by the prior `skill-trait/` planning (`SKA skill-trait config` was a planned entry citing F080). F116 v1 ships this as the populated facet spec, codifying the F080 namespace conventions.
