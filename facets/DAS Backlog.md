---
description: "Active work tracking"
---
# DAS Backlog
The work queue — one `{slug} Backlog.md` per anchor, every unit of work as a row carrying bracket × horizon, F/T-numbered and block-anchored.

| -[[DAS Backlog]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Backlog](hook://p/DAS%20Backlog) |
| --- | --- |
| Related | [[templates/backlog.md\|backlog template]],  [[DAS Roadmap]],  [[DAS Icebox]],  [[DAS Query]],  [[workflow]],   |
| Examples | [[SKA Backlog\|real instance (SKA anchor)]],   |
| Rules | [[R-backlog]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — `{slug} Track/{slug} Backlog.md` is the anchor's workflow-state core: one bullet row per unit of work (`- **F<n> — Title** [Status] — body ^F<n>`) under horizon H2s (`## Now` / `## Next` / `## Later`) plus workflow H2s (`## Ready` / `## Active` / `## Verify` / `## Done`). Row ids are monotonic, zero-padded, never reused (F = feature, T = task, C = OpenSpec change); brackets carry the groomed state ([Ready] rows must name a `- **Next:**` step). Mutations go through `state`, never hand-edits; the render propagates each anchor's section into the vault-wide `Q.md`. **Cardinality: one per anchor.**
|  |  |
| **Table of Contents** |  |
| [[#Reference Example]] |  |
| [[#Format Specification]] |  |
| [[#Status brackets]] |  |
| [[#H2 sections]] |  |
| [[#Definition of Ready]] |  |
| [[#Item Status]] |  |
| [[#Design Principle — Minimize User Back-and-Forth]] |  |
| [[#The groom frontier]] |  |
| [[#Location]] |  |
| [[#Relationship to Other Planning Docs]] |  |

**Location:** `{slug} Docs/{slug} Plan/{slug} Backlog.md`

The backlog file (`{slug} Backlog.md`) holds ideas, low-priority tasks, and deferred work that don't belong on the active Todo or Roadmap yet. Items graduate to the Roadmap or Todo when they become priorities.

For items the user wants to remember but is **not** actively considering — distant-future / someday-maybe entries — use the optional [[DAS Icebox]] instead. Backlog is the *active* deferred-work list; Icebox is the *frozen* one.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Backlog.md` — Backlog.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# CAE Backlog

| -[[HBR Backlog]]- | |
| --- | --- |
| --- | |


## Active
- **F003 — Retry backoff polish** — Tune exponential-backoff caps after user feedback on long retries

## Ready
- **F001 — Cron syntax** — Support cron expressions for recurring task schedules

## Now
- **F002 — Task groups** [Designing] — Allow grouping related tasks that run as a batch
- **F007 — Webhook notifications** [Verify] — Webhook fires on task completion. Verify: trigger a test job and check that the configured webhook URL receives a POST with the documented JSON payload (see [[HBR PRD]] § Webhooks).

## Next
- **F004 — Priority levels** [ ] — Add high/medium/low priority beyond just deadline ordering

## Later
- **F011 — Async task DAGs** [ ] — Long-shot: support directed-acyclic dependencies between tasks

## Done
- **F005 — Retry config** — Per-task retry limits (done in PR #4, see [[FEX Roadmap#M2]])
- **F006 — JSON output** — Machine-readable task status output (done in PR #2)

## Legwork
- **F009 — User feedback on retry UX** — User mentioned retry errors are confusing; rework error messages
- **F008 — Doc consistency pass** — Module docs reference old API names from pre-M2
- **F010 — Test coverage for edge cases** — Add tests for empty task lists and concurrent scheduling

---



# Format Specification

## Top of doc (canonical, per F060)

Every Backlog opens with the standard top-of-doc format: YAML frontmatter + `# {slug} Backlog` H1 + dispatch-table placeholder (`| -[[{slug} Backlog]]- | |` + standard separator). See `[[skills/rewire/SKILL]]` § Default doc top-of-file.

## Format

Each entry is a definition-list item with a unique **F-number** prefix, **zero-padded to three digits** (`F001` … `F999`):

```
- **F{NNN} — Item Name** [Status] — short description.
```

`F` is for **feature**, in the broad sense of "a thing to be done" — not strictly "feature document." Every backlog item gets an F-number, whether or not it warrants a separate feature doc. If the item has a feature doc, that doc's H1 carries the same F-number; if not, the F-row stands alone in the backlog with the description inline.

The F-number lets the user refer unambiguously to a single item ("do F005", "F012 needs more detail"). Filenames sort lexicographically the same way they sort numerically because of the zero-padding (`F002 — …` < `F010 — …` < `F100 — …`).

### Numbering policy — monotonic, never recycled, zero-padded triple-digit

**Zero-padded triple-digit form**: F-numbers are written as `F001` … `F999`. The padding is structural — it makes filename sort order match numeric order without special tooling. Up to 999 F-numbers per anchor before the format would need to grow; for any active anchor, that's far in the future. Anchors that exceed 999 can extend to four digits (`F1000`) without breaking older three-digit references.

**Monotonic, never recycled**: F-numbers are **assigned in monotonically increasing order** and **never reused**. When a new item is added, it gets `F{highest-F-in-file + 1}` zero-padded. When an item reaches Done (or moves to Icebox, or is cancelled), its F-number is **not** released back into the pool. Stable forever.

**F-number namespace is shared across backlog AND icebox** (per `[[SKA workflow]]` § Active-work invariant). When numbering a new feature, take the highest F-number across both `{slug} Backlog.md` and `{slug} Icebox.md` and increment. An item moving from backlog to icebox keeps its F-number; thawing back to backlog restores the same F-number. No collisions ever.

**`M-<Name>` handles are a separate namespace for roadmap entries** (`{slug} Roadmap.md`, per [[DAS Roadmap]]). A roadmap entry is a *nested* item whose handle is `M-<Name>.<path>` — top-level entries are **named** (`M-Auth`, `M-CLI`), sub-levels numeric (`M-CLI.3.5`), and the name-path encodes the entry's position in the tree. Unique within the roadmap; doesn't collide with `F`/`T`.

**`R` handles are roadmap tasks — a backlog commitment to execute a roadmap entry.** When a roadmap entry is pulled onto the backlog as work-to-do, its backlog handle is `R` + the entry's identifier (e.g. `R-CLI.3.5`). The reference is **flat**: it names one entry — a **leaf** (the usual case, "do this item") or a **non-leaf** ("do the whole subtree"). `R` is the roadmap counterpart of `T`: both are executable tasks, `T` filed straight to the backlog, `R` sourced from the roadmap.

**Names are identity; order is document position (no stored number).** Roadmap entries and the `R` tasks that reference them resolve on the entry's **name-path** — a milestone's order is just its position in the roadmap file, and any display ordinal is *computed* from that position, never stored in a handle. So `R` references carry no number to go stale: reordering/inserting roadmap entries shifts positions automatically while every `R` reference (and any done-log citing it) keeps resolving on the name. Only **renaming** an entry forces a sweep — far rarer than reorder/insert, which is exactly why the name carries identity. Full convention + the unique-name invariant: [[DAS Roadmap]] § Names are identity (R-roadmap-12).

**T-numbers are the handle for non-feature tasks.** A `T<n>` is a backlog work-item with **no feature doc** — the row body itself is the spec, and it typically carries wiki-links to the design-doc sections / files / artifacts it operates on. The distinction from `F<n>` is the doc: **`F<n>` = a feature with a doc under `{slug} Design/{slug} Features/`; `T<n>` = a task the backlog row fully captures.** `T` is a separate prefix-namespace (disambiguated like `M<n>`), monotonic and never-recycled within the backlog; both `F` and `T` rows can carry any workflow-state bracket and both are addressed by their handle from questions / `Q.md` / cross-links. **Go-forward, not retroactive:** anchors that numbered every row `F<n>` (the legacy `B→F` fold) are grandfathered — existing rows keep their `F<n>`; new task-rows adopt `T<n>` as the `state` mint gains the category. Rationale + the four-handle model (`F` / `T` / `M` / `R`): [[Query PRD]] § Work-item identity.

This is a change from the legacy B-number policy, which used gap-fill (lowest unused integer). With F-numbers:

- A reference like "F011" means the same thing forever, across all reorganizations.
- Display order in the file may not match numeric order — items are added and resolved in arbitrary order.
- Don't renumber existing items to compact — F-numbers are stable references.

### Wiki-link conventions for feature docs

F-numbers are per-anchor namespaces; the same `F<n> — Title` filename can appear in multiple anchors over time. Obsidian wiki-links resolve by path-proximity, which makes within-anchor links unambiguous but cross-anchor links potentially incorrect — a bare `[[F<n> — Title]]` link from anchor A could silently resolve to anchor B's file if A doesn't have one with that name.

**Rule:**

- **Within-anchor wiki-links** to feature docs use the bare form: `[[F<n> — Title]]`. Path-proximity resolves correctly.
- **Cross-anchor wiki-links** to feature docs must be **path-qualified**: `[[ANCHOR Slug/.../Features/F<n> — Title]]`, or use an explicit alias like `[[F<n> — Title|SKA F<n>]]` when the link target is unambiguous in the surrounding context.
- `Q.md` and `{slug} queries.md` only ever link to `[[ANCHOR]]` and `[[{slug} queries|{slug}]]` — never directly to feature docs across anchors — so they are unaffected by this rule.

**Creation-time guard.** `/feature` step 1b (per `[[SKA feature]]` § 1b) greps the vault for an existing H1 with the same title before writing a new feature doc. If a same-title file already exists in another anchor, the agent surfaces it as a single inline question — rename, or proceed knowing both files exist and cross-anchor links to either must be qualified per the rule above. Within-anchor collisions block creation outright (titles must be unique within an anchor).

### Transition note: pre-existing B-numbers

Anchors that have historical Done items numbered with the legacy `B<n>` convention preserve those numbers as-is — they cite commit hashes and are part of the historical record. Active items at migration time get renamed `B<n>` → `F<n>` (preserving the number); new items thereafter increment past the highest existing F or B in the file. So a backlog mid-migration may show:

```
## Done
- **B1 — ...** — (historical)
- **B7 — ...** — (historical)

## Ready
- **F011 — ...** — (active, was B11 pre-migration)

## Upcoming
- **F016 — ...** — (new since migration)
```

## Status brackets

Each F-row may carry a workflow-state bracket per the `[[SKA workflow]]` discipline: `[ ]` / `[Designing]` / `[Questions]` / `[Blocked]` / `[Blocked F<NNN>]` / `[Waiting]` / `[Waiting Nd]` / `[Waiting Nh]` / `[Watching]` / `[Watching Nd]` / `[Watching Nh]` / `[Ready]` / `[Active]` / `[Verify]` / `[Done]`. The bracket is mandatory only for items in horizon sections (Now/Next/Later — per `[[SKA backlog]]`). Items in workflow-state H2s (`## Ready`, `## Active`, `## Verify`, `## Done`) have their state implied by the H2; the bracket is optional/redundant.

**The bracket reflects the state of the *remaining* work, never aggregate history.** If a row has 17 of 28 sub-bullets done and the remaining 11 all need user input, the bracket is `[Questions]` — not `[Ready]`, not `[Partial — 17/28]`. Partial-progress counts belong in the row body (or in a dedicated "N of M done" notation inside the body), never in the bracket.

**`[Partial — …]` is NOT a valid bracket form.** Only the standard brackets enumerated above are permitted. A row carrying `[Partial — N of M done]` (or any `[Partial …]` variant) is malformed and must be rewritten to one of the standard brackets per the state of the *remaining* sub-bullets. `/groom` rewrites these on encounter (per `[[SKA groom]]` § Bracket reassessment).

**Aggregate-row treatment.** When an item has heterogeneous sub-bullets (e.g., an `/audit` finding row with some mechanical-ready and some user-gated sub-bullets), the spec is **pre-split on creation**: produce ≥1 backlog row per state-cluster — one `[Ready]` row containing mechanical sub-bullets, one or more `[Questions]` rows for sub-bullets needing user input (each linking to a feature doc where the Qs are parked per `[[SKA ask]]`). Done sub-bullets are excluded entirely. See `[[SKA audit]]` § Backlog entry format for the canonical producer.

`[Blocked F<NNN>]` is the **chained** form of `[Blocked]` — used when the blocker is another feature's progression. The chained F-number is the description; the user clicks `F<NNN>` to learn the actual current state of the blocker. Generic `[Blocked]` (without an F-number) is for non-feature blockers — diagnostic capture, external review, a missing API — and the row body must describe what's blocking.

**`[Blocked]` vs `[Questions]` — the universe test** *(user ruling 2026-07-06)*: **Blocked means something in the universe must change** — an external actor's action, an artifact that doesn't exist yet, another feature landing. **If what's missing is an answer from the user, the state is `[Questions]`** — always, regardless of how the answer will be produced (a chat reply, a queries-doc entry, a discussion the user wants to have with another agent first). "The user hasn't decided yet" is the *definition* of a pending question, not an external obstacle; bracketing it `[Blocked]` hides it from the Questions count and the queries surface, which exist precisely to route user decisions.

`[Waiting]` rows must say what we're waiting on in the body. Distinct from `[Blocked]`: Blocked has a fixable obstacle (an actor's action would unblock it); Waiting does not (just letting time pass or observing for an external event we *want* to occur — bug to reoccur, log file to fill, GPU run to finish). Timed forms (`[Waiting 1d]`, `[Waiting 4h]`) must additionally include the absolute calendar date/time the wait expires in the body, since "1d" by itself ages and becomes meaningless without knowing when it was written.

`[Watching]` rows are the **polarity opposite of `[Waiting]`**: a fix has been shipped and we're soaking on it, observing for *non*-recurrence. Body must say what was changed and what non-recurrence would prove. Timed forms (`[Watching 7d]`, `[Watching 24h]`) — the common case — must include the absolute soak-expiry date in the body. At expiry with no recurrence, `/groom` suggests `[Verify]` for user confirm-and-close; on recurrence during the soak, regress to `[Active]` or `[Designing]`. No `[Watching F<NNN>]` form — Watching is about a fix you shipped, not a chained dependency.

All three states — `[Blocked]`, `[Waiting]`, `[Watching]` — are reconsidered every `/groom` pass; see `[[SKA workflow]]` § Blocked, Waiting, and Watching semantics.

## H2 sections

Entries are grouped under H2 sections of three kinds — workflow-state, horizon, and category. The full discipline lives in `[[SKA backlog]]`; the summary is:

**Workflow-state H2s** (state implied by H2; `[Status]` bracket optional/redundant):

- **Active** — Items the Pilot is actively driving forward right now (state `[Active]`).
- **Ready** — Items whose status is `[Ready]` (see § Definition of Ready below).
- **Done** — Items that graduated and were finished (with cross-references to where).

**Verify is a status, not a section.** Items in `[Verify]` state stay in their horizon H2 (`## Now` is typical, since most verify happens on imminent work) with the `[Verify]` bracket. There is no `## Verify` H2. Rationale: verify is short-lived (waiting on user yes/no) and conceptually keeps the item in its horizon — verifying it doesn't change the *when* intent. The bracket alone carries the state.

**Horizon H2s** (per `[[SKA backlog]]`; `[Status]` bracket mandatory — workflow state is carried by the bracket since the H2 only conveys *when*):

- **Now** — Imminent — the next 1–2 cycles. The "we really expect to do this shortly" zone.
- **Next** — Committed but not the next thing up. Visible and ordered, but explicitly deferred.
- **Later** — Known wants — will get to eventually. Lower priority than Next.

**Category H2** (cross-cutting; not a state and not a horizon):

- **Legwork** — Autonomous agent work that should be done proactively. Includes user feedback integration, planning actions, doc consistency fixes, and other tasks the agent can execute without user approval. The `/code execute` priority loop pulls from this section as Tier 2 legwork (after PR merging and worker dispatch).

Items typically flow `Now [ ] → Now [Ready] → ## Active → Now [Verify] → ## Done` (or `Next/Later → Now → ...` when scheduling intent shifts). Note: `[Verify]` items stay in their horizon H2 with the bracket; they don't move to a separate H2. The `roster` skill prints a per-bucket count line (one count per H2 plus a Verify count derived from brackets across horizon H2s; sum equals total). The `groom` skill walks horizon H2s looking for items with status `Unset / Designing / Questions / Blocked` and tries to promote candidates to `[Ready]` (see § Definition of Ready and § Item Status below).

**Legacy `## Upcoming`.** Anchors that pre-date the horizons discipline may still have `## Upcoming` as the catch-all pre-ready section. Treat it as a transitional alias for `## Now` until the anchor is migrated. New backlogs use `## Now / ## Next / ## Later` from the start.

**Why horizons exist.** Without them the backlog is binary — items are either "in" (visible, competing for attention) or in the Icebox (effectively invisible). Deferring an item then has no good home: the Icebox makes it disappear, `## Now` keeps it competing with imminent work. The three ordered tiers capture the gradient between *imminent* and *indefinite* without leaving the backlog.

**Now vs Active — a common confusion.** `## Now` is a *scheduling intent* ("we want to pull this in soon"); `## Active` is a *state* ("we have started"). They are not interchangeable — an item sits in `## Now` until work begins, then moves to `## Active`.

**Two axes, not one.** Horizon (*when*) and workflow state (*how far*) are independent — every combination is legal:

- `## Later` + `[Ready]` — design is clean; just no plan for when.
- `## Now` + `[Designing]` — we want this soon, but it still has open questions.
- `## Now` + `[Active]` — unusual; once active the item moves to the `## Active` H2.

**The boredom test.** Before demoting an item Now → Next or Next → Later, ask: *"Am I avoiding this because there's a real reason it should wait, or because I'm bored of it?"* If it's the latter, leave it in Now and either schedule it for real or genuinely demote it to the Icebox. A horizon move should reflect a real shift in commitment, not procrastination dressed up as planning — the agent applies this test before suggesting a horizon demotion.

For items that are explicitly parked / out-of-scope-for-now / someday-maybe, use the optional [[DAS Icebox]] file rather than a Deferred section here.

## Definition of Ready

The canonical definition lives in the **`workflow` discipline** — see `[[SKA workflow]]` § Definition of Ready. The full state graph (`[Designing]` / `[Questions]` / `[Blocked]` / `[Ready]` / `[Active]` / `[Verify]` / `[Done]`) and the bar for each transition also live there.

For convenience: **An item is Ready when you believe you know how to do this task without further involvement of the user.** This is the bar `/groom` checks for each candidate. If the task still hides any "wait, what about X?" the user would have to answer, it's not Ready — it's `[Questions]`, paired with a `→ [[Feature Doc]]` link to where the questions live.

## Item Status

Every backlog item has one of these statuses, derived from where the bullet sits and what (if anything) it links to:

| Status | How to recognize |
| --- | --- |
| **Ready** | Bullet is under `## Ready`. |
| **Active** | Bullet is under `## Active`. |
| **Questions** | Bullet text contains a `→ [[Feature Doc]]` link to a doc with pending questions; status bracket `[Questions]`. The item is parked there until the user answers. |
| **Blocked** | Bullet has bracket `[Blocked]` (generic — body describes the blocker) or `[Blocked F<NNN>]` (chained — blocker is another feature's progression; click `F<NNN>` to learn its state). Skipped by `/groom`'s promotion pass; reconsidered by `/groom`'s bracket reassessment; counts only under its horizon H2 (no Q/V/A/R contribution). |
| **Waiting** | Bullet has bracket `[Waiting]` / `[Waiting Nd]` / `[Waiting Nh]`. **Body must say what we're waiting on** — an event we *want* to occur; timed forms must also include the absolute expiration date in the body. No actor's action would unblock — distinct from Blocked. Skipped by `/groom`'s promotion pass; reconsidered by `/groom`'s bracket reassessment; counts only under its horizon H2 (no Q/V/A/R contribution). |
| **Watching** | Bullet has bracket `[Watching]` / `[Watching Nd]` / `[Watching Nh]`. **Body must say what was changed and what non-recurrence would prove** — soak on a shipped fix; timed forms must also include the absolute soak-expiry date in the body. Resolves on *non*-recurrence (opposite polarity from Waiting). Skipped by `/groom`'s promotion pass; reconsidered by `/groom`'s bracket reassessment; counts only under its horizon H2 (no Q/V/A/R contribution). |
| **Verify** | Bullet has bracket `[Verify]` (lives under its horizon H2; no dedicated `## Verify` H2). |
| **Done** | Bullet is under `## Done`. |
| **Unset / Upcoming** | Bullet is under a horizon H2 (`## Now`, `## Next`, `## Later`) — or the legacy `## Upcoming` — or `## Legwork`, with bracket `[ ]` / `[Designing]` / absent, AND has no link to active open questions. This is the "candidate for promotion" status. |

### The `→ [[X]]` link convention — for rows with feature docs

When a feature row has unresolved questions, the bullet description should be replaced with a pointer to where those questions live:

```
- **F012 — Item Name** [Questions] — → [[F012 — Item Name]]
```

The `→ [[Feature Doc]]` link is the marker. As long as the linked doc has pending questions in its `## Open Questions` block, the backlog item's status is **Questions**. When the user resolves those questions, the item can be re-readied (the description gets rewritten to reflect the resolved design, and the bullet moves to `## Ready`).

For rows without a feature doc, see § B-row inline Qs below.

### B-row inline Qs — questions go at the top of the row body

**`[Questions]` is a structural promise: clicking the row's wiki-link MUST land on numbered `Q<n>` items the user can resolve in chat.** For rows that don't have a feature doc — typically B-rows (named only in the backlog), inline tasks, audit findings — the questions live as numbered sub-bullets directly under the row, *at the top* of the body:

```
- **B-name — Short title** [Questions] — one-line context (the incident, the task, why it matters).
  - **Q1 — <short question>** — <one-line elaboration if needed>.
  - **Q2 — <short question>** — <one-line elaboration if needed>.
  - **Q3 — <short question>** — <one-line elaboration if needed>.
```

**The bracket asserts the row body contains at least one numbered `Q<n>` sub-bullet.** A B-row carrying `[Questions]` without numbered Qs is malformed. Either:

- Hoist the informal questions to numbered form (Q1, Q2, …) at the top of the row body — then the bracket is honest, or
- Rebracket to a state the row actually satisfies (`[Designing]`, `[Blocked]`, `[ ]`).

**Query link form (per `[[DAS Query]]` / `[[SKA ask]]` § Mandatory wiki-link):** `[[{slug} Backlog#B-name|B-name]]` — clicking lands at the row, where the numbered Qs are immediately visible.

**Promotion to feature doc.** If the inline Q set grows too large to fit comfortably as row sub-bullets — rule of thumb: more than 3–4 Qs, or any Q whose body needs multiple lines of elaboration — promote the row to a feature doc via `/feature`. The feature doc's `## Open Questions` H2 (first H2, below the H1) is the canonical Q surface and assigns a stable F-number from the per-anchor F-counter. After promotion, the backlog row's description becomes a `→ [[F<n> — Title]]` pointer per the convention above.

**Why this matters.** The bracket promise (`[Questions]` → click → land on numbered Qs) is what makes `queries.md` and `Q.md` navigable. A bracket without numbered Qs at the link target leaves the user unable to answer with the shorthand `B-name Q3: yes` because there's no Q3 to address — a silent-failure that has historically slipped past skill-level discipline (see [[feedback_close_round_trip_loopholes]]). Numbered Qs at a knowable location make the rule mechanically checkable.

## Design Principle — Minimize User Back-and-Forth

Workflow operations that touch the backlog — `/groom`, `/ask`, `/roster`, audits, and similar batch operations — **must process the entire batch autonomously before involving the user**. Never interrupt mid-run to ask a question; route every question that emerges to its feature doc's `## Open Questions` block, then surface the first blocked doc at the end of the run as the user's single next action.

Each round-trip with the user costs scrollback context and stalls the batch — design every workflow to require *one* round-trip per pass, not N. Inline questions are an anti-pattern in batch operations — every question, however trivial, is parked in the queries surface (per [[Query PRD]] R1; the former one-trivial-inline-question concession was retired 2026-07-05).

## The groom frontier

**The frontier is the set of tasks that could be next for execution** (defined 2026-07-05, F228; canonical statement in [[Query PRD]] § The groom frontier): rows under `## Active` / `## Ready` / `## Now` / `## Next`, plus items soon on the relevant roadmaps — the next unmet milestone of `{slug} Roadmap.md` when one exists. `## Later` and the icebox are not frontier. `/groom`'s purpose is to get every frontier task **fully ready to be executed** — planned (a declared `- **Next:**` step), promoted when the Definition of Ready holds, or honestly bracketed behind its named blocker/questions. `/ask` mines its anticipatory questions from the frontier. The `R-backlog` ruleset below encodes the resulting file-invariants.

## Location

`{slug} Backlog.md` lives in `{slug} Docs/{slug} Plan/`.

## Relationship to Other Planning Docs

- **Todo** — active, near-term tasks
- **Roadmap** — milestone-based execution plan (uses `R<n>.<m>` numbering for hierarchical milestone references; planned but deferred)
- **Backlog** — active deferred-work list: ideas under consideration, low-priority but not abandoned
- **[[DAS Icebox|Icebox]]** — optional cold-storage list for items not under active consideration

Items graduate from Backlog to Todo or Roadmap when they become priorities, or move to Icebox when they cool off.

# BRIEF

*(Maintainer note — agent-facing cautions.)*

- **The `state` script is the write path** — every convention this spec adds must stay parseable by `backlog-edit.py`'s row grammar; change the grammar and the script together.
- **Bracket vocabulary is closed** — new states get ruled on in [[SKA workflow]] first, then land here; don't invent brackets in instances.
- **Horizon H2 names are load-bearing** (audit-q scans them); renaming a section is a breaking change across every anchor.
