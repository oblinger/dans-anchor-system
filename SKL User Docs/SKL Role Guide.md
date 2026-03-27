---
description: How agent roles work — Pilot, PM, Worker, Setup, and the compact-reload mechanism
---

# SKL Role Guide (Skill: [[role/SKILL]])

The Role skill defines persistent identities that agents carry across context compactions. A role determines what the agent does, how it communicates, and how it recovers when context is compressed. The four roles are Pilot (orchestrating agent), PM (project manager with reactive judgment), Worker (task executor), and Setup (role assignment).

Roles solve the compaction problem. When Claude's context window fills up and older messages are compressed, the agent can lose its sense of identity and current task. The POST-COMPACT RELOAD mechanism automatically re-injects the role definition and current state after every compaction, so the agent picks up where it left off.

To assign a role to a project, add a role header as the first line of the project's `CLAUDE.md`. The backtick-wrapped path in that line is what the automatic reload hook uses to find the role file.

## Commands

| Command | Description |
|---------|-------------|
| `/role pilot` | Orchestrating agent — planning, implementation, dispatch |
| `/role pm` | Project manager — reactive judgment, failure triage |
| `/role worker` | Task executor — spec, implement, PR, report |
| `/role setup` | Set up a new role or assign a role to a project |

## Key Concepts

- **One role per agent** — An agent is a Pilot, PM, or Worker in a given session, not multiple roles at once
- **Role header** — First line of CLAUDE.md: `You are the {ROLE} for the {PROJECT} project. Role: \`~/.claude/skills/role/role-{role}.md\``
- **POST-COMPACT RELOAD** — Each role file has a section that gets automatically injected after context compaction. This is how the agent remembers what it is
- **Automatic reload** — A SessionStart hook in `~/.claude/settings.json` greps for the backtick-wrapped path and reads the reload section. No manual re-reading needed
- **Pilot** — The orchestrating role. Plans work, dispatches to workers, makes design decisions. Has a priority loop for deciding what to do next
- **PM** — Reactive judgment role. Triages failures, makes go/no-go calls, manages risk
- **Worker** — Pure executor. Receives a spec, implements it, creates a PR, reports back
- **Backticks are load-bearing** — The path in the role header must be wrapped in backticks or the reload hook cannot find it
