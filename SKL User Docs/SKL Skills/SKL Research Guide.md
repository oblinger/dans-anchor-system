---
description: How to run structured research — deep investigations and landscape surveys
---

# SKL Research Guide (Skill: [[research/SKILL]])

The Research skill provides structured workflows for gathering, analyzing, and synthesizing information. The two primary modes are dig (deep investigation of a specific entity) and survey (broad landscape scan of a topic area). Additional modes handle person research and book summaries.

Every research action produces a report in the RRR (Research Reports) anchor at `~/ob/kmr/RR/RR Research Reports/`. Reports are organized as dated folders with a main markdown file and optional supporting materials. After creating a report, the agent adds it to the RRR dispatch table.

When you say "research this", "look into", "investigate", "what tools exist for", or "do a survey", the agent selects the appropriate research action automatically.

## Commands

| Command | Description |
|---------|-------------|
| `/research dig` | Deep investigation of a specific entity — produce a dossier |
| `/research survey` | Broad survey of a topic area — produce a landscape report |
| `/research person` | Research a person — produce a person-file dossier |
| `/research book` | Research a book — produce a summary |

## Key Concepts

- **Dig vs survey** — Dig goes deep on one thing (a company, a tool, a technology). Survey goes wide across a category (what tools exist, what approaches are common)
- **Report output** — All reports go to `~/ob/kmr/RR/RR Research Reports/{YYYY-MM-DD} {Report Name}/`
- **Dispatch table** — After creating a report, a row is prepended to `RRR.md` for navigation
- **Full URLs** — All referenced web pages are listed as full clickable URLs, not shortened links
- **Web search** — Research actions use WebSearch and WebFetch extensively to gather current information
