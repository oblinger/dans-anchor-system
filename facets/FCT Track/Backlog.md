---
description: "Active work tracking"
---
# FCT Backlog

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`


The backlog file (`{NAME} Backlog.md`) holds ideas, low-priority tasks, and deferred work that don't belong on the active Todo or Roadmap yet. Items graduate to the Roadmap or Todo when they become priorities.

For items the user wants to remember but is **not** actively considering — distant-future / someday-maybe entries — use the optional [[FCT Icebox]] instead. Backlog is the *active* deferred-work list; Icebox is the *frozen* one.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Backlog.md` — Backlog.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# CAE Backlog

| -[[CAE Backlog]]- | |
| --- | --- |
| --- | |


## Active
- **F003 — Retry backoff polish** — Tune exponential-backoff caps after user feedback on long retries

## Ready
- **F001 — Cron syntax** — Support cron expressions for recurring task schedules

## Now
- **F002 — Task groups** [Designing] — Allow grouping related tasks that run as a batch
- **F007 — Webhook notifications** [Verify] — Webhook fires on task completion. Verify: trigger a test job and check that the configured webhook URL receives a POST with the documented JSON payload (see [[CAE PRD]] § Webhooks).

## Next
- **F004 — Priority levels** [ ] — Add high/medium/low priority beyond just deadline ordering

## Later
- **F011 — Async task DAGs** [ ] — Long-shot: support directed-acyclic dependencies between tasks

