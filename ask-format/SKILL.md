---
name: ask-format
description: Discipline. The format for any user-actionable surface that an agent writes — Questions (Q<n>), Verifies, à la carte items, resolution-acceptance phrases. Owns the navigation invariant (every Q / Verify is link-targetable). Cited by /ask, /triage, /feature, /groom, /crank, and /audit q.
user_invocable: false
---

# ask-format

This is a **discipline**, not a user-invocable skill. Other skills cite it.

The format for **anything an agent writes that needs the user to act** — pending Questions, Verifications, à la carte items, resolution-acceptance phrases. Captures both the layout (what each item looks like) and the navigation invariant (the user must be able to click directly to the item from anywhere it's referenced).

The reliability gain comes from the skill-loading mechanic: when a parent skill cites `[[ask-format]]`, Claude Code loads this discipline into context before the parent runs. The parent then writes per these rules automatically.


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
| **None** | Genuine uncertainty — user-preference-dependent or insufficient context. | `- **Recommendation:** None. <one-line reason: why uncertain>.` |

Pick exactly one label. Don't fudge with "lean strongly" or "weak recommendation" — those collapse to Lean.

### Spacing

- **No blank line** between the Question header, its options, and the Recommendation — they belong to the same question group.
- **One blank line after the Recommendation**, separating each question from the next.

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

Auto-decisions made under [[F068]] (visible + low recoverability) **skip Phase 1 entirely** — they go directly into the bottom `## Resolved` H2 as H3 entries, without staging at top.


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


## Anti-patterns

- **Inline alternatives** — `"Either (a) X or (b) Y"` collapsed onto one line. Always sub-bullets, always labeled.
- **Nested Recommendation** — `Recommendation:` sub-bullet under the options. Outdent it.
- **No strength label** — *"I think B is probably better"* without Strong/Lean/None. Pick a label.
- **Bare-file link** — `[[F23]]` referring to F23's Q3. Use the block-ID form.
- **Flatfooted Verify** — `**Verify** — check that the panel renders.` with no "what I verified" / "specific steps" / "why human" / "expected output". Use the four-piece form.
- **Q-numbers renumbered** — never. Stable references.
- **Editing accepted Agent Resolutions** — accumulated until accepted; don't reshape mid-flight.


## Cross-references

- `[[SKA ask]]` — the writer skill. Both parented and bare modes write per this discipline.
- `[[SKA triage]]` — the reader skill. Renders items written per this discipline.
- `[[SKA feature]]` — creates `## Open Questions` blocks at feature-doc creation.
- `[[SKA groom]]` — parks questions into feature docs per this discipline.
- `[[SKA crank]]` — when surfacing user-actionable items, uses this discipline.
- `[[audit q]]` — enforces this discipline mechanically.
- `[[CAB Backlog]]` § Numbering policy — same lowest-unused-integer rule.
- `[[F068]]` — assume-and-announce; defines when an auto-decision (skipping Phase 1) is valid.
- `[[F086]]` — accumulate-resolutions semantics; defines acceptance/rollback phrases.
