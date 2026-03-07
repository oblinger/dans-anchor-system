# Claude Code Skills

A collection of reusable skill modules for [Claude Code](https://claude.ai/code). Each skill defines workflows, conventions, and domain knowledge that Claude Code agents can invoke during interactive sessions.

Skills extend what an AI coding agent can do — from structured development workflows and markdown formatting to product research, Google Workspace integration, and multi-agent role management.


## How Skills Work

Each skill lives in its own folder with a `SKILL.md` entry point. When a user types `/skill-name action` (e.g., `/dev plan`, `/research dig`), Claude Code reads the corresponding action file and executes the workflow defined there.

Skills are:
- **Declarative** — written in markdown, not code. The agent interprets the workflow instructions.
- **Composable** — skills reference each other (e.g., `/dev publish` uses markdown formatting conventions from `/md`).
- **Stateless** — no runtime dependencies. Everything the agent needs is in the skill files.


## Skills

| Skill | Description | Actions |
|-------|-------------|---------|
| **[CAB](CAB/SKILL.md)** | Common Anchor Blueprint — create, validate, and manage structured folder systems | `create`, `tidy`, `move`, `migrate`, `pr-flow`, `pilot-flow`, `tlc-scan` |
| **[Dev](dev/SKILL.md)** | Development workflow — planning, execution, setup, and replanning | `plan`, `execute`, `replan`, `setup`, `forge`, `publish` |
| **[Edit](edit/SKILL.md)** | Visual editing — diagrams, mockups, and visual content | `excalidraw` |
| **[Google](google/SKILL.md)** | Google Workspace — Sheets and Slides via CLI | `sheets`, `slides` |
| **[MD](md/SKILL.md)** | Markdown formatting — heading spacing, file trees, TOCs, dispatch tables | `file-tree`, `toc` |
| **[Product](product/SKILL.md)** | Product research and purchasing — hunt, compare, buy | `hunt`, `find`, `buy`, `reorder` |
| **[Research](research/SKILL.md)** | Investigation and synthesis — entity dossiers and topic surveys | `dig`, `survey` |
| **[Role](role/SKILL.md)** | Agent role definitions — persistent identity across sessions | `pilot`, `pm`, `worker`, `setup` |


## Folder Structure

```
skills/
├── README.md              This file
├── CAB/                   Common Anchor Blueprint
│   ├── SKILL.md           Entry point + dispatch table
│   ├── cab-setup.md       Action: create new anchor
│   ├── cab-tidy.md        Action: validate structure
│   ├── cab-types/         Anchor type specifications
│   ├── cab-parts/         Part format specs + reference examples
│   └── cab-rules/         Convention rules
├── dev/                   Development workflow
│   ├── SKILL.md
│   ├── dev-plan.md        Action: 6-step planning pipeline
│   ├── dev-execute.md     Action: execution priority loop
│   ├── dev-forge.md       Action: rebuild + restart cycle
│   ├── dev-publish.md     Action: publish to website
│   └── dev-*.md           Other actions + topic references
├── edit/                  Visual editing
├── google/                Google Workspace integration
├── md/                    Markdown formatting
│   ├── SKILL.md
│   ├── md-file-tree.md    4 file tree formats
│   ├── md-toc.md          TOC conventions
│   └── md-toc.py          TOC auto-generation script
├── product/               Product research + purchasing
├── research/              Investigation + synthesis
│   ├── SKILL.md
│   ├── research-dig.md    Entity dossier workflow
│   └── research-survey.md Topic landscape workflow
└── role/                  Agent role definitions
    ├── SKILL.md
    ├── role-pilot.md      Orchestrator role
    ├── role-pm.md         Project manager role
    └── role-worker.md     Task executor role
```


## Creating a New Skill

1. Create a folder under `skills/` named after the skill
2. Add `SKILL.md` with YAML frontmatter (`name`, `description`, `tools`, `user_invocable: true`)
3. Add action files (`{skill}-{action}.md`) with workflow instructions
4. Register the skill in `SKILL.md`'s dispatch table

### SKILL.md Format

```yaml
---
name: myskill
description: >
  One-line description shown in the skills list.
  Use with an action argument: /myskill do-thing.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---
```

### Action File Format

Each action file is a markdown document with:
- A heading describing the action
- Prerequisites or context needed
- Step-by-step workflow the agent follows
- Examples or reference patterns


## License

MIT License. See [LICENSE](LICENSE) for details.
