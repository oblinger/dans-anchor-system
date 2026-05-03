---
name: triage
description: >
  Surface every item across the current anchor that requires user
  involvement — pending questions in feature docs and items in `[Verify]`
  state — into one batched inbox at `{NAME} Docs/{NAME} Plan/{NAME} Triage.md`.
  Mirrors the backlog's horizon structure (Now / Next / Later); filters
  to items in `[Questions]` or `[Verify]` state; copies backlog-row
  description text verbatim for verify items. The user can answer with
  shorthand like "F5 Q4: yes" (resolves a question) or "verified F23"
  (moves the item to `## Done` and updates the feature-doc Status).
  Use when the user types `/triage`, says `triage` (DMUX prefix-trigger
  auto-prefixes `/triage`), or sends `"` (a single double-quote) as the
  entire message.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Triage — Inbox of Items Needing User Input

Generate the agent-owned triage file at `{NAME} Docs/{NAME} Plan/{NAME} Triage.md`. Walks the anchor's backlog, finds every item in `[Questions]` or `[Verify]` state, and writes a single agent-owned file the user reads to see "everything currently waiting on me."

DMUX trigger: **`triage`** (prefix-trigger; speaking `triage` stashes `/triage`, parallel to `snip` / `commission` / `fortify` / `groom`). Also: **`"`** (a single double-quote as the entire message), parallel to `crank`/`'` and `/land`/`.`. Slash invocation: `/triage`, `/triage roadmap`, `/triage milestone {N}`.


## When to Use

- User types `/triage`, says `triage` (DMUX auto-prefixes), or sends `"` as the entire message.
- User says "triage and groom" or "groom and then triage" (Pilot interprets as run `/groom` first, then `/triage`).
- User asks "what's waiting on me" / "what do you need from me" / "show the inbox".
- After `/groom` parks one or more items in feature docs (some flows naturally chain `/groom` → `/triage`).


## Definition of "needing user input"

An item needs user input if and only if its workflow state is one of:

- **`[Questions]`** — the bullet's description has a `→ [[Feature Doc]]` link to a feature doc whose `## Open Questions` block has at least one pending question (per `[[ask]]`).
- **`[Verify]`** — the bullet has the `[Verify]` bracket (verify items live in their horizon H2, per `[[CAB Backlog]]` § Verify is a status, not a section).

Everything else — `[ ]`, `[Designing]`, `[Blocked]`, `[Ready]`, `[Active]`, `[Done]` — is hidden from the body but counted in the H1 banner.


## Sources & invocation

| Invocation | Scope |
| --- | --- |
| `/triage` (or `triage` spoken, or `"` alone) | Default — walk `{NAME} Backlog.md`. |
| `/triage roadmap` | Walk the next milestone of `{NAME} Roadmap.md` (each milestone has its own backlog-shaped block). |
| `/triage milestone {N}` | Walk a named roadmap milestone. |
| `/triage icebox` | Walk `{NAME} Icebox.md` instead. Default scope (bare `/triage`) excludes the icebox per `[[workflow]]` § Active-work invariant; explicit invocation surfaces iced items needing input. |

Argument shape parallels `/groom`. Items in the icebox (`{NAME} Icebox.md`) are *not* surfaced by triage — Icebox items are explicitly parked, with feature docs that have open questions; the invariant says they don't compete for attention.


## Output file format — `{NAME} Triage.md`

Authoritative spec: `[[CAB Triage]]`. Summary:

```markdown
---
description: triage inbox (agent-owned)
---


# [[{NAME}]] Triage   -   Active: N    Ready: N    Now: N    Next: N    Later: N    Questions: N    Verify: N    Icebox: N


## À la carte

- **A1 — {short name}** — {full question text}. **Recommendation:** Lean (B). {one-line reason}.

## Now

- **F{n} — {Item Name}** [Questions] — → [[F{n} — {Item Name}]] — {N} pending Qs ({Q1, Q2, …}).
- **F{n} — {Item Name}** [Verify] — {verify-plan text copied verbatim from the backlog row}. → [[F{n} — Feature]] · [[agent-artifact]] · [[SKL <X>]].

## Next

- {as above for ## Next}

## Later

- {as above for ## Later}
```

**H1 banner — the count line.** Three spaces around the `-` separating "Triage" from the counts; four spaces between successive counts. Counts come from `/roster`'s per-bucket scheme (one count per H2; `Verify` is bracket-derived; `Icebox` from `{NAME} Icebox.md` if it exists).

**Body — horizon H2s only.** No `## Active`, `## Ready`, `## Verify`, or `## Done` sections in the body — those are workflow-state H2s in the backlog, but in triage we only need user-input items grouped by where they live in the horizon H2s. Items with `[Verify]` bracket appear in their horizon (typically `## Now`).

**Sections with no qualifying items are omitted** from the body. If the entire anchor has zero `[Questions]` and zero `[Verify]` items, the body is empty — print just the H1 banner + a one-liner "_Nothing currently waiting on you._"

**À la carte** is for anchor-level / cross-cutting / agent-raised questions (no backlog row). Use prefix `Q{n}` — same prefix as feature-attached Qs but in its own per-anchor namespace (lowest unused integer; never recycled). Show full Q text inline. À la carte questions surface only when the agent genuinely needs user input AND isn't fairly confident of the answer (per F13 Q6). The colloquial name "à la carte" stays so the user can refer to them in conversation ("the SKA à la carte questions").


## Runbook

### 1. Locate the source

- Walk up from `cwd` to find `.anchor`. If none, say "No anchor found from `{cwd}` upward." and stop.
- Read `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`. If absent, say so and stop.
- Note `{NAME} Icebox.md` for the Icebox count (zero if absent).
- Resolve the target file: `{NAME} Docs/{NAME} Plan/{NAME} Triage.md` (create if absent).

