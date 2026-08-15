---
name: anchor
description: >
  Anchor operations — both a single anchor and the anchor system's machinery.
  Actions: /anchor scan (discover anchors), /anchor config (manage .anchor),
  /anchor docs-audit (docs vs source),
  /anchor install (one-time per-machine wiring of the CLI tools).
  Use when the user says: "scan for anchors", "anchor config", "install the anchor tools".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Anchor — the anchor toolkit
requires:: vault
subsystem:: [[DAS Anchor Design]] — the Anchor group's subsystem profile

The toolkit verb for anchor machinery. Overloaded by design (F234 Q1=A, 2026-07-14): actions pertain either to a *single anchor* (config, docs-audit) or to the *anchor system as a whole* (scan, install) — one umbrella covers both.

## Actions

| Usage | Runbook / script | Description |
|-------|------------------|-------------|
| `/anchor scan` | `scripts/cab-scan.py` | Discover all anchors in the vault, write the anchor index |
| `/anchor config` | `scripts/cab-config.py` | Manage an anchor's `.anchor` configuration |
| `/anchor docs-audit` | `scripts/audit-docs.py <path> [--json]` | Compare a source tree against Files.md, Dev dispatch, and module docs |
| `/anchor install` | [[anchor-install]] | One-time per-machine wiring of the anchor CLI tools onto `$PATH` |

(`/install` was folded in as the `install` action per [[F234 — Subsystem profiles — joint architecture overview per group (Phoenix prerequisite)|F234]] Q1=A, 2026-07-14.)

## Scripts

All scripts live in `~/.claude/skills/anchor/scripts/`. Script filenames retain their historical `cab-` prefixes; the actions above are the stable interface.

## Specification

The anchor specification lives at [[DAS Anchor]] (facet) with the marker-file details in [[DAS Dot Anchor]]. Key properties: slug, path, traits. Required files: `{slug}.md`, `.anchor`.
