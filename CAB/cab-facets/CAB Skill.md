---
description: SKILL.md entry point for skill anchors
---
# CAB Skill

An omnibus Claude Code skill that groups related actions, reference data, and scripts under a single `/name` command. Invoked via `/name action` (e.g., `/cab setup`, `/md toc`).

**Working example:** `~/.claude/skills/CAE/SKILL.md` — SKILL.md (CAE is a skill folder).

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
4. **Dispatch table** — Wiki-link table mirroring the anchor's anchor page format. Groups reference data by section (e.g., Types, Parts, Rules). Every entry is a clickable wiki-link. Only present when the skill manages reference data.
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
- **Naming** — `{name}-{category}/` (e.g., `cab-traits/`, `cab-rules/`, `cab-facets/`)
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


## Disciplines (`user_invocable: false`)

A **discipline** is a SKILL.md that defines a methodology rather than an invocable command. The user never types `/<name>` to invoke it directly. Instead, other skills cite the discipline and follow its rules when the relevant situation arises.

Disciplines live in `~/.claude/skills/{name}/` with the same folder structure as user-invocable skills, but with `user_invocable: false` in the frontmatter and no Actions table (since there are no actions to dispatch).

### Examples

- `ask-questions` — how the agent batches, numbers, and resolves user questions during feature design / planning. Cited by `/feature`, `/code plan`, `/code architect`, `/ready`, `/fortify`.
- `finalize` — verify → commit → push → merge → docs → cleanup ceremony. Cited by `/land`, `/crank`, `/code release`.
- `workflow` — canonical state graph for a unit of work, Definition of Ready, per-surface mappings. Cited by `[[CAB Backlog]]`, `feature/SKILL.md`, `/ready`, `/mint`, `/finalize`.

### Parallel user docs — required

**Every discipline must ship with a parallel user-facing doc**, the same shape as user-invocable skills. The two files are:

| File | Audience | Content |
|---|---|---|
| `~/.claude/skills/{name}/SKILL.md` | Agent | Full methodology, decision tables, edge cases, anti-patterns. Loaded when a citing skill activates the discipline. |
| `~/.claude/skills/SKL User Docs/SKL Skills/SKL <Name>.md` | User | Concept-focused. What the discipline does, when the user notices it, the format/output the user sees, what to do in response. Shorter than the agent doc. |

The user doc is what surfaces in the SKL dispatch table (the user-facing skills index). The agent doc never appears there directly — only via citations from other skills.

### Why disciplines are not user-invocable

A discipline is a *rule the agent follows*, not a command the user issues. Making it `user_invocable: true` would imply the user can run it as a one-shot, but the discipline only makes sense in context (during a feature design, mid-implementation, etc.). The relevant trigger is *the situation*, not a user invocation.

### When to make something a discipline vs. a skill

- **Skill** (`user_invocable: true`) — has a clear "do this thing now" semantic. The user invokes it. Examples: `/audit`, `/ready`, `/feature`.
- **Discipline** (`user_invocable: false`) — a methodology that other skills follow. The user doesn't invoke it; skills cite it. Examples: `ask-questions`, `finalize`, `workflow`.
- **Both?** — if a single concept has both a "the user wants to run this now" form and an "agent always follows this when applicable" form, split into a skill + discipline pair (e.g., `/finalize` could in principle be invoked, but the *ceremony* is the discipline; we kept only the discipline form for now).
