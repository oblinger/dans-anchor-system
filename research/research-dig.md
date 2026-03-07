# Dig — Entity Investigation

Deep investigation of a specific, named entity. The target is a proper noun — a company, person, paper, product, project, or web post. Produce a dossier covering what the entity is, key facts, and relevant context.

## Workflow

1. **Identify the entity** — confirm the target name and category (person, company, paper, product, project, post)
2. **Search broadly** — use web search to find primary sources, official pages, and authoritative references
3. **Gather key facts** — collect the information appropriate for the entity category
4. **Cross-reference** — verify facts across multiple sources where possible
5. **Produce report** — write the dossier in a dated report folder (see [[#Report Output]])
6. **Log it** — add a row to [[RSH Log]] with the report link and description

## Report Output

Every research action produces a report in the RSH Log folder:

```
RSH Log/
└── {YYYY-MM-DD} {Report Name}/
    ├── {YYYY-MM-DD} {Report Name}.md    Main report (folder file)
    └── ...                               Supporting files (optional)
```

- **Report name** — 3–5 words describing the subject
- **Folder file** — the main write-up; same name as the folder
- **URLs in the report** — all referenced web pages listed as full clickable URLs so they work in Obsidian
- **Surfed pages** — if pages were opened for the user during research, include those URLs in the report too
- **Log entry** — after creating the report, prepend a row to the [[RSH Log]] table:
  `| [[{YYYY-MM-DD} {Report Name}]] | {one-line description} |`

## Dossier Sections

- **Summary** — one-paragraph overview
- **Key Facts** — structured by category (varies by entity type)
- **Sources** — full URLs to all referenced material
- **Open Questions** — anything notable that couldn't be confirmed

## Entity Categories

Future versions will have category-specific investigation templates (person, company, paper, product, post). For now, adapt the investigation approach to fit the entity type using common sense about what matters for that category.
