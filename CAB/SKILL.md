---
name: cab
description: >
  Common Anchor Blueprint — create, validate, and manage anchor folder structures.
  Use with an action argument: /cab setup, /cab tidy, /cab move, /cab migrate, /cab pr-flow, /cab pilot-flow, /cab rid-scan.
  Reference files for rules, parts, and formats are available in this folder.
tools: Read, Write, Edit, Bash, Glob, Grep, Task
user_invocable: true
---

# CAB — Common Anchor Blueprint

Manage anchor folder structures according to the Common Anchor Blueprint specification.

| Section                                | Contents                                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [[CAB Types]]                          | [[Simple Anchor]], [[Topic Anchor]], [[Code Anchor]], [[Paper Anchor]], [[Skill Anchor]]                                                                                                                                                                                                                                                                               |
| [[CAB All Files]]<br><br>[[CAB Parts]] | [[CAB Folder]], [[CAB Anchor Page]], [[CAB Docs]], [[CAB Backlog]], <br> [[CAB Features]], [[CAB Files]], [[CAB Roadmap]], <br> [[CAB Code Repository]], [[CAB Project Page]], [[CAB Documentation Site]], <br> [[CAB Claude]], [[CAB Module Doc]], [[CAB Skill]], [[CAB PRD]], <br> [[CAB Open Questions]], [[CAB System Design]], [[CAB UX Design]], <br> [[CAB Discussion]], [[CAB Cards]], [[CAB Inbox]] |
| [[CAB Rules]]                          | [[CAB Defined Terms]], [[CAB Markdown Formatting]], [[CAB Naming Conventions]], <br> [[CAB Page Conventions]], [[CAB Docs Conventions]], [[CAB Documentation Publishing]], <br> [[CAB Repository Structure]], [[CAB Rust Rules]], [[CAB Integrations]], <br> [[CAB Research]], [[CAB Maintenance]]                                                                       |


## Actions

Each action is defined in a sub-file. When invoked, read the corresponding file and execute its workflow.

| Usage              | File                | Description                                                       |
| ------------------ | ------------------- | ----------------------------------------------------------------- |
| `/cab create`      | [[cab-create]]      | Create a new anchor — gather info, create structure, register     |
| `/cab tidy`        | [[cab-tidy]]        | Validate and correct anchor folder structure                      |
| `/cab move`        | [[cab-move]]        | Move an anchor and update all path-dependent systems              |
| `/cab migrate`     | [[cab-migrate]]     | Convert an anchor from one type to another                        |
| `/cab pr-flow`     | [[cab-pr-flow]]     | Iterative PR-based development with user review                   |
| `/cab pilot-flow`  | [[cab-pilot-flow]]  | Top-down design then implementation (dispatches to /code skills)   |
| `/cab rid-scan`    | [[cab-rid-scan]]    | Scan for new RIDs and sync the index                              |
| `/cab lint`        | [[cab-lint]]        | Lint an anchor — check structure, files, links against CAB type rules |
| `/cab maintain`    | [[cab-maintain]]    | Keep derived files in sync — run standing maintenance orders      |
| `/cab scan`        | [[cab-scan]]        | Discover all anchors, write registry to ~/.config/skl/anchors.yaml          |
| `/cab config`      | [[cab-config]]      | Manage .anchor/config.yaml — init, set, get, show anchor paths              |
| `/cab install`     | [[cab-install]]     | Install CAB tools (stat, cab-config, cab-scan, cab-lint) into ~/bin         |
| `/cab compile`     | [[compile/compile]] | Compile CAB specs into executable checklists for skill actions              |
| `/cab migrate-claude` | [[cab-migrate-claude]] | Migrate a Claude Code session when an anchor moves to a new path         |
| `/cab publish`     | [[cab-publish]]     | Deploy an anchor's public page to the web (gitproj or GitHub Pages)      |
| (ref)              | [[stat]]            | Activity status tracking — `stat add/update/archive` across projects        |
| `/cab yore`        | [[cab-yore]]        | Archive folders/anchors to Yore with date-prefixed zip            |
| `/cab streams`     | [[cab-streams]]     | Content stream definitions (stub)                                 |


## Reference

Reference files live in subdirectories of this skill folder:

| What you need  | Where to find it                                                    |
| -------------- | ------------------------------------------------------------------- |
| Base file tree | [[CAB Base]] — canonical tree for all types                        |
| Anchor types   | `cab-types/` — one file per type with deltas from base              |
| Part specs     | `cab-parts/` — format spec + reference example for each file type   |
| Full file tree | [[CAB All Files]] — every possible file across all types            |
| Rules          | `cab-rules/` — naming, markdown, docs, integrations                 |

Read these on demand when the action workflow requires specific format or structural details.


## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory and execute its workflow
4. If no argument or unrecognized argument, show the dispatch table above
