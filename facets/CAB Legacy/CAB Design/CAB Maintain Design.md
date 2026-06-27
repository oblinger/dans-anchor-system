---
description: design distillation — the maintain skill (keep derived files in sync with source files)
---
# CAB Maintain Design

**From:** [[F210 — Maintain Skill]]

Distilled design for the **maintain** skill — keeps derived files in sync with their sources. Lives in both CAB (structure maintenance) and DEV (code/docs maintenance). Design-phase; see [[F210 — Maintain Skill]] for the full spec + open questions.

## Essence

- **Maintenance table** at `{NAME} Docs/{NAME} Plan/{NAME} Maintenance.md` — a markdown table of `Source | Action | Description` rows declaring what must stay in sync (e.g. `dev/SKILL.md → copy actions table to DEV.md`; `Code/src/**/*.rs → update module docs`). Sources may be globs and follow symlinks.
- **State file** `.skl/maintain/state.json` — per-source `source_mtime` + `last_verified`; a row needs work when on-disk mtime is newer than recorded.
- **Script** `maintain.py <anchor> [--check | --update <source>]` — `--check` reports out-of-date rows (it does not perform the work); `--update` records a source as verified. The skill reads the report and executes each row's Action.
- **Workflow** — `/cab maintain` (or `/dev maintain`): run `--check`, execute each stale row's Action, then `--update` to record success.

## Relationship to siblings

Rewire fixes structural wiring; lint detects problems; **maintain** keeps derived content in sync proactively — the first concrete form of "standing orders."

## Open design questions (unresolved — see F210)

Glob-handling in the Source column; Action-column format (free-form English vs structured verbs); auto-run as part of `/dev verify`; non-file triggers (e.g. `git log --since`).
