---
name: ask-format
description: Discipline. The format for any user-actionable surface that an agent writes — Questions (Q<n>), Verifies, à la carte items, resolution-acceptance phrases. Owns the navigation invariant (every Q / Verify is link-targetable). Cited by /ask, /triage, /feature, /groom, /crank, and /audit q.
user_invocable: false
---

# ask-format

ask-format is *the layout discipline for any user-actionable surface an agent writes — pending Questions, Verifications, à la carte items, and the resolution / acceptance phrases that close them.* What distinguishes a conformant surface from an ad-hoc one:

- **Block-IDs** — every Q and Verify carries a `^F<n>-Q<m>` or `^F<n>-V<m>` block-ID so it is link-targetable from anywhere in the vault.
- **Labeled alternatives** — every Q has `(A)` / `(B)` / `(C)` options on their own sub-bullets; no inline `"X or Y"` shorthand.
- **Recommendation strength** — every Q ends with `**Recommendation:** Strong / Lean / None — <reason>`. Strong means decide; None means user-only.
- **Numbered Q-headers** — Q1, Q2, … per-doc monotonic; persist forever (never recycled).
- **Standard acceptance phrasing** — answers in the form `F<n> Q<m>: yes` / `verified F<n>` so the receiving skill can mechanically map shorthand → action.

This is a discipline, not a user-invocable skill — other skills cite it via `[[DSC ask-format]]` and Claude Code loads it into context before they run.


## Who cites this discipline

| Skill | What it uses |
|---|---|
| `/ask` | Question layout (both parented and bare modes), numbering, write-surfaces, acceptance/rollback phrases. |
| `/triage` | Recognizes well-formed Q-rows and Verify-rows when rendering the body. Does not enforce — that's `/audit q`. |
| `/feature` | The `## Open Questions` block format below the H1. Phase 1/2/3 lifecycle. |
| `/groom` | When parking questions into newly-created feature docs, uses this format. |
| `/crank` | When `/crank` is about to surface a Question or Verify to the user, uses this format. Prevents the flatfooted ask. |
| `/audit q` | **Enforces** the discipline mechanically via rules C6–C11. |


## Surfaces — where these items live

