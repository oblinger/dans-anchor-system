---
name: md
description: >
  Markdown utility verbs — produce or maintain markdown artifacts: /md file-tree (format file trees),
  /md toc (regenerate tables of contents), /md dispatch-table (build dispatch pages), /md cards
  (build cheat / summary / detail cards), /md track-changes (inline diff HTML for edits). Bare /md
  glances the [[markdown]] discipline rules. The format-rule content moved to [[markdown]] 2026-06-10 —
  this skill keeps utility verbs only.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# MD — Markdown Utility Verbs

User-invokable utility skill that produces or maintains markdown artifacts (file trees, TOCs, dispatch tables, cards, track-changes diffs); bare `/md` opens the companion [[markdown]] discipline.

User-invokable verbs that produce or maintain markdown artifacts. The companion discipline [[markdown]] owns the *format rules*; this skill owns the *operations*.

| ACTIONS                | File                    | Description                                              |
| ---------------------- | ----------------------- | -------------------------------------------------------- |
| `/md file-tree`        | [[md-file-tree]]        | File tree diagram format — 4 forms with box-drawing      |
| `/md toc`              | [[md-toc]]              | Table of contents format — 3 forms + auto-generation     |
| `/md dispatch-table`   | [[md-dispatch-table]]   | Dense link table + dispatch pages for navigation hubs    |
| `/md cards`            | [[md-cards]]            | Cards format — cheat sheets, summary cards, detail cards |
| `/md track-changes`    | [[md-track-changes]]    | Track changes — inline diff HTML for markdown edits      |

For format rules (the "every time you write markdown" discipline) see **[[markdown]]**. Bare `/md` opens that file.

## Scripts

| Script       | Usage                                                        |
| ------------ | ------------------------------------------------------------ |
| `md-toc.py`  | Auto-generate TOC from H2/H3 headings. Run via `uv run`.    |

```bash
uv run ~/.claude/skills/md/md-toc.py <file.md>           # Replace TOC in-place
uv run ~/.claude/skills/md/md-toc.py <file.md> --dry-run  # Preview to stdout
```

## Dispatch

On invocation:

1. Parse the argument to determine the action.
2. Look up the file from the Actions table above.
3. Read that file from this skill's directory and execute its workflow.
4. **No argument or unrecognized argument** — glance [[markdown]] (the discipline file) since the user is asking about markdown writ large.

## Related

- [[markdown]] — sibling discipline; the format rules cited by every facet and authoring skill.
- [[progressive-disclosure]] — sibling discipline; what-goes-where-in-a-doc.
- [[ask-format]] — sibling discipline; user-actionable surface format.
