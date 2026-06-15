# Code Anchor

The Code trait spec — defines how an anchor that owns a git repository differs from [[CAB Base]], including the inline-vs-linked repo modes, required `code:` key in `.anchor`, and code-specific structure and audit checks.

Follows [[CAB Base]] with these deltas:

## When to Use

Any project with a code repository — whether the repo is public or
private, whether it lives inside the vault or outside.

## Deltas from Base

- **Code repository** — every Code Anchor has an associated git repo
- **`.anchor` has `code:` key** — declares the repo's location. Required
  for the `code` trait; scripts error if missing.
- **CLAUDE.md** — present at anchor root only. Never duplicated in the
  repo — a single source of truth prevents drift.
- **README.md** — present in repo root
- **Docs sync** — `{NAME} User/` and `{NAME} Dev/` can be sync-pushed to
  the repo's `docs/`

## Repo Mode

A Code Anchor operates in one of two modes. Both declare the repo via
the `code:` key in `.anchor`.

### Inline Mode
The repo IS the anchor folder. Code and docs live together. Use when
all materials can be version-controlled together (private projects, or
projects where docs are public).

```
{kebab-name}/                        repo = anchor folder
├── .anchor                          has `code: .`
├── .git/
├── README.md
├── CLAUDE.md
├── {NAME}.md                        anchor page
├── {NAME} Docs/                     planning docs (standard base structure)
├── justfile                         build recipes
├── src/                             source code
└── docs/                            sync-pushed from Docs/ (optional)
```

`.anchor` contains: `code: .`

### Linked Mode
Docs live in the vault; code lives at `~/ob/proj/`. The `.anchor` file's
`code:` key points to the repo location. Use when docs should stay
private while code is public, or when the repo should not contain vault
files.

```
{CAB Folder}/                        in vault (~/ob/kmr/)
├── .anchor                          has `code: ../../proj/{path}/{repo}` (or absolute)
├── {CAB Folder}.md                  marker file
├── {NAME}.md                        anchor page
├── {NAME} Docs/                     planning docs (standard base structure)
└── CLAUDE.md

~/ob/proj/{path}/{repo}/             outside vault, reached via `.anchor` code:
├── .git/
├── README.md
├── justfile
├── src/
└── docs/                            sync-pushed from Docs/ (optional)
```

`.anchor` contains: `code: ../../proj/{path}/{repo}` (relative to anchor
root) or an absolute path.

### Choosing a Mode

- **Inline** when: private repo, or you don't mind docs in the repo
- **Linked** when: public repo with private planning docs, or repo is
  large/complex and shouldn't live in the vault

## Naming Conventions

- **kebab-case** = repository / folder name
- **{NAME}** = slug or anchor identifier used for all doc files
- Example: `dict-a-mux` (repo) → `DMUX` (slug) → `DMUX Docs/`, `DMUX.md`

## Setup Checklist (additions to base)

1. Choose repo mode (inline or linked)
2. Add `code:` key to `.anchor`:
   - Inline: `code: .`
   - Linked: `code: <relative-or-absolute-path-to-repo>`
3. Create README.md in repo; CLAUDE.md stays in the anchor root only
4. If justfile exists: add standard recipes (`forge`, `test`, `publish`)
5. Register sync-push targets if User/ or Dev/ docs exist

## Audit

Type-specific structure checks for Code Anchors. These are run by
`/audit structure` after the common checks.

### Required files

- `.anchor` with a `code:` key — the code repository must be declared
- `{NAME} Docs/{NAME} Dev/` folder with dispatch page (`{NAME} Dev.md`)
- `{NAME} Docs/{NAME} Design/` folder with dispatch page (`{NAME} Design.md`) — per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]]; holds Architecture + Interface
- `{NAME} Docs/{NAME} User/` folder with dispatch page (`{NAME} User.md`)
- `{NAME} Docs/{NAME} Dev/{NAME} Files.md` — codebase file tree
- `{NAME} Docs/{NAME} Design/{NAME} Interface.md` — top-level layer contract (REQUIRED for Code, per [[CAB Interface]]; relocated from `{NAME} User/` per F094 Q3=A — 2026-06-01)
- `README.md` in the repo root

