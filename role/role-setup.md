# role-setup — Set Up a New Role or Assign a Role to a Project

Configure an agent role for a project, or create a new role definition.


## Assigning an Existing Role to a Project

### Step 1: Add the Role Header

Add this as the **first line** of the project's `CLAUDE.md`:

```
You are the {ROLE} for the {PROJECT} project. Role: `~/.claude/skills/role/role-{role}.md`
```

Examples:
```
You are the Pilot for the ClaudiMux project. Role: `~/.claude/skills/role/role-pilot.md`
You are the Worker for the TSK project. Role: `~/.claude/skills/role/role-worker.md`
```

This line does two things:
- **States the identity** — the agent reads it every session via CLAUDE.md
- **Carries the path** — the backtick-wrapped path matching `.claude/skills/role/` is what the global SessionStart hook greps to find the role file and inject its POST-COMPACT RELOAD section

The backticks around the path are **load-bearing**. Without them, the automatic reload won't find the file.

### Step 2: Verify the Hook

The global `~/.claude/settings.json` has SessionStart hooks (both compact and startup) that automatically extract the role file path and inject the POST-COMPACT RELOAD section. No per-project configuration needed.

Verify:
```bash
cat ~/.claude/settings.json | grep -A5 "SessionStart"
```

### Step 3: Test

Run `/compact` in the project and verify the agent:
1. Knows its role identity
2. Has the key operating rules from the POST-COMPACT RELOAD section
3. Resumes work without any manual re-reading


## Creating a New Role

### Step 1: Create the Role File

Create `~/.claude/skills/role/role-{name}.md` following this structure:

```markdown
# role-{name} — {Name} Role Definition

## Role
One-paragraph description of what this role does.

## Workflows
How this role operates day-to-day.

## Commands
Key commands this role uses.

## POST-COMPACT RELOAD
Compressed briefing — everything the agent needs to resume after compaction.
Keep this section short (10-15 lines). It's re-read frequently.

Required fields:
- **Identity** — one line saying what you are
- **Key rules** — 3-5 most important operating principles
- **After /compact** — what to re-read and what commands to run to restore state
```

### Step 2: Register in SKILL.md

Add the new role to the Actions table in `/role` SKILL.md.

### Step 3: Update SKL.md

Add the role link to the Roles row in SKL.md.
