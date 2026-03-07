# Public Repo Anchor

Follows [[CAB Base]] with these deltas:

## When to Use

Public/open-source projects where planning docs must remain private while the code is public.

## Deltas from Base

- **Wrapper folder** — Title Case folder is the anchor; repo is a subfolder or symlink
- **Private docs outside repo** — `{NAME} Docs/` lives in the wrapper, not in the repo
- **Code symlink** — `Code ->` points to the repo (which lives in `~/ob/proj/`)
- **CLAUDE.md** — present at both wrapper and repo level
- **`docs/` sync target** — `{NAME} User/` and `{NAME} Dev/` can be sync-pushed to the repo's `docs/`

## Structure Additions

```
{FULL_NAME}/                             wrapper folder = anchor
├── ...                                  (base structure)
├── CLAUDE.md
├── Code -> ~/ob/proj/{project}/{repo}   symlink to repository
│
│   (repo lives outside vault at ~/ob/proj/)
└── {kebab-name}/                        public repository
    ├── .git/
    ├── README.md
    ├── CLAUDE.md
    ├── docs/                            sync-pushed from Docs/
    │   ├── user/                        ← from {NAME} User/
    │   └── dev/                         ← from {NAME} Dev/
    └── src/
```

## Naming Conventions

- **Title Case with spaces** = wrapper folder (anchor)
- **kebab-case** = Git repository subfolder
- **{NAME}** = TLC or anchor identifier used for all doc files

## Setup Checklist (additions to base)

1. Create `{kebab-name}/` repo, initialize git
2. Create README.md and CLAUDE.md in repo
3. Create `Code` symlink → repo path
4. Register sync-push targets if User/ or Dev/ docs exist
