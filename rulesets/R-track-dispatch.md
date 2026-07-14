# RULESET R-track-dispatch
include::
where:: `file: **/{slug} Track.md`
description:: Rules every `{slug} Track.md` dispatch page must satisfy — location, structure, top-left cell identity, and contents restricted to tracking metadata only.

### RULE R-track-dispatch-01 — File lives inside the Track folder (checked)
The file is named `{slug} Track.md` and lives at `{slug} Track/{slug} Track.md` — inside the root-level `{slug} Track/` folder.
**Check pattern:** the file's path matches `{slug} Track/{slug} Track.md`.
**Why:** the Track dispatch page is the entry point for the Track folder; misplacing it breaks the folder's navigation chain.

-[[{slug} Track]]-` (checked)
-[[{slug} Track]]-` (with surrounding dashes); the second cell begins with `>` and includes a `: work tracking + planning` label.
**Check pattern:** the first table row matches `| -\[\[.+ Track\]\]- |`.
**Why:** the top-left cell anchors CAB Anchor Page mechanics (the `-...-` dash pattern wires the dispatch table to the auto-management system); reformatting it breaks structural tooling.

### RULE R-track-dispatch-03 — Contents restricted to tracking metadata (sampled)
Body rows list only tracking-metadata documents: Backlog (required), Status, Discussion, Icebox, Inbox, ask, Messages, Questions. Design artifacts (PRD, UX, Architecture, Features, Roadmap, Testing, Decisions) MUST NOT appear as rows.
**Check pattern:** no row links a file from the `{slug} Design/` subtree or any design-artifact type listed in § What does NOT live in Track.
**Why:** Track holds workflow state and ephemeral surfaces; design artifacts live in `{slug} Design/`. Mixing them collapses the Track/Design split that F094 and the 2026-06-10 restructure established.

### RULE R-track-dispatch-04 — Backlog row is required when Track trait is present (checked)
The dispatch table includes a row linking `{slug} Backlog.md`; this is the only mandatory child of the Track folder.
**Check pattern:** a row linking `[[{slug} Backlog]]` (or its pipe-aliased form) exists.
**Why:** the [[DAS Backlog]] is required for the Track trait; a Track dispatch page without a Backlog row signals the backlog is missing, not optional.
