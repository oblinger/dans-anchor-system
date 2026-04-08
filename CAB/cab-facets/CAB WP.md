---
description: dated work products — papers, reports, polished outputs
---
# CAB WP

Work Products — polished, dated outputs of human+agent collaboration. Papers, reports, analyses, presentations.

## Location

`{RID} WP/` at the anchor root (not inside Docs). Created on first use via `/cab wp`.

## Structure

```
{Anchor}/
├── {RID} WP/
│   ├── {RID} WP.md                         dispatch page (reverse chronological)
│   ├── 2026-03-28 Architecture Review/
│   │   └── 2026-03-28 Architecture Review.md
│   └── 2026-04-15 Security Audit/
│       ├── 2026-04-15 Security Audit.md
│       └── appendix-a.md
```

## Naming

- Folder and main file share the same name: `{date} {name}/` contains `{date} {name}.md`
- Date format: `YYYY-MM-DD`
- No RID prefix on files inside WP (date + name provides uniqueness)
- Always a folder, even for single-file work products — they often grow

## Dispatch Page

`{RID} WP/{RID} WP.md` contains a reverse chronological table:

```markdown
| -[[{RID} WP]]- >: | +> |
| --- |
| [[2026-04-15 Security Audit]] |
| [[2026-03-28 Architecture Review]] |
```

The `>:` marker signals HookAnchor to include child anchor WP entries (future feature).

## Anchor Page Row

When the WP folder is created, a **Work** row is added to the anchor dispatch table after the standard rows:

```
| Work | [[{RID} WP\|WP]] |
```

## Distinction from Other Dated Content

| Type | Location | Created by | Purpose |
|------|----------|-----------|---------|
| **WP** | `{RID} WP/` at root | `/cab wp` on request | Polished work products |
| **Outputs** | `{RID} Outputs/` in Plan | `stat add` automatically | Agent-generated reports |
| **Log** | anchor page or log file | manual | Informal notes and history |
| **Features** | `{RID} Features/` in Plan | `/code feature` | Feature design specs |
