---
name: role
description: >
  Agent role definitions and role management.
  Use with an action argument: /role pilot, /role pm, /role worker, /role setup.
  Each role defines identity, workflows, git protocol, and a POST-COMPACT RELOAD section.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Role — Agent Role Definitions

Define and manage agent roles. Each role specifies identity, workflows, and a compact-reload protocol.


| ACTIONS            | File               | Description                                              |
| ------------------ | ------------------ | -------------------------------------------------------- |
| `/role pilot`      | [[role-pilot]]     | Orchestrating agent — planning, implementation, dispatch |
| `/role pm`         | [[role-pm]]        | Project manager — reactive judgment, failure triage      |
| `/role worker`     | [[role-worker]]    | Task executor — spec → implement → PR → report          |
| `/role setup`      | [[role-setup]]     | Set up a new role or assign a role to a project          |


## How Roles Work

A **role** is a persistent identity that an agent carries across compactions. It defines what the agent does, how it communicates, and how it recovers after context is compressed.

### Automatic Reload Mechanism

A global SessionStart hook in `~/.claude/settings.json` fires on every session start (both startup and post-compact). It:

1. Walks up from the working directory looking for a `CLAUDE.md`
2. Greps for a backtick-wrapped path matching `.claude/skills/role/[^`]*`
3. Reads the `## POST-COMPACT RELOAD` section from that file
4. Injects it into the agent's context automatically

This means the agent never needs to manually re-read anything — the reload is automatic.

### Activating a Role

To give a project a role, add a **role header** as the first line of the project's `CLAUDE.md`:

```
You are the {ROLE} for the {PROJECT} project. Role: `~/.claude/skills/role/role-{role}.md`
```

This line does two things:
- **States the identity** — the agent reads it every session via CLAUDE.md
- **Carries the path** — the backtick-wrapped path is what the hook greps to find the role file

The backticks around the path are load-bearing. Without them, the hook can't find the file.

### Role Assignment

- **One role per agent session** — an agent is a Pilot, PM, or Worker, not multiple
- **Role defined by CLAUDE.md** — the role header tells the agent what it is
- **Roles are project-scoped** — the same human may have different agents in different roles across projects


## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory and execute its workflow
4. If no argument or unrecognized argument, show the actions table above
