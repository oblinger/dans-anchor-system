---
description: "the proj facet — an optional root-level {slug} Proj/ folder holding an anchor's subprojects as a dated, reverse-chronological stream; renamed from Subs 2026-08-25"
group: folder
---

| -[[DAS Proj]]- | → [[DAS]] → [[FCT]] → [DAS Proj](hook://p/DAS%20Proj)  |
| --- | --- |
| Related | [[DAS WP]],  [[DAS Features]],  [[DAS Backlog]],  [[DAS Dot Anchor]],  [[DAS Anchor Page]],   |
| Examples | [[SV Proj\|reference instance]],  [[A2X Subs\|legacy instance]],   |
| Rules | [[R-proj]],   |

# DAS Proj
An anchor's subprojects as a **dated, named, reverse-chronological stream** — an optional root-level `{slug} Proj/` folder holding one folder per project, newest first on the index page.

**TLDR** — a **proj** is a focused sub-effort inside an anchor that deserves its own folder: an engagement, a work effort, a subproject of days-to-months. It starts as one spine page and may grow sibling docs, its own spine, even its own backlog — all optional. The stream is the point: projects arrive over time, and the dated names plus the reverse-chron index make the folder read as a history ("oh yeah, that was last year"). **Cardinality: one** — at most one `{slug} Proj/` per anchor, elective, holding many project folders. The reference instance for the dated form is [[SV Proj]] (with a `Prior/` archive and a spine template); [[A2X Subs]] is the grandfathered minted-form instance under the legacy zone name.

**Renamed from Subs (Dan, 2026-08-25).** "Sub" named the relation; "Proj" names the thing. The original worry — overloading "proj" — dissolves because the zone is always anchor-prefixed: `SV Proj` cannot be confused with a global projects home, and `DAS Proj` / `SV Proj` reads as "subproject" without saying so. The rename was forced honestly: the first real stream instance ([[SV Proj]]) was built by hand as `Proj` with dated names, never adopting the Subs grammar — practice out-voted the spec.

## Location

`{anchor}/{slug} Proj/` — at the **anchor root**, sibling of `{slug} Design/`, `{slug} Track/`, and `{slug} Log/`. Not inside Track or Design (Dan's ruling, F331 Q2): projects grow many internal files and are neither pure design content nor pure tracking metadata.

The folder holds an index page `{slug} Proj.md` with a dispatch table listing projects **reverse-chronologically** (newest first) and a `...` catch-all, so a project folder dropped in is surfaced without being hand-listed. A `{slug} Proj Prior/` subfolder may hold finished/dead/dormant projects, keeping the live listing short while preserving the history. The **container folder itself carries no `.anchor`** — it is a zone of the parent anchor, not an anchor of its own.

## Naming grammar — two forms

- **Dated (default)** — `YYYY-MM-DD Name/` (or `YYYY-MM Name/` when day precision is noise), with a matching top page of the same name. The date is the project's start (or first contact); it earns its keep because projects are remembered temporally. Collision avoidance is natural — date + name — so **no mint is required**; the index page is the registry.
- **Minted (elective variant)** — `{SLUG}{NNN} - Name/`, the F331 form: fused slug + zero-padded F-number from the anchor's ordinary `state define <anchor> Backlog F+` mint, for subprojects that want a backlog row as their tracking handle — a subproject is *just a big feature* from the mint's point of view. Internal files carry the `{SLUG}{NNN} ` prefix. Use this form when backlog-linkage matters; use the dated form when the stream is the tracking.

## External content — the thin-spine discipline

Many projects keep most or all of their working content in a remote tool (Notion, Google Drive, a partner's system). The rule: **if it is in the stream, it gets a local folder — however thin.** Remote-only is acceptable for bookmarks, never for projects, because:

- **Stream integrity** — the reverse-chron listing is only trusted if every project is in it; one remote-only project makes the register lie by omission.
- **The register layer is local-native** — what was promised, when, who the players are, what is owed: that layer is authored here and exists in no remote tool (see [[SV Proj Template]] — the masthead *is* this layer).
- **Agents are blind to remote-only** — a spine page is the one greppable, linkable landing point; a Notion-only project is invisible to every agent workflow.
- **External content rots** — permissions, reorgs, departures. The spine records the pointers and the shape.

**Declare the external home with the `proj-home::` inline field** — a DataView `::` field in the spine page's body or masthead table (visible to the reader, never frontmatter) naming where the real content lives. A folder carrying `proj-home::` is *deliberately thin*, not incomplete. A HookAnchor external-link command (jump straight to the remote home) is a welcome complement — navigation, not record.

**Future direction (unbuilt):** an automated pull-down that caches `proj-home::` content locally, so remote material is tracked and greppable. The cache and the register stay distinct layers — a perfect cache still doesn't author the promises/players/obligations view; the register is why the spine exists even after caching lands.

## Discovery

No standing alias by default. The parent anchor's dispatch table carries a hand-authored row (above the separator) linking the Proj index — the path is: jump to the parent page, click through. An `ha` alias for the single currently-hot project is an optional convenience, deleted at close-out.

## Retirement

Dated form: move the folder into `{slug} Proj Prior/` (or strike its index row) — the stream keeps the history. Minted form: the backlog row goes `[Done]`; the folder stays as the record or is yored wholesale. No slug was minted in either form, so slug-retirement is never involved — this cheapness is the point.

## When appropriate

**Use a proj when** a sub-effort will accumulate several files over days-to-months and reads as one focused project — or when an engagement stream (partners, contracts, campaigns) wants a dated register. **Do not when** the work fits a single feature doc — that stays a plain `{SLUG}{NNN} - Title.md` in `{slug} Design/{slug} Features/`, and the Proj folder is never scaffolded ahead of need.

## Legacy — `Subs`

Pre-rename instances named `{slug} Subs/` (e.g. [[A2X Subs]]) **remain valid and are never renamed**, like the pre-F298 feature filenames: matchers and resolvers accept both zone names permanently. New zones are always `{slug} Proj/`.

## Tooling

The workflow resolvers (`backlog-edit.py`) glob `* Proj/{stem}/{stem}.md` and `* Proj/{stem}.md` (plus the legacy `* Subs/` forms) beside the Features locations, so `state` verbs resolve a minted project's top page exactly as they resolve a feature doc.

## Audit

[[R-proj]] — zone location and index page, folder/top-page naming (both grammars), internal-file prefix (minted form), `.anchor` discipline, backlog-row invariant (minted form), and the `proj-home::` thin-spine declaration. All stated, not yet checked.

# BRIEF

- **What this is** — the folder-form home for an anchor's subproject stream. Specified originally as Subs by [[TINK331 - Subproject convention: short-lived sub-efforts inside an anchor|TINK F331]] (2026-08-14); renamed and re-grounded as Proj by TINK F596 (2026-08-25, Dan + Tink): dated names as the default grammar, F-minted names as the elective variant, external-home discipline added. [[SV Proj]] is normative for the dated form; [[A2X Subs]] for the minted layout.
- **The container folder must NOT be an anchor.** Only the project folders inside it may carry `.anchor` (declaring their own slug — for minted projects, the fused form). HookAnchor's daemon has repeatedly auto-stamped an empty `.anchor` onto the container when nearby files change — remove it when it appears; a container `.anchor` makes the zone resolve as a competing anchor.
- **Never put the parent's slug in a project's `.anchor`** — resolution goes ambiguous. The project's own slug or nothing.
- **Projects are not Features-folder content.** A numbered folder in `{slug} Design/{slug} Features/` is the *folder-doc feature* form; the Proj folder exists precisely to keep multi-file projects from swamping that listing. One home per item, chosen by whether it reads as one doc or one project.
