---
description: "dated feature specs (F-numbered)"
---
# CAB Features

Specification for the **Features** facet — the F-numbered per-feature design docs that live under an anchor's `{NAME} Design/{NAME} Features/` folder, with their index page and pre-document Open-Questions zone.

**Location:** `{NAME} Design/{NAME} Features/` (folder; one file per feature, `F<NNN> — <Title>.md`).

**Relocated to Design 2026-06-10** — previously lived at `{NAME} Track/{NAME} Features/` (per F094) and `{NAME} Docs/{NAME} Plan/{NAME} Features/` (pre-F094). Moved into Design alongside [[CAB Roadmap]] because feature docs are themselves design artifacts — each carries a Summary, Success Criteria, and Design section that the PRD / Architecture / Testing facets refer to. Track now holds only [[CAB Backlog]], [[CAB Status]], and tracking metadata. Lazy migration: existing anchors stay at the old location until next `/feature` or `/design` touch repositions them (F142).

Individual feature specifications, each in an F-numbered file inside the Features subfolder of the Design folder.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Features/2026-04-21 Scheduler Pause.md` — demonstrates the Open-Questions-above-H1 convention.

Below is a condensed reference example.

# Reference Example
---

```
CAE Docs/CAE Plan/
└── CAE Features/
    ├── CAE Features.md                  ← feature index
    ├── 2026-03-15 Retry Logic.md
    └── 2026-04-02 Recurring Tasks.md
```

**CAE Features.md** (index, reverse chronological):

```markdown
- [[2026-04-02 Recurring Tasks]] — Cron-style recurring task schedules [proposed]
- [[2026-03-15 Retry Logic]] — Automatic retry with exponential backoff [done]
```

**2026-03-15 Retry Logic.md** (individual feature):

```markdown
---
description: Automatic retry with exponential backoff
---

## Open Questions

Blocking decisions. The feature cannot move from Designing → Agreed while
this list is non-empty.

- **Q2 — cap on max-retries?** — should there be an absolute upper bound,
  or can users set arbitrarily high values? Options: 100 absolute, user-configurable, no cap.

### Resolved

- **Q1 — jitter strategy?** — **Resolution:** full-jitter (delay * rand(0,1)).
  Incorporated into Design § Backoff.



# Retry Logic

## Summary

When a task fails, CAE automatically retries it using exponential backoff
with jitter. This eliminates manual re-queuing for transient failures
(network timeouts, resource contention). The user configures max retries
and base delay per task or globally.

## Requirements

- Max retry count configurable per task (default: 3)
- Exponential backoff: delay = base * 2^attempt + jitter
- Tasks marked `failed` after exhausting retries
- Retry history visible in `tsk status <id>`

## Design

Retry state stored in the task record: attempt count, next retry time,
last error. The scheduler checks retry-eligible tasks each tick and
re-enqueues them at the computed delay.

## Status

Designing — awaiting resolution of Q2.
```

**Note the layout:** `## Open Questions` sits ABOVE the `# Retry Logic` H1. It is pre-document material — the first thing the user sees when opening the file. Resolved questions move to the H3 `### Resolved` subsection; they never get deleted.

---



## Features Folder Structure

Features are documented in their own subfolder within `{NAME} Docs/`:

```
{NAME} Docs/
└── {NAME} Features/
    ├── {NAME} Features.md               ← feature index (reverse chronological)
    ├── 2026-01-15 User Auth.md          ← individual feature
    ├── 2026-01-22 Dark Mode.md
    └── 2026-02-03 Export CSV.md
```

## Features Index Page

The `{NAME} Features.md` page lists all features in reverse chronological order (newest first):

```markdown
- [[2026-02-03 Export CSV]] — Export data to CSV format [proposed]
- [[2026-01-22 Dark Mode]] — Theme support for dark mode [in progress]
- [[2026-01-15 User Auth]] — User authentication via OAuth [done]
```

- **FILE NAME** - Each feature is a dated file using the format `YYYY-MM-DD Feature Name.md`, with the date indicating when the feature was introduced or documented.
- **FEATURE STATUS** - Status (`proposed` | `in progress` | `done` | `cut`) is tracked on the features index page, not in the feature document itself.


