# CAB Naming Conventions

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

**Every markdown file and every folder inside an anchor must be prefixed with `{NAME}`** (the slug if one exists, otherwise the full anchor name). This is not optional — it prevents collisions in the shared Obsidian namespace where all files across all anchors are visible.

- **Files:** `{NAME} PRD.md`, `{NAME} Roadmap.md`, `{NAME} Simulator.md`
- **Folders:** `{NAME} Docs/`, `{NAME} Dev/`, `{NAME} bio/`
- **Nested files:** Still prefixed — `{NAME} bio/{NAME} Chemistry.md`

The only exceptions are files that are inherently unique and not part of the Obsidian namespace:
- `CLAUDE.md` — Claude Code config (one per project root)
- `README.md`, `API_REFERENCE.md`, `CONFIG_REFERENCE.md` — repo conventions
- Code files (`.py`, `.ts`, etc.) — not markdown, not in Obsidian's link graph

**Why folders too?** Each folder may contain an index markdown file describing that group (e.g., `{NAME} bio/{NAME} bio.md`). If the folder isn't prefixed, neither is the index file, and collisions follow.
