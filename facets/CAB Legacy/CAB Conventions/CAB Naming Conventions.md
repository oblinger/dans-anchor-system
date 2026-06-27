# CAB Naming Conventions

The CAB naming conventions spec — slugs, the `{NAME}` prefix rule for repeated-structure files, and exceptions — that govern how anchor files and folders are named across the vault.

## slug (slugs)
- Commonly accessed anchors have a short acronym for quick access
- Ideally short (2-5 letters), hence "slug" — e.g., SYS, ABIO, PC
- **slugs should always be ALL CAPS** (e.g., SYS, ABIO, PC)
- If an anchor has a slug, create `{slug}.md` in the `{slug} Docs/` folder
- The root folder has `{FULL_NAME}.md` containing only: `See [[slug]]`
- The slug file in Docs becomes the primary anchor markdown with all the content

## slug Index
- The slug index contains a table of all slugs
- Periodically scan `~/ob/kmr` and `~/ob/proj` to find anchor folders with slugs
- Table fields:
  - **DATE** — Creation date of slug.md file (table sorted reverse chronologically)
  - **slug** — Wiki link to the acronym file
  - **FULL ANCHOR NAME** — Folder name containing the slug
  - **DESC** — Description (stored in YAML frontmatter as `description:`)

## Finding Anchors
Use the `ha` (HookAnchor) command to find anchor paths by slug or name:
```bash
ha -p ASP              # Returns path to the ASP anchor folder
ha -p "Alien Biology"  # Find by full name
```

## Auxiliary Commands
Some anchor types register additional commands beyond the primary anchor command:

| Command Pattern | Anchor Type | Action |
|-----------------|-------------|--------|
| `{slug} Code` | [[Code Anchor]] | Opens the repository folder in Finder |

Auxiliary commands use the same prefix (slug or full name) followed by a capitalized keyword.

## {NAME} Prefix Rule

The `{NAME}` prefix exists to prevent **basename collisions** in the shared Obsidian namespace, where every markdown file across every anchor is visible by basename. The rule is targeted, not universal.

### Required: prefix on **repeated-structure** files and folders

Every file or folder that participates in CAB's **repeated structure** — i.e., it shows up under the same name in *every* anchor — must carry the `{NAME}` prefix. Without the prefix, every anchor's `Backlog.md` collides with every other anchor's `Backlog.md`.

This applies to:

- **Standard CAB facets** — `{NAME} PRD.md`, `{NAME} Backlog.md`, `{NAME} Roadmap.md`, `{NAME} Triage.md`, `{NAME} Questions.md`, `{NAME} Inbox.md`, `{NAME} Icebox.md`, `{NAME} Files.md`, `{NAME} Architecture.md`, `{NAME} Discussion.md`, `{NAME} Principles.md`, `{NAME} Rules.md`, `{NAME} Outputs.md`, `{NAME} WP.md`, `{NAME} CLI.md`, `{NAME} Cards.md`, `{NAME} Module Doc.md`, `{NAME} UX Design.md`, `{NAME} System Design.md`, `{NAME} Folder.md`, `{NAME} Anchor Page.md`, `{NAME} Skill.md`, `{NAME} All Files.md`, `{NAME} Documentation Site.md`, `{NAME} Project Page.md`, `{NAME} Code Repository.md`.
- **Standard structural folders** — `{NAME} Docs/`, `{NAME} Plan/`, `{NAME} Dev/`, `{NAME} User/`, `{NAME} Features/`, `{NAME} bio/`, etc. Folder gets prefixed because its index file (`{NAME} bio/{NAME} bio.md`) needs to be unique too.
- **Nested standard files** — `{NAME} bio/{NAME} Chemistry.md` if Chemistry is itself part of a repeated structure inside bio.

The full enumeration of repeated-structure facets lives in [[CAB All Files]] and the dispatch in [[Facets]].

### Optional: semantically-unique files MAY use the prefix

Files with a **vault-globally-unique** name — not a repeated structure across anchors — don't strictly require the prefix. These are content files with one-off names that won't collide even unprefixed. Examples:

- A one-off feature spec like `2026-04-15 Pause Migration.md` inside `{NAME} Features/`.
- A unique content document inside `{NAME} bio/` like `Mitochondrial Pathway Notes.md`.
- A research note or work product that has its own descriptive title.

These files MAY use the `{NAME}` prefix for stylistic consistency, but they don't have to. Authors choose based on whether the unprefixed name is descriptive enough on its own.

### Hard exceptions: inherently unique, never prefixed

Files outside the Obsidian namespace or governed by external conventions are never prefixed:
- `CLAUDE.md` — Claude Code config, one per project root, hard-coded discovery path.
- `README.md`, `API_REFERENCE.md`, `CONFIG_REFERENCE.md` — repo / GitHub conventions.
- `SKILL.md` — Claude Code skill spec, hard-coded discovery path.
- `.anchor` — anchor marker file, named by HookAnchor.
- Code files (`.py`, `.ts`, `.rs`, etc.) — not markdown, not in Obsidian's link graph.

### Skill-anchor exception (within SKA)

Per-skill anchor folders inside the SKA hierarchy (e.g., `Drive Skills/mint/`, `Anchor Skills/audit/`) use **lowercase bare-verb names** matching the runtime skill name at `~/.claude/skills/<verb>/`. The skill's anchor page inside is `<verb>.md` (lowercase, matching the folder). This is a deliberate exception to the prefix rule because skill names are assumed globally unique — they're verbs that have to be unique anyway to avoid runtime ambiguity. Repeated-structure children of a skill anchor (e.g., `audit/Audit Docs/`, `audit/Audit Plan/`) still follow the prefix rule using the skill name as `{NAME}`.

### Why this matters

Obsidian basename resolution: `[[Backlog]]` looks up by basename. If two files share a basename, the wiki-link becomes ambiguous and HookAnchor disambiguates with path-form `[[anchor1/Backlog]]`, which is exactly the slash-form noise that the prefix is designed to prevent. The prefix narrows where the rule is needed — to repeated-structure files — and keeps the rule from being theatrical on already-unique content.

# BRIEF

- **This is the authoritative naming-conventions spec for CAB.** Slugs (ALL CAPS short acronyms), the `{NAME}` prefix rule, and their exceptions are defined here; other CAB facets/rules/skills cite this file rather than restate the conventions.
- **NOT for** anchor-type taxonomy, facet-shape rules, folder-structure rules, or per-anchor naming choices. Type taxonomy lives in CAB types; facet shapes in their `CAB <Facet>.md` specs; per-anchor names are author choices not governed here.
- **Inclusion test:** a rule belongs here only if it answers "what is this file/folder *called*?" at the basename level — slug form, prefix form, capitalization, namespace-collision avoidance. Structural rules ("every anchor has a Docs folder") belong elsewhere.
- **Keep the repeated-structure enumeration in sync** — the `{NAME} <Facet>.md` list under §Required must stay aligned with [[CAB All Files]] and the [[Facets]] dispatch; when a new repeated facet is added there, add it here too (and vice-versa).
- **Hard-exception list is load-bearing** — `CLAUDE.md`, `README.md`, `SKILL.md`, `.anchor`, code files: each is exempt because of an external discovery contract. Don't add an exception without naming the external contract that forces it.
- **Skill-anchor lowercase-bare-verb exception is also load-bearing** — it ties to runtime skill discovery at `~/.claude/skills/<verb>/`. Don't generalize this exception to other anchor types; it's specific to SKA-per-skill anchors.
- **Don't pile examples here.** This file is the rule; worked examples belong in the cited specs (CAB All Files, Facets, individual facet specs). One illustrative example per rule is plenty.
