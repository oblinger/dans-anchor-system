---
description: "the anchor traits — declarable properties an anchor carries in its `.anchor`"
---

# TRT - Traits
The declarable properties an anchor carries in its `.anchor` `traits:` key — each specializes the [[Common Anchor Blueprint]].

| -[[TRT]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [TRT](hook://p/TRT)<br>: the anchor traits — declarable specializations of an anchor |
| --- | --- |
| Related | [[SKL\|Skills]],  [[FCT\|Facets]],  [[DSC\|Disciplines]],  [[LBR\|Library]],  [[DAS\|ob-skills]],   |

All anchor types follow the [[Common Anchor Blueprint]]. Each type adds specializations:

- **[[Simple Anchor]]** — Just the folder and anchor page. No repo, no docs folder.
- **[[Topic Anchor]]** — Evergreen knowledge area. No repo, but has standard `{NAME} Docs/` structure. Anchor page is a routing hub to child anchors.
- **[[Code Anchor]]** — Has a code repository, declared by the `code:` key in `.anchor`. Inline mode (`code: .`, repo = anchor folder) or linked mode (`code: <path>`, repo typically at `~/ob/proj/`). Replaces the former Private Repo, Public Repo, and Split Anchor types.
- **[[Paper Anchor]]** — Iterative document revision with version table and section-based editing.
- **[[Skill Anchor]]** — Claude Code skill group in `~/.claude/skills/`. Entry point is `SKILL.md`, not a marker file.

The five above are **identity traits** — single-valued ("at most one of {Simple, Topic, Code, Paper}"; Skill composes). **Capability traits** layer on top of an identity trait (cardinality many):

- **[[Track]]** — the anchor is driven through a planning + backlog lifecycle (the "drive loop"). Co-requires the Backlog facet; composes with Topic / Code / Paper / Skill; excludes Simple. Its tree is the `{NAME} Plan/` folder (rename to `{NAME} Track/` deferred).
- **[[Collection]]** — the anchor *enumerates a collection of members* of an expected (usually one) type — its page carries a Member zone (member list / member groups) below the Masthead. Composes freely with any identity trait (no exclusions, per [[CAB Aspects]] § Governing principle); commonly Topic or Simple. Datedness of members is orthogonal ([[file-association]]). Examples: Bespoke, Log, AT, Disk, prj.

**Git-aspect traits** (mutually exclusive — exactly one per anchor, per [[CAB Aspects]] composability matrix) shape how the agent handles git boundaries (per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] v2 architecture, Q12 resolved 2026-06-01):

- **[[Commit]]** — agent commits at logical boundaries without asking; new-commit-on-top, never amends; never auto-pushes. **Default for Code anchors.** Requires `Code`; excludes `PR` and `NoGit`. Spec: [[SKL Mode Git Commit]].
- **[[PR]]** — every state-touching commit gated through a pull request on its own branch with user review before further work continues. For high-blast-radius repositories. Requires `Code` and a PR-capable host; excludes `Commit` and `NoGit`. Spec: [[SKL Mode Git PR]].
- **[[NoGit]]** — anchor has no per-anchor git repository; the agent performs no git operations on it. **Default for non-Code anchors.** Excludes `Code`, `Skill`, `Commit`, `PR`.

**Cadence traits** (mutually exclusive — exactly one per anchor at a time) shape the agent's recurring trade-off posture:

- **[[Drive]]** — agent-driven, optimistic, minimum-interruption posture. **System default.** Excludes `Lean`. Spec: [[SKL Mode Drive]]; F091 `compact` trigger inlines the load-bearing rules at POST-COMPACT.
- **[[Lean]]** — cautious, distrust-the-foundation, fortify-before-adding posture. Used when work has stopped converging. Per-turn invocation via `/fortify`; declarative per-anchor activation via `Lean` in `traits:`. Excludes `Drive`.

# BRIEF

- **What a trait is.** A named, declarable property of an anchor — listed in the anchor's `.anchor` `traits:` key. Each trait specializes the [[Common Anchor Blueprint]] in a defined way (extra files, extra rules, extra agent behavior). Traits are *what the agent reads to know how to treat this anchor*.
- **Four categories.** *Identity* (single-valued — pick one of Simple/Topic/Code/Paper; Skill composes), *Capability* (many — e.g. Track), *Git-aspect* (exactly one — Commit/PR/NoGit), *Cadence* (exactly one — Drive/Lean). Composability and exclusion rules are authoritative in [[CAB Aspects]].
- **How to add a new trait.** (1) Decide the category and the composability rule (excludes/requires/defaults). (2) Create `[[<Trait>]].md` with the trait's spec — what it adds to an anchor, when it applies, examples. (3) Add a bullet to the appropriate section of this catalog. (4) Update [[CAB Aspects]]'s composability matrix. (5) If the trait carries operational mode behavior, author a `SKL Mode <Trait>.md`. (6) If the trait warrants validation rules, add an `R-trait-<name>` ruleset (see below).
- **Traits vs. facets.** A *trait* is a declarable property of the **anchor** (in `.anchor`'s `traits:`); a *facet* is a per-doc shape applied to a **file** inside the anchor (e.g. Backlog, Rules, Decisions, API Doc). Traits often *require* certain facets — e.g. Track requires the Backlog facet. The trait declares *what the anchor is*; the facet declares *what one file inside it looks like*.
- **Ruleset cross-link.** Trait-wide rules (what every Skill anchor must have, what every Track anchor must carry) live in `R-<trait>` rulesets per the prescriptive rules format ([[FCT Ruleset]]); link from the trait's spec file. The catalog row stays terse — a one-line composability note plus a wiki-link to the spec.
- **Don't pile per-trait content here.** This is a routing catalog. Each trait's full spec lives in its own `[[<Trait>]].md`; SKL mode behavior lives in `SKL Mode <Trait>.md`; rules live in `R-<trait>`. The row is a dashboard summary + pointer.