## Done
- **F005 — Retry config** — Per-task retry limits (done in PR #4, see [[CAE Roadmap#M2]])
- **F006 — JSON output** — Machine-readable task status output (done in PR #2)

## Legwork
- **F009 — User feedback on retry UX** — User mentioned retry errors are confusing; rework error messages
- **F008 — Doc consistency pass** — Module docs reference old API names from pre-M2
- **F010 — Test coverage for edge cases** — Add tests for empty task lists and concurrent scheduling

---



# Format Specification

## Top of doc (canonical, per F060)

Every Backlog opens with the standard top-of-doc format: YAML frontmatter + `# {NAME} Backlog` H1 + dispatch-table placeholder (`| -[[{NAME} Backlog]]- | |` + standard separator). See `[[skills/rewire/SKILL]]` § Default doc top-of-file.

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

**F-number namespace is shared across backlog AND icebox** (per `[[SKA workflow]]` § Active-work invariant). When numbering a new feature, take the highest F-number across both `{NAME} Backlog.md` and `{NAME} Icebox.md` and increment. An item moving from backlog to icebox keeps its F-number; thawing back to backlog restores the same F-number. No collisions ever.

**M-numbers are a separate namespace for roadmap milestones** (`{NAME} Roadmap.md`). M-numbers are hierarchical (M1, M1.2, M1.2.3) and are unique only within the roadmap; they don't collide with F-numbers.

This is a change from the legacy B-number policy, which used gap-fill (lowest unused integer). With F-numbers:

- A reference like "F011" means the same thing forever, across all reorganizations.
- Display order in the file may not match numeric order — items are added and resolved in arbitrary order.
- Don't renumber existing items to compact — F-numbers are stable references.

### Wiki-link conventions for feature docs

F-numbers are per-anchor namespaces; the same `F<n> — Title` filename can appear in multiple anchors over time. Obsidian wiki-links resolve by path-proximity, which makes within-anchor links unambiguous but cross-anchor links potentially incorrect — a bare `[[F<n> — Title]]` link from anchor A could silently resolve to anchor B's file if A doesn't have one with that name.

**Rule:**

- **Within-anchor wiki-links** to feature docs use the bare form: `[[F<n> — Title]]`. Path-proximity resolves correctly.
- **Cross-anchor wiki-links** to feature docs must be **path-qualified**: `[[ANCHOR Slug/.../Features/F<n> — Title]]`, or use an explicit alias like `[[F<n> — Title|SKA F<n>]]` when the link target is unambiguous in the surrounding context.
- `Q.md` and `{NAME} Triage.md` only ever link to `[[ANCHOR]]` and `[[Q#ANCHOR Triage|ANCHOR Triage]]` — never directly to feature docs across anchors — so they are unaffected by this rule.

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

**Aggregate-row treatment.** When an item has heterogeneous sub-bullets (e.g., an `/audit` finding row with some mechanical-ready and some user-gated sub-bullets), the spec is **pre-split on creation**: produce ≥1 backlog row per state-cluster — one `[Ready]` row containing mechanical sub-bullets, one or more `[Questions]` rows for sub-bullets needing user input (each linking to a feature doc where the Qs are parked per `[[SKA query]]`). Done sub-bullets are excluded entirely. See `[[SKA audit]]` § Backlog entry format for the canonical producer.

`[Blocked F<NNN>]` is the **chained** form of `[Blocked]` — used when the blocker is another feature's progression. The chained F-number is the description; the user clicks `F<NNN>` to learn the actual current state of the blocker. Generic `[Blocked]` (without an F-number) is for non-feature blockers — diagnostic capture, external review, missing API, cross-agent decision — and the row body must describe what's blocking.

`[Waiting]` rows must say what we're waiting on in the body. Distinct from `[Blocked]`: Blocked has a fixable obstacle (an actor's action would unblock it); Waiting does not (just letting time pass or observing for an external event we *want* to occur — bug to reoccur, log file to fill, GPU run to finish). Timed forms (`[Waiting 1d]`, `[Waiting 4h]`) must additionally include the absolute calendar date/time the wait expires in the body, since "1d" by itself ages and becomes meaningless without knowing when it was written.

`[Watching]` rows are the **polarity opposite of `[Waiting]`**: a fix has been shipped and we're soaking on it, observing for *non*-recurrence. Body must say what was changed and what non-recurrence would prove. Timed forms (`[Watching 7d]`, `[Watching 24h]`) — the common case — must include the absolute soak-expiry date in the body. At expiry with no recurrence, triage suggests `[Verify]` for user confirm-and-close; on recurrence during the soak, regress to `[Active]` or `[Designing]`. No `[Watching F<NNN>]` form — Watching is about a fix you shipped, not a chained dependency.

All three states — `[Blocked]`, `[Waiting]`, `[Watching]` — are reconsidered every `/triage` pass; see `[[SKA workflow]]` § Blocked, Waiting, and Watching semantics.

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

For items that are explicitly parked / out-of-scope-for-now / someday-maybe, use the optional [[FCT Icebox]] file rather than a Deferred section here.

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
| **Blocked** | Bullet has bracket `[Blocked]` (generic — body describes the blocker) or `[Blocked F<NNN>]` (chained — blocker is another feature's progression; click `F<NNN>` to learn its state). Skipped by `/groom`; reconsidered by `/triage`; counts only under its horizon H2 (no Q/V/A/R contribution). |
| **Waiting** | Bullet has bracket `[Waiting]` / `[Waiting Nd]` / `[Waiting Nh]`. **Body must say what we're waiting on** — an event we *want* to occur; timed forms must also include the absolute expiration date in the body. No actor's action would unblock — distinct from Blocked. Skipped by `/groom`; reconsidered by `/triage`; counts only under its horizon H2 (no Q/V/A/R contribution). |
| **Watching** | Bullet has bracket `[Watching]` / `[Watching Nd]` / `[Watching Nh]`. **Body must say what was changed and what non-recurrence would prove** — soak on a shipped fix; timed forms must also include the absolute soak-expiry date in the body. Resolves on *non*-recurrence (opposite polarity from Waiting). Skipped by `/groom`; reconsidered by `/triage`; counts only under its horizon H2 (no Q/V/A/R contribution). |
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

**Triage link form (per `[[FCT Triage]]` / `[[SKA triage]]` § Mandatory wiki-link):** `[[{NAME} Backlog#B-name|B-name]]` — clicking lands at the row, where the numbered Qs are immediately visible.

**Promotion to feature doc.** If the inline Q set grows too large to fit comfortably as row sub-bullets — rule of thumb: more than 3–4 Qs, or any Q whose body needs multiple lines of elaboration — promote the row to a feature doc via `/feature`. The feature doc's `## Open Questions` H2 below H1 is the canonical Q surface and assigns a stable F-number from the per-anchor F-counter. After promotion, the backlog row's description becomes a `→ [[F<n> — Title]]` pointer per the convention above.

**Why this matters.** The bracket promise (`[Questions]` → click → land on numbered Qs) is what makes `/triage` and `Q.md` navigable. A bracket without numbered Qs at the link target leaves the user unable to answer with the shorthand `B-name Q3: yes` because there's no Q3 to address — a silent-failure that has historically slipped past skill-level discipline (see [[feedback_close_round_trip_loopholes]]). Numbered Qs at a knowable location make the rule mechanically checkable.

## Design Principle — Minimize User Back-and-Forth

Workflow operations that touch the backlog — `/groom`, `/triage`, `/roster`, audits, and similar batch operations — **must process the entire batch autonomously before involving the user**. Never interrupt mid-run to ask a question; route every question that emerges to its feature doc's `## Open Questions` block, then surface the first blocked doc at the end of the run as the user's single next action.

Each round-trip with the user costs scrollback context and stalls the batch — design every workflow to require *one* round-trip per pass, not N. Inline questions are an anti-pattern in batch operations.

(One concession: a single, genuinely trivial question may be deferred to the very end of a `/groom` run and asked after the roster prints, where it stays pinned to the bottom of the screen. Never more than one such inline question per run.)

## Location

`{NAME} Backlog.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Relationship to Other Planning Docs

- **Todo** — active, near-term tasks
- **Roadmap** — milestone-based execution plan (uses `R<n>.<m>` numbering for hierarchical milestone references; planned but deferred)
- **Backlog** — active deferred-work list: ideas under consideration, low-priority but not abandoned
- **[[FCT Icebox|Icebox]]** — optional cold-storage list for items not under active consideration

Items graduate from Backlog to Todo or Roadmap when they become priorities, or move to Icebox when they cool off.