### 2. Compute the count line

Walk every bullet in the backlog. Partition into the per-roster scheme (one count per H2):
- `Active` — bullets under `## Active`
- `Ready` — bullets under `## Ready`
- `Now` / `Next` / `Later` — bullets under each horizon H2
- `Questions` — count of bullets with `[Questions]` bracket across `## Active`, `## Ready`, `## Now`, `## Next` only. **`## Later` is excluded** — Later items are explicitly deferred attention; their questions don't belong in the inbox until they're promoted. (Items with `[Questions]` in `## Later` are still listed under `Later`'s H2 count, just not added to `Questions`.)
- `Verify` — count of bullets across all horizon H2s with `[Verify]` bracket. Items counted as `Questions` or `Verify` are *also* counted under their horizon H2 — these are bracket-derived overlays, not partitions. See `[[backlog-horizons]]` for the rule.
- `Icebox` — bullets in `{NAME} Icebox.md`

`## Done` and `## Legwork` are excluded.

### 3. Filter to triage-eligible items

For each bullet across all horizon H2s:
- If bracket is `[Questions]` → include. The description should already be `→ [[Feature Doc]]`. Open the feature doc, count pending Qs in its `## Open Questions` block (children of pending parents count if they're separate top-level Qs; sub-bullets under a parent don't add to the count). Render as:
  ```
  - **F{n} — {Item Name}** [Questions] — → [[F{n} — {Item Name}]] — {N} pending Qs ({Q1, Q3, …}).
  ```
- If bracket is `[Verify]` → include. Copy the backlog row's **description text verbatim** (the verify-plan text written when the item was set to `[Verify]`). Render as:
  ```
  - **F{n} — {Item Name}** [Verify] — {description text from backlog}.
  ```

Items with any other bracket are skipped.

### 4. Compute à la carte questions

Only include if the agent has genuine user-input questions that don't belong to any backlog row. Strong bias toward NOT raising (per F13 Q6). When in doubt: answer it yourself or put it in a feature doc.

### 5. Destructively rewrite `{NAME} Triage.md`

Replace the entire file (preserving only the YAML frontmatter, with `description: triage inbox (agent-owned)`). Body order:
- H1 banner
- `## À la carte` (only if any à la carte Qs — Q-numbered per F25 Q5/Q8)
- `## Now` (only if any qualifying items)
- `## Next` (only if any qualifying items)
- `## Later` (only if any qualifying items)

Within each H2, preserve source order from the backlog. Insert one blank line between bullets.

### 6. Regenerate the anchor's H2 in `~/ob/kmr/Q.md`

**This is the new step F25 added to triage.** After regenerating `{NAME} Triage.md`, also regenerate the anchor's H2 entry in the vault-level Agent Status dashboard at `~/ob/kmr/Q.md`. Logic is identical to `ask/SKILL.md` step 5 (the canonical reference). Summary:

1. Count pending Qs (sum across feature docs + à la carte block) and Ready items (count under `## Ready` in `{NAME} Backlog.md`).
2. If both = 0: remove any `## QUESTIONS — {NAME}` or `## READY — {NAME}` H2 from `Q.md`. Done.
3. Otherwise: build `## {PREFIX} — {NAME} — [[{NAME}]] · [[{NAME} Triage]] — {summary tail}` (PREFIX = `QUESTIONS` if pending ≥ 1 else `READY`). Body for QUESTIONS: à la carte bare bullets first, then `### F<n>` H3s. Body for READY: empty. Apply 12-line soft cap with overflow pointer.
4. Remove any stale H2 for this anchor; insert the new one at the top of Q.md (move-to-front, always, regardless of body change).
5. Refresh H1 banner: `# Agent Status   -   Questions: N    Ready: M` (anchor counts).

See `ask/SKILL.md` § 5 for the full spec and example layout. Both `/ask` and `/triage` produce a fresh Q.md anchor H2 on every invocation.

### 7. Glance the file

Always glance the file after the regen completes:

```bash
open "{NAME} Docs/{NAME} Plan/{NAME} Triage.md"
```

This is the natural close of a triage run — the user sees the inbox immediately. (Per `[[ask]]` the glance is allowed: the agent has just modified the file with new state, and the user is in active mode by virtue of having invoked `/triage`.)

### 8. Print a one-line summary in chat

```
/triage — {NAME}: {N} items waiting on you ({Q} pending questions, {V} verify). Refreshed {NAME} Triage and Q.md.
```

Where `Q` is the count of `[Questions]` items and `V` is the count of `[Verify]` items in the body.


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
- **Empty body** — H1 banner is still written; body has a single `_Nothing currently waiting on you._` line. Glance regardless.
- **Backlog item missing F-number** — render as `**F? — {Item Name}**` and surface the missing-number issue in the chat summary, but don't fix it inline (that's `/groom`'s job).


## Cross-references

- **`[[CAB Triage]]`** — file-format spec.
- **`[[CAB Backlog]]`** — backlog format, F-numbering, status brackets, `[Verify]` semantics.
- **`[[ask]]`** — `## Open Questions` block format inside feature docs (the source of question text).
- **`[[backlog-horizons]]`** — horizon H2s (Now / Next / Later) and the per-bucket count scheme.
- **`[[workflow]]`** — `[Questions]` / `[Verify]` / `[Done]` state semantics and transitions.
- **`/groom`** — pairs with triage; groom *creates* the question state by parking, triage *gathers* and surfaces it.
- **`/roster`** — counts every backlog item once per bucket; triage's H1 count line uses the same scheme so the two views agree.
