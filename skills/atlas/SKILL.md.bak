---
name: atlas
description: Maintain the user's vault-wide glossary/router (`[[Atlas]]` at `~/ob/kmr/MY/Atlas/Atlas.md`). Add or refine entries for named things in the vault, keep `[[ATL Slugs]]` in sync, enforce the routing-not-duplication and no-guessable-info disciplines. Use when a new named thing (anchor, concept, standard, tool) needs to be discoverable from the master glossary, or when an existing entry needs refinement. Slash-only — the spoken word "atlas" is too common to be a DMUX prefix-trigger.
user_invocable: true
---

# /atlas

Maintain the vault-wide glossary and router at `~/ob/kmr/MY/Atlas/Atlas.md`. Atlas is the agent's primary discovery surface for named things in the user's knowledge repo — anchors, concepts, standards, tools, project codenames. Every entry **routes to the canonical source** rather than duplicating its content.

User docs: `[[Atlas]]` (the file itself is the documentation).

## What this skill maintains

| Surface | Path | Purpose |
|---|---|---|
| **Atlas** | `~/ob/kmr/MY/Atlas/Atlas.md` | Alphabetical glossary of named things. Each entry = `## Name` H2 + paragraph + `([[slug]])` terminator. |
| **ATL Slugs** | `~/ob/kmr/MY/Atlas/ATL Slugs.md` | Master index — one row per named thing with three columns: `Slug` (hook URL), `Atlas` (block-link to the H2), `Summary` (one-phrase distillation). |

Both surfaces stay in sync. Adding an Atlas entry adds a Slugs row; refining a body refines the Summary.

## Actions

| Form | What it does |
|---|---|
| `/atlas add <name>` | Add a new entry for `<name>`. Inserts in alphabetical position; writes the Slugs row; glances the result. |
| `/atlas update <name>` | Refine an existing entry. Re-syncs the Slugs Summary cell. |
| `/atlas` (bare) | Glance Atlas.md + ATL Slugs.md so the user can browse or edit by hand. |

## Discipline (load-bearing)

The whole point of Atlas is to be a single, trustworthy router. The disciplines below are non-negotiable — they're what make Atlas useful instead of just another set of notes.

### 1. Routing, not duplication

An Atlas entry **points to** the canonical source; it never holds the canonical content. If a user reads an Atlas entry and gets a complete answer without following any link, the entry is wrong — the content should be at the link target, and the entry should be a one-paragraph summary plus a pointer.

Anti-pattern: a long Atlas entry with code samples / tables / lists. Right pattern: a paragraph naming what the thing is + where to read more.

### 2. No guessable info

The agent reading Atlas already knows: standard CLAUDE.md conventions, that `.anchor` files mark anchors, common shell commands, what an anchor folder layout looks like, anything trivially `ls`-able. **Do not include any of that in an entry.**

Atlas entries earn their bytes only by carrying *non-obvious* facts: the user's specific convention, a where-it-lives that isn't derivable from the slug, a related-names cluster the agent wouldn't guess.

Sanity check before writing an entry: *"Could a fresh agent with general CLAUDE.md context derive this?"* If yes, cut it.

### 3. Alphabetical order, never categorical

Entries are sorted by name. **Never group by category** (no "Anchors" section followed by "Tools" section). The Organizing principles block at the top of Atlas.md is the only categorical writing; everything below is flat alphabetical.

When the file grows unwieldy, split alphabetically (`Atlas A-F.md`, `Atlas G-M.md`, …) — never by category. (Not yet — the file is well under that threshold.)

### 4. Entry shape

```markdown
## Name

One paragraph: what it is, where it lives, intended use, constraints, related-name links. End with the slug in parentheses if the name has one.  ([[slug]])
```

- One H2 per name. The H2 text matches the slug exactly (case + spaces preserved).
- One paragraph (rarely two for genuinely structural entries; never more than two).
- Wiki-link related names liberally so the entry is a discoverability node.
- Close with `([[slug]])` so the reader can jump straight to the resolved page. Omit the parens if the name has no slug (e.g. concepts).
- If the entry has hard rules the agent must obey (rare), append a `Rules:` block after the paragraph (see the existing `## Atlas` entry as the reference).

