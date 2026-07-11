---
description: Messages facet — the agent's per-anchor inbox of background-process messages that the agent reads on every pause. Distinct from `{slug} Inbox.md` which is the user's drop-zone for raw input.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Messages](hook://p/DAS%20Messages)
# FCT Messages
Spec for the **Messages facet** — the per-anchor file `{slug} Messages.md` that holds background-process notes for the agent to read on every pause, separate from the user's raw-input `{slug} Inbox.md`.

**Related:** [[DAS Inbox]],  [[FCT Backlog]],  [[DAS Track]],  [[CAB Base]]
**Examples:** [[HBR Messages\|minimal]],  [[HBR Messages\|with real system messages]]

**Cardinality: one per anchor** — each anchor has exactly one `{slug} Messages.md` file at its root.

# RULESET R-messages
include::
where:: `{anchor}/* Messages.md`
description:: the Messages facet — agent's per-anchor background-process inbox, distinct from the user's Inbox

Embedded ruleset for the Messages facet, co-located per [[F133 — Rulesets folder convention + facet embedding|F133]].

### RULE R-messages-01 — File is `{slug} Messages.md` at the anchor root (checked)
check:: h1_is_anchor_messages

The messages file is `{slug}/{slug} Messages.md` — not under Track or Docs, and not the Inbox.

**Check pattern:** `{anchor}/{slug} Messages.md` exists and its H1 is `# {slug} Messages`.

### RULE R-messages-02 — Agent-facing background notes only (stated)

Messages holds background-process / out-of-band notes the agent reads on every pause — not user-dropped raw input (that is `{slug} Inbox.md`).

### RULE R-messages-03 — Distinct from Inbox (stated)

The Messages-vs-Inbox split (agent-read background notes vs. user-dropped raw input) is load-bearing; never blur the two on an instance or in this spec.

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. It defines the `{slug} Messages.md` facet; it is not itself a messages file.)*

- **Inclusion test** — content belongs here only when it defines how Messages files are structured, written, read, or pruned across anchors; per-anchor message content or single-anchor examples belong elsewhere. Routing for displaced content: project-wide rules → CLAUDE.md; markdown-rendering → [[R-markdown]]; Inbox-facet rules → `CAB Inbox.md`.
- **Load-bearing distinction to preserve** — the frontmatter `description` and R-messages-03 both fix the Messages-vs-Inbox split (agent-read background notes vs. user-dropped raw input); any edit that loosens or removes that distinction breaks the facet's reason for existing.
- **Cross-references to keep in sync** — [[CAB Base]] dispatch tables, [[DAS Anchor Tree]] tree, and any anchor template that scaffolds a `{slug} Messages.md`.
- **Conventions** — refer to sibling facets by their CAB filename (`~~[[FCT Inbox]]~~`, `[[CAB Backlog]]`); refer to per-anchor instances with the `{slug}` placeholder, never a concrete anchor's name.
[2026-07-10 12:31:25] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
[2026-07-10 12:59:48] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
[2026-07-10 13:14:07] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
[2026-07-10 15:24:43] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
[2026-07-10 15:24:51] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
[2026-07-10 15:25:01] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
[2026-07-10 15:25:14] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
[2026-07-10 15:25:16] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
[2026-07-10 15:25:20] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
[2026-07-10 15:25:26] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
[2026-07-10 15:25:29] [INFO] backlog at SYS/Bespoke/Skill Agent/ob-skills/facets/DAS Backlog.md was edited
