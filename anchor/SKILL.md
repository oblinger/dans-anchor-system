---
name: anchor
description: >
  Anchor operations — the fundamental organizational unit. An anchor is a named folder
  that tools attach to. This skill provides scripts and actions for working with anchors:
  auditing docs against source, managing config, scanning for anchors, status tracking.
  See [[SKD Anchor]] for the full specification.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: false
---

# Anchor

Scripts and actions for operating on anchors. Not directly user-invocable — other skills
(audit, cab, code) delegate to these.

## Scripts

All scripts live in `~/.claude/skills/anchor/scripts/`.

| Script | Usage | Description |
|--------|-------|-------------|
| `audit-docs.py` | `python3 scripts/audit-docs.py <path> [--json] [--verbose]` | Compare source tree against Files.md, Dev dispatch, and module docs |
| `stat.py` | (future — currently in CAB) | Activity status tracking |
| `lint.py` | (future — currently in CAB/LINT) | Structural lint checks |
| `config.py` | (future — currently in CAB) | Manage .anchor/config.yaml |
| `scan.py` | (future — currently in CAB) | Discover all anchors in vault |

## Specification

The anchor specification lives in Skill Docket: [[SKD Anchor]]

Key properties: RID, Path, Type. Required files: `{RID}.md`, `.anchor/config.yaml`.
