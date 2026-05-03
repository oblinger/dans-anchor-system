---
name: triage
description: >
  Surface the **status of the anchor** — every backlog item except those in
  `## Later` and `## Icebox` — into one batched inbox at
  `{NAME} Docs/{NAME} Plan/{NAME} Triage.md`. Body has 4 H2s
  (Active / Ready / Now / Next), source order from the backlog, one bullet per
  item. Status brackets carry counts (`**[3 Questions]**`, `**[Verify]**`).
  H1 banner has an anchor TAG (`[U]` / `[A]` / `[U+A]` / `[G]` / `[?]` / `[]`)
  and pipe-grouped totals. À la carte questions live in the sibling
  `{NAME} Questions.md` facet — Triage carries one bullet line linking to it
  directly under the H1. The user can answer with shorthand like "F5 Q4: yes"
  (resolves a question) or "verified F23" (moves the item to `## Done` and
  updates the feature-doc Status). Use when the user types `/triage`, says
  `triage` (DMUX prefix-trigger auto-prefixes `/triage`), or sends `"` (a
  single double-quote) as the entire message.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Triage — Status of the Anchor

Generate the agent-owned triage file at `{NAME} Docs/{NAME} Plan/{NAME} Triage.md`. The file is the **status of the anchor**: it walks the backlog, lists every item except those in `## Later` and `## Icebox`, and writes one bullet per item under workflow-state H2s (`## Active`, `## Ready`, `## Now`, `## Next`). The user reads it to see "where everything stands and what's waiting on me."

DMUX trigger: **`triage`** (prefix-trigger; speaking `triage` stashes `/triage`, parallel to `snip` / `commission` / `fortify` / `groom`). Also: **`"`** (a single double-quote as the entire message), parallel to `crank`/`'` and `/land`/`.`. Slash invocation: `/triage`, `/triage roadmap`, `/triage milestone {N}`.


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
| `/triage icebox` | Walk `{NAME} Icebox.md` instead. Default scope (bare `/triage`) excludes the icebox per `[[workflow]]` § Active-work invariant; explicit invocation surfaces iced items needing input. |

Argument shape parallels `/groom`. Items in the icebox are not surfaced by default — Icebox items are explicitly parked, and the invariant says they don't compete for attention.


## Output file format — `{NAME} Triage.md`

Authoritative spec: `[[CAB Triage]]`. Summary:

```markdown
---
description: triage inbox (agent-owned)
---

# [<TAG>]  [[{NAME}]] Triage  -  Questions N    Verify N   |   Active N    Ready N   |   Now N    Next N    Later N    Icebox N
- **[N Questions]**  [[{NAME} Questions]]
## Active
- **[Active]** [[F<n> Title]] — description.
## Ready
- **[Ready]** [[F<n> Title]] — description.
- **[N Ready]** [[F<n> Title]] — description (milestone with N sub-items).
## Now
- **[N Questions]** [[F<n> Title]] — description.
- **[Verify]** [[F<n> Title]] — verify-plan text.
	- (Optional) sub-bullet with extended verification details.
- **[Ready]** [[F<n> Title]] — description.
## Next
- **[N Questions]** [[F<n> Title]] — description.
- **[N Ready]** [[F<n> Title]] — description.
```

**No blank lines anywhere in the body.** Every line carries information.

**No meta prose.** No "this page is maintained by the agent..." text. The user knows what the page is.

**No `## À la carte` H2.** Replaced by the single bullet line directly under the H1 linking to `[[{NAME} Questions]]` (only present when à la carte has pending Qs).

**Sections with no qualifying items are omitted** entirely (not even an empty H2). If the anchor has no items at all in Active/Ready/Now/Next, the body is just the H1 banner — nothing else.

**Items in `## Later` or `## Icebox` are not shown in the body** — only counted in the H1 banner. The framing: Triage = status of the anchor; lists all items except Later and Icebox.

