---
description: "the Skill primitive — SKILL.md entry-point structure and conventions"
---

# DAS Skill
An omnibus Claude Code skill that groups related actions, reference data, and scripts under a single `/name` command. Invoked via `/name action` (e.g., `/cab setup`, `/md toc`).

| -[[DAS Skill]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Skill](hook://p/DAS%20Skill) |
| --- | --- |
| Related | [[DAS Facet]],  [[DAS Ruleset]],  [[DAS Primitives]],  [[DAS Aspects]],   |
| Examples | [[FEX Skill\|canonical exemplar]],  [[FEX Minimal Skill\|minimal capsule]],   |
| Rules | [[R-skill]],  [[R-skill-md]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[facets/DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Disciplines Brief]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Plan Dispatch]],  [[DAS PRD]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS TSK User Guide]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — Every skill anchor ships a `SKILL.md` with fixed frontmatter (`name`, `description`, `tools`, `user_invocable`) and a fixed section order (Title → Brief → dispatch tables → Actions → Reference → Dispatch protocol). Disciplines (`user_invocable: false`) additionally require a parallel user-facing doc at `docs/<domain>/DAS <Name>.md`. **Cardinality: one per anchor** — each skill folder has exactly one `SKILL.md` entry point.

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
| ~~[[OPS Runbooks]]~~  | ~~[[OPS Deploy Checklist]]~~, ~~[[OPS Rollback]]~~, ~~[[OPS Scaling]]~~       |
| ~~[[OPS Playbooks]]~~ | ~~[[OPS Incident Response]]~~, ~~[[OPS Post-Mortem]]~~, ~~[[OPS On-Call]]~~   |

\## Actions

| Usage            | File              | Description                                    |
| ---------------- | ----------------- | ---------------------------------------------- |
| `/ops deploy`    | ~~[[ops-deploy]]~~    | Staged deployment with rollback checkpoints    |
| `/ops monitor`   | ~~[[ops-monitor]]~~   | Health check sweep across all services         |
| `/ops incident`  | ~~[[ops-incident]]~~  | Incident response — triage, mitigate, document |

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

**F060 — SKILL.md is exempt.** SKILL.md is the Claude Code skill entry point; its frontmatter has fixed required fields (`name`, `description`, `tools`, `user_invocable`) and the body has a fixed structure (Title → Brief → dispatch tables → Actions → Reference → Dispatch protocol). The F060 dispatch-table placeholder rule applies to the **anchor root page `{Slug}.md`** (e.g., `Groom.md`) for skill anchors, not to SKILL.md itself.

SKILL.md has these sections in order:

1. **Frontmatter** — YAML with `name`, `description`, `tools`, `user_invocable: true`
2. **Title** — `# {slug} — {Full Name}`
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

- `finalize` — verify → commit → push → merge → docs → cleanup ceremony. Cited by `/land`, `/crank`, `/code release`.
- `workflow` — canonical state graph for a unit of work, Definition of Ready, per-surface mappings. Cited by `[[DAS Backlog]]`, `feature/SKILL.md`, `/groom`, `/mint`, `/finalize`.

(Note: `ask-questions` was a discipline in earlier versions; it was promoted to the user-invocable `/ask` skill 2026-04-30 — see F10. Skills that previously cited `~~[[ask-questions]]~~` now invoke `/ask`.)

### Parallel user docs — required

**Every discipline must ship with a parallel user-facing doc**, the same shape as user-invocable skills. The two files are:

| File | Audience | Content |
|---|---|---|
| `~/.claude/skills/{name}/SKILL.md` | Agent | Full methodology, decision tables, edge cases, anti-patterns. Loaded when a citing skill activates the discipline. |
| `docs/<domain>/DAS <Name>.md` (dans-anchor-system repo) | User | Concept-focused. What the discipline does, when the user notices it, the format/output the user sees, what to do in response. Shorter than the agent doc. |

The user doc is what surfaces in the [[DAS Skills]] kind index (the user-facing skills index). The agent doc never appears there directly — only via citations from other skills.

### H1 convention — no slash on disciplines

User-invocable skills have a slash command, so their user-doc H1 is `# /Name` (e.g., `# /Audit`, `# /Ready`). The slash mirrors what the user actually types.

Disciplines are NOT invocable, so a slash in the H1 would be a small lie. **Discipline user-doc H1s use `# Name Discipline`** — no slash, with the "Discipline" suffix making the kind explicit and matching the agent SKILL.md's H1. Examples: `# Ask-Questions Discipline`, `# Finalize Discipline`, `# Workflow Discipline`.

### Why disciplines are not user-invocable

A discipline is a *rule the agent follows*, not a command the user issues. Making it `user_invocable: true` would imply the user can run it as a one-shot, but the discipline only makes sense in context (during a feature design, mid-implementation, etc.). The relevant trigger is *the situation*, not a user invocation.

### When to make something a discipline vs. a skill