| Item shape | Surface |
|---|---|
| Doc-attached `Q<n>` | The doc's `## Open Questions` H2 below H1 |
| À la carte `Q<n>` | `{NAME} Questions.md`, `## Open Questions` H2 |
| Inline-on-backlog-row `Q<n>` | Under the B-row in `{NAME} Backlog.md` |
| `[Verify]` request | Standalone item in the backlog row's bracket, body describes the verify |
| Drain snapshot | `{NAME} ask.md` (bare `/ask`'s output, three sections) |


## Five-piece question layout

Every `Q<n>` has the same shape so the user can scan many at once and rubber-stamp the high-confidence ones.

1. **Question header** — one top-level bullet: `- **Q<n> — Short question name** — context, why we're asking, what's at stake. ^<container>-Q<n>`. The block-ID is **mandatory** (per § Navigation invariant).
2. **Options as labeled sub-bullets** when there are alternatives — each on its **own** sub-bullet, prefixed with a label the user can reference unambiguously (`(A)` / `(B)` / `(D1)` / `(D2)` …). **Never embed alternatives inline as prose** — `"Either (a) X or (b) Y"` defeats the whole point. One alternative per bullet, labeled, no exceptions.
3. **Recommendation as a sibling top-level bullet** — **outdented to the same level as the Question header**, not nested under the options. The bolded `**Recommendation:**` prefix is the eye-anchor; outdenting makes it pop visually as the answer-line, not as one more option to read.
4. **Strength label** — exactly one of: **Strong** / **Lean** / **None**.
5. **One-line reason** for the recommendation — what about the alternatives makes the recommended one the right call.

### Recommendation strength

| Label | When to use | Format |
|---|---|---|
| **Strong** | High confidence; clear reason; alternatives have no meaningful trade-off. User can rubber-stamp. | `- **Recommendation:** Strong (B). <reason>.` |
| **Lean** | Moderate confidence; one option seems better but alternatives are defensible. User should consider. | `- **Recommendation:** Lean (B). <reason>.` |
| **None** | Genuine uncertainty — user-preference-dependent or insufficient context. | `- **Recommendation:** None. <one-line reason naming what specifically the agent doesn't know>.` |

Pick exactly one label. Don't fudge with "lean strongly" or "weak recommendation" — those collapse to Lean.

**Try first, `None` second** (per user direction 2026-06-04 / audit § Governing principle). The Recommendation is the **agent's** field, never the user's. Before writing `None`, the agent reads the Design section, conversation history, prior similar decisions in `## Resolved`, memory, related backlog rows, the user's stated preferences — and tries to form a real Strong or Lean. **`None` is the answer when honest effort produces no basis for a stronger pick**, not a placeholder for "I haven't tried yet." The user reviews `None` recommendations specifically — that's their actionable inbox; they cannot review a *missing* Recommendation. **Empty Recommendation = agent didn't try. Audit C9 fails it; the 100%-fix discipline requires the agent fill it in.**

### Spacing — load-bearing visual structure

Per user direction 2026-05-25: *"the questions are bulleted ... they always have a list of alternatives that are labeled that each begin on their own line within the bullet ... And there's always a blank line between the bullet sections."*

- **Each option is its own labeled sub-bullet** `- **(A)** ...` — one per line, no exceptions. Never combine `(A)` and `(B)` on a single line. (Enforced by **audit-q C19**.)
- **No blank line** between the Question header, its options, and the Recommendation — they belong to the same question group.
- **One blank line after the Recommendation**, separating each question from the next. (Enforced by **audit-q C20**.) The blank line is the visual separator that lets the user's eyes parse the doc as a list of question-groups.

### Canonical example

```
- **Q3 — `/land` + `/roster`: always run roster, or only when work was landed?** When `/land` finds nothing in flight, two options. ^F013-Q3
  - **(A)** Always run roster — print state-of-the-work even when zero activities landed. Cost: one extra block of output.
  - **(B)** Only run roster after work was landed — skip if there was nothing in flight. Cost: lose the "you're at zero, here's the next-action menu" signal in the empty case.
- **Recommendation:** Lean (A). The empty case still benefits from a "here's what's queued up" view; the cost is tiny.

- **Q4 — Next question name** — context. ^F013-Q4
  - **(A)** Option A — short description.
  - **(B)** Option B — short description.
- **Recommendation:** Strong (B). One-line reason.
```

### Open-ended (no alternatives)

```
- **Q5 — How should we name the new module?** — context. ^F013-Q5
- **Recommendation:** None. Pure preference call — your choice between `worker`, `runner`, or `executor`.
```


## Four-piece verify layout

A `[Verify]` item is structurally a request to the user to do something the agent couldn't mechanically do. The format mandates that the writer think through each piece — what's done, what's left, why, what success looks like — so the user receives a fully-specified ask, not a flatfooted "verify this".

1. **Verify header** — one top-level bullet: `- **Verify — Short verify name** — one-sentence summary of what needs verification. ^<container>-V<n>`. The block-ID is mandatory (same as Q-items).
2. **What the agent already verified** — sub-bullet: concrete mechanical checks the agent ran, with results. (Example: *"Ran `pytest tests/F23_test.py`: 12/12 green. Confirmed file exists at `path/to/x.md`. Greppped the codebase for `old_name` — 0 hits."*)
3. **What's left for the user** — sub-bullet(s): specific named steps the user takes. Each step concrete enough that the user could automate it next time. **Why human eyes**: one line per residual — what the agent CAN'T mechanically check (UI rendering, semantic correctness, smell test, integration with the rest of life).
4. **Expected output** — sub-bullet: what success looks like. (Example: *"The panel renders without overflow on a 1440×900 window. The Cmd+Shift+P shortcut opens the inspector. The toolbar shows the new `History` icon."*)

### Canonical Verify example

```
- **Verify — F058 dispatch-table row format landed in CAB Traits/Code Anchor.md** — confirm the row-format section reads as intended and would resolve future ambiguities. ^F058-V1
  - **What I verified:** Ran `grep -c '^### Dispatch row format$' "CAB/CAB Traits/Code Anchor.md"` → 1 match. Confirmed the with-children + without-children + forbidden-forms + breadcrumb-exception sub-sections are all present. Ran `markdown-link-check` over the file → 0 broken links.
  - **What's left for you:** Open `CAB/CAB Traits/Code Anchor.md` § Dispatch row format. Read the four sub-sections in order. Confirm: (a) the with-children form covers the cases you remember surfacing in SVAR.md, (b) the without-children form doesn't drift from the actual SKL.md dispatch tables, (c) the forbidden-forms section catches the markdown-link-with-hook-URL pattern that was the original prompt.
  - **Why human eyes:** The format spec is for *future* drift prevention — only you know whether it actually captures the cases you cared about. Mechanical checks can confirm structure, not intent-match.
  - **Expected output:** "Looks right" or specific edits to the spec (which sub-section to tighten, what to add).
```

### When the verify is trivial

If the verify reduces to *"glance the file"* with no decomposable sub-steps, drop the four-bullet structure and use a one-line form:

```
- **Verify — F058 spec landed** — glance `CAB/CAB Traits/Code Anchor.md` § Dispatch row format; intent-match check. ^F058-V1
```

But verify carefully: if the user's last 5 verifies all ended up needing multiple back-and-forth clarifying messages, that's evidence the one-line form is being abused. Default to the four-piece form unless you're certain.


## Deferred-by-use Verify — `[Verify-by YYYY-MM-DD]`

Some Verifies are best handled **passively**: the user's normal workflow naturally exercises the change, and any failure becomes user-visible during that normal use. For these, interrupting the user to actively verify is friction with no benefit — but optimistically marking `[Done]` is premature because the change might still fail.

**The deferred-by-use pattern**: file the item as `[Verify-by YYYY-MM-DD]` in `## Later`. The user doesn't scan Later in normal workflow, so it doesn't interrupt them. If the change fails during the window, the user notices and pulls the item back. After the date passes, `/groom` auto-moves the item to `## Done` with a note that the deferred-by-use window expired without recurrence.

### When to use the deferred pattern (both conditions required)

- **High confidence the change is right** — agent has tested mechanically or the change is structurally simple.
- **Failure mode is user-visible during normal use** — the user will see the failure as part of how they normally interact with the system. Silent failures, infrequently-exercised paths, or "fails only when X happens once a year" do NOT qualify.

If only one condition holds, escalate to active `[Verify]`. If neither, the change isn't really verified — keep as `[Designing]` or `[Active]`.

### Bracket form

```
- **F<n> — Title** [Verify-by 2026-06-23] — what the change was. Naturally exercised by: <one-line statement of what normal usage will hit the change>.
```

The body **must** include a "Naturally exercised by" line — names the workflow that will hit it. Without this, the rationale isn't auditable later, and the agent can't reason later about whether the window should extend.

### Placement

`[Verify-by <date>]` items go in `## Later`, never in `## Now` or `## Next`. The whole point is that the user isn't supposed to see them in their daily view — they're parked, awaiting passive verification.

### Forward-throw window — agent picks per item, no default

The agent picks the date based on **exercise frequency**, not a fixed default. Suggested windows:

| Change shape | Suggested window |
|---|---|
| Daily-hit (UI, dispatch tables, breadcrumbs) | **3–7 days** |
| Discipline that fires every few /ask calls | **~2 weeks** |
| Migration that runs nightly | **1–2 weeks** |
| Infrequent skill (`/publish`, `/install`, `/yore`) | **30–60 days** |
| "I really don't know how often this gets used" | **30 days** (safety fallback) |

The window goes in the bracket; the **reason** for that window goes in the body. *"Verify-by 2026-06-09 — next /ask call hits the new format"* is auditable. *"Verify-by 2026-06-09"* alone is not.

### Triage behavior

Per `[[SKA triage]]` § Render: Later items with `[Questions]` or `[Verify]` brackets surface in the Later H2. **Extension for `[Verify-by <date>]`:**
- If today < date → surface in Later H2 (user can see it if they look).
- If today >= date → **hide**. The item is past its deferred-by-use deadline; auto-completion happens at next `/groom`.

This keeps the banner counts honest (the Verify count doesn't include expired-but-not-yet-groomed items) and stops Triage from showing items that are about to disappear.

### Auto-expiration via /groom

Per `[[SKA groom]]` § Bracket reassessment: when scanning, for each `[Verify-by <date>]` row where today >= date:

1. **Default**: move to `## Done` with note *"Auto-Done <today-date> — `[Verify-by <bracket-date>]` window expired with no failure surfaced."*
2. **Optional extension**: if the agent has evidence the change wasn't actually exercised (e.g., the relevant skill hasn't run since the row was filed), extend the bracket date and add a note *"Extended to <new-date> — no usage observed yet."*

The agent's call between (1) and (2) depends on whether "naturally exercised" actually happened. Default is auto-Done; extension is the rare case.

### When NOT to use the deferred pattern

- **High-stakes change** — financial, security, deploy, irreversible. Always active `[Verify]`.
- **Silent-failure mode** — failure wouldn't surface to the user even if it hit. Always active `[Verify]`.
- **"Probably works but I'm not sure"** — that's a Question, not a deferred-Verify. Don't smuggle uncertainty under the deferred label; the "high confidence" precondition is binary.
- **Irreversible if it fails** — even if user-visible, if the failure mode destroys data or sends external messages, active-Verify is the right call.


## Navigation invariant

**Every Q-item and Verify-item the agent writes MUST be link-targetable, and every reference to it from elsewhere MUST use the link-targeting form.** The user clicks; the cursor lands on the item. Items the user can't click to are broken in the same way as items with no Recommendation are broken.

### Block-ID on the item

Every `Q<n>` / `Verify` bullet ends with an Obsidian block-ID:

- **Q-items**: `^<container>-Q<n>` (e.g., `^F082-Q3`, `^SKA-Q1`, `^QFix-Q2`)
- **Verify-items**: `^<container>-V<n>` (e.g., `^F058-V1`, `^B-skl-user-docs-V1`)

Where `<container>` is the F-number for feature-doc Qs, the slug for à la carte, or the row-ID for B-row inline.

### Link form for references

When referring to a specific Q or Verify from elsewhere:

| Container | Link form |
|---|---|
| Feature doc | `[[F<NNN> — Title#^F<NNN>-Q<n>\|F<NNN> Q<n>]]` |
| À la carte | `[[{NAME} Questions#^{NAME}-Q<n>\|{NAME} Q<n>]]` |
| B-row inline | `[[{NAME} Backlog#^<row-id>-Q<n>\|<row-id> Q<n>]]` |
| Verify item | Same pattern with `-V<n>` instead of `-Q<n>` |

**Never link to the container alone** when referring to a specific Q or Verify. `[[F23]]` lands on the doc; the user has to scan for Q3. The block-ID form lands the cursor on the item directly.


## Numbering policy

`Q<n>` and `V<n>` numbers are stable references — once assigned, never renumber, even when items resolve out of order. Skipped numbers are fine. Same lowest-unused-integer policy as backlog F-numbers (per [[CAB Backlog]] § Numbering policy), scoped per container:

- Each feature doc has its own Q-namespace.
- Each anchor's `{NAME} Questions.md` has its own Q-namespace.
- Each B-row's inline Qs have their own namespace.
- V-namespace is independent of Q-namespace (so `F23` can have both `Q3` and `V1`).


## Phase 1 / 2 / 3 lifecycle (Open Questions blocks)

A document with `Q<n>` items moves through three phases (per [[SKA ask]]):

**Phase 1 — pending Qs exist.** `## Open Questions` H2 sits below H1, containing pending Qs. Resolved Qs accumulate inside as a `### Resolved` H3 sub-section.

**Phase 2 — all Qs resolved.** Delete the `## Open Questions` H2 entirely. Migrate the `### Resolved` content to a `## Resolved` H2 at the bottom of the doc.

**Phase 3 — new Q arises later.** Recreate `## Open Questions` below H1; same lifecycle as Phase 1.

Auto-decisions made under [[F068 — Assume-and-announce discipline (Drive mode)|F068]] (visible + low recoverability) **skip Phase 1 entirely** — they go directly into the bottom `## Resolved` H2 as H3 entries, without staging at top.


## Acceptance & rollback (per F086)

In bare `/ask` mode, the agent's auto-resolutions accumulate in `{NAME} ask.md`'s `## Agent Resolutions` section across invocations until the user explicitly accepts.

### Acceptance — the user must explicitly say "resolution(s)"

The user must explicitly mention the word **"resolution(s)"** in an accepting context. Bare phrases like *"looks good"* / *"accept"* / *"lgtm"* don't count — too ambiguous because the user is doing many things in chat at once.

Counts as acceptance:
- *"resolutions look good"*
- *"accept the resolutions"*
- *"all the resolutions look good"*
- *"resolutions approved"*
- *"accept the first 5 resolutions"* (partial)
- *"the QFix resolutions look good"* (partial)

Does NOT count:
- *"looks good"* / *"accept"* / *"lgtm"* / *"approved"* — too ambiguous

### Rollback

The user references a specific resolution: *"roll back F085 Q1"* / *"actually do (B) on F081 Q4"*. The agent reverses the underlying change (feature doc Resolved → Open Questions; backlog row may rebracket). The remaining resolutions stay accumulated — rollback does **not** implicitly accept others. The user closes with a single *"the rest of the resolutions look good"* when done.

### Partial accept

The user can name a subset: *"accept the first 5 resolutions"* / *"the QFix resolutions look good"*. The agent removes the named subset; rest stay accumulated.


## Enforcement (via /audit q)

`skills/audit/scripts/audit-q.py` enforces this discipline mechanically. Rules:

| Rule | Check | Fix mode |
|---|---|---|
| **C6** — block-ID present | Every `**Q<n> — ...**` bullet has `^<container>-Q<n>` at end of line. | Auto-fix: append canonical `^<container>-Q<n>`. |
| **C7** — block-ID link form | Every external `Q<n>` reference uses `[[file#^<container>-Q<n>\|...]]` form, not bare `[[file]]` or `[[file#heading]]`. | Report only. |
| **C8** — labeled alternatives | A Q row with embedded prose alternatives (`"Either (a) X or (b) Y"`) is non-compliant. | Report only. |
| **C9** — Recommendation present | Every Q has a sibling Recommendation bullet with one of: Strong / Lean / None. | Report only. |
| **C10** — Recommendation outdented | The Recommendation bullet is at the same indent level as the Question header (not nested under options). | Auto-fix: rewrite indentation. |
| **C11** — Verify four-piece | Every `Verify` row that's not the trivial one-line form has all four sub-bullets: what-verified / what's-left / why-human / expected-output. | Report only. |
| **C12** — Verify-by has rationale | Every `[Verify-by YYYY-MM-DD]` row body contains a *"Naturally exercised by: …"* line. | Report only. |

`/audit q` is auto-wired as a post-condition into `/triage`, `/groom`, `/mint`, `/finalize`, `/feature` (per [[F076]] Q6). Adding the C6–C11 rules means every caller enforces the discipline automatically.


## Pre-ask self-check — six guidelines (per F105 + B-stop-asking-trivial-checks)

Before adding any Q to the queue, the agent runs this self-check. If any rule matches, the Q is auto-resolved and the decision goes to `## Agent Resolutions` (per F068 announce mechanic) — never surfaced. These are concrete patterns under F068's general "visibility + low-recoverability → auto-decide" rule.

### Rule 1 — Aggregate within the anchor before surfacing

Gather every pending Q across the anchor's surfaces — every feature doc's `## Open Questions` block + the anchor's à la carte `{NAME} Questions.md` — into one batch. Don't surface one feature's Qs in isolation when other features have pending Qs the user could answer in the same turn. If three feature docs each have a few open Qs, surface all of them together; if one has 4 and another has 2, surface 6 not 4.

**Scope is per-anchor.** Q formulation belongs to the agent who owns the anchor's context; cross-anchor aggregation is rejected. Within-anchor across-feature aggregation is the rule. No quantitative threshold — "everything pending in this anchor" is the batch.

### Rule 2 — Never ask "should we continue / stop?"

Auto-answer: **continue.** The user can always interrupt; they don't need a permission prompt. Drafted Qs of the shape *"is now a good time to pause?"* / *"should I stop here?"* / *"are you still engaged?"* are auto-resolved as continue and don't reach the user. (This extends `/crank`'s hard continuation rule from crank's own Q-escape to every Q-asking skill.)

### Rule 3 — Never ask "should we burn tokens for a better outcome?"

Auto-answer: **yes, do the more complete thing.** Per Drive Mode (more not less) and F068's quality-axis amendment (tokens are not the constraint; user-interruption cost and quality are). Drafted Qs of the shape *"should I add tests for plausibly-reachable edge cases?"* / *"should I expand coverage on X?"* / *"should I verify across more cases?"* / *"should I generate a longer/more complete output?"* are auto-resolved as yes.

**Sanity cap.** When the cost/value ratio is genuinely insane (e.g., running a 30-minute integration suite to verify a docstring typo), the agent uses judgment and may auto-decline. But the **default** is yes; the burden is on the agent to articulate why the larger-token path is *not* worth it before declining.

### Rule 4 — Never ask "how to split the work?"

Auto-answer: **agent decides.** Drafted Qs of the shape *"should A and B be one feature or two?"* / *"should we extract X into its own feature?"* / *"is C in scope or separate?"* — the agent picks the shape that makes each piece independently shippable, and files the resulting features with the correct brackets:

- Different dependencies → split. File the dependency-free piece as `[Ready]`; file the dependent piece with `[Blocked F<n>]` or `[Designing]` as appropriate.
- Splitting creates a piece doable RIGHT NOW (Definition of Ready met) → that piece's bracket is `[Ready]`; the next `/crank` picks it up.
- Truly inseparable → don't split.

The user sees the resulting feature(s) on the backlog. No Q surfaces.

### Rule 5 — Never ask "quick way or complete way?"

Auto-answer: **complete way.** Per Drive Mode.

**Escape valve.** If there's a legitimate reason to do the quick way first (e.g., a partial fix unblocks downstream work the user is waiting on), do the quick way AND **file the complete way as a `[Ready]` feature on the backlog** so it's queued up for the next `/crank`. The user sees both on the backlog — the patch shipping now, the complete fix waiting.

### Rule 6 — Never ask a Q the agent can answer by reading a file

Auto-answer: **agent does the check.** If a Verify or Q reduces to "open file X and look for Y" AND the agent has Read access to X AND no human judgment is required, the agent runs the check itself and surfaces only the verified result — never the verification action. Drafted Verifies of the shape *"open MACAPP.md after the next scan and confirm dedup worked"* or Qs of the shape *"what does line 47 of config.toml say?"* — when the agent has Read access — are auto-resolved by running the check.

**Failure mode this catches** (observed 2026-06-03, cross-anchor): agent finished a fix, then asked the user to "open MACAPP.md after the next scan" to confirm dedup worked — the agent could have done the Read itself with one tool call. Surfacing it as a user Verify created a round-trip with no human signal needed.

**The three preconditions, in order:**
1. **Reduces to a file-content check** — the Q/Verify is "look in file X for Y" or equivalent (a grep, a JSON parse, a count, a state inspection).
2. **Agent has Read access to X** — the file is on disk and reachable by the agent's tools. (Files behind UIs the agent can't reach, screenshots only in the user's head, prod-system queries — fail this gate; surface as a real user task.)
3. **No human judgment is required** — "did the script execute" / "does the count match" / "is the field present" pass; "does this design feel right" / "does the layout look balanced" / "is this what the user meant" fail.

**Tier mapping** (per `[[DSC verification]]` § The four tiers): items satisfying all three are **Tier 1 (agent-immediate)** — run the check, ship the verified result. Misclassifying a Tier-1 check as Tier 3/4 ("the user will see this in normal use") because asking *feels collaborative* is the failure mode this rule names.

**Counter-example — when to ASK:** the Verify requires looking at UI rendering / human judgment on aesthetics / observation in a system the agent can't reach (an iOS app running on the user's device, a Slack message thread the agent has no API for, a sensation about whether code "feels right"). These are legitimately user-only. Rule 6 narrows to the trivial-grep case.

