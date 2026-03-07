
# COMMON ANCHOR BLUEPRINT


| Section                                | Contents                                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [[CAB Types]]                          | [[Simple Anchor]], [[Topic Anchor]], [[Split Anchor]], <br> [[Private Repo Anchor]], [[Public Repo Anchor]], [[Paper Anchor]], [[Skill Anchor]]                                                                                                                                                                                                                           |
| [[CAB All Files]]<br><br>[[CAB Parts]] | [[CAB Folder]], [[CAB Page]], [[CAB Docs]], [[CAB Backlog]], <br> [[CAB Features]], [[CAB Files]], [[CAB Roadmap]], <br> [[CAB Code Repository]], [[CAB Documentation Site]], <br> [[CAB Claude]], [[CAB Module Doc]], [[CAB Skill]], [[CAB PRD]], <br> [[CAB Open Questions]], [[CAB System Design]], [[CAB UX Design]], <br> [[CAB Design Discussions]], [[CAB Cards]], [[CAB Inbox]] |
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
| `/cab pilot-flow`  | [[cab-pilot-flow]]  | Top-down design then implementation (dispatches to /dev skills)   |
| `/cab tlc-scan`    | [[cab-tlc-scan]]    | Scan for new TLCs and sync the index                              |
| `/cab streams`     | [[cab-streams]]     | Content stream definitions (stub)                                 |
