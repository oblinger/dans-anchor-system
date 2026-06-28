---
description: "the work-surface facets (centralized in SKA per D08, but specified here)"
---

# Track & execute
The the work-surface facets (centralized in SKA per D08, but specified here).

| -[[FCT Track]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [FCT Track](hook://p/FCT%20Track)<br>: the work-surface facets (centralized in SKA per D08, but specified here) |
| --- | --- |
| Design | [[Workflow Design\|Design]],   |
| Facets | [[Backlog]],  [[FCT Features\|Features]],  [[FCT Inbox\|Inbox]],  [[FCT Icebox\|Icebox]],  [[FCT Messages\|Messages]],  [[FCT Log\|Log]],  [[FCT Triage\|Triage]],  [[FCT Status\|Status]],   |

**Linkage** — this facet's existence ⟺ the anchor runs the [[workflow]] discipline; the two share one design folder, [[Workflow Design]] (hosted on the behavioral core), reachable from either page per [[SKA Decisions]] D10.

# RULESET R-track-group
include::
where:: anchor
description:: the FCT Track family index — the work-surface facet group page

What `/audit` checks on this facet-group index page. It is a grouped-Container anchor page (chassis governed by `R-anchor-page`); the rules here are the **group-membership** invariants for the work-surface facet family. Format of this set: [[FCT Ruleset]].

### RULE R-track-group-01 — The Facets row indexes every work-surface facet (checked)

The `Facets` row links every track / work-surface facet (Backlog, Features, Inbox, Icebox, Messages, Log, Triage, Status), and each member's breadcrumb routes through this page.

**Check pattern:** the `Facets`-row link set equals the work-surface facet files under `FCT Track/`; each member breadcrumb passes through `[[FCT Track]]`.

### RULE R-track-group-02 — Specifies the work surfaces; SKA owns the instances (stated)

This family *specifies* the work-surface facets, but the live tracking instances for the skills ecosystem are centralized on the shared SKA surface ([[SKA Decisions|D08]]) — SKA sub-projects carry no `{NAME} Track/` of their own.

### RULE R-track-group-03 — Track folder presence is a trait; omit when no active tracking (checked)

A `{NAME} Track/` folder exists **iff** the anchor maintains active tracking — a live backlog, feature docs, messages, or status. Its presence is itself the signal that the anchor is tracked. An anchor with no tracking, or only template boilerplate (empty `backlog`/`plan`/`principles` stubs), carries **no** Track folder: during migration, **wipe the boilerplate and omit the folder**. (SKA sub-projects additionally centralize tracking on the SKA surface per R-track-group-02, so they carry no Track folder regardless.)

**Check pattern:** for each `{NAME} Track/`, assert at least one child carries distinct authored tracking content; a boilerplate-only Track folder is a violation — remove it.

**Why:** parallel to the Design facet (R-design-08) — folder existence is an honest trait. An empty Track folder claims a tracking process the anchor doesn't run.

### RULE R-track-group-04 — Inbox lives in the Track folder (checked)
The anchor's `{NAME} Inbox.md` (the agent message inbox) lives **inside `{NAME} Track/`**, never at the anchor root — Inbox is a track / work-surface facet, alongside Backlog, Messages, and Icebox.
**Check pattern:** no `{NAME} Inbox.md` sits at the anchor root; any Inbox that exists is under `{NAME} Track/`. An empty / boilerplate Inbox is wiped, not relocated (R-track-group-03).
**Why:** the inbox is part of the tracking surface; stranding it at the root hides it from the Track dispatch and breaks the one-place-for-the-work-surface convention.