**Within an H2**: items appear in **source order from the backlog**. The H1 banner already counts items by status, so re-grouping by status inside H2s is redundant. Reorder by editing the backlog (or asking the agent).


## Anchor TAG — cascading rule

Decide the H1 TAG by checking in order; first match wins, except U and A combine:

1. **U** if anchor has any `[Questions]` or `[Verify]` items (user-actionable).
2. **A** if anchor has any `[Active]` or `[Ready]` items (agent-actionable).
3. If both U and A: combine as `U+A` (literal `+`).
4. **G** if (no U AND no A) AND anchor has any items in `## Now` or `## Next` (groomable).
5. **?** if (no U, A, G) AND anchor has items in `## Later`.
6. **`[]`** (empty brackets) if nothing anywhere.

Tag values: `[U]`, `[A]`, `[U+A]`, `[G]`, `[?]`, `[]`.


## Status brackets — count and form

| Form | When |
|---|---|
| `**[Questions]**` | Single pending question (count omitted; rare). |
| `**[N Questions]**` | N pending questions in the feature doc's `## Open Questions` block (N > 1). |
| `**[Verify]**` | Single verification needed. Verify text inlines as the description (and may extend to a sub-bullet). |
| `**[N Verify]**` | N independent verification items (rare). When N is large, verify items live in the feature doc's `## Open Questions` § Verify subsection (parallel to Questions). |
| `**[Ready]**` | Single feature ready to mint. |
| `**[N Ready]**` | Milestone-style F with N independent sub-items in its roadmap, all ready. |
| `**[Active]**` | In flight (a worker is currently minting). |

The bracket is **bold**; the wiki-link to the feature doc is **not** bold; description follows after ` — ` and ends with a period.


## H1 banner spacing — exact

```
# [<TAG>]  [[{NAME}]] Triage  -  Questions N    Verify N   |   Active N    Ready N   |   Now N    Next N    Later N    Icebox N
```

- Two spaces between `[<TAG>]` and `[[{NAME}]]`.
- One space between `[[{NAME}]]` and `Triage`.
- **Three spaces around the `-`** separating "Triage" from the count groups.
- **Four spaces between counts within a group**.
- **Three-space-pipe-three-space** (`   |   `) between the three count groups.

Three count groups: user-actionable (`Questions`, `Verify`) | agent-actionable (`Active`, `Ready`) | horizon (`Now`, `Next`, `Later`, `Icebox`).


## À la carte — lives in `{NAME} Questions.md`

À la carte (anchor-level, cross-cutting, agent-raised) questions live in a **separate facet file**: `{NAME} Docs/{NAME} Plan/{NAME} Questions.md`. Spec: `[[CAB Questions]]`. Same `## Open Questions` block format as feature docs (per `[[ask]]`); same Phase 1 / 2 / 3 lifecycle.

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
- Resolve the target file: `{NAME} Docs/{NAME} Plan/{NAME} Triage.md` (create if absent).

### 2. Compute the H1 banner counts

Walk every bullet in the backlog. Compute:
- **Active / Ready / Now / Next / Later** — bullet count under each H2.
- **Icebox** — bullet count in `{NAME} Icebox.md` (zero if absent).
- **Questions** — sum of pending `Q<n>` across feature docs whose backlog rows are in Active/Ready/Now/Next (NOT Later or Icebox), **plus** pending `Q<n>` in `{NAME} Questions.md`.
- **Verify** — bullets across Active/Ready/Now/Next with the `[Verify]` bracket.

`## Done` and `## Legwork` are excluded from all counts.

### 3. Compute the anchor TAG

Apply the cascading rule above to pick `[U]` / `[A]` / `[U+A]` / `[G]` / `[?]` / `[]`.

### 4. Compute the à la carte bullet

Read `{NAME} Questions.md`. If it has pending `Q<n>` in `## Open Questions`, render the count and emit:

```
- **[N Questions]**  [[{NAME} Questions]]
```

(Two spaces between the bracket and the wiki-link.) Omit the line entirely when N=0.