- **Skill** (`user_invocable: true`) — has a clear "do this thing now" semantic. The user invokes it. Examples: `/audit`, `/groom`, `/feature`.
- **Discipline** (`user_invocable: false`) — a methodology that other skills follow. The user doesn't invoke it; skills cite it. Examples: `finalize`, `workflow`, `backlog-horizons`.
- **Both?** — if a single concept has both a "the user wants to run this now" form and an "agent always follows this when applicable" form, split into a skill + discipline pair (e.g., `/finalize` could in principle be invoked, but the *ceremony* is the discipline; we kept only the discipline form for now).

# Skill dossier page — the `DAS <Name>` doc

Distinct from the `SKILL.md` runbook specified above: every skill also has a **concept dossier** — `docs/<domain>/DAS <Name>.md` in the dans-anchor-system repo — the user-facing entry for the skill. It is a flat page (not a folder anchor) opening with a hub content-table, per the F229 flat-by-kind structure: category lives in the `<domain>` folder + the [[DAS Skills]] kind index, not a per-skill folder tree.

**Hub-table rows** on the dossier page (a content table, not an anchor dispatch table):

1. **breadcrumb** — `… → [[DAS]] → DAS <Name>`.
2. **Related** — **always links the actual skill runbook**: `[[skills/<name>/SKILL.md\|SKILL]]`. This is the rule — every skill doc points at its runbook, and that is the minimum Related row.
3. **Design** — links the design root, `~~[[DAS <Name> Design|Design]]~~` in `design/<domain>/`. The Design row carries **only the design elements that actually exist** (PRD, decisions, discussion); the minimum is the design root alone.
4. **Facet** — links the skill's paired facet/ruleset when one exists (e.g. `/groom` ⟷ [[DAS Backlog]]).

**Summary line** — the one sentence directly under the H1 states the skill's **essence** — what the command does at its core, per [[DAS Anchor Page]] R-anchor-page-06. Convention: lead with the backticked command, e.g. `/feature` — creates a new feature document specifying work to be done — not a feature list or mechanism tour.

**Body** — below the hub table, the skill's user-facing guide. It ranges from a one-line summary (minimal) to a full guide with `## What it does` / `## When NOT to use` sections (maximal). Genuine guide prose **stays**; enumerations that belong to *other* skills do not (they route to those skills — e.g. `/mint`'s page must not list `/code` / `/spike` / `/forge`).

**Design root** — `design/<domain>/DAS <Name> Design.md` exists **only once there is design material** (PRD, decisions, design discussion). Emptiness-until-needed is a *rule, not text*: do **not** write a "this is the design surface, empty until the pieces are needed" sentence into each one — the name says it. When material arrives it lands as rows in the design root, and the dossier's Design row lists what now exists.

**Examples — minimal and maximal:**

- **Minimal skill** → [[DAS Mint]]: dossier page (breadcrumb + Related + Design). The floor.
- **Maximal skill** → [[DAS Groom]]: the same skeleton, but a full user-guide body plus PRD + shared resolution-layer design in its Design row.

## SKA anchors own Design, not Track — shared by skills, facets, disciplines

A skill anchor — like **every** SKA sub-project anchor — **owns its own design but never its own tracking.** Activity-tracking for the whole skills ecosystem is centralized on the shared SKA surface ([[SKA Decisions|D08]]); a skill carries a `{slug} Design/` folder (minimum: just an `.anchor`, growing as design docs are earned), **no `{slug} Track/`**, and **no `{slug} Status.md`** (design-phase completeness is tracked only for SKA-the-project, not per sub-project). **Facets ([[DAS Facet]]) and disciplines share this exact strategy** — the single normative rule lives on the anchor-page facet as `R-anchor-page-subproject` ([[DAS Anchor Page]]); this section is the skill-facet pointer to it. The design surface is flat (`{slug} Design/` directly under the anchor, no `{slug} Docs/` wrapper).

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this SKILL.md spec. The normative contract is the body + RULESET R-skill-md above.)*

- **Inclusion test** — a rule belongs here only if it governs *the SKILL.md entry-point file itself*: frontmatter shape, section sequence, action-file naming, reference-subdirectory conventions, the discipline-vs-skill split, the dispatch protocol. Per-action workflow, per-skill reference data, and per-anchor structure rules do NOT belong here.
- **Keep content that belongs elsewhere out** — anchor-page format → [[DAS Anchor Page]] (the "F060 — SKILL.md is exempt" callout is the canonical pointer to where anchor-page rules diverge from SKILL.md rules); markdown-rendering → [[R-markdown]]; per-trait rules (every Skill anchor has X) → the relevant trait spec; project-wide rules → CLAUDE.md. Don't split the discipline user-doc requirement (parallel `DAS <Name>.md` + no-slash `# Name Discipline` H1) out of R-skill-md-05.
- **Reference Example block is load-bearing** — the escaped `\#` headings inside the code-fenced YAML block are intentional: they prevent the example sections from being parsed as real H1/H2 headings in this spec. Do not unescape them.
- **Cross-reference integrity** — when this spec changes (new required section, renamed field, new convention), audit every existing `~/.claude/skills/*/SKILL.md` and the CAB Base / CAB All Files dispatch tables for drift before considering the change shipped.
