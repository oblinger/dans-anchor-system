---
name: cab
description: DEPRECATED. CAB is now a data-spec anchor at Skill Agent/CAB/ — not a skill. Anchor verbs are flat skills now (tidy, publish, lint, maintain, wp, yore, move, etc.).
tools: Read
user_invocable: false
---

# CAB — Deprecated

`cab/` is no longer a user-invocable skill. The reorganization split CAB's two responsibilities:

1. **Data spec** (what an anchor IS — facets, disciplines, rules, traits) → `Skill Agent/CAB/` at the SKA root. Read those for the blueprint.
2. **Action verbs** (what you DO to anchors) → individual flat skills:

| Old form | New form |
|---|---|
| `/cab tidy`        | `/tidy` |
| `/cab publish`     | `/publish` |
| `/cab lint`        | `/lint` |
| `/cab maintain`    | `/maintain` |
| `/cab wp <name>`   | `/wp <name>` |
| `/cab yore`        | `/yore` |
| `/cab move`        | `/move` (or `/migrate` for broader reorg) |
| `/cab streams`     | `/streams` |
| `/cab install`     | `/install` |
| `/cab pilot-flow`  | `/pilot-flow` |
| `/cab pr-flow`     | `/pr-flow` |
| `/cab slug-scan`   | `/slug-scan` |
| `/cab create`      | `/create anchor` (router skill) |
| `/cab migrate`     | `/migrate` |

This SKILL.md remains as a tombstone so Claude Code's resolver doesn't surface stale `/cab <verb>` paths. The folder may be retired entirely once leftover scripts and reference content (cab-config.py, LINT User Docs/, etc.) have new homes — see SKA reorg backlog.
