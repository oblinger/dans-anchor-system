---
description: Query facet — the format of an anchor's `{slug} queries.md`, the file `/ask` builds to ask the user questions. Rules about what a valid queries file looks like.
---

# DAS Query
The asking surface: one `{slug} queries.md` per anchor, in `{slug} Track/`, that `/ask` builds and trims.

| -[[DAS Query]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Query](hook://p/DAS%20Query) |
| --- | --- |
| Related | [[templates/query.md\|query template]],  [[DAS Ask]] (the skill that builds it),  [[DAS Status]],  [[DAS Messages]], |
| Examples | [[SKA queries\|real instance (SKA anchor)]],   |
| Rules | [[R-query]],   |

**TLDR** — One `{slug} queries.md` per anchor (cardinality: one), in `{slug} Track/`, owned by the `/ask` skill. Opens with the anchor's **status banner** (TAG + counts) as its H1, then the fixed five-section order (`## Agent Resolutions` → `## Verifications` → `## Immediate Questions` → `## Questions` → `## Ready`); empty sections omitted. Verifications are agent-run / user-judged — never "user runs X". Questions are self-contained or wiki-linked. The whole body is **copied verbatim into the anchor's `Q.md` section** (F231 — the query file is the queue-file content; there is no separate triage view). The file shrinks toward empty as answers are applied. Validated by `/audit doc` via `R-query`.

## What it is

`{slug} queries.md` is the single per-anchor surface where the user answers everything the agents need from them — **and it is simultaneously the anchor's status view**: its banner + body are copied into the anchor's section of the global `~/ob/kmr/Q.md` dashboard (F231, retiring the separate triage view). The **`/ask` skill** ([[DAS Ask]]) *drives* it (determination routing — walking open questions, running verifications ahead of time), but the file itself is **mechanically rendered** by `queries-render.py` (`audit/scripts/`), fired on every `state` mutation via `audit-q --fix`; the same render copies the body into `Q.md`. **This facet** governs what the resulting *file* must look like, so it can be audited (`/audit doc`, the F167 on-write hook). The skill + renderer cite these rules rather than restating them.

## Parts

- **Frontmatter + banner H1** — `description:` then the **status banner** as the H1 (see § The banner). Inside `queries.md` the banner self-links `[[{slug}|{slug}]]`; the copy in `Q.md` links `[[{slug} queries|{slug}]]` (the click-into page).
- **Five sections, fixed order** (each omitted when empty): `## Agent Resolutions`, `## Verifications`, `## Immediate Questions`, `## Questions`, `## Ready`.
- The file is **agent-owned and trimmed on answer** — answered items are removed, so it shrinks toward empty.
- **Copied into `Q.md`** — the banner (retargeted) + the whole body become the anchor's per-anchor section in the global dashboard, bubbled to the top and destructively rewritten on each render (see § Copied into Q.md).

## The banner

The H1 is the anchor's **status banner**, the exact form (spacing locked — the renderer and `R-query-16` depend on it):

`# [<TAG>]  [[{slug}|{slug}]]  -  Ready N    Questions N   |   Now N    Next N    Later N    Verify N    Icebox N`

- **TAG cascade** (first match wins, U and A combine): `[U]` any `[Questions]`/`[Verify]` items · `[A]` any `[Active]`/`[Ready]` items · `[U+A]` both · `[G]` items only in `## Now`/`## Next` · `[-]` items only in `## Later` · `[]` nothing anywhere.
- **Two headline numbers** — `Ready` = `[Active]`+`[Ready]`(+`[Agreed]`) in active horizons; `Questions` = pending `Q<n>` across `[Questions]`-row feature docs plus `[Verify]`-bracket rows.
- **Horizon group** — `Now`/`Next`/`Later`/`Verify`/`Icebox` raw per-H2 bullet counts (placement, not state).
- **Spacing** — two spaces after `[<TAG>]`; three spaces around the `-`; four spaces between counts in a group; `   |   ` (three-space-pipe-three-space) between the headline pair and the horizon group. A trailing `{N}` appears only when the anchor's `B-QFix` carries N > 0 residuals.

## Copied into Q.md

The banner + body are copied into the anchor's section of `~/ob/kmr/Q.md` (the global queue-file dashboard) — the single cross-anchor surface. The copy is **agent-owned and destructively rewritten** on each render: the renderer removes the existing section and re-inserts the fresh one at the top of `Q.md` (bubble-to-top). The only difference from the on-disk `queries.md` is the banner link target (`[[{slug} queries|{slug}]]` in `Q.md`, so the user clicks over to the drain page). There is no separate per-anchor triage file and no separately-formatted triage render — the query file *is* the queue-file content.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + the [[R-query]] ruleset; the procedure that builds the file lives in [[DAS Ask]].)*

- **`R-query` is in the `R-doc` umbrella** — so `/audit doc {slug} queries.md` and the F167 on-write hook validate it. If the spec changes, fix it here; [[DAS Ask]] cites these rules and follows.
