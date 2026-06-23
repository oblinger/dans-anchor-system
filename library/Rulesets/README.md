# sets/ — Canonical decision-set library

This folder holds **canonical decision sets** (post-F113 successor to `~/.claude/skills/rule/sets/`). Each set is a standalone markdown doc bundling related decisions that apply to a specific style of anchor or a specific cross-cutting concern.

Per [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture]] Phase 3: decision sets supersede rulesets. When an anchor pulls a set in, the set's decisions get renumbered into the anchor's local D-NN namespace and appended as an H2 grouping in `{NAME} Decisions.md` (per F113 Q2 — copy-in semantics).

## Layout

```
sets/
├── README.md            ← this file
│
│   # Trait-scoped sets (per CAB trait taxonomy)
├── Code/
│   ├── mac-app.md       ← macOS app development (signing, TCC, sandbox)
│   ├── ios.md           ← iOS app development (sibling to mac-app)
│   ├── rust.md          ← Rust crate development
│   ├── python.md        ← Python tooling and scripts
│   ├── shell.md         ← bash / zsh shell scripting
│   ├── frontend.md      ← TypeScript / React frontend
│   ├── cloud-backend.md ← backend service code anchors
│   └── cli-tool.md      ← command-line tool design
├── Skill/
│   ├── anchor-shape.md  ← skill-anchor structural shape
│   └── discipline.md    ← discipline-style skill conventions (ask-format / verification / mode style)
├── Topic/
├── Paper/
└── Simple/
│
│   # Cross-cutting category sets (not trait-scoped)
├── Doc/
│   ├── md-formatting.md          ← markdown formatting conventions
│   ├── progressive-disclosure.md ← citing the discipline as decisions
│   ├── wiki-links.md             ← Obsidian wiki-link conventions
│   └── file-naming.md            ← file and folder naming
├── Git/
│   ├── commit-discipline.md      ← commit-on-transition, no amend
│   ├── pr-workflow.md            ← PR-based development decisions
│   └── no-force-main.md          ← never force-push to main
├── Test/
│   ├── integration-not-mock.md   ← integration tests hit real systems
│   ├── deterministic.md          ← no clock / random dependence
│   └── property-based.md         ← proptest patterns
├── Process/
│   ├── feature-lifecycle.md      ← designing → ready → active → verify → done
│   └── verification-tiers.md     ← citing the verification discipline
├── Arch/
│   ├── factory-pegboard.md       ← factory pattern (per F108)
│   ├── interfaces-folder.md      ← single Interfaces/ folder
│   └── single-source-of-truth.md ← no duplicate code, use imports
│
│   # Owner-scoped sets (apply to one person's projects regardless of trait or domain)
└── Ob/
    └── ob.md                     ← Dan's personal cross-project decisions (markdown-valid-for-Obsidian, ...)
```

- **Trait-scoped folders** match trait names per the [[TRT]] taxonomy (post-F090: Code / Skill / Topic / Paper / Simple). Sets here apply when an anchor declares the matching trait.
- **Cross-cutting folders** are not trait-scoped — they apply across traits when the anchor opts in. Naming is by concern (Doc / Git / Test / Process / Arch).
- **Owner-scoped folders** are pulled in by every anchor a person owns, regardless of trait. (`Ob/` = Dan's personal set.)
- **Set files** are kebab-case `.md` files. Multiple sets per category are expected — different sub-styles within a category have different decision needs.


## File format

Each set file:

```markdown
---
description: <one-line description of when this set applies>
trait: <Trait name — matches parent folder, omit for cross-cutting sets>
applies-when: <free-form condition string for /decision consider>
set-id: <short-prefix used in D-numbering inside this set, e.g., MA for mac-app>
---

# <Folder>/<set-name> — <Title>

Brief paragraph: what this set is, when it applies.

### D-<SET>01 — <decision name> (<tier>)
<declarative decision>
**Why:** <reason>
**Check pattern:** <how to mechanically verify, for tracked / checked tiers>

### D-<SET>02 — <decision name> (<tier>)
...
```

**Conventions:**

- **Set-scoped D-numbers** — e.g., `D-MA01`, `D-MA02` for the mac-app set; `D-RUST01` for the rust set. Collision-safe when an anchor composes multiple sets, since each set's prefix differs.
- **Per F113 Q2:** at pull-in time, decisions get renumbered into the anchor's local D-NN namespace (e.g., `D-MA01` → `D17` in SKA's `Decisions.md`). The original `D-MA01` ID stays referenced in the H2 grouping header for traceability.
- **Tier annotation** — every decision carries `(tracked)` / `(checked)` / `(reviewed)` / `(stated)` per F113 Q1.
- **`trait:`** is required for trait-scoped sets; omitted for cross-cutting sets.
- **`applies-when:`** is free-form prose; future `/decision consider` reads it to recommend sets that match a project's characteristics.
- **`set-id:`** is the D-number prefix for decisions in this set. Keep short (2-5 chars).


## How sets are populated

- **`/decision discover`** (post-F113 successor to `/rule discover`) — walks the vault, finds existing decisions across anchors, groups by trait + similarity, emits a report.
- **`/decision curate`** — walks the discover report with the user, names + assembles candidate sets, writes them here.
- **User direct authoring** — for decisions sourced from user judgment or external literature, hand-edit set files directly. (Used for the initial Mac app coding set, 2026-06-05.)


## How sets are consumed

- **`/decision consider`** (post-F113 successor to `/rule consider`) — reads sets, recommends which apply to a project, applies approved ones into the anchor's `{NAME} Decisions.md`.
- **`/decision sync`** — three-way-merge distribution of canonical sets into anchor copies; respects user-local edits.
- **`/decision suggest`** — given an anchor's traits, proposes which sets to adopt.


## State of the library

**Bootstrapping** — populated as the user identifies decisions worth canonicalizing. Populated entries: `Code/mac-app.md` (2026-06-05) — D-MA01 no-ad-hoc-codesigning; `Ob/ob.md` (2026-06-06) — D-OB01 markdown-valid-for-Obsidian. The catalog above lists planned sets as folder/filename placeholders; populated entries get a one-line description added.


## Related

- [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture]] — the umbrella feature; Phase 3 commissions decision sets.
- [[F082 — Common ruleset across projects]] — F082 ships the predecessor `rule/sets/` library; F113 Phase 3 migrates it here.
- [[FCT Decisions]] — per-anchor Decisions facet spec.
- [[TRT]] — the canonical trait taxonomy.
