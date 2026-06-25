---
description: "the Skill primitive — SKILL.md entry-point structure and conventions"
---
# FCT Skill
An omnibus Claude Code skill that groups related actions, reference data, and scripts under a single `/name` command. Invoked via `/name action` (e.g., `/cab setup`, `/md toc`).

| -[[FCT Skill]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Primitives]] → [FCT Skill](hook://p/FCT%20Skill)<br>: the Skill primitive — SKILL.md entry-point structure and conventions |
| --- | --- |
| Related | [[FCT Facet]],  [[FCT Ruleset]],  [[FCT Primitives]],  [[CAB Aspects]],   |
| Examples | [[CAE Skill\|canonical exemplar]],  [[CAE Minimal Skill\|minimal capsule]],   |

**TLDR** — Every skill anchor ships a `SKILL.md` with fixed frontmatter (`name`, `description`, `tools`, `user_invocable`) and a fixed section order (Title → Brief → dispatch tables → Actions → Reference → Dispatch protocol). Disciplines (`user_invocable: false`) additionally require a parallel user-facing doc at `SKL User Docs/SKL Skills/SKL <Name>.md`. **Cardinality: one per anchor** — each skill folder has exactly one `SKILL.md` entry point.

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

**F060 — SKILL.md is exempt.** SKILL.md is the Claude Code skill entry point; its frontmatter has fixed required fields (`name`, `description`, `tools`, `user_invocable`) and the body has a fixed structure (Title → Brief → dispatch tables → Actions → Reference → Dispatch protocol). The F060 dispatch-table placeholder rule applies to the **anchor root page `{Slug}.md`** (e.g., `Groom.md`) for skill anchors, not to SKILL.md itself.

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

- `finalize` — verify → commit → push → merge → docs → cleanup ceremony. Cited by `/land`, `/crank`, `/code release`.
- `workflow` — canonical state graph for a unit of work, Definition of Ready, per-surface mappings. Cited by `[[CAB Backlog]]`, `feature/SKILL.md`, `/groom`, `/mint`, `/finalize`.

(Note: `ask-questions` was a discipline in earlier versions; it was promoted to the user-invocable `/ask` skill 2026-04-30 — see F10. Skills that previously cited `[[ask-questions]]` now invoke `/ask`.)

### Parallel user docs — required

**Every discipline must ship with a parallel user-facing doc**, the same shape as user-invocable skills. The two files are:

| File | Audience | Content |
|---|---|---|
| `~/.claude/skills/{name}/SKILL.md` | Agent | Full methodology, decision tables, edge cases, anti-patterns. Loaded when a citing skill activates the discipline. |
| `~/.claude/skills/SKL User Docs/SKL Skills/SKL <Name>.md` | User | Concept-focused. What the discipline does, when the user notices it, the format/output the user sees, what to do in response. Shorter than the agent doc. |

The user doc is what surfaces in the SKL dispatch table (the user-facing skills index). The agent doc never appears there directly — only via citations from other skills.

### H1 convention — no slash on disciplines

User-invocable skills have a slash command, so their user-doc H1 is `# /Name` (e.g., `# /Audit`, `# /Ready`). The slash mirrors what the user actually types.

Disciplines are NOT invocable, so a slash in the H1 would be a small lie. **Discipline user-doc H1s use `# Name Discipline`** — no slash, with the "Discipline" suffix making the kind explicit and matching the agent SKILL.md's H1. Examples: `# Ask-Questions Discipline`, `# Finalize Discipline`, `# Workflow Discipline`.

### Why disciplines are not user-invocable

A discipline is a *rule the agent follows*, not a command the user issues. Making it `user_invocable: true` would imply the user can run it as a one-shot, but the discipline only makes sense in context (during a feature design, mid-implementation, etc.). The relevant trigger is *the situation*, not a user invocation.

### When to make something a discipline vs. a skill

- **Skill** (`user_invocable: true`) — has a clear "do this thing now" semantic. The user invokes it. Examples: `/audit`, `/groom`, `/feature`.
- **Discipline** (`user_invocable: false`) — a methodology that other skills follow. The user doesn't invoke it; skills cite it. Examples: `finalize`, `workflow`, `backlog-horizons`.
- **Both?** — if a single concept has both a "the user wants to run this now" form and an "agent always follows this when applicable" form, split into a skill + discipline pair (e.g., `/finalize` could in principle be invoked, but the *ceremony* is the discipline; we kept only the discipline form for now).

# Skill anchor page — the `SKL <Name>` doc

Distinct from the `SKILL.md` runbook specified above: every skill also has a **doc / anchor page** in the SKL tree — `SKL <Name>` — the user-facing entry for the skill. It is a **sub-project** anchor page ([[FCT Anchor Page]] → `R-anchor-page-subproject`): a folder anchor with a switchboard masthead plus a body that is the skill's user guide.

**A skill is a folder.** Minimal shape:

- `SKL <Name>/`
  - `SKL <Name>.md` — the entry page
  - `SKL <Name> Design.md` — the **design root** (a child anchor page)
  - `.anchor`

**Masthead rows** on the entry page (a [[FCT Dispatch Table]]):

1. **breadcrumb** — `… → [[SKL <Group>]] → SKL <Name>`.
2. **Related** — **always links the actual skill runbook**: `[[skills/<name>/SKILL.md\|SKILL]]`. This is the rule — every skill doc points at its runbook, and that is the minimum Related row.
3. **Design** — links the design root, `[[SKL <Name> Design\|Design]]`. The Design row carries **only the design elements that actually exist**; the minimum is the design root alone.

**Summary line** — the one sentence directly under the H1 states the skill's **essence** — what the command does at its core, per [[FCT Anchor Page]] R-anchor-page-06. Convention: lead with the backticked command, e.g. `/feature` — creates a new feature document specifying work to be done — not a feature list or mechanism tour.

**Body** — below the masthead, the skill's user-facing guide. It ranges from a one-line summary (minimal) to a full guide with `## What it does` / `## When NOT to use` sections (maximal). Genuine guide prose **stays**; enumerations that belong to *other* skills do not (they route to those skills — e.g. `/mint`'s page must not list `/code` / `/spike` / `/forge`).

