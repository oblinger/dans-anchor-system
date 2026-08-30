---
description: Query facet — the format of an anchor's `{slug} queries.md`, the file `/ask` builds to ask the user questions. Rules about what a valid queries file looks like.
group: file
---

| -[[DAS Query]]- | → [[DAS]] → [[FCT]] → [DAS Query](hook://p/DAS%20Query)  |
| --- | --- |
| Related | [[templates/query.md\|query template]],  [[DAS Status]],  [[DAS Messages]],   |
| [[DAS Ask]]  | the skill that builds it |
| Examples | [[Tink queries\|real instance (SKA anchor)]],   |
| Rules | [[R-query]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS At Entity]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Proj]],  [[DAS Project Page]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[DAS Skill]],  [[DAS Specs]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Query
The asking surface: one `{slug} queries.md` per anchor, in `{slug} Track/`, that `/ask` builds and trims.

**TLDR** — One `{slug} queries.md` per anchor (cardinality: one), in `{slug} Track/`, owned by the `/ask` skill. Opens with the anchor's **status banner** (TAG + counts) as its H1, then the fixed five-section order (`## Agent Resolutions` → `## Verifications` → `## Immediate Questions` → `## Questions` → `## Ready`); empty sections omitted. Verifications are agent-run / user-judged — never "user runs X". Questions are self-contained or wiki-linked. The whole body is **copied verbatim into the anchor's `Q.md` section** (F231 — the query file is the queue-file content; there is no separate triage view). The file shrinks toward empty as answers are applied. Validated by `/audit doc` via `R-query`.

## What it is

`{slug} queries.md` is the single per-anchor surface where the user answers everything the agents need from them — **and it is simultaneously the anchor's status view**: its banner + body are copied into the anchor's section of the global `~/ob/kmr/Q.md` dashboard (F231, retiring the separate triage view). The **`/ask` skill** ([[DAS Ask]]) *drives* it (determination routing — walking open questions, running verifications ahead of time), but the file itself is **mechanically rendered** by `queries-render.py` (`audit/scripts/`), fired on every `state` mutation via `audit-q --fix`; the same render copies the body into `Q.md`. **This facet** governs what the resulting *file* must look like, so it can be audited (`/audit doc`, the F167 on-write hook). The skill + renderer cite these rules rather than restating them.

## Parts

- **Frontmatter + banner H1** — `description:` then the **status banner** as the H1 (see § The banner). Inside `queries.md` the banner self-links `~~[[{slug}|{slug}]]~~`; the copy in `Q.md` links `~~[[{slug} queries|{slug}]]~~` (the click-into page).
- **Five sections, fixed order** (each omitted when empty): `## Agent Resolutions`, `## Verifications`, `## Immediate Questions`, `## Questions`, `## Ready`.
- The file is **agent-owned and trimmed on answer** — answered items are removed, so it shrinks toward empty.
- **Copied into `Q.md`** — the banner (retargeted) + the whole body become the anchor's per-anchor section in the global dashboard, bubbled to the top and destructively rewritten on each render (see § Copied into Q.md).

## The banner

The H1 is the anchor's **status banner**, the exact form (spacing locked — the renderer and `R-query-16` depend on it):

`# [<TAG>]  ~~[[{slug}|{slug}]]~~  -  Ready N    User N   |   Now N    Next N    Later N   |   Parked N    Waiting N    Icebox N`

### The design commitment: three zones, ordered by attention

Ruled by Dan 2026-08-07 and recorded here because it is the **only** thing the layout is for. The three zones are not a taxonomy — they are a reading order:

| zone | question it answers | contents |
|---|---|---|
| **1** | what do I act on? | `Ready`, `User` — visibility classes; `Inbox` when non-zero |
| **2** | what is coming? | `Now`, `Next`, `Later` — horizons |
| **3** | what am I not looking at? | `Parked`, `Waiting`, `Icebox` — two classes **and** one horizon |

**Zone 3 deliberately mixes a horizon in with two classes, and that mix is correct.** Dan named it and kept it: *"I know it kind of mixes things up a little bit, but I do think that's the better ordering… The reason is simply visibility."* An editor who later regularizes the zones into classes-then-horizons will have destroyed the design. If a new count is added, it goes in the zone matching **how much attention it deserves**, never the zone matching what kind of thing it is.

**Every count is a count of ROWS**, including `User`. Dan, 2026-08-07: *"if I have 10 items that each have one question, I'm much more motivated to answer a bunch of questions since I'm going to unblock a tremendous amount of work. If I had one ticket that had 10 questions, I'm not really very motivated to work on that."* The number that drives action is **how many things are blocked on the user**, not how much answering work is queued — so a row carrying four open questions contributes **1**, not 4. This reverses the earlier behaviour, which counted individual `Q<n>` entries.

- **TAG cascade** (first match wins, U and A combine): `[U]` any `[Questions]`/`[Verify]` items · `[A]` any `[Active]`/`[Ready]` items · `[U+A]` both · `[G]` items only in `## Now`/`## Next` · `[-]` items only in `## Later` · `[]` nothing anywhere.
- **Zone 1 — class counts, rows.** `Ready` = rows whose bracket set contains `[Ready]`, `[Active]` or `[Agreed]`. `User` = rows whose bracket set contains `[Questions]`, `[User]` or `[Designing]`. A row whose bracket is a set counts in **both**, so the two numbers may sum to more than the row count — that is intended, not a defect (see [[DAS Backlog]] § The state table).
- **Zone 1 is scoped to the active horizons** (`## Now`, `## Next`), and this scoping is **stated rather than implicit** — zone 2 already reports the horizons, so a hidden filter in zone 1 produces a number no reader can reconcile.
- **Zone 2 — horizon group.** `Now`/`Next`/`Later`, raw per-H2 bullet counts: placement, not state. `Verify` **left this group** when it became a class; it is now inside `Parked`.
- **Zone 3 — the quiet group, rows.** `Parked` = `[Verify]` + `[Blocked …]`, unscoped by horizon; `Waiting` = `[Waiting …]` + `[Watching …]`, unscoped; `Icebox` = the Icebox file's row count. Parked and Waiting are counted here **precisely because they are omitted from the body** — a class that appears in no list and no count is invisible everywhere but the raw backlog.
- **Spacing** — two spaces after `[<TAG>]`; three spaces around the `-`; four spaces between counts within a group; `   |   ` (three-space-pipe-three-space) between groups. Two fields are conditional and both follow the same rule — *show only when non-zero*: `Inbox N`, immediately after `User N` in zone 1, and the trailing `{N}` residual count. `R-query-16` locks this form and moves with it.
- **`Inbox N` — pending entries in `{slug} Inbox.md`** (T131 leg 2). An undrained entry is something to act on, so it sits in zone 1 by the attention rule above rather than with the quiet counts. PENDING is defined *negatively against the tag vocabulary*: an entry is processed iff its section carries a sanctioned `R-fct-inbox-03` tag (`DONE` or `MOVED → …`), and `Inbox N` counts the dated entries that do not. Deliberately no dependence on `R-fct-inbox-02`'s claim about *where* a tag sits or whether every H2 must have one — that sentence is contested (it forbids the untagged pending state `R-fct-inbox-04` presupposes) and it belongs to SKA. Reading only the vocabulary keeps this count correct however that is settled.

**Zone 1 is scoped and zone 3 is not, so the three zones do not reconcile — by design.** Zone 1 counts only rows the body lists, which is **the active horizons and nothing else**; zone 3 counts its two classes across every live horizon.

*(This sentence read "…the active horizons, **plus the `[Questions]`/`[Verify]` rows that render under `## Later`**" between 2026-08-07 and 2026-08-19. That clause described the implementation rather than the design, and the implementation was wrong — see § A `## Later` row renders nowhere below. Removed, not softened: it contradicted the sentence two bullets up that scopes zone 1 to `## Now` / `## Next`.)* The asymmetry follows from what each zone is *for*: zone 1 answers *what do I act on*, which is meaningless outside the active horizons, while zone 3 answers *what am I not looking at*, which is meaningless if it is scoped to what you are looking at.

The visible consequence is that **a row sitting in `## Later` appears in no class count at all.** That is not a leak: every live row is counted exactly once in zone 2, so the row is on the banner as part of `Later N` — it simply is not claimed by a class, because parking work in `## Later` is a statement that nobody is acting on it yet. **If such a row should be acted on, the fix is to promote its horizon, not to widen zone 1** — widening zone 1 would put work in the *act on it* zone that the backlog has explicitly deferred, which is the reverse of the reading order the whole layout exists to produce.

## A `## Later` row renders nowhere

**The body is the active horizons. `## Later` lists nothing, whatever bracket a row carries** — restored 2026-08-19 after a two-month drift, and the drift is worth recording because every step of it looked local and correct.

The design has said this in three places all along: the zone-1 scoping bullet above; F284 § Scope note (*"`Later` and `Icebox` are deliberately out of scope… a total render over every horizon would bury the frontier it exists to surface"*); and `queries-render.py`'s own zone-3 comment, which says `Parked` and `Waiting` are counted *"precisely BECAUSE they are omitted from the body."*

What happened instead:

1. **2026-06-02** — a user direction, carried in the renderer as a comment: *"only count from ACTIVE horizons. Rows parked in `## Later` or `## Verify` are passive observation, not active questions."*
2. **2026-06-04** — MUX showed `Questions 0` on the banner while the body listed two `## Later` rows. Two repairs were available: **narrow the body** to match the banner, or **widen the banner** to match the body. F305 took the second and deleted the 2026-06-02 direction in the same commit.
3. **After that**, `[Blocked …]` was admitted on real evidence (37 rows were rendering nowhere), and a quote attributed to the user — *"Ready, User and Parked are all shown"* — was added to justify the branch. That quote has **no primary source**: it appears only in the function's own comment and in documents citing it, and it enumerates *banner zone labels*, so even at face value it rules on what the banner **counts**, not on what the body **renders**.

**Nothing vanishes, and that is what makes the narrow reading safe.** The 37-rows finding is real; its answer is zone 3, not a body listing. A `[Blocked …]` row parked in `## Later` is counted in `Parked N` (unscoped by horizon) *and* in `Later N` — on the banner twice, and in the backlog file. It is deferred, not disappeared. Measured at the restore: 86 rows across 11 backlogs left the body, and TINK's queue went from 54 bullets to 8.

**The corollary for `[Blocked <handle>]` and `## Blockers`:** a blocker is elevated only when a row that **renders** waits on it. A parked waiter promotes nothing, because the reader is never told it is blocked — *"a blocker for something parked in `## Later` is not a blocker, it is a note"* (2026-07-30). `C55`'s visibility check carries the same precondition for the same reason.

## Copied into Q.md

The banner + body are copied into the anchor's section of `~/ob/kmr/Q.md` (the global queue-file dashboard) — the single cross-anchor surface. The copy is **agent-owned and destructively rewritten** on each render: the renderer removes the existing section and re-inserts the fresh one at the top of `Q.md` (bubble-to-top). The only difference from the on-disk `queries.md` is the banner link target (`~~[[{slug} queries|{slug}]]~~` in `Q.md`, so the user clicks over to the drain page). There is no separate per-anchor triage file and no separately-formatted triage render — the query file *is* the queue-file content.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + the [[R-query]] ruleset; the procedure that builds the file lives in [[DAS Ask]].)*

- **`R-query` is in the `R-doc` umbrella** — so `/audit doc {slug} queries.md` and the F167 on-write hook validate it. If the spec changes, fix it here; [[DAS Ask]] cites these rules and follows.
