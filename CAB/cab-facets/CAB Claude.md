---
description: CLAUDE.md agent configuration
---
# CAB Claude

**Location:** `CLAUDE.md`


The `CLAUDE.md` file configures Claude Code behavior when working inside an anchor folder. It is optional — only needed when the anchor will be used with Claude Code.

**Working example:** `~/.claude/skills/CAE/CLAUDE.md` — CLAUDE.md.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

You are the Pilot for the CAE example project. Role: `~/.claude/skills/role/role-pilot.md`
\# CLAUDE.md

\## Mission

You are the CAE developer agent. Your job is to implement, test, and maintain the cae-example CLI tool.

\## Working Directory

You are rooted in `CAE example/`. The code repo is reached via the `code:` key in `.anchor` (which may point inside this folder or elsewhere).

\## Key Files

- `CAE.md` — Anchor page, navigation hub
- `CAE Docs/CAE Plan/CAE PRD.md` — Product requirements
- `CAE Docs/CAE Plan/CAE Roadmap.md` — Milestone plan
- `CAE Docs/CAE Plan/CAE Files.md` — File tree with descriptions
- `Code/src/taskrunner/scheduler.py` — Core scheduling engine

\## Commands

```bash
ha -p CAE                              # Find anchor path
cd Code && python -m pytest            # Run tests
cd Code && python -m taskrunner --help  # CLI help
```

\## Formatting Rules

Follow CAB markdown conventions. H1/H2 get 3 blank lines before, 1 after.

---



# Format Specification

## Location

`CLAUDE.md` sits at the anchor folder root (alongside `{NAME}.md`).

## Contents

A typical `CLAUDE.md` includes:

- **Mission statement** — what the agent's job is in this folder
- **Working directory** — confirms the root context
- **Key files** — important files and their purposes
- **Architecture** — file tree showing the folder structure
- **Commands** — shell commands relevant to the project
- **Formatting rules** — project-specific conventions
- **Cross-reference integrity** — what to check when making changes

## Agentic Project Header

When an anchor is used as an agentic project (multi-agent workflow with SKD), add a pilot role declaration as the first lines of `CLAUDE.md`:

```
You are the Pilot for the {PROJECT} project. Role: `~/.claude/skills/role/role-pilot.md`
```

This ensures the Claude session running in that folder adopts the Pilot role on startup and after context compaction. Only add this header when the anchor will actually be driven by agents — it is not part of the default template.