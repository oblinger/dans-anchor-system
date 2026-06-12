# Curate — Walk a discovery report and assemble per-trait rule sets

Phase 2 of [[F082 — Common rule set across projects]]. Reads the report produced by `/rule discover`, walks the user through each multi-rule cluster within each trait, helps name candidate rule sets, and writes the canonical sets to `~/.claude/skills/rule/sets/<trait>/<set-name>.md`.

## When to Use

After running `/rule discover` and reading the report. The user wants to consolidate the rules they've authored across anchors into reusable per-trait rule sets.

## Runbook (agent-driven flow)

### 1. Load the discovery report

```
~/.config/ob-skills/rule/discovery-report.md
```

If missing, fall back to a freshly-run discovery (invoke `/rule discover`). If present, check the date in the H1 — if stale (> 1 day) or the user wants a fresh sweep, re-run discovery first.

### 2. Identify candidate rule sets

For each trait section in the report, identify the **multi-rule clusters** (Cluster N where the bullet list has more than one rule). Each is a candidate rule set — multiple anchors authored similar rules, so the cluster is a natural canonical-set seed.

Also surface the user-added rules from online literature (the user manually edits `~/.claude/skills/rule/sets/<trait>/<set>.md` files outside this flow; the curate step doesn't capture those, but the user may want to merge a new discovery cluster with an existing set they've already drafted).

### 3. Walk the user through each candidate

Per cluster, present:
- The cluster's representative rule (the first rule found, used as the cluster name).
- All rules in the cluster, with their anchor sources.
- A proposed set name (the agent suggests; user confirms or overrides).
- The destination path (`~/.claude/skills/rule/sets/<trait>/<set>.md`).

The user decides:
- **(A) Adopt** — create the set file at the destination; agent writes the H1, the trait+description frontmatter, and the rules (preserving R-numbers OR re-numbering per the new set's policy).
- **(B) Merge** — append into an existing set file. User picks which.
- **(C) Skip** — don't promote this cluster (one-off rules, not generalizable).
- **(D) Split** — the cluster combined unrelated rules; user separates them into distinct candidate sets.

This is a multi-step conversation; the agent shouldn't bulk-create sets without the user's confirmation on each cluster.

### 4. Write the set file(s)

Each rule set is a standalone markdown doc:

```markdown
---
description: <one-line description of when this set applies>
trait: <Trait name — matches the parent folder>
applies-when: <condition string — used by /rule consider to match projects>
---

# <Trait>/<set-name> — <Title>

Brief paragraph: what this set is, when it applies.

### R-<SET>01 — <rule name>
RULE: <declaration>.
<optional explanatory paragraph>

### R-<SET>02 — <rule name>
RULE: <declaration>.

...
```

Conventions:
- **Filename** is kebab-case: `frontend.md`, `cloud-backend.md`, `cli-tool.md`.
- **Frontmatter `trait:`** matches the parent folder name (e.g., `trait: Code`). Lets `/rule consider` filter rulesets by an anchor's traits.
- **`applies-when:`** is a condition string `/rule consider` uses to match projects (e.g., "Project uses a UI framework"). Free-form prose; the agent interprets.
- **R-numbers** use a set-scoped prefix (e.g., `R-FE01`, `R-FE02`) so a project carrying multiple sets doesn't collide.
- **Preserve the source rule's wording** as much as possible; condense where multiple anchors had the same idea worded differently.

### 5. Surface the manifest

After all clusters are walked, list the sets created/updated in chat:

```
/rule curate — created/updated 3 rule sets:
  - sets/Code/frontend.md (5 rules)
  - sets/Code/cloud-backend.md (4 rules)
  - sets/Skill/anchor-shape.md (3 rules)
```

Commit. The library lives in the skills repo, so committed sets ship to other machines on the next pull.

## Conventions

### Multiple sets per trait — design intent

A trait may carry many rule sets, each covering a different sub-style. Examples:

- `Code/frontend.md` — UI-framework conventions (React/Svelte/Vue patterns).
- `Code/cloud-backend.md` — server-side service conventions (logging, retries, observability).
- `Code/cli-tool.md` — command-line tool conventions (XDG paths, exit codes, flags).

Different code anchors adopt different combinations. Per [[F082]] Q5/Q6: this is the design.

### Versioning

Rule sets are version-controlled with the skills repo (`ob-skills`). When the user revises a set, the commit message captures the intent. The eventual `/rule sync` (F082 v2) will respect set versions via the three-way merge.

### Online-literature rules

Per [[F082]] Q6: the user can add rules from online literature directly to a set file (hand-edit) without going through discover-then-curate. Those rules don't appear in any anchor's `rules/` folder; they enter the library because the user typed them in.

## What this skill does NOT do

- It doesn't propagate sets to projects. That's `/rule sync` (F082 v2).
- It doesn't run the discovery sweep itself — invoke `/rule discover` first.
- It doesn't enforce rule-numbering conventions across all sets — each set is locally consistent (R-FE01, R-FE02) but R-numbers may collide across sets when projects compose multiple sets. (That's expected; the project-side `/rule check` resolves by source-set.)

## Related

- [[F082 — Common rule set across projects]] — the feature this implements (Phase 2).
- `/rule discover` — Phase 1 (produces the input report).
- `/rule consider` — pre-existing; recommends curated sets for a project (Phase 3-ish; user-controlled adoption).
- `/rule sync` — v2 of F082; intelligent three-way-merge distribution.
