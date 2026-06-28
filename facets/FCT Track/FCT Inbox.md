---
description: raw incoming content to process
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Track]] → [FCT Inbox](hook://p/FCT%20Inbox)

# FCT Inbox
Facet spec for the `{NAME} Inbox.md` drop-zone file — the chronological log of raw input pasted in for later processing into the anchor's planning docs.

**Related:** [[FCT Discussion]],  [[FCT Backlog]],  [[FCT PRD]],  [[FCT Roadmap]]
**Examples:** [[CAE Inbox\|example]]

**TLDR** — A single `{NAME} Inbox.md` file (one per anchor) is the paste-first drop zone for raw input; processed entries stay with a `DONE` or `MOVED →` status tag as a permanent log.

**Cardinality:** one per anchor.

The inbox (`{NAME} Inbox.md`) is a drop zone for raw input — long descriptions, change requests, design thoughts, reference material — pasted in for processing and integration into the planning and execution docs.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Inbox.md` — Inbox.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# CAE Inbox

| -[[CAE Inbox]]- |  |
| --- | --- |
| --- | |

Items below have been processed and moved to their destination docs.

## 2026-02-28 — Retry backoff tuning    `DONE`
User reported exponential backoff too aggressive for short tasks. Captured in [[CAE Open Questions#14]].

Original input:
> When I schedule a 2-second task and it fails, the retry waits 4s, then 8s, then 16s. For quick tasks this feels excessive. Could we cap the backoff or use linear for tasks under 10s?

## 2026-02-25 — Priority starvation fix    `MOVED → CAE Roadmap#M3`
Discussed promotion logic for starved low-priority tasks. Design notes moved to [[CAE Discussion#2026-02-25]]. Implementation planned for M3.

## 2026-02-20 — Initial feature brainstorm    `DONE`
Raw feature list from kickoff meeting. Items distributed to [[CAE PRD]] and [[CAE Backlog]].

---

# Format Specification

## Location

`{NAME} Inbox.md` lives at the anchor root, alongside the anchor page.

## Top of doc (canonical, per F060)

Every Inbox file opens with the standard top-of-doc format: YAML frontmatter + `# {NAME} Inbox` H1 + dispatch-table placeholder. See `[[skills/rewire/SKILL]]` § Default doc top-of-file.

## Format
- Reverse chronological dated sections (H2)
- Each heading: `## YYYY-MM-DD — Topic    \`STATUS\``
- Status tags: `DONE` (processed in place), `MOVED → {destination}` (content relocated)
- Original input preserved as blockquotes when useful as a record

## Lifecycle
- Content is pasted in, then processed by an agent or the user who integrates it into the appropriate planning docs (PRD, Roadmap, Todo, Backlog)
- Processed entries remain with a status tag as a persistent log of what was communicated
- Rarely revisited after processing

# RULESET R-fct-inbox
include::
where:: file: **/{NAME} Inbox.md
description:: Rules every `{NAME} Inbox.md` instance must satisfy — location, heading format, and status-tag vocabulary.

### RULE R-fct-inbox-01 — File exists at the anchor root (checked)
The Inbox file lives at the anchor root: `{NAME} Inbox.md`, alongside the anchor page.
**Check pattern:** file is present at `<anchor-root>/{NAME} Inbox.md`.
**Why:** co-location with top-level anchor docs ensures consistent discoverability by agents and users. (Tier: checked)

### RULE R-fct-inbox-02 — Sections are reverse-chronological H2s with a status tag (checked)
Each entry heading follows the form `## YYYY-MM-DD — {Topic}` followed by a backtick-wrapped `{STATUS}` tag, where `{STATUS}` is one of the two sanctioned tags.
**Check pattern:** every H2 matches `^## \d{4}-\d{2}-\d{2} — .+` and carries a backtick-wrapped status tag.
**Why:** consistent heading format lets agents scan for processed vs. pending entries without parsing free-form prose. (Tier: checked)

### RULE R-fct-inbox-03 — Only sanctioned status tags are used (checked)
The only permitted status values are `DONE` (processed in place) and `MOVED → {destination}` (content relocated). No other tags may be used without updating this spec.
**Check pattern:** no H2 carries a status tag other than `DONE` or `MOVED → …`.
**Why:** downstream tooling and agent skills key off these exact strings; ad-hoc tags silently break detection. (Tier: checked)

### RULE R-fct-inbox-04 — Processed entries are retained, not deleted (stated)
After processing, entries remain in the file with their status tag intact as a permanent log of what was communicated and where it went.
**Check pattern:** no H2 entry disappears upon processing; entries only gain a status tag.
**Why:** the Inbox doubles as an audit trail; deleting processed entries destroys the history of what input arrived and where it was routed. (Tier: stated)

# BRIEF

- **This file is the facet spec for `{NAME} Inbox.md`** — it defines the shape, location, lifecycle, and status-tag vocabulary every anchor's Inbox file must follow. It is NOT itself an inbox.
- **Authority scope** — covers only the Inbox facet. Drop-zone semantics for other surfaces (Backlog, PRD, Roadmap, Discussion) belong in their own CAB facet specs; do not generalize Inbox rules here to cover them.
- **Inclusion test for new content** — a rule belongs here only if it constrains how an Inbox file is authored, located, formatted, or processed. Cross-facet workflow (how Inbox entries promote to PRD/Roadmap/Backlog) lives in the destination facet specs, not here.
- **The Reference Example zone is illustrative, not authoritative** — when the canonical format changes (location pattern, status tags, top-of-doc rules), update the Format Specification section first; revise the Reference Example only to keep it in sync. Do not let the example drift into spec.
- **Status-tag vocabulary is load-bearing** — `DONE` and `MOVED → {destination}` are the only sanctioned tags. Adding tags requires updating this spec; downstream tooling and agent skills key off these strings.
- **Don't inline anchor-specific examples** — the working example link (`CAE Inbox`) is the canonical live instance; per-anchor variations belong in that anchor's docs, not here.
- **Top-of-doc rules come from rewire** — the YAML frontmatter + H1 + dispatch-table placeholder shape is owned by `[[skills/rewire/SKILL]]` § Default doc top-of-file; do not duplicate that spec here, just cite it.
