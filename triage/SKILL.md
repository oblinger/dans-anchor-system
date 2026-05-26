---
name: triage
description: >
  Surface the **status of the anchor** into the anchor's per-anchor section of
  the global `~/ob/kmr/Q.md` dashboard (per F075, 2026-05-19 — per-anchor Triage
  files retired; Q.md is the single triage surface). Body has up to 5 H2s
  (Active / Ready / Now / Next / Later — Later only surfaces items carrying
  `[Questions]` or `[Verify]` brackets per 2026-05-20; Icebox never rendered).
  Source order from the backlog, one bullet per qualifying item. Status
  brackets carry counts (`**[3 Questions]**`, `**[Verify]**`).
  H1 banner has an anchor TAG (`[U]` / `[A]` / `[U+A]` / `[G]` / `[-]` / `[]`)
  and pipe-grouped totals. À la carte questions live in the sibling
  `{NAME} Questions.md` facet — Triage carries one bullet line linking to it
  directly under the H1. The user can answer with shorthand like "F005 Q4: yes"
  (resolves a question) or "verified F23" (moves the item to `## Done` and
  updates the feature-doc Status). Use when the user types `/triage` or
  sends `"` (a single double-quote) as the entire message. Slash-only — the
  spoken word "triage" is NOT a DMUX prefix-trigger.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Triage — Status of the Anchor

Regenerate the anchor's per-anchor section in `~/ob/kmr/Q.md` (the **single triage surface** per F075, 2026-05-19 — per-anchor `{NAME} Triage.md` files retired). The section is the **status of the anchor**: it walks the backlog and writes one bullet per item under workflow-state H2s (`## Active`, `## Ready`, `## Now`, `## Next`). Items in `## Later` are normally hidden, **except** Later items that carry `[Questions]` or `[Verify]` brackets — those are user-actionable and get surfaced under a `## Later` H2 in the body so the banner's Q/V counts always match a visible row (2026-05-20). Items in `## Icebox` are never shown in the body. The user reads Q.md to see "where everything stands and what's waiting on me."

Punctuation trigger: **`"`** (a single double-quote as the entire message), parallel to `crank`/`'` and `/land`/`.`. Slash invocation: `/triage`, `/triage roadmap`, `/triage milestone {N}`. **Slash-only — the spoken word "triage" is NOT a DMUX prefix-trigger** (removed 2026-05-04; too easy to fire by accident in normal speech, same reasoning as /crank and /ask; `"` is the dedicated single-keystroke shortcut).


**Question / Verify format**: this skill renders items written per the [[ask-format]] discipline. `/triage` does not enforce format compliance — that's `/audit q`, auto-wired as a post-condition per F076 Q6.

## When to Use

- User types `/triage`, says `triage` (DMUX auto-prefixes), or sends `"` as the entire message.
- User says "triage and groom" or "groom and then triage" (Pilot interprets as run `/groom` first, then `/triage`).
- User asks "what's waiting on me" / "what do you need from me" / "show the inbox" / "status of the anchor".
- After `/groom` parks one or more items in feature docs (some flows naturally chain `/groom` → `/triage`).


## Sources & invocation

| Invocation | Scope |
| --- | --- |
| `/triage` (or `triage` spoken, or `"` alone) | Default — walk `{NAME} Backlog.md`. |
| `/triage roadmap` | Walk the next milestone of `{NAME} Roadmap.md` (each milestone has its own backlog-shaped block). |
| `/triage milestone {N}` | Walk a named roadmap milestone. |
| `/triage icebox` | Walk `{NAME} Icebox.md` instead. Default scope (bare `/triage`) excludes the icebox per `[[SKA workflow]]` § Active-work invariant; explicit invocation surfaces iced items needing input. |

Argument shape parallels `/groom`. Items in the icebox are not surfaced by default — Icebox items are explicitly parked, and the invariant says they don't compete for attention.


## Output format — anchor's section inside `~/ob/kmr/Q.md`

Authoritative spec: `[[CAB Triage]]` (presentation form, unmoored from any per-anchor file per F075). Summary:

```markdown
---
description: triage inbox (agent-owned)
---

# [<TAG>]  [[{NAME} ask|{NAME}]]  -  Ready N    Questions N   |   Now N    Next N    Later N    Icebox N
- **[N Questions]**  [[{NAME} Questions]]
## Active
- **[Active]** [[F<n> Title]] — description.
## Ready
- **[Ready]** [[F<n> Title]] — description.
- **[N Ready]** [[F<n> Title]] — description (milestone with N sub-items).
## Now
- **[N Questions]** [[F<n> Title]] — description.
- **[Verify]** [[F<n> Title]] — one-line verify-plan text. ([[F<n> Title#Verify|details]])
- **[Ready]** [[F<n> Title]] — description.
## Next
- **[N Questions]** [[F<n> Title]] — description.
- **[N Ready]** [[F<n> Title]] — description.
## Later
- **[N Questions]** [[F<n> Title]] — description.   ← Later items only appear when [Questions] or [Verify]
- **[Verify]** [[F<n> Title]] — verify-plan text.
```

