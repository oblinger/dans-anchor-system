---
description: "Structured research workflows — gather sources on a target (entity/topic/person/book/concept) and produce a synthesized dated report in the matching SRCH output stream"
---
# DAS Research
Structured research workflows. You give it a target (entity / topic / person / book / skill concept), it gathers sources, synthesizes findings, and produces a dated report in the [[SRCH]] output stream matching the shape of what it produced, under `~/ob/kmr/Topic/Search/`.

| -[[DAS Research]]- | : Structured research workflows — gather sources on a target (entity/topic/person/book/concept) and produce a synthesized dated report in the matching SRCH output stream<br>→ [[DAS]] → [docs](hook://docs) → [DAS Research](hook://p/DAS%20Research)  |
| --- | --- |
| ... |  |

Every research action shares the same output skeleton: a dated report folder with a results table at the top, written analysis below, and full URLs in a Sources section so links work outside Obsidian.

## Sub-skills

| Action | What it does |
|---|---|
| [[DAS Research Dig\|Dig]] | Deep investigation of a specific entity — produces a dossier on a company, product, technology, project, or other concrete subject |
| [[DAS Research Survey\|Survey]] | Broad survey of a topic area — produces a landscape report (major players, approaches, trends, gaps) |
| [[DAS Research Skill\|Skill]] | Compare agent skills addressing a concept — choice-point analysis + groupings, for "should I build / rebuild this skill, and how?" |
| [[DAS Research Person\|Person]] | Research a person — produces an AT person-file dossier with background, work history, public footprint |
| [[DAS Research Book\|Book]] | Research a book — produces a summary in BOOK Summary |

Sub-skill docs marked with broken links are not yet written (tracked by [[TINK Backlog#^B-skl-user-docs|B-skl-user-docs]]).

## Common output: a dated file in the matching stream

Every action writes to the [[SRCH]] output stream matching the shape of what it produced — [[Survey]] (comparisons), [[Profile]] (one-entity dossiers), [[Find]] (lookups), [[Guide]] (playbooks):

```
~/ob/kmr/Topic/Search/{Survey|Profile|Find|Guide}/
├── {YYYY-MM-DD} {Report Name}.md        ← the usual case: one flat dated file
└── {YYYY-MM-DD} {Report Name}/          ← only when there are supporting files
    ├── {YYYY-MM-DD} {Report Name}.md    ← folder note, same name as the folder
    └── ...                              ← supporting files (PDF, docx, sub-reports)
```

After writing, the action prepends a row to that stream's catalog page with a link and one-line description, so every report is one click from the dispatch. The former `RR/RR Research Reports/` home ([[SLUG|RRR]]) was retired 2026-08-01 and its reports migrated into these streams — don't write there.

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