**Design root** — `SKL <Name> Design.md` is itself an anchor page that is **empty until there is design material** (PRD, decisions, design discussion). Emptiness-until-needed is a *rule, not text*: do **not** write a "this is the design surface, empty until the pieces are needed" sentence into each one — the name says it. When material arrives it lands as rows in the design root, and the parent's Design row lists what now exists.

**Examples — minimal and maximal:**

- **Minimal skill** → [[SKL Mint]]: folder + entry page (breadcrumb + Related + Design) + empty design root. The floor.
- **Maximal skill** → [[SKL Ask]]: the same skeleton, but a full user-guide body; its design root fills in once a PRD / decisions / discussion exist.

## SKA anchors own Design, not Track — shared by skills, facets, disciplines

A skill anchor — like **every** SKA sub-project anchor — **owns its own design but never its own tracking.** Activity-tracking for the whole skills ecosystem is centralized on the shared SKA surface ([[SKA Decisions|D08]]); a skill carries a `{NAME} Design/` folder (minimum: just an `.anchor`, growing as design docs are earned), **no `{NAME} Track/`**, and **no `{NAME} Status.md`** (design-phase completeness is tracked only for SKA-the-project, not per sub-project). **Facets ([[FCT Facet]]) and disciplines share this exact strategy** — the single normative rule lives on the anchor-page facet as `R-anchor-page-subproject` ([[FCT Anchor Page]]); this section is the skill-facet pointer to it. The design surface is flat (`{NAME} Design/` directly under the anchor, no `{NAME} Docs/` wrapper).

# RULESET R-skill-md
include::
where:: file:{ANCHOR}/SKILL.md
description:: the `SKILL.md` entry-point structure for a Claude Code skill

