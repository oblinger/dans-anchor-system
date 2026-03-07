---
name: research
description: >
  Research workflows — structured investigation, source gathering, and synthesis.
  Use with an action argument: /research dig, /research survey.
tools: Read, Write, Edit, Bash, WebSearch, WebFetch, Glob, Grep
user_invocable: true
---

# Research — Investigation & Synthesis
Structured research workflows for gathering, analyzing, and synthesizing information from web sources, documents, and codebases.


| ACTIONS            | File                | Description                                                 |
| ------------------ | ------------------- | ----------------------------------------------------------- |
| `/research dig`    | [[research-dig]]    | Deep investigation of a specific entity — produce a dossier |
| `/research survey` | [[research-survey]] | Broad survey of a topic area — produce a landscape report   |


## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory and execute its workflow
4. If no argument or unrecognized argument, show the actions table above
