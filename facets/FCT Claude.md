---
description: CLAUDE.md agent configuration
---
# CAB Claude

Facet spec for the optional `CLAUDE.md` file at an anchor's root that configures Claude Code behavior when the agent is rooted in that anchor.

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

## F060 — exempt

`CLAUDE.md` is a Claude Code configuration file consumed by the harness, not a CAB facet doc inside the anchor's documentation tree. The F060 dispatch-table placeholder rule does not apply — the file's first lines are reserved for the optional Pilot role declaration and the agent mission, not a dispatch table.

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

# BRIEF

- **This file is the facet spec for `CLAUDE.md`** — it defines the shape, location, and contents of the anchor-root Claude Code config file. It is NOT itself a `CLAUDE.md` template; the body holds a reference example and the format rules.
- **Inclusion test for new content** — only add material here if it constrains the shape, location, or contents of `CLAUDE.md` as a CAB facet across all anchors. Per-anchor mission text, role declarations, or commands belong in the actual `CLAUDE.md` files inside each anchor, not here.
- **Do NOT inline project-wide agent policy** (commit conventions, trigger words, `ctrl`/`gsa`/`exp` usage) — that lives in `~/.claude/CLAUDE.md` (global) and is cited from anchor `CLAUDE.md` files, not duplicated into this spec.
- **The F060 exemption is load-bearing** — `CLAUDE.md` does NOT carry the standard CAB dispatch-table placeholder because it is consumed by the Claude Code harness, not by anchor-doc readers. Do not "fix" the missing dispatch table by adding the F060 rule here.
- **Reference Example uses escaped headings** (`\# CLAUDE.md`, `\## Mission`) so the example's H1/H2s don't collide with this facet spec's outline — preserve the backslash escapes when editing the example block.
- **Pilot role header is opt-in, not default** — keep the "only add when driven by agents" guard intact; agentic-project anchors get the header, plain-content anchors do not.
- **Cited by:** SKD Anchor (lists `CLAUDE.md` as an optional facet), [[Skill Agent]] pilot setup, any anchor adopting agentic-project workflow. When the format changes, audit those citations.