What `/audit` checks on a skill's `SKILL.md` entry point. Cardinality: one per skill anchor. Format of this set: [[FCT Ruleset]].

### RULE R-skill-md-01 — Frontmatter declares name / description / tools / user_invocable (checked)

`SKILL.md` opens with YAML frontmatter carrying the required fields `name`, `description`, `tools`, and `user_invocable`.

**Check pattern:** frontmatter parses; all four keys are present and non-empty.

### RULE R-skill-md-02 — Sections appear in the fixed order (checked)

The body follows the fixed sequence: Title (`# {NAME} — {Full Name}`) → Brief → optional dispatch table → Actions → Reference → optional Topics → optional Scripts → Dispatch protocol.

**Check pattern:** the H1/H2 sequence is a subsequence of that fixed order; no foreign top-level section interleaves.

### RULE R-skill-md-03 — Ends with the 4-step dispatch protocol (checked)

`SKILL.md` ends with the standard dispatch protocol: parse the argument, look up the file in the Actions table, read + execute it, else show the dispatch table.

**Check pattern:** a `## Dispatch` section is the final section and enumerates the 4 steps.

### RULE R-skill-md-04 — Action files are lowercase-hyphenated `{name}-{action}.md` (checked)

Each action referenced in the Actions table is its own file named `{name}-{action}.md` (lowercase, hyphenated); reference-data files keep their original names — the casing distinguishes actions from reference data.

**Check pattern:** every Actions-table target resolves to a `{name}-*.md` file in the skill root.

### RULE R-skill-md-05 — A discipline (`user_invocable: false`) ships a parallel user doc and a no-slash H1 (checked)

A discipline carries `user_invocable: false`, no Actions table, a parallel user-facing doc at `SKL User Docs/SKL Skills/SKL <Name>.md`, and a `# Name Discipline` user-doc H1 (no slash — a slash would imply it's invocable).

**Check pattern:** if `user_invocable: false`, assert the parallel `SKL <Name>.md` exists and its H1 is `# {Name} Discipline`.

# BRIEF

- **This is the CAB facet spec for SKILL.md** — the authority on the required frontmatter fields, fixed section order, and dispatch-protocol footer that every Claude Code skill entry-point file must conform to. Edits here change the contract every skill in `~/.claude/skills/` is audited against.
- **Inclusion test** — a rule belongs here only if it applies to *the SKILL.md entry-point file itself*: frontmatter shape, section sequence, action-file naming, reference-subdirectory conventions, the discipline-vs-skill split, the dispatch protocol. Per-action workflow content, per-skill reference data, and per-anchor structure rules do NOT belong here.
- **Do NOT inline content that belongs elsewhere** — anchor-page format → [[FCT Anchor Page]] (F060 placeholder rule); markdown-rendering rules → [[R-markdown]]; per-trait rules (every Skill anchor has X) → the relevant trait spec; project-wide rules → CLAUDE.md. The "F060 — SKILL.md is exempt" callout is the canonical pointer to where anchor-page rules diverge from SKILL.md rules.
- **Reference Example block is load-bearing** — the escaped `\#` headings inside the code-fenced YAML block are intentional: they prevent the example sections from being parsed as real H1/H2 headings in this spec. Do not unescape them.
- **Discipline pairing is part of this spec** — `user_invocable: false` SKILL.md files MUST ship a parallel user-facing doc at `SKL User Docs/SKL Skills/SKL <Name>.md` and use `# Name Discipline` H1 (no slash). Keep both halves of the rule together; don't split the user-doc requirement into a separate spec.
- **Cross-reference integrity** — when this spec changes (new required section, renamed field, new convention), audit every existing `~/.claude/skills/*/SKILL.md` and the CAB Base / CAB All Files dispatch tables for drift before considering the change shipped.
- **Body discipline** — keep the spec body lean; resist the urge to dump worked examples or migration notes into the body. The Reference Example + Format Specification + Disciplines sections are the canonical shape; new content lands as a new H2 only when it's a genuine structural rule.
