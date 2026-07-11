# Dan's Anchor System

Dan's Anchor System (DAS) is a structured system for organizing the documents, projects, and knowledge that an AI coding agent like [Claude Code](https://claude.ai/code) works with. It gives every project a predictable shape, so an agent can navigate, plan, and maintain it without re-learning the layout each time.

*(Designed for Claude Code but should work with any AI agent that supports the SKILL.md format.)*

The system is built from five kinds of parts:

- **Skills** are the `/`-invocable verbs (create, groom, mint, audit, and more), grouped by what they do.
- **Facets** are per-document structural specs (backlog, roadmap, PRD, architecture, and so on).
- **Disciplines** are cross-cutting conventions the agent reads (workflow, markdown, verification).
- **Traits** are the paradigms a project declares in its `.anchor` file (Code, Paper, Topic, Drive, Commit).
- **Rulesets** are the machine-checkable constraints that keep all of the above consistent.

## Skill groups

| Group | What it covers |
|-------|-------------|
| **Anchor** | Create, install, move, migrate, publish, and archive anchors |
| **Track** | Plan and groom work: backlog, questions, workflow state |
| **Drive** | Move work forward: feature, crank, mint, finalize, land |
| **Dev** | Build software: architect, code, fix, PR flow |
| **Doc** | Author documents: markdown, diagrams, editing |
| **Hygiene** | Keep anchors healthy: audit, tidy, dedupe, rewire, maintain |
| **Search** | Research and purchasing: find, survey, compare, buy |
| **Utility** | Everyday helpers: cook, ctrl, exp, snip |

## How it works

Each skill lives in its own folder with a `SKILL.md` entry point. When a user types `/skill-name action` (for example `/feature`, `/groom`, `/audit`), the agent reads the corresponding action file and runs the workflow defined there.

The whole system is **declarative** (written in markdown, not code), **composable** (parts reference each other), and **auditable** (rulesets check that anchors conform).

## License

MIT License. See [LICENSE](LICENSE) for details.
