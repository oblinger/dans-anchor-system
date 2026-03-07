# CAB Naming Conventions

## TLC (Three Letter Codes)
- Commonly accessed anchors have a short acronym for quick access
- Ideally three letters, hence "TLC" — but can be 2-5 letters if needed
- **TLCs should always be ALL CAPS** (e.g., SYS, ABIO, PC)
- If an anchor has a TLC, create `{TLC}.md` in the `{TLC} Docs/` folder
- The root folder has `{FULL_NAME}.md` containing only: `See [[TLC]]`
- The TLC file in Docs becomes the primary anchor markdown with all the content

## TLC Index
- The TLC index contains a table of all TLCs
- Periodically scan `~/ob/kmr` and `~/ob/proj` to find anchor folders with TLCs
- Table fields:
  - **DATE** — Creation date of TLC.md file (table sorted reverse chronologically)
  - **TLC** — Wiki link to the acronym file
  - **FULL ANCHOR NAME** — Folder name containing the TLC
  - **DESC** — Description (stored in anchor markdown with prefix `desc::`)

## Finding Anchors
Use the `ha` (HookAnchor) command to find anchor paths by TLC or name:
```bash
ha -p ASP              # Returns path to the ASP anchor folder
ha -p "Alien Biology"  # Find by full name
```

## Auxiliary Commands
Some anchor types register additional commands beyond the primary anchor command:

| Command Pattern | Anchor Type | Action |
|-----------------|-------------|--------|
| `{TLC} Code` | [[Split Anchor]] | Opens the repository folder in Finder |

Auxiliary commands use the same prefix (TLC or full name) followed by a capitalized keyword.

## {NAME} Prefix Rule

**Every markdown file and every folder inside an anchor must be prefixed with `{NAME}`** (the TLC if one exists, otherwise the full anchor name). This is not optional — it prevents collisions in the shared Obsidian namespace where all files across all anchors are visible.

- **Files:** `{NAME} PRD.md`, `{NAME} Roadmap.md`, `{NAME} Simulator.md`
- **Folders:** `{NAME} Docs/`, `{NAME} Dev/`, `{NAME} bio/`
- **Nested files:** Still prefixed — `{NAME} bio/{NAME} Chemistry.md`

The only exceptions are files that are inherently unique and not part of the Obsidian namespace:
- `CLAUDE.md` — Claude Code config (one per project root)
- `README.md`, `API_REFERENCE.md`, `CONFIG_REFERENCE.md` — repo conventions
- Code files (`.py`, `.ts`, etc.) — not markdown, not in Obsidian's link graph

**Why folders too?** Each folder may contain an index markdown file describing that group (e.g., `{NAME} bio/{NAME} bio.md`). If the folder isn't prefixed, neither is the index file, and collisions follow.
