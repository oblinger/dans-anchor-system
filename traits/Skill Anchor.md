# Skill Anchor

A Skill Anchor is *a conventional CAB anchor whose code is its `SKILL.md` and whose user-facing content lives at well-defined locations outside the anchor's filesystem folder.* What distinguishes a Skill Anchor from a Code Anchor:

- **`SKILL.md` is the code** — agent-loaded entry point at `~/.claude/skills/<folder>/SKILL.md`, kebab-case folder name (Claude Code requirement). No `{NAME} Dev/` directory; no source-repo.
- **User docs live in SKL** — `~/.claude/skills/SKL User Docs/SKL Skills/SKL <Slug>.md` (NOT under the anchor's `{NAME} User/` folder).
- **Multiple runtime surfaces** — the SKILL.md + scripts + tests + rules/decision sets all live under `~/.claude/skills/<folder>/`, while the anchor's docs (`{NAME} Track/`, `{NAME} Features/`, etc.) live at the SKA filesystem location. Both surfaces are formally part of the anchor; their split is captured by the `skill-*` facets (per [[F116 — Skills as conventional anchors — retire skill-trait, convert to CAB facets with skill- prefix]]).
- **Composes with `skill-*` facets (v1, per F116 Q2 = B)** — `skill-testing` (tests/), `skill-search-rules` (rules/), `skill-script` (scripts/), `skill-config` (per F080's `~/.config/ob-skills/<name>/`). Each facet applies when its location has content; an anchor doesn't need all of them. `skill-doc` and `skill-spec` are reserved facet names that will ship in a later iteration.

Otherwise this anchor follows [[CAB Base]] with the standard CAB shape (anchor page, Track/Features/Backlog if there's content).

**Working example:** [[CSE]] (Common Skill Example) — a fully-wired Skill Anchor demonstrating the layout. Use CSE when you need to see the actual files; use the spec below for the rules.


## When to Use

Claude Code skills with their own design history — PRD, feature docs, backlog. The skill's anchor accrues design narrative as it evolves.

For trivial skills with no design history (one-shot recipes that won't see iteration), the slim form is acceptable: `SKILL.md` + action files at the runtime location, no `{NAME} Track/` tree. Promote to the full form on the first feature design.


## Structure

```text
# Runtime location (where SKILL.md and skill-* facet content lives)
~/.claude/skills/<folder>/                   ← kebab-case folder name (Claude Code requirement)
├── SKILL.md                                 the agent-loaded entry point — the "code"
├── <folder>-<action>.md                     action files (kebab-case)
├── scripts/                                 optional — skill-script facet
├── tests/                                   optional — skill-testing facet
├── rules/                                   optional — skill-search-rules facet (for search-family skills)
└── sets/                                    optional — canonical decision-set library (per F113 Phase 3)

# Anchor filesystem location (where {NAME} Track/ etc. live)
SYS/Bespoke/Skill Agent/<Category>/<Slug>/   ← anchor root
├── .anchor                                  anchor config — declares `traits: [Skill Anchor]`
├── <Slug>.md                                anchor page with dispatch table
└── <Slug> Track/                            optional — create when there's content
    ├── <Slug> Backlog.md
    ├── <Slug> Features/
    │   ├── <Slug> Features.md
    │   └── F<NNN> — Title.md
    └── ...
```

The two locations are formally part of the same anchor. The `skill-*` facets document the relative-to-runtime paths.


## Naming Conventions — folder vs slug

| Context | Convention | Example |
|---|---|---|
| **Skill runtime folder** | kebab-case, lowercase (Claude Code requirement) | `groom/`, `backlog-horizons/` |
| **Action files** | kebab-case, prefixed by folder name | `groom-runbook.md`, `backlog-horizons-promote.md` |
| **Slug** | Title Case, space-separated (matches SKL doc name) | `SKA groom`, `SKA backlog-horizons` |
| **Anchor docs** | Slug-prefixed, Title Case | `SKA groom Backlog.md` |
| **Anchor root page** | `{Slug}.md` at anchor folder root | `SKA groom/SKA groom.md` |
| **User-facing doc** | `SKL {Slug}.md` in SKL tree | `SKL User Docs/SKL Skills/SKL groom.md` |

**Why two cases:** Claude Code resolves skills from kebab-case folder names; CAB anchor docs use Title Case slug-prefixes for human readability and Obsidian wiki-link clarity. The two layers coexist because file extensions and case-insensitive resolution always disambiguate.


## Anchor Page Dispatch Table

The anchor root page (`{Slug}.md`) follows [[CAB Anchor Page]] with one Skill-Anchor-specific row shape: the **first row** is `Skill` and carries two surfaces — the skill spec (`[[<folder>/SKILL|SKILL.md]]`) and the user-facing doc (`[[SKL <Slug>|User Docs]]`); the second row is the optional `Track` row carrying `[[<Slug> Backlog|Backlog]]` and `[[<Slug> Features|Features]]`. As a rendered two-row example:

| Row | Surfaces |
| --- | --- |
| Skill | `[[<folder>/SKILL\|SKILL.md]]`, `[[SKL <Slug>\|User Docs]]` |
| `[[<Slug> Track\|Track]]`+ | `[[<Slug> Backlog\|Backlog]]`, `[[<Slug> Features\|Features]]` |

The `Skill` row replaces the `Dev` and `User` rows that a Code Anchor would have. It carries the two things a reader of the anchor most needs to find: the skill spec (agent-loaded) and the user-facing doc.


## Feature Docs

Skill-specific feature designs live in `{Slug} Track/{Slug} Features/`. F-numbers are anchor-wide per the [[SKA feature]] skill — `F042` is unique within this anchor regardless of folder location.

Cross-skill features (touching 2+ skills) and meta-anchor features (about SKA itself) live in the SKA-level Features folder. Skill-specific features belong with the skill.


## Optional vs Required

| File / folder | When required |
|------|---------------|
| `~/.claude/skills/<folder>/SKILL.md` | always |
| `.anchor` (declaring `traits: [Skill Anchor]`) | always |
| `{Slug}.md` (anchor root) | always (per F036 — every skill folder gets a CAB anchor structure) |
| `{Slug} Track/{Slug} Backlog.md` | optional — create only when there's content |
| `{Slug} Track/{Slug} Features/` | optional — create when first feature doc is filed |
| `{Slug} Track/{Slug} PRD.md` | optional |
| `tests/`, `scripts/`, `rules/`, `sets/` (runtime location) | per the corresponding `skill-*` facet — optional, create when there's content |

Per F116, the eager-scaffold approach is dropped: anchors don't pre-create Backlog/Triage/PRD files. Create only when the skill has actual content for those facets. Simple skills stay slim.


## Anchor Identity — slug collision warning

Some skills share names with parent-level project anchors (e.g., `cab/` skill at `~/.claude/skills/cab/` vs `CAB/` project anchor at `Bespoke/Skill Agent/CAB/`). When that's the case:

- The **project anchor** (uppercase folder, sibling to SKA) carries the slug and gets `[[CAB]]` wiki-links.
- The **skill runtime folder** does NOT create a `{Slug}.md` anchor root page — it would collide with the project's slug on macOS case-insensitive filesystems.
- The skill folder still has `SKILL.md` and action files; the anchor docs (Track/Features/etc.) live in the project anchor instead, not duplicated under the skill.

This is the case for `cab/`, `io/`, `dev/` (where applicable). For all other skills (no parent-level project), the full Skill Anchor structure applies.


## Audit

### Required files

- `SKILL.md` with valid YAML frontmatter (name, description, user_invocable)
- Action files referenced from the SKILL.md dispatch table
- `.anchor` declares `traits: [Skill Anchor]`
- Anchor root page (`{Slug}.md`) with the `Skill` dispatch row

### Common findings

- `traits:` missing the `Skill Anchor` declaration
- Anchor root page missing the `Skill` first-row dispatch with both `SKILL.md` and `SKL <Slug>` links
- User docs in `{Slug} User/` (or pre-F113 `{Slug} Docs/{Slug} User/`) instead of the canonical `SKL User Docs/SKL Skills/SKL <Slug>.md`
- Feature docs in the SKA-level Features folder when they're skill-specific (should be migrated)
- Eagerly-scaffolded empty Backlog/Triage/PRD files (deprecated by F116 — create on demand only)


## Migration note (F116)

Rewritten in place by F116. The principal change: the parallel `SKA skill-trait/` registry is gone; its content is now part of CAB as the `skill-*` facets (composing with this Skill Anchor trait). Substantive structural conventions (folder layout, naming, dispatch table) are preserved. Q1 = A means the filename stays `Skill Anchor.md` — no wiki-link sweep needed for trait references; references to the `[[SKA skill-trait]]` registry get rewritten to the new `[[CAB skill-<name>]]` facet links.

# BRIEF

- **This file is the Skill Anchor trait spec** — the authoritative definition of what makes an anchor a Skill Anchor (two-location split, `SKILL.md` as code, SKL doc location, composing `skill-*` facets). Edits here change the contract that every Skill Anchor must satisfy.
- **NOT for per-skill content** — do not pile individual skill examples, runbooks, or design narratives here; those belong in each skill's own anchor (`{Slug} Track/`) or in [[CSE]] (the worked example).
- **Inclusion test for edits** — a rule belongs here only if it applies to *every* Skill Anchor. Rules that apply to one sub-shape go in the matching `skill-*` facet (`CAB skill-testing`, `CAB skill-script`, `CAB skill-search-rules`, `CAB skill-config`, etc.); rules that apply to all anchors go in [[CAB Base]].
- **Two-location split is load-bearing** — the runtime location (`~/.claude/skills/<folder>/`, kebab-case) and the anchor filesystem location (`SYS/Bespoke/Skill Agent/<Category>/<Slug>/`, Title Case slug) are both formally part of the anchor. Don't collapse them or imply one is canonical; both must be documented in any structural change.
- **Naming convention table is contract** — folder/action/slug/anchor-docs casing rules are referenced by audit and by the create/install skills; preserve column meaning when editing. Case-insensitive filesystems on macOS make slug-collision warnings (`cab/`, `io/`, `dev/`) load-bearing — don't drop that section.
- **Composes with `skill-*` facets, does not absorb them** — when a per-facet rule grows here, factor it out to the matching `CAB skill-<name>` facet spec rather than letting this file accumulate facet-specific detail.
- **Cross-references to keep aligned on edits** — [[CSE]] (worked example), [[CAB Base]] (parent shape), [[CAB Anchor Page]] (dispatch table rules), F116 (the rewrite that produced this spec), and the `skill-*` facet specs. Renaming or restructuring this file requires sweeping wiki-links across all of them.
