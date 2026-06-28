---
description: "facet spec for the versions/ release-artifact store — the immutable, tag-gated folder a project's published builds land in"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Output]] → [FCT Versions](hook://p/FCT%20Versions)

# FCT Versions
Facet spec for the `versions/` folder — the immutable, flat store of published release artifacts (`<version> <app>.dmg`) a code project promotes builds into at `publish` time.

**Related:** [[FCT Code Repository]],  [[FCT Outputs]],  [[FCT Facet]]
**Examples:** [[HBR Versions\|worked example]],  [[OBU\|live monorepo instance]]

**TLDR** — A single flat `versions/` folder at a code repo's root holding the **immutable** published release artifacts, each named **`<version> <app>.dmg`** (version-first, so it sorts by version across every app sharing the repo). Promoted into only by the `publish` recipe; the matching pushed git tag is the published-marker. **Cardinality: one** folder per repo (holding **many** artifact files). Detection: **folder-existence**. The policy lives in [[OBU Decisions]] D02; this facet is its reusable, citable form.

A code project that ships a downloadable build needs one predictable place for *released* artifacts — distinct from the disposable `dist/` scratch directory where builds are assembled and freely overwritten. The `versions/` folder is that place: once `publish` promotes a build into it, that copy is never rewritten. The folder is the *output* surface of the build/release tooling — which is why it sits in the [[FCT Output]] family.

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

Formalized in the embedded [[#RULESET R-versions]] below: artifacts use the `<version> <app>.dmg` form; the folder is flat and shared; promoted artifacts are immutable; each names a pushed tag; the store lives in the repo / an offload location, **not** the snapshotted vault (per [[feedback_keep_ob_lean]]).

## Expected usage

Written **only** by the `publish` recipe in `dist/release.just`; `build-dmg` writes the disposable `dist/` copy, never `versions/`. Read by humans (download a past release) and by `build-dmg`'s guard (a version whose tag is pushed is protected). The post-publish bug-fix path is a **new version**, never an overwrite.

## Skills and audits that attach

The `publish` / `build-dmg` recipes (shared `dist/release.just`) write and guard it; `/audit` checks instances against [[#RULESET R-versions]]. The governing decision is [[OBU Decisions]] D02; the realization is described in [[OBU Build Arch]].

# RULESET R-versions
include::
where:: file: versions/*.dmg
description:: the versions/ release-artifact store — immutable, tag-gated published builds

What `/audit` checks on a project's `versions/` store. Tiers: **checked** (mechanically verifiable), **sampled** (spot-checked), **stated** (a principle the author honors). The governing policy is [[OBU Decisions]] D02.

### RULE R-versions-01 — Artifacts use `<version> <app>.dmg`, version first (checked)
check:: regex_basename ^\d+\.\d+\.\d+(-[0-9A-Za-z.]+)? .+\.dmg$
Each file in `versions/` is named `<semver> <app>.dmg` — the version first (pre-release suffix allowed), a single space, the app name, then `.dmg`.
**Check pattern:** every `versions/*.dmg` basename matches `^\d+\.\d+\.\d+(-[0-9A-Za-z.]+)? .+\.dmg$`.
**Why:** version-first is what makes a plain sort order the folder by version across every app sharing it; a per-app or name-first scheme loses that.

### RULE R-versions-02 — One flat shared folder at the repo root (checked)
The store is a single `versions/` at the repo root, holding artifact files directly — no per-app subfolders, no per-version subfolders, no nesting.
**Check pattern:** `versions/` contains only artifact files (no subdirectories); there is no second `versions/` elsewhere in the repo.
**Why:** in a monorepo the *one* shared flat folder is what lets several components coexist and sort together; per-app folders re-fragment the store.

### RULE R-versions-03 — Promoted artifacts are immutable (stated)
Once `publish` promotes a build into `versions/`, that file is never rewritten in place. A post-publish fix ships as a **new version** (`bump-version`), producing a new file — never an overwrite of an existing one.
**Why:** the store is the durable record of what shipped; an in-place rewrite destroys that record and the D01 build-stamp's forensic value.

### RULE R-versions-04 — Each artifact corresponds to a pushed release tag (sampled)
Every `<version> <app>.dmg` has a matching pushed git tag — `v<version>` (standalone repo) or `<app>/v<version>` (monorepo) — the published-marker that `build-dmg` then guards against.
**Check pattern:** for a sampled artifact, the corresponding tag exists on the remote.
**Why:** `publish` pushes the tag and promotes the DMG as one act; an artifact with no tag is an un-guarded, half-published build.

### RULE R-versions-05 — The store lives in the repo / an offload, not the snapshotted vault (stated)
`versions/` lives in the code repository (or a dedicated offload location), never inside the snapshotted vault, so published binaries don't bloat every snapshot.
**Why:** the vault is snapshotted; DMGs are large and immutable — keeping them out of it keeps `~/ob` lean (per [[feedback_keep_ob_lean]]).

# BRIEF

- **This is a CAB facet spec, not a per-project record.** Rules here describe how *any* project's `versions/` store is shaped — never inline one project's actual release list. Worked instances are linked in the `Examples` row ([[HBR Versions]] = worked example; [[OBU]] = the live monorepo that adopts it).
- **`dist/` vs `versions/` is the load-bearing distinction** — `dist/` is disposable scratch (written by `build-dmg`, freely overwritten); `versions/` is the immutable promotion target (written only by `publish`). Any edit that blurs that boundary is load-bearing; re-read [[OBU Decisions]] D02 before relaxing it.
- **Version-first naming is the whole point.** `<version> <app>.dmg` (not `<app> <version>`) is what makes the flat shared folder sort by version across a monorepo's apps. Don't "tidy" it into per-app subfolders — R-versions-02 forbids exactly that.
- **Inclusion test for additions:** content belongs here only if it concerns the *release-artifact store's* shape (location, naming, immutability, tag correspondence, where it lives). Versioning mechanics (the `VERSION` file, `bump-version`) live in D01; the recipe wiring lives in [[OBU Build Arch]]; this facet is scoped to the folder.
- **Governing decision is [[OBU Decisions]] D02** — this facet is the reusable, citable form of that OBU-local D-record; if D02's convention changes, update both in the same pass.
