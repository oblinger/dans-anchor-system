# RULESET R-versions
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file: versions/*.dmg`
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
