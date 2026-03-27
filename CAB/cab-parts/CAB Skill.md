# CAB Skill

An omnibus Claude Code skill that groups related actions, reference data, and scripts under a single `/name` command. Invoked via `/name action` (e.g., `/cab setup`, `/md toc`).

Below is a reference example for a hypothetical skill "ops" (Operations).

# Reference Example
---

```yaml
---
name: ops
description: >
  Operations skill — deployments, monitoring, and incident response.
  Use with an action argument: /ops deploy, /ops monitor, /ops incident.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---
```

\# OPS — Operations
Deployment, monitoring, and incident response workflows.

| Section           | Contents                                                          |
| ----------------- | ----------------------------------------------------------------- |
| [[OPS Runbooks]]  | [[OPS Deploy Checklist]], [[OPS Rollback]], [[OPS Scaling]]       |
| [[OPS Playbooks]] | [[OPS Incident Response]], [[OPS Post-Mortem]], [[OPS On-Call]]   |

\## Actions

| Usage            | File              | Description                                    |
| ---------------- | ----------------- | ---------------------------------------------- |
| `/ops deploy`    | [[ops-deploy]]    | Staged deployment with rollback checkpoints    |
| `/ops monitor`   | [[ops-monitor]]   | Health check sweep across all services         |
| `/ops incident`  | [[ops-incident]]  | Incident response — triage, mitigate, document |

\## Reference

| What you need   | Where to find it                                  |
| --------------- | ------------------------------------------------- |
| Runbooks        | `ops-runbooks/` — step-by-step operational guides |
| Playbooks       | `ops-playbooks/` — incident and on-call playbooks |

\## Scripts

| Script            | Usage                                              |
| ----------------- | -------------------------------------------------- |
| `ops-status.py`   | Aggregate service health into a summary dashboard  |

\## Dispatch

On invocation:
1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory and execute its workflow
4. If no argument or unrecognized argument, show the dispatch table above

---



# Format Specification


## Location

Skills live at `~/.claude/skills/{name}/`. The skill folder is typically symlinked into the Obsidian vault so files are navigable from both Claude Code and Obsidian.


## SKILL.md Structure

The root file `SKILL.md` is the only file loaded into context when the skill is invoked. All other files in the skill folder are inert until explicitly read. This makes it safe to store large amounts of reference data alongside the skill.

SKILL.md has these sections in order:

1. **Frontmatter** — YAML with `name`, `description`, `tools`, `user_invocable: true`
2. **Title** — `# {NAME} — {Full Name}`
3. **Brief** — One-line description of the skill's purpose
4. **Dispatch table** — Wiki-link table mirroring the anchor's RID page format. Groups reference data by section (e.g., Types, Parts, Rules). Every entry is a clickable wiki-link. Only present when the skill manages reference data.
5. **Actions** — Table of `/name action` commands, each linking to a sub-file
6. **Reference** — Table pointing to subdirectories containing reference data
7. **Topics** — Optional table of domain-specific reference files read on demand
8. **Scripts** — Optional table of utility scripts with usage examples
9. **Dispatch** — Standard 4-step dispatch protocol


## Action Files

Each action is a separate markdown file in the skill root:
- **Naming** — lowercase, hyphenated: `{name}-{action}.md` (e.g., `cab-create.md`, `md-toc.md`)
- **Content** — Workflow steps the agent follows when the action is invoked. Should be self-contained enough to execute without reading SKILL.md again.


## Reference Data Subdirectories

Large reference data lives in subdirectories within the skill folder:
- **Naming** — `{name}-{category}/` (e.g., `cab-types/`, `cab-rules/`, `cab-parts/`)
- **File naming** — Reference files keep their original names (e.g., `CAB Simple Anchor.md`). Action files use the lowercase hyphenated convention. This distinction makes it clear which files are actions and which are reference data.
- **Wiki-links** — Since Obsidian resolves wiki-links by filename regardless of path, moving files into skill subdirectories does not break existing links.


## Scripts

Scripts are utility programs that live in the skill folder:
- Run via `uv run ~/.claude/skills/{name}/{script}` for Python scripts
- Listed in the Scripts section of SKILL.md with usage examples


## Dispatch Protocol

Every SKILL.md ends with the same dispatch protocol:

1. Parse the argument to determine the action
2. Look up the file from the Actions table
3. Read that file from the skill's directory and execute its workflow
4. If no argument or unrecognized argument, show the dispatch table
