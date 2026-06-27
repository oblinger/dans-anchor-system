# CAB Integrations

Optional tools and services that anchors may integrate with.

## Git
- Anchor may have its own git repository at the repo subdirectory
- Default remote: private repo on GitHub
- Repository name matches subdirectory name

## GitHub Pages
- Published documentation hosted via GitHub Pages
- URL pattern: `username.github.io/repo-name/`
- Built from `docs/` folder or `gh-pages` branch

## Claude (CLAUDE.md)
- See [[CAB Claude]] for full specification
- `CLAUDE.md` at anchor root configures Claude Code behavior

## tmux
- Project may have associated tmux session for development
- Session name typically matches slug

# BRIEF

- **This file catalogs optional external integrations** an anchor MAY adopt (git, GitHub Pages, Claude/CLAUDE.md, tmux) — purely opt-in surface conventions, not anchor-shape rules.
- **NOT for required anchor structure** — folder layout, dispatch tables, facet conventions belong in [[CAB Anchor]], [[CAB All Files]], or the relevant `CAB <Facet>.md`. Don't pile structural rules here.
- **Inclusion test:** an integration belongs here only if (a) it's an **external tool/service** an anchor connects to, (b) adoption is **optional**, and (c) the convention is **cross-anchor** (any anchor MAY adopt it). One-anchor-specific tooling belongs in that anchor's docs, not here.
- **Each integration is a short H2 section** with a bulleted named list of conventions (URL patterns, naming rules, default locations). Keep entries terse — link out to the canonical spec (e.g. `[[CAB Claude]]` for CLAUDE.md) rather than inlining details.
- **Load-bearing:** integration H2 names are referenced from other CAB docs and anchor specs; renaming an H2 (e.g. `## GitHub Pages` → `## Pages`) silently breaks wiki-link anchors. Add new H2s freely; rename only with a cross-reference sweep.
