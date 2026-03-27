# Dan's Skills

Personal skills for AI coding agents. Many are fairly general-purpose — please enjoy.

*(Designed for [Claude Code](https://claude.ai/code) but should work well with other AI agents that support the SKILL.md format.)*


## Skills

| Skill | Description |
|-------|-------------|
| **[CAB](CAB/SKILL.md)** | Common Anchor Blueprint — structured folder systems with typed anchors, dispatch tables, and lint validation |
| **[Dev](dev/SKILL.md)** | Full development lifecycle — 9 stages from planning through release, with testing, debugging, and multi-agent orchestration |
| **[Ctrl](ctrl/SKILL.md)** | Local environment control — browser automation, persistent tmux sessions, system interaction |
| **[IO](io/SKILL.md)** | External system I/O — Google Sheets/Slides/Drive, Dropbox, Notion, file sync via rclone |
| **[Edit](edit/SKILL.md)** | Visual editing — Excalidraw diagrams with SVG export and Obsidian embedding |
| **[MD](md/SKILL.md)** | Markdown formatting — file trees, TOC, dispatch tables, cards, track changes |
| **[Product](product/SKILL.md)** | Product research and purchasing — hunt, find, buy, reorder |
| **[Research](research/SKILL.md)** | Investigation and synthesis — entity dossiers, topic surveys, book summaries |
| **[Role](role/SKILL.md)** | Agent role definitions — pilot, pm, worker with persistent identity across sessions |
| **[Rule](rule/SKILL.md)** | Project rule management — define semantic rules, check code against them, triage exceptions, and drive fixes |


## Dev Skill — Development Lifecycle

The largest skill. 40+ actions organized into a numbered lifecycle:

| Stage | Name | Actions |
|-------|------|---------|
| 1x | Plan | anchor, prd, research, ux, system, plan-audit |
| 2x | Architect | modules, system-design, test-plan, roadmap, arch-audit |
| 3x | Implement | spec, code, test, review, verify, commit |
| 4x | Release | changelog, version, package, publish, ship |
| | ***Capabilities*** | |
| 5x | Test | assess, scaffold, write-tests, verify |
| 6x | Verify | rewire, lint, fix |
| 7x | Adapt | open-questions, replan |
| 8x | Tactical | forge, debug, refactor |
| 9x | Orchestrate | workers, worktrees, pr-flow, merge |


## CAB Skill — Common Anchor Blueprint

A system for organizing projects into typed anchor folders with consistent structure, dispatch tables for navigation, module documentation that tracks source code, and a lint tool that validates everything.

| Action | What it does |
|--------|-------------|
| `/cab setup` | Create a new anchor with full doc skeleton |
| `/cab lint` | Validate structure and module docs against source code |
| `/cab tidy` | Fix structural issues |
| `/cab yore` | Archive to Yore |
| `/cab move` | Rename/relocate an anchor |
| `/cab migrate` | Convert between anchor types |


## How Skills Work

Each skill lives in its own folder with a `SKILL.md` entry point. When a user types `/skill-name action` (e.g., `/code plan`, `/research dig`), the agent reads the corresponding action file and executes the workflow.

Skills are:
- **Declarative** — written in markdown, not code. The agent interprets the workflow instructions.
- **Composable** — skills reference each other (e.g., `/code publish` uses `/md` formatting conventions).
- **Stateless** — no runtime dependencies. Everything the agent needs is in the skill files.


## Creating a New Skill

1. Create a folder under `skills/` named after the skill
2. Add `SKILL.md` with YAML frontmatter (`name`, `description`, `tools`, `user_invocable: true`)
3. Add action files (`{skill}-{action}.md`) with workflow instructions
4. Register the skill in `SKILL.md`'s dispatch table

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


## License

MIT License. See [LICENSE](LICENSE) for details.
