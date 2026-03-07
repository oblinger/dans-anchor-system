# Private Repo Anchor

Follows [[CAB Base]] with these deltas:

## When to Use

Private projects where all planning and design documents can be committed alongside code. No need to separate private docs from public code.

## Deltas from Base

- **Repo = anchor** — the repository root IS the anchor folder
- **Kebab-case folder name** — repo/folder uses `{kebab-name}`, anchor page uses `{NAME}`
- **No `Code` symlink** — code is right here
- **CLAUDE.md and README.md** — present at anchor root
- **`docs/` sync target** — `{NAME} User/` and `{NAME} Dev/` can be sync-pushed to `docs/` at repo root

## Structure Additions

```
{kebab-name}/                            repository = anchor folder
├── ...                                  (base structure)
├── .git/
├── README.md
├── CLAUDE.md
├── docs/                                sync-pushed from Docs/
│   ├── user/                            ← from {NAME} User/
│   └── dev/                             ← from {NAME} Dev/
└── src/
```

## Naming Conventions

- **kebab-case** = repository / anchor folder name
- **snake_case** = Python package name (if applicable)
- **{NAME}** = TLC or anchor identifier used for all doc files

Example: `double-click` (repo) → `ODC` (TLC) → `ODC Docs/`, `ODC.md`

## Setup Checklist (additions to base)

1. Initialize git in the anchor folder
2. Create README.md and CLAUDE.md
3. Register sync-push targets if User/ or Dev/ docs exist