### 5. ATL Slugs row stays in sync

Every Atlas entry has a corresponding row in `ATL Slugs.md`:

```
| [Name](hook://p/Name%20URL%20Encoded) | [[Atlas#Name\|Name]] | One-phrase summary derived from the entry. |
```

- **Slug column** — markdown link `[Name](hook://p/Name)` with URL-encoded spaces (`%20`). Blank for entries without a resolvable slug.
- **Atlas column** — wiki-link to the Atlas H2 using the block-style fragment: `[[Atlas#Name\|Name]]`. Always present (the row exists *because* of the Atlas entry).
- **Summary column** — one phrase distilled from the entry body. Updates when the body is refined.

Rows are sorted alphabetically by **name** (the Atlas column's display text), matching the Atlas file's order.

## Runbook — `/atlas add <name>`

1. **Read** `~/ob/kmr/MY/Atlas/Atlas.md` to locate the alphabetical insertion point (the H2 immediately following where `## <name>` would sit).
2. **Compose** the entry per § 4 above. Lean ruthlessly on § 2 (no-guessable-info) — the first draft is almost always too long.
3. **Insert** the entry at the right alphabetical position. Preserve the blank line before/after to keep H2s separated.
4. **Read** `~/ob/kmr/MY/Atlas/ATL Slugs.md` and **insert** the matching row at the same alphabetical position.
5. **Glance** Atlas.md so the user can verify:
   ```bash
   open "$HOME/ob/kmr/MY/Atlas/Atlas.md"
   ```
6. Report the entry added + summary line, in one short line.

## Runbook — `/atlas update <name>`

1. **Read** Atlas.md, locate the existing `## <name>` H2.
2. **Edit** the body in place. Apply discipline § 1 + § 2 — almost always means cutting, rarely means adding.
3. **Read** ATL Slugs.md, find the row, **re-derive** the Summary cell from the refined body, and update it.
4. **Glance** Atlas.md.
5. Report what changed in one short line.

## Runbook — bare `/atlas`

1. **Glance** Atlas.md + ATL Slugs.md so the user can browse:
   ```bash
   open "$HOME/ob/kmr/MY/Atlas/Atlas.md"
   open "$HOME/ob/kmr/MY/Atlas/ATL Slugs.md"
   ```
2. Stop. Bare invocation is read-mode; no edits.

## When NOT to use this skill

- **Editing per-anchor docs** — those live in the anchor's own folder. Atlas only points; it doesn't carry anchor-specific content.
- **Bulk migration / structural reshape of Atlas itself** — file an `[[ATL Backlog]]` row instead. Atlas restructure is project work tracked in `~/ob/kmr/MY/Atlas/ATL Plan/`.
- **Creating "SYS Atlas" / "Project Atlas" parallels** — Atlas is the *single, vault-wide* router. Per-anchor routing belongs in the anchor's own dispatch table, not a parallel Atlas file. (This failure mode happened once already — `SYS/Atlas.md` was created and deleted 2026-06-01.)

## Anti-patterns

- Writing an entry that fully answers a user question — that content belongs at the link target, not in the Atlas.
- Adding bullet lists, sub-headers, or tables inside an entry body — entries are paragraphs.
- Grouping entries by category — Atlas is strictly alphabetical.
- Letting Atlas.md and ATL Slugs.md drift — every add/update touches both.
- Including info the agent already knows from CLAUDE.md or general anchor conventions.
- Creating a second, scoped Atlas (e.g. `SYS/Atlas.md`, `prj/Atlas.md`) — anchors carry their own dispatch tables; the vault has one Atlas.

## Related

- Atlas itself: `[[Atlas]]` (the file)
- Master index: `[[ATL Slugs]]`
- Anchor page: `[[ATL]]`
- Project planning: `[[ATL Plan]]` / `[[ATL Backlog]]`