**No blank lines anywhere in the body.** Every line carries information.

**No meta prose.** No "this page is maintained by the agent..." text. The user knows what the page is.

**No `## À la carte` H2.** Replaced by the single bullet line directly under the H1 linking to `[[{NAME} Questions]]` (only present when à la carte has pending Qs).

**Sections with no qualifying items are omitted** entirely (not even an empty H2). If the anchor has no items at all in Active/Ready/Now/Next, the body is just the H1 banner — nothing else.

**Items in `## Later`: selectively shown in the body** (2026-05-20). Later items with `[Questions]` or `[Verify]` brackets are surfaced under a `## Later` H2 in the body — they're user-actionable, and surfacing them guarantees the H1 banner's `Questions N` / `Verify N` counts match a visible row. All other Later items (`[ ]` / `[Designing]` / `[Blocked]` / `[Waiting]` / `[Watching]` / `[Ready]` / etc.) stay hidden — they're deferred and don't compete for attention. **Items in `## Icebox` are never shown in the body** — only counted in the H1 banner.

**Special case — `[Verify-by YYYY-MM-DD]`** (per [[ask-format]] § Deferred-by-use Verify): surface in Later H2 only while `today < YYYY-MM-DD`. Past the date, hide — the item is awaiting auto-expiration by the next `/groom` sweep, which moves it to `## Done`. This keeps banner counts honest: the `Verify N` count excludes expired-but-not-yet-groomed items, so the user never sees a phantom Verify in the body waiting on nothing.

**Within an H2**: items appear in **source order from the backlog**. The H1 banner already counts items by status, so re-grouping by status inside H2s is redundant. Reorder by editing the backlog (or asking the agent).


## Anchor TAG — cascading rule

Decide the H1 TAG by checking in order; first match wins, except U and A combine:

1. **U** if anchor has any `[Questions]` or `[Verify]` items (user-actionable).
2. **A** if anchor has any `[Active]` or `[Ready]` items (agent-actionable).
3. If both U and A: combine as `U+A` (literal `+`).
4. **G** if (no U AND no A) AND anchor has any items in `## Now` or `## Next` (groomable).
5. **-** if (no U, A, G) AND anchor has items in `## Later`.
6. **`[]`** (empty brackets) if nothing anywhere.

Tag values: `[U]`, `[A]`, `[U+A]`, `[G]`, `[-]`, `[]`.


## Status brackets — count and form

| Form | When |
|---|---|
| `**[Questions]**` | Single pending numbered Q at the link target (count omitted; rare). |
| `**[N Questions]**` | N pending numbered Qs at the link target (N > 1). |

**Bracket promise.** `[Questions]` / `[N Questions]` is a **structural claim**: following the row's wiki-link MUST land on N numbered `Q<n>` items the user can resolve in chat with the shorthand `<id> Q<n>: <answer>` (per § Question-resolution path). This is not an agent-trigger label ("there are open issues here") — it is a user-facing promise about what they will find when they click.

Link target by row class:

- **Feature row** → feature doc's `## Open Questions` H2 below H1; Qs are top-level bullets `**Q1 — …**`, `**Q2 — …**` (per `[[SKA ask]]`).
- **B-row (no feature doc)** → backlog row itself; Qs are sub-bullets `**Q1 — …**`, `**Q2 — …**` at the top of the row body (per `[[CAB Backlog]]` § B-row inline Qs).
- **À la carte (anchor-level)** → `{NAME} Questions.md` § Open Questions; same Q format as feature docs (per `[[CAB Questions]]`).

**The bracket is forbidden when the link target has zero numbered Qs.** Before emitting `[Questions]`, verify the target contains at least one `Q<n>`. If zero: either hoist the informal Qs to numbered form (the right fix), or rebracket to a state the row actually satisfies (`[Designing]` / `[Blocked]` / etc.). This is the rule that — without it — produces the failure mode where the user clicks `[Questions]` and lands on prose with no answerable Qs (cf. [[feedback_close_round_trip_loopholes]]).