If the legacy `## À la carte` H2 still exists inside `{NAME} Triage.md` (legacy from F25), migrate its content to `{NAME} Questions.md` on this regen pass — that's a one-time migration step. Existing à la carte Qs (using `Q<n>` after F25; if any pre-F25 anchor still has `A<n>`, also flip to `Q<n>` per F25 Q5 resolution).

### 5. Render body H2s

For each backlog H2 in this fixed order — `## Active`, `## Ready`, `## Now`, `## Next` — render the H2 line and one bullet per item, **in source order from the backlog**. Skip the H2 entirely when no items qualify. **Do not render `## Later` or `## Icebox`.**

For each item:

- Resolve the bracket using the existing item state in the backlog row, then map to one of the bracket forms above.
- For `[Questions]` items: count pending `Q<n>` in the linked feature doc's `## Open Questions` block. If N=1 use `**[Questions]**`; otherwise `**[N Questions]**`.
- For `[Verify]` items: use `**[Verify]**` (single) and copy the backlog row's verify-plan description as the body. If the verify text is long enough that the user wants more space, allow an indented sub-bullet with the extended verification details (one tab of indent, no bracket prefix, just prose).
- For `[Ready]` / `[Active]`: copy the backlog row's description (trim to one line ending in a period).
- Milestone-style multi-Ready items get `**[N Ready]**` with N = number of independent ready sub-items in the linked roadmap/feature doc.

Bullet template:

```
- **[<status>]** [[F<n> Title]] — description.
```

### 6. Destructively rewrite `{NAME} Triage.md`

Replace the entire file (preserving only the YAML frontmatter, with `description: triage inbox (agent-owned)`). File order:

1. YAML frontmatter
2. (Frontmatter delimiter ends with one blank line; the H1 follows.)
3. H1 banner
4. À la carte bullet line (only if N > 0)
5. `## Active` H2 + bullets (only if any)
6. `## Ready` H2 + bullets (only if any)
7. `## Now` H2 + bullets (only if any)
8. `## Next` H2 + bullets (only if any)

**No blank lines** between any of (3)–(8). The file is dense.

### 7. Regenerate the anchor's section in `~/ob/kmr/Q.md`

`Q.md` is the **vault-level Agent Status dashboard**. After regenerating `{NAME} Triage.md`, also regenerate the anchor's per-anchor section in `Q.md`. Per F28 Q3 (full body always):

The per-anchor section is **identical content** to the just-generated `{NAME} Triage.md` body — same H2s, same bullets, same ordering. The only difference is the H1-equivalent line: the slug-prefix becomes a wiki-link via `[[NAME Triage|NAME]]` syntax (renders as "NAME" but links to the Triage file).

```markdown
# [<TAG>]  [[{NAME} Triage|{NAME}]] Triage  -  Questions N    Verify N   |   Active N    Ready N   |   Now N    Next N    Later N    Icebox N
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

**If the anchor has TAG `[]`** (zero items anywhere): remove its per-anchor section from Q.md entirely. Done.

### 8. Glance the file

Always glance the file after the regen completes:

```bash
open "{NAME} Docs/{NAME} Plan/{NAME} Triage.md"
```

This is the natural close of a triage run — the user sees the inbox immediately. (Per `[[ask]]` the glance is allowed: the agent has just modified the file with new state, and the user is in active mode by virtue of having invoked `/triage`.)

### 9. Print a one-line summary in chat

```
/triage — {NAME}: TAG {TAG}; {Q} Qs, {V} verify, {A} active, {R} ready (Now {N}, Next {X}, Later {L}, Icebox {I}). Refreshed {NAME} Triage and Q.md.
```


## Sticky-context protocol

When the user says "I'm in F11 now" (or any phrasing that names a single feature), maintain F11 as the active context across subsequent turns. Plain `Q7: {answer}` from then on means F11 Q7 — no need for the user to repeat the F-number until they announce a switch ("now F12"). The initial F-number is the disambiguator; sticky context handles the rest.


## Verify-resolution path

When the user responds with "F23 verified" / "verified F23" (or any natural-language equivalent referencing a `[Verify]` item by F-number), the agent:

1. Locates the backlog row with `[Verify]` bracket and the matching F-number.
2. Moves the row to `## Done`. The bracket on `## Done` items is optional/redundant per `[[CAB Backlog]]`; the H2 implies the state.
3. Updates the corresponding feature-doc `## Status` field to `Done`.
4. Optionally appends a one-line "Verified YYYY-MM-DD" note to the Done row if the user requested confirmation.