### Required dispatch rows

- **Dev** row in anchor page dispatch table, linking to Dev dispatch
- **Design** row linking to Design dispatch (per F094)
- **User** row if User folder exists

### Dispatch row format

Dispatch-table rows on a code-trait anchor page use **bare wikilinks only** — no markdown-link form, no path-based `hook://` URLs in row cells, no strikethrough wrappers.

**With children** — the row anchors a sub-anchor that itself has a dispatch table — `| [[{Name}|{alias}]]+ | [[{Child1}|{alias}]], [[{Child2}|{alias}]], ... |`. The `+` suffix on the left-column wikilink marks the row as expandable. The right column packs comma-separated wikilinks to the children, one alias per child.

**Without children** — the row anchors a leaf with no sub-dispatch — `| [[{Name}|{alias}]] | {description} |`. The right column is a free-text description.

**Reference example:** `~/ob/kmr/SV/ww/svar-docs/SVAR.md` lines 11–17 shows both forms on a `cab-traits: code` anchor.

**Forbidden forms** — any of these renders as struck-through and is treated as broken:

- `~~[Name/Name](hook://Name%20path/Name%20path)~~` — markdown-link with path-based hook URL wrapped in strikethrough
- `[Name](hook://Name)` — any markdown-link-with-hook-URL in a row cell
- Strikethrough wrappers (`~~ ... ~~`) anywhere in a row

**Breadcrumb exception:** the breadcrumb at the *top* of the anchor page legitimately uses `[Name](hook://p/{slug})` form — `hook://p/<slug>` is the only resolvable hook-URL form, used for jumping to an anchor by slug. Dispatch rows *below* the breadcrumb stay in pure wikilink form.

### Code-specific checks

- `.anchor` has a `code:` key, and that path resolves to an existing
  directory (absolute, or relative to anchor root; `.` for inline)
- Dev dispatch page links to all module docs in the Dev folder
- Files.md exists and lists source files
- If `justfile` exists in repo, verify it has standard recipes
  (at minimum: `test`)
- CLAUDE.md exists at anchor root only — not duplicated in the repo

## Anchor-page example

Worked anchor-page example carrying this trait: [[HBR]] (a synthetic Code project). The full catalog of anchor-page kinds and their examples is in [[FCT Anchor Page]].

# BRIEF

- **This file IS the Code trait specification** — the authoritative delta-from-[[CAB Base]] for anchors that own a git repository; the `code` trait in `cab-traits:` resolves here for structure, audit, and setup rules.
- **NOT a place for general anchor rules** — anything that applies to every anchor regardless of trait belongs in [[CAB Base]]; trait-specific rules for other traits (Skill, Paper, Topic, Simple) belong in their own `traits/<Trait>.md` file, not here.
- **Inclusion test** — a rule belongs here only if it is true for *every* Code anchor and *false or absent* for non-Code anchors (e.g. the `code:` key in `.anchor`, the README.md in repo root, the inline-vs-linked repo modes). Generic markdown/dispatch-table rules go to [[markdown]] or [[CAB Base]] respectively.
- **Two repo modes are load-bearing** — Inline (`code: .`, repo IS anchor folder) and Linked (`code:` points outside vault, typically to `~/ob/proj/`). Don't conflate; both must remain documented as first-class because real projects use both (e.g. `ob-utils` is Linked, most private projects are Inline).
- **Audit section mirrors `/audit structure` script behavior** — Required files / Required dispatch rows / Code-specific checks correspond to actual checks; changing wording here without updating the audit script (or vice versa) silently desyncs the spec from enforcement.
- **Dispatch row format rules are prescriptive, not descriptive** — the bare-wikilink-only rule and the explicit Forbidden forms list exist because past anchors drifted into struck-through markdown-link forms; keep the Forbidden list intact when editing.
- **Don't inline content owned by sibling specs** — Interface lives in [[CAB Interface]], dispatch-row mechanics in the [[progressive-disclosure]] discipline, brief/TLDR rules in [[FCT Brief]]; reference, don't duplicate.
