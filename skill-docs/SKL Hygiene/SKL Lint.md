---
description: "`/lint` (or `/cab lint`) is the static-analysis pass over an anchor — it scans the folder structure, dispatch tables, and module docs against the CAB type rules and tells you what's missing, stale,…"
---
# /Lint

`/lint` (or `/cab lint`) is the static-analysis pass over an anchor — it scans the folder structure, dispatch tables, and module docs against the CAB type rules and tells you what's missing, stale, or out of conformance. The default level (5) compares your module docs to the actual source code, flagging undocumented classes, methods, enums, and fields, plus stale doc entries for things that have been deleted. Use it when you say "lint this," "check the structure," or "are there violations."

Lint is **detect-only by design**. Even when the finding implies an obvious fix — missing dispatch row, missing module doc, misplaced file — lint never edits or moves things itself; that's `/rewire`'s job. Findings either get fixed in the relevant markdown file or get an entry in the anchor's `.anchor.d/lint/exceptions.md` file (for genuinely-private items, trivial accessors, or whole categories you want to skip via glob). Levels go from 1 (bare bones marker file checks) up to 9 (pedantic spacing and TOC formatting); pick the level via `/lint 3` or `/lint 8`.
