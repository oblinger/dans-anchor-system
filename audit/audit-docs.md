# Docs — Audit Documentation Against Source Code

Ensure every source module has a correct module doc, Files.md matches the source tree, and docs stay current.

## Steps

1. Detect anchor, find code path from `.anchor/config.yaml`
2. Read the compiled checklist: `~/.claude/skills/audit/audit-docs.compiled.md`
3. Execute **Phase 1: Scan** — inventory source, compare to docs, check freshness
4. Execute **Phase 2: Report** — build fixes table, post to stat
5. If `--fix` flag: execute **Phase 3: Fix** — create missing docs, update stale docs

## Modes

- **`/audit docs`** — scan and report only. Posts punch list to stat.
- **`/audit docs --fix`** — scan, report, then fix all issues.
- **`/audit docs --recheck`** — ignore freshness, check every doc against source.
