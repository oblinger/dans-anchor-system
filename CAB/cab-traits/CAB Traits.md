

All anchor types follow the [[Common Anchor Blueprint]]. Each type adds specializations:

- **[[Simple Anchor]]** — Just the folder and anchor page. No repo, no docs folder.
- **[[Topic Anchor]]** — Evergreen knowledge area. No repo, but has standard `{NAME} Docs/` structure. Anchor page is a routing hub to child anchors.
- **[[Code Anchor]]** — Has a code repository, either inline (repo = anchor) or linked (repo at `~/ob/proj/`, connected by `Code` symlink). Replaces the former Private Repo, Public Repo, and Split Anchor types.
- **[[Paper Anchor]]** — Iterative document revision with version table and section-based editing.
- **[[Skill Anchor]]** — Claude Code skill group in `~/.claude/skills/`. Entry point is `SKILL.md`, not a marker file.

