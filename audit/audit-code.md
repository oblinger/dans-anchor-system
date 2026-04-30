# Code — Audit Code Patterns and Quality

Systematic code quality audit using Semgrep for mechanical pattern detection and agent reasoning for intent-level analysis. Each concern has a catalog with language-specific patterns. **Reports findings only.** Fix work goes into a backlog entry; no source files are modified.

## Steps

1. Detect project language from `.anchor` file (or frontmatter) or file extensions.
2. Run Semgrep with generic rules: `semgrep --config ~/.claude/skills/audit/catalogs/ --json <code-path>`.
3. Parse Semgrep results — these are the mechanical findings.
4. For each applicable catalog `.md` file in `~/.claude/skills/audit/catalogs/`, read it and perform agent-level analysis on the source code.
5. Combine Semgrep findings + agent findings into a findings table:

```
| # | Catalog | Location | Issue |
|---|---------|----------|-------|
| 1 | fallbacks | src/lib.rs:42 | `unwrap_or_default()` on a Result that should propagate |
| 2 | stale | src/util.rs:18 | TODO from 2024 — likely abandoned |
```

Print this table to the console. **If `dry` substring is in args**, stop here — print "dry-run — no backlog entry written."

6. Write the backlog entry. Locate `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`. Read it, find the lowest unused B-number (per [[CAB Backlog]] § Format), and append a new bullet under `## Upcoming`:

```
- **B<n> — Code audit: <N> findings (<YYYY-MM-DD>)** [Ready] — work surfaced by `/audit code`. Sub-bullets are candidate splits if this needs to be broken up.
  - <catalog>: <file:line> — <short issue>
  - …
```

Group sub-bullets by catalog (fallbacks → stale → multipath → testing), then by file path. Keep each sub-bullet to one line.

If sub-bullet count would exceed ~50, split into multiple entries by catalog cluster (one entry per catalog). The orchestrator will allocate consecutive B-numbers in this case.

If there are zero findings, do **not** write an entry.

7. Report. Print a one-line summary:
- With findings: `code: N findings → B<n>` (or `B<n>..B<m>` if split)
- Clean: `code: clean — no entry written`
- Dry: `code: N findings (dry-run, no entry written)`

The orchestrator (or single-skill caller) will roll this up into the final stat post.

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

- `/audit code` — run all catalogs + Semgrep, write a backlog entry.
- `/audit code fallbacks` — run only the silent-fallbacks catalog (still writes a backlog entry, but scoped to that catalog).
- `/audit code dry` (or `dry` anywhere in args) — scan and report only; do not write a backlog entry.

There is no `--fix` flag. Audits never fix.

## What Semgrep Catches vs Agent

**Semgrep (fast, deterministic):** exact syntax patterns — `catch {}`, `.ok()`, `unwrap_or_default()`, `try?`, `except: pass`.

**Agent (slower, reasoning):** intent analysis — "is this default value hiding a real failure?" "is this guard clause silently dropping an error that should propagate?" "is this config.get fallback masking a missing dependency?".

Both run every time. Semgrep findings are always real. Agent findings are reviewed.
