# Fix: Claude Permissions

## Known Bug: .claude/ Protected Directory (v2.1.79+)

Writes to `~/.claude/` ALWAYS prompt for permission due to a confirmed bug in Claude Code. The `.claude/` directory protection is hardcoded and runs **before** permission rules are evaluated. The documentation says `.claude/skills/` should be exempt, but the code doesn't implement the exemption.

**No settings change can fix this.** `bypassPermissions`, `--dangerously-skip-permissions`, and path-specific allow rules are all correct but never evaluated — the protected path check fires first.

### Workaround: Write to the real path, not the symlink

Skills live at the real path:
```
/Users/oblinger/ob/kmr/SYS/Bespoke/Skill Agent/skills/
```

They are symlinked to `~/.claude/skills/`. When editing skill files, use the real path to avoid the `.claude/` protection check.

---

## Settings.local.json Accumulation

When agents approve specific commands, Claude Code adds them to the project's `.claude/settings.local.json`. This creates a narrow allow list that **overrides** the global `Bash(*)` permission.

### Runbook

#### 1. Find all project-level settings files

```bash
find ~/ob -name "settings.local.json" -path "*/.claude/*" 2>/dev/null
```

#### 2. Clean them all

```bash
find ~/ob -name "settings.local.json" -path "*/.claude/*" -exec sh -c 'echo "{}" > "$1"' _ {} \;
```

#### 3. Verify global settings are correct

Read `~/.claude/settings.json` and confirm:
- `permissions.allow` includes `Bash(*)`
- `permissions.defaultMode` is `bypassPermissions` (NOT `dontAsk` — that auto-denies unlisted tools)
- `skipDangerousModePermissionPrompt` is `true`

#### 4. Report

---

**>>> RESTART CLAUDE CODE SESSION TO TAKE EFFECT <<<**

**>>> RESTART CLAUDE CODE SESSION TO TAKE EFFECT <<<**

**>>> RESTART CLAUDE CODE SESSION TO TAKE EFFECT <<<**

---
