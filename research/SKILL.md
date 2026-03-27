---
name: research
description: >
  Research workflows — structured investigation, source gathering, and synthesis.
  Use with an action argument: /research dig, /research survey, /research person, /research book.
  When the user says "do a survey", "run a survey", "survey this", "research this",
  "look into", "investigate", "find out about", "what tools exist for",
  "what's out there for", invoke /research survey or /research dig as appropriate.
tools: Read, Write, Edit, Bash, WebSearch, WebFetch, Glob, Grep
user_invocable: true
---

# Research — Investigation & Synthesis
Structured research workflows for gathering, analyzing, and synthesizing information from web sources, documents, and codebases.


## Report Output — All Types

Every research action produces a report in the **RRR** (Research Reports) anchor:

```
~/ob/kmr/RR/RR Research Reports/
├── RR Research Reports.md              marker file
├── RRR.md                              dispatch table (reverse chronological)
├── {YYYY-MM-DD} {Report Name}/         ← one folder per report
│   ├── {YYYY-MM-DD} {Report Name}.md   main report (folder file = anchor file)
│   └── ...                             supporting files (optional)
```

- **Folder name** = `{YYYY-MM-DD} {Report Name}` — date of the research, 3-5 word topic
- **Folder file** = same name as folder + `.md` — this is the main report
- **All report types** (survey, dig, person, book) go in this single location
- **URLs** — all referenced web pages listed as full clickable URLs
- **Dispatch table** — after creating the report, prepend a row to `RRR.md`:
  `| [[{YYYY-MM-DD} {Report Name}\|{date} {short name}]] | one-line description |`


| ACTIONS             | File                 | Description                                                 |
| ------------------- | -------------------- | ----------------------------------------------------------- |
| `/research dig`     | [[research-dig]]     | Deep investigation of a specific entity — produce a dossier |
| `/research survey`  | [[research-survey]]  | Broad survey of a topic area — produce a landscape report   |
| `/research person`  | [[research-person]]  | Research a person — produce an AT person-file dossier        |
| `/research book`    | [[research-book]]    | Research a book — produce a summary in BOOK Summary          |


## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory and execute its workflow
4. If no argument or unrecognized argument, show the actions table above