| `**[Verify]**` | Single verification needed. Verify text inlines as the description (and may extend to a sub-bullet). |
| `**[N Verify]**` | N independent verification items (rare). When N is large, verify items live in the feature doc's `## Open Questions` § Verify subsection (parallel to Questions). |
| `**[Ready]**` | Single feature the agent could pick up **in this turn** and execute to Done/Verify with **zero further user interaction**. See [[SKA workflow]] § Definition of Ready → The RIGHT NOW test for the full rule. Hedging language ("likely", "fallback", "in case", "awaits", "revisit if") disqualifies — rebracket to `[Waiting]`, `[Blocked]`, or `[Questions]` before rendering. |
| `**[N Ready]**` | Milestone-style F with N independent sub-items in its roadmap, all ready (same RIGHT NOW bar per sub-item). |
| `**[Active]**` | In flight (a worker is currently minting). |
| `**[Blocked]**` | Generic blocker — body must describe what's blocking. Doesn't contribute to Q/V/A/R banner counts. |
| `**[Blocked F<NNN>]**` | Chained on another feature. Click `F<NNN>` to learn its current state. Doesn't contribute to Q/V/A/R banner counts. |
| `**[Waiting]**` | **Body must say what we're waiting on.** Indefinite soft watch — observing for an event we *want* to occur. Doesn't contribute to Q/V/A/R banner counts. |
| `**[Waiting Nd]**` / `**[Waiting Nh]**` | **Body must say what we're waiting on, plus the absolute calendar date/time the wait expires.** Time-bound; relative durations age, so the date in the body is what makes the row auditable. Doesn't contribute to Q/V/A/R banner counts. |
| `**[Watching]**` | **Body must say what was changed and what non-recurrence would prove.** Soak on a fix — observing for an event we *don't* want to occur. Opposite polarity from Waiting (resolution = event doesn't happen). Bare form rare; prefer timed forms below. Doesn't contribute to Q/V/A/R banner counts. |
| `**[Watching Nd]**` / `**[Watching Nh]**` | **Body must say what was changed, what non-recurrence proves, plus the absolute calendar date/time the soak expires.** Most common Watching form. At expiry with no recurrence, triage suggests `[Verify]` for user confirm-and-close. Doesn't contribute to Q/V/A/R banner counts. |

The bracket is **bold**; the wiki-link to the feature doc is **not** bold; description follows after ` — ` and ends with a period.

**Blocked, Waiting, and Watching items don't contribute to TAG**. The cascade (U → A → U+A → G → ? → []) ignores all three — those rows are neither user-actionable nor agent-actionable right now. An anchor whose only items are Blocked / Waiting / Watching falls through to `[G]` (groomable — needs unblocking, wait-condition observation, or soak-expiry-without-recurrence) or `[]`. This is honest: a `[A]` TAG should mean "the agent has work it can pick up immediately"; if every Ready row is actually `[Blocked F<n>]`, `[Waiting]`, or `[Watching]`, the TAG must reflect that.

**Reconsider Blocked, Waiting, and Watching on every triage pass.** All three states are claims that the row is neither agent-actionable nor needing user input *right now*. That claim ages — blockers resolve, watched events occur, soak periods expire — and the claim must be re-checked. For each `[Blocked]`, `[Waiting]`, or `[Watching]` row encountered:

