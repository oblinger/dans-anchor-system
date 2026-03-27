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
- Session name typically matches RID
