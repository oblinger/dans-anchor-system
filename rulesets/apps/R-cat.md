# RULESET R-cat
include::
where:: `file:{anchor}/**/*.md`
description:: how the catalog operates — the checkable layer under [[CAT Decisions]]' D-records

**Registered 2026-09-02 per [[Tink Backlog#^T362|T362]] Q1 (Dan, 2026-09-01).** This block lived in [[CAT Decisions]] from 2026-08-31 as prose: Warden's corpus is a single directory and nothing under the vault compiles. It now lives here, activated by the `cat` trait on `SYS Catalog/.anchor` — `warden compile` derives the trait name from the ruleset name. [[CAT Decisions]] links here and holds no copy. Whether each rule *fires* is measured, not assumed — [[Atticus Backlog#^T188|T188]] stage 4.

### RULE R-cat-01 — Every catalog entry names where its documentation lives (sampled)

implements D1. Every entry page — a page describing one asset (a drive, a machine, an app, a repo, a photo library) — carries a **docs pointer**: a `Docs:` line or table row wiki-linking where that asset's documentation, procedures and decisions live. Shared doctrine may be named once per sub-catalog set (fifteen drive pages may each point at the same [[Disk Procedures]]); an asset with no doctrine anywhere states that (`Docs: none yet`) so absence is visible rather than silent.

**Check pattern:** for each entry page under a sub-catalog (excluding index pages, doctrine pages, templates, and Track/Yore surfaces), assert a line or table row labeled `Docs` whose value is a wiki-link or an explicit `none yet`.

**Why:** the recurring failure this estate has actually suffered is not missing documentation but documentation nothing points at (D1 names the `SYS Wiring` incident). A pointer costs one row and makes the absence auditable.

### RULE R-cat-02 — Every sub-catalog root page exists and resolves (checked)

implements D3. Every sub-catalog folder named in [[CAT]]'s dispatch table contains an index page named for its slug (`Disk/Disk.md`, `App/App.md`, `Computer/Computer.md`), so the `[[slug]]` links the dispatch table carries resolve to a real page.

**Check pattern:** for each sub-catalog folder directly under `SYS Catalog/`, assert a `<folder-slug>.md` (or aliased equivalent) exists inside it.

**Why:** a sub-catalog whose own root is missing is the strongest instance of the R-cat-01 failure — the dispatch table points, nothing answers, and no reader notices because the link renders identically either way. `Computer/` shipped in exactly this state and was found by an audit rather than by anyone looking (T188).
