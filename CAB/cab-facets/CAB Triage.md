---
description: triage inbox — status of the anchor, with all items except Later/Icebox surfaced one line each
---
# CAB Triage

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Triage.md`


The Triage file is the **status of the anchor** — the single place the user looks to see "where everything stands and what wants my attention next." It lists every item in the anchor's backlog **except** items in `## Later` and `## Icebox` (those are explicitly deferred and are counted in the H1 banner only). The body is grouped by workflow-state H2: `## Active`, `## Ready`, `## Now`, `## Next`. Within each H2, items appear in **source order from the backlog** (per F028 Q2). The whole file is **agent-owned and destructively rewritten** on each `/ask` or `/triage` run.

Triage is the *inbox at the anchor scope*. The vault-level *Agent Status dashboard* lives at `~/ob/kmr/Q.md`; both `/ask` and `/triage` regenerate the anchor's per-anchor section there on every invocation (per F25, format updated by F28).

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Triage.md`.

# Reference Example
---

```markdown
---
description: triage inbox (agent-owned)
---

# [U+A]  [[CAE]] Triage  -  Questions 2    Verify 1   |   Active 1    Ready 1   |   Now 2    Next 1    Later 1    Icebox 0
- **[3 Questions]**  [[CAE Questions]]
## Active
- **[Active]** [[F001 — Cron Syntax]] — Cron expressions for recurring task schedules.
## Ready
- **[Ready]** [[F003 — Retry Backoff Polish]] — Tune exponential-backoff caps after user feedback.
## Now
- **[4 Questions]** [[F002 Task Groups]] — Rendering of task groups.
- **[Verify]** [[F007 — Webhook Notifications]] — Webhook fires on task completion. ([[F007 — Webhook Notifications#Verify|details]])
## Next
- **[5 Questions]** [[F004 Priority Levels]] — 2 pending Qs (Q1, Q3).
- **[3 Ready]** [[F017 Update Backing Store]] — Milestone-style F with three independent ready sub-items.
```

---



# Format Specification

## Location

`{NAME} Triage.md` lives in `{NAME} Docs/{NAME} Plan/`.


## No blank lines

**No blank lines in the body.** Every line carries information; the user wants maximum signal density on a high-traffic surface. The single blank line between the YAML frontmatter and the H1 (rendered by the frontmatter delimiters) is the only whitespace.


## H1 banner

```
# [<TAG>]  [[{NAME}]] Triage  -  Questions N    Verify N   |   Active N    Ready N   |   Now N    Next N    Later N    Icebox N
```

**Spacing — lock exact** (per F028 Q6):
- Two spaces between `[<TAG>]` and `[[{NAME}]]`.
- One space after `[[{NAME}]]` and before `Triage`.
- **Three spaces around the `-`** separating "Triage" from the count groups.
- **Four spaces between counts within a group**.
- **Three-space-pipe-three-space (`   |   `)** between the three count groups.

**Three count groups, in order:**
1. **User-actionable** — `Questions N    Verify N`
2. **Agent-actionable** — `Active N    Ready N`
3. **Horizon** — `Now N    Next N    Later N    Icebox N`

**Counts:**
- `Questions` — sum of pending `Q<n>` across all feature docs that have rows in `## Active` / `## Ready` / `## Now` / `## Next` (i.e., not Later or Icebox), plus pending `Q<n>` in `{NAME} Questions.md` (the new à la carte facet).
- `Verify` — bullets across `## Active` / `## Ready` / `## Now` / `## Next` with the `[Verify]` bracket.
- `Active`, `Ready`, `Now`, `Next`, `Later` — bullets under each backlog H2 (one count each).
- `Icebox` — bullets in `{NAME} Icebox.md` if it exists; else 0.


## Anchor TAG — cascading rule

Decide the H1 TAG by checking in order; the first match wins, except U and A combine:

| TAG | When |
|---|---|
| `[U]` | Anchor has any `[Questions]` or `[Verify]` items (user-actionable). |
| `[A]` | Anchor has any `[Active]` or `[Ready]` items (agent-actionable). |
| `[U+A]` | Both U and A apply (combine; literal `+`). |
| `[G]` | No U, no A; anchor has items in `## Now` or `## Next` (groomable). |
| `[?]` | No U, A, G; anchor has items in `## Later`. |
| `[]` | Nothing anywhere. Empty brackets, literal `[]`. |


## À la carte bullet — directly under H1

If `{NAME} Questions.md` has any pending Qs, add **one line** directly under the H1 (no blank line, no H2 wrapper):

```
- **[N Questions]**  [[{NAME} Questions]]
```

Two spaces between `**[N Questions]**` and the wiki-link (matches the user's reference example). Bracket form: `**[Questions]**` for N=1, `**[N Questions]**` for N>1. Omitted entirely when there are zero pending à la carte Qs.

The legacy `## À la carte` H2 inside `{NAME} Triage.md` is **removed** (per F28). À la carte content lives in `[[CAB Questions]]` now.


## Body H2s

Body H2s, in this fixed order: `## Active`, `## Ready`, `## Now`, `## Next`. Sections with zero qualifying items are **omitted entirely** (no empty H2). `## Later` and `## Icebox` items are **never listed** in the body — only counted in the H1 banner.

If the anchor has zero items in Active/Ready/Now/Next, the body is just the H1 (and possibly the à la carte bullet line). No explanatory prose.


## Bullet format — exact

Each bullet is one line:

```
- **[<status>]** [[F<n> Title]] — description.
```

- **Bracket bolded** — `**[Active]**`, `**[Ready]**`, `**[Verify]**`, `**[Questions]**` (or `**[N Questions]**` / `**[N Ready]**` / `**[N Verify]**` when count > 1).
- **One space** between the bracket and the wiki-link. The wiki-link is **not** bold.
- **One em-dash with single spaces** (` — `) before the description.
- **Description ends with a period.** Same as backlog convention.

**Verify items: one-line text + `(details)` link.** The bracket wiki-link `[[F<n> Title]]` already links to the whole feature doc; if the feature doc has a detailed `## Verify` section, **append `([[F<n> Title#Verify|details]])`** at the end of the line so the user can click straight to the verification details. **No indented sub-bullets** for extended verify text — link to the section instead. The one-line summary is usually enough; the link is there when more is needed.

```
- **[Verify]** [[F007 — Webhook Notifications]] — Webhook fires on task completion. ([[F007 — Webhook Notifications#Verify|details]])
```


## Status brackets — count and form

| Form | When |
|---|---|
| `**[Questions]**` | Single pending question (count omitted; rare — usually multiples). |
| `**[N Questions]**` | N pending questions in the feature doc's `## Open Questions` block (N > 1). |
| `**[Verify]**` | Single verification needed. Verify text inlines as the description (and may extend to a sub-bullet). |
| `**[N Verify]**` | N independent verification items (rare). When N is large, verify items live in the feature doc's `## Open Questions` § Verify subsection (parallel to Questions); the Triage just links. |
| `**[Ready]**` | Single feature ready to mint. |
| `**[N Ready]**` | Milestone-style F with N independent sub-items in its roadmap, all ready. |
| `**[Active]**` | In flight (a worker is currently minting). |
| `**[Designing]**`, `**[Blocked]**` | Reserved — typically not surfaced in Triage body since they're not user/agent-actionable now. |


## Ordering within a body H2

**Source order from the backlog** (per F028 Q2): items appear in the order they appear in `{NAME} Backlog.md` under the same H2. The backlog is the source of truth for ordering; the user reorders by editing the backlog (or asking the agent to). The H1 banner already counts items by status, so re-grouping by status inside H2s is redundant.


## No meta prose, no breadcrumb, no Notes

- **No "this file is maintained by..."** explanatory prose. The user knows what the page is.
- **No `:>>` breadcrumb above the H1** — the H1 wiki-link to the anchor is the navigation.
- **No `# Notes` H1** — anything the user wants to persist belongs in the relevant feature doc, not this scratch file.


## Agent-owned, destructively rewritten

The whole file (below the YAML frontmatter) is agent-owned. Every `/ask` or `/triage` run regenerates it from scratch by walking the backlog. There are no marker comments, no preserve-user-edits regions.


## Lifecycle

- **Created on first `/triage` (or à la carte `/ask`) run.** The file is generated at `{NAME} Docs/{NAME} Plan/{NAME} Triage.md` if absent.
- **Rewritten on every subsequent `/ask` / `/triage` run** (strictly idempotent + destructive).
- **Glanced at end of an active-mode run** so the user sees the inbox after the regen completes.


## Relationship to other planning docs

- **[[CAB Backlog]]** — source of truth for what's in flight, including item ordering. Triage filters/lists the backlog rows (excluding Later/Icebox) and applies the bracket-form rules.
- **`## Open Questions` blocks inside feature docs** (per `[[ask]]`) — source of truth for question text. Triage points at them via wiki-link to the feature doc; it doesn't duplicate the Q content.
- **[[CAB Questions]]** — sibling facet for à la carte Qs. Triage carries the count + link bullet directly under H1; the Questions facet holds the actual Q content.
- **`/roster`** — counts every item once per backlog H2; triage's H1 banner uses the same scheme so the two views agree.
- **`~/ob/kmr/Q.md`** — vault-level Agent Status dashboard. Each anchor's per-anchor section in Q.md is **identical content** to that anchor's Triage body (per F028 Q3), with the slug-prefix becoming a wiki-link via `[[NAME Triage|NAME]]` syntax.
