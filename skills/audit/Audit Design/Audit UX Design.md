---
description: "invocation surface + output format"
---

# Audit UX Design

How the user and agent invoke audit and what they see back. The interaction shape follows the two trigger modes and four levels in [[Audit PRD]].

## Command grammar

```
/audit [sub] [target] [dry] [aggressive]
```

- **`sub`** — optional sub-action (below). Omitted → the orchestrator runs every sub-audit applicable to the target's traits.
- **`target`** — an anchor, a path, or omitted (walk up from cwd to the nearest `.anchor`).
- **`dry`** — report-only; forces the Informational level regardless of anchor setting. The opt-out from fix-by-default.
- **`aggressive`** — opt in to the Aggressive level for this run (structural refactors). Absent → Standard.

The default explicit run **fixes** at Standard and prints a per-rule summary. There is no level flag for Online — that level belongs to the hooks, never the command line.

## Sub-action roster (preserved)

`structure · anchor · doc · dispatch · rules · docs · publish · code · q · q-fix · features · markdown · architecture · integrity`

Each keeps its current behavior; the roadmap ([[Audit Roadmap]]) migrates them onto the unified engine. `dispatch`, `q`, and `features` already fix by default; under V2 every sub-action does, with `dry` as the universal opt-out.

## Explicit-pass output

A per-rule roll-up, grouped by outcome:

- **Fixed** — what was repaired (rule + target + one-line detail), already applied on disk.
- **Flagged** — findings left for the user (judgment calls, ambiguous, or radical), each with the rule and a one-line why.
- **N/A / Pass** — collapsed to counts.

`dry` prints the same roll-up with everything that *would* be fixed listed under **Would fix** instead of **Fixed**.

## On-write surfacing

The online hook is silent when it can be. Per write it returns:

- **Auto-fixed** — applied in place; surfaced as a brief note ("R-markdown-14 trimmed trailing whitespace") so the agent knows the file changed under it.
- **Flagged** — mechanical violations with no safe fixer, plus a throttled, `where::`-relevance-gated reminder of the **judgment-rule titles** for that file kind ("backlog file — review against R-backlog-03 source-order"). Full rule text is fetched on demand; reminders surface once per file per session to avoid fatigue.

Nothing is surfaced for a file no rule matches.

## Deletion mark + sweep

When a rule's violation implies content removal, audit does not delete — it inserts a callout wrapping the content:

> [!info] Recommend deleting — redundant with the Overview; superseded 2026-06-10.
> …the content to remove, verbatim…

The marks accumulate across audits. A **separate explicit command** removes them all:

```
/audit sweep [target]
```

`sweep` is the only operation that deletes, and it deletes *only* the content inside `Recommend deleting` callouts — never anything a normal audit touched. It is never bundled into a normal `/audit` run, so an ordinary audit can never cost the user content.
