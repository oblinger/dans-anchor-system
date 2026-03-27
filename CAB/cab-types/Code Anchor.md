# Code Anchor

Follows [[CAB Base]] with these deltas:

## When to Use

Any project with a code repository — whether the repo is public or private, whether it lives inside the vault or outside.

## Deltas from Base

- **Code repository** — every Code Anchor has an associated git repo
- **CLAUDE.md** — present at anchor root only. Never duplicated in the repo — a single source of truth prevents drift.
- **README.md** — present in repo root
- **Docs sync** — `{NAME} User/` and `{NAME} Dev/` can be sync-pushed to the repo's `docs/`

## Repo Mode

A Code Anchor operates in one of two modes:

### Inline Mode
The repo IS the anchor folder. Code and docs live together. Use when all materials can be version-controlled together (private projects, or projects where docs are public).

```
{kebab-name}/                        repo = anchor folder
├── .git/
├── README.md
├── CLAUDE.md
├── {NAME}.md                        anchor page
├── {NAME} Docs/                     planning docs (standard base structure)
├── justfile                         build recipes
├── src/                             source code
└── docs/                            sync-pushed from Docs/ (optional)
```

### Linked Mode
Docs live in the vault; code lives at `~/ob/proj/`. A `Code` symlink connects them. Use when docs should stay private while code is public, or when the repo should not contain vault files.

```
{CAB Folder}/                        in vault (~/ob/kmr/)
├── {CAB Folder}.md                  marker file
├── {NAME}.md                        anchor page
├── {NAME} Docs/                     planning docs (standard base structure)
├── CLAUDE.md
└── Code -> ~/ob/proj/{path}/{repo}  symlink to repository

~/ob/proj/{path}/{repo}/             outside vault
├── .git/
├── README.md
├── justfile
├── src/
└── docs/                            sync-pushed from Docs/ (optional)
```

### Choosing a Mode

- **Inline** when: private repo, or you don't mind docs in the repo
- **Linked** when: public repo with private planning docs, or repo is large/complex and shouldn't live in the vault

## Naming Conventions

- **kebab-case** = repository / folder name
- **{NAME}** = RID or anchor identifier used for all doc files
- Example: `dict-a-mux` (repo) -> `DMUX` (RID) -> `DMUX Docs/`, `DMUX.md`

## Setup Checklist (additions to base)

1. Choose repo mode (inline or linked)
2. If linked: create `Code` symlink → repo path
3. Create README.md in repo; CLAUDE.md stays in the anchor root only
4. If justfile exists: add standard recipes (`forge`, `test`, `publish`)
5. Register sync-push targets if User/ or Dev/ docs exist

## Audit

Type-specific structure checks for Code Anchors. These are run by `/audit structure` after the common checks.

### Required files

- `Code` symlink or inline `.git/` — the code repository must be reachable
- `{NAME} Docs/{NAME} Dev/` folder with dispatch page (`{NAME} Dev.md`)
- `{NAME} Docs/{NAME} User/` folder with dispatch page (`{NAME} User.md`)
- `{NAME} Docs/{NAME} Dev/{NAME} Files.md` — codebase file tree
- `README.md` in the repo root

### Required dispatch rows

- **Dev** row in anchor page dispatch table, linking to Dev dispatch
- **User** row if User folder exists

### Code-specific checks

- `Code` symlink resolves to an existing directory (linked mode) or `.git/` exists (inline mode)
- Dev dispatch page links to all module docs in the Dev folder
- Files.md exists and lists source files
- If `justfile` exists in repo, verify it has standard recipes (at minimum: `test`)
- CLAUDE.md exists at anchor root only — not duplicated in the repo
