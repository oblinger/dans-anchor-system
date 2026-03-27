# Survey — Topic Landscape

Broad survey of a topic area, category, or question. The target is not a single entity but a space — a technology area, a market segment, a research question, a class of tools. Produce a landscape report covering the major players, approaches, and state of the art.

## Workflow

1. **Clarify the scope** — confirm the topic area and what the user wants to understand (landscape, comparison, state of the art, options analysis)
2. **Search broadly** — cast a wide net across web sources, looking for overviews, comparisons, and authoritative surveys
3. **Identify structure** — find the natural categories, dimensions, or axes that organize the space
4. **Fill in the map** — for each category or major player, gather enough detail to characterize it
5. **Synthesize** — identify patterns, gaps, trends, and notable outliers
6. **Produce report** — write the landscape report in a dated report folder (see [[#Report Output]])
7. **Log it** — add a row to [[RRR]] with the report link and description

## Report Output

Every research action produces a report in the RRR folder:

```
RRR/
└── {YYYY-MM-DD} {Report Name}/
    ├── {YYYY-MM-DD} {Report Name}.md    Main report (folder file)
    └── ...                               Supporting files (optional)
```

- **Report name** — 3–5 words describing the subject
- **Folder file** — the main write-up; same name as the folder
- **URLs in the report** — all referenced web pages listed as full clickable URLs so they work in Obsidian
- **Surfed pages** — if pages were opened for the user during research, include those URLs in the report too
- **Log entry** — after creating the report, prepend a row to the [[RRR]] table:
  `| [[{YYYY-MM-DD} {Report Name}]] | {one-line description} |`

## Report Sections (in order)

1. **Results Table** — ALWAYS first. A single table where rows are the entries found and columns are relevant properties. This is the primary deliverable — the reader should see the results before any prose. The table can be wide enough to require a large monitor. Choose columns that let the reader compare entries at a glance (e.g., Name, Category, Language, Key Feature, Relevance). The first column is always the entry name as a markdown link to its URL: `[PSX](https://github.com/m-mdy-m/psx)` — do NOT have separate Name and URL columns.

2. **Overview** — what this space is and why it matters

3. **Landscape** — the major categories, players, or approaches, organized by the natural structure of the space. Expands on what the table summarizes.

4. **Trends** — what's changing, what's emerging

5. **Gaps** — what's missing from the landscape, what no one has built yet

6. **Recommendations** — if the user asked for guidance, a clear recommendation with reasoning

7. **Sources** — full URLs to all referenced material
