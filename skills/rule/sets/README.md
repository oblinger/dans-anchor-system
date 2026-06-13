# sets/ — Canonical per-trait ruleset library

This folder holds **canonical rulesets**, organized per trait (per [[F082]] Q5 + [[F090 — Retire CAB Types, unify under Traits, Facets-as-Traits-by-file-existence|F090]] unified trait taxonomy). Each set is a standalone markdown doc declaring rules that apply to a specific style of anchor.

## Layout

```
sets/
├── README.md            ← this file
├── Code/
│   ├── frontend.md      ← rules for UI-framework code anchors
│   ├── cloud-backend.md ← rules for backend service code anchors
│   └── cli-tool.md      ← rules for command-line tool code anchors
├── Skill/
│   └── anchor-shape.md  ← rules for skill anchors
├── Topic/
└── Paper/
```

- **Trait folders** match trait names per the [[CAB Traits]] taxonomy (post-F090: Code / Skill / Topic / Paper / Simple, plus file-existence traits where applicable).
- **Set files** are kebab-case `.md` files inside the trait folder. Multiple sets per trait are expected — different sub-styles within a trait have different rule needs.

## File format

Each set file:

```markdown
---
description: <one-line description of when this set applies>
trait: <Trait name — matches parent folder>
applies-when: <condition string for /rule consider>
---

# <Trait>/<set-name> — <Title>

Brief paragraph: what this set is, when it applies.

### R-<SET>01 — <rule name>
RULE: <declarative constraint>.
<optional explanatory paragraph>

### R-<SET>02 — <rule name>
RULE: <declarative constraint>.

...
```

Conventions:
- **Set-scoped R-numbers** (e.g., `R-FE01`, `R-CB01`) — collision-safe when a project composes multiple sets.
- **`trait:`** must match the parent folder name; `/rule consider` filters sets by an anchor's declared traits.
- **`applies-when:`** is free-form prose; `/rule consider` reads it to recommend sets that match a project's characteristics.

## How sets are populated

- **`/rule discover`** — walks the vault, finds existing rules across anchors, groups by trait + similarity, emits a report.
- **`/rule curate`** — walks the discover report with the user, names + assembles candidate sets, writes them here.
- **User direct authoring** — for rules sourced from online literature / external sources, the user can hand-edit set files directly.

## How sets are consumed

- **`/rule consider`** (pre-existing) — reads sets, recommends which apply to a project, applies approved ones into the project's `rules/` folder.
- **`/rule sync`** (F082 v2) — intelligent three-way-merge distribution of canonical sets into project copies; respects user-local edits.
- **`/rule suggest`** (F082 v2) — given a project's traits, proposes which sets to adopt and changes to existing sets.

## State of the library (as of F082 v1)

The library is **bootstrapping**. F082 v1 ships `/rule discover` + `/rule curate` to produce the initial sets; the user runs them to populate the trait folders. Pre-existing rulesets at `~/.claude/skills/rule/rulesets/` (oblinger-rules.md, xdg-config.md) are NOT migrated by F082 v1 — they continue to coexist; future cleanup may consolidate.

## Related

- [[F082 — Common ruleset across projects]] — the feature commissioning this library.
- [[F090 — Retire CAB Types, unify under Traits, Facets-as-Traits-by-file-existence]] — provides the trait taxonomy.
- [[CAB Traits]] — the canonical trait taxonomy.
