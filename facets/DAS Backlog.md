---
description: "Active work tracking"
---
# FCT Backlog

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

**Promotion to feature doc.** If the inline Q set grows too large to fit comfortably as row sub-bullets — rule of thumb: more than 3–4 Qs, or any Q whose body needs multiple lines of elaboration — promote the row to a feature doc via `/feature`. The feature doc's `## Open Questions` H2 below H1 is the canonical Q surface and assigns a stable F-number from the per-anchor F-counter. After promotion, the backlog row's description becomes a `→ [[F<n> — Title]]` pointer per the convention above.

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

# RULESET R-backlog
include::
where:: `file:{anchor}/**/* Backlog.md`
description:: SKA skill anchor for the backlog-horizons skill

What `/audit doc` checks on a backlog file. The skills that maintain it are `/groom` (frontier planning) and the `state` tool (mutations); these are the file-invariants the groomed state must satisfy. Format of this set: [[DAS Ruleset]].

## The groomed states — each carries a body contract that a rule checks

Grooming drives every frontier row into exactly one **groomed state**, and each state is only honest if its body carries the contract below. These are the same canonical states as [[SKA workflow]] § The canonical state graph; the table names, per state, *what the body must contain* and *which `R-backlog` / `R-query` rule mechanically checks it*. A row whose bracket claims a state its body doesn't satisfy is malformed — that is the failure the rules exist to catch.

| # | Groomed state | Bracket(s) | Body contract — what must be present | Checked by |
|---|---|---|---|---|
| 1 | **Executable** | `[Ready]` / `[Active]` | a `- **Next:**` sub-bullet stating the next step the agent takes with zero user involvement | R-backlog-02 |
| 2 | **Questions** | `[Questions]` | at least one numbered `Q<n>` reachable from the row — inline `- **Q<n>` sub-bullets, or a `→ [[Feature Doc]]` link to a `## Open Questions` block; each Q satisfies the five-part question bar (identifier + specific question + labeled `**(A)**` options + Recommendation + a live wiki-link to every named artifact) | R-backlog-05 + R-query-08 / R-query-13 / R-query-15 |
| 3 | **Blocked / Waiting** | `[Blocked]` / `[Waiting …]` / `[Watching …]` | names the *specific* obstacle or awaited/observed event (`[Blocked F<NNN>]` is exempt — the chained link is the description) | R-backlog-06 |
| 4 | **Verify** | `[Verify]` / `[Verify-by …]` | a `- **Verify:**` sub-bullet stating the concrete yes/no the user answers from where they sit | R-backlog-04 |
| 5 | **Watching** | `[Watching …]` | a `- **Verify:**` non-recurrence question (R-backlog-04) **and**, for timed forms, an absolute `YYYY-MM-DD` soak-expiry date in the body | R-backlog-04 + R-backlog-07 |

Timed `[Waiting Nd/Nh]` forms share the state-3 obstacle contract *and* the state-5 absolute-date contract (R-backlog-07). Transient `[Designing]` (still being planned) and terminal `[Done]` are not groomed exit states — a frontier row must not rest in `[Designing]` after a groom. The cross-cutting rule behind states 2–5 is **references get links**: any artifact a row's body tells the user to look at is a live `[[wiki-link]]` (enforced on the queries surface by R-query-15).

### RULE R-backlog-01 — The frontier is Now + Next + the next roadmap milestone (stated)

The **groom frontier** — the tasks that could be next for execution — is the rows under `## Active` / `## Ready` / `## Now` / `## Next`, plus the next unmet milestone of `{slug} Roadmap.md` when the anchor has one. `## Later` and the icebox are not frontier. The rules below hold over the frontier: after a groom, every frontier row is either executable (`[Ready]`/`[Active]` with a declared plan) or honestly parked (`[Questions]`/`[Blocked]`/`[Waiting]`/`[Watching]`/`[Verify]` with the obstacle named).

### RULE R-backlog-02 — Frontier `[Ready]`/`[Active]` rows declare a `Next:` step (checked)
check:: backlog_frontier_planned

