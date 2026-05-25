---
name: ob-skills
description: Internal helper — reads ~/.claude/ob-skills.md for per-user skill configuration parameters. Not user-invocable; consumed by other skills via the `ob-skills config` CLI.
user_invocable: false
---

# OBskill

The OBskill folder hosts the **ob-skills configuration mechanism** for the user's skill suite. Not a user-facing skill — its job is to be the canonical reader of `~/.claude/ob-skills.md`.

Feature design: [[F072 — Skills config file (~_.claude_skills.md)]]. Companion to [[F071 — Standard skill-data location convention]].

## Contents

- **`scripts/ob-skills config`** — a small bash script that reads `~/.claude/ob-skills.md` for `<key> :: <value>` parameter lines. Skills shell out to it from their runbooks; not invoked directly by users.

## Usage from another skill's SKILL.md

```bash
DATA_ROOT="$(~/.claude/skills/ob-skills/scripts/ob-skills config skill_data.root --default "$HOME/ob/kmr/SYS/ob-skills")"
ALLOWLIST="$DATA_ROOT/<skill-name>/<filename>.md"
```

The script's read order:
1. The config file (`~/.claude/ob-skills.md` or `$OB_SKILLS_CONFIG`).
2. The caller's `--default <value>` fallback.
3. Empty string if neither matches.

Skills never fail for missing config — the `--default` value covers the bootstrap case.

## Why it lives in the skills folder

Per [[SKA System Design]] § "Where helper scripts live": helper scripts live inside the skills folder so every machine running these skills finds them at the same path. Skills locate this script via the hardcoded path `~/.claude/skills/ob-skills/scripts/ob-skills config` — one path, like the config file itself.
