---
description: mend messages for the Log facet — what to actually do when an R-log rule fires
---

# DAS Mend Log
Remediation messages for the `{slug} Log` facet, cashed in by `warden mend R-log-<nn>`.

A mend message answers one question: *what do I do about this specific error?* It states the fix, then points at the facet and a worked example. It never restates the facet — if a reader gets the whole convention here without following a link, the message has grown into the thing it points at, and the two will disagree within a month.

### MEND log-location

Put the log where the facet expects it, then re-run the write.

The log is `{slug} Log/` (a folder of dated entries) or `{slug} Log.md` (a single file) directly under the anchor root — never under `{slug} Track/`, never under a Docs folder, never at the vault root. Pick the folder form when entries are long enough to want their own files; the single-file form otherwise. Both are equally valid and you can convert later.

If the file is already written and merely misplaced, move it rather than creating a second one — two logs for one anchor is the failure this rule exists to prevent.

For the model and the entry-naming rules, read [[DAS Log]]. For a worked example, see `SKA Log/`.

### MEND log-dispatch

Add a dispatch row on the anchor page pointing at the log, then re-run the write.

The anchor page (`{slug}.md`) must carry `[[{slug} Log]]` in its masthead so the log is reachable from the anchor's front door. A log nothing links to is a log nobody reads.

Do not hand-author the masthead — run `/audit dispatch`, which builds the row in the correct fixed position. Hand-editing a dispatch table is its own class of error, and the identity cell has a load-bearing `→ ` prefix that is easy to lose.

For the table grammar, read [[DAS Dispatch Table]].