Every `[Ready]` or `[Active]` row under a frontier H2 carries a `- **Next:**` sub-bullet declaring the next concrete step the agent will take with zero user involvement. A `[Ready]` row that cannot state a no-user next step is not really Ready — the bracket is lying (this is the render's `⚠ none declared` forcing-function, promoted to a rule).

**Check pattern:** for each top-level row under `## Active` / `## Ready` / `## Now` / `## Next` whose bracket is `[Ready]` or `[Active]`, the row's indented sub-bullets include one starting `- **Next:**`.

### RULE R-backlog-03 — Frontier rows are bracket-resolved (checked)
check:: backlog_frontier_bracketed

A top-level row under `## Now` / `## Next` with no status bracket (or the bare placeholder `[ ]`) is **ungroomed frontier** — the task might be next, but nobody has planned it, questioned it, or named its blocker. Groom owes it a pass. (`## Later` rows may sit unbracketed; they are not frontier.)

**Check pattern:** every top-level `- **…**` row under `## Now` / `## Next` carries a `[...]` bracket other than `[ ]`.

### RULE R-backlog-04 — `[Verify*]` / `[Watching*]` rows carry a concrete question (checked)
check:: backlog_verify_concrete

Every `[Verify]` / `[Verify-by …]` / `[Watching …]` row carries a `- **Verify:**` sub-bullet stating the concrete yes/no the user can answer from where they sit (do X, observe Y — did Y happen?). The mechanical queries render quotes it verbatim; a Verify row without one renders as an unanswerable ⚠.

**Check pattern:** for each row whose bracket starts `Verify` or `Watching`, the row's indented sub-bullets include one starting `- **Verify:**`.

### RULE R-backlog-05 — `[Questions]` rows keep the bracket promise — a numbered `Q<n>` is reachable (checked)
check:: backlog_questions_have_numbered_q

`[Questions]` is a **structural promise**: following the row lands the user on a numbered `Q<n>` they can answer in chat (`<id> Q<n>: <answer>`). The state-2 body contract is satisfied one of two ways — inline `- **Q<n>` sub-bullets at the top of the row body (B-rows / task-rows with no doc, per § B-row inline Qs), **or** a `→ [[Feature Doc]]` link delegating the Qs to that doc's `## Open Questions` (per § The `→ [[X]]` link convention). A `[Questions]` row with neither is malformed — the user clicks and lands on prose with nothing to answer (the [[feedback_close_round_trip_loopholes]] failure). Fix by hoisting the informal questions to numbered form or adding the `→ [[Doc]]` link — or rebracket to a state the row actually satisfies.

**Check pattern:** for each row whose bracket is `Questions` (or `N Questions`), either an indented sub-bullet starts `- **Q<n>` or the row/sub-bullets contain a `→ [[…]]` link.

### RULE R-backlog-06 — `[Blocked]` / `[Waiting …]` / `[Watching …]` rows name their obstacle (checked)
check:: backlog_blocker_named

The state-3 body contract, and the antidote to the lazy-Blocked / lazy-Waiting / lazy-Watching failure mode ([[SKA workflow]] § The lazy-Blocked … failure mode): a bracket claiming one of these states is a claim about *why the row is not actionable right now*, and the body must make that claim auditable in one read — the specific blocker (Blocked), the awaited event we *want* (Waiting), or the shipped change + what non-recurrence proves (Watching). A bare bracket with no explanatory body (or sub-bullet) is a thought-terminating label, not a groomed state. **`[Blocked F<NNN>]` is exempt** — the chained F-number link *is* the description.

**Check pattern:** for each row whose bracket head is `Blocked` / `Waiting` / `Watching` and is not the chained `Blocked F<NNN>` form, the row carries descriptive body text after the bracket (or at least one sub-bullet). An empty or near-empty body with no sub-bullet fails.

### RULE R-backlog-07 — Timed `[Waiting Nd/Nh]` / `[Watching Nd/Nh]` rows carry an absolute expiry date (checked)
check:: backlog_timed_has_expiry_date

The relative duration in a timed bracket (`1d`, `4h`, `7d`) **ages** — "1d" is meaningless without knowing when it was written. So the state-5 (and timed state-3) contract requires the body to give the absolute calendar date the wait/soak expires, in `YYYY-MM-DD` form. The terse `Nd`/`Nh` stays in the bracket for glanceability; the date lives in the body, and `/groom` reads it to decide when to prompt for rebracketing.

**Check pattern:** for each row whose bracket matches `(Waiting|Watching) \d+[dh]`, the row line or a sub-bullet contains a `\d{4}-\d{2}-\d{2}` date.
