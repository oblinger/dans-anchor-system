---
description: CLAUDE.md agent configuration
---

# DAS Claude
Facet spec for the optional `CLAUDE.md` file at an anchor's root that configures Claude Code behavior when the agent is rooted in that anchor.

| -[[DAS Claude]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Claude](hook://p/DAS%20Claude) |
| --- | --- |
| Related | [[DAS Anchor Page]],  [[DAS Dot Anchor]],  [[DAS Aspects]],  [[DAS Facet]],   |
| Examples | [[CAE CLAUDE\|agentic-project form]],  [[SYS CLAUDE\|plain-content form]],   |
| Rules | [[R-fct-claude]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**Cardinality:** one per anchor — at most one `CLAUDE.md` sits at the anchor root.

**TLDR** — This facet governs the optional `CLAUDE.md` config file at an anchor root. It is exempt from the F060 dispatch-table rule (the harness, not anchor readers, consumes it). Two usage tiers: plain-content anchors get only a mission/commands section; agentic-project anchors add a Pilot role header as the first line.

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

`CLAUDE.md` sits at the anchor folder root (alongside `{slug}.md`).

## F060 — exempt

`CLAUDE.md` is a Claude Code configuration file consumed by the harness, not a DAS facet doc inside the anchor's documentation tree. The F060 dispatch-table placeholder rule does not apply — the file's first lines are reserved for the optional Pilot role declaration and the agent mission, not a dispatch table.

## Contents

A typical `CLAUDE.md` includes:

- **Mission statement** — what the agent's job is in this folder
- **Working directory** — confirms the root context
- **Key files** — important files and their purposes
- **Architecture** — file tree showing the folder structure
- **Commands** — shell commands relevant to the project
- **Formatting rules** — project-specific conventions
- **Cross-reference integrity** — what to check when making changes

Project-wide agent policy (commit conventions, trigger words, shared tool usage) is not duplicated into an anchor's `CLAUDE.md` — it lives in the global `~/.claude/CLAUDE.md` and is cited from anchor `CLAUDE.md` files where relevant.

## Agentic Project Header

When an anchor is used as an agentic project (multi-agent workflow with SKD), add a pilot role declaration as the first lines of `CLAUDE.md`:

```
You are the Pilot for the {PROJECT} project. Role: `~/.claude/skills/role/role-pilot.md`
```

This ensures the Claude session running in that folder adopts the Pilot role on startup and after context compaction. Only add this header when the anchor will actually be driven by agents — it is not part of the default template.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. This file is the facet spec for `CLAUDE.md`, not itself a `CLAUDE.md` template; the normative spec is the body above.)*

- **Inclusion test** — add material only if it constrains the shape, location, or contents of `CLAUDE.md` as a DAS facet across all anchors; per-anchor mission text, role declarations, or commands belong in each anchor's own `CLAUDE.md`, and project-wide agent policy stays in the global `~/.claude/CLAUDE.md` (see § Contents), not in this spec.
- **Don't regress the F060 exemption or the opt-in Pilot guard** — `CLAUDE.md` intentionally carries no dispatch table (R-fct-claude-04); the "only add the Pilot header when driven by agents" guard stays intact.
- **Reference Example headings are escaped** (`\# CLAUDE.md`, `\## Mission`) so they don't collide with this spec's outline — preserve the backslash escapes when editing the example block.
- **Cited by:** SKD Anchor (lists `CLAUDE.md` as an optional facet), [[SKA|Skill Agent]] pilot setup, any anchor adopting agentic-project workflow — audit those citations when the format changes.
