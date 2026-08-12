---
description: "facet spec for the versions/ release-artifact store — the immutable, tag-gated folder a project's published builds land in"
group: file
---

| -[[DAS Versions]]- | → [[DAS]] → [[FCT]] → [DAS Versions](hook://p/DAS%20Versions)  |
| --- | --- |
| Related | [[DAS Code Repository]],  [[DAS Outputs]],  [[DAS Facet]],   |
| Examples | [[HBR Versions\|worked example]],  [[OBU\|live monorepo instance]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Versions
Facet spec for the `versions/` folder — the immutable, flat store of published release artifacts (`<version> <app>.dmg`) a code project promotes builds into at `publish` time.

**TLDR** — A single flat `versions/` folder at a code repo's root holding the **immutable** published release artifacts, each named **`<version> <app>.dmg`** (version-first, so it sorts by version across every app sharing the repo). Promoted into only by the `publish` recipe; the matching pushed git tag is the published-marker. **Cardinality: one** folder per repo (holding **many** artifact files). Detection: **folder-existence**. The policy lives in [[OBU Decisions]] D02; this facet is its reusable, citable form.

A code project that ships a downloadable build needs one predictable place for *released* artifacts — distinct from the disposable `dist/` scratch directory where builds are assembled and freely overwritten. The `versions/` folder is that place: once `publish` promotes a build into it, that copy is never rewritten. The folder is the *output* surface of the build/release tooling — which is why it sits in the [[DAS Output]] family.

## What it is

The store of **published** release artifacts for a project. The build/release tooling (the shared `dist/release.just`, per [[OBU Build Arch]]) draws a hard line between two folders: `dist/<app>-<version>.dmg` is the **disposable** build (overwritten freely during the bump → build → test loop), and `versions/` is the **immutable** promotion target. `publish` is the only writer; it copies the verified DMG into `versions/` and pushes the release git tag in the same act.

## How it's detected

**Folder-existence** (non-default — not file-existence): a `versions/` directory at the **code repo root**. **Cardinality: one** `versions/` per repo; it holds **many** artifact files. In a monorepo with several versioned components, the *one* shared folder serves all of them — never a per-app `versions/`.

## Format

- One flat folder, `versions/`, at the repo root — no per-app subfolders, no nesting.
- Each artifact is named **`<version> <app>.dmg`** — the semver **first**, then a space, then the app name, then `.dmg`. Version-first so a plain directory sort orders the whole folder by version across every app: `versions/0.9.0 hello.dmg`, `versions/1.0.0 hello.dmg`, `versions/1.0.0 tauri-hello.dmg`.
- Each artifact corresponds to a **pushed release tag** (`v<version>` standalone, or `<app>/v<version>` namespaced in a monorepo) — the tag is the published-marker.

Below is a condensed reference instance; the linked examples above are the real worked ones.

```
my-app/                              code repo root
├── VERSION                          1.0.0  (D01 source of truth)
├── justfile                         imports dist/release.just
├── dist/                            DISPOSABLE — freely overwritten
│   └── my-app-1.0.0.dmg             scratch build
└── versions/                        IMMUTABLE — promoted by `publish`
    ├── 0.9.0 my-app.dmg
    ├── 1.0.0 my-app.dmg
    └── 1.0.0 my-helper.dmg          (monorepo: one flat folder, many apps)
```

## Constraints

Formalized in the embedded [[R-versions]] below: artifacts use the `<version> <app>.dmg` form; the folder is flat and shared; promoted artifacts are immutable; each names a pushed tag; the store lives in the repo / an offload location, **not** the snapshotted vault (per [[feedback_keep_ob_lean]]).

## Expected usage

Written **only** by the `publish` recipe in `dist/release.just`; `build-dmg` writes the disposable `dist/` copy, never `versions/`. Read by humans (download a past release) and by `build-dmg`'s guard (a version whose tag is pushed is protected). The post-publish bug-fix path is a **new version**, never an overwrite.

## Skills and audits that attach

The `publish` / `build-dmg` recipes (shared `dist/release.just`) write and guard it; `/audit` checks instances against [[R-versions]]. The governing decision is [[OBU Decisions]] D02; the realization is described in [[OBU Build Arch]].

# BRIEF

*(Maintainer note — this facet is scoped to the release-artifact store's shape (location, naming, immutability, tag correspondence, where it lives); additions belong here only if they concern that folder, never one project's actual release list. Versioning mechanics (the `VERSION` file, `bump-version`) live in [[OBU Decisions]] D01; the recipe wiring lives in [[OBU Build Arch]]. The governing policy is [[OBU Decisions]] D02 — this facet is its reusable, citable form; if D02's convention changes, update both in the same pass.)*
