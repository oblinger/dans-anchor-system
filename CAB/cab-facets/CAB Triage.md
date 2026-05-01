---
description: triage inbox — items across the anchor that need user input (pending Qs and verifications)
---
# CAB Triage

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Triage.md`


The Triage file is the single place the user looks to see "everything currently waiting on me" — pending questions in feature docs and items in `[Verify]` state awaiting user verification. The file is **agent-owned and destructively rewritten** on each `/triage` run; the user reads it and responds with shorthand like "F5 Q4: yes" or "verified F23".

Triage is the *inbox*; per-feature `## Open Questions` blocks (per `[[ask-questions]]`) and `[Verify]` brackets on backlog rows (per `[[CAB Backlog]]`) are the *source of truth*. Triage just gathers them.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Triage.md` — Triage.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

```markdown
---
description: triage inbox (agent-owned)
---


# [[CAE]] Triage   -   Active: 1    Ready: 2    Now: 3    Next: 1    Later: 0    Verify: 1    Icebox: 4


## Now

- **F2 — Task groups** [Questions] — → [[F2 — Task Groups]] — 3 pending Qs (Q1, Q2, Q3).
- **F7 — Webhook notifications** [Verify] — Webhook fires on task completion. Verify by triggering a test job and confirming POST payload (see [[CAE PRD]] § Webhooks). → [[F7 — Webhook Notifications]] · [[CAE PRD]].

## Next

- **F4 — Priority levels** [Questions] — → [[F4 — Priority Levels]] — 5 pending Qs.
```

---



# Format Specification

## Location

`{NAME} Triage.md` lives in `{NAME} Docs/{NAME} Plan/`.


## Document Structure

### Single H1 with embedded counts

The H1 carries everything the user needs at a glance — a wiki-link to the anchor, the literal word "Triage", and the per-bucket count line:

```
# [[{NAME}]] Triage   -   Active: N    Ready: N    Now: N    Next: N    Later: N    Questions: N    Verify: N    Icebox: N
```

- **Wiki-link to the anchor** — `[[{NAME}]]` so the user can click through to the anchor page from the triage view.
- **Literal "Triage"** — labels what the file is.
- **Inline count line** — same per-bucket structure as `/roster`'s output (per `[[backlog-horizons]]`). Order: `Active`, `Ready`, `Now`, `Next`, `Later`, `Questions`, `Verify`, `Icebox`. The first five are H2 partitions (each item appears in exactly one). The next two — `Questions` and `Verify` — are bracket-derived overlays (`Questions` excludes `## Later`; `Verify` includes all horizon H2s). `Icebox` is a separate-file tail. Big and visible at the top of the file.
- **Spacing convention** — three spaces around the `-` separating "Triage" from the counts; four spaces between successive counts. The wide spacing keeps the line scannable as a banner instead of a paragraph.

### Body — horizon H2s, filtered to user-input items

Below the H1, the body mirrors the backlog's horizon H2s (`## Now`, `## Next`, `## Later`) — per `[[backlog-horizons]]` and the `/triage` skill design (F13). Only items in `[Questions]` or `[Verify]` state appear; everything else is hidden but still counted in the H1 line.

Each entry preserves the source backlog-row text. For `[Verify]` items, the description text **is** the verify-plan instructions (per F13 Q11) — what was implemented, what to check, with up to three wiki-links at the end (`[[F<n> — Feature]] · [[agent-artifact]] · [[SKL <X>]]`). For `[Questions]` items, the description collapses to `→ [[Feature Doc]] — N pending Qs (Qx, Qy, …)`.

À la carte questions (agent-raised, no backlog row) appear under their own `## À la carte` H2 above the horizon sections.

### No breadcrumb, no Notes section

Earlier drafts of this file had a `:>>` breadcrumb above the H1 and a separate `# Notes` H1 for user-owned content. Both are gone. The breadcrumb is redundant once the wiki-link in the H1 carries the anchor connection; the Notes section was unnecessary because the file is purely a triage view — anything the user wants to add belongs in the relevant feature doc, not in this scratch file.

### Agent-owned, destructively rewritten

The whole file (below the YAML frontmatter) is agent-owned. Every `/triage` run regenerates it from scratch by walking the backlog. There are no marker comments, no preserve-user-edits regions — if the user wants persistent content, it goes in a feature doc or other anchor surface, not here.


## Lifecycle

- **Created on first `/triage` run.** The file is generated at `{NAME} Docs/{NAME} Plan/{NAME} Triage.md` if absent.
- **Rewritten on every subsequent `/triage` run** (per F13 Q9: strictly idempotent + destructive).
- **Glanced at end of run** so the user sees the inbox after the regen completes.


## Relationship to other planning docs

- **[[CAB Backlog]]** — source of truth for what's in flight. Triage filters the backlog rows to those needing user input.
- **`## Open Questions` blocks inside feature docs** (per `[[ask-questions]]`) — source of truth for question text. Triage points at them; it doesn't duplicate the Q content.
- **`/roster`** — counts every item once per bucket; triage's H1 count line uses the same scheme so the two views agree.
