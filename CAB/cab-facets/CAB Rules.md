---
description: per-anchor rules file — design principles, structural rules, and code rules
---

# CAB Rules

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Rules.md`


The per-anchor Rules file (`{NAME} Rules.md`) is the single destination for everything `/audit rules` and `/rule check` enforce. It has three fixed sections in a fixed order.

**Working example:** [`~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Rules.md`](../../CAE/CAE%20Docs/CAE%20Plan/CAE%20Rules.md) — a complete rules file with all three sections populated.

Below is a condensed reference for the format.


# Reference Example
---

```markdown
# {NAME} Rules

## Design Principles

### P01 — One Queue, One Clock

All scheduling decisions flow through a single priority queue ...

**Why:** parallel scheduling paths diverge under load ...

**Encoded by:** R01, R02


## Structural Rules

### R10 — Every Markdown File Prefixed with `{NAME}`

**RULE:** Every `.md` file and subfolder inside the anchor uses the `{NAME}` prefix ...

**Check pattern:** Walk the anchor tree ...

### Exceptions

_None._


## Code Rules

### R01 — One Queue, One Clock (encodes [[#P01 ...|P01]])

**RULE:** All task scheduling flows through `TaskScheduler.queue` ...

**Check pattern:** Grep for `PriorityQueue`, `BinaryHeap<Task` ...

### Exceptions

| ID    | File                  | Line | Grade | Summary                 |
| ----- | --------------------- | ---- | ----- | ----------------------- |
| EX001 | `src/cli/progress.rs` | 42   | B     | UI refresh tick ...     |

**EX001 — `src/cli/progress.rs:42`**

- **Summary:** Progress bar refresh uses `thread::sleep` ...
- **Purpose:** Human-readable animation; not coordinating with scheduling.
- **Keep:** Yes. Test coverage does not depend on wall-clock time.
- **Alternative:** Could route through `Clock`, but ...
- **Gain/Loss:** Keeping saves an architectural layer ...
```

---



# Format Specification

## Location

`{NAME} Rules.md` lives inside `{NAME} Docs/{NAME} Plan/`. It is declared in `.anchor` as:

```yaml
rules: {NAME} Docs/{NAME} Plan/{NAME} Rules.md
```

The Plan folder location is deliberate — it applies to every anchor trait, not just `code`. A simple, topic, or paper anchor still has structural rules (naming, markdown formatting) even with zero code.

## Section Ordering — Fixed

Three sections in this order:

1. **Design Principles** — project philosophy (`P01`, `P02`, ...). Canonical source; nothing else in the anchor restates a principle.
2. **Structural Rules** — naming, markdown, dispatch-table, docs-sync checks (`R10`, `R11`, ...). Apply regardless of trait.
3. **Code Rules** — code-specific checks (`R01`–`R09`). Present only if the `code` trait is active.

`/audit rules` and `/rule check` rely on this ordering to find their scan targets. Don't reorder, don't split, don't rename the H2 headings.

## ID Scheme

- **Principles:** `P01`, `P02`, ... — never change once assigned.
- **Code rules:** `R01`–`R09` — reserved for code-specific rules.
- **Structural rules:** `R10` onward — start at R10 so code and structural rules share one numbering space but are visually separable.
- **Exceptions:** `EX001`, `EX002`, ... — globally unique across the anchor. Source-code comments use `// EX001` to tag the intentional violation.

## Single Source of Truth — Design Principles

Principles are stated once, in this file, under `## Design Principles`. System Design, Architecture, and the anchor page reference them by ID with a wiki-link — they do *not* restate the principle.

Cross-references from elsewhere:

```markdown
- **[[{NAME} Rules#P01 — One Queue, One Clock|P01]]** — realized by ...
```

This keeps the philosophy editable in exactly one place. Changing a principle means changing one file; drift between docs cannot happen.

## Principle Declaration

Each principle:

- **H3 heading** — `### P{NN} — Short Name`
- **Statement paragraph** — one paragraph declaring the principle
- **Why:** — the rationale (short, what incident or reasoning drove this)
- **Encoded by:** — comma-separated list of R-rule IDs that enforce it

A principle with no encoded rules is aspirational, not enforced. That's sometimes fine during design, but `/audit rules` flags it as a drift risk.

## Rule Declaration

Each rule:

- **H3 heading** — `### R{NN} — Short Name`, optionally suffixed with `(encodes P{NN})` and a wiki-link to the principle when the rule encodes one
- **RULE:** — the declarative statement; must be grep-able or describable as a pattern that `/rule check` can operationalize
- **Check pattern:** — how `/rule check` looks for violations (grep patterns, semantic cues)
- **Exceptions** — table `| ID | File | Line | Grade | Summary |`, one row per exception
- **Per-exception block** — `**EXxxx — path:line**` followed by:
  - **Summary** — what the violation is
  - **Purpose** — why the code does this
  - **Keep** — Yes/No, should we keep it
  - **Alternative** — what the rule-compliant version would look like
  - **Gain/Loss** — the tradeoff of keeping vs. fixing

Exceptions with no per-exception block are incomplete — `/rule triage` flags them.

## Lifecycle

- **Create** when the anchor is set up (skeleton with empty sections)
- **Fill in Design Principles** during `/code architect` or when the user says "these are our principles"
- **Add Code Rules** as they come up — often in response to a bug that illuminates the missing rule
- **Add Structural Rules** are mostly inherited from CAB conventions; project-specific additions go here
- **Exceptions accumulate** when `/rule check` finds a violation the team decides to keep — always with a grade and the full per-exception block

The rules file is a living document. It should be edited with every PR that changes architectural decisions.