1. Read the body's stated blocker / wait condition / soaked change.
2. Decide: still true? If yes, leave as-is. If no, rebracket per the polarity of the state:
   - **`[Blocked]` → blocker resolved** — rebracket to `[Ready]` (or whatever state the row was in pre-block).
   - **`[Waiting]` → event occurred** — rebracket to `[Verify]` (the awaited event now needs checking) or `[Active]` (work can resume on the new evidence).
   - **`[Watching]` → soak expired with no recurrence** — rebracket to `[Verify]` so the user can confirm the fix held and close to `[Done]`.
   - **`[Watching]` → recurrence happened during the soak** — rebracket to `[Active]` or `[Designing]` (the fix didn't hold; resume work on the bug).
3. Watch for lazy states — rows whose body doesn't actually name what makes the state honest:
   - **Lazy-Blocked** — no specific actor-and-action named. Usually `[Ready]` or `[Questions]` in disguise.
   - **Lazy-Waiting** — no specific event-and-source named. Usually `[Ready]` in disguise.
   - **Lazy-Watching** — no specific shipped-change-and-non-recurrence-proof named. Usually `[Waiting]` (we want the event, not avoiding it) or `[Active]` (no fix has shipped yet) in disguise.
4. Watch for the **Waiting/Watching polarity flip** — a row marked `[Waiting]` whose body actually describes a shipped fix and what non-recurrence would prove is misbracketed and should be `[Watching]`. And vice versa. The triage prompt is different ("any recurrence since X?" vs "has the event happened yet?"); the wrong bracket asks the wrong question.

This re-evaluation is *the* primary value of these states; without it, Blocked / Waiting / Watching becomes a write-only graveyard.

**Reconsider `[Ready]` on every triage pass — Ready means RIGHT NOW.** `[Ready]` is a promise that the agent could execute the row **in this turn** with **zero further user interaction**. Triage enforces that promise. For each `[Ready]` row encountered:
1. Read the description text. Scan for hedging phrases: *"likely superseded"*, *"held as fallback"*, *"in case X"*, *"if X surprises us"*, *"awaits natural recurrence"*, *"revisit only if"*, *"soaking"*, *"burn-in"*, *"watching for recurrence"*, *"fix shipped, observing"*, *"may need"*, *"might want to"*, *"probably"*, *"possibly"*, *"contingent on"*, *"depends on whether"* (and close paraphrases — the list names a *failure mode*, not a closed dictionary).
2. If any hedging phrase appears, the row is **by definition not Ready**. Rebracket per [[SKA workflow]] § Definition of Ready → Disqualifying language:
   - "Likely superseded by F<NNN>" / "held as fallback in case F<NNN>" / "revisit only if F<NNN> fails" → **`[Blocked F<NNN>]`** (the row sleeps until F<NNN>'s outcome is known).
   - "Awaits natural recurrence" / "wait for the bug to come back" → **`[Waiting]`** (body must name what we're observing; if time-bound, use `[Waiting Nd]` with absolute expiry date).
   - "Soaking" / "burn-in" / "fix shipped, watching for recurrence" → **`[Watching Nd]`** (body must name what was changed, what non-recurrence proves, and the absolute soak-expiry date).
   - "May need to do X" / "might want to" / "probably" / "depends on whether" → **`[Questions]`** with a `→ [[Doc]]` link (the uncertainty is a question the agent can't resolve alone).
3. **Rebracket in BOTH places**: the backlog row AND the rendered triage line. Don't quietly inherit a wrong bracket from the backlog — fix it at the source, then render honestly.
4. After rebracket, recompute the H1 banner counts and the anchor TAG. A `[Ready]` row that became `[Blocked F<NNN>]`, `[Waiting]`, or `[Watching]` no longer contributes to the `Ready` count or the `A` TAG.

The user reads `[Ready]` and trusts it. If a row's description includes "we'll see if F23 fixes it; if not we'll do this one" — that row is `[Blocked F23]`, not `[Ready]`. If it says "fix shipped; let's watch for a week" — that's `[Watching 7d]`, not `[Ready]`. The whole point of having `[Blocked]`, `[Waiting]`, and `[Watching]` brackets is that they're more honest than a vague `[Ready]` — use them.


## H1 banner spacing — exact

```
# [<TAG>]  [[{NAME} ask|{NAME}]]  -  Ready N    Questions N   |   Now N    Next N    Later N    Icebox N
```

- Two spaces between `[<TAG>]` and `[[{NAME}]]`.
- One space between `[[{NAME}]]` and `Triage`.
- **Three spaces around the `-`** separating "Triage" from the count groups.
- **Four spaces between counts within a group**.
- **Three-space-pipe-three-space** (`   |   `) between the three count groups.

Three count groups: user-actionable (`Questions`, `Verify`) | agent-actionable (`Active`, `Ready`) | horizon (`Now`, `Next`, `Later`, `Icebox`).


## À la carte — lives in `{NAME} Questions.md`

À la carte (anchor-level, cross-cutting, agent-raised) questions live in a **separate facet file**: `{NAME} Docs/{NAME} Plan/{NAME} Questions.md`. Spec: `[[CAB Questions]]`. Same `## Open Questions` block format as feature docs (per `[[SKA ask]]`); same Phase 1 / 2 / 3 lifecycle.

In the Triage file, à la carte presence is just **one line directly under the H1**:

```
- **[N Questions]**  [[{NAME} Questions]]
```

Two spaces between the bracket and the wiki-link. Bracket form: `**[Questions]**` for N=1, `**[N Questions]**` for N>1. Omitted when there are zero pending à la carte Qs.


## Runbook

### 1. Locate the source

- Walk up from `cwd` to find `.anchor`. If none, say "No anchor found from `{cwd}` upward." and stop.
- Read `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`. If absent, say so and stop.
- Note `{NAME} Icebox.md` for the Icebox count (zero if absent).
- Note `{NAME} Questions.md` for the à la carte Q count (zero if absent).
- Resolve the target file: `~/ob/kmr/Q.md` (the global Agent Status dashboard; create if absent). The anchor's per-anchor section within Q.md is identified by its H1-equivalent line `# [<TAG>]  [[{NAME} ask|{NAME}]]  -  ...` (per B14 — link target moved from in-page heading anchor to the `{NAME} ask.md` file where the user actually answers questions; display text dropped "Triage" since the page IS triage).

### 2. Compute the H1 banner counts

**Single counting model — all workflow-state banner counts read from item brackets, not H2 placement.** H2 sections are organizational/horizon containers; brackets are the source of truth for state. This unification (per F061) closes the prior mixed model where Active/Ready counted by H2 membership while Verify counted by bracket — an inconsistency that silently miscounted items under `## Ready` H2 carrying `[Questions]` brackets as Ready.

Walk every bullet in the backlog. Compute the H1 banner with **two merged groups** (per 2026-05-24 banner simplification):

- **Ready** = bullets with `[Active]` bracket + bullets with `[Ready]` (or `[Agreed]` synonym) bracket — summed. Both states are "agent-actionable"; the banner doesn't differentiate. The body H2s (`## Active`, `## Ready`) still render separately for clarity.
- **Questions** = bullets with `[Verify]` bracket + sum of pending `Q<n>` across feature docs whose backlog rows have `[Questions]` bracket + pending `Q<n>` in `{NAME} Questions.md` — summed. Both states are "user-actionable"; the banner doesn't differentiate. The body H2s still surface `[Verify]` and `[N Questions]` brackets separately for clarity.
- **Now / Next / Later** — bullet count under each horizon H2 (these are horizon labels, not workflow states — H2-membership is correct here).
- **Icebox** — bullet count in `{NAME} Icebox.md` (zero if absent).

(Internally, the agent still computes Active / Ready / Verify / Questions separately — needed for the TAG cascading rule and for body H2 rendering — but only the merged numbers appear in the H1 banner.)

In all cases, **exclude any bullet with a `[Done]` or `[Done YYYY-MM-DD]` bracket** (those are stale rows that belong in `## Done`; not part of triage's surface). `## Done` and `## Legwork` are excluded from all counts.

**A bullet under `## Ready` H2 with a `[Questions]` bracket counts as Questions, not Ready.** That is the structural fix from F061 — bracket is authoritative, H2 placement is organizational. (`/groom` is responsible for rewriting any stale/non-standard brackets to the standard set — see `[[SKA groom]]` § Bracket reassessment.)

### 3. Compute the anchor TAG

Apply the cascading rule above to pick `[U]` / `[A]` / `[U+A]` / `[G]` / `[-]` / `[]`.

### 4. Compute the à la carte bullet

Read `{NAME} Questions.md`. If it has pending `Q<n>` in `## Open Questions`, render the count and emit:

```
- **[N Questions]**  [[{NAME} Questions]]
```

(Two spaces between the bracket and the wiki-link.) Omit the line entirely when N=0.

(Legacy `## À la carte` H2s inside any surviving `{NAME} Triage.md` are no longer relevant — those files are retired per F075. Any pre-F25 anchor with `A<n>` Q-numbering in `{NAME} Questions.md` should be flipped to `Q<n>` per F025 Q5.)

### 5. Render body H2s

For each backlog H2 in this fixed order — `## Active`, `## Ready`, `## Now`, `## Next`, `## Later` — render the H2 line and one bullet per qualifying item, **in source order from the backlog**. Skip the H2 entirely when no items qualify.

- For `## Active`, `## Ready`, `## Now`, `## Next` — all items qualify (subject to the standard `[Done]`-skip rule below).
- For `## Later` — **only items carrying `[Questions]` or `[Verify]` brackets qualify** (per 2026-05-20 selective-surfacing rule). All other Later items stay hidden.

**Do not render `## Icebox`** under any condition.

**Never render `[Done]` items.** Any row with a `[Done]` or `[Done YYYY-MM-DD]` bracket is skipped — those are completed items that belong in `## Done` (a `/groom` will move them; in the meantime, triage just hides them). The presence of `[Done]` rows in horizon H2s should be reported in the chat-summary line at the end so the user knows cleanup is pending, but they never appear in the body. Same for `[Done]` rows mis-placed in `## Active` or `## Ready`.

For each item:

- Resolve the bracket using the existing item state in the backlog row, then map to one of the bracket forms above.
- For `[Questions]` items: count pending `Q<n>` in the linked feature doc's `## Open Questions` block. If N=1 use `**[Questions]**`; otherwise `**[N Questions]**`.
- For `[Verify]` items: use `**[Verify]**` (single) and copy the backlog row's one-line verify-plan description as the body. The wiki-link `[[F<n> Title]]` already links to the whole feature doc; if the feature doc has a detailed `## Verify` section, **append `([[F<n> Title#Verify|details]])`** at the end of the line so the user can click through to the verification details directly. **Do not** use indented sub-bullets for extended verify text — link to the section instead. The one-line summary is usually enough; the link is there when more is needed.
- For `[Ready]` / `[Active]`: copy the backlog row's description (trim to one line ending in a period).
- Milestone-style multi-Ready items get `**[N Ready]**` with N = number of independent ready sub-items in the linked roadmap/feature doc.

Bullet template (three link forms by row class — see § Mandatory wiki-link below):

```
- **[<status>]** [[F<n> — Title]] — description.              ← feature row
- **[<status>]** [[{NAME} Backlog#B<n>|B<n>]] — description.  ← backlog-only B-row
- **[<status>]** [[YYYY-MM-DD Title]] — description.          ← bug/ad-hoc with its own doc
```

**Mandatory wiki-link on every row.** Every triage row's title MUST be a wiki-link — there is no row class for which inline-description-without-link is acceptable. **The row IS the link, not just a description**: the user navigates *through* triage to the source; a row without a link is a broken row, because the description text alone gives no path to the actual content. (No-link rows force the user to grep the backlog or feature folder to find what the row is talking about — which defeats the point of triage.)

Three link forms by row class — pick the most specific that exists:

- **Feature rows (`F<n>`)** → `[[F<n> — Title]]` to the feature doc. **No exceptions** — not for features that don't have a feature doc yet (the link will be broken; that's a useful signal, not a reason to omit), not for short references (`F063`), not for "obviously local" features. Rendering a bare `F<n>` is a spec violation.
- **Backlog rows (`B<n>`, ad-hoc tasks named only in the backlog)** → `[[{NAME} Backlog#B<n>|B<n>]]` (pipe alias to keep the visible token short). The backlog row is the canonical source — every B-identifier has a stable anchor inside `{NAME} Backlog.md`, so this link form ALWAYS resolves. **There is no "the backlog row doesn't link to anything" escape hatch** — the backlog row IS the something to link to.
- **Bug rows with their own doc** → link to the bug doc (`[[YYYY-MM-DD Title]]` or whatever the canonical home is). Falls back to `[[{NAME} Backlog#<id>|<id>]]` when no separate doc exists.

If you find yourself writing a row whose title is bold-only (no `[[...]]`), stop — that's the failure mode this rule names. Pick a link form above.

### 6. Regenerate the anchor's section in `~/ob/kmr/Q.md` (the only write target)

`Q.md` is the **vault-level Agent Status dashboard** AND the single triage surface (per F075, 2026-05-19). Per-anchor `{NAME} Triage.md` files do not exist — Q.md sections are the only rendered form. Update the touched anchor's section in Q.md and bubble it to the top. Per F028 Q3 (full body always):

The per-anchor section format — H1-equivalent line `# [<TAG>]  [[{NAME} ask|{NAME}]]  -  …` where the slug `{NAME}` is a wiki-link to the anchor's `{NAME} ask.md` drain page (per B14 — clicking takes the user to where they actually answer questions). Followed by body H2s with bullets in source order from the backlog.

```markdown
# [<TAG>]  [[{NAME} ask|{NAME}]]  -  Ready N    Questions N   |   Now N    Next N    Later N    Icebox N
- **[N Questions]** [[{NAME} Questions]]
## Active
- ...
## Ready
- ...
## Now
- ...
## Next
- ...
```

(Inside Q.md per-anchor sections, the H2s render at H2 level — same as the Triage file, since each anchor section is at H1 level.)

**Overflow rule.** If Q.md as a whole would exceed a soft cap (~2 screenfuls; tune in implementation), individual anchor sections collapse to *just the H1-equivalent line* (which contains the link). The user clicks through to the full body. **No partial paste** — either the whole body, or just the link.

**Q.md H1 banner**: `# Agent Status   -   Questions: N    Ready: M` where N = anchors with TAG U or U+A, M = anchors with TAG A or U+A. (Same counts as F25; format unchanged.)

**De-dupe + move-to-front**: remove any existing per-anchor section for `{NAME}`, insert the new one at the top of the body (immediately after the H1 banner). Always move-to-front, regardless of whether content changed.
**Then invoke `/audit q` to verify (per F076 Q6 auto-wiring).** The audit's fix-by-default behavior catches any drift introduced by this skill's edits — broken links, stale brackets, banner mismatches, stale `[Done]` rows — and either repairs them mechanically OR (rare) files a `QFix [Ready]` backlog entry the user can address later. Surfacing any QFix entry is part of this skill's "done" criteria.

**If the anchor has TAG `[]`** (zero items anywhere): remove its per-anchor section from Q.md entirely. Done.

### 7. Glance Q.md — NEVER glance the per-anchor Triage file

Always glance the global Agent Status dashboard after the regen completes:

```bash
open ~/ob/kmr/Q.md
```

The just-updated per-anchor section sits at the top of Q.md (per § 7's move-to-front rule), so the user sees this anchor's freshly-rendered state immediately *and* sees its place relative to other anchors needing attention. Q.md is the single user-facing glance surface.

**Never glance `{NAME} Triage.md` directly.** The per-anchor Triage file is the agent's persistent intermediate state — Q.md is the dashboard the user actually reads. Opening the per-anchor file would force the user to navigate to the global view themselves, which is exactly the friction Q.md was built to eliminate. **There is only one glance target for `/triage`, and it is `~/ob/kmr/Q.md`.**

(Per `[[SKA ask]]` the glance is allowed: the agent has just modified Q.md with new state, and the user is in active mode by virtue of having invoked `/triage`.)

### 8. Print the anchor's banner as the LAST line of chat output — visually emphasized

The final lines of chat output after a `/triage` run MUST be the anchor's just-rendered banner, **wrapped in equal-sign rules above and below and rendered bold**. This is the user's "boom — this is the status" signal; the visual delimiter makes the banner unmistakable even when chat is dense.

**Format — three lines, exactly:**

```
======================================================================
**[<TAG>]  <NAME> Triage  -  Ready N    Questions N   |   Now N    Next N    Later N    Icebox N**
======================================================================
```

- **Top rule**: 70 equal signs on their own line.
- **Banner line**: bolded with `**...**` markdown, same content/spacing as the Q.md H1 (two spaces after `[<TAG>]`, three spaces around `-`, four spaces between counts within a group, `   |   ` between groups).
- **Bottom rule**: 70 equal signs on their own line.

The 70-char rule width matches typical terminal width; renders as a continuous bar in chat.

**Why this matters.** The user's invocation pattern is `"` (`/triage`) or `'` (`/crank`) — single keystrokes. After either, the LAST chat content is what they see without scrolling. When `/crank` ran a long mint sequence and then `/triage` painted state, the banner can otherwise get lost above the per-anchor counts. The `===` rules + bold make it pop. Per the user spec change 2026-05-25: *"the triage needs to stand out more. ... boom. This is the status of things."*

This **replaces** the older one-line `/triage — {NAME}: TAG {TAG}; …` summary form. The banner is the densest summary of anchor state; the visual emphasis guarantees visibility on every press.

**Exact transformation from the Q.md H1 line** (for the bold middle row):
- Drop the leading `# ` (H1 marker).
- Replace `[[<NAME> ask|<NAME>]]` with the plain text `<NAME> Triage` (no Obsidian markup in chat; keep the "Triage" word in the chat-form for clarity since chat doesn't have the page context Q.md does).
- Wrap the whole thing in `**...**` for bold.
- Everything else (TAG, spacing, count groups) preserved verbatim.

**Stale-Done note** — if any `[Done]`-bracketed rows were skipped from rendering, append a one-line note ABOVE the top rule so the banner block (rule + bold + rule) stays last:

```
Note: {K} stale [Done] rows still in horizon H2s — run /groom to move to ## Done.
======================================================================
**[<TAG>]  <NAME> Triage  -  Ready N    Questions N   |   Now N    Next N    Later N    Icebox N**
======================================================================
```

**Crank interaction.** When `/crank` ends with `/triage` (any Ready==0 exit path per `[[SKA crank]]` § Post-loop exit), the chained `/triage`'s banner block is crank's last chat content — `'` always lands on the bold-banner-between-rules whenever Ready dropped to zero. When `/crank` exits silently (Ready > 0), no banner is printed — that's the "agent still has work" signal.

**Hard-continuation directive — mandatory annotation when Ready > 0.** Per user direction 2026-05-26 (after observing an agent emit `Loop exited cleanly` with `Ready 1    Questions 1`): when the rendered banner has `Ready N` with **N > 0**, append a directive line BETWEEN the banner and the bottom rule, addressed to whichever agent reads the chat (typically the same agent that just rendered it). The line cites `crank/SKILL.md` and names the 3-gate exit requirement so the agent can't paraphrase its way past the rule:

```
======================================================================
**[<TAG>]  <NAME> Triage  -  Ready N    Questions N   |   Now N    Next N    Later N    Icebox N**
⚠ Ready > 0 — agent MUST continue per crank/SKILL.md § Hard rule. To stop, print 3-gate argument (uncertain + high-downside + risk-of-continuing). 'Loop exited cleanly' is a spec violation.
======================================================================
```

The directive appears **only when N > 0**; omitted when Ready 0 (no agent action available, banner stands alone). This is the structural defense against lazy-stop phrasings: the agent reads the banner at the moment they're tempted to stop, and the directive sits inline with the banner so it can't be skipped.


## Sticky-context protocol

When the user says "I'm in F11 now" (or any phrasing that names a single feature), maintain F11 as the active context across subsequent turns. Plain `Q7: {answer}` from then on means F011 Q7 — no need for the user to repeat the F-number until they announce a switch ("now F12"). The initial F-number is the disambiguator; sticky context handles the rest.


## Verify-resolution path

When the user responds with "F23 verified" / "verified F23" (or any natural-language equivalent referencing a `[Verify]` item by F-number), the agent:

1. Locates the backlog row with `[Verify]` bracket and the matching F-number.
2. Moves the row to `## Done`. The bracket on `## Done` items is optional/redundant per `[[CAB Backlog]]`; the H2 implies the state.
3. Updates the corresponding feature-doc `## Status` field to `Done`.
4. Optionally appends a one-line "Verified YYYY-MM-DD" note to the Done row if the user requested confirmation.

This is the canonical `[Verify]` → `[Done]` transition from `[[SKA workflow]]`. User verification *is* the gate that opens Done.


## Question-resolution path

When the user responds with `F005 Q4: yes` (or the sticky-context shorthand `Q4: yes` after announcing F5 as context), follow `[[SKA ask]]` § Resolution:

1. Locate F5's feature doc, find Q4 in its `## Open Questions` block.
2. Move Q4 to `### Resolved` with the user's answer in the canonical form: `**Q4** — **Resolution:** {one-sentence summary}. Incorporated into {section / conversation}.`
3. Update the relevant Design (or other) section if the resolution changes the spec.
4. Do NOT glance the feature doc on resolution (per `[[SKA ask]]` § Glance rules).

If F5 has zero pending Qs after the resolution, follow Phase 1 → Phase 2 in `[[SKA ask]]`: delete `## Open Questions` H2, migrate accumulated `### Resolved` to a `## Resolved` H2 at the bottom.

For à la carte Qs (`{NAME} Q3: …`), the same path applies against `{NAME} Questions.md` instead of a feature doc.


## What `/triage` does NOT do

- Doesn't create new feature docs — that's `/groom`'s job.
- Doesn't move backlog items between H2s on its own (except via the verify-resolution path when the user says "F23 verified").
- Doesn't answer the questions or auto-resolve them — its job is surfacing.
- Doesn't write to feature docs except via the question-resolution path (when the user actually answered a Q).


## Compound usage: "triage and groom"

When the user says "triage and groom" (or "groom and then triage" — order in language doesn't matter), the Pilot runs `/groom` first to populate `[Questions]` state by parking new items, then `/triage` to surface the inbox. This is a Pilot-level natural-language interpretation, not a special flag or DMUX trigger — keeps both skills small.


## Idempotence

Strictly idempotent + destructive. The agent rewrites the entire anchor section within Q.md on every run. No marker comments, no preserve-user-edits regions — each per-anchor section is agent-owned space. Running twice with no backlog change produces no diff on the second pass (the bubble-to-top is still no-op if the section is already at top).


## Failure modes

- **No anchor found** — say "No anchor found from `{cwd}` upward." and stop.
- **No backlog file** — say "No `{NAME} Backlog.md` at `{expected path}`." and stop.
- **Empty body** — H1 banner is still written (TAG = `[]`); body is empty. Glance regardless.
- **Backlog item missing F-number** — render as `**F? — {Item Name}**` and surface the missing-number issue in the chat summary, but don't fix it inline (that's `/groom`'s job).


## Cross-references

- **`[[CAB Triage]]`** — presentation-form spec (no per-anchor file location per F075).
- **`[[CAB Questions]]`** — sibling à la carte facet.
- **`[[CAB Backlog]]`** — backlog format, F-numbering, status brackets, `[Verify]` semantics.
- **`[[SKA ask]]`** — `## Open Questions` block format inside feature docs (the source of question text), and the writer for à la carte Qs.
- **`[[SKA backlog-horizons]]`** — horizon H2s (Now / Next / Later) and the per-bucket count scheme.
- **`[[SKA workflow]]`** — `[Questions]` / `[Verify]` / `[Done]` state semantics and transitions.
- **`/groom`** — pairs with triage; groom *creates* the question state by parking, triage *gathers* and surfaces it.
- **`/roster`** — counts every backlog item once per bucket; triage's H1 count line uses the same scheme so the two views agree.
