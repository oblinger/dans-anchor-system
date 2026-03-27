---
description: How to create and manage anchor folder structures using the Common Anchor Blueprint
---

# SKL CAB Guide (Skill: [[CAB/SKILL]])

The Common Anchor Blueprint (CAB) defines a standard folder structure for organizing projects and content areas. Every anchor has a type that determines which files and folders it contains. The five types are Simple, Topic, Code, Paper, and Skill — each building on a common base with type-specific additions.

CAB is the structural backbone of the system. When you create a new project, CAB gives it a standardized shape. When you reorganize, CAB validates that nothing is broken. The specification lives in `~/.claude/skills/CAB/` with separate files for types, parts, and rules.

An anchor's identity comes from its RID (Root ID) — a short uppercase code like CLF or HA. The anchor page (a markdown file matching the folder name) is the hub. All other files and folders follow predictable naming conventions defined by the anchor type.

## Commands

| Command | Description |
|---------|-------------|
| `/cab create` | Create a new anchor — prompts for name, type, location |
| `/cab tidy` | Validate and correct an existing anchor's structure |
| `/cab move` | Move an anchor and update all path-dependent references |
| `/cab migrate` | Convert an anchor from one type to another |
| `/cab config` | Manage `.skl/config.yaml` — init, set, get, show paths |
| `/cab scan` | Discover all anchors and write registry to `~/.config/skl/anchors.yaml` |
| `/cab install` | Install CAB tools (stat, cab-config, cab-scan, cab-lint) into `~/bin` |
| `/cab lint` | Check structure, files, and links against CAB type rules |
| `/cab maintain` | Run standing maintenance orders (keep derived files in sync) |
| `/cab rid-scan` | Scan for new RIDs and sync the index |
| `/cab yore` | Archive folders/anchors to Yore with date-prefixed zip |

## Key Concepts

- **Anchor types** — Simple (flat folder), Topic (docs + backlog), Code (full dev setup with repo, tests, roadmap), Paper (research/writing), Skill (agent skill with SKILL.md entry point)
- **Parts** — Standard files that can appear in an anchor: Anchor Page, Docs, Backlog, Features, Roadmap, Module Docs, PRD, System Design, etc. Each part has a spec in `cab-parts/`
- **Rules** — Naming conventions, markdown formatting, docs conventions, repository structure. Each rule is in `cab-rules/`
- **Base file tree** — All types share a common base structure defined in CAB Base. Type specs add or remove from this base
- **`.skl/config.yaml`** — Per-anchor configuration file linking to docs, rules, and other paths
- **`ha -p "{name}"`** — Look up any anchor's path by RID or name