## Feature Document Format

The feature document has **two zones**:

1. **Pre-document zone (above the H1)** — `## Open Questions` and its `### Resolved` subsection. This is blocking material that must be visible the moment the user opens the file. It exists on every feature doc, even if empty.
2. **Document zone (H1 and below)** — the feature spec proper: Summary, Design, etc.

### Pre-document zone — always present

| Section | Level | Required | Purpose |
|---------|-------|----------|---------|
| `## Open Questions` | H2 above H1 | Always | Blocking decisions; feature cannot leave Designing while non-empty |
| `### Resolved` | H3 under Open Questions | Always (can be empty) | Answered questions move here with the resolution; never deleted |

When Open Questions is empty, leave the H2 with a one-liner placeholder (e.g. `_None — design is clean._`) — preserve the structure so the convention is visible.

**Workflow note:** every time an agent edits Open Questions — adds a question, resolves one, moves one to Resolved — it immediately runs `open "<path to this file>"` so the doc surfaces on the user's screen. The `/feature` skill's Runbook step 1a enforces this.

### Document zone — H1 and below

Start with only the mandatory sections; add optional sections as the feature grows in complexity.

**Mandatory:**
- **H1 `# [[{NAME}]] · F{n} — {Feature Name}`** — anchor-slug breadcrumb (wiki-link to anchor page) + F-number + title. The leading `[[{NAME}]]` lets the reader (a) jump back to the anchor page and (b) immediately see which anchor they're in — load-bearing when many anchors are active and feature docs look similar across them. Filename matches without the `[[]]` brackets: `F{n} — {Feature Name}.md`.
- **Title encodes M-position when feature is commissioned from a roadmap milestone** (per [[CAB Roadmap]] R-roadmap-10). Format: `F<NNN> — M-<Name>.<position>: <Title from Roadmap entry>`. Example: `F118 — M-CLI.3.5: Implement CLI Core Statements.md`. The roadmap entry gets a `[F118]` marker pointing at the feature doc. Bi-directional discoverability without rename-cost. See [[F144 — Completed Roadmap + named milestones]] for the provenance discussion. **Features commissioned NOT from a roadmap stay `F<NNN> — <Title>` form** — absence of M-prefix signals "filed independently."
- **F060 placement.** The feature-doc H1 already carries its own breadcrumb (`[[{NAME}]] ·`), so the F060 dispatch-table placeholder is **optional** for feature docs. New feature docs may skip the placeholder; older ones that have it can keep it. Rewire does not insert one if absent.
- **TLDR (per `progressive-disclosure`)** — 3-5 one-line bullets, each with a 2-3-word bolded descriptor, placed immediately after the H1 (before Summary). Feature docs are the initial scope of the TLDR-required rule — they reduce cleanly to a few one-line bullets capturing the gist. Format: `**TLDR**` heading then a bullet list of `- **<Descriptor>** — <one-line summary>`.
- **Summary** — What the feature does and why it exists (1-2 paragraphs)
- **Status** — lifecycle state (Designing / Agreed / Implementing / Testing / Done)

**Optional (add as needed, H2 headings in document order):**
- **Interface** — Description of external interface (API, CLI, config, user, etc.)
- **Requirements** — Specific acceptance criteria or constraints
- **Design** — Technical approach, architecture decisions, trade-offs
- **Dependencies** — What this feature depends on or what it blocks
- **Roadmap** — Execution plan for substantial features. See § Roadmap section below.
- **Notes** — Working notes, research

### `## Roadmap` section — for features substantial enough to spawn sub-work

Large feature docs sometimes need their own sub-roadmap — the feature is a chunk of work that breaks down into multiple independent sub-tasks or sub-features. The `## Roadmap` H2 is the home for this sub-plan; it follows the [[CAB Roadmap]] conventions (multi-level numbering, checkboxes, Status-line, etc.) scoped to *inside this feature*.

**Two patterns within a feature's Roadmap:**

