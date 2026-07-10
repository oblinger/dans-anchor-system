---
description: "the anchor traits — declarable specializations of an anchor"
---

# TRT - Traits
The declarable properties an anchor carries in its `.anchor` `traits:` key — each specializes the [[Common Anchor Blueprint]].

| -[[TRT]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[traits]] → [TRT](hook://p/TRT)<br>: the anchor traits — declarable specializations of an anchor |
| --- | --- |
| Related | [[SKL\|Skills]],  [[FCT\|Facets]],  [[DSC\|Disciplines]],  [[LBR\|Library]],  [[DAS\|ob-skills]],   |

All anchor types follow the [[Common Anchor Blueprint]]. Each type adds specializations:

- **[[Simple Anchor]]** — Just the folder and anchor page. No repo, no docs folder.
- **[[Topic Anchor]]** — Evergreen knowledge area. No repo, but has standard `{slug} Docs/` structure. Anchor page is a routing hub to child anchors.
- **[[Code Anchor]]** — Has a code repository, declared by the `code:` key in `.anchor`. Inline mode (`code: .`, repo = anchor folder) or linked mode (`code: <path>`, repo typically at `~/ob/proj/`). Replaces the former Private Repo, Public Repo, and Split Anchor types.
- **[[Paper Anchor]]** — Iterative document revision with version table and section-based editing.
- **[[Skill Anchor]]** — Claude Code skill group in `~/.claude/skills/`. Entry point is `SKILL.md`, not a marker file.

The five above are **identity traits** — single-valued ("at most one of {Simple, Topic, Code, Paper}"; Skill composes). **Capability traits** layer on top of an identity trait (cardinality many):

- **[[Track]]** — the anchor is driven through a planning + backlog lifecycle (the "drive loop"). Co-requires the Backlog facet; composes with Topic / Code / Paper / Skill; excludes Simple. Its tree is the `{slug} Plan/` folder (rename to `{slug} Track/` deferred).
- **[[Collection]]** (`collection`) — the anchor *enumerates a collection of members of a like kind* — an expected, usually-one member type (a **union** is fine; the trivial "they're all markdown pages" does **not** count). Declared by `collection` in `.anchor`'s `traits:`. **Semantic, not layout** — it asserts the members share a kind; the dispatch-table *shape* (compact `...` / auto-list `| --- | |` / grouped `+`) is **read off the table, never declared**, and auto-graduates by size. Composes freely with any identity — commonly [[Topic Anchor]] (a topic that is *also* a like-kind set, e.g. `RR Papers`) or [[Simple Anchor]]; no exclusions, per [[CAB Aspects]] § Governing principle. Datedness is orthogonal ([[file-association]]). Examples: [[Espresso]], [[HBR Log]], every `* Features` / `* Log` / `* Roadmap`. Contrast a heterogeneous routing-hub Topic (`RR`, `MY`, bare `Log`) which is *not* a collection. Per [[SKA Decisions]] D11 + [[F152 — Set Anchor trait — homogeneous-collection anchor kind; dispatch-organization via existing disciplines|F152]].

**Git-aspect traits** (mutually exclusive — exactly one per anchor, per [[CAB Aspects]] composability matrix) shape how the agent handles git boundaries (per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] v2 architecture, Q12 resolved 2026-06-01):

- **[[Commit]]** — agent commits at logical boundaries without asking; new-commit-on-top, never amends; never auto-pushes. **Default for Code anchors.** Requires `Code`; excludes `PR` and `NoGit`. Spec: [[SKL Mode Git Commit]].
- **[[PR]]** — every state-touching commit gated through a pull request on its own branch with user review before further work continues. For high-blast-radius repositories. Requires `Code` and a PR-capable host; excludes `Commit` and `NoGit`. Spec: [[SKL Mode Git PR]].
- **[[NoGit]]** — anchor has no per-anchor git repository; the agent performs no git operations on it. **Default for non-Code anchors.** Excludes `Code`, `Skill`, `Commit`, `PR`.

**Cadence traits** (mutually exclusive — exactly one per anchor at a time) shape the agent's recurring trade-off posture:

- **[[Drive]]** — agent-driven, optimistic, minimum-interruption posture. **System default.** Excludes `Lean`. Spec: [[SKL Mode Drive]]; F091 `compact` trigger inlines the load-bearing rules at POST-COMPACT.
- **[[Lean]]** — cautious, distrust-the-foundation, fortify-before-adding posture. Used when work has stopped converging. Per-turn invocation via `/fortify`; declarative per-anchor activation via `Lean` in `traits:`. Excludes `Drive`.

## Traits vs. facets

A *trait* is a declarable property of the **anchor** (in `.anchor`'s `traits:`); a *facet* is a per-doc shape applied to a **file** inside the anchor (e.g. Backlog, Rules, Decisions, API Doc). Traits often *require* certain facets — e.g. Track requires the Backlog facet. The trait declares *what the anchor is*; the facet declares *what one file inside it looks like*.

# BRIEF

*(Maintainer note — this is a routing catalog, not per-trait spec: each trait's full spec lives in its own [[<Trait>]].md, operational mode behavior in `SKL Mode <Trait>.md`, trait-wide validation rules in an `R-<trait>` ruleset ([[DAS Ruleset]]), and composability/exclusion rules in [[CAB Aspects]]. Keep catalog rows terse — a one-line composability note plus a wiki-link to the spec.)*

- **Adding a new trait** — (1) decide category + composability rule (excludes/requires/defaults); (2) create `[[<Trait>]].md` with the spec (what it adds, when it applies, examples); (3) add a bullet to the right section of this catalog; (4) update [[CAB Aspects]]'s composability matrix; (5) author `SKL Mode <Trait>.md` if it carries operational mode behavior; (6) add an `R-trait-<name>` ruleset if it warrants validation.
