---
description: Validate the shape and wiki-link integrity of Architecture docs (`<NAME> Architecture.md` + reachable subsystem Arch docs). Two rules: diagram-then-table at top of doc, and wiki-links on every module reference in the component table. Auto-invoked by `/architect`; also runnable standalone.
---

# Audit Architecture — `/audit architecture`

Validates the shape contract of every reachable Architecture doc in the vault. Catches two structural drift modes that `/architect` doesn't currently enforce:

1. **Shape:** every Arch doc must begin with a block diagram (within the first 30 lines after H1), immediately followed by a markdown table (within 5 lines of the diagram). The diagram-then-table pattern is the doc's reader contract — "here's the shape; here's the legend."
2. **Wiki-link integrity:** every cell of the component table that names a vault file must be a wiki-link `[[X]]`, not plain text. The opt-out `[ext: <name>]` tag is available for legitimate external references.

Sibling of `/audit q` / `/audit markdown` / `/audit docs`. Spec: `[[F092 — Audit architecture]]`.

## When to invoke

- **Auto** — `/architect` (and every sub-skill: `/architect new`, `/architect update`, `/architect changes`, `/architect drift`) invokes this skill as its last step. Mirrors how `/triage` / `/groom` / `/mint` auto-invoke `/audit q` per the F076 Q6 post-condition.
- **Manual** — user types `/audit architecture` to re-check after fixing one doc by hand, or to scan from a known state before a refactor.

## Trigger

Slash-only: `/audit architecture [args]`. Not a DMUX prefix-trigger (the word "audit" and "architecture" are too common in natural speech).

## CLI

```
audit-architecture [--scope reach|anchor|file|all]
                   [--anchor NAME] [--file PATH]
                   [--fix] [--dry]
```

| Flag | Meaning |
|---|---|
| `--scope reach` | **Default.** From every anchor's main `<NAME> Architecture.md`, walk wiki-links to every reachable `<X> Architecture.md` / `<X> Arch.md`. |
| `--scope anchor --anchor SKA` | Reachability walk starting from that one anchor's main Arch doc. |
| `--scope file --file <path>` | Single-file audit. |
| `--scope all` | Every Arch-stem `.md` file in the vault (unreachable too). |
| `--fix` | Apply A3 auto-fixes — wrap unambiguous basenames in `[[...]]`. |
| `--dry` | Report-only; refuse to write. |

## Rules (v1)

| ID | Rule | Auto-fix? |
|---|---|---|
| **A1** | Block diagram present within the first 30 lines after H1. Accepted forms: `` ```mermaid `` code fence; wiki-link image embed `![[X.svg]]`; markdown image link `![alt](X.svg)`. Image extensions: `svg`, `png`, `jpg`/`jpeg`, `gif`, `webp`, `excalidraw`, `drawio`. | No (manual fix — add diagram). |
| **A2** | Markdown table starts within 5 lines after the diagram ends (allowing blank-line spacing). | No (manual fix — add table). |
| **A3** | Every cell of the component table that names a vault file (basename match) is a wiki-link `[[X]]`, not plain text. Exception: cells tagged `[ext: <name>]` opt out. | Yes — wrap unambiguous basenames in `[[...]]` if `--fix` is set. Ambiguous basenames (multi-anchor matches) are report-only. |
| **A4** | The diagram + table pair exists — Arch doc with ONE half of the shape is broken. | No (manual fix). |

## Detection — what's in scope

**Default `--scope reach`:**

1. Find every `.md` file whose basename ends with ` Architecture` (the main Arch docs).
2. From each, BFS-walk wiki-links to other Arch-stem docs (basename matches `<X> Architecture` or `<X> Arch`).
3. Audit the closure.

**Out of scope (always skipped):** files under `Versions/` (snapshot archives), `.history/` (md_history backups), `worktrees/` (agent worktrees), `.anchor.d/` (HA cache), `.build/`, `.cache/`, `target/`, `node_modules/`.

## Runbook

When invoked:

1. **Build the vault index** (via audit-q's `build_vault_index` primitive — shared).
2. **Collect targets** per `--scope`.
3. **For each target, audit:**
   - Find H1 (skipping YAML frontmatter).
   - Find block diagram in the first 30 lines after H1.
   - Find markdown table within 5 lines after the diagram.
   - For each table cell, find plain-text basenames that match vault files.
4. **Emit findings** with `A1`/`A2`/`A3`/`A4` codes.
5. **If `--fix`:** apply A3 wrap-in-brackets edits.
6. **Exit code:** 1 if errors, 0 otherwise. (Warnings don't trigger exit-1 — they're surfacing, not blocking.)

## Integration with `/architect`

Every `/architect` sub-skill (`new`, `update`, `changes`, `drift`) appends a post-condition step:

```bash
~/.claude/skills/audit/scripts/audit-architecture.py --scope reach
```

If findings are non-zero, the skill reports them inline but does **not** block the mint. The agent can address them in the same turn (when the violation is the agent's own work) or file them as a backlog row for downstream cleanup.

## Implementation

- Script: `~/.claude/skills/audit/scripts/audit-architecture.py` (~450 lines).
- Reuses audit-q.py primitives (`build_vault_index`, `links_in_file`, `headings_in`) via `importlib.util.spec_from_file_location` — the audit family shares the same vault-walk machinery.
- Findings dataclass parallel to audit-q's; report shape identical.

## Out of scope (v1)

- **Diagram content validation** — the rule checks shape (diagram present), not that the diagram is semantically correct.
- **Table content validation** — A3 covers wiki-link integrity in cells; column structure (e.g., "must have a Role column") is not enforced.
- **Bidirectional link verification** — auditing that `[[ComponentA]]` reciprocally lists this Arch doc in its own breadcrumb is out of scope for v1.