### How auto-resolution surfaces

When any rule auto-resolves a Q, the decision is recorded in the relevant doc's `## Resolved` H2 (feature doc) or in `## Agent Resolutions` (bare `/ask`'s drain page) with a one-line note: *"Auto-resolved per ask-format § Pre-ask self-check rule N: <decision>."* The user reviews on next `/ask` and can roll back if any auto-call was wrong (per F086 acceptance & rollback).

## Anti-patterns

- **Inline alternatives** — `"Either (a) X or (b) Y"` collapsed onto one line. Always sub-bullets, always labeled.
- **Nested Recommendation** — `Recommendation:` sub-bullet under the options. Outdent it.
- **No strength label** — *"I think B is probably better"* without Strong/Lean/None. Pick a label.
- **Bare-file link** — `[[F23]]` referring to F23's Q3. Use the block-ID form.
- **Flatfooted Verify** — `**Verify** — check that the panel renders.` with no "what I verified" / "specific steps" / "why human" / "expected output". Use the four-piece form.
- **Q-numbers renumbered** — never. Stable references.
- **Editing accepted Agent Resolutions** — accumulated until accepted; don't reshape mid-flight.
- **Bare "A vs B" in chat / console / transient channels** — never write *"your read on A vs B"* or *"waiting on A or B"* in chat. Letter labels lose meaning across messages — the user reads chat linearly and won't have the ask doc's option text in scrollback. Restate the full question + each option's content + reference by `F<n>-Q<n>` (or equivalent identifier). The ask doc itself is governed by the rest of this discipline; this rule covers the transient-channel surface.


