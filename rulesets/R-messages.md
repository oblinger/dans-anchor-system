# RULESET R-messages
include::
where:: `{anchor}/* Messages.md, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog (a `DAS <Name>.md` is the SPEC for the facet, not an instance; specs are governed by [[R-facet-spec]]) — added 2026-07-13, T014 follow-on.
description:: the Messages facet — agent's per-anchor background-process inbox, distinct from the user's Inbox

Ruleset for this facet — spec: [[DAS Messages]] (extracted from the spec 2026-07-12).

### RULE R-messages-01 — File is `{slug} Messages.md` at the anchor root (checked)
check:: h1_is_anchor_messages

The messages file is `{slug}/{slug} Messages.md` — not under Track or Docs, and not the Inbox.

**Check pattern:** `{anchor}/{slug} Messages.md` exists and its H1 is `# {slug} Messages`.

### RULE R-messages-02 — Agent-facing background notes only (stated)

Messages holds background-process / out-of-band notes the agent reads on every pause — not user-dropped raw input (that is `{slug} Inbox.md`).

### RULE R-messages-03 — Distinct from Inbox (stated)

The Messages-vs-Inbox split (agent-read background notes vs. user-dropped raw input) is load-bearing; never blur the two on an instance or in this spec.
