# Code — Audit Code Patterns and Quality

Systematic code quality audit using Semgrep for mechanical pattern detection and agent reasoning for intent-level analysis. Each concern has a catalog with language-specific patterns.

## Steps

1. Detect project language from `.anchor/config.yaml` or file extensions
2. Run Semgrep with generic rules: `semgrep --config ~/.claude/skills/audit/catalogs/ --json <code-path>`
3. Parse Semgrep results — these are the mechanical findings
4. For each applicable catalog `.md` file in `~/.claude/skills/audit/catalogs/`, read it and perform agent-level analysis on the source code
5. Combine Semgrep findings + agent findings into a fixes table using this format:

```
| Finding | Issue | Fix |
|---------|-------|-----|
| **1.** file:line<br>`pattern` | What's wrong | How to fix it |
```

The Finding column packs: number, file:line, and pattern name. Issue and Fix get the remaining width.

6. Post to stat with status "Ready" — the audit output is the spec for what to fix
7. Add a backlog entry linking to the output

## Catalogs

Each catalog is a focused analysis — one concern, with language-specific patterns inside.

| Catalog | What it catches |
|---------|----------------|
| [[catalogs/all-fallbacks\|fallbacks]] | Error swallowing, default values hiding failures, ignored return values |
| [[catalogs/all-stale\|stale]] | TODOs, commented-out code, dead imports, deprecated remnants, orphan files |
| [[catalogs/all-multipath\|multipath]] | Multiple implementations, redundant branches, duplicate logic |
| [[catalogs/all-testing\|testing]] | Missing test files, untested error paths, ignored tests |

## Semgrep Rules

Semgrep `.yaml` rule files live alongside their `.md` catalog in `~/.claude/skills/audit/catalogs/`. Each catalog concern has both a markdown file (agent reasoning checklist) and a yaml file (mechanical Semgrep patterns). Both are in the same folder.

For project-specific Semgrep rules, add them to the project's rules file or create a `.semgrep.yaml` in the repo root.

## Modes

- `/audit code` — run all catalogs + Semgrep
- `/audit code fallbacks` — run only the silent-fallbacks catalog
- `/audit code --fix` — find and fix

## What Semgrep Catches vs Agent

**Semgrep (fast, deterministic):** exact syntax patterns — `catch {}`, `.ok()`, `unwrap_or_default()`, `try?`, `except: pass`

**Agent (slower, reasoning):** intent analysis — "is this default value hiding a real failure?" "is this guard clause silently dropping an error that should propagate?" "is this config.get fallback masking a missing dependency?"

Both run every time. Semgrep findings are always real. Agent findings are reviewed.