## Chat & transient-channel asks — restate context inline

The five-piece layout above governs **written surfaces** (ask doc, feature doc, à la carte facet). When an agent surfaces a pending question into a **transient channel** — a chat message, a console status line, a one-shot prompt — the rules tighten further:

- **Full question text inline.** Restate the actual question. Don't write *"your read on F77 Q7?"* — write *"F77 Q7 — naming convention for flow-Traits: bare nouns (`Drive`/`PR`/`Commit`) vs `-Mode` suffix vs `-Flow` suffix vs mixed-by-category."*
- **Full option content inline.** Don't write *"A vs B."* Write each option's actual text — *"(A) bare nouns / (B) -Mode suffix / (C) -Flow suffix / (D) mixed."*
- **F<n>-Q<n> reference required.** Always cite the canonical-record location so the user can locate the durable version, but the chat itself stays self-contained.
- **Recommendation strength inline.** *"Lean (A) — matches F090 unsuffixed names."* Not just *"recommend A."*

**Why:** chat is read linearly. By the time the user sees *"waiting on A or B,"* the message that defined A and B may be 20 messages back. Bare letter references force a context-rebuild that the user reasonably refuses. Per durable user feedback (2026-06-06): *"You should never ask me waiting on A or B. Because there's no context with that... F18 Q3, A or B. That would be a well formed question to me."*

The principle generalizes to **any user-actionable item in a transient channel** — verifies surfaced in console output, à la carte items printed in a status report, even multi-step confirmations across turns. If the user can't act on the chat message without scrolling back or opening another file, the message is incomplete.


## Cross-references

- `[[SKA ask]]` — the writer skill. Both parented and bare modes write per this discipline.
- `[[SKA triage]]` — the reader skill. Renders items written per this discipline.
- `[[SKA feature]]` — creates `## Open Questions` blocks at feature-doc creation.
- `[[SKA groom]]` — parks questions into feature docs per this discipline.
- `[[SKA crank]]` — when surfacing user-actionable items, uses this discipline.
- `[[audit q]]` — enforces this discipline mechanically.
- `[[CAB Backlog]]` § Numbering policy — same lowest-unused-integer rule.
- `[[F068 — Assume-and-announce discipline (Drive mode)|F068]]` — assume-and-announce; defines when an auto-decision (skipping Phase 1) is valid.
- `[[F086]]` — accumulate-resolutions semantics; defines acceptance/rollback phrases.