1. **Dotted sub-numbering** — `F<NNN>.1`, `F<NNN>.2`, `F<NNN>.3` for sub-items that stay inside this feature doc. Each sub-item is a chunk of work that gets minted in turn; the parent F-number stays the unit of feature-level tracking. Use when the sub-items are too small to deserve their own feature docs.
2. **Sub-feature spinoffs** — bullets like `[ ] [[F<NNN+k> — <Title>]]` (or bare brackets `[F<NNN+k> — <Title>]` for as-yet-unwritten feature docs) when a sub-item is substantial enough to deserve its own feature doc. The parent's roadmap captures the intent; the child feature doc gets authored when work on that piece begins.

Both patterns can mix in the same Roadmap section — small inline sub-items stay dotted; substantial spinoffs get their own F-numbers.

**Example:**

```markdown
## Roadmap

- [x] **F017.1 — WAL append path** — wrap enqueue/dequeue in `cae.wal` append. Independent.
- [x] **F017.2 — SQLite schema + migrations** — `migrations/0001_init.sql`. Independent of F017.1.
- [ ] **F017.3 — Recovery loader** — depends on F017.1 + F017.2. Will spawn:
    - [ ] [F049 — WAL compaction strategy] — not yet authored; capture when recovery loader's bottleneck surfaces.
- [ ] **F017.4 — Backpressure on durable enqueue** — defer to post-MVP.

**Status:** Core complete — F017.1 + F017.2 merged. F017.3 in progress; F049 deferred.
```

When the Roadmap section drives the feature's tracking, the feature doc's `## Status` field above carries the rollup ("Core complete — 2/4 sub-items done") and the Roadmap section carries the per-sub-item detail. Consistent with CAB Roadmap's "checkbox + Status-line + per-item-checkbox" three-axis convention applied at smaller scope.

**Referencing as-yet-undesigned sub-features.** Bare-bracket entries `[F<NNN+k> — <Title>]` signal "this sub-feature will exist when authoring catches up." When the agent / user reaches that sub-item and creates the actual feature doc, the bare brackets upgrade to `[[F<NNN+k> — <Title>]]` wiki-links. The roadmap captures intent without requiring all sub-features to be designed up front.

---

# BRIEF

- **This is the Features facet spec** — the authoritative definition of how F-numbered feature docs and their index page are shaped. Skills like `/feature`, `/design`, `/groom`, and `/crank` cite this file; downstream tooling (audit, rewire) checks anchors against it.
- **NOT a feature index, NOT a backlog, NOT a roadmap** — don't pile concrete F<NNN> entries, status lists, or per-anchor feature catalogs here. Those live in `{NAME} Features.md` index pages within each anchor, or in [[CAB Backlog]] / [[CAB Roadmap]] for their respective concerns.
- **Inclusion test for edits** — a change belongs here only if it defines the *shape* of feature docs across all anchors: folder location, filename pattern, the two-zone layout (Open Questions above H1; spec body below), mandatory vs optional H2 sections, title-encoding conventions (M-position), or the Roadmap-within-feature sub-pattern. Anchor-local feature conventions go in `{NAME} Rules.md` or `{NAME} Decisions.md`, not here.
- **Load-bearing conventions** — the Open-Questions-above-H1 layout, the `F<NNN> — <Title>.md` filename pattern (zero-padded triple-digit per memory), the `# [[{NAME}]] · F{n} — {Title}` H1 breadcrumb, the optional `M-<Name>.<position>:` title segment for roadmap-commissioned features, and the reverse-chronological index format. Changing any of these ripples across every anchor — update worked examples and downstream skill runbooks in the same pass.
- **Cross-references to maintain** — [[CAB Roadmap]] (M-position title encoding, sub-roadmap pattern), [[CAB Backlog]] (tracking surface), [[CAB Status]] (lifecycle states), `progressive-disclosure` (TLDR rule), and the relocation note (F094 → 2026-06-10 Design move; F142 lazy-migration). Keep these aligned when the shape evolves.
- **Body discipline** — the body is already long because it carries the worked example and format tables; resist adding meta prose about how the spec is organized. New rules attach to the existing section that owns the topic (Format / Folder Structure / Roadmap subsection) rather than spawning new top-level sections.
