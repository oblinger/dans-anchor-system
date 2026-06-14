---
description: User docs for the /research family — structured investigation, source gathering, synthesis
---
# /Research
Structured research workflows. You give it a target (entity / topic / person / book / skill concept), it gathers sources, synthesizes findings, and produces a report in the RRR (Research Reports) anchor at `~/ob/kmr/RR/RR Research Reports/`.

| -[[SKL Research]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Search]] → [SKL Research](hook://p/SKL%20Research)<br>: the SKL Research doc |
| --- | --- |
| [[SKL Research Design\|Design]] |  |

Every research action shares the same output skeleton: a dated report folder with a results table at the top, written analysis below, and full URLs in a Sources section so links work outside Obsidian.

## Sub-skills

| Action | What it does |
|---|---|
| [[SKL Research Dig\|Dig]] | Deep investigation of a specific entity — produces a dossier on a company, product, technology, project, or other concrete subject |
| [[SKL Research Survey\|Survey]] | Broad survey of a topic area — produces a landscape report (major players, approaches, trends, gaps) |
| [[SKL Research Skill\|Skill]] | Compare agent skills addressing a concept — choice-point analysis + groupings, for "should I build / rebuild this skill, and how?" |
| [[SKL Research Person\|Person]] | Research a person — produces an AT person-file dossier with background, work history, public footprint |
| [[SKL Research Book\|Book]] | Research a book — produces a summary in BOOK Summary |

Sub-skill docs marked with broken links are not yet written (tracked by [[SKA Backlog#^B-skl-user-docs|B-skl-user-docs]]).

## Common output: the RRR report

Every action writes to:

```
~/ob/kmr/RR/RR Research Reports/
└── {YYYY-MM-DD} {Report Name}/
    ├── {YYYY-MM-DD} {Report Name}.md   ← main report (folder file)
    └── ...                              ← supporting files (optional)
```

After writing, the action prepends a row to `[[RRR]]` (the Research Reports dispatch page) with a link and one-line description, so every report is one click away from the dispatch.

## Common shape: results table first

Every report opens with a **Results Table** — rows are entries, columns are properties that let you compare at a glance. The first column is the entry name as a markdown link to its source URL (no separate "Name" + "URL" columns). Entries are ranked by value to the user, with a blank separator row between top-tier and the rest.

After the table, prose: overview, analysis, recommendations (when asked), and sources.

## When to use which

- **Looking at one specific thing** → `/research dig`
- **Want the landscape of a space** → `/research survey`
- **Specifically comparing agent skills** → `/research skill` (specialized survey; pre-bakes the domain + columns + required choice-point analysis)
- **Researching a person** → `/research person`
- **Researching a book** → `/research book`

If `/research skill` and `/research survey` both seem to apply: `/research survey` is for "what's out there" (flat enumeration is acceptable), `/research skill` is for "how should I think about the choices" (choice-point analysis is mandatory).