This is the canonical `[Verify]` → `[Done]` transition from `[[workflow]]`. User verification *is* the gate that opens Done.


## Question-resolution path

When the user responds with `F5 Q4: yes` (or the sticky-context shorthand `Q4: yes` after announcing F5 as context), follow `[[ask]]` § Resolution:

1. Locate F5's feature doc, find Q4 in its `## Open Questions` block.
2. Move Q4 to `### Resolved` with the user's answer in the canonical form: `**Q4** — **Resolution:** {one-sentence summary}. Incorporated into {section / conversation}.`
3. Update the relevant Design (or other) section if the resolution changes the spec.
4. Do NOT glance the feature doc on resolution (per `[[ask]]` § Glance rules).

If F5 has zero pending Qs after the resolution, follow Phase 1 → Phase 2 in `[[ask]]`: delete `## Open Questions` H2, migrate accumulated `### Resolved` to a `## Resolved` H2 at the bottom.

For à la carte Qs (`{NAME} Q3: …`), the same path applies against `{NAME} Questions.md` instead of a feature doc.


## What `/triage` does NOT do

- Doesn't create new feature docs — that's `/groom`'s job.
- Doesn't move backlog items between H2s on its own (except via the verify-resolution path when the user says "F23 verified").
- Doesn't answer the questions or auto-resolve them — its job is surfacing.
- Doesn't write to feature docs except via the question-resolution path (when the user actually answered a Q).


## Compound usage: "triage and groom"

When the user says "triage and groom" (or "groom and then triage" — order in language doesn't matter), the Pilot runs `/groom` first to populate `[Questions]` state by parking new items, then `/triage` to surface the inbox. This is a Pilot-level natural-language interpretation, not a special flag or DMUX trigger — keeps both skills small.


## Idempotence

Strictly idempotent + destructive. The agent rewrites the entire `{NAME} Triage.md` body on every run. No marker comments, no preserve-user-edits regions — the whole file (below frontmatter) is agent-owned space. Running twice with no backlog change produces no diff on the second pass.


## Failure modes

- **No anchor found** — say "No anchor found from `{cwd}` upward." and stop.
- **No backlog file** — say "No `{NAME} Backlog.md` at `{expected path}`." and stop.
- **Empty body** — H1 banner is still written (TAG = `[]`); body is empty. Glance regardless.
- **Backlog item missing F-number** — render as `**F? — {Item Name}**` and surface the missing-number issue in the chat summary, but don't fix it inline (that's `/groom`'s job).


## Cross-references

- **`[[CAB Triage]]`** — file-format spec.
- **`[[CAB Questions]]`** — sibling à la carte facet.
- **`[[CAB Backlog]]`** — backlog format, F-numbering, status brackets, `[Verify]` semantics.
- **`[[ask]]`** — `## Open Questions` block format inside feature docs (the source of question text), and the writer for à la carte Qs.
- **`[[backlog-horizons]]`** — horizon H2s (Now / Next / Later) and the per-bucket count scheme.
- **`[[workflow]]`** — `[Questions]` / `[Verify]` / `[Done]` state semantics and transitions.
- **`/groom`** — pairs with triage; groom *creates* the question state by parking, triage *gathers* and surfaces it.
- **`/roster`** — counts every backlog item once per bucket; triage's H1 count line uses the same scheme so the two views agree.
