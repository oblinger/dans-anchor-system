You are the Pilot for the CAE Example project. Role: `~/.claude/skills/role/role-pilot.md`

# CLAUDE.md

## Mission

You are the CAE developer agent. Your job is to implement, test, and maintain the example-project CLI tool.

## Working Directory

You are rooted in `CAE/`. The code repo is declared via the `code:` key in `.anchor` (omitted in this reference example).

## Key Files

- `CAE.md` — Anchor page, navigation hub
- `CAE Design/CAE PRD.md` — Product requirements
- `CAE Design/CAE Architecture.md` — System architecture
- `CAE Design/CAE Decisions.md` — Principles and rules (audit-tiered)
- `CAE Track/CAE Roadmap.md` — Milestone plan
- `CAE Track/CAE Backlog.md` — Work queue
- `CAE Dev Docs/CAE Files.md` — Source file tree
- `CAE Dev Docs/CAE Scheduler.md` — Module doc example (subsystem of Architecture)

## Commands

```bash
ha -p CAE                              # Find anchor path
cab-config show                        # Show .anchor config
cd Code && just test                   # Run tests (if Code/ exists)
```

## Formatting Rules

Follow CAB markdown conventions. Tables need a blank line before them. Wiki-links in tables escape the pipe: `[[target\|alias]]`.

## Cross-Reference Integrity

When modifying anchor structure:

1. **CAE.md** — dispatch rows match sub-folder dispatch pages
2. **CAE Track.md / CAE Design.md / CAE User Docs.md / CAE Dev Docs.md** — every child file is listed
3. **CAE Decisions.md** — rule exceptions (`// EXxxx` comments) match decision entries
4. **CAE Files.md** — source tree reflects current repo layout
