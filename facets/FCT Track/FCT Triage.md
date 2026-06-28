---
description: "triage — presentation form for an anchor's status inside the global Q.md dashboard"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Track]] → [FCT Triage](hook://p/FCT%20Triage)

# FCT Triage
Specification for the **Triage view** — the format and rules for rendering an anchor's status (banner, H2s, brackets) into its section of the global `~/ob/kmr/Q.md` dashboard.

**Related:** [[FCT Backlog]] (source of items), [[CAB Backlog]] (status brackets), [[SKA triage]] (renderer), [[FCT Query]] (anchor questions surface)
**Examples:** [[Q#CAE Triage\|CAE section (minimal)]],  [[Q#SKA Triage\|SKA section (fuller)]]

| Table of Contents |  |
|---|---|
| [[#Location]] |  |
| [[#No blank lines]] |  |
| [[#H1 line — the anchor's section heading inside Q.md]] |  |
| [[#Anchor TAG — cascading rule]] |  |
| [[#No anchor-level questions bullet]] |  |
| [[#Body H2s]] |  |
| [[#Bullet format — exact]] |  |
| [[#Status brackets — count and form]] |  |
| [[#Ordering within a body H2]] |  |
| [[#No meta prose, no breadcrumb, no Notes]] |  |
| [[#Agent-owned, destructively rewritten]] |  |
| [[#Lifecycle]] |  |
| [[#Relationship to other planning docs]] |  |
| **[[#BRIEF]]** |  |

**TLDR** — The Triage facet defines the *rendered format* of an anchor's status section inside `~/ob/kmr/Q.md`: the H1 banner (TAG, counts, exact spacing), body H2s (`## Active` … `## Later`, skipping empty), bullet form (bolded bracket + mandatory wiki-link + em-dash description), and the selective-Later rule (only `[Questions]`/`[Verify]` items surface under `## Later`). **Cardinality: one per anchor** — each anchor owns exactly one section in `Q.md`, destructively rewritten on each `/triage` run. No per-anchor file; the view lives only in `Q.md`.

**Presentation form — no per-anchor file location.** As of F075 (2026-05-19), per-anchor `{NAME} Triage.md` files are retired. The triage view is rendered into the anchor's per-anchor section of `~/ob/kmr/Q.md`, which is the single triage surface for the vault. This facet remains a real concept (the triage view of an anchor's state) and its format is specified here; it just no longer corresponds to a per-anchor file. **Anchor-page dispatch tables do NOT link to this facet** (there is no per-anchor file to link to). CAB-level references to `[[FCT Triage]]` (from `CAB Base.md`, this spec) remain — the facet definition is still a real artifact.

The Triage **view** is the **status of the anchor** — the single place the user looks to see "where everything stands and what wants my attention next." It lists items grouped by workflow-state H2: `## Active`, `## Ready`, `## Now`, `## Next`, and **selectively** `## Later`. Within each H2, items appear in **source order from the backlog** (per F028 Q2).

**Selective Later** (2026-05-20): Later items normally stay hidden — they're deferred and don't compete for attention. **Exception:** Later items carrying `[Questions]` or `[Verify]` brackets DO get surfaced under a `## Later` H2 in the body. The reason is a counting invariant — the H1 banner shows `Questions N` and `Verify N`; every counted Q or V must have a visible row the user can click. Without this exception, a `[Questions]` row in Later would inflate the banner count without giving the user a place to act on it.

**Icebox is never shown in the body** — only counted in the H1 banner (`Icebox N`).

Each anchor's section in Q.md is **agent-owned and destructively rewritten** on each `/triage` run (and on the participating-skill post-condition per F075 Q2 — `/groom`, `/mint`, `/finalize`, `/feature` Phase transitions, `/audit` finding-row writes).

**Working example:** SKA's section inside `~/ob/kmr/Q.md` — open it for a live rendered instance.

# Format Specification

## Location

**None — per-anchor.** The triage view is rendered into the anchor's section inside `~/ob/kmr/Q.md` (per F075). There is no per-anchor file. CAB-level dispatch tables continue to reference `[[FCT Triage]]` (this spec file); anchor-page dispatch tables do not.

## No blank lines

**No blank lines in the body.** Every line carries information; the user wants maximum signal density on a high-traffic surface. The single blank line between the YAML frontmatter and the H1 (rendered by the frontmatter delimiters) is the only whitespace.

## H1 line — the anchor's section heading inside Q.md

The section heading is a level-1 heading (the literal `# [` prefix is also the section-boundary marker the renderer scans for) of this exact form:

`# [<TAG>]  [[{NAME} queries|{NAME}]]  -  Ready N    Questions N   |   Now N    Next N    Later N    Verify N    Icebox N`

**Link form** (per F176, supersedes F075 Q1's heading-anchor form): `[[{NAME} queries|{NAME}]]` — links to the anchor's `{NAME} queries.md` drain page (where the user actually answers questions), display text `{NAME}`. Fallback chain when that file doesn't exist yet: `{NAME} queries` → `{NAME} Triage` → `{NAME}` → plain text (avoids emitting a dead link).

**Spacing — lock exact** (per F028 Q6):
- Two spaces between `[<TAG>]` and the link.
- **Three spaces around the `-`** separating the link from the counts.
- **Four spaces between counts within a group**.
- **Three-space-pipe-three-space (`   |   `)** between the two headline numbers and the horizon group.

**Two headline numbers + a horizon group** (per the 2026-05-24 banner simplification — each headline number MERGES two states):
1. **Ready** (agent-actionable) — `[Active]` + `[Ready]` rows summed, **including the `[Agreed]` feature-lifecycle synonym for Ready**. The body H2s still render `## Active` and `## Ready` separately.
2. **Questions** (user-actionable) — pending `Q<n>` across feature docs whose rows carry `[Questions]`, **plus `[Verify]`-bracket rows**, summed. The body still surfaces `[Verify]` and `[N Questions]` rows separately.
3. **Horizon group** — `Now`, `Next`, `Later`, `Verify`, `Icebox`: raw per-H2 bullet counts (placement, not state).

**Counts:**
- `Ready` (headline) — count of `[Active]` + `[Ready]` + `[Agreed]` rows in the active horizons (`## Active` / `## Ready` / `## Now` / `## Next`).
- `Questions` (headline) — pending `Q<n>` across feature docs with `[Questions]` rows in the active horizons, plus `[Verify]`-bracket rows in those horizons, summed.
- `Now`, `Next`, `Later`, `Verify` (horizon) — bullets under each backlog H2, one count each, excluding `[Done]`-bracketed rows. (`Verify` here is the `## Verify` H2 count, distinct from the `[Verify]`-bracket rows folded into the headline `Questions`.)
- `Icebox` — bullets in `{NAME} Icebox.md` if it exists; else 0.

## Anchor TAG — cascading rule

Decide the H1 TAG by checking in order; the first match wins, except U and A combine:

| TAG | When |
|---|---|
| `[U]` | Anchor has any `[Questions]` or `[Verify]` items (user-actionable). |
| `[A]` | Anchor has any `[Active]` or `[Ready]` items (agent-actionable). |
| `[U+A]` | Both U and A apply (combine; literal `+`). |
| `[G]` | No U, no A; anchor has items in `## Now` or `## Next` (groomable). |
| `[-]` | No U, A, G; anchor has items in `## Later`. |
| `[]` | Nothing anywhere. Empty brackets, literal `[]`. |

## No anchor-level questions bullet

Triage carries **no** questions bullet under the H1. Anchor-level (non-feature) questions are authored directly in `{NAME} queries.md` § `## Questions` (per `[[FCT Query]]`) — there is no separate questions facet, and triage does not surface or count them. The H1 already links to `[[{NAME} queries]]`, which is where those questions live.

## Body H2s

Body H2s, in this fixed order: `## Active`, `## Ready`, `## Now`, `## Next`, `## Later`. Sections with zero qualifying items are **omitted entirely** (no empty H2).

**Qualification rule** (which items render under each H2):

- For `## Active`, `## Ready`, `## Now`, `## Next` — every item in that backlog H2 qualifies (except `[Done]`-bracketed stale rows; `/groom` migrates those).
- For `## Later` — **only items carrying `[Questions]` or `[Verify]` brackets qualify** (selective surfacing, 2026-05-20). Rationale: every banner Q or V count must correspond to a visible row the user can click. Later items without those brackets stay hidden — they're deferred and don't compete for attention.

**`## Icebox` is never rendered** in the body — only counted in the H1 banner.

If the anchor has zero items in Active/Ready/Now/Next, the body is just the H1 (and possibly the à la carte bullet line). No explanatory prose.

## Bullet format — exact

Each bullet is one line, with **a wiki-link as the title — mandatory, no exceptions, every row class**. The three row-class forms (literal templates):

- `- **[<status>]** [[F<n> — Title]] — description.` — feature row
- `- **[<status>]** [[{NAME} Backlog#B<n>|B<n>]] — description.` — backlog-only B-row
- `- **[<status>]** [[YYYY-MM-DD Title]] — description.` — bug/ad-hoc with its own doc

- **Bracket bolded** — `**[Active]**`, `**[Ready]**`, `**[Verify]**`, `**[Questions]**` (or `**[N Questions]**` / `**[N Ready]**` / `**[N Verify]**` when count > 1).
- **One space** between the bracket and the wiki-link. The wiki-link is **not** bold.
- **One em-dash with single spaces** (` — `) before the description.
- **Description ends with a period.** Same as backlog convention.

**Mandatory wiki-link — every row.** The row title MUST be a wiki-link. **No row class has an inline-bold-only escape hatch.** The row IS the link, not just a description: the user navigates *through* triage to the source; a row without a link is a broken row. Three link forms by row class:

- **Feature rows (`F<n>`)** → `[[F<n> — Title]]` to the feature doc. Even when the feature doc doesn't exist yet (broken link = useful signal).
- **Backlog rows (`B<n>`, ad-hoc tasks named only in the backlog)** → `[[{NAME} Backlog#B<n>|B<n>]]`. Every B-identifier has a stable anchor in the backlog file, so this link form ALWAYS resolves.
- **Bug rows with their own doc** → link to that doc. Fall back to `[[{NAME} Backlog#<id>|<id>]]` when no separate doc exists.

The renderer-side enforcement of this rule lives in `[[SKA triage]]` § Mandatory wiki-link.

**Verify items: one-line text + `(details)` link.** The bracket wiki-link `[[F<n> — Title]]` already links to the whole feature doc; if the feature doc has a detailed `## Verify` section, **append `([[F<n> — Title#Verify|details]])`** at the end of the line so the user can click straight to the verification details. **No indented sub-bullets** for extended verify text — link to the section instead. The one-line summary is usually enough; the link is there when more is needed.

Example: `- **[Verify]** [[F007 — Webhook Notifications]] — Webhook fires on task completion. ([[F007 — Webhook Notifications#Verify|details]])`

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

Each anchor's section inside Q.md is agent-owned. Every `/triage` run — or post-condition run by `/groom`, `/mint`, `/finalize`, `/feature` (Phase transitions), or `/audit` (finding-row writes) — regenerates the section from scratch by walking the backlog, removes the existing section from Q.md, and inserts the new one at the top of Q.md (bubble-to-top). There are no marker comments, no preserve-user-edits regions inside the section.

## Lifecycle

- **Created on first `/triage` (or à la carte `/query`) run** — the anchor's section is inserted at the top of Q.md if absent.
- **Rewritten + bubbled-to-top** on every subsequent participating-skill run.
- **Removed from Q.md entirely** when the anchor has TAG `[]` (zero items anywhere).
- **Glanced at end of an active-mode run** — but the glance target is `~/ob/kmr/Q.md`, not any per-anchor file. See `[[SKA triage]]` § 7.

## Relationship to other planning docs

- **[[CAB Backlog]]** — source of truth for what's in flight, including item ordering. Triage filters/lists the backlog rows (excluding Later/Icebox) and applies the bracket-form rules. The backlog file is NOT reordered by triage; bubble-to-top happens only in Q.md (per F075 Q2).
- **`## Open Questions` blocks inside feature docs** (per `[[FCT Query]]`) — source of truth for question text. Triage points at them via wiki-link to the feature doc; it doesn't duplicate the Q content.
- **`{NAME} queries.md` § `## Questions`** (per `[[FCT Query]]`) — where anchor-level (non-feature) questions are authored directly. Triage neither counts nor surfaces them; they reach the user via the H1 link to the queries page.
- **`/roster`** — counts every item once per backlog H2; triage's H1 banner uses the same scheme so the two views agree.
- **`~/ob/kmr/Q.md`** — the single triage surface (per F075). Each anchor's per-anchor section here IS the triage view; it lives nowhere else.
- **Anchor pages (`{NAME}.md`)** — do **not** carry a dispatch-table row pointing at this facet, since no per-anchor file exists to link to. The anchor's Q.md section is reached via the global dashboard, not via per-anchor navigation.

# RULESET R-fct-triage
include::
where:: context: Q.md anchor-sections
description:: Rules for the triage view rendered into each anchor's section of `~/ob/kmr/Q.md`. Governs the H1 banner format, body H2 inclusion, bullet form, and the selective-Later invariant. Cardinality: **one per anchor** — each anchor owns exactly one section in Q.md.

### RULE R-fct-triage-01 — H1 banner has exact spacing (checked)
The H1 section heading follows the form `# [<TAG>]  [[Q#{NAME} Triage|{NAME} Triage]]   -   <count groups>` with: two spaces between TAG and the link; three spaces around the `-` separator; four spaces between counts within a group; `   |   ` (three-space-pipe-three-space) between the three count groups (User-actionable / Agent-actionable / Horizon).
**Check pattern:** H1 matches the prescribed spacing pattern — deviations (single spaces, missing pipe groups) are a failure.
**Why:** the renderer (`[[SKA triage]]`) references the exact spacing; relaxing it silently breaks the renderer.

### RULE R-fct-triage-02 — Every bullet title is a wiki-link (checked)
Every body bullet's title MUST be a wiki-link — `[[F<n> — Title]]` for feature rows, `[[{NAME} Backlog#B<n>|B<n>]]` for backlog-only rows, or a bug-doc link — with no exceptions. A row without a wiki-link is a broken row.
**Check pattern:** each `-` bullet starts with `**[<status>]** [[` — any bullet missing the `[[` link-open is a failure.
**Why:** triage is navigation; a row without a link leaves the user with no path to the source.

### RULE R-fct-triage-03 — Selective Later: only [Questions]/[Verify] items render (checked)
Under `## Later`, only items carrying a `[Questions]` or `[Verify]` bracket qualify. Later items without those brackets are omitted. If no Later item qualifies, the `## Later` H2 is omitted entirely.
**Check pattern:** every row under `## Later` has a bolded `[Questions]`, `[N Questions]`, `[Verify]`, or `[N Verify]` bracket; the `## Later` H2 is absent when zero qualify.
**Why:** a counting invariant — the H1 banner's `Questions N` and `Verify N` counts must each have a clickable row; surfacing all Later items would clutter a high-traffic surface.

### RULE R-fct-triage-04 — Empty H2s are omitted (checked)
Any body H2 (`## Active`, `## Ready`, `## Now`, `## Next`, `## Later`) with zero qualifying items is omitted entirely. The `## Icebox` H2 is never rendered (counted only in the banner).
**Check pattern:** the rendered section has no `## <H2>` immediately followed by another `## ` or end-of-section without at least one bullet.
**Why:** empty H2s add noise on a high-density, no-blank-lines surface.

# BRIEF

- **This file is the CAB facet spec for the Triage view** — it defines format, H1 banner shape, count groups, anchor TAG cascading rule, body H2 ordering, bullet form, and qualifies which items render. Authority for triage rendering lives here; `[[SKA triage]]` is the renderer that enforces these rules.
- **NOT for per-anchor triage content.** As of F075 (2026-05-19), per-anchor `{NAME} Triage.md` files are retired — the view renders into the anchor's section of `~/ob/kmr/Q.md`. Do not re-introduce per-anchor file conventions here; do not document per-anchor file locations.
- **Inclusion test for new format rules.** A rule belongs here only if it concerns *how the triage view is rendered* (banner spacing, bracket forms, ordering, qualification). Rules about *how to write to Q.md* (script behavior, idempotence, file write mechanics) belong in `[[SKA triage]]`. Rules about *what items mean* (workflow states, brackets like `[Verify]`) belong in `[[CAB Backlog]]` or `[[workflow]]`.
- **Load-bearing: exact spacing in the H1 banner.** The two-space / three-space-around-dash / four-space-within-group / three-space-pipe-three-space scheme (per F028 Q6) is referenced by the renderer; do not relax to "use any whitespace" without updating `[[SKA triage]]` in lockstep.
- **Load-bearing: the mandatory wiki-link rule for every row.** Every triage bullet's title MUST be a wiki-link (feature doc, backlog heading-anchor, or bug doc). Removing this constraint breaks user navigation through triage; the renderer enforces it via `[[SKA triage]]` § Mandatory wiki-link.
- **Selective Later is a counting invariant, not a style choice.** Later items with `[Questions]` or `[Verify]` brackets MUST surface under `## Later` because every banner Q/V count needs a clickable row. Do not "clean up" by hiding all Later items — that breaks the count-vs-row correspondence.
- **No inline reference example** — a facet spec must not embed a rendered sample instance. The canonical shape lives in the literal inline-code templates under `# Format Specification` (H1 banner, bullet form — inline code, never fenced, so the linter's no-markdown-in-fences rule is satisfied while the placeholders stay literal); the live rendered instance is the **Working example** (SKA's section in `~/ob/kmr/Q.md`). Keep the Format Specification templates in lockstep with the renderer `[[SKA triage]]`.